from uuid import uuid4

from fastapi import FastAPI, HTTPException, Security, status

from app.auth import require_gateway_api_key
from app.config import settings
from app.providers.errors import (
    ProviderConfigurationError,
    ProviderCreditExhaustedError,
)
from app.routing import (
    SUPPORTED_ROUTING_POLICIES,
    ProviderRouter,
    UnsupportedRoutingPolicyError,
)
from app.schemas import GenerateRequest, GenerateResponse

app = FastAPI(
    title="Mini AI Gateway",
    version="0.3.0",
)

provider_router = ProviderRouter(settings)


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": app.version,
        "provider": provider_router.default_provider.name,
    }


@app.post(
    "/v1/generate",
    response_model=GenerateResponse,
    dependencies=[Security(require_gateway_api_key)],
)
async def generate(
    request: GenerateRequest,
) -> GenerateResponse:
    try:
        active_provider = provider_router.resolve(request.routing_policy)
    except UnsupportedRoutingPolicyError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "unsupported_routing_policy",
                "message": str(exc),
                "supported_policies": SUPPORTED_ROUTING_POLICIES,
            },
        ) from exc
    except ProviderConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "provider_not_configured",
                "message": str(exc),
            },
        ) from exc

    try:
        output = await active_provider.generate(request.prompt)
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
        provider=active_provider.name,
        model=active_provider.model,
        output=output,
    )
