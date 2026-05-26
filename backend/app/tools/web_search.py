from __future__ import annotations

import time
from ddgs import DDGS


class WebSearchTool:
    def search(self, query: str, max_results: int = 5):
        results = []

        for attempt in range(3):
            try:
                with DDGS() as ddgs:
                    search_results = list(ddgs.text(
                        query,
                        max_results=max_results,
                    ))
                    for item in search_results:
                        results.append({
                            "title": item.get("title", ""),
                            "href": item.get("href", ""),
                            "body": item.get("body", ""),
                        })
                if results:
                    break
            except Exception as e:
                if attempt < 2:
                    time.sleep(2)
                else:
                    return {
                        "query": query,
                        "results": [],
                        "message": f"Web search failed: {str(e)}",
                        "agent": "web_search",
                    }

        return {
            "query": query,
            "results": results,
            "message": f"Returned {len(results)} search result(s).",
            "agent": "web_search",
        }