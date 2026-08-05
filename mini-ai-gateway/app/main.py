from uuid import uuid4

from fastapi import FastAPI

from app.providers.mock import MockProvider
from app.schemas import GenerateRequest, GenerateResponse

app = FastAPI(
    title="Mini AI Gateway",
    version="0.1.0",
)

provider = MockProvider()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy",
            "service" : "Nothing special",
            "version": app.version,}


@app.post("/v1/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest) -> GenerateResponse:
    
    print(f"Received request: {request.model_dump()}")

    output = await provider.generate(
        prompt=request.prompt,
        repeat=request.repeat,
    )


    response = GenerateResponse(
        request_id=str(uuid4()),
        provider=provider.name,
        model=provider.model,
        received_prompt=request.prompt,
        repeat=request.repeat,
        output=output,
    )
    print(f"Sending response: {response.model_dump()}")
    return response