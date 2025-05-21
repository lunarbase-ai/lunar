#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
from lunarbase.persistence.connections.storage_connection import StorageConnection
from lunarbase.config import LunarConfig
from pathlib import Path
from typing import List, Dict
import json
import shutil
import glob
import os
from fastapi import UploadFile

class LocalFilesStorageConnection(StorageConnection):
    def __init__(self, config: LunarConfig):
        super().__init__(config)

        self._lunar_base_path = self.config.LUNAR_STORAGE_BASE_PATH


    def connect(self) -> "LocalFilesStorageConnection":
        return self

    @property
    def lunar_base_path(self) -> str:
        return self._lunar_base_path

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

    def get_as_dict_from_json(self, path: str) -> Dict:
        try:
            content = self.read_path(path)
            return json.loads(content.decode("utf-8"))
        except Exception as e:
            raise ValueError(
                f"Problem encountered with path {path}: {str(e)}!"
            )

    def get_all_as_dict_from_json(self, path: str) -> List[Dict]:
        try:
            resolved_path = self._resolve_path(path)
        except ValueError as e:
            raise ValueError(f"Problem encountered with path {path}: {str(e)}!")
        elements = []
        try:
            element_paths = glob.glob(str(resolved_path))
        except FileNotFoundError:
            element_paths = []
        for element_path in element_paths:
            if not element_path.lower().endswith(".json"):
                continue
            elements.append(self.get_as_dict_from_json(element_path))
        return elements

    def read_path(self, path: str) -> bytes:
        """
        TODO: This is blocking while reading
        """
        path: Path = self._resolve_path(path)

        if not path.exists():
            raise ValueError(f"Path {path} does not exist.")

        if not path.is_file():
            raise ValueError(f"Path {path} is not a file.")

        with open(path, mode="rb") as f:
            content = f.read()

        return content

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


    def delete(self, path: str) -> bool:
        try:
            resolved_path = self._resolve_path(path=path)
        except ValueError as e:
            raise ValueError(f"Problem encountered with path {path}: {str(e)}!")

        if Path(resolved_path).is_dir():
            shutil.rmtree(str(resolved_path))
        else:
            Path(resolved_path).unlink(missing_ok=False)
        return True

    def exists(self, path: str) -> bool:
        try:
            resolved_path = self._resolve_path(path)
            
            return Path(resolved_path).exists()
        except ValueError:
            return False

    def _resolve_path(self, path: str) -> Path:
        basepath = (
            Path(self.lunar_base_path).expanduser().resolve()
            if self.lunar_base_path
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

    def remove_empty_directories(self, path: str, remove_root: bool = False) -> None:
        resolved_path = self._resolve_path(path)
        for dirpath, dirnames, filenames in os.walk(resolved_path, topdown=False):
            if not filenames and not dirnames:
                if Path(dirpath) == resolved_path and not remove_root:
                    continue
                try:
                    Path(dirpath).rmdir()
                except Exception as e:
                    print(f"Failed to remove {dirpath}: {e}")
    

    def save_file(self, path: str, file: UploadFile) -> str:
        try:
            resolved_path = self._resolve_path(path=path)
        except ValueError as e:
            raise ValueError(f"Problem encountered with path {path}: {str(e)}!")

        try:
            file_path = self.build_path(resolved_path, file.filename)
            self.write_path(file_path, bytes())
            with open(file_path, "wb") as f:
                while contents := file.file.read(1024 * 100):
                    f.write(contents)
        except Exception as e:
            raise ValueError(
                f"Something went wrong while saving file {file.filename} to {str(resolved_path)}: {str(e)}"
            )
        finally:
            file.file.close()

        return str(file_path)

    def disconnect(self):
        pass