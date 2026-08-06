from app.config import Settings
from app.providers.base import AIProvider
from app.providers.mock import MockProvider
from app.providers.openai import OpenAIProvider


def create_provider(settings: Settings) -> AIProvider:
    if settings.ai_provider == "mock":
        return MockProvider()

    if settings.ai_provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")

        if not settings.openai_model:
            raise ValueError("OPENAI_MODEL이 설정되지 않았습니다.")

        return OpenAIProvider(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
        )

    raise ValueError(
        f"지원하지 않는 Provider입니다: {settings.ai_provider}"
    )