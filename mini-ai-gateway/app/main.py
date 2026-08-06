from uuid import uuid4

from fastapi import FastAPI

from app.config import settings
from app.providers.factory import create_provider
from app.schemas import GenerateRequest, GenerateResponse

app = FastAPI(
    title="Mini AI Gateway",
    version="0.2.0",
)

provider = create_provider(settings)


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": app.version,
        "provider": provider.name,
    }


@app.post(
    "/v1/generate",
    response_model=GenerateResponse,
)
async def generate(
    request: GenerateRequest,
) -> GenerateResponse:
    output = await provider.generate(request.prompt)

    return GenerateResponse(
        request_id=str(uuid4()),
        provider=provider.name,
        model=provider.model,
        output=output,
    )