"""
LLM wrapper for Google Gemini.

Every reasoning stage in the pipeline (extract / eligibility /
score / checklist) calls through this module so there is one
place to handle JSON parsing, retries, and API errors.
"""

import os
import re
import json
import time

from google import genai


_client = None

# Gemini model used for the hackathon prototype.
MODEL = "gemini-2.5-flash"


def _get_client():
    """Create and return the Gemini client."""

    global _client

    if _client is None:
        api_key = os.environ.get("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Add it to backend/.env"
            )

        _client = genai.Client(api_key=api_key)

    return _client


def _strip_fences(text: str) -> str:
    """Remove markdown code fences if Gemini returns them."""

    text = text.strip()

    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    return text.strip()


def _extract_json(text: str) -> dict:
    """Try to extract a JSON object from Gemini's response."""

    text = _strip_fences(text)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Fallback: find the first JSON object in the response.
    match = re.search(
        r"\{.*\}",
        text,
        re.DOTALL
    )

    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    raise ValueError(
        "Gemini returned a response that could not be parsed as JSON."
    )


def call_claude_json(
    system: str,
    user: str,
    max_tokens: int = 1024
) -> dict:
    """
    Call Gemini and parse a JSON object from the response.

    The function name is intentionally kept as call_claude_json
    so the existing agent files do not need to be changed.
    """

    client = _get_client()

    full_prompt = (
        system
        + "\n\n"
        + "Respond with ONLY a valid JSON object."
        + " No markdown fences."
        + " No commentary before or after."
        + "\n\nUSER TASK:\n"
        + user
    )

    last_error = None

    for attempt in range(2):

        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=full_prompt,
                config={
                    "temperature": 0.2,
                    "max_output_tokens": max_tokens,
                    "response_mime_type": "application/json",
                },
            )

            text = response.text or ""

            return _extract_json(text)

        except json.JSONDecodeError as exc:

            last_error = exc

            full_prompt += (
                "\n\nYour previous response was not valid JSON."
                "\nReturn ONLY a valid JSON object."
            )

        except ValueError as exc:

            last_error = exc

            full_prompt += (
                "\n\nYour previous response was not valid JSON."
                "\nReturn ONLY a valid JSON object."
            )

        except Exception as exc:

            last_error = exc

            print(
                f"Gemini API error "
                f"(attempt {attempt + 1}/2): {exc}"
            )

            # Do not immediately retry quota errors.
            error_text = str(exc)

            if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
                raise RuntimeError(
                    "Gemini API quota has been exceeded. "
                    "Please wait for the quota to reset or check "
                    "your Gemini API usage/billing limits."
                ) from exc

            if attempt == 0:
                time.sleep(1)

    raise RuntimeError(
        f"Gemini API request failed after retries: {last_error}"
    ) from last_error