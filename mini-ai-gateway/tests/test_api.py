import pytest
from httpx2 import ASGITransport, AsyncClient, Response

import app.main as main
from app.providers.errors import ProviderCreditExhaustedError
from app.providers.mock import MockProvider


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(autouse=True)
def use_mock_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(main, "provider", MockProvider())


async def request(method: str, path: str, **kwargs: object) -> Response:
    transport = ASGITransport(app=main.app)
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        return await client.request(method, path, **kwargs)


@pytest.mark.anyio
async def test_health() -> None:
    response = await request("GET", "/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "version": "0.2.0",
        "provider": "mock",
    }


@pytest.mark.anyio
async def test_generate() -> None:
    response = await request(
        "POST",
        "/v1/generate",
        json={"prompt": "hello"},
    )

    assert response.status_code == 200

    body = response.json()
    assert body["provider"] == "mock"
    assert body["model"] == "mock-v1"
    assert body["output"] == "[MOCK PROVIDER] Received: HELLO"
    assert body["request_id"]


@pytest.mark.anyio
async def test_generate_rejects_empty_prompt() -> None:
    response = await request(
        "POST",
        "/v1/generate",
        json={"prompt": ""},
    )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_generate_reports_exhausted_provider_credit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class CreditExhaustedProvider:
        name = "openai"
        model = "test-model"

        async def generate(self, prompt: str) -> str:
            raise ProviderCreditExhaustedError(
                "OpenAI provider has no available credit."
            )

    monkeypatch.setattr(main, "provider", CreditExhaustedProvider())

    response = await request(
        "POST",
        "/v1/generate",
        json={"prompt": "hello"},
    )

    assert response.status_code == 503
    assert response.json() == {
        "detail": {
            "code": "provider_credit_exhausted",
            "message": "OpenAI provider has no available credit.",
        }
    }
