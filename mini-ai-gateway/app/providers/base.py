from typing import Protocol


class AIProvider(Protocol):
    name: str
    model: str

    async def generate(self, prompt: str) -> str:
        ...