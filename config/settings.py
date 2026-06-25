import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def env(key: str, default: str) -> str:
    return os.environ.get(key, default)


# Paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
CASES_DIR = DATA_DIR / "cases"
ASSETS_DIR = PROJECT_ROOT / "assets"

# LLM
LLM_MODEL = env("LLM_MODEL", "gemma3:4b")
LLM_ENDPOINT = env("LLM_ENDPOINT", "http://localhost:11434/api/chat")
LLM_TEMPERATURE = float(env("LLM_TEMPERATURE", "1.0"))
LLM_TOP_P = float(env("LLM_TOP_P", "0.0"))

# Embedding
EMBEDDING_MODEL = env("EMBEDDING_MODEL", "nomic-embed-text")
EMBEDDING_ENDPOINT = env("EMBEDDING_ENDPOINT", "http://localhost:11434")

# RAG
RAG_TOP_K = int(env("RAG_TOP_K", "3"))
RAG_CHUNK_SIZE = int(env("RAG_CHUNK_SIZE", "1000"))
RAG_CHUNK_OVERLAP = int(env("RAG_CHUNK_OVERLAP", "200"))

# CBR
CBR_WEIGHT_PRODUCT_TYPE = float(env("CBR_WEIGHT_PRODUCT_TYPE", "0.25"))
CBR_WEIGHT_DESTINATION_COUNTRY = float(env("CBR_WEIGHT_DESTINATION_COUNTRY", "0.15"))
CBR_WEIGHT_SPECIES = float(env("CBR_WEIGHT_SPECIES", "0.20"))
CBR_WEIGHT_EXPORT_QUANTITY = float(env("CBR_WEIGHT_EXPORT_QUANTITY", "0.15"))
CBR_WEIGHT_RAW_MATERIAL = float(env("CBR_WEIGHT_RAW_MATERIAL", "0.10"))
CBR_WEIGHT_SUPPLIERS = float(env("CBR_WEIGHT_SUPPLIERS", "0.10"))
CBR_WEIGHT_INVOICE_COUNT = float(env("CBR_WEIGHT_INVOICE_COUNT", "0.05"))

# Database
DB_CONNECTION = env("DB_CONNECTION", "postgresql+psycopg://postgres:postgres@localhost:5432/vector_db")
DB_COLLECTION = env("DB_COLLECTION", "vector_db")

# API
API_HOST = env("API_HOST", "0.0.0.0")
API_PORT = int(env("API_PORT", "8001"))

# MCP
MCP_HOST = env("MCP_HOST", "0.0.0.0")
MCP_PORT = int(env("MCP_PORT", "8002"))
