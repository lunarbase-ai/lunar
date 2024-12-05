from enum import Enum
from typing import Union, Dict, ClassVar, Any
from uuid import uuid4

from pydantic import Field, BaseModel, field_validator
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
            return [
                field_name
                for field_name, filed_info in AzureChatGPTConnectionAttributes.model_fields.items()
                if filed_info.is_required()
            ]
        else:
            return []


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
            base_obj = cls.model_validate(obj_dict)
        except ValueError as e:
            raise e

        base_class = base_obj.type.value
        if base_class not in cls.__subclasses__():
            raise ValueError(
                f"Invalid LLM type {base_class}! Expected one of {LLMType.list()}"
            )
        subcls = {sub.__name for sub in cls.__subclasses__()}
        for subclass in subcls:
            if subclass == base_class:
                return subclass.model_validate(obj_dict)

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

        _expected = _type.expected_connection_attributes()
        if len(_expected) == 0:
            return value

        _name = info.data.get("name", "")
        for _exp in _expected:
            if _exp not in value:
                raise ValueError(
                    f"{_exp} not a valid connection attribute for LLM {_name}! Valid connection attributes are: {_expected}!"
                )
        return value


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
