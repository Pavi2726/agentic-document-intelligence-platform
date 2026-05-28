from __future__ import annotations


# SQL: file/system/query metadata questions.
# These should be answered from PostgreSQL, not from document chunks.
SQL_EXACT_PHRASES = [
    "how many documents",
    "how many files",
    "how many chunks",
    "how many queries",
    "list all files",
    "list all documents",
    "list files",
    "list documents",
    "show uploaded files",
    "show all files",
    "show all documents",
    "show files",
    "show documents",
    "uploaded files",
    "uploaded documents",
    "file count",
    "document count",
    "chunk count",
    "query count",
    "chunks indexed",
    "indexed chunks",
    "total chunks",
    "files in the system",
    "documents in the system",
    "recently uploaded",
    "recent uploads",
    "recent queries",
    "query history",
    "all files",
    "all documents",
]


# Web search: real-world/current information not guaranteed
# to exist inside uploaded documents.
WEB_SEARCH_KEYWORDS = [
    "ceo of",
    "founder of",
    "who runs",
    "who leads",
    "who is the ceo",
    "who is the founder",
    "stock price",
    "share price",
    "market cap",
    "latest news",
    "recent news",
    "news about",
    "trending",
    "ai trends",
    "web search",
    "right now",
    "currently working at",
    "headquarters of",
    "latest",
    "today",
    "current",
    "recent",
    "live",
    "now",
]


# Graph RAG: relationship/entity questions.
# These should be answered using Neo4j.
GRAPH_KEYWORDS = [
    "relationship between",
    "relation between",
    "connected to",
    "connection between",
    "linked to",
    "associated with",
    "relationship of",
    "relation of",
    "how is",
    "connected",
    "graph",
    "entities in",
    "node",
    "edge",
]


def classify_query(query: str) -> str:
    """
    Classify user query into one backend route.

    Returns:
    - sql
    - web_search
    - graph_rag
    - vector_rag
    """

    normalized = query.lower().strip()

    # 1. SQL first because some SQL phrases contain words like "recent",
    # which could otherwise be mistaken for web search.
    if any(phrase in normalized for phrase in SQL_EXACT_PHRASES):
        return "sql"

    # 2. Web search for current/live/external knowledge.
    if any(keyword in normalized for keyword in WEB_SEARCH_KEYWORDS):
        return "web_search"

    # 3. Graph RAG for relationship/entity questions.
    if any(keyword in normalized for keyword in GRAPH_KEYWORDS):
        return "graph_rag"

    # 4. Default route: document content retrieval from FAISS.
    return "vector_rag"


def route_query(query: str):
    """
    Returns the selected category and a human-readable routing reason.
    """

    category = classify_query(query)

    reasons = {
        "vector_rag": "Matched document content retrieval intent from the query.",
        "graph_rag": "Matched graph relationship intent from the query.",
        "sql": "Matched file/system metadata intent from the query.",
        "web_search": "Matched external real-world information intent from the query.",
    }

    return category, reasons[category]