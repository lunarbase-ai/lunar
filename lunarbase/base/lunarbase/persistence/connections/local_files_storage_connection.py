
from lunarbase.persistence.connections.storage_connection import StorageConnection
from lunarbase.config import LunarConfig
class LocalFilesStorageConnection(StorageConnection):
    def __init__(self, config: LunarConfig):
        super().__init__(config)

    def connect(self) -> "LocalFilesStorageConnection":
        return self

    def disconnect(self):
        pass

    def teste(self) -> str:
        return 'teste'