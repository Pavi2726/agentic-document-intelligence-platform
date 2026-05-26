from __future__ import annotations

import os
import shutil
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.agents.supervisor import run_supervisor
from app.core.config import settings
from app.db.neo4j_db import Neo4jClient
from app.db.postgres import create_upload_session, log_query, store_document_metadata
from app.retrievers.vector_rag import vector_rag
from app.tools.file_processor import FileProcessor

router = APIRouter()
file_processor = FileProcessor()


class QueryRequest(BaseModel):
    query: str


def extract_graph_entities(chunks: list[dict], filename: str) -> None:
    """Background task: extract entities from chunks and store in Neo4j."""
    try:
        client = Neo4jClient()
        if client.health_check():
            count = client.extract_and_store_from_chunks(chunks, filename)
            print(f"[Graph] Stored {count} relationships for '{filename}'")
        client.close()
    except Exception as e:
        print(f"[Graph] Entity extraction failed: {e}")


@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "database_checks": {
            "postgres_configured": bool(settings.POSTGRES_URL),
            "neo4j_configured": bool(settings.NEO4J_URI),
            "groq_configured": bool(settings.GROQ_API_KEY),
        },
        "vector_store_ready": vector_rag.has_documents() or os.path.exists(settings.VECTOR_STORE_DIR),
    }


@router.post("/upload")
async def upload_file(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    filename = file.filename or ""
    ext = os.path.splitext(filename)[1].lower()

    if ext not in [".pdf", ".docx", ".txt"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Only .pdf, .docx, and .txt files are supported.",
        )

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        chunks = file_processor.process_file(file_path)
        indexed_count = vector_rag.index_chunks(chunks)
        vector_rag.set_active_document(filename)

        session_id = uuid4().hex
        create_upload_session(session_id=session_id, filename=filename)
        store_document_metadata(filename=filename, file_path=file_path, chunk_count=len(chunks))

        # Extract entities to Neo4j in background (non-blocking)
        if background_tasks:
            background_tasks.add_task(extract_graph_entities, chunks, filename)
        else:
            extract_graph_entities(chunks, filename)

        return {
            "message": "File uploaded and indexed successfully.",
            "filename": filename,
            "file_path": file_path,
            "session_id": session_id,
            "total_chunks": len(chunks),
            "indexed_chunks": indexed_count,
            "chunks_preview": [
                {
                    "chunk_index": chunk["chunk_index"],
                    "text_preview": chunk["text"][:100] + "..." if len(chunk["text"]) > 100 else chunk["text"],
                }
                for chunk in chunks[:3]
            ],
        }
    except Exception as exc:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error processing file: {exc}") from exc


@router.post("/query")
async def query_documents(payload: QueryRequest):
    query = payload.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    try:
        supervisor_result = run_supervisor(query)
        result = supervisor_result.get("result", {})
        agent = result.get("agent", supervisor_result.get("category", "unknown"))
        log_query(
            query=query,
            agent=agent,
            response_preview=str(result)[:400],
        )
        return supervisor_result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Query processing failed: {exc}") from exc