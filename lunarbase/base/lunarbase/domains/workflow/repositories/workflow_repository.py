
from abc import ABC, abstractmethod
from lunarbase.persistence.connections.storage_connection import StorageConnection
from lunarbase.modeling.data_models import WorkflowModel


class WorkflowRepository(ABC):
    def __init__(self, connection: StorageConnection):
        self._connection = connection

    @abstractmethod
    def save(self, workflow: WorkflowModel, user_id: str):
        pass