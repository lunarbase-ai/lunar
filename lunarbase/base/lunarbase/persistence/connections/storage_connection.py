from abc import ABC, abstractmethod


class StorageConnection(ABC):

    def __init__(self):
        pass
    
    @abstractmethod
    def connect(self) -> "StorageConnection":
        pass

    @abstractmethod
    def disconnect(self):
        pass