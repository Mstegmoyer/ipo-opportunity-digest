"""Deterministic qualification filters for raw candidates."""

from __future__ import annotations

from collections.abc import Iterable

from .constants import ALLOWED_COMPANY_TYPES, PRIORITY_INITIATIVE_TYPES
from .models import IPOOpportunity, Opportunity, QualificationDecision


def _has_source_urls(source_urls: list[str]) -> bool:
    return any(url.strip() for url in source_urls)


def qualify_opportunity(candidate: Opportunity) -> QualificationDecision:
    """Apply deterministic, code-based qualification rules."""

    reasons: list[str] = []

    if not candidate.is_us_based:
        reasons.append("company_not_us_based")

    if candidate.company_qualification.value not in ALLOWED_COMPANY_TYPES:
        reasons.append("company_out_of_scope")

    if candidate.initiative_type not in PRIORITY_INITIATIVE_TYPES:
        reasons.append("initiative_not_priority")

    if not _has_source_urls(candidate.source_urls):
        reasons.append("missing_source_url")

    return QualificationDecision(is_qualified=not reasons, reasons=tuple(reasons))


def qualify_ipo_opportunity(candidate: IPOOpportunity) -> QualificationDecision:
    """Apply deterministic qualification rules to raw IPO candidates."""

    reasons: list[str] = []

    if not candidate.is_us_based:
        reasons.append("company_not_us_based")

    if candidate.company_qualification.value not in ALLOWED_COMPANY_TYPES:
        reasons.append("company_out_of_scope")

    if not _has_source_urls(candidate.source_urls):
        reasons.append("missing_source_url")

    return QualificationDecision(is_qualified=not reasons, reasons=tuple(reasons))


def filter_qualified_opportunities(candidates: Iterable[Opportunity]) -> list[Opportunity]:
    """Return only qualified finance transformation opportunities."""

    qualified: list[Opportunity] = []
    for candidate in candidates:
        if qualify_opportunity(candidate).is_qualified:
            qualified.append(candidate)
    return qualified


def filter_qualified_ipos(candidates: Iterable[IPOOpportunity]) -> list[IPOOpportunity]:
    """Return only qualified IPO opportunities."""

    qualified: list[IPOOpportunity] = []
    for candidate in candidates:
        if qualify_ipo_opportunity(candidate).is_qualified:
            qualified.append(candidate)
    return qualified
