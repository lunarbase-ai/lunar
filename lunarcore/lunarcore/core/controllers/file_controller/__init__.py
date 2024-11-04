# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
#
# SPDX-License-Identifier: LicenseRef-lunarbase
import os
from typing import Union, Dict

from lunarcore.core.persistence import PersistenceLayer
from lunarcore.core.search_indexes.component_search_index import ComponentSearchIndex
from lunarcore.config import LunarConfig
from lunarcore.core.controllers.demo_controller import DemoController


class FileController:
    def __init__(self, config: Union[str, Dict, LunarConfig]):
        self._config = config
        if isinstance(self._config, str):
            self._config = LunarConfig.get_config(settings_file_path=config)
        elif isinstance(self._config, dict):
            self._config = LunarConfig.model_validate(config)

        self._persistence_layer = PersistenceLayer(config=self._config)

        self._custom_component_search_index = ComponentSearchIndex(config=self._config)
        self._demo_controller = DemoController(config=self._config)

    @property
    def persistence_layer(self):
        return self._persistence_layer

    async def save(self, user_id: str, workflow_id: str, file):
        file_path = self._persistence_layer.get_user_workflow_files_path(
            user_id=user_id, workflow_id=workflow_id
        )
        file_path = await self._persistence_layer.save_file_to_storage(
            path=os.path.join(file_path, workflow_id),
            file=file,
        )

        return file_path

    async def copy_demo_files_to_workflow(
        self, demo_id: str, user_id: str, workflow_id: str
    ):
        demo_path = os.path.join(self._config.DEMO_STORAGE_PATH, demo_id)
        template_files = [
            f
            for f in os.listdir(demo_path)
            if os.path.isfile(os.path.join(demo_path, f))
            and not (
                os.path.join(demo_path, f).endswith(f"{demo_id}.json")
                or os.path.join(demo_path, f).endswith(f"{demo_id}.json.license")
            )
        ]
        for filename in template_files:
            await self._persistence_layer.save_file_to_storage_from_path(
                os.path.join(demo_path, filename),
                os.path.join(
                    self._persistence_layer.get_user_workflow_files_path(
                        user_id=user_id, workflow_id=workflow_id
                    ),
                    workflow_id,
                ),
            )

    async def list_all_workflow_files(self, user_id: str, workflow_id: str):
        file_path = os.path.join(
            self._persistence_layer.get_user_workflow_files_path(
                user_id=user_id, workflow_id=workflow_id
            ),
            workflow_id,
        )
        files = await self._persistence_layer.get_all_files(path=f"{file_path}/*")
        return files

    async def get_by_path(self, file_path: str):
        file = await self._persistence_layer.get_file_by_path(
            path=file_path,
        )
        return file

    async def search(self, query: str):
        pass

    async def delete(self, file_path: str):
        pass
