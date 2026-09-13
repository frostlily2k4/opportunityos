"""
OpportunityOS Pipeline

Orchestrates:

Search
-> Extract
-> Filter generic pages
-> Check eligibility
-> Score + rank
-> Act

Each stage yields a progress update so the frontend can render
the pipeline live.
"""

import asyncio

from .search import search_opportunities
from .extract import extract_details
from .eligibility import check_eligibility
from .scoring import score_opportunity
from .checklist import generate_checklist, generate_draft
from .cache import save_cache, get_cached_fallback


TOP_N = 5


async def run_pipeline_stream(query: str, profile: dict):

    # ============================================================
    # 1. SEARCH
    # ============================================================

    yield {
        "stage": "search",
        "status": "running",
        "message": "Searching live opportunities..."
    }

    try:
        raw_results = await asyncio.to_thread(
            search_opportunities,
            query
        )

        if not raw_results:
            raise ValueError("No live results found.")

        save_cache(query, raw_results)

    except Exception as exc:

        print(f"Search error: {exc}")

        raw_results = get_cached_fallback(query)

        if raw_results:

            yield {
                "stage": "search",
                "status": "warning",
                "message": (
                    "Live search failed - using a cached run "
                    "for this query."
                )
            }

        else:

            yield {
                "stage": "search",
                "status": "error",
                "message": (
                    "Live search failed and no cached results "
                    "exist for this exact query."
                )
            }

            yield {
                "stage": "done",
                "status": "error",
                "message": "Nothing to show.",
                "data": []
            }

            return

    yield {
        "stage": "search",
        "status": "done",
        "message": (
            f"Found {len(raw_results)} candidate pages."
        )
    }

    # ============================================================
    # 2. EXTRACT
    # ============================================================

    yield {
        "stage": "extract",
        "status": "running",
        "message": (
            "Reading pages and extracting opportunity details..."
        )
    }

    try:

        extracted = await asyncio.gather(
            *[
                asyncio.to_thread(
                    extract_details,
                    r
                )
                for r in raw_results
            ]
        )

    except Exception as exc:

        print(f"Extraction error: {exc}")

        yield {
            "stage": "extract",
            "status": "error",
            "message": (
                f"Opportunity extraction failed: {exc}"
            )
        }

        yield {
            "stage": "done",
            "status": "error",
            "message": "Pipeline stopped.",
            "data": []
        }

        return

    # ============================================================
    # 3. FILTER GENERIC / INVALID PAGES
    # ============================================================

    specific_opportunities = [
        opportunity
        for opportunity in extracted
        if opportunity.get(
            "is_specific_opportunity",
            False
        ) is True
    ]

    rejected_count = (
        len(extracted)
        - len(specific_opportunities)
    )

    if not specific_opportunities:

        yield {
            "stage": "extract",
            "status": "warning",
            "message": (
                "No specific actionable opportunities "
                "were found in the search results."
            )
        }

        yield {
            "stage": "done",
            "status": "done",
            "message": "No actionable opportunities found.",
            "data": []
        }

        return

    yield {
        "stage": "extract",
        "status": "done",
        "message": (
            f"Found {len(specific_opportunities)} specific "
            f"opportunities and filtered out "
            f"{rejected_count} generic pages."
        )
    }

    # ============================================================
    # 4. ELIGIBILITY
    # ============================================================

    yield {
        "stage": "eligibility",
        "status": "running",
        "message": (
            "Checking eligibility against your profile..."
        )
    }

    try:

        checked = await asyncio.gather(
            *[
                asyncio.to_thread(
                    check_eligibility,
                    opportunity,
                    profile
                )
                for opportunity in specific_opportunities
            ]
        )

    except Exception as exc:

        print(f"Eligibility error: {exc}")

        yield {
            "stage": "eligibility",
            "status": "error",
            "message": (
                f"Eligibility check failed: {exc}"
            )
        }

        yield {
            "stage": "done",
            "status": "error",
            "message": "Pipeline stopped.",
            "data": []
        }

        return

    eligible_count = sum(
        1
        for opportunity in checked
        if opportunity.get(
            "eligibility",
            {}
        ).get("status") == "eligible"
    )

    yield {
        "stage": "eligibility",
        "status": "done",
        "message": (
            f"Eligibility checked. "
            f"{eligible_count} opportunities appear eligible."
        )
    }

    # ============================================================
    # 5. SCORE
    # ============================================================

    yield {
        "stage": "score",
        "status": "running",
        "message": "Scoring opportunities..."
    }

    try:

        scored = await asyncio.gather(
            *[
                asyncio.to_thread(
                    score_opportunity,
                    opportunity,
                    profile
                )
                for opportunity in checked
            ]
        )

    except Exception as exc:

        print(f"Scoring error: {exc}")

        yield {
            "stage": "score",
            "status": "error",
            "message": f"Scoring failed: {exc}"
        }

        yield {
            "stage": "done",
            "status": "error",
            "message": "Pipeline stopped.",
            "data": []
        }

        return

    # ============================================================
    # 6. FILTER EXPIRED / INELIGIBLE BEFORE RANKING
    # ============================================================

    actionable = [
        opportunity
        for opportunity in scored
        if opportunity.get(
            "eligibility",
            {}
        ).get("status")
        not in {"expired", "ineligible"}
    ]

    expired_or_ineligible_count = (
        len(scored) - len(actionable)
    )

    # ============================================================
    # 7. RANK
    # ============================================================

    ranked = sorted(
        actionable,
        key=lambda x: x.get("score", 0),
        reverse=True
    )[:TOP_N]

    yield {
        "stage": "score",
        "status": "done",
        "message": (
            f"Ranked top {len(ranked)} actionable opportunities. "
            f"Excluded {expired_or_ineligible_count} "
            f"expired/ineligible opportunities."
        )
    }

    # ============================================================
    # 8. ACT
    # ============================================================

    yield {
        "stage": "act",
        "status": "running",
        "message": (
            "Preparing application checklists and drafts..."
        )
    }

    try:

        for opportunity in ranked:

            opportunity["checklist"] = (
                await asyncio.to_thread(
                    generate_checklist,
                    opportunity,
                    profile
                )
            )

            opportunity["draft_email"] = (
                await asyncio.to_thread(
                    generate_draft,
                    opportunity,
                    profile
                )
            )

    except Exception as exc:

        print(f"Action generation error: {exc}")

        yield {
            "stage": "act",
            "status": "error",
            "message": (
                f"Application preparation failed: {exc}"
            )
        }

        yield {
            "stage": "done",
            "status": "error",
            "message": "Pipeline stopped.",
            "data": ranked
        }

        return

    yield {
        "stage": "act",
        "status": "done",
        "message": "Application actions are ready."
    }

    # ============================================================
    # 9. DONE
    # ============================================================

    yield {
        "stage": "done",
        "status": "done",
        "message": "Pipeline complete.",
        "data": ranked
    }