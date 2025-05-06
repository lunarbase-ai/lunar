
from typing import Optional
from lunarbase.config import LunarConfig
from lunarbase.domains.workflow.repositories.workflow_repository import WorkflowRepository
from lunarbase.persistence.connections.local_files_storage_connection import LocalFilesStorageConnection
import json
from lunarbase.modeling.data_models import WorkflowModel


class LocalFilesWorkflowRepository(WorkflowRepository):
    def __init__(
        self,
        connection: LocalFilesStorageConnection,
        config: LunarConfig,
    ):
        super().__init__(connection, config)

    def save(self, user_id: str, workflow: Optional[WorkflowModel] = None) -> WorkflowModel:
        if workflow is None:
            workflow = WorkflowModel(
                name="Untitled",
                description="",
            )

        workflow_path = self._connection.build_path(
            self._get_user_workflows_root_path(user_id), workflow.id, f"{workflow.id}.json"
        )

        workflow_dict = json.loads(workflow.model_dump_json(by_alias=True))

        self._connection.save_dict_as_json(workflow_path, workflow_dict)

        return workflow
        
    
    def _get_user_workflows_root_path(self, user_id: str) -> str:
        return self._connection.build_path(
            self._config.USER_DATA_PATH, user_id, self._config.USER_WORKFLOW_ROOT
        )
    
    def _get_user_workflow_venv_path(self, workflow_id: str, user_id: str) -> str:
        workflow_root_path = self._get_user_workflows_root_path(user_id)
        return self._connection.build_path(
            workflow_root_path, workflow_id, self._config.USER_WORKFLOW_VENV_ROOT
        )
    
    def _get_user_workflows_index_path(self, user_id: str) -> str:
        return self._connection.build_path(
            self._config.USER_DATA_PATH,
            user_id,
            self._config.USER_INDEX_ROOT,
            self._config.WORKFLOW_INDEX_NAME,
        )
    
    def _get_user_workflow_reports_path(self, user_id: str, workflow_id: str) -> str:
        workflow_root_path = self._get_user_workflows_root_path(user_id)
        return self._connection.build_path(
            workflow_root_path, workflow_id, self._config.REPORT_PATH
        )
    
    # Pra testar isso eu preciso de um workflow_id que exista.
    def _get_user_workflow_path(self, workflow_id: str, user_id: Optional[str] = None) -> str:
        if user_id is None:
            candidate_paths = self._connection.glob(
                self._config.USER_DATA_PATH,
                pattern=f"*/{self._config.USER_WORKFLOW_ROOT}/{workflow_id}"
            )
            if candidate_paths:
                user_id = candidate_paths[0].parent.parent.name
            else:
                raise FileNotFoundError(f"No workflow found with id {workflow_id}")
        workflow_root = self._get_user_workflows_root_path(user_id)
        return self._connection.build_path(workflow_root, workflow_id)