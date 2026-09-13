"""
Stage 5: act.

Generates concrete application artifacts for actionable opportunities:
a checklist and a tailored draft note.

Expired and clearly ineligible opportunities are not given application
actions.
"""

import json
from .llm import call_claude_json


CHECKLIST_SYSTEM = """
You are the ACT stage of an AI opportunity discovery agent.

Your job is to turn an actionable opportunity into concrete next steps
for the student.

Only generate application actions when the opportunity is actionable.

If the opportunity is:
- expired
- clearly ineligible
- missing enough information to act safely

return an empty checklist.

Never invent application requirements.
Never claim that an application was submitted.
"""


DRAFT_SYSTEM = """
You write a short, tailored application email or cover note for a student.

Only create a draft when the opportunity is actionable and the student
appears eligible.

Use only facts present in the opportunity and profile.
Never invent experience, projects, achievements, or qualifications.
Do not claim that an application was submitted.
"""


def _is_actionable(opportunity: dict) -> bool:
    eligibility = opportunity.get("eligibility", {})

    status = eligibility.get("status")
    eligible = eligibility.get("eligible")

    if status in {"expired", "ineligible"}:
        return False

    if eligible is False:
        return False

    return True


def generate_checklist(opportunity: dict, profile: dict) -> list[str]:

    if not _is_actionable(opportunity):
        return []

    user = f"""
Opportunity:
{json.dumps(opportunity, indent=2)}

Profile:
{json.dumps(profile, indent=2)}

Return JSON:

{{
  "checklist": [
    "step 1",
    "step 2"
  ]
}}

Create 5-8 concrete, ordered application steps.

Prioritize:
- documents explicitly required
- eligibility details to verify
- application form steps
- portfolio/GitHub requirements if explicitly stated
- deadline
- final submission check

Do not invent requirements.
Do not include generic filler.
"""


    result = call_claude_json(CHECKLIST_SYSTEM, user)

    checklist = result.get("checklist", [])

    if not isinstance(checklist, list):
        return []

    return [
        str(step).strip()
        for step in checklist
        if str(step).strip()
    ][:8]


def generate_draft(opportunity: dict, profile: dict) -> str:

    if not _is_actionable(opportunity):
        return ""

    user = f"""
Opportunity:
{json.dumps(opportunity, indent=2)}

Profile:
{json.dumps(profile, indent=2)}

Return JSON:

{{
  "draft": "the email or cover note text"
}}

Write 120-180 words.

Make it specific to this opportunity and this profile.

You may reference:
- the student's actual degree
- actual skills
- actual interests
- actual projects or experience if provided

Do not invent anything.

Plain text only.
No subject line.
Sign off with the student's name if one is provided.
"""


    result = call_claude_json(DRAFT_SYSTEM, user)

    draft = result.get("draft", "")

    if not isinstance(draft, str):
        return ""

    return draft.strip()