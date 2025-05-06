
from lunarbase.domains.workflow.repositories.workflow_repository import WorkflowRepository
from lunarbase.persistence.connections.local_files_storage_connection import LocalFilesStorageConnection
from lunarbase.modeling.data_models import WorkflowModel


class LocalFilesWorkflowRepository(WorkflowRepository):
    def __init__(self, connection: LocalFilesStorageConnection):
        super().__init__(connection)

    def save(self, workflow: WorkflowModel, user_id: str):
        pass
    