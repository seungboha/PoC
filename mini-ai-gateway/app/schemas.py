from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    prompt: str = Field(
        min_length=1,
        max_length=4000,
        description="prompt to generate a response from AI model",
    )


class GenerateResponse(BaseModel):
    request_id: str
    provider: str
    model: str
    output: str