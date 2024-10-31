# SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os.path
from pathlib import Path

from dotenv import dotenv_values
from pydantic import Field, field_validator, model_validator, field_serializer, Extra
from pydantic_settings import BaseSettings, SettingsConfigDict
from enum import Enum
from typing import Optional, ClassVar

DEFAULT_PROFILE = "default"


# LUNAR_ROOT = Path(__file__).parent.parent.parent.as_posix()
# LUNAR_PACKAGE_PATH = Path(__file__).parent.parent.as_posix()
# LUNAR_PACKAGE_NAME = os.path.basename(LUNAR_PACKAGE_PATH)
#
# COMPONENT_PACKAGE_NAME = "component_library"
# COMPONENT_PACKAGE_PATH = os.path.join(LUNAR_PACKAGE_PATH, COMPONENT_PACKAGE_NAME)

COMPONENT_EXAMPLE_WORKFLOW_NAME = "example.json"


class Storage(Enum):
    # S3 = "S3" # S3 Disabled for now
    LOCAL = "LOCAL"
    # AZURE = "AZURE" # Work in progress


class LunarConfig(BaseSettings):
    DEFAULT_ENV: ClassVar = (
        f"{Path(__file__).parent.parent.parent.parent.parent.as_posix()}/.env"
    )

    LUNAR_STORAGE_TYPE: str = Field(default="LOCAL")
    LUNAR_STORAGE_BASE_PATH: str = Field(default="./")
    USER_DATA_PATH: str = Field(default="users")
    SYSTEM_DATA_PATH: str = Field(default="system")

    COMPONENT_LIBRARY_PATH: str = Field(default="component_library")
    COMPONENT_EXAMPLE_WORKFLOW_NAME = "example.json"

    DEMO_STORAGE_PATH: str = Field(default="demos")
    BASE_VENV_PATH: str = Field(default="base_venv")
    INDEX_DIR_PATH: str = Field(default="indexes")

    WORKFLOW_INDEX_NAME: str = Field(default="workflow_index")
    COMPONENT_INDEX_NAME: str = Field(default="component_index")

    PERSISTENT_REGISTRY_STARTUP_FILE: str = Field(default="./components.json")
    PERSISTENT_REGISTRY_NAME: str = Field(default="registry.json")

    LUNAR_S3_STORAGE_KEY: Optional[str] = Field(default=None)
    LUNAR_S3_STORAGE_SECRET: Optional[str] = Field(default=None)
    LUNAR_S3_STORAGE_HOST: Optional[str] = Field(default=None)
    LUNAR_S3_STORAGE_PORT: Optional[str] = Field(default=None)

    LUNARBASE_PORT: int = Field(default=8088)
    LUNARBASE_ADDRESS: str = Field(default="0.0.0.0")

    REGISTRY_GITHUB_TOKEN: Optional[str] = Field(default=None)
    REGISTRY_ALWAYS_UPDATE: bool = Field(default=False)

    DEFAULT_USER_PROFILE: str = Field(default="admin")

    AZURE_ENDPOINT: Optional[str] = Field(default=None)
    AZURE_DEPLOYMENT: Optional[str] = Field(default=None)
    OPENAI_API_KEY: Optional[str] = Field(default=None)
    OPENAI_API_VERSION: Optional[str] = Field(default="2024-02-01")

    TMP_PATH: str = Field(default="tmp")
    OUT_PATH: str = Field(default="output")
    REPORT_PATH: str = Field(default="reports")
    FILES_PATH: str = Field(default="files")

    # USER SETTINGS
    USER_ENVIRONMENT_FILE: str = Field(default=".env")
    USER_WORKFLOW_ROOT: str = Field(default="workflows")
    USER_FILE_ROOT: str = Field(default="files")
    USER_WORKFLOW_VENV_ROOT: str = Field(default="venv")
    USER_COMPONENT_VENV_ROOT: str = Field(default="default_component_venv")

    USER_INDEX_ROOT: str = Field(default="indexes")
    USER_SSL_CERT_ROOT: str = Field(default="ssl_certs")
    USER_CUSTOM_ROOT: str = Field(default="custom_components")

    model_config = SettingsConfigDict(extra=Extra.ignore)

    @model_validator(mode="after")
    def validate_all(self):
        base_path = self.LUNAR_STORAGE_BASE_PATH or "./"
        base_path = os.path.abspath(base_path)

        self.SYSTEM_DATA_PATH = os.path.join(base_path, self.SYSTEM_DATA_PATH)
        self.USER_DATA_PATH = os.path.join(base_path, self.USER_DATA_PATH)
        self.BASE_VENV_PATH = os.path.join(self.SYSTEM_DATA_PATH, self.BASE_VENV_PATH)
        self.INDEX_DIR_PATH = os.path.join(self.SYSTEM_DATA_PATH, self.INDEX_DIR_PATH)
        self.PERSISTENT_REGISTRY_NAME = os.path.join(
            self.SYSTEM_DATA_PATH, self.PERSISTENT_REGISTRY_NAME
        )
        self.DEMO_STORAGE_PATH = os.path.join(
            self.SYSTEM_DATA_PATH, self.DEMO_STORAGE_PATH
        )
        self.COMPONENT_LIBRARY_PATH = os.path.join(
            self.SYSTEM_DATA_PATH, self.COMPONENT_LIBRARY_PATH
        )

        return self

    @field_validator("LUNAR_STORAGE_TYPE")
    @classmethod
    def validate_storage(cls, storage_value):
        storage_value = str(storage_value).upper()
        if storage_value not in Storage.__dict__["_member_names_"]:
            raise ValueError(
                "Unknown flow storage type type {}. Accepted types are {}.".format(
                    storage_value, Storage.__dict__["_member_names_"]
                )
            )
        # elif storage_value == Storage.AZURE:
        #     raise NotImplemented

        return Storage[storage_value]

    @field_serializer("LUNAR_STORAGE_TYPE", when_used="always")
    def serialize_flow_storage(value):
        if isinstance(value, Storage):
            return value.value
        return value

    def get_component_index(self):
        return os.path.join(self.INDEX_DIR_PATH, self.COMPONENT_INDEX_NAME)

    def get_workflow_index(self):
        return os.path.join(self.INDEX_DIR_PATH, self.WORKFLOW_INDEX_NAME)

    @staticmethod
    def get_config(
        settings_file_path: str,
        settings_encoding: str = "utf-8",
    ):
        if not os.path.isfile(settings_file_path):
            raise FileNotFoundError(
                f"Configuration file {settings_file_path} not found!"
            )

        settings = dotenv_values(settings_file_path, encoding=settings_encoding)
        config_model = LunarConfig.parse_obj(settings)

        return config_model


GLOBAL_CONFIG = None
if os.path.isfile(LunarConfig.DEFAULT_ENV):
    GLOBAL_CONFIG = LunarConfig.get_config(settings_file_path=LunarConfig.DEFAULT_ENV)
if GLOBAL_CONFIG is None:
    raise FileNotFoundError(LunarConfig.DEFAULT_ENV)
