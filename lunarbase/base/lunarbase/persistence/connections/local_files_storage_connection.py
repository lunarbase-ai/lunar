
from lunarbase.persistence.connections.storage_connection import StorageConnection
from lunarbase.config import LunarConfig
from pathlib import Path
from typing import List

class LocalFilesStorageConnection(StorageConnection):
    def __init__(self, config: LunarConfig):
        super().__init__(config)

    def connect(self) -> "LocalFilesStorageConnection":
        return self


    def build_path(self, *parts) -> str:
        base_path = Path(*parts)
        return str(base_path)

    def glob(self, *parts, pattern: str) -> List[Path]:
        """Glob for files matching pattern under the path built from parts."""
        base_path = Path(*parts)
        return list(base_path.glob(pattern))

    def disconnect(self):
        pass