from enum import Enum
from typing import Union, Dict, ClassVar, Any
from uuid import uuid4

from pydantic import Field, BaseModel, field_validator, field_serializer
from pydantic_core.core_schema import ValidationInfo

from lunarbase.modeling.llms.attributes import (
    AzureChatGPTConnectionAttributes,
    AzureChatGPTConfigurationAttributes,
)
from lunarbase.utils import to_camel


class LLMType(Enum):
    # Keep the values consistent with the LLM class types
    AZURE_CHAT_GPT = "AzureChatGPT"

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

    def expected_connection_attributes(self):
        if self == LLMType.AZURE_CHAT_GPT:
            return AzureChatGPTConnectionAttributes, [
                field_name
                for field_name, filed_info in AzureChatGPTConnectionAttributes.model_fields.items()
                if filed_info.is_required()
            ]
        else:
            return None, []


class LLM(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(default=...)
    description: str = Field(default=...)
    type: Union[LLMType, str] = Field(default=...)
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
                base_class = LLMType[base_class.upper()]
            base_class = base_class.value
        except (KeyError, AttributeError):
            raise ValueError(
                f"Invalid LLM {obj_dict}! Expected one of {LLMType.list()}"
            )

        subcls = {sub.__name__: sub for sub in cls.__subclasses__()}
        if base_class not in subcls:
            raise ValueError(
                f"Invalid LLM type {base_class}! Expected one of {LLMType.list()}"
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
                value = LLMType[value.upper()]
            except KeyError:
                raise ValueError(
                    f"Invalid LLM type {value}! Expected one of {LLMType.list()}"
                )

        subcls = {sub.__name for sub in cls.__subclasses__()}
        if len(subcls) == 0:
            subcls = LLMType.list()
        if value.value not in subcls:
            raise ValueError(f"Invalid LLM type {value}! Expected one of {subcls}")
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
                f"Invalid type {_type} for LLM {info.data.get('name', '<>')}. Expected one of {LLMType.list()}"
            )

        expected_connection_type, _expected = _type.expected_connection_attributes()
        _name = info.data.get("name", "")
        try:
            return expected_connection_type.model_validate(value)
        except ValueError as e:
            raise ValueError(
                f"Invalid connection attributes for LLM {_name}: {e}!"
            )


class AzureChatGPT(LLM):
    SYSTEM_PROMPT: ClassVar[str] = (
        "You are a helpful AI assistant. Your name is Lunar AI."
    )
    name: str = Field(default="Azure OpenAI Chat GPT")
    type: LLMType = Field(default_factory=lambda: LLMType.AZURE_CHAT_GPT, frozen=True)
    description: str = Field(
        default="Azure Chat GPT - allows gen ai operations using Azure Chat GPT."
    )
    connection_attributes: Union[Dict, AzureChatGPTConnectionAttributes] = Field(
        default=...
    )
