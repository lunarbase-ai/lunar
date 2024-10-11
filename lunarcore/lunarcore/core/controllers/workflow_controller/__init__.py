# SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import os.path
import warnings
from typing import Union, Dict, Optional

from dotenv import dotenv_values
from pydantic import ValidationError

from lunarcore.config import LunarConfig
from lunarcore.core.orchestration.engine import run_workflow_as_prefect_flow
from lunarcore.core.persistence import PersistenceLayer
from lunarcore.core.search_indexes.workflow_search_index import WorkflowSearchIndex
from lunarcore.core.data_models import (
    WorkflowModel,
)
from lunarcore.utils import get_config
from lunarcore.core.auto_workflow import AutoWorkflow


class WorkflowController:
    def __init__(self, config: Union[str, Dict, LunarConfig]):
        self._config = config
        if isinstance(self._config, str):
            self._config = get_config(settings_file_path=config)
        elif isinstance(self._config, dict):
            self._config = LunarConfig.parse_obj(config)
        self._persistence_layer = PersistenceLayer(config=self._config)
        self._workflow_search_index = WorkflowSearchIndex(config=self._config)

    @property
    def config(self):
        return self._config

    @property
    def persistence_layer(self):
        return self._persistence_layer

    async def tmp_save(self, workflow: WorkflowModel, user_id: str):
        tmp_path = self._persistence_layer.get_user_tmp(user_id)
        return await self._persistence_layer.save_to_storage_as_json(
            path=os.path.join(tmp_path, f"{workflow.id}.json"),
            data=json.loads(workflow.json(by_alias=True)),
        )

    async def tmp_delete(self, workflow_id: str, user_id: str):
        tmp_path = self._persistence_layer.get_user_tmp(user_id)
        return await self._persistence_layer.delete(
            path=os.path.join(tmp_path, f"{workflow_id}.json")
        )

    async def save(self, workflow: Optional[WorkflowModel], user_id: str):
        if workflow is None:
            workflow = WorkflowModel(
                name="Untitled",
                description="",
            )
        self._persistence_layer.init_workflow_dirs(
            user_id=user_id, workflow_id=workflow.id
        )
        self._workflow_search_index.index([workflow], user_id)
        return await self._persistence_layer.save_to_storage_as_json(
            path=os.path.join(
                self._persistence_layer.get_user_workflow_root(user_id),
                workflow.id,
                f"{workflow.id}.json",
            ),
            data=json.loads(workflow.json(by_alias=True)),
        )

    async def auto_create(self, auto_workflow: AutoWorkflow, user_id: str):
        return await self.save(auto_workflow.generate_workflow(), user_id)

    async def auto_modify(
        self, auto_workflow: AutoWorkflow, instruction: str, user_id: str
    ):
        return await self.save(
            auto_workflow.generate_workflow_modification(instruction), user_id
        )

    async def update(self, workflow: WorkflowModel, user_id: str):
        self._workflow_search_index.remove_document(workflow.id, user_id)
        return await self.save(workflow, user_id)

    async def list_all(self, user_id="*"):
        self._persistence_layer.get_user_workflow_root(user_id),
        flow_list = await self._persistence_layer.get_all_as_dict(
            path=os.path.join(
                self._config.USER_DATA_PATH,
                "*",
                self._config.USER_WORKFLOW_ROOT,
                "*.json",
            )
        )

        flow_list = map(lambda chain: WorkflowModel.model_validate(chain), flow_list)

        return list(flow_list)

    async def list_short(self, user_id="*"):
        workflow_list = await self._persistence_layer.get_all_as_dict(
            path=os.path.join(
                self._config.USER_DATA_PATH,
                user_id,
                self._config.USER_WORKFLOW_ROOT,
                "*",
                "*.json",
            )
        )

        parsed_workflows = []
        for workflow in workflow_list:
            try:
                parsed_workflows.append(
                    WorkflowModel.model_validate(workflow).short_model()
                )
            except ValidationError as validation_error:
                warnings.warn(f"Failed to parse workflow:\n{validation_error}")
                continue

        return list(parsed_workflows)

    async def get_by_id(self, workflow_id: str, user_id: str):
        flow = await self._persistence_layer.get_from_storage_as_dict(
            path=os.path.join(
                self._persistence_layer.get_user_workflow_root(user_id),
                workflow_id,
                f"{workflow_id}.json",
            )
        )
        return WorkflowModel.model_validate(flow)

    async def delete(self, workflow_id: str, user_id: str):
        self._workflow_search_index.remove_document(workflow_id, user_id)
        return await self._persistence_layer.delete(
            path=os.path.join(
                self._persistence_layer.get_user_workflow_root(user_id), workflow_id
            )
        )

    async def search(self, query: str, user_id: str):
        return self._workflow_search_index.search(query, user_id)

    async def run(self, workflow: WorkflowModel, user_id: Optional[str] = None):
        workflow = WorkflowModel.model_validate(workflow)
        user_id = user_id or self._config.DEFAULT_USER_PROFILE

        venv_dir = self._persistence_layer.get_workflow_venv(
            user_id=user_id, workflow_id=workflow.id
        )

        env_path = self._persistence_layer.get_user_environment_path(user_id)
        environment = dict()
        if os.path.isfile(env_path):
            environment.update(dotenv_values(env_path))

        if not os.path.isdir(venv_dir):
            workflow_path = await self.save(workflow, user_id=user_id)
            result = await run_workflow_as_prefect_flow(
                workflow_path=workflow_path, venv=venv_dir, environment=environment
            )

        else:
            workflow_path = await self.tmp_save(workflow=workflow, user_id=user_id)

            result = await run_workflow_as_prefect_flow(
                workflow_path=workflow_path, venv=venv_dir, environment=environment
            )

            await self.tmp_delete(workflow_id=workflow.id, user_id=user_id)

        return result
