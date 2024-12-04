# SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import json
from pathlib import Path
from typing import Dict, List, Optional, Union

from dotenv import dotenv_values
from lunarbase.config import LunarConfig
from lunarbase.indexing.component_search_index import ComponentSearchIndex
from lunarbase.orchestration.engine import run_component_as_prefect_flow
from lunarbase.persistence import PersistenceLayer
from lunarbase.modeling.data_models import ComponentModel

from lunarbase import LUNAR_CONTEXT
from lunarbase.utils import setup_logger

logger = setup_logger("Component controller")

class ComponentController:
    def __init__(self, config: Union[str, Dict, LunarConfig]):
        self._config = config
        if isinstance(self._config, str):
            if not Path(self._config).is_file():
                raise FileNotFoundError(
                    f"Configuration file {self._config} does not exist!"
                )
            self._config = LunarConfig.get_config(settings_file_path=config)
        elif isinstance(self._config, dict):
            self._config = LunarConfig.model_validate(config)

        self._persistence_layer = PersistenceLayer(config=self._config)
        self._component_search_index = ComponentSearchIndex(config=self._config)

    @property
    def component_search_index(self):
        return self._component_search_index

    @property
    def config(self):
        return self._config

    async def index_global_components(self):
        # if len(LUNAR_CONTEXT.lunar_registry.components) == 0:
        #     await LUNAR_CONTEXT.lunar_registry.load_components()

        global_components = self.list_global_components()
        self._component_search_index.index_global_components(global_components)

    async def tmp_save(self, component: ComponentModel, user_id: str):
        tmp_path = self._persistence_layer.get_user_tmp(user_id)
        return await self._persistence_layer.save_to_storage_as_json(
            path=str(Path(tmp_path, f"{component.id}.json")),
            data=json.loads(component.json(by_alias=True)),  # To allow aliasing
        )

    async def tmp_delete(self, component_id: str, user_id: str):
        tmp_path = self._persistence_layer.get_user_tmp(user_id)
        await self._persistence_layer.delete(
            path=str(Path(tmp_path, f"{component_id}.json")),
        )
        return tmp_path

    async def save(self, custom_component: ComponentModel, user_id: str):
        existing_components = self._component_search_index.get_component(
            component_id=custom_component.id, user_id=user_id
        )

        if len(existing_components) != 0:
            self._component_search_index.remove_component(custom_component.id, user_id)

        custom_component.is_custom = True
        self._component_search_index.index([custom_component], user_id)
        await self._persistence_layer.save_to_storage_as_json(
            path=str(
                Path(
                    self._persistence_layer.get_user_custom_root(user_id),
                    f"{custom_component.id}.json",
                )
            ),
            data=json.loads(custom_component.json(by_alias=True)),  # To allow aliasing
        )

        return custom_component

    async def save_auto_custom_components(
        self, components: List[ComponentModel], user_id: str
    ):
        for component in components:
            if component.is_custom:
                await self.save(component, user_id)

    async def delete(self, custom_component_id: str, user_id: str):
        existing_components = self._component_search_index.get_component(
            custom_component_id, user_id
        )
        if len(existing_components) != 0:
            self._component_search_index.remove_component(custom_component_id, user_id)
        await self._persistence_layer.delete(
            path=str(
                Path(
                    self._persistence_layer.get_user_custom_root(user_id),
                    f"{custom_component_id}.json",
                )
            )
        )

    @staticmethod
    def list_global_components():
        components = sorted(
            [
                registered_component.component_model
                for registered_component in LUNAR_CONTEXT.lunar_registry.components
            ],
            key=lambda cmp: cmp.name,
        )
        return components

    async def list_all_components(self, user_id: str = "*"):
        components = self.list_global_components()
        custom_components = await self._persistence_layer.get_all_as_dict(
            path=str(Path(self._persistence_layer.get_user_custom_root(user_id), "*"))
        )
        components.extend(
            [ComponentModel.parse_obj(comp) for comp in custom_components]
        )
        return components

    async def list_custom_components(self, user_id: str):
        components = await self._persistence_layer.get_all_as_dict(
            path=self._persistence_layer.get_user_custom_root(user_id)
        )
        return map(
            lambda component_dict: ComponentModel.parse_raw(json.dumps(component_dict)),
            components,
        )

    async def get_by_id(self, component_id: str, user_id: str):
        core_component = next(
            (comp for comp in self.list_global_components() if comp.id == component_id),
            None,
        )
        if core_component is not None:
            return core_component
        custom_component = await self._persistence_layer.get_from_storage_as_dict(
            path=str(
                Path(
                    self._persistence_layer.get_user_custom_root(user_id),
                    f"{component_id}.json",
                )
            )
        )
        return ComponentModel.parse_raw(json.dumps(custom_component))

    async def search(self, query: str, user_id: str):
        search_results = self._component_search_index.search(query, user_id)
        components = []
        for i, result_mapping in enumerate(search_results):
            if result_mapping["is_custom"]:
                component_model = await self.get_by_id(result_mapping["id"], user_id)
                components.append(component_model)
            else:
                pkg_comp = LUNAR_CONTEXT.lunar_registry.get_by_class_name(
                    result_mapping["type"]
                )
                if pkg_comp is not None:
                    components.append(pkg_comp[1])
        return components

    async def get_example_workflow_by_label(self, label: str, user_id: Optional[str]):
        candidates = [
            comp
            for comp in self.list_global_components()
            if label.upper() in comp.label.upper()
        ]
        component = candidates.pop()
        return component.get_component_example()

    async def run(self, component: ComponentModel, user_id: Optional[str] = None):
        component = ComponentModel.model_validate(component)
        user_id = user_id or self._config.DEFAULT_USER_PROFILE

        venv_dir = None
        if component.workflow_id is not None:
            venv_dir = self._persistence_layer.get_workflow_venv(
                user_id=user_id, workflow_id=component.workflow_id
            )

        if venv_dir is None or not Path(venv_dir).is_dir():
            venv_dir = self._persistence_layer.get_user_component_venv(user_id)

        env_path = self._persistence_layer.get_user_environment_path(user_id)
        environment = {"LUNAR_USERID": str(user_id)}
        if Path(env_path).is_file():
            environment.update(dotenv_values(env_path))

        component_path = await self.tmp_save(component=component, user_id=user_id)
        result = await run_component_as_prefect_flow(
            component_path=component_path, venv=venv_dir, environment=environment
        )

        # TODO: A potential sanity check for this cleanup (e.g., tmp_component_path == the result of the below)
        _ = await self.tmp_delete(component_id=component.id, user_id=user_id)

        return result

    async def publish_component(
            self,
            author: str,
            author_email: str,
            component_name: str,
            component_description: str,
            component_class: str,
            component_documentation: str,
            version: str,
            access_token: str,
            user_id: str
    ):
        github_publisher_service = GithubPublisherService(access_token=access_token)
        component_publisher = ComponentPublisher(publisher=github_publisher_service)
        component_publisher.publish_component(
            author,
            author_email,
            component_name,
            component_description,
            component_class,
            component_documentation,
            version
        )
