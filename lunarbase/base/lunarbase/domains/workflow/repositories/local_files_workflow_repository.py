
from typing import Optional, List
from lunarbase.config import LunarConfig
from lunarbase.domains.workflow.repositories.workflow_repository import WorkflowRepository
from lunarbase.persistence.connections.local_files_storage_connection import LocalFilesStorageConnection
import json
from lunarbase.modeling.data_models import WorkflowModel
from pydantic import ValidationError 
from lunarbase.persistence import PersistenceLayer
import uuid

class LocalFilesWorkflowRepository(WorkflowRepository):
    def __init__(
        self,
        connection: LocalFilesStorageConnection,
        config: LunarConfig,
        persistence_layer: PersistenceLayer
    ):
        super().__init__(connection, config)
        self._persistence_layer = persistence_layer

    @property
    def persistence_layer(self):
        return self._persistence_layer


    def save(self, user_id: str, workflow: Optional[WorkflowModel] = None) -> WorkflowModel:
        if workflow is None:
            workflow = WorkflowModel(
                name="Untitled",
                description="",
                id=str(uuid.uuid4()),
            )

        self.persistence_layer.init_workflow_dirs(user_id, workflow.id)

        workflow_path = self.connection.build_path(
            self._get_user_workflows_root_path(user_id), workflow.id, f"{workflow.id}.json"
        )

        workflow_dict = json.loads(workflow.model_dump_json(by_alias=True))

        self.connection.save_dict_as_json(workflow_path, workflow_dict)

        return workflow


    def tmp_save(self, user_id: str, workflow: WorkflowModel) -> WorkflowModel:
        tmp_path = self._get_user_tmp_root_path(user_id)
        workflow_path = self.connection.build_path(
            tmp_path,
            f"{workflow.id}.json"
        )

        workflow_dict = json.loads(workflow.model_dump_json(by_alias=True))

        self.connection.save_dict_as_json(workflow_path, workflow_dict)

        return workflow

    def delete(self, user_id: str, workflow_id: str) -> bool:
        workflow_path = self.get_user_workflow_path(workflow_id, user_id)
        return self.connection.delete(workflow_path)

    def tmp_delete(self, user_id: str, workflow_id: str) -> bool:
        tmp_path = self._get_user_tmp_root_path(user_id)
        workflow_path = self.connection.build_path(
            tmp_path,
            f"{workflow_id}.json"
        )
        return self.connection.delete(workflow_path)

    def update(self, user_id: str, workflow: WorkflowModel) -> WorkflowModel:        
        return self.save(user_id, workflow)

    def show(self, user_id: str, workflow_id: str) -> WorkflowModel:
        workflow_path = self.connection.build_path(
            self._get_user_workflows_root_path(user_id), workflow_id, f"{workflow_id}.json"
        )
        workflow_dict = self.connection.get_as_dict_from_json(workflow_path)

        try:
            workflow = WorkflowModel.model_validate(workflow_dict)
        except ValidationError as e:
            raise ValueError(f"Dictionary is not a valid workflow model!")

        return workflow

    def get_all(self, user_id: Optional[str] = None) -> List[WorkflowModel]:
        if user_id is None:
            workflows_path = self.connection.build_path(
                self._get_user_workflows_root_path("*"),
                "*",
                "*.json"
            )
        else:
            workflows_path = self.connection.build_path(
                self._get_user_workflows_root_path(user_id),
                "*",
                "*.json"
            )


        workflows = self.connection.get_all_as_dict_from_json(workflows_path)

        return [WorkflowModel.model_validate(workflow) for workflow in workflows]

    
    def _get_user_workflows_root_path(self, user_id: str) -> str:
        return self.connection.build_path(
            self.config.USER_DATA_PATH, user_id, self.config.USER_WORKFLOW_ROOT
        )
    
    def _get_user_workflow_venv_path(self, workflow_id: str, user_id: str) -> str:
        workflow_root_path = self._get_user_workflows_root_path(user_id)
        return self.connection.build_path(
            workflow_root_path, workflow_id, self.config.USER_WORKFLOW_VENV_ROOT
        )
    
    def _get_user_workflows_index_path(self, user_id: str) -> str:
        return self.connection.build_path(
            self.config.USER_DATA_PATH,
            user_id,
            self.config.USER_INDEX_ROOT,
            self.config.WORKFLOW_INDEX_NAME,
        )
    
    def _get_user_workflow_reports_path(self, user_id: str, workflow_id: str) -> str:
        workflow_root_path = self._get_user_workflows_root_path(user_id)
        return self.connection.build_path(
            workflow_root_path, workflow_id, self.config.REPORT_PATH
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
        workflow_root = self._get_user_workflows_root_path(user_id)
        return self.connection.build_path(workflow_root, workflow_id)

    def _get_user_workflow_files_path(self, user_id: str, workflow_id: str) -> str:
        workflow_root_path = self._get_user_workflows_root_path(user_id)
        return self.connection.build_path(
            workflow_root_path, workflow_id, self.config.FILES_PATH
        )
    
    
    def _get_user_tmp_root_path(self, user_id: str) -> str:
        return self.connection.build_path(
            self.config.USER_DATA_PATH,
            user_id,
            self.config.TMP_PATH
        )