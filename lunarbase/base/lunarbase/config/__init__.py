# SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#
# SPDX-License-Identifier: GPL-3.0-or-later
import os
import pathlib
from pathlib import Path

from dotenv import dotenv_values
from pydantic import Field, field_validator, model_validator, field_serializer, Extra
from pydantic_settings import BaseSettings, SettingsConfigDict
from enum import Enum
from typing import Optional, ClassVar

from lunarbase.components.errors import ConfigFileIsMissing

DEFAULT_PROFILE = "default"
COMPONENT_EXAMPLE_WORKFLOW_NAME = "example.json"

ENVIRONMENT_PREFIX = "$LUNARENV::"
OPTIONAL_ENVIRONMENT_PREFIX = "$LUNARENV?::"


class Storage(Enum):
    # S3 = "S3" # S3 Disabled for now
    LOCAL = "LOCAL"
    # AZURE = "AZURE" # Work in progress


class LunarConfig(BaseSettings):
    DEFAULT_ENV: ClassVar[str] = str(
        Path(Path(__file__).parent.parent.parent.parent.parent, ".env").absolute()
    )
    DOCKER_ENV: ClassVar = f"{Path(__file__).parent.parent.parent.as_posix()}/.env"

    IN_DOCKER_FLAG: ClassVar = (
        f"{Path(__file__).parent.parent.parent.as_posix()}/in_docker"
    )
    DOCKER_ENV: ClassVar = f"{Path(__file__).parent.parent.parent.as_posix()}/.env"

    IN_DOCKER_FLAG: ClassVar = (
        f"{Path(__file__).parent.parent.parent.as_posix()}/in_docker"
    )

    LUNAR_STORAGE_TYPE: str = Field(default="LOCAL")
    LUNAR_STORAGE_BASE_PATH: str = Field(default_factory=os.getcwd)
    USER_DATA_PATH: str = Field(default="users")
    SYSTEM_DATA_PATH: str = Field(default="system")
    SYSTEM_TMP_PATH: str = Field(default="tmp")

    COMPONENT_LIBRARY_PATH: str = Field(default="component_library")
    COMPONENT_EXAMPLE_WORKFLOW_NAME: str = Field(default="example.json")

    DEMO_STORAGE_PATH: str = Field(default="demos")
    BASE_VENV_PATH: str = Field(default="base_venv")
    INDEX_DIR_PATH: str = Field(default="indexes")

    WORKFLOW_INDEX_NAME: str = Field(default="workflow_index")
    COMPONENT_INDEX_NAME: str = Field(default="component_index")

    REGISTRY_FILE: str = Field(default="./components.txt")
    REGISTRY_CACHE: str = Field(default="registry.json")

    LUNAR_S3_STORAGE_KEY: Optional[str] = Field(default=None)
    LUNAR_S3_STORAGE_SECRET: Optional[str] = Field(default=None)
    LUNAR_S3_STORAGE_HOST: Optional[str] = Field(default=None)
    LUNAR_S3_STORAGE_PORT: Optional[str] = Field(default=None)

    LUNARBASE_PORT: int = Field(default="8088")
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
    USER_DATASOURCE_ROOT: str = Field(default="datasources")
    USER_LLM_ROOT: str = Field(default="llms")
    USER_FILE_ROOT: str = Field(default="files")
    USER_WORKFLOW_VENV_ROOT: str = Field(default="venv")
    USER_COMPONENT_VENV_ROOT: str = Field(default="default_component_venv")

    USER_INDEX_ROOT: str = Field(default="indexes")
    USER_SSL_CERT_ROOT: str = Field(default="ssl_certs")
    USER_CUSTOM_ROOT: str = Field(default="custom_components")

    model_config = SettingsConfigDict(extra="ignore")

    @model_validator(mode="after")
    def validate_all(self):
        base_path: str = str(
            Path(self.LUNAR_STORAGE_BASE_PATH).absolute()
        )

        self.SYSTEM_DATA_PATH = str(Path(base_path, self.SYSTEM_DATA_PATH))
        self.SYSTEM_TMP_PATH = str(Path(self.SYSTEM_DATA_PATH, self.SYSTEM_TMP_PATH))
        self.USER_DATA_PATH = str(Path(base_path, self.USER_DATA_PATH))
        self.BASE_VENV_PATH = str(Path(self.SYSTEM_DATA_PATH, self.BASE_VENV_PATH))
        self.INDEX_DIR_PATH = str(Path(self.SYSTEM_DATA_PATH, self.INDEX_DIR_PATH))
 
        self.REGISTRY_CACHE = str(Path(self.SYSTEM_DATA_PATH, self.REGISTRY_CACHE))
        self.DEMO_STORAGE_PATH = str(
            Path(self.SYSTEM_DATA_PATH, self.DEMO_STORAGE_PATH)
        )
        self.COMPONENT_LIBRARY_PATH = str(
            Path(self.SYSTEM_DATA_PATH, self.COMPONENT_LIBRARY_PATH)
        )

        return self

    @field_validator("LUNAR_STORAGE_BASE_PATH")
    @classmethod
    def validate_base_path(cls, base_path):
        base_path = Path(base_path).absolute()
        if not base_path.is_dir():
            base_path.mkdir(parents=True, exist_ok=True)

        return str(base_path)

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

        return Storage[storage_value]

    @field_serializer("LUNAR_STORAGE_TYPE", when_used="always")
    def serialize_flow_storage(value):
        if isinstance(value, Storage):
            return value.value
        return value

    def get_component_index(self):
        return str(Path(self.INDEX_DIR_PATH, self.COMPONENT_INDEX_NAME))

    def get_workflow_index(self):
        return str(Path(self.INDEX_DIR_PATH, self.WORKFLOW_INDEX_NAME))

    @staticmethod
    def get_config(
        settings_file_path: str,
        settings_encoding: str = "utf-8",
    ):
        if not Path(settings_file_path).is_file():
            raise FileNotFoundError(
                f"Configuration file {settings_file_path} not found!"
            )

        settings = dotenv_values(settings_file_path, encoding=settings_encoding)
        config_model = LunarConfig.model_validate(settings)

        return config_model


GLOBAL_CONFIG = None

if pathlib.Path(LunarConfig.DEFAULT_ENV).is_file():
    GLOBAL_CONFIG = LunarConfig.get_config(settings_file_path=LunarConfig.DEFAULT_ENV)

if pathlib.Path("app", "in_docker") and pathlib.Path(LunarConfig.DOCKER_ENV).is_file():
    GLOBAL_CONFIG = LunarConfig.get_config(settings_file_path=LunarConfig.DOCKER_ENV)

if GLOBAL_CONFIG is None:
    raise ConfigFileIsMissing(LunarConfig.DEFAULT_ENV)
