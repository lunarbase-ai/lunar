from lunarbase.persistence.connections.storage_connection import StorageConnection
from lunarbase.config import LunarConfig
from lunarbase.persistence.resolvers.file_path_resolver import FilePathResolver
from typing import Optional


class LocalFilesPathResolver(FilePathResolver):
    def __init__(self, connection: StorageConnection, config: LunarConfig):
        super().__init__(connection, config)

    def get_user_workflows_root_path(self, user_id: str) -> str:
        return self.connection.build_path(
            self.config.USER_DATA_PATH, user_id, self.config.USER_WORKFLOW_ROOT
        )

    def get_user_workflow_venv_path(self, workflow_id: str, user_id: str) -> str:
        workflow_root_path = self.get_user_workflows_root_path(user_id)
        return self.connection.build_path(
            workflow_root_path, workflow_id, self.config.USER_WORKFLOW_VENV_ROOT
        )

    def get_user_workflows_index_path(self, user_id: str) -> str:
        return self.connection.build_path(
            self.config.USER_DATA_PATH,
            user_id,
            self.config.USER_INDEX_ROOT,
            self.config.WORKFLOW_INDEX_NAME,
        )

    def get_user_workflow_reports_path(self, user_id: str, workflow_id: str) -> str:
        workflow_root_path = self.get_user_workflows_root_path(user_id)
        return self.connection.build_path(
            workflow_root_path, workflow_id, self.config.REPORT_PATH
        )

    def get_user_workflow_files_path(self, user_id: str, workflow_id: str) -> str:
        workflow_root_path = self.get_user_workflows_root_path(user_id)
        return self.connection.build_path(
            workflow_root_path, workflow_id, self.config.FILES_PATH
        )

    def get_user_workflow_path(self, workflow_id: str, user_id: Optional[str] = None) -> str:
        if user_id is None:
            candidate_paths = self.connection.glob(
                self.config.USER_DATA_PATH,
                pattern=f"*/{self.config.USER_WORKFLOW_ROOT}/{workflow_id}"
            )
            if candidate_paths:
                user_id = candidate_paths[0].parent.parent.name
            else:
                raise FileNotFoundError(f"No workflow found with id {workflow_id}")
        workflow_root = self.get_user_workflows_root_path(user_id)
        return self.connection.build_path(workflow_root, workflow_id)

    def get_user_workflow_json_path(self, workflow_id: str, user_id: Optional[str] = None) -> str:
        workflow_path = self.get_user_workflow_path(workflow_id, user_id)
        return self.connection.build_path(workflow_path, f"{workflow_id}.json")

    def get_user_tmp_root_path(self, user_id: str) -> str:
        return self.connection.build_path(
            self.config.USER_DATA_PATH,
            user_id,
            self.config.TMP_PATH
        )