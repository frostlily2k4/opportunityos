"""
Stage 4: score.
Produces a 0-100 fit score used for ranking.

Expired and clearly ineligible opportunities receive 0.
"""

import json
from .llm import call_claude_json


SYSTEM = """
You are the scoring stage of an AI opportunity discovery agent.

Score how useful an opportunity is for a specific student from 0 to 100.

IMPORTANT HARD RULES:

1. EXPIRED opportunities MUST receive score 0.
2. Clearly INELIGIBLE opportunities MUST receive score 0.
3. Opportunities with UNCLEAR eligibility can receive a moderate score,
   but should not outrank clearly eligible opportunities.
4. Never give an expired opportunity a positive recommendation.
5. Never invent information that is missing from the opportunity.

For active opportunities, consider:

- Eligibility fit
- Relevance to the student's skills and interests
- Deadline/actionability
- Overall value, prize, stipend, learning potential, or prestige

Return only valid JSON.
"""


def score_opportunity(opportunity: dict, profile: dict) -> dict:

    eligibility = opportunity.get("eligibility", {})

    status = eligibility.get("status")
    eligible = eligibility.get("eligible")

    # Hard safety rule: expired opportunities must never be recommended.
    if status == "expired":
        opportunity["score"] = 0
        opportunity["score_rationale"] = (
            "This opportunity has expired and is no longer actionable."
        )
        return opportunity

    # Hard safety rule: clearly ineligible opportunities must not rank highly.
    if status == "ineligible" or eligible is False:
        opportunity["score"] = 0
        opportunity["score_rationale"] = (
            "The student does not appear eligible for this opportunity."
        )
        return opportunity

    user = f"""
Profile:
{json.dumps(profile, indent=2)}

Opportunity:
{json.dumps(opportunity, indent=2)}

Eligibility:
{json.dumps(eligibility, indent=2)}

Today's date should be considered when evaluating the deadline.

Return JSON:

{{
  "score": <integer from 0 to 100>,
  "rationale": "one or two concise sentences explaining the score"
}}

Rules:

- The opportunity must not be expired.
- If eligibility status is "eligible", it can receive a high score
  when the opportunity strongly matches the profile.
- If eligibility status is "unclear", keep the score moderate because
  important information is missing.
- Consider skills, education, location, deadline, and overall opportunity
  value.
- Do not invent missing information.
"""

    result = call_claude_json(SYSTEM, user)

    score = result.get("score", 0)

    # Defensive validation.
    try:
        score = int(score)
    except (TypeError, ValueError):
        score = 0

    score = max(0, min(100, score))

    opportunity["score"] = score
    opportunity["score_rationale"] = result.get("rationale", "")

    return opportunity