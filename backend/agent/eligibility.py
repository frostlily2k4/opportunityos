"""
Stage 3: eligibility.
Compares an extracted opportunity against the user's profile and
explicitly checks deadline status.
"""

import json
from datetime import date
from .llm import call_claude_json


SYSTEM = """
You are the eligibility stage of an AI opportunity discovery agent.

Determine whether a student can reasonably apply to an opportunity.

Evaluate these factors:

1. Education / student status
2. Required skills
3. Location / remote eligibility
4. Experience requirements
5. Application deadline

Be conservative and NEVER invent requirements.

IMPORTANT DEADLINE RULES:

- Today's date is supplied in the user prompt.
- If the deadline is a real date before today, the opportunity is EXPIRED.
- If the deadline is today or in the future, it is NOT expired.
- If the deadline is unknown, say so.
- Never assume an unknown deadline is still open.

Use these status values:

- "eligible"
- "ineligible"
- "unclear"
- "expired"

The "eligible" field must be:
- true when the student appears eligible
- false when clearly ineligible or expired
- "unclear" when there is not enough information

Return only valid JSON.
"""


def check_eligibility(opportunity: dict, profile: dict) -> dict:
    today = date.today().isoformat()

    user = f"""
Today's date:
{today}

User profile:
{json.dumps(profile, indent=2)}

Opportunity:
{json.dumps(opportunity, indent=2)}

Return JSON in exactly this structure:

{{
  "eligible": true | false | "unclear",
  "status": "eligible" | "ineligible" | "unclear" | "expired",
  "reasons": [
    "short, specific reasons for the verdict"
  ],
  "missing_info": [
    "profile or opportunity information needed to be sure"
  ]
}}

Rules:

- Check the opportunity's actual deadline against today's date.
- If the deadline has passed, status MUST be "expired" and eligible MUST be false.
- If the opportunity has no usable eligibility information, status should be
  "unclear" rather than guessing.
- If the opportunity is clearly incompatible with the student's education,
  skills, location, or other stated requirements, status should be
  "ineligible".
- If the requirements match the profile and the deadline is still open,
  status should be "eligible".
- Use only information explicitly present in the opportunity and profile.
- Keep reasons concise and factual.
"""

    result = call_claude_json(SYSTEM, user)

    # Defensive defaults so the pipeline always receives a predictable shape.
    result.setdefault("eligible", "unclear")
    result.setdefault("status", "unclear")
    result.setdefault("reasons", [])
    result.setdefault("missing_info", [])

    opportunity["eligibility"] = result

    return opportunity