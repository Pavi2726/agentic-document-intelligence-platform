from __future__ import annotations

from typing import TypedDict

from groq import Groq
from langgraph.graph import END, StateGraph

from app.agents.router import route_query
from app.core.config import settings
from app.retrievers.graph_rag import GraphRAG
from app.retrievers.sql_rag import SQLRAG
from app.retrievers.vector_rag import vector_rag
from app.tools.web_search import WebSearchTool

MIN_SCORE_THRESHOLD = 0.30


class SupervisorState(TypedDict):
    query: str
    category: str
    reason: str
    result: dict


graph_rag = GraphRAG()
sql_rag = SQLRAG()
web_search_tool = WebSearchTool()
groq_client = Groq(api_key=settings.GROQ_API_KEY)

def synthesize_answer(query: str, chunks: list[dict]) -> str:
    relevant_chunks = [c for c in chunks if c.get("score", 0) >= MIN_SCORE_THRESHOLD]

    if not relevant_chunks:
        return "No relevant information found in the document."

    context = "\n\n".join(
        [f"[Chunk {i}]:\n{c.get('text', '')}"
         for i, c in enumerate(relevant_chunks[:5])]
    )

    prompt = f"""Read these document excerpts and answer the question directly.
If you see names, dates, amounts — use them in your answer.

Excerpts:
{context}

Question: {query}
Answer:"""

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.1,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"LLM synthesis failed: {e}"
    
def classify_node(state: SupervisorState):
    category, reason = route_query(state["query"])
    return {
        "query": state["query"],
        "category": category,
        "reason": reason,
        "result": {},
    }


def retrieve_node(state: SupervisorState):
    category = state["category"]
    query = state["query"]

    if category == "vector_rag":
        raw_results = vector_rag.search(query)
        answer = synthesize_answer(query, raw_results)
        result = {
            "agent": "vector_rag",
            "answer": answer,                    # ← Direct natural language answer
            "results": raw_results,              # ← Raw chunks still included
            "message": "Retrieved and synthesized answer from document chunks.",
        }

    elif category == "graph_rag":
        result = graph_rag.retrieve(query)
        result["agent"] = "graph_rag"

    elif category == "sql":
        result = sql_rag.handle_query(query)
        result["agent"] = "sql"

    else:  # web_search
        result = web_search_tool.search(query)
        result["agent"] = "web_search"

    return {
        "query": query,
        "category": category,
        "reason": state["reason"],
        "result": result,
    }


workflow = StateGraph(SupervisorState)
workflow.add_node("classify", classify_node)
workflow.add_node("retrieve", retrieve_node)
workflow.set_entry_point("classify")
workflow.add_edge("classify", "retrieve")
workflow.add_edge("retrieve", END)

supervisor_workflow = workflow.compile()


def run_supervisor(query: str):
    result = supervisor_workflow.invoke({
        "query": query,
        "category": "",
        "reason": "",
        "result": {},
    })
    return result