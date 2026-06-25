from fastapi import APIRouter
from fastapi.responses import JSONResponse

from api.services.llm import ollama_run

router = APIRouter(prefix="/ollama", tags=["Ollama"])


@router.get("/ask")
async def query_ollama(query: str, ctx: str) -> JSONResponse:
    return await ollama_run(query=query, ctx=ctx)
