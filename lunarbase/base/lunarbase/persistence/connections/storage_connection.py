from abc import ABC, abstractmethod


class StorageConnection(ABC):
    @abstractmethod
    def connect(self) -> "StorageConnection":
        pass

    @abstractmethod
    def disconnect(self):
        pass