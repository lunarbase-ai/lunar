
from abc import ABC, abstractmethod
from lunarbase.persistence.connections.storage_connection import StorageConnection
from lunarbase.modeling.data_models import WorkflowModel
from lunarbase.config import LunarConfig


class WorkflowRepository(ABC):
    def __init__(self, connection: StorageConnection, config: LunarConfig):
        self._connection = connection.connect()
        self._config = config

    # @abstractmethod
    # def save(self, workflow: WorkflowModel, user_id: str):
    #     pass