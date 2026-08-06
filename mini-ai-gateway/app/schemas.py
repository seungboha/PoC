from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    prompt: str = Field(
        min_length=1,
        max_length=4000,
        description="AI 모델에 전달할 입력",
    )


class GenerateResponse(BaseModel):
    request_id: str
    provider: str
    model: str
    output: str