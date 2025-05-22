#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
import asyncio
from lunarbase.config import LunarConfig
from lunarbase.registry import LunarRegistry
from lunarbase.domains.workflow.repositories import WorkflowRepository
from lunarbase.modeling.data_models import WorkflowModel
from typing import Optional, List, Dict
from lunarbase.indexing.workflow_search_index import WorkflowSearchIndex
from lunarbase.agent_copilot import AgentCopilot
from lunarbase.persistence import PersistenceLayer

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
from lunarbase.domains.workflow.event_dispatcher import QueuedEventDispatcher

from lunarcore.component.data_types import DataType
from lunarbase.utils import setup_logger
from dotenv import dotenv_values
from pathlib import Path
from time import sleep
from lunarbase.orchestration.engine import LunarEngine
from lunarbase.persistence.resolvers import FilePathResolver
from lunarbase.domains.workflow.event_dispatcher import EventDispatcher

class WorkflowController:
    def __init__(
        self,
        config: LunarConfig,
        lunar_registry: LunarRegistry,
        lunar_engine: LunarEngine,
        workflow_repository: WorkflowRepository,
        agent_copilot: AgentCopilot,
        workflow_search_index: WorkflowSearchIndex,
        persistence_layer: PersistenceLayer,
        path_resolver: FilePathResolver
    ):
        self._config = config
        self._lunar_registry = lunar_registry
        self._lunar_engine = lunar_engine
        self._workflow_repository = workflow_repository
        self._agent_copilot = agent_copilot
        self._workflow_search_index = workflow_search_index
        self._persistence_layer = persistence_layer
        self._path_resolver = path_resolver
        self.__logger = setup_logger("workflow-controller")

    @property
    def config(self):
        return self._config

    @property
    def lunar_registry(self):
        return self._lunar_registry
    
    @property
    def workflow_repository(self):
        return self._workflow_repository
    
    @property
    def agent_copilot(self):
        return self._agent_copilot
    
    @property
    def workflow_search_index(self):
        return self._workflow_search_index
    
    @property
    def persistence_layer(self):
        return self._persistence_layer
    
    @property
    def path_resolver(self):
        return self._path_resolver

    def tmp_save(self, workflow: WorkflowModel, user_id: str):
        return self.workflow_repository.tmp_save(user_id, workflow)

    def tmp_delete(self, workflow_id: str, user_id: str):
        return self.workflow_repository.tmp_delete(user_id, workflow_id)

    def save(self, workflow: Optional[WorkflowModel], user_id: str):
        if workflow is None:
            workflow = WorkflowModel(
                name="Untitled",
                description="",
            )
        self.workflow_search_index.index([workflow], user_id)

        return self.workflow_repository.save(user_id, workflow)

    def auto_create(self, intent: str, user_id: str):
        new_workflow = self.agent_copilot.generate_workflow(intent)

        return self.save(new_workflow, user_id)

    def auto_modify(self, workflow: WorkflowModel, intent: str, user_id: str):
        new_workflow = self.agent_copilot.modify_workflow(workflow, intent)
        
        return self.save(new_workflow, user_id)

    def update(self, workflow: WorkflowModel, user_id: str):
        self.workflow_search_index.remove_document(workflow.id, user_id)
        return self.save(workflow, user_id)

    def list_all(self, user_id="*"):
        return self.workflow_repository.get_all(user_id)

    def list_short(self, user_id="*"):
        workflow_list = self.workflow_repository.get_all(user_id)
        return [w.short_model() for w in workflow_list]

    def get_by_id(self, workflow_id: str, user_id: str):
        return self.workflow_repository.show(user_id, workflow_id)

    def delete(self, workflow_id: str, user_id: str):
        self.workflow_search_index.remove_document(workflow_id, user_id)
        return self.workflow_repository.delete(user_id, workflow_id)

    def search(self, query: str, user_id: str):
        return self.workflow_search_index.search(query, user_id)
    
    def cancel(self, workflow_id: str, user_id: str):
        with get_client(sync_client=True) as client:
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
        workflow = self.workflow_repository.show(user_id, workflow_id)


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
        workflow = self.workflow_repository.show(user_id, workflow_id)
        
        sources = [dep.source_label for dep in workflow.dependencies]
        sources_set = set(sources)
        
        labels = [comp.label for comp in workflow.components]
        labels_set = set(labels)

        outputs = labels_set - sources_set

        return list(outputs)

    async def run_workflow_by_id(self, workflow_id: str, workflow_inputs: List[Dict], user_id: str):
        workflow = self.workflow_repository.show(user_id, workflow_id)
        
        for component in workflow.components:
            for input in component.inputs:
                for new_input in workflow_inputs:
                    if input.key == new_input["key"]:
                        input.value = new_input["value"]
        return await self.run(workflow, user_id)
                        

    async def stream_workflow_by_id(self, workflow_id: str, workflow_inputs: List[Dict], user_id: str):
        workflow = self.workflow_repository.show(user_id, workflow_id)
        for component in workflow.components:
            for input in component.inputs:
                for new_input in workflow_inputs:
                    if input.key == new_input["key"]:
                        input.value = new_input["value"]
        queue: asyncio.Queue = asyncio.Queue()
        dispatcher = QueuedEventDispatcher(workflow_id, queue)
        run_task = asyncio.create_task(self.run(workflow, user_id, dispatcher))
        while True:
            if run_task.done() and queue.empty():
                break
            try:
                event = await asyncio.wait_for(queue.get(), timeout=0.1)
                yield event
            except asyncio.TimeoutError:
                continue
        final_result = await run_task
        return

    async def run(self, workflow: WorkflowModel, user_id: Optional[str] = None, event_dispatcher: Optional[EventDispatcher] = None):
        workflow = WorkflowModel.model_validate(workflow)
        
        user_id = user_id or self.config.DEFAULT_USER_PROFILE

        venv_dir = self.persistence_layer.get_workflow_venv(
            user_id=user_id, workflow_id=workflow.id
        )

        env_path = self.persistence_layer.get_user_environment_path(user_id)
        environment = {"LUNAR_USERID": str(user_id)}
        if Path(env_path).is_file():
            environment.update(dotenv_values(env_path))

        for component in workflow.components:
            for input in component.inputs:
                if input.key.lower() == "workflow" and isinstance(input.value, str):
                    workflow_id = input.value
                    input.value = self.get_by_id(workflow_id, user_id).dict()


        workflow_path = Path(self.path_resolver.get_user_workflow_json_path(workflow.id, user_id))
        if Path(workflow_path).exists():
            self.workflow_repository.update(user_id=user_id, workflow=workflow)
            result = await self._lunar_engine.run_workflow_as_prefect_flow(
                lunar_registry=self.lunar_registry, workflow_path=str(workflow_path), 
                venv=venv_dir, environment=environment, event_dispatcher=event_dispatcher
            )
        else:
            self.__logger.info(f"Workflow {workflow.id} does not exist in {workflow_path}. Saving to tmp and running.")
            self.workflow_repository.tmp_save(user_id=user_id, workflow=workflow)
            workflow_path = str(Path(self.path_resolver.get_user_tmp_root_path(user_id), f"{workflow.id}.json"))

            result = await self._lunar_engine.run_workflow_as_prefect_flow(
                lunar_registry=self.lunar_registry, workflow_path=workflow_path, 
                venv=venv_dir, environment=environment, event_dispatcher=event_dispatcher
            )

            self.workflow_repository.tmp_delete(user_id=user_id, workflow_id=workflow.id)

        self.lunar_registry.remove_workflow_runtime(workflow_id=workflow.id)

        return result
    
    