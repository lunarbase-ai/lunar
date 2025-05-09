# SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import warnings
from pathlib import Path
from time import sleep
from typing import Dict, List, Optional, Union

from dotenv import dotenv_values
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from pydantic import ValidationError
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

from lunarbase.agent_copilot import AgentCopilot
from lunarbase.config import LunarConfig
from lunarbase.domains.workflow.event_dispatcher import EventDispatcher
from lunarbase.indexing.workflow_search_index import WorkflowSearchIndex
from lunarbase.modeling.data_models import WorkflowModel
from lunarbase.orchestration.engine import run_workflow_as_prefect_flow
from lunarbase.persistence import PersistenceLayer
from lunarbase.registry import LunarRegistry
from lunarbase.utils import setup_logger

from lunarcore.component.data_types import DataType


class WorkflowController:
    def __init__(self, config: Union[str, Dict, LunarConfig], lunar_registry: LunarRegistry):
        self._config = config
        self._lunar_registry=lunar_registry
        self._persistence_layer = PersistenceLayer(config=self._config)
        self._workflow_search_index = WorkflowSearchIndex(config=self._config)
        self.__logger = setup_logger("workflow-controller")
        llm = AzureChatOpenAI(
            openai_api_version=config.AZURE_OPENAI_API_VERSION,
            deployment_name=config.AZURE_OPENAI_DEPLOYMENT,
            openai_api_key=config.AZURE_OPENAI_API_KEY,
            azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
            model_name=config.AZURE_OPENAI_MODEL_NAME,
        )
        embeddings = AzureOpenAIEmbeddings(
            openai_api_version=config.AZURE_OPENAI_API_VERSION,
            model=config.AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT,
            openai_api_key=config.AZURE_OPENAI_API_KEY,
            azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
        )
        self._agent_copilot = AgentCopilot(
            lunar_config=self._config,
            lunar_registry=self._lunar_registry,
            llm=llm,
            embeddings=embeddings,
            vector_store=InMemoryVectorStore,
        )

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

    def auto_create(self, intent: str, user_id: str):
        new_workflow = self._agent_copilot.generate_workflow(intent)
        self.save(new_workflow, user_id)
        return new_workflow

    def auto_modify(
        self, workflow: WorkflowModel, intent: str, user_id: str
    ):
        new_workflow = self._agent_copilot.modify_workflow(workflow, intent)
        self.save(new_workflow, user_id)
        return new_workflow

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

    async def get_workflow_component_inputs(self, workflow_id: str, user_id: str):
        workflow = self.get_by_id(workflow_id, user_id)

        inputs = []
        for component in workflow.components:
            for input in component.inputs:
                if input.value is None or \
                        input.value == "" or \
                        input.value == ":undef:" or \
                        input.data_type == DataType.LIST and input.value == []:
                    inputs.append({
                        "type": input.data_type,
                        "id": input.id,
                        "key": input.key,
                        "is_template_variable": False,
                        "value": None
                    })
                for key, value in input.template_variables.items():
                    if value is None or value == "" or value == ":undef:":
                        inputs.append({
                            "type": input.data_type,
                            "id": input.id,
                            "key": key,
                            "is_template_variable": True,
                            "value": None
                        })

        return {
            "name": workflow.name,
            "description": workflow.description,
            "inputs": inputs
        }

    async def get_workflow_component_outputs(self, workflow_id: str, user_id: str):
        workflow = self.get_by_id(workflow_id, user_id)

        sources = [dep.source_label for dep in workflow.dependencies]
        sources_set = set(sources)
        labels = [comp.label for comp in workflow.components]
        labels_set = set(labels)

        outputs = labels_set - sources_set

        return list(outputs)

    async def run_workflow_by_id(self, workflow_id: str, workflow_inputs: List[Dict], user_id: str):
        workflow = self.get_by_id(workflow_id, user_id)
        for component in workflow.components:
            for input in component.inputs:
                for new_input in workflow_inputs:
                    if input.key == new_input["key"]:
                        input.value = new_input["value"]

        return await self.run(workflow, user_id)

    async def stream_workflow_by_id(self, workflow_id: str, workflow_inputs: List[Dict], user_id: str):
        workflow = self.get_by_id(workflow_id, user_id)
        for component in workflow.components:
            for input in component.inputs:
                for new_input in workflow_inputs:
                    if input.key == new_input["key"]:
                        input.value = new_input["value"]
        event_dispatcher = EventDispatcher(workflow_id=workflow_id)
        return await self.run(workflow, user_id, event_dispatcher)

    async def run(self, workflow: WorkflowModel, user_id: Optional[str] = None, event_dispatcher=None):
        workflow = WorkflowModel.model_validate(workflow)

        user_id = user_id or self._config.DEFAULT_USER_PROFILE

        venv_dir = self._persistence_layer.get_workflow_venv(
            user_id=user_id, workflow_id=workflow.id
        )

        env_path = self._persistence_layer.get_user_environment_path(user_id)
        environment = {"LUNAR_USERID": str(user_id)}
        if Path(env_path).is_file():
            environment.update(dotenv_values(env_path))

        for component in workflow.components:
            for input in component.inputs:
                if input.key.lower() == "workflow" and isinstance(input.value, str):
                    workflow_id = input.value
                    input.value = self.get_by_id(workflow_id, user_id).dict()

        if not Path(venv_dir).is_dir():
            workflow_path = self.save(workflow, user_id=user_id)
            result = await run_workflow_as_prefect_flow(
                lunar_registry=self._lunar_registry, workflow_path=workflow_path, 
                venv=venv_dir, environment=environment
            )

        else:
            workflow_path = self.tmp_save(workflow=workflow, user_id=user_id)

            result = await run_workflow_as_prefect_flow(
                lunar_registry=self._lunar_registry, workflow_path=workflow_path, 
                venv=venv_dir, environment=environment, event_dispatcher=event_dispatcher
            )

            self.tmp_delete(workflow_id=workflow.id, user_id=user_id)

        self._lunar_registry.remove_workflow_runtime(workflow_id=workflow.id)

        return result