"""
Best-effort cache: if you run a query once successfully, this saves the raw
search results to disk. If the live search fails later (bad wifi at the
venue, rate limit, etc.) for that *exact* query, we serve the cached copy
instead of showing an error mid-demo.

Tip: run your planned demo queries once during rehearsal so they're warm.
We deliberately do NOT fall back across different queries - showing
internships when someone asked for hackathons would look broken, not smart.
"""
import os
import json
import hashlib
import glob

CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "_cache")
os.makedirs(CACHE_DIR, exist_ok=True)


def _path(query: str) -> str:
    h = hashlib.md5(query.strip().lower().encode()).hexdigest()
    return os.path.join(CACHE_DIR, f"{h}.json")


def save_cache(query: str, results: list[dict]) -> None:
    try:
        with open(_path(query), "w") as f:
            json.dump(results, f)
    except Exception:
        pass  # caching is best-effort, never break the pipeline over it


def get_cached_fallback(query: str) -> list[dict]:
    p = _path(query)
    if os.path.exists(p):
        with open(p) as f:
            return json.load(f)
    return []


def list_cached_queries() -> list[str]:
    return [os.path.basename(f) for f in glob.glob(os.path.join(CACHE_DIR, "*.json"))]
