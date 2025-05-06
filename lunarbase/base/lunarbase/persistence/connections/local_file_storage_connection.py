
from lunarbase.persistence.connections.storage_connection import StorageConnection

class LocalFileStorageConnection(StorageConnection):
    def __init__(self):
        super().__init__()

    def connect(self) -> "LocalFileStorageConnection":
        return self

    def disconnect(self):
        pass