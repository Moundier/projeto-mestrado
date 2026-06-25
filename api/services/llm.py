import os

import httpx
from fastapi.responses import JSONResponse

from api.services.rag import rag_retrieve


def get_env(key: str, default: str) -> str:
    return os.environ.get(key, default)


async def ollama_run(query: str, ctx: str) -> JSONResponse:
    context = await rag_retrieve(query)

    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    payload = {
        "model": get_env("LLM_MODEL", "gemma3:4b"),
        "messages": [
            {"role": "system", "content": f"Context: {context}"},
            {"role": "user", "content": query},
        ],
        "temperature": float(get_env("LLM_TEMPERATURE", "1.0")),
        "top_p": float(get_env("LLM_TOP_P", "0.0")),
        "stream": False,
    }

    try:
        async with httpx.AsyncClient() as client:
            url = get_env("LLM_ENDPOINT", "http://localhost:11434/api/chat")
            timeout = httpx.Timeout(120.0, read=60.0)
            response = await client.post(
                url=url,
                json=payload,
                headers=headers,
                timeout=timeout,
            )
            response.raise_for_status()
            result = response.json()
            return JSONResponse(result)

    except httpx.HTTPStatusError as e:
        return JSONResponse(
            {"detail": e.response.text}, status_code=e.response.status_code
        )
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
