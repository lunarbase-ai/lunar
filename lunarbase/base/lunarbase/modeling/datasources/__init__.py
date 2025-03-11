from abc import abstractmethod
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Union
from uuid import uuid4

from pydantic import (
    BaseModel,
    Field,
    field_validator,
    field_serializer,
)
from pydantic_core.core_schema import ValidationInfo

from lunarcore.component.data_types import File
from lunarbase.modeling.datasources.attributes import (
    LocalFileConnectionAttributes,
    PostgresqlConnectionAttributes,
    SparqlConnectionAttributes,
)
from lunarbase.utils import to_camel


class DataSourceType(Enum):
    # Keep the values consistent with the DataSource class types
    LOCAL_FILE = "LocalFile"
    POSTGRESQL = "Postgresql"
    SPARQL = "Sparql"

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

    def expected_connection_attributes(self):
        if self == DataSourceType.LOCAL_FILE:
            return LocalFileConnectionAttributes, [
                field_name
                for field_name, filed_info in LocalFileConnectionAttributes.model_fields.items()
                if filed_info.is_required()
            ]
        elif self == DataSourceType.POSTGRESQL:
            return PostgresqlConnectionAttributes, [
                field_name
                for field_name, filed_info in PostgresqlConnectionAttributes.model_fields.items()
                if filed_info.is_required()
            ]
        elif self == DataSourceType.SPARQL:
            return SparqlConnectionAttributes, [
                field_name
                for field_name, filed_info in SparqlConnectionAttributes.model_fields.items()
                if filed_info.is_required()
            ]
        else:
            return None, []


class DataSource(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(default=...)
    description: str = Field(default=...)
    type: Union[DataSourceType, str] = Field(default=...)
    connection_attributes: Union[BaseModel, Dict[str, Any]] = Field(
        default_factory=dict
    )

    class Config:
        alias_generator = to_camel
        populate_by_name = True
        validate_assignment = True
        arbitrary_attributes_allowed = True
        extra = "forbid"

    @classmethod
    def polymorphic_validation(cls, obj_dict: Dict):
        try:
            base_class = obj_dict["type"]
            if isinstance(base_class, str):
                base_class = DataSourceType[base_class.upper()]
            base_class = base_class.value
        except (KeyError, AttributeError):
            raise ValueError(
                f"Invalid DataSource {obj_dict}! Expected one of {DataSourceType.list()}"
            )

        subcls = {sub.__name__: sub for sub in cls.__subclasses__()}
        if base_class not in subcls:
            raise ValueError(
                f"Invalid DataSource type {base_class}! Expected one of {DataSourceType.list()}"
            )
        for subclass_name, subcls in subcls.items():
            if subclass_name == base_class:
                return subcls.model_validate(obj_dict)

    @field_serializer("type")
    @classmethod
    def serialize_type(cls, value):
        if isinstance(value, Enum):
            return value.name
        return value

    @field_validator("type")
    @classmethod
    def validate_type(cls, value):
        if isinstance(value, str):
            try:
                value = DataSourceType[value.upper()]
            except KeyError:
                raise ValueError(
                    f"Invalid DataSource type {value}! Expected one of {DataSourceType.list()}"
                )

        subcls = {sub.__name__ for sub in cls.__subclasses__()}
        if len(subcls) == 0:
            subcls = DataSourceType.list()
        if value.value not in subcls:
            raise ValueError(
                f"Invalid DataSource type {value}! Expected one of {DataSourceType.list()}"
            )
        return value

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

        _type = info.data.get("type")
        if _type is None:
            raise ValueError(
                f"Invalid type {_type} for DataSource {info.data.get('name', '<>')}. Expected one of {DataSourceType.list()}"
            )

        expected_connection_type, _expected = _type.expected_connection_attributes()
        _name = info.data.get("name", "")
        try:
            return expected_connection_type.model_validate(value)
        except ValueError as e:
            raise ValueError(
                f"Invalid connection attributes for DataSource {_name}: {e}!"
            )


    @abstractmethod
    def to_component_input(self, **kwargs: Any):
        pass


class LocalFile(DataSource):
    name: str = Field(default="Local file datasource")
    type: Union[str, DataSourceType] = Field(
        default_factory=lambda: DataSourceType.LOCAL_FILE,
        frozen=True,
    )
    description: str = Field(
        default="Local file datasource - allows read and write operations on local files."
    )
    connection_attributes: Union[Dict, LocalFileConnectionAttributes] = Field(
        default=...
    )

    def to_component_input(self, base_path: str, missing_ok: bool = True):
        if not Path(base_path).exists():
            raise FileNotFoundError(f"Base path for file {self.name} does not exist!")
        files = []
        for file in self.connection_attributes.files:
            _path = Path(base_path, file.file_name)
            if not _path.exists() and not missing_ok:
                raise FileNotFoundError(f"File {file.file_name} does not exist on the server!")
            _size = _path.stat().st_size if _path.exists() else 0
            files.append(File(
                name=file.file_name,
                description=self.description,
                type=file.file_type,
                size=_size,
                path=str(_path),
            ))
        return files


class Postgresql(DataSource):
    name: str = Field(default="Postgresql datasource")
    type: Union[str, DataSourceType] = Field(
        default_factory=lambda: DataSourceType.POSTGRESQL,
        frozen=True,
    )
    description: str = Field(
        default="Postgresql or SQLite datasource - allows read and write operations on a Postgresql or a local SQLite database."
    )
    connection_attributes: Union[Dict, PostgresqlConnectionAttributes] = Field(
        default=...
    )

    def to_component_input(self, **kwargs: Any):
        pass


class Sparql(DataSource):
    name: str = Field(default="SPARQL datasource")
    type: Union[str, DataSourceType] = Field(
        default_factory=lambda: DataSourceType.SPARQL,
        frozen=True,
    )
    description: str = Field(
        default="SPARQL datasource - allows read and write operations on a SPARQL endpoint."
    )
    connection_attributes: Union[Dict, SparqlConnectionAttributes] = Field(default=...)

    def to_component_input(self, **kwargs: Any):
        return self.connection_attributes.dict()
