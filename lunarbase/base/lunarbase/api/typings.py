from pydantic import BaseModel


class CodeCompletionRequestBody(BaseModel):
    code: str
