from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_generate() -> None:
    response = client.post(
        "/v1/generate",
        json={"prompt": "hello"},
    )

    assert response.status_code == 200

    body = response.json()
    assert body["provider"] == "mock"
    assert body["model"] == "mock-v1"
    assert body["output"] == "[MOCK] hello"
    assert body["request_id"]