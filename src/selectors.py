"""Deterministic shortlist selection pipeline helpers."""

from __future__ import annotations

import hashlib
from datetime import date
from typing import Protocol

from .constants import IPO_LIMIT, MINIMUM_WATCHLIST_SCORE, OPPORTUNITY_LIMIT
from .dedupe import dedupe_ipos_by_company, dedupe_opportunities_by_company
from .models import IPOOpportunity, Opportunity, ScoredIPOOpportunity, ScoredOpportunity
from .qualify import filter_qualified_ipos, filter_qualified_opportunities
from .scoring import score_ipo_opportunity, score_opportunity


class FinalistSummarizer(Protocol):
    """Model-facing interface used only after deterministic selection."""

    def summarize_finance_finalists(self, finalists: list[ScoredOpportunity]) -> list[str]:
        ...

    def summarize_ipo_finalists(self, finalists: list[ScoredIPOOpportunity]) -> list[str]:
        ...


def opportunity_signature(candidate: ScoredOpportunity) -> str:
    """Create deterministic signature used for repeat suppression history checks."""

    source = "|".join(sorted(candidate.opportunity.source_urls))
    payload = "::".join(
        [
            candidate.opportunity.company_name.strip().lower(),
            candidate.opportunity.initiative_type.strip().lower(),
            candidate.opportunity.timeline.strip().lower(),
            candidate.opportunity.summary.strip().lower(),
            source,
        ]
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def apply_repeat_suppression(
    candidates: list[ScoredOpportunity],
    *,
    history_by_company: dict[str, dict[str, str]] | None,
    today: date,
    cooldown_days: int = 30,
) -> tuple[list[ScoredOpportunity], list[ScoredOpportunity]]:
    """Suppress unchanged recently-alerted companies based on deterministic history."""

    if not history_by_company:
        return candidates, []

    retained: list[ScoredOpportunity] = []
    suppressed: list[ScoredOpportunity] = []
    for candidate in candidates:
        key = candidate.opportunity.company_name.strip().lower()
        history = history_by_company.get(key)
        if history is None:
            retained.append(candidate)
            continue

        last_alerted_raw = history.get("last_alerted")
        signature = history.get("signature")
        if not last_alerted_raw or not signature:
            retained.append(candidate)
            continue

        candidate_signature = opportunity_signature(candidate)
        # Material update: allow candidate immediately.
        if candidate_signature != signature:
            retained.append(candidate)
            continue

        last_alerted = date.fromisoformat(last_alerted_raw)
        age = (today - last_alerted).days
        if age <= cooldown_days:
            suppressed.append(candidate)
        else:
            retained.append(candidate)

    return retained, suppressed


def shortlist_opportunities(
    raw_candidates: list[Opportunity],
    *,
    today: date,
    history_by_company: dict[str, dict[str, str]] | None = None,
    cooldown_days: int = 30,
) -> list[ScoredOpportunity]:
    """Deterministic pipeline: raw -> qualified -> deduped -> scored -> selected."""

    qualified = filter_qualified_opportunities(raw_candidates)
    deduped = dedupe_opportunities_by_company(qualified)
    scored = [score_opportunity(candidate, today=today) for candidate in deduped]

    filtered = [candidate for candidate in scored if candidate.score >= MINIMUM_WATCHLIST_SCORE]
    filtered, _ = apply_repeat_suppression(
        filtered,
        history_by_company=history_by_company,
        today=today,
        cooldown_days=cooldown_days,
    )

    ranked = sorted(
        filtered,
        key=lambda item: (item.score, item.opportunity.trigger_date, item.opportunity.company_name.lower()),
        reverse=True,
    )
    return ranked[:OPPORTUNITY_LIMIT]


def shortlist_ipos(raw_candidates: list[IPOOpportunity], *, today: date) -> list[ScoredIPOOpportunity]:
    """Deterministic IPO pipeline: raw -> qualified -> deduped -> scored -> selected."""

    qualified = filter_qualified_ipos(raw_candidates)
    deduped = dedupe_ipos_by_company(qualified)
    scored = [score_ipo_opportunity(candidate, today=today) for candidate in deduped]

    ranked = sorted(
        scored,
        key=lambda item: (item.score, item.opportunity.date, item.opportunity.company_name.lower()),
        reverse=True,
    )
    return ranked[:IPO_LIMIT]


def history_updates_from_finalists(
    finalists: list[ScoredOpportunity],
    *,
    today: date,
) -> dict[str, dict[str, str]]:
    """Build deterministic history index entries from sent finalists."""

    updates: dict[str, dict[str, str]] = {}
    for candidate in finalists:
        key = candidate.opportunity.company_name.strip().lower()
        updates[key] = {
            "last_alerted": today.isoformat(),
            "signature": opportunity_signature(candidate),
        }
    return updates


def summarize_selected_finalists(
    *,
    top_opportunities: list[ScoredOpportunity],
    top_ipos: list[ScoredIPOOpportunity],
    summarizer: FinalistSummarizer,
) -> tuple[list[str], list[str]]:
    """Apply model summarization after deterministic selection only."""

    finance_summaries = summarizer.summarize_finance_finalists(top_opportunities)
    ipo_summaries = summarizer.summarize_ipo_finalists(top_ipos)
    return finance_summaries, ipo_summaries
