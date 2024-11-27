from abc import abstractmethod
from collections import defaultdict
from pathlib import Path
from typing import Optional, Any, Dict, Type, List, Union
from urllib.parse import urlparse, quote
from uuid import uuid4

from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
)
from pydantic_core.core_schema import ValidationInfo
from sqlalchemy import URL, create_engine, Engine, text

from lunarbase.utils import to_camel

import mimetypes


class InheritanceTracker(object):
    class __metaclass__(type):
        __inheritors__ = defaultdict(list)

        def __new__(meta, name, bases, dct):
            klass = type.__new__(meta, name, bases, dct)
            for base in klass.mro()[1:-1]:
                meta.__inheritors__[base].append(klass.__name__.upper())
            return klass


class DataSourceType(BaseModel):
    name: str = Field(default=...)
    expected_connection_attributes: List[str] = Field(default_factory=list)
    expected_configuration_attributes: List[str] = Field(default_factory=list)

    class Config:
        alias_generator = to_camel
        populate_by_name = True
        validate_assignment = True

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        normal_value = value.upper()
        if normal_value not in InheritanceTracker.__inheritors__[DataSource]:
            raise ValueError(
                f"{value} not a valid datasource type! Valid types are: {InheritanceTracker.__inheritors__[DataSource]}!"
            )


class DataSource(BaseModel, metaclass=InheritanceTracker):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(default=...)
    description: str = Field(default=...)
    type: DataSourceType = Field(default=...)
    connection_attributes: Union[BaseModel, Dict[str, Any]] = Field(
        default_factory=dict
    )
    configuration_attributes: Union[BaseModel, Dict[str, Any]] = Field(
        default_factory=dict
    )

    class Config:
        alias_generator = to_camel
        populate_by_name = True
        validate_assignment = True
        arbitrary_attributes_allowed = True

    @field_validator("connection_attributes")
    @classmethod
    def validate_connection_attributes(cls, value, info: ValidationInfo):
        if not isinstance(value, dict):
            try:
                value = value.model_dump()
            except AttributeError:
                raise ValueError(
                    f"Connection_attributes must be a dictionary! Got {type(value)} instead!"
                )

        _expected = info.data.get("expected_connection_attributes", [])
        if len(_expected) == 0:
            return value

        _name = info.data.get("name", "")
        _expected = set(_expected)
        for attr_key, _ in value.items():
            if attr_key not in _expected:
                raise ValueError(
                    f"{attr_key} not a valid connection attribute for {_name}! Valid connection attributes are: {_expected}!"
                )
        return value

    @field_validator("configuration_attributes")
    @classmethod
    def validate_configuration_attributes(cls, value, info: ValidationInfo):
        if not isinstance(value, dict):
            try:
                value = value.model_dump()
            except AttributeError:
                raise ValueError(
                    f"Configuration_attributes must be a dictionary! Got {type(value)} instead!"
                )

        _expected = info.data.get("expected_configuration_attributes", [])
        if len(_expected) == 0:
            return value

        _name = info.data.get("name", "")
        _expected = set(_expected)
        for attr_key, _ in value.items():
            if attr_key not in _expected:
                raise ValueError(
                    f"{attr_key} not a valid configuration attribute for {_name}! Valid connection attributes are: {_expected}!"
                )
        return value

    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def read(self, **kwargs: Any):
        pass

    @abstractmethod
    def write(self, **kwargs: Any):
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class LocalFileConnectionAttributes(BaseModel):
    path: str = Field(default=...)
    file_type: Optional[str] = Field(default=None)

    @model_validator(mode="after")
    def validate_local_file(self):
        if self.file_type is None:
            self.file_type, _ = mimetypes.guess_type(self.path)
            if self.file_type is None:
                raise ValueError(
                    f"Could not determine file type for {self.path}! Please specify file_type!"
                    f"Accepted values are {mimetypes.types_map.values()}"
                )
        return self


class LocalFileConfigurationAttributes(BaseModel):
    pass


class LocalFile(DataSource):
    name: str = Field(default="Local file datasource")
    type: DataSourceType = Field(
        default_factory=lambda: DataSourceType(
            name="LOCALFILE",
            expected_connection_attributes=list(
                LocalFileConnectionAttributes.model_fields.keys()
            ),
            expected_configuration_attributes=[],
        )
    )
    description: str = Field(
        default="Local file datasource - allows read and write operations on local files."
    )
    connection_attributes: Union[Dict, LocalFileConnectionAttributes] = Field(default=...)
    configuration_attributes: Union[Dict, LocalFileConfigurationAttributes] = Field(
        default_factory=dict
    )

    def __enter__(self):
        """
        Must be called before use
        """
        _path = Path(self.connection_attributes.path)
        if not _path.exists():
            _path.touch(exist_ok=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def read(self, chunk_size: int = -1):
        _path = Path(self.connection_attributes.path)
        filename = _path.name

        if not _path.exists():
            raise FileNotFoundError(f"File '{filename}' not found.")

        try:
            with open(str(_path), "r") as file:
                while True:
                    data = file.read(chunk_size)
                    if not data:
                        break
                    yield data
        except Exception as e:
            raise e

    def write(self, data: bytes, mode: str = "wb"):
        if mode not in {"w", "wb", "a", "ab"}:
            raise ValueError(
                f"Invalid mode {mode}! Accepted values are 'w', 'wb', 'a', 'ab'"
            )

        _path = Path(self.connection_attributes.path)
        filename = _path.name

        if not _path.exists():
            raise FileNotFoundError(f"File '{filename}' not found.")

        try:
            with open(str(_path), mode) as file:
                file.write(data)
        except Exception as e:
            raise e


class PostgresqlConnectionAttributes(BaseModel):
    url: Optional[str] = Field(default=None)
    driver_name: Optional[str] = Field(default=None)
    username: Optional[str] = Field(default=None)
    password: Optional[str] = Field(default=None)
    host: Optional[str] = Field(default=None)
    port: Optional[str] = Field(default=None)
    database: Optional[str] = Field(default=None)
    additional_connection_kwargs: Optional[Dict] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_connection_attributes(self):
        if self.url is not None:
            _url = urlparse(self.url)
            if _url.scheme != "sqlite":
                left_url, _, right_url = self.url.rpartition("@")
                self.driver_name, credentials = left_url.split("://", 1)
                self.username, self.password = credentials.split(":", 1)
                host, self.database = right_url.split("/", 1)
                self.host, _, self.port = host.rpartition(":")
            else:
                self.driver_name = _url.scheme
                self.database = _url.path

        self.url = str(
            URL.create(
                self.driver_name,
                username=self.username,
                password=quote(self.password) if self.password else None,
                host=self.host,
                port=self.port,
                database=self.database,
            )
        )

class PostgresqlConfigurationAttributes:
    pass

class Postgresql(DataSource):
    name = str = Field(default="Postgresql datasource")
    type: DataSourceType = Field(
        default_factory=lambda: DataSourceType(
            name="POSTGRESQL",
            expected_connection_attributes=list(
                PostgresqlConnectionAttributes.model_fields.keys()
            ),
            expected_configuration_attributes=[],
        )
    )
    description: str = Field(
        default="Postgresql or SQLite datasource - allows read and write operations on a Postgresql or a local SQLite database."
    )
    connection_attributes: Union[Dict, PostgresqlConnectionAttributes] = Field(default=...)
    configuration_attributes: Union[Dict, PostgresqlConfigurationAttributes] = Field(
        default_factory=dict
    )

    engine: Optional[Engine] = Field(default=None)

    def __enter__(self):
        self.engine = create_engine(
            self.connection_attributes.url,
            **self.connection_attributes.additional_connection_kwargs,
        )
        return self

    def read(self, query_string: str, chunk_size: int = 1000):
        if self.engine is None:
            raise ValueError("Must call __enter__ before using the datasource!")

        with self.engine.connect() as connection:
            proxy = connection.execution_options(stream_results=True).execute(
                text(query_string)
            )
            while "batch not empty":
                batch = proxy.fetchmany(chunk_size)
                if not batch:
                    break

                data = [r._asdict() for r in batch]
                yield data

    def write(self, query_string: str):
        return NotImplemented

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.engine.dispose(close=True)
        self.engine = None
