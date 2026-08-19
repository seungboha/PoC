from unittest.mock import AsyncMock

import httpx
import pytest
from openai import RateLimitError

from app.providers.errors import ProviderCreditExhaustedError
from app.providers.openai import OpenAIProvider


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def rate_limit_error(code: str) -> RateLimitError:
    request = httpx.Request(
        "POST",
        "https://api.openai.com/v1/responses",
    )
    response = httpx.Response(429, request=request)

    return RateLimitError(
        "OpenAI request failed.",
        response=response,
        body={
            "code": code,
            "type": "insufficient_quota",
        },
    )


@pytest.mark.anyio
async def test_generate_translates_exhausted_credit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = OpenAIProvider(
        api_key="test-key",
        model="test-model",
    )
    error = rate_limit_error("credit_balance_exhausted")
    create = AsyncMock(side_effect=error)
    monkeypatch.setattr(provider.client.responses, "create", create)

    try:
        with pytest.raises(
            ProviderCreditExhaustedError,
            match="OpenAI provider has no available credit",
        ):
            await provider.generate("hello")
    finally:
        await provider.client.close()


@pytest.mark.anyio
async def test_generate_does_not_mislabel_temporary_rate_limit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = OpenAIProvider(
        api_key="test-key",
        model="test-model",
    )
    error = rate_limit_error("rate_limit_exceeded")
    create = AsyncMock(side_effect=error)
    monkeypatch.setattr(provider.client.responses, "create", create)

    try:
        with pytest.raises(RateLimitError) as exc_info:
            await provider.generate("hello")
    finally:
        await provider.client.close()

    assert exc_info.value is error
