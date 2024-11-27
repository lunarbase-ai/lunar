from abc import abstractmethod
from typing import Any, Optional, Union, Dict, ClassVar

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI
from pydantic import Field, field_validator, BaseModel

from lunarbase.modeling.datasources import (
    DataSourceType,
    InheritanceTracker,
    DataSource,
)


class LLMType(DataSourceType):
    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        normal_value = value.upper()
        if normal_value not in InheritanceTracker.__inheritors__[LLM]:
            raise ValueError(
                f"{value} not a valid LLM type! Valid types are: {InheritanceTracker.__inheritors__[LLM]}!"
            )


class LLM(DataSource):
    type: LLMType = Field(default=...)

    @abstractmethod
    def __enter__(self):
        pass

    def read(self, **kwargs: Any):
        pass

    def write(self, **kwargs: Any):
        pass

    @abstractmethod
    def prompt(self, **kwargs: Any):
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class AzureChatGPTConnectionAttributes(BaseModel):
    openai_api_version: str = Field(default=...)
    deployment_name: str = Field(default=...)
    openai_api_key: str = Field(default=...)
    azure_endpoint: str = Field(default=...)
    model_name: str = Field(default=...)
    temperature: float = Field(default=0.7)
    timeout: float = Field(default=30.0)
    max_tokens: int = Field(default=1024)


class AzureChatGPTConfigurationAttributes(BaseModel):
    pass


class AzureChatGPT(LLM):
    SYSTEM_PROMPT: ClassVar[str] = (
        "You are a helpful AI assistant. Your name is Lunar AI."
    )
    name: str = Field(default="Azure OpenAI Chat GPT")
    type: LLMType = Field(
        default_factory=lambda: LLMType(
            name="AZURECHATGPT",
            expected_connection_attributes=list(
                AzureChatGPTConnectionAttributes.model_fields.keys()
            ),
            expected_configuration_attributes=[],
        )
    )
    description: str = Field(
        default="Azure Chat GPT - allows gen ai operations using Azure Chat GPT."
    )
    connection_attributes: Union[Dict, AzureChatGPTConnectionAttributes] = Field(
        default=...
    )
    configuration_attributes: Union[Dict, AzureChatGPTConfigurationAttributes] = Field(
        default_factory=dict
    )

    client: Optional[Any] = Field(default=None)

    def __enter__(self):
        self.client = AzureChatOpenAI(**self.connection_attributes)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client = None

    def prompt(self, user_prompt: str, system_prompt: str = SYSTEM_PROMPT):
        if self.client is None:
            raise ValueError("Must call __enter__ before using the LLM!")

        user_prompt_template = PromptTemplate(
            input_variables=["prompt"],
            template="{prompt}",
        )
        system_prompt_template = PromptTemplate(
            input_variables=["prompt"],
            template="{prompt}",
        )
        system_message = SystemMessage(
            content=system_prompt_template.format(prompt=system_prompt)
        )
        user_message = HumanMessage(
            content=user_prompt_template.format(prompt=user_prompt)
        )

        messages = [system_message, user_message]
        result = self.client.invoke(messages).content

        return str(result).strip("\n").strip().replace('"', "'")
