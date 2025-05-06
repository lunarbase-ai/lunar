
from lunarbase.persistence.connections.storage_connection import StorageConnection
from lunarbase.config import LunarConfig
from pathlib import Path
from typing import List, Dict
import json

class LocalFilesStorageConnection(StorageConnection):
    def __init__(self, config: LunarConfig):
        super().__init__(config)

        self._lunar_base_path = self._config.LUNAR_STORAGE_BASE_PATH

    def connect(self) -> "LocalFilesStorageConnection":
        return self


    def build_path(self, *parts) -> str:
        base_path = Path(*parts)
        return str(base_path)

    def glob(self, *parts, pattern: str) -> List[Path]:
        """Glob for files matching pattern under the path built from parts."""
        base_path = Path(*parts)
        return list(base_path.glob(pattern))

    def save_dict_as_json(self, path: str, data:Dict) -> str:
        try:
            resolved_path = self._resolve_path(path=path)
        except ValueError as e:
            raise ValueError(f"Problem encountered with path {path}: {str(e)}!")

        data = json.dumps(data, indent=2)
        try:
            return self.write_path(
                str(resolved_path), bytes(data, "utf-8")
            )
        except Exception as e:
            raise ValueError(
                f"Something went wrong wile saving file to {str(resolved_path)}: {str(e)}"
            )

    def write_path(self, path: str, content: bytes) -> str:
        """
        TODO: This is blocking while writing
        """
        path: Path = self._resolve_path(path)

        # Construct the path if it does not exist
        path.parent.mkdir(exist_ok=True, parents=True)

        # Check if the file already exists
        if path.exists() and not path.is_file():
            raise ValueError(f"Path {path} already exists and is not a file.")

        with open(path, mode="wb") as f:
            f.write(content)
        # Leave path stringify to the OS
        return str(path)

    def _resolve_path(self, path: str) -> Path:
        basepath = (
            Path(self._lunar_base_path).expanduser().resolve()
            if self._lunar_base_path
            else Path(".").resolve()
        )


        path: Path = Path(path).expanduser()

        if not path.is_absolute():
            path = basepath / path
        else:
            path = path.resolve()
            if basepath not in path.parents and (basepath != path):
                raise ValueError(
                    f"Provided path {path} is outside of the base path {basepath}."
                )

        return path

    def disconnect(self):
        pass