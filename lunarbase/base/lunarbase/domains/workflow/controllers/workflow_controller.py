from lunarbase.config import LunarConfig
from lunarbase.registry import LunarRegistry
from lunarbase.domains.workflow.repositories import WorkflowRepository
from lunarbase.modeling.data_models import WorkflowModel
from typing import Optional, List, Dict


class WorkflowController:
    def __init__(
        self,
        config: LunarConfig,
        lunar_registry: LunarRegistry,
        workflow_repository: WorkflowRepository,
        agent_copilot: AgentCopilot
    ):
        self._config = config
        self._lunar_registry = lunar_registry
        self._workflow_repository = workflow_repository
        self._agent_copilot = agent_copilot

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


    def tmp_save(self, workflow: WorkflowModel, user_id: str):
        return self.workflow_repository.tmp_save(user_id, workflow)

    def tmp_delete(self, workflow_id: str, user_id: str):
        return self.workflow_repository.tmp_delete(user_id, workflow_id)

    def save(self, workflow: Optional[WorkflowModel], user_id: str):
        pass

    def auto_create(self, intent: str, user_id: str):
        pass

    def auto_modify(self, workflow: WorkflowModel, intent: str, user_id: str):
        pass

    def update(self, workflow: WorkflowModel, user_id: str):
        pass

    def list_all(self, user_id="*"):
        pass

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
    
    