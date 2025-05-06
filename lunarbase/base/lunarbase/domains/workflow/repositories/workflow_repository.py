
from abc import ABC, abstractmethod
from lunarbase.persistence.connections.storage_connection import StorageConnection
from lunarbase.modeling.data_models import WorkflowModel
from lunarbase.config import LunarConfig
from typing import Optional


class WorkflowRepository(ABC):
    def __init__(self, connection: StorageConnection, config: LunarConfig):
        self._connection = connection.connect()
        self._config = config

    @abstractmethod
    def save(self, user_id: str, workflow: Optional[WorkflowModel] = None) -> WorkflowModel:
        pass