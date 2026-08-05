from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    prompt: str = Field(
        min_length=1,
        max_length=4000,
        description="prompt to generate a response from AI model",
    )

    repeat: int = Field(
        default=1,
        ge=1,
        le=3,
        description="Mock provider will repeat the prompt this many times in the output",
    )


class GenerateResponse(BaseModel):
    request_id: str
    provider: str
    model: str
    received_prompt: str
    repeat: int
    output: str