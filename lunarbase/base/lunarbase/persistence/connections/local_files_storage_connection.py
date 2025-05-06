
from lunarbase.persistence.connections.storage_connection import StorageConnection
from lunarbase.config import LunarConfig
from pathlib import Path

class LocalFilesStorageConnection(StorageConnection):
    def __init__(self, config: LunarConfig):
        super().__init__(config)

    def connect(self) -> "LocalFilesStorageConnection":
        return self

    def disconnect(self):
        pass

    def build_path(self, *parts) -> str:
        return str(Path(*parts))