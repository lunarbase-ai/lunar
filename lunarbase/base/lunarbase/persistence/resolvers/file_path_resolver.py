#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
from abc import ABC, abstractmethod
from lunarbase.persistence.connections.storage_connection import StorageConnection
from lunarbase.config import LunarConfig
from typing import Optional


class FilePathResolver(ABC):
    def __init__(self, connection: StorageConnection, config: LunarConfig):
        self._connection = connection.connect()
        self._config = config

    @property
    def connection(self):
        return self._connection

    @property
    def config(self):
        return self._config

    @abstractmethod
    def get_user_workflows_root_path(self, user_id: str) -> str:
        pass

    @abstractmethod
    def get_user_workflow_venv_path(self, workflow_id: str, user_id: str) -> str:
        pass

    @abstractmethod
    def get_user_workflows_index_path(self, user_id: str) -> str:
        pass

    @abstractmethod
    def get_user_workflow_reports_path(self, user_id: str, workflow_id: str) -> str:
        pass

    @abstractmethod
    def get_user_workflow_files_path(self, user_id: str, workflow_id: str) -> str:
        pass

    @abstractmethod
    def get_user_workflow_path(self, workflow_id: str, user_id: Optional[str] = None) -> str:
        pass

    @abstractmethod
    def get_user_workflow_json_path(self, workflow_id: str, user_id: Optional[str] = None) -> str:
        pass

    @abstractmethod
    def get_user_tmp_root_path(self, user_id: str) -> str:
        pass

    @abstractmethod
    def get_user_datasources_root_path(self, user_id: str) -> str:
        pass