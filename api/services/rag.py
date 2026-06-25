import os
import sys
from typing import Iterable

from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings as connect_ollama_embeddings
from langchain_postgres.vectorstores import PGVector
from langchain_text_splitters import CharacterTextSplitter


def get_env(key: str, default: str) -> str:
    return os.environ.get(key, default)


def get_connection_ollama_embeddings():
    return connect_ollama_embeddings(
        base_url=get_env("EMBEDDING_ENDPOINT", "http://localhost:11434"),
        model=get_env("EMBEDDING_MODEL", "nomic-embed-text"),
    )


def get_vector_store():
    try:
        collection = get_env("DB_COLLECTION", "vector_db")
        connection = get_env(
            "DB_CONNECTION",
            "postgresql+psycopg://postgres:postgres@localhost:5432/vector_db",
        )

        embedding_model = get_connection_ollama_embeddings()

        vector_store = PGVector(
            embeddings=embedding_model,
            connection=connection,
            collection_name=collection,
            use_jsonb=True,
        )

        return vector_store

    except Exception as e:
        print(str(e), file=sys.stderr)
        raise RuntimeError(f"Could not create vector store: {e}") from e


async def rag_retrieve(query: str) -> str:
    vector_store = get_vector_store()
    top_k = int(get_env("RAG_TOP_K", "3"))
    results = vector_store.similarity_search(query=query, k=top_k)
    context = "\n\n".join([doc.page_content for doc in results])
    return context


async def add_to_vectorstore(docs: Iterable[Document]):
    chunk_size = int(get_env("RAG_CHUNK_SIZE", "1000"))
    chunk_overlap = int(get_env("RAG_CHUNK_OVERLAP", "200"))
    splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.split_documents(docs)
    vector_store = get_vector_store()
    await vector_store.aadd_documents(chunks)
    return len(chunks)
