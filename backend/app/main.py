from dotenv import load_dotenv

load_dotenv()

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router
from app.core.config import settings
from app.db.neo4j_db import Neo4jClient
from app.db.postgres import init_db
from app.retrievers.graph_rag import GraphRAG
from app.retrievers.vector_rag import VectorRAGStore

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.VECTOR_STORE_DIR, exist_ok=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend Multi-Agent retrieval engine for documents",
    version="1.0.0",
)

# Increase file upload size limit to 50MB
app.router.route_class = type(
    "CustomRoute",
    (app.router.route_class,),
    {"max_body_size": 50 * 1024 * 1024}
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    try:
        init_db()
    except Exception:
        pass

    try:
        VectorRAGStore()
    except Exception:
        pass

    try:
        graph_client = Neo4jClient()
        graph_rag = GraphRAG(client=graph_client)
        graph_rag.initialize()
        graph_client.close()
    except Exception:
        pass


app.include_router(api_router, prefix="/api")


@app.get("/")
def read_root():
    return {"message": f"Welcome to the {settings.PROJECT_NAME} API. Access /docs for swagger UI."}
