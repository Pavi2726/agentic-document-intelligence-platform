from __future__ import annotations

from app.db.neo4j_db import Neo4jClient


class GraphRAG:
    def __init__(self, client: Neo4jClient | None = None):
        self.client = client or Neo4jClient()

    def initialize(self) -> None:
        self.client.initialize_schema()

    def retrieve(self, query: str):
        if not self.client.health_check():
            return {
                "query": query,
                "status": "unavailable",
                "results": [],
                "message": "Neo4j is not available right now.",
            }

        results = self.client.search_relationships(query)
        if not results:
            return {
                "query": query,
                "status": "ok",
                "results": [],
                "message": "No graph relationships matched the query.",
            }

        return {
            "query": query,
            "status": "ok",
            "results": results,
            "message": f"Returned {len(results)} relationship result(s).",
        }
