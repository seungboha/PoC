class MockProvider:
    name = "mock"
    model = "mock-v1"

    async def generate(self, prompt: str) -> str:
        return f"[MOCK] {prompt}"