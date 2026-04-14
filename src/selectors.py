"""Deterministic shortlist selection pipeline helpers."""

from __future__ import annotations

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


def shortlist_opportunities(raw_candidates: list[Opportunity], *, today: date) -> list[ScoredOpportunity]:
    """Deterministic pipeline: raw -> qualified -> deduped -> scored -> selected."""

    qualified = filter_qualified_opportunities(raw_candidates)
    deduped = dedupe_opportunities_by_company(qualified)
    scored = [score_opportunity(candidate, today=today) for candidate in deduped]

    ranked = sorted(
        (candidate for candidate in scored if candidate.score >= MINIMUM_WATCHLIST_SCORE),
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
