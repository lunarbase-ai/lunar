#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later

import glob
import json
import os
import pathlib
import shutil
from pathlib import Path

from fastapi import UploadFile
from typing import Union, Dict, Optional

from prefect.filesystems import LocalFileSystem

from lunarcore.config import Storage, LunarConfig


class PersistenceLayer:
    def __init__(self, config: Union[str, Dict, LunarConfig]):
        self._config = config
        if isinstance(self._config, str):
            self._config = LunarConfig.get_config(settings_file_path=config)
        elif isinstance(self._config, dict):
            self._config = LunarConfig.parse_obj(config)

        self.flow_storage = LocalFileSystem(
            basepath=self._config.LUNAR_STORAGE_BASE_PATH
        )

    def init_local_storage(self):
        base_path = self._config.LUNAR_STORAGE_BASE_PATH or os.path.dirname(
            os.path.dirname(os.path.dirname(__file__))
        )
        base_path = os.path.abspath(base_path)
        Path(base_path).mkdir(parents=True, exist_ok=True)

        Path(self._config.SYSTEM_DATA_PATH).mkdir(parents=True, exist_ok=True)
        Path(self._config.USER_DATA_PATH).mkdir(parents=True, exist_ok=True)
        Path(self._config.BASE_VENV_PATH).mkdir(parents=True, exist_ok=True)
        Path(self._config.INDEX_DIR_PATH).mkdir(parents=True, exist_ok=True)
        Path(
            os.path.join(self._config.INDEX_DIR_PATH, self._config.COMPONENT_INDEX_NAME)
        ).mkdir(parents=True, exist_ok=True)
        Path(
            os.path.join(self._config.INDEX_DIR_PATH, self._config.WORKFLOW_INDEX_NAME)
        ).mkdir(parents=True, exist_ok=True)
        Path(self._config.DEMO_STORAGE_PATH).mkdir(parents=True, exist_ok=True)

    def get_user_tmp(self, user_id: str):
        return os.path.join(self._config.USER_DATA_PATH, user_id, self._config.TMP_PATH)

    def get_user_workflow_root(self, user_id: str):
        return os.path.join(
            self._config.USER_DATA_PATH, user_id, self._config.USER_WORKFLOW_ROOT
        )

    def get_user_environment_path(self, user_id: str):
        return os.path.join(
            self._config.USER_DATA_PATH, user_id, self._config.USER_ENVIRONMENT_FILE
        )

    def get_user_component_venv(self, user_id: str):
        return os.path.join(
            self._config.USER_DATA_PATH, user_id, self._config.USER_COMPONENT_VENV_ROOT
        )

    def get_workflow_venv(self, workflow_id: str, user_id: Optional[str] = None):
        if user_id is None:
            candidate_paths = list(
                pathlib.Path(self.config.USER_DATA_PATH).glob(
                    f"*/{self.config.USER_WORKFLOW_ROOT}/{workflow_id}"
                )
            )
            if len(candidate_paths) > 0:
                user_id = candidate_paths[0].parent.parent.name
        return os.path.join(
            self.get_user_workflow_root(user_id),
            workflow_id,
            self._config.USER_WORKFLOW_VENV_ROOT,
        )

    def get_user_component_index(self, user_id: str):
        return os.path.join(
            self._config.USER_DATA_PATH,
            user_id,
            self._config.USER_INDEX_ROOT,
            self._config.COMPONENT_INDEX_NAME,
        )

    def get_user_workflow_index(self, user_id: str):
        return os.path.join(
            self._config.USER_DATA_PATH,
            user_id,
            self._config.USER_INDEX_ROOT,
            self._config.WORKFLOW_INDEX_NAME,
        )

    def get_user_file_root(self, user_id):
        return os.path.join(
            self._config.USER_DATA_PATH, user_id, self._config.USER_FILE_ROOT
        )

    def get_user_custom_root(self, user_id: str):
        return os.path.join(
            self._config.USER_DATA_PATH, user_id, self._config.USER_CUSTOM_ROOT
        )

    def get_user_workflow_report_path(self, user_id: str, workflow_id: str):
        return os.path.join(
            self.get_user_workflow_root(user_id), workflow_id, self._config.REPORT_PATH
        )

    def get_user_workflow_path(self, workflow_id: str, user_id: Optional[str] = None):
        if user_id is None:
            candidate_paths = list(
                pathlib.Path(self.config.USER_DATA_PATH).glob(
                    f"*/{self.config.USER_WORKFLOW_ROOT}/{workflow_id}"
                )
            )
            if len(candidate_paths) > 0:
                user_id = candidate_paths[0].parent.parent.name
        return os.path.join(self.get_user_workflow_root(user_id), workflow_id)

    def get_user_workflow_files_path(self, user_id: str, workflow_id: str):
        return os.path.join(
            self.get_user_workflow_root(user_id), workflow_id, self._config.FILES_PATH
        )

    def get_user_workflow_notebook_path(self, user_id: str, workflow_id: str):
        return os.path.join(
            self.get_user_workflow_root(user_id), workflow_id, self._config.NOTEBOOK_PATH
        )

    def init_workflow_dirs(self, user_id: str, workflow_id: str):
        if self._config.LUNAR_STORAGE_TYPE != Storage.LOCAL:
            raise NotImplementedError("Only local storage is supported!")

        Path(
            os.path.join(
                self.get_user_workflow_root(user_id),
                workflow_id,
                self._config.REPORT_PATH,
            )
        ).mkdir(parents=True, exist_ok=True)

        Path(
            os.path.join(
                self.get_user_workflow_root(user_id),
                workflow_id,
                self._config.FILES_PATH,
            )
        ).mkdir(parents=True, exist_ok=True)

        Path(
            os.path.join(
                self.get_user_workflow_root(user_id),
                workflow_id,
                self._config.USER_WORKFLOW_VENV_ROOT,
            )
        ).mkdir(parents=True, exist_ok=True)

        Path(
            os.path.join(
                self.get_user_workflow_root(user_id),
                workflow_id,
                self._config.NOTEBOOK_PATH,
            )
        ).mkdir(parents=True, exist_ok=True)

    def init_user_profile(self, user_id: str):
        if self._config.LUNAR_STORAGE_TYPE != Storage.LOCAL:
            raise NotImplementedError("Only local storage is supported!")

        Path(self.get_user_workflow_root(user_id)).mkdir(parents=True, exist_ok=True)
        Path(self.get_user_file_root(user_id)).mkdir(parents=True, exist_ok=True)

        Path(
            os.path.join(
                self._config.USER_DATA_PATH, user_id, self._config.USER_INDEX_ROOT
            )
        ).mkdir(parents=True, exist_ok=True)
        Path(self.get_user_component_index(user_id)).mkdir(parents=True, exist_ok=True)
        Path(self.get_user_workflow_index(user_id)).mkdir(parents=True, exist_ok=True)

        Path(self.get_user_custom_root(user_id)).mkdir(parents=True, exist_ok=True)

        Path(self.get_user_tmp(user_id)).mkdir(parents=True, exist_ok=True)

        Path(self.get_user_environment_path(user_id)).touch(exist_ok=True)

    @property
    def config(self):
        return self._config

    async def save_file_to_storage(self, path: str, file: UploadFile):
        try:
            resolved_path = self.flow_storage._resolve_path(path=path)
        except ValueError as e:
            raise ValueError(f"Problem encountered with path {path}: {str(e)}!")

        if self._config.LUNAR_STORAGE_TYPE == Storage.LOCAL:
            try:
                await self.flow_storage.write_path(
                    f"{resolved_path}/{file.filename}", bytes()
                )
                with open(os.path.join(resolved_path, file.filename), "wb") as f:
                    while contents := file.file.read(1024 * 1024):
                        f.write(contents)
            except Exception as e:
                raise ValueError(
                    f"Something went wrong wile saving file {file.filename} to {str(resolved_path)}: {str(e)}"
                )
            finally:
                file.file.close()
        else:
            raise ValueError(
                f"{self._config.LUNAR_STORAGE_TYPE} storage is not implemented yet"
            )

        return str(resolved_path)

    async def save_file_to_storage_from_path(
        self, from_path_with_filename: str, to_path_dir: str
    ):
        filename = os.path.basename(from_path_with_filename)
        try:
            resolved_path = self.flow_storage._resolve_path(path=to_path_dir)
        except ValueError as e:
            raise ValueError(f"Problem encountered with path {to_path_dir}: {str(e)}!")

        if self._config.LUNAR_STORAGE_TYPE == Storage.LOCAL:
            try:
                await self.flow_storage.write_path(
                    f"{resolved_path}/{filename}", bytes()
                )
                shutil.copy(
                    from_path_with_filename, os.path.join(resolved_path, filename)
                )
            except Exception as e:
                raise ValueError(
                    f"Something went wrong wile saving file {filename} to {str(resolved_path)}: {str(e)}"
                )
        else:
            raise ValueError(
                f"{self._config.LUNAR_STORAGE_TYPE} storage is not implemented yet"
            )

        return str(resolved_path)
    
    async def file_exists(self, path: str) -> bool:
        return os.path.exists(path)

    async def get_file_by_path(self, path: str):
        data = await self.flow_storage.read_path(path)
        return data

    async def get_all_files(self, path: str):
        path = self.flow_storage._resolve_path(path)
        file_paths = glob.glob(str(path))
        return file_paths

    async def save_to_storage_as_json(self, path: str, data: Dict):
        try:
            resolved_path = self.flow_storage._resolve_path(path=path)
        except ValueError as e:
            raise ValueError(f"Problem encountered with path {path}: {str(e)}!")

        data = json.dumps(data, indent=2)
        try:
            write_result = await self.flow_storage.write_path(
                resolved_path.as_posix(), bytes(data, "utf-8")
            )
        except Exception as e:
            raise ValueError(
                f"Something went wrong wile saving file to {str(resolved_path)}: {str(e)}"
            )
        return write_result

    async def get_from_storage_as_dict(self, path: str):
        data = await self.flow_storage.read_path(path)
        return json.loads(data.decode("utf-8"))

    async def get_all_as_dict(self, path: str):
        try:
            resolved_path = self.flow_storage._resolve_path(path=path)
        except ValueError as e:
            raise ValueError(f"Problem encountered with path {path}: {str(e)}!")
        elements = []
        if self._config.LUNAR_STORAGE_TYPE == Storage.LOCAL:
            try:
                element_paths = glob.glob(str(resolved_path))
            except FileNotFoundError:
                element_paths = []

            for element_path in element_paths:
                if not str(element_path).lower().endswith(".json"):
                    continue
                element = await self.get_from_storage_as_dict(path=element_path)
                elements.append(element)

        else:
            raise ValueError(
                f"Unknown storage type {self._config.LUNAR_STORAGE_TYPE}. Supported types: {self._config.LUNAR_STORAGE_TYPE.__class__.__dict__['_member_names_']}"
            )
        return elements

    async def delete(self, path: str):
        try:
            resolved_path = self.flow_storage._resolve_path(path=path)
        except ValueError as e:
            raise ValueError(f"Problem encountered with path {path}: {str(e)}!")

        if self._config.LUNAR_STORAGE_TYPE == Storage.LOCAL:
            if os.path.isdir(resolved_path):
                shutil.rmtree(str(resolved_path))
            else:
                if not os.path.isfile(resolved_path):
                    raise ValueError(f"File {str(resolved_path)} does not exist.")
                os.remove(str(resolved_path))
            return True
        else:
            raise ValueError(
                f"Unknown storage type {self._config.LUNAR_STORAGE_TYPE}. Supported types: {self._config.LUNAR_STORAGE_TYPE.__class__.__dict__['_member_names_']}"
            )
