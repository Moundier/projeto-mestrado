#!/usr/bin/env python3
import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from api.routes.ollama import router as router_ollama
from api.routes.rag import router as router_rag
from api.routes.cbr import router as router_cbr

api = FastAPI(title="CAOL Intelligence Agent")
api.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8001",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api.include_router(router_ollama)
api.include_router(router_rag)
api.include_router(router_cbr)


@api.get("/")
async def root():
    return {"message": "CAOL Intelligence Agent API is running"}


def run_api():
    import uvicorn
    host = os.environ.get("API_HOST", "0.0.0.0")
    port = int(os.environ.get("API_PORT", "8001"))
    uvicorn.run("app:api", host=host, port=port, reload=True)


def run_mcp():
    from mcp_server import run_server
    host = os.environ.get("MCP_HOST", "0.0.0.0")
    port = int(os.environ.get("MCP_PORT", "8002"))
    run_server(host=host, port=port)


def load_cases():
    from api.services.repository import load_all_cases
    cases = load_all_cases()
    print(f"Loaded {len(cases)} historical CAOL cases.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CAOL Intelligence Agent")
    parser.add_argument(
        "mode",
        nargs="?",
        default="api",
        choices=["api", "mcp", "both", "load"],
        help="Run mode: api (default), mcp, both, or load",
    )
    args = parser.parse_args()

    if args.mode == "api":
        run_api()
    elif args.mode == "mcp":
        run_mcp()
    elif args.mode == "both":
        import threading
        t = threading.Thread(target=run_mcp, daemon=True)
        t.start()
        run_api()
    elif args.mode == "load":
        load_cases()
