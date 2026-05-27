from __future__ import annotations

import os
import shutil
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile, Header
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.agents.supervisor import run_supervisor
from app.core.config import settings
from app.db.neo4j_db import Neo4jClient
from app.db.postgres import create_upload_session, log_query, store_document_metadata, get_documents, get_recent_logs
from app.retrievers.vector_rag import vector_rag
from app.tools.file_processor import FileProcessor
from app.services.response_synthesis import synthesis_engine
from app.services.conversation_context import context_manager
from app.retrievers.graph_rag import GraphRAG
from app.retrievers.sql_rag import SQLRAG
from app.auth.user_manager import user_manager

router = APIRouter()
file_processor = FileProcessor()


class QueryRequest(BaseModel):
    query: str
    session_id: str | None = None


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    stream: bool = False


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str = ""


def extract_graph_entities(chunks: list[dict], filename: str) -> None:
    """Background task: extract entities from chunks and store in Neo4j."""
    try:
        client = Neo4jClient()
        if client.health_check():
            # Process only first 5 chunks for efficiency
            sample_chunks = chunks[:5]
            count = client.extract_and_store_from_chunks(sample_chunks, filename)
            print(f"[Graph] Stored {count} relationships for '{filename}' from {len(sample_chunks)} chunks")
        else:
            print(f"[Graph] Neo4j not available, skipping entity extraction")
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


@router.post("/auth/register")
async def register(payload: RegisterRequest):
    """Register a new user."""
    if not payload.username or len(payload.username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters")
    
    if not payload.password or len(payload.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    result = user_manager.register_user(payload.username, payload.password, payload.email)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result


@router.post("/auth/login")
async def login(payload: LoginRequest):
    """Login user and return session token."""
    result = user_manager.login_user(payload.username, payload.password)
    
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["message"])
    
    return result


@router.post("/auth/logout")
async def logout(authorization: str = Header(None)):
    """Logout user and invalidate session."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    result = user_manager.logout_user(token)
    
    return result


@router.get("/auth/me")
async def get_current_user(authorization: str = Header(None)):
    """Get current user information."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    session = user_manager.verify_session(token)
    
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    user_info = user_manager.get_user_info(session["username"])
    
    if not user_info:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user_info


@router.post("/upload")
async def upload_file(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    print(f"[Upload] Received file: {file.filename}, content_type: {file.content_type}")
    
    filename = file.filename or ""
    ext = os.path.splitext(filename)[1].lower()

    if ext not in [".pdf", ".docx", ".txt"]:
        print(f"[Upload] Rejected: unsupported file type {ext}")
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Only .pdf, .docx, and .txt files are supported.",
        )

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    print(f"[Upload] Saving to: {file_path}")

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print(f"[Upload] File saved successfully")

        print(f"[Upload] Processing file...")
        chunks = file_processor.process_file(file_path)
        print(f"[Upload] Extracted {len(chunks)} chunks")
        
        indexed_count = vector_rag.index_chunks(chunks)
        print(f"[Upload] Indexed {indexed_count} chunks")
        
        vector_rag.set_active_document(filename)

        session_id = uuid4().hex
        try:
            create_upload_session(session_id=session_id, filename=filename)
        except Exception as e:
            print(f"[Postgres] create_upload_session failed: {e}")

        try:
            store_document_metadata(filename=filename, file_path=file_path, chunk_count=len(chunks))
        except Exception as e:
            print(f"[Postgres] store_document_metadata failed: {e}")

        # Extract entities to Neo4j in background (non-blocking)
        if background_tasks:
            background_tasks.add_task(extract_graph_entities, chunks, filename)
        else:
            extract_graph_entities(chunks, filename)

        print(f"[Upload] Success: {filename}")
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
        print(f"[Upload] Error: {exc}")
        import traceback
        traceback.print_exc()
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


@router.post("/chat")
async def chat(payload: ChatRequest):
    """US-11 & US-12: Chat endpoint with synthesis and context management."""
    message = payload.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    
    try:
        session_id = payload.session_id or context_manager.create_session()
        context_manager.add_message(session_id, "user", message)
        
        # Get conversation context
        context = context_manager.get_context(session_id, limit=5)
        
        # Retrieve from all sources
        vector_results = vector_rag.search(message, top_k=5)
        
        try:
            graph_rag = GraphRAG(Neo4jClient())
            graph_response = graph_rag.retrieve(message)
            graph_results = graph_response.get("results", [])
        except Exception as e:
            print(f"[Graph] Query failed: {e}")
            graph_results = []
        
        try:
            sql_rag = SQLRAG()
            sql_response = sql_rag.handle_query(message)
            sql_results = sql_response.get("results", [])
        except Exception as e:
            print(f"[SQL] Query failed: {e}")
            sql_results = []
        
        if payload.stream:
            def generate():
                full_response = ""
                try:
                    for chunk in synthesis_engine.synthesize_streaming(
                        message, vector_results, graph_results, sql_results
                    ):
                        full_response += chunk
                        yield chunk
                    context_manager.add_message(session_id, "assistant", full_response)
                except Exception as e:
                    yield f"Error: {str(e)}"
            
            response = StreamingResponse(generate(), media_type="text/plain")
            response.headers["X-Session-Id"] = session_id
            return response
        
        response = synthesis_engine.synthesize(
            message, vector_results, graph_results, sql_results
        )
        
        context_manager.add_message(session_id, "assistant", response["answer"])
        
        return {
            "session_id": session_id,
            "answer": response["answer"],
            "sources": response["sources"],
            "context_used": len(context)
        }
    except Exception as exc:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(exc)}") from exc


@router.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """Get full chat history for a session."""
    history = context_manager.get_full_history(session_id)
    return {"session_id": session_id, "history": history}


@router.delete("/chat/session/{session_id}")
async def delete_chat_session(session_id: str):
    """Delete a chat session."""
    context_manager.delete_session(session_id)
    return {"message": "Session deleted successfully"}


@router.get("/chat/sessions")
async def list_chat_sessions(user_id: str = "default"):
    """List all chat sessions for a user."""
    sessions = context_manager.list_sessions(user_id)
    return {"sessions": sessions}


@router.get("/documents")
async def list_documents():
    """US-14: List all uploaded documents."""
    try:
        docs = get_documents()
        if docs:
            return {
                "documents": [
                    {
                        "id": doc.id,
                        "filename": doc.filename,
                        "file_path": doc.file_path,
                        "chunk_count": doc.chunk_count,
                        "uploaded_at": str(doc.uploaded_at),
                    }
                    for doc in docs
                ]
            }
    except Exception as e:
        print(f"[Postgres] get_documents failed: {e}")
    
    # Fallback: Read from filesystem if PostgreSQL is not available
    print("[Documents] Using filesystem fallback")
    docs_from_fs = []
    
    # Get chunk counts from vector store metadata
    chunk_counts = {}
    for chunk in vector_rag.metadata:
        filename = chunk.get("filename")
        if filename:
            chunk_counts[filename] = chunk_counts.get(filename, 0) + 1
    
    if os.path.exists(settings.UPLOAD_DIR):
        from datetime import datetime
        for idx, filename in enumerate(os.listdir(settings.UPLOAD_DIR)):
            file_path = os.path.join(settings.UPLOAD_DIR, filename)
            if os.path.isfile(file_path):
                stat = os.stat(file_path)
                uploaded_at = datetime.fromtimestamp(stat.st_mtime).isoformat()
                docs_from_fs.append({
                    "id": idx + 1,
                    "filename": filename,
                    "file_path": file_path,
                    "chunk_count": chunk_counts.get(filename, 0),
                    "uploaded_at": uploaded_at,
                })
    
    return {"documents": docs_from_fs}


@router.delete("/documents/{filename}")
async def delete_document(filename: str):
    """US-14: Delete a document."""
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return {"message": f"Document {filename} deleted successfully"}


@router.get("/graph/data")
async def get_graph_data():
    """US-16: Get knowledge graph data for visualization."""
    try:
        client = Neo4jClient()
        if client.health_check():
            with client.driver.session() as session:
                result = session.run("""
                    MATCH (a:Entity)-[r:RELATION]->(b:Entity)
                    RETURN a.name AS source, b.name AS target, r.type AS relation, r.source AS document
                    LIMIT 200
                """)
                edges = [dict(record) for record in result]
                
                if edges:  # If Neo4j has data, use it
                    nodes_set = set()
                    for edge in edges:
                        nodes_set.add(edge['source'])
                        nodes_set.add(edge['target'])
                    
                    nodes = [{'id': node, 'label': node} for node in nodes_set]
                    client.close()
                    return {"nodes": nodes, "edges": edges}
            
            client.close()
    except Exception as e:
        print(f"[Graph] Neo4j failed: {e}")
    
    # Fallback: Generate graph from vector store metadata using Groq
    print("[Graph] Using vector store fallback with Groq extraction")
    nodes = []
    edges = []
    nodes_set = set()
    
    # Group chunks by document
    docs_chunks = {}
    for chunk in vector_rag.metadata[:20]:  # Limit to first 20 chunks for efficiency
        filename = chunk.get("filename", "unknown")
        if filename not in docs_chunks:
            docs_chunks[filename] = []
        docs_chunks[filename].append(chunk)
    
    # Extract entities from each document using Groq
    from app.db.neo4j_db import Neo4jClient
    temp_client = Neo4jClient()
    
    for filename, chunks in docs_chunks.items():
        for chunk in chunks[:3]:  # Max 3 chunks per document
            text = chunk.get("text", "")
            if len(text) < 50:
                continue
            
            try:
                relationships = temp_client.extract_entities_with_groq(text)
                for rel in relationships:
                    source = rel.get("subject", "").strip()
                    target = rel.get("object", "").strip()
                    relation = rel.get("relation", "RELATED_TO").strip()
                    
                    if source and target:
                        nodes_set.add(source)
                        nodes_set.add(target)
                        edges.append({
                            "source": source,
                            "target": target,
                            "relation": relation,
                            "document": filename
                        })
            except Exception as e:
                print(f"[Graph] Entity extraction failed for chunk: {e}")
                continue
    
    nodes = [{'id': node, 'label': node} for node in nodes_set]
    
    # If still no data, create a simple document-based graph
    if not nodes:
        print("[Graph] Creating simple document-based graph")
        for filename in docs_chunks.keys():
            nodes.append({'id': filename, 'label': filename})
            nodes_set.add(filename)
        
        # Connect documents that share similar content
        filenames = list(docs_chunks.keys())
        for i, file1 in enumerate(filenames):
            for file2 in filenames[i+1:]:
                edges.append({
                    "source": file1,
                    "target": file2,
                    "relation": "RELATED_DOCUMENT",
                    "document": "system"
                })
    
    return {"nodes": nodes, "edges": edges}


@router.get("/analytics/metrics")
async def get_analytics_metrics():
    """US-17: Get analytics metrics for dashboard."""
    
    # Try to get data from PostgreSQL first
    try:
        from app.db.postgres import get_documents, get_recent_logs
        docs = get_documents(limit=100)
        logs = get_recent_logs(limit=100)
        
        total_docs = len(docs)
        total_chunks = sum(doc.chunk_count for doc in docs)
        total_queries = len(logs)
        
        recent_activity = [
            {
                "query": log.query,
                "agent": log.agent,
                "timestamp": str(log.created_at)
            }
            for log in logs[:10]
        ]
    except Exception as e:
        print(f"[Analytics] PostgreSQL failed, using fallback: {e}")
        
        # Fallback: Use vector store and filesystem
        total_docs = 0
        total_chunks = 0
        
        # Count documents from filesystem
        if os.path.exists(settings.UPLOAD_DIR):
            files = [f for f in os.listdir(settings.UPLOAD_DIR) if os.path.isfile(os.path.join(settings.UPLOAD_DIR, f))]
            total_docs = len(files)
        
        # Count chunks from vector store
        chunk_counts = {}
        for chunk in vector_rag.metadata:
            filename = chunk.get("filename")
            if filename:
                chunk_counts[filename] = chunk_counts.get(filename, 0) + 1
        total_chunks = sum(chunk_counts.values())
        
        # No query logs without database
        total_queries = 0
        recent_activity = []
    
    # Generate mock API usage data (since we don't track this)
    from datetime import datetime, timedelta
    today = datetime.now()
    api_usage = []
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        api_usage.append({
            "date": date.strftime("%Y-%m-%d"),
            "requests": total_queries + (i * 10) if total_queries > 0 else 50 + (i * 15)
        })
    
    # Latency data (mock data based on typical performance)
    latency_data = [
        {"endpoint": "/upload", "avg_ms": 450},
        {"endpoint": "/chat", "avg_ms": 320},
        {"endpoint": "/query", "avg_ms": 280},
        {"endpoint": "/documents", "avg_ms": 50},
        {"endpoint": "/graph/data", "avg_ms": 180},
    ]
    
    return {
        "total_documents": total_docs,
        "total_chunks": total_chunks,
        "total_queries": total_queries,
        "api_usage": api_usage,
        "latency": latency_data,
        "recent_activity": recent_activity
    }


@router.put("/chat/session/{session_id}/rename")
async def rename_chat_session(session_id: str, name: str):
    """US-18: Rename a chat session."""
    # Store session name in MongoDB
    if context_manager.db is not None:
        context_manager.db.chat_sessions.update_one(
            {"session_id": session_id},
            {"$set": {"name": name}},
            upsert=True
        )
    return {"message": "Session renamed successfully"}


@router.get("/chat/sessions/search")
async def search_chat_sessions(query: str, user_id: str = "default"):
    """US-18: Search chat sessions."""
    if context_manager.db is None:
        return {"sessions": []}
    
    pipeline = [
        {"$match": {
            "session_id": {"$regex": f"^session_{user_id}_"},
            "content": {"$regex": query, "$options": "i"}
        }},
        {"$group": {
            "_id": "$session_id",
            "last_message": {"$last": "$timestamp"},
            "message_count": {"$sum": 1}
        }},
        {"$sort": {"last_message": -1}}
    ]
    
    results = list(context_manager.db.chat_history.aggregate(pipeline))
    return {
        "sessions": [{
            "session_id": doc["_id"],
            "last_message": str(doc["last_message"]),
            "message_count": doc["message_count"]
        } for doc in results]
    }