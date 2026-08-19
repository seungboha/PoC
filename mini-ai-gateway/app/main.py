from uuid import uuid4

from fastapi import FastAPI, HTTPException, status

from app.config import settings
from app.providers.errors import ProviderCreditExhaustedError
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
    try:
        output = await provider.generate(request.prompt)
    except ProviderCreditExhaustedError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "provider_credit_exhausted",
                "message": str(exc),
            },
        ) from exc

    return GenerateResponse(
        request_id=str(uuid4()),
        provider=provider.name,
        model=provider.model,
        output=output,
    )
