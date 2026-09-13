"""
Anakin web reader.

Uses Anakin's URL Scraper to turn live webpages into clean Markdown
before Gemini performs opportunity extraction and reasoning.
"""

import os
import requests


ANAKIN_SCRAPE_URL = "https://api.anakin.io/v1/url-scraper/scrape"


def scrape_with_anakin(url: str) -> str:
    """
    Read a webpage using Anakin and return clean Markdown.

    Anakin's Zero Touch read-only scraper can work without an API key.
    If ANAKIN_API_KEY is available, it is sent for authenticated usage.
    """

    headers = {
        "Content-Type": "application/json"
    }

    api_key = os.environ.get("ANAKIN_API_KEY")

    if api_key:
        headers["X-API-Key"] = api_key

    response = requests.post(
        ANAKIN_SCRAPE_URL,
        headers=headers,
        json={
            "url": url
        },
        timeout=90,
    )

    response.raise_for_status()

    data = response.json()

    markdown = data.get("markdown", "")

    if not markdown:
        raise RuntimeError(
            "Anakin returned no webpage content."
        )

    return markdown