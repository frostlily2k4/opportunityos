"""
Stage 1: Search.
Finds specific, actionable opportunity pages on the live web using Tavily.
"""

import os
import requests

TAVILY_URL = "https://api.tavily.com/search"


def search_opportunities(query: str, max_results: int = 8) -> list[dict]:
    api_key = os.environ.get("TAVILY_API_KEY")

    if not api_key:
        raise RuntimeError(
            "TAVILY_API_KEY is not set (see .env.example)"
        )

    search_query = f"""
{query}
specific internship hackathon scholarship competition opportunity
official application page
eligibility requirements
deadline
apply
2026
"""

    resp = requests.post(
        TAVILY_URL,
        json={
            "api_key": api_key,
            "query": search_query,
            "search_depth": "advanced",
            "include_raw_content": True,
            "max_results": max_results,
            "topic": "general",
        },
        timeout=25,
    )

    resp.raise_for_status()
    data = resp.json()

    results = []

    for r in data.get("results", []):
        content = (
            r.get("raw_content")
            or r.get("content")
            or ""
        )

        url = r.get("url")

        if not content or not url:
            continue

        results.append(
            {
                "title": r.get("title", "Untitled"),
                "url": url,
                "content": content[:8000],
            }
        )

    return results