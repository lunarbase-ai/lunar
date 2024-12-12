# SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import warnings
from pathlib import Path
from time import sleep
from typing import Dict, Optional, Union

from dotenv import dotenv_values

from lunarbase import LUNAR_CONTEXT
from lunarbase.auto_workflow import AutoWorkflow
from lunarbase.config import LunarConfig
from lunarbase.indexing.workflow_search_index import WorkflowSearchIndex
from lunarbase.orchestration.engine import run_workflow_as_prefect_flow
from lunarbase.persistence import PersistenceLayer
from lunarbase.utils import setup_logger
from lunarbase.modeling.data_models import WorkflowModel
from prefect import get_client
from prefect.client.schemas import SetStateStatus, StateType
from prefect.client.schemas.filters import (
    FlowRunFilter,
    FlowRunFilterName,
    FlowRunFilterState,
    FlowRunFilterStateType,
)
from prefect.client.schemas.sorting import FlowRunSort
from prefect.exceptions import ObjectNotFound
from prefect.states import Cancelling
from pydantic import ValidationError


class WorkflowController:
    def __init__(self, config: Union[str, Dict, LunarConfig]):
        self._config = config
        if isinstance(self._config, str):
            self._config = LunarConfig.get_config(settings_file_path=config)
        elif isinstance(self._config, dict):
            self._config = LunarConfig.parse_obj(config)
        self._persistence_layer = PersistenceLayer(config=self._config)
        self._workflow_search_index = WorkflowSearchIndex(config=self._config)
        self.__logger = setup_logger("workflow-controller")

    @property
    def config(self):
        return self._config

    @property
    def persistence_layer(self):
        return self._persistence_layer

    def tmp_save(self, workflow: WorkflowModel, user_id: str):
        tmp_path = self._persistence_layer.get_user_tmp(user_id)
        return self._persistence_layer.save_to_storage_as_json(
            path=str(Path(tmp_path, f"{workflow.id}.json")),
            data=json.loads(workflow.json(by_alias=True)),
        )

    def tmp_delete(self, workflow_id: str, user_id: str):
        tmp_path = self._persistence_layer.get_user_tmp(user_id)
        return self._persistence_layer.delete(
            path=str(Path(tmp_path, f"{workflow_id}.json"))
        )

    def save(self, workflow: Optional[WorkflowModel], user_id: str):
        if workflow is None:
            workflow = WorkflowModel(
                name="Untitled",
                description="",
            )
        self._persistence_layer.init_workflow_dirs(
            user_id=user_id, workflow_id=workflow.id
        )
        self._workflow_search_index.index([workflow], user_id)
        return self._persistence_layer.save_to_storage_as_json(
            path=str(
                Path(
                    self._persistence_layer.get_user_workflow_root(user_id),
                    workflow.id,
                    f"{workflow.id}.json",
                )
            ),
            data=json.loads(workflow.json(by_alias=True)),
        )

    def auto_create(self, auto_workflow: AutoWorkflow, user_id: str):
        return self.save(auto_workflow.generate_workflow(), user_id)

    def auto_modify(
        self, auto_workflow: AutoWorkflow, instruction: str, user_id: str
    ):
        return self.save(
            auto_workflow.generate_workflow_modification(instruction), user_id
        )

    def update(self, workflow: WorkflowModel, user_id: str):
        self._workflow_search_index.remove_document(workflow.id, user_id)
        return self.save(workflow, user_id)

    def list_all(self, user_id="*"):
        self._persistence_layer.get_user_workflow_root(user_id),
        flow_list = self._persistence_layer.get_all_as_dict(
            path=str(
                Path(
                    self._config.USER_DATA_PATH,
                    "*",
                    self._config.USER_WORKFLOW_ROOT,
                    "*.json",
                )
            )
        )

        flow_list = map(lambda chain: WorkflowModel.model_validate(chain), flow_list)

        return list(flow_list)

    def list_short(self, user_id="*"):
        workflow_list = self._persistence_layer.get_all_as_dict(
            path=str(
                Path(
                    self._config.USER_DATA_PATH,
                    user_id,
                    self._config.USER_WORKFLOW_ROOT,
                    "*",
                    "*.json",
                )
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

    def get_by_id(self, workflow_id: str, user_id: str):
        flow = self._persistence_layer.get_from_storage_as_dict(
            path=str(
                Path(
                    self._persistence_layer.get_user_workflow_root(user_id),
                    workflow_id,
                    f"{workflow_id}.json",
                )
            )
        )
        return WorkflowModel.model_validate(flow)

    def delete(self, workflow_id: str, user_id: str):
        self._workflow_search_index.remove_document(workflow_id, user_id)
        return self._persistence_layer.delete(
            path=str(
                Path(
                    self._persistence_layer.get_user_workflow_root(user_id), workflow_id
                )
            )
        )

    def search(self, query: str, user_id: str):
        return self._workflow_search_index.search(query, user_id)

    def cancel(self, workflow_id: str, user_id: str):
        # with get_client() as client:
        with get_client(sync_client=True) as client:
            # flow_run_data = client.read_flow_runs(
            flow_run_data = client.read_flow_runs(
                flow_run_filter=FlowRunFilter(
                    name=FlowRunFilterName(any_=[workflow_id]),
                    state=FlowRunFilterState(
                        type=FlowRunFilterStateType(
                            any_=[
                                StateType.RUNNING,
                                StateType.PAUSED,
                                StateType.PENDING,
                                StateType.SCHEDULED,
                            ]
                        )
                    ),
                ),
                sort=FlowRunSort.START_TIME_DESC,
                limit=1,
            )

            current_runs = [fd.dict() for fd in flow_run_data or []]
            if not len(current_runs):
                self.__logger.warn(
                    f"No runs found yet for workflow {workflow_id}. Let's give it a chance and try again ..."
                )
                sleep(3)
                flow_run_data = client.read_flow_runs(
                    flow_run_filter=FlowRunFilter(
                        name=FlowRunFilterName(any_=[workflow_id]),
                        state=FlowRunFilterState(
                            type=FlowRunFilterStateType(
                                any_=[
                                    StateType.RUNNING,
                                    StateType.PAUSED,
                                    StateType.PENDING,
                                    StateType.SCHEDULED,
                                ]
                            )
                        ),
                    ),
                    sort=FlowRunSort.START_TIME_DESC,
                    limit=1,
                )
                current_runs = [fd.dict() for fd in flow_run_data or []]
                if not len(current_runs):
                    self.__logger.error(
                        f"No runs found for workflow {workflow_id}. Nothing to cancel."
                    )
                    return

            self.__logger.info(
                f"Cancelling workflow {workflow_id} in run {current_runs[0]['id']} ..."
            )
            cancelling_state = Cancelling(message="Cancelling at admin's request!")
            try:
                # result = client.set_flow_run_state(
                result = client.set_flow_run_state(
                    flow_run_id=current_runs[0]["id"], state=cancelling_state
                )
            except ObjectNotFound:
                self.__logger.error(f"Flow run '{id}' not found!")

            if result.status == SetStateStatus.ABORT:
                self.__logger.error(
                    f"Flow run '{id}' was unable to be cancelled. Reason:"
                    f" '{result.details.reason}'"
                )
                return

            self.__logger.info(
                f"Workflow {workflow_id} in run {current_runs[0]['id']} "
                f"was successfully scheduled for cancellation with status: {result.status}"
            )

    def run(self, workflow: WorkflowModel, user_id: Optional[str] = None):
        workflow = WorkflowModel.model_validate(workflow)

        user_id = user_id or self._config.DEFAULT_USER_PROFILE

        venv_dir = self._persistence_layer.get_workflow_venv(
            user_id=user_id, workflow_id=workflow.id
        )

        env_path = self._persistence_layer.get_user_environment_path(user_id)
        environment = {"LUNAR_USERID": str(user_id)}
        if Path(env_path).is_file():
            environment.update(dotenv_values(env_path))

        # LUNAR_CONTEXT.lunar_registry.add_workflow_runtime(
        #     workflow_id=workflow.id, workflow_name=workflow.name
        # )

        if not Path(venv_dir).is_dir():
            workflow_path = self.save(workflow, user_id=user_id)
            result = run_workflow_as_prefect_flow(
                workflow_path=workflow_path, venv=venv_dir, environment=environment
            )

        else:
            workflow_path = self.tmp_save(workflow=workflow, user_id=user_id)

            result = run_workflow_as_prefect_flow(
                workflow_path=workflow_path, venv=venv_dir, environment=environment
            )

            self.tmp_delete(workflow_id=workflow.id, user_id=user_id)

        LUNAR_CONTEXT.lunar_registry.remove_workflow_runtime(workflow_id=workflow.id)

        return result
