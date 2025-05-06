
from lunarbase.config import LunarConfig
from lunarbase.domains.workflow.repositories.workflow_repository import WorkflowRepository
from lunarbase.persistence.connections.local_files_storage_connection import LocalFilesStorageConnection
from lunarbase.modeling.data_models import WorkflowModel


class LocalFilesWorkflowRepository(WorkflowRepository):
    def __init__(self, connection: LocalFilesStorageConnection, config: LunarConfig):
        super().__init__(connection, config)

    def save(self, workflow: WorkflowModel, user_id: str):
        return user_id
    
    def teste(self) -> str:
        return 'teste'
    