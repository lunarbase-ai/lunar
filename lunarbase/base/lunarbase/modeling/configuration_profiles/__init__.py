from enum import Enum
from typing import Any, Dict, Union
from uuid import uuid4

from lunarbase.modeling.configuration_profiles.typings import ConfigurationProfileType
from pydantic import (
    BaseModel,
    Field,
    field_validator,
    field_serializer,
)
from lunarbase.utils import to_camel


class ConfigurationProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(default=...)
    description: str = Field(default=...)
    type: Union[ConfigurationProfileType, str] = Field(default=...)
    fields: Union[Dict[str, Any]] = Field(default_factory=dict)

    class Config:
        alias_generator = to_camel
        populate_by_name = True
        validate_assignment = True
        arbitrary_attributes_allowed = True
        extra = "forbid"

    @field_serializer("type", when_used="always")
    @classmethod
    def serialize_type(cls, value):
        if isinstance(value, Enum):
            return value.value
        return value

    @field_validator("type")
    @classmethod
    def validate_type(cls, value):
        if isinstance(value, str):
            try:
                value = ConfigurationProfileType[value.upper()]
            except KeyError:
                value = ConfigurationProfileType(value)
        return value
