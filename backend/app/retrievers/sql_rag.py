from __future__ import annotations

from app.db.postgres import (
    get_document_count,
    get_documents,
    get_recent_logs,
    get_total_chunks,
)


class SQLRAG:
    """Handles ONLY file/system metadata queries. Document content goes to vector_rag."""

    def _is_count_query(self, normalized: str) -> bool:
        patterns = (
            "how many files",
            "how many documents",
            "file count",
            "document count",
            "count of files",
            "count of documents",
            "count uploaded",
        )
        return any(pattern in normalized for pattern in patterns)

    def _is_chunk_query(self, normalized: str) -> bool:
        patterns = (
            "how many chunks",
            "chunks indexed",
            "indexed chunks",
            "total chunks",
            "chunk count",
            "count chunks",
            "count of chunks",
        )
        return any(pattern in normalized for pattern in patterns)

    def _is_list_query(self, normalized: str) -> bool:
        patterns = (
            "list all files",
            "list all documents",
            "show uploaded files",
            "show all files",
            "show all documents",
            "uploaded files",
            "uploaded documents",
            "show files",
            "show documents",
            "all files",
            "all documents",
            "list files",
            "list documents",
        )
        return any(pattern in normalized for pattern in patterns)

    def _is_log_query(self, normalized: str) -> bool:
        patterns = (
            "log",
            "logs",
            "recent queries",
            "query history",
            "retrieval history",
            "show recent queries",
        )
        return any(pattern in normalized for pattern in patterns)

    def handle_query(self, query: str):
        normalized = query.lower().strip()

        if self._is_count_query(normalized):
            return {
                "query": query,
                "status": "ok",
                "agent": "sql",
                "results": [{"count": get_document_count()}],
                "message": "Retrieved uploaded document count.",
            }

        if self._is_chunk_query(normalized):
            return {
                "query": query,
                "status": "ok",
                "agent": "sql",
                "results": [{"total_chunks": get_total_chunks()}],
                "message": "Retrieved total indexed chunk count.",
            }

        if self._is_log_query(normalized):
            return {
                "query": query,
                "status": "ok",
                "agent": "sql",
                "results": [
                    {
                        "id": log.id,
                        "query": log.query,
                        "agent": log.agent,
                        "response_preview": log.response_preview,
                        "created_at": str(log.created_at),
                    }
                    for log in get_recent_logs()
                ],
                "message": "Retrieved recent retrieval logs.",
            }

        if self._is_list_query(normalized):
            return {
                "query": query,
                "status": "ok",
                "agent": "sql",
                "results": [
                    {
                        "id": doc.id,
                        "filename": doc.filename,
                        "file_path": doc.file_path,
                        "chunk_count": doc.chunk_count,
                        "uploaded_at": str(doc.uploaded_at),
                    }
                    for doc in get_documents()
                ],
                "message": "Retrieved document metadata from PostgreSQL.",
            }

        return {
            "query": query,
            "status": "ok",
            "agent": "sql",
            "results": [],
            "message": "Query did not match any SQL metadata pattern. Try asking about document content instead.",
        }