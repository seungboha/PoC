import pytest
from httpx2 import ASGITransport, AsyncClient, Response

import app.main as main
from app.config import Settings
from app.providers.base import AIProvider
from app.providers.errors import ProviderCreditExhaustedError
from app.providers.mock import MockProvider
from app.routing import ProviderRouter

TEST_API_KEY = "test-gateway-key"
AUTH_HEADERS = {"X-API-Key": TEST_API_KEY}


class QualityProvider:
    name = "openai"
    model = "quality-model"

    async def generate(self, prompt: str) -> str:
        return f"[QUALITY] {prompt}"


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(autouse=True)
def configure_test_gateway(monkeypatch: pytest.MonkeyPatch) -> None:
    test_settings = Settings(
        _env_file=None,
        ai_provider="mock",
    )
    providers: dict[str, AIProvider] = {
        "mock": MockProvider(),
        "openai": QualityProvider(),
    }

    def provider_factory(
        settings: Settings,
        provider_name: str | None,
    ) -> AIProvider:
        selected_provider = provider_name or settings.ai_provider
        return providers[selected_provider]

    monkeypatch.setattr(
        main,
        "provider_router",
        ProviderRouter(test_settings, provider_factory),
    )
    monkeypatch.setattr(
        main.settings,
        "gateway_api_key",
        TEST_API_KEY,
    )


async def request(method: str, path: str, **kwargs: object) -> Response:
    transport = ASGITransport(app=main.app)
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        return await client.request(method, path, **kwargs)


@pytest.mark.anyio
async def test_health_is_public() -> None:
    response = await request("GET", "/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "version": "0.3.0",
        "provider": "mock",
    }


@pytest.mark.anyio
async def test_generate_requires_api_key() -> None:
    response = await request(
        "POST",
        "/v1/generate",
        json={"prompt": "hello"},
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid or missing API key."
    }


@pytest.mark.anyio
async def test_generate_rejects_invalid_api_key() -> None:
    response = await request(
        "POST",
        "/v1/generate",
        headers={"X-API-Key": "wrong-key"},
        json={"prompt": "hello"},
    )

    assert response.status_code == 401


@pytest.mark.anyio
async def test_generate_uses_configured_provider_by_default() -> None:
    response = await request(
        "POST",
        "/v1/generate",
        headers=AUTH_HEADERS,
        json={"prompt": "hello"},
    )

    assert response.status_code == 200

    body = response.json()
    assert body["provider"] == "mock"
    assert body["model"] == "mock-v1"
    assert body["output"] == "[MOCK PROVIDER] Received: HELLO"
    assert body["request_id"]


@pytest.mark.anyio
@pytest.mark.parametrize("routing_policy", ["speed", "cost"])
async def test_generate_routes_speed_and_cost_to_mock(
    routing_policy: str,
) -> None:
    response = await request(
        "POST",
        "/v1/generate",
        headers=AUTH_HEADERS,
        json={
            "prompt": "hello",
            "routing_policy": routing_policy,
        },
    )

    assert response.status_code == 200
    assert response.json()["provider"] == "mock"


@pytest.mark.anyio
async def test_generate_routes_quality_to_openai() -> None:
    response = await request(
        "POST",
        "/v1/generate",
        headers=AUTH_HEADERS,
        json={
            "prompt": "hello",
            "routing_policy": "quality",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "request_id": response.json()["request_id"],
        "provider": "openai",
        "model": "quality-model",
        "output": "[QUALITY] hello",
    }


@pytest.mark.anyio
async def test_generate_rejects_unsupported_routing_policy() -> None:
    response = await request(
        "POST",
        "/v1/generate",
        headers=AUTH_HEADERS,
        json={
            "prompt": "hello",
            "routing_policy": "unknown",
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": {
            "code": "unsupported_routing_policy",
            "message": "Unsupported routing policy: unknown",
            "supported_policies": ["speed", "quality", "cost"],
        }
    }


@pytest.mark.anyio
async def test_generate_reports_unconfigured_quality_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    test_settings = Settings(
        _env_file=None,
        ai_provider="mock",
        openai_api_key="",
        openai_model="",
    )
    monkeypatch.setattr(
        main,
        "provider_router",
        ProviderRouter(test_settings),
    )

    response = await request(
        "POST",
        "/v1/generate",
        headers=AUTH_HEADERS,
        json={
            "prompt": "hello",
            "routing_policy": "quality",
        },
    )

    assert response.status_code == 503
    assert response.json()["detail"]["code"] == (
        "provider_not_configured"
    )


@pytest.mark.anyio
async def test_generate_rejects_empty_prompt() -> None:
    response = await request(
        "POST",
        "/v1/generate",
        headers=AUTH_HEADERS,
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

    router = main.provider_router
    monkeypatch.setattr(
        router,
        "default_provider",
        CreditExhaustedProvider(),
    )

    response = await request(
        "POST",
        "/v1/generate",
        headers=AUTH_HEADERS,
        json={"prompt": "hello"},
    )

    assert response.status_code == 503
    assert response.json() == {
        "detail": {
            "code": "provider_credit_exhausted",
            "message": "OpenAI provider has no available credit.",
        }
    }


def test_openapi_documents_gateway_api_key() -> None:
    openapi_schema = main.app.openapi()
    security_scheme = openapi_schema["components"]["securitySchemes"][
        "GatewayAPIKey"
    ]

    assert security_scheme == {
        "type": "apiKey",
        "description": "API key for accessing the Mini AI Gateway",
        "in": "header",
        "name": "X-API-Key",
    }
    assert openapi_schema["paths"]["/v1/generate"]["post"][
        "security"
    ] == [{"GatewayAPIKey": []}]
