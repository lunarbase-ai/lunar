from pydantic import BaseModel


class CodeCompletionRequestBody(BaseModel):
    code: str


class ComponentPublishingRequestBody(BaseModel):
    author: str
    author_email: str
    component_name: str
    component_description: str
    component_class: str
    component_documentation: str
    version: str
    access_token: str
    user_id: str
