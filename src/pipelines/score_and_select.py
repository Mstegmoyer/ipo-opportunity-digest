"""Deterministic score + select pipeline."""

from __future__ import annotations

from datetime import date

from ..models import IPOOpportunity, Opportunity, ScoredIPOOpportunity, ScoredOpportunity
from ..selectors import shortlist_ipos, shortlist_opportunities


def score_and_select(
    *,
    raw_ipos: list[IPOOpportunity],
    raw_opportunities: list[Opportunity],
    today: date,
) -> tuple[list[ScoredIPOOpportunity], list[ScoredOpportunity]]:
    """Deterministically score and select finalists."""

    top_ipos = shortlist_ipos(raw_ipos, today=today)
    top_opportunities = shortlist_opportunities(raw_opportunities, today=today)
    return top_ipos, top_opportunities
