from fastapi import APIRouter, UploadFile
from langchain_core.documents import Document

from api.services.rag import add_to_vectorstore

router = APIRouter(prefix="/rag", tags=["RAG"])


@router.post("/ingest/upload_file/")
async def upload_file(file: UploadFile):
    content = await file.read()
    docs = [Document(page_content=content.decode(), metadata={"source": file.filename})]
    count = await add_to_vectorstore(docs)
    return {"message": f"Added {count} chunks from {file.filename}"}
