from pydantic import BaseModel, Field


class AzureChatGPTConnectionAttributes(BaseModel):
    openai_api_version: str = Field(default=...)
    deployment_name: str = Field(default=...)
    openai_api_key: str = Field(default=...)
    azure_endpoint: str = Field(default=...)
    model_name: str = Field(default=...)
    temperature: float = Field(default=0.7)
    timeout: float = Field(default=30.0)
    max_tokens: int = Field(default=1024)

    class Config:
        protected_namespaces = ()


class AzureChatGPTConfigurationAttributes(BaseModel):
    pass