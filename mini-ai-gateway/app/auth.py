from secrets import compare_digest
from typing import Annotated

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.config import settings

gateway_api_key_header = APIKeyHeader(
    name="X-API-Key",
    scheme_name="GatewayAPIKey",
    description="API key for accessing the Mini AI Gateway",
    auto_error=False,
)


async def require_gateway_api_key(
    api_key: Annotated[
        str | None,
        Security(gateway_api_key_header),
    ],
) -> None:
    expected_api_key = settings.gateway_api_key

    if (
        not expected_api_key
        or api_key is None
        or not compare_digest(api_key, expected_api_key)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key.",
        )
