
from lunarbase.persistence.connections.storage_connection import StorageConnection

class LocalFilesStorageConnection(StorageConnection):
    def __init__(self):
        super().__init__()

    def connect(self) -> "LocalFilesStorageConnection":
        return self

    def disconnect(self):
        pass

    def teste(self) -> str:
        return 'teste'