import asyncio


class MockProvider:
    name = "mock"
    model = "mock-v1"

    async def generate(
        self,
        prompt: str,
        repeat: int = 1,
    ) -> str:
        await asyncio.sleep(0.5)

        result = f"[MOCK] {prompt}"
        return " | ".join([result] * repeat)