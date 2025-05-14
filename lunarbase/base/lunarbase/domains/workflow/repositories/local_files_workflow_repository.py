#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later

from typing import Optional, List
from lunarbase.config import LunarConfig
from lunarbase.domains.workflow.repositories.workflow_repository import WorkflowRepository
from lunarbase.persistence.connections.local_files_storage_connection import LocalFilesStorageConnection
import json
from lunarbase.modeling.data_models import WorkflowModel
from pydantic import ValidationError 
from lunarbase.persistence import PersistenceLayer
import uuid
from lunarbase.persistence.resolvers.file_path_resolver import FilePathResolver

class LocalFilesWorkflowRepository(WorkflowRepository):
    def __init__(
        self,
        connection: LocalFilesStorageConnection,
        config: LunarConfig,
        persistence_layer: PersistenceLayer,
        path_resolver: FilePathResolver
    ):
        super().__init__(connection, config)
        self._persistence_layer = persistence_layer
        self._path_resolver = path_resolver

    @property
    def persistence_layer(self):
        return self._persistence_layer

    @property
    def path_resolver(self):
        return self._path_resolver


    def save(self, user_id: str, workflow: Optional[WorkflowModel] = None) -> WorkflowModel:
        if workflow is None:
            workflow = WorkflowModel(
                name="Untitled",
                description="",
                id=str(uuid.uuid4()),
            )

        self.persistence_layer.init_workflow_dirs(user_id, workflow.id)

        workflow_path = self.connection.build_path(
            self.path_resolver.get_user_workflows_root_path(user_id), workflow.id, f"{workflow.id}.json"
        )

        workflow_dict = json.loads(workflow.model_dump_json(by_alias=True))

        self.connection.save_dict_as_json(workflow_path, workflow_dict)

        return workflow


    def tmp_save(self, user_id: str, workflow: WorkflowModel) -> WorkflowModel:
        tmp_path = self.path_resolver.get_user_tmp_root_path(user_id)
        workflow_path = self.connection.build_path(
            tmp_path,
            f"{workflow.id}.json"
        )

        workflow_dict = json.loads(workflow.model_dump_json(by_alias=True))

        self.connection.save_dict_as_json(workflow_path, workflow_dict)

        return workflow

    def delete(self, user_id: str, workflow_id: str) -> bool:
        workflow_path = self.path_resolver.get_user_workflow_path(workflow_id, user_id)
        return self.connection.delete(workflow_path)

    def tmp_delete(self, user_id: str, workflow_id: str) -> bool:
        tmp_path = self.path_resolver.get_user_tmp_root_path(user_id)
        workflow_path = self.connection.build_path(
            tmp_path,
            f"{workflow_id}.json"
        )
        return self.connection.delete(workflow_path)

    def update(self, user_id: str, workflow: WorkflowModel) -> WorkflowModel:        
        return self.save(user_id, workflow)

    def show(self, user_id: str, workflow_id: str) -> WorkflowModel:
        workflow_path = self.connection.build_path(
            self.path_resolver.get_user_workflows_root_path(user_id), workflow_id, f"{workflow_id}.json"
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
                self.path_resolver.get_user_workflows_root_path("*"),
                "*",
                "*.json"
            )
        else:
            workflows_path = self.connection.build_path(
                self.path_resolver.get_user_workflows_root_path(user_id),
                "*",
                "*.json"
            )


        workflows = self.connection.get_all_as_dict_from_json(workflows_path)

        return [WorkflowModel.model_validate(workflow) for workflow in workflows]

