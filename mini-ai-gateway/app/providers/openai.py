from openai import AsyncOpenAI, RateLimitError

from app.providers.errors import ProviderCreditExhaustedError


class OpenAIProvider:
    name = "openai"

    def __init__(self, api_key: str, model: str) -> None:
        self.model = model
        self.client = AsyncOpenAI(api_key=api_key)

    async def generate(self, prompt: str) -> str:
        try:
            response = await self.client.responses.create(
                model=self.model,
                input=prompt,
            )
        except RateLimitError as exc:
            if exc.code == "credit_balance_exhausted":
                raise ProviderCreditExhaustedError(
                    "OpenAI provider has no available credit."
                ) from exc

            raise

        return response.output_text
