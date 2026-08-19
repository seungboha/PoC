import asyncio


class MockProvider:
    name = "mock"
    model = "mock-v1"

    async def generate(self, prompt: str) -> str:
        await asyncio.sleep(0.5)
        return f"[MOCK PROVIDER] Received: {prompt.upper()}"