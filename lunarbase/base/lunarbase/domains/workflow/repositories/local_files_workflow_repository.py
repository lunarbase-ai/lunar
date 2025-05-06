
from lunarbase.config import LunarConfig
from lunarbase.domains.workflow.repositories.workflow_repository import WorkflowRepository
from lunarbase.persistence.connections.local_files_storage_connection import LocalFilesStorageConnection
from lunarbase.modeling.data_models import WorkflowModel


class LocalFilesWorkflowRepository(WorkflowRepository):
    def __init__(self, connection: LocalFilesStorageConnection, config: LunarConfig):
        super().__init__(connection, config)
    
    def _build_user_workflows_root_path(self, user_id: str) -> str:
        return self._connection.build_path(
            self._config.USER_DATA_PATH, user_id, self._config.USER_WORKFLOW_ROOT
        )
    
    def _build_user_workflow_venv_path(self, workflow_id: str, user_id: str) -> str:
        workflow_root_path = self._build_user_workflows_root_path(user_id)
        return self._connection.build_path(
            workflow_root_path, workflow_id, self._config.USER_WORKFLOW_VENV_ROOT
        )
    
    def _build_user_workflows_index_path(self, user_id: str) -> str:
        return self._connection.build_path(
            self._config.USER_DATA_PATH,
            user_id,
            self._config.USER_INDEX_ROOT,
            self._config.WORKFLOW_INDEX_NAME,
        )
    
    def _build_user_workflow_reports_path(self, user_id: str, workflow_id: str) -> str:
        workflow_root_path = self._build_user_workflows_root_path(user_id)
        return self._connection.build_path(
            workflow_root_path, workflow_id, self._config.REPORT_PATH
        )

