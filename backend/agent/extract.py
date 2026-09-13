"""
Stage 2: Extract.
Turns messy webpage text into a structured opportunity record.
"""

from .llm import call_claude_json


SYSTEM = """
You are the extraction stage of an AI opportunity discovery agent.

Your job is to determine whether a webpage contains a SPECIFIC,
ACTIONABLE opportunity such as:

- an internship
- a hackathon
- a scholarship
- a competition

A useful opportunity page should contain enough information to help
a student actually evaluate or apply for it.

IMPORTANT:

1. Do NOT treat generic search pages as opportunities.
2. Do NOT treat category/listing pages as a single opportunity.
3. Do NOT treat Reddit discussions as opportunities.
4. Do NOT treat Instagram/social-media posts as the primary opportunity.
5. Do NOT treat news articles or general advice articles as opportunities.
6. Do NOT invent missing information.
7. If the page is not a specific opportunity, set:
   "is_specific_opportunity": false
8. If the page IS a specific opportunity, set:
   "is_specific_opportunity": true.
"""


def extract_details(raw: dict) -> dict:

    user = f"""
Page title:
{raw['title']}

Page URL:
{raw['url']}

Page content:
---
{raw['content']}
---

Return ONLY valid JSON using this structure:

{{
  "is_specific_opportunity": true,
  "title": "",
  "organization": "",
  "type": "internship|hackathon|scholarship|competition|other",
  "deadline": "ISO date or unknown",
  "location": "remote / city, country / unknown",
  "eligibility_requirements": [],
  "required_documents": [],
  "stipend_or_prize": "string or unknown",
  "apply_url": "",
  "summary": ""
}}

Rules:

- is_specific_opportunity must be false for generic search pages,
  listing pages, social posts, discussion threads, news articles,
  and general informational pages.
- For a specific opportunity, extract only information explicitly
  present on the page.
- Do not guess eligibility.
- Do not guess deadlines.
- Do not guess organizations.
- apply_url should be the best actual application URL found.
- If no application URL is available, use the original page URL.
- summary must be exactly two concise sentences.
"""

    result = call_claude_json(SYSTEM, user)

    result.setdefault("is_specific_opportunity", False)
    result.setdefault("apply_url", raw["url"])
    result["source_url"] = raw["url"]

    return result