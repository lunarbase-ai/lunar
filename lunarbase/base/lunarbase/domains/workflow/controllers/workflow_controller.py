from lunarbase.config import LunarConfig
from lunarbase.registry import LunarRegistry
from lunarbase.domains.workflow.repositories import WorkflowRepository
from lunarbase.modeling.data_models import WorkflowModel
from typing import Optional, List, Dict
from lunarbase.indexing.workflow_search_index import WorkflowSearchIndex
from lunarbase.agent_copilot import AgentCopilot
from lunarbase.persistence import PersistenceLayer
from prefect import get_client
from lunarcore.component.data_types import DataType


class WorkflowController:
    def __init__(
        self,
        config: LunarConfig,
        lunar_registry: LunarRegistry,
        workflow_repository: WorkflowRepository,
        agent_copilot: AgentCopilot,
        workflow_search_index: WorkflowSearchIndex,
    ):
        self._config = config
        self._lunar_registry = lunar_registry
        self._workflow_repository = workflow_repository
        self._agent_copilot = agent_copilot
        self._workflow_search_index = workflow_search_index

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
        pass

    async def get_workflow_component_inputs(self, workflow_id: str, user_id: str):
        workflow = self.workflow_repository.show(user_id, workflow_id)

        inputs = []
        for component in workflow.components:
            for input in component.inputs:
                is_none = input.value is None or \
                        input.value == "" or \
                        input.value == ":undef:" or \
                        input.data_type == DataType.LIST and input.value == []

                inputs.append({
                    "type": input.data_type,
                    "id": input.id,
                    "key": input.key,
                    "is_template_variable": False,
                    "value": input.value if not is_none else None
                })    

                for key, value in input.template_variables.items():
                    is_none = value is None or \
                        value == "" or \
                        value == ":undef:"

                    inputs.append({
                        "type": input.data_type,
                        "id": input.id,
                        "key": key,
                        "is_template_variable": True,
                        "value": value if not is_none else None
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
        pass

    async def stream_workflow_by_id(self, workflow_id: str, workflow_inputs: List[Dict], user_id: str):
        pass

    async def run(self, workflow: WorkflowModel, user_id: Optional[str] = None, event_dispatcher=None):
        pass
    
    