from abc import abstractmethod
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Union
from uuid import uuid4

from pydantic import (
    BaseModel,
    Field,
    field_validator,
)
from pydantic_core.core_schema import ValidationInfo

from lunarcore.component.data_types import File
from lunarbase.modeling.datasources.attributes import (
    LocalFileConnectionAttributes,
    PostgresqlConnectionAttributes,
)
from lunarbase.utils import to_camel


class DataSourceType(Enum):
    # Keep the values consistent with the DataSource class types
    LOCAL_FILE = "LocalFile"
    POSTGRESQL = "Postgresql"

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

    def expected_connection_attributes(self):
        if self == DataSourceType.LOCAL_FILE:
            return list(LocalFileConnectionAttributes.model_fields.keys())
        elif self == DataSourceType.POSTGRESQL:
            return list(PostgresqlConnectionAttributes.model_fields.keys())
        else:
            return []


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
            base_obj = cls.model_validate(obj_dict)
        except ValueError as e:
            raise e

        base_class = base_obj.type.value
        subcls = {sub.__name__ for sub in cls.__subclasses__()}
        if base_class not in subcls:
            raise ValueError(
                f"Invalid DataSource type {base_class}! Expected one of {DataSourceType.list()}"
            )
        for subclass in subcls:
            if subclass == base_class:
                return subclass.model_validate(obj_dict)

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

        _expected = _type.expected_connection_attributes()
        if len(_expected) == 0:
            return value

        _name = info.data.get("name", "")
        for _exp in _expected:
            if _exp not in value:
                raise ValueError(
                    f"{_exp} not a valid connection attribute for DataSource {_name}! Valid connection attributes are: {_expected}!"
                )
        return value

    @abstractmethod
    def to_component_input(self, **kwargs: Any):
        pass


class LocalFile(DataSource):
    name: str = Field(default="Local file datasource")
    type: DataSourceType = Field(
        default_factory=lambda: DataSourceType.LOCAL_FILE,
        frozen=True,
    )
    description: str = Field(
        default="Local file datasource - allows read and write operations on local files."
    )
    connection_attributes: Union[Dict, LocalFileConnectionAttributes] = Field(
        default=...
    )

    def to_component_input(self, base_path: str):
        if not Path(base_path).exists():
            raise FileNotFoundError(f"Base path for file {self.name} does not exist!")

        _path = Path(base_path, self.connection_attributes["file_name"])
        if not _path.exists():
            raise FileNotFoundError(f"File {self.name} does not exist on the server!")

        _size = Path(_path).stat().st_size
        return File(
            name=self.configuration_attributes["file_name"],
            description=self.description,
            type=self.configuration_attributes["file_type"],
            size=_size,
            path=_path,
        )


class Postgresql(DataSource):
    name: str = Field(default="Postgresql datasource")
    type: DataSourceType = Field(
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
