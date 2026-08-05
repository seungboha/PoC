from uuid import uuid4

from fastapi import FastAPI

from app.providers.mock import MockProvider
from app.schemas import GenerateRequest, GenerateResponse

app = FastAPI(
    title="Mini AI Gateway",
    version="0.1.0",
)

provider = MockProvider()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.post("/v1/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest) -> GenerateResponse:
    output = await provider.generate(request.prompt)

    return GenerateResponse(
        request_id=str(uuid4()),
        provider=provider.name,
        model=provider.model,
        output=output,
    )