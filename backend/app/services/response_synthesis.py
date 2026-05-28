"""US-11: Response Synthesis Engine - Combines vector, graph, and keyword search results."""
from __future__ import annotations

import concurrent.futures
import traceback

from groq import Groq
from app.core.config import settings


class ResponseSynthesisEngine:
    def __init__(self):
        try:
            self.client = Groq(api_key=settings.GROQ_API_KEY)
        except Exception as e:
            print(f"Warning: Groq client initialization failed: {e}")
            self.client = None

    def _build_context(
        self,
        vector_results: list[dict],
        graph_results: list[dict],
        sql_results: list[dict],
    ) -> str:
        context_parts = []

        if vector_results:
            context_parts.append(
                "Vector Search Results:\n" + "\n".join(
                    f"- {r.get('text', '')[:200]}" for r in vector_results[:3]
                )
            )

        if graph_results:
            context_parts.append(
                "Knowledge Graph Results:\n" + "\n".join(
                    f"- {r.get('source', '')} -> {r.get('relationship', '')} -> {r.get('target', '')}"
                    for r in graph_results[:3]
                )
            )

        if sql_results:
            context_parts.append(f"Metadata Results:\n{sql_results}")

        return "\n\n".join(context_parts) if context_parts else "No relevant context found."

    def _call_groq(self, messages: list[dict], stream: bool):
        if not self.client:
            raise RuntimeError("Groq client is not available.")

        def do_call():
            return self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
                stream=stream,
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(do_call)
            try:
                return future.result(timeout=25)
            except concurrent.futures.TimeoutError:
                future.cancel()
                raise TimeoutError("Groq API request timed out after 25 seconds.")
            except Exception:
                traceback.print_exc()
                raise

    def synthesize(
        self,
        query: str,
        vector_results: list[dict],
        graph_results: list[dict],
        sql_results: list[dict],
    ) -> dict:
        """Combine all retrieval results into one coherent AI response."""
        if not self.client:
            return {
                "query": query,
                "answer": "Groq API is not available. Please check your API key configuration.",
                "sources": {
                    "vector_count": len(vector_results),
                    "graph_count": len(graph_results),
                    "sql_count": len(sql_results),
                },
            }

        context = self._build_context(vector_results, graph_results, sql_results)
        
        # Check if we have relevant document context (score threshold)
        has_relevant_context = any(
            result.get('score', 0) > 0.3 for result in vector_results
        ) if vector_results else False
        
        if has_relevant_context:
            # We have relevant document context - try to answer from it first
            system_prompt = """You are a helpful AI assistant. Answer the question using the provided context from documents. 
            If the context contains relevant information, use it to answer. 
            If the context doesn't fully answer the question, you can supplement with your general knowledge.
            Always be helpful and provide the best answer possible."""
            user_prompt = f"Context from documents:\n{context}\n\nQuestion: {query}\n\nProvide a helpful answer:"
        else:
            # No relevant context - use general knowledge
            system_prompt = "You are a helpful AI assistant. Answer questions clearly and accurately using your knowledge."
            user_prompt = f"Question: {query}\n\nProvide a helpful and accurate answer:"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            response = self._call_groq(messages=messages, stream=False)
        except Exception as exc:
            return {
                "query": query,
                "answer": f"Error generating response: {exc}",
                "sources": {
                    "vector_count": len(vector_results),
                    "graph_count": len(graph_results),
                    "sql_count": len(sql_results),
                },
            }

        return {
            "query": query,
            "answer": response.choices[0].message.content,
            "sources": {
                "vector_count": len(vector_results),
                "graph_count": len(graph_results),
                "sql_count": len(sql_results),
            },
        }

    def synthesize_streaming(
        self,
        query: str,
        vector_results: list[dict],
        graph_results: list[dict],
        sql_results: list[dict],
    ):
        """Stream the synthesized response for real-time UI updates."""
        context = self._build_context(vector_results, graph_results, sql_results)
        
        # Check if we have relevant document context (score threshold)
        has_relevant_context = any(
            result.get('score', 0) > 0.3 for result in vector_results
        ) if vector_results else False
        
        if has_relevant_context:
            # We have relevant document context - try to answer from it first
            system_prompt = """You are a helpful AI assistant. Answer the question using the provided context from documents. 
            If the context contains relevant information, use it to answer. 
            If the context doesn't fully answer the question, you can supplement with your general knowledge.
            Always be helpful and provide the best answer possible."""
            user_prompt = f"Context from documents:\n{context}\n\nQuestion: {query}\n\nProvide a helpful answer:"
        else:
            # No relevant context - use general knowledge
            system_prompt = "You are a helpful AI assistant. Answer questions clearly and accurately using your knowledge."
            user_prompt = f"Question: {query}\n\nProvide a helpful and accurate answer:"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            stream = self._call_groq(messages=messages, stream=True)
        except Exception as exc:
            yield f"Error generating response: {exc}"
            return

        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


synthesis_engine = ResponseSynthesisEngine()
