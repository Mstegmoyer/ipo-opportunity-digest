"""Deterministic deduplication helpers."""

from __future__ import annotations

from collections.abc import Iterable

from .models import IPOOpportunity, Opportunity


def dedupe_opportunities_by_company(candidates: Iterable[Opportunity]) -> list[Opportunity]:
    """Deduplicate by normalized company name and keep most recent trigger."""

    latest_by_company: dict[str, Opportunity] = {}
    for candidate in candidates:
        key = candidate.company_name.strip().lower()
        current = latest_by_company.get(key)
        if current is None or candidate.trigger_date > current.trigger_date:
            latest_by_company[key] = candidate
    return list(latest_by_company.values())


def dedupe_ipos_by_company(candidates: Iterable[IPOOpportunity]) -> list[IPOOpportunity]:
    """Deduplicate IPO candidates by normalized company name and keep newest signal date."""

    latest_by_company: dict[str, IPOOpportunity] = {}
    for candidate in candidates:
        key = candidate.company_name.strip().lower()
        current = latest_by_company.get(key)
        if current is None or candidate.date > current.date:
            latest_by_company[key] = candidate
    return list(latest_by_company.values())
