from abc import ABC, abstractmethod
from lunarbase.persistence.connections.storage_connection import StorageConnection
from lunarbase.modeling.data_models import WorkflowModel
from lunarbase.config import LunarConfig
from typing import Optional
from lunarbase.persistence.repositories.base_repository import LunarRepository


class WorkflowRepository(LunarRepository):
    def __init__(self, connection: StorageConnection, config: LunarConfig):
        super().__init__(connection, config)

    @abstractmethod
    def save(self, user_id: str, workflow: Optional[WorkflowModel] = None) -> WorkflowModel:
        pass

    @abstractmethod
    def update(self, user_id: str, workflow: WorkflowModel) -> WorkflowModel:
        pass

    @abstractmethod
    def show(self, user_id: str, workflow_id: str) -> WorkflowModel:
        pass
