from lunarbase.config import LunarConfig
from lunarbase.registry import LunarRegistry
from lunarbase.domains.workflow.repositories import WorkflowRepository
from lunarbase.modeling.data_models import WorkflowModel
from typing import Optional, List, Dict
from lunarbase.indexing.workflow_search_index import WorkflowSearchIndex
from lunarbase.agent_copilot import AgentCopilot
from lunarbase.persistence import PersistenceLayer

class WorkflowController:
    def __init__(
        self,
        config: LunarConfig,
        lunar_registry: LunarRegistry,
        workflow_repository: WorkflowRepository,
        agent_copilot: AgentCopilot,
        workflow_search_index: WorkflowSearchIndex,
        persistence_layer: PersistenceLayer
    ):
        self._config = config
        self._lunar_registry = lunar_registry
        self._workflow_repository = workflow_repository
        self._agent_copilot = agent_copilot
        self._workflow_search_index = workflow_search_index
        self._persistence_layer = persistence_layer

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
        self.persistence_layer.init_workflow_dirs(
            user_id=user_id, workflow_id=workflow.id
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
        return self.workflow_repository.getAll(user_id)

    def list_short(self, user_id="*"):
        pass

    def get_by_id(self, workflow_id: str, user_id: str):
        pass

    def delete(self, workflow_id: str, user_id: str):
        pass

    def search(self, query: str, user_id: str):
        pass
    
    def cancel(self, workflow_id: str, user_id: str):
        pass

    async def get_workflow_component_inputs(self, workflow_id: str, user_id: str):
        pass

    async def get_workflow_component_outputs(self, workflow_id: str, user_id: str):
        pass

    async def run_workflow_by_id(self, workflow_id: str, workflow_inputs: List[Dict], user_id: str):
        pass

    async def stream_workflow_by_id(self, workflow_id: str, workflow_inputs: List[Dict], user_id: str):
        pass

    async def run(self, workflow: WorkflowModel, user_id: Optional[str] = None, event_dispatcher=None):
        pass
    
    