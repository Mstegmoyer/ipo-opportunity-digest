"""Deterministic weighted scoring utilities."""

from __future__ import annotations

from datetime import date

from .constants import PRIORITY_INITIATIVE_TYPES, SCORING_WEIGHTS
from .models import IPOOpportunity, Opportunity, RecencyBucket, ScoredIPOOpportunity, ScoredOpportunity, ScoringComponents


def recency_bucket(event_date: date, today: date) -> RecencyBucket:
    """Map event date to AGENTS recency buckets."""

    delta_days = max((today - event_date).days, 0)
    if delta_days <= 30:
        return RecencyBucket.DAYS_0_30
    if delta_days <= 90:
        return RecencyBucket.DAYS_31_90
    return RecencyBucket.DAYS_90_PLUS


def _bounded(value: int, minimum: int, maximum: int, field_name: str) -> int:
    if not minimum <= value <= maximum:
        raise ValueError(f"{field_name} must be between {minimum} and {maximum}.")
    return value


def score_components(
    *,
    trigger_strength: int,
    company_qualification_fit: int,
    enterprise_scale_strategic_relevance: int,
    offering_alignment: int,
    recency: int,
    source_confidence: int,
) -> ScoringComponents:
    """Build and validate scoring components against deterministic limits."""

    components = ScoringComponents(
        trigger_strength=_bounded(trigger_strength, 0, 25, "trigger_strength"),
        company_qualification_fit=_bounded(company_qualification_fit, 0, 20, "company_qualification_fit"),
        enterprise_scale_strategic_relevance=_bounded(
            enterprise_scale_strategic_relevance,
            0,
            15,
            "enterprise_scale_strategic_relevance",
        ),
        offering_alignment=_bounded(offering_alignment, 0, 20, "offering_alignment"),
        recency=_bounded(recency, 0, 10, "recency"),
        source_confidence=_bounded(source_confidence, 0, 10, "source_confidence"),
    )
    if components.total > sum(SCORING_WEIGHTS.values()):
        raise ValueError("Total score components exceed max weighted score.")
    return components


def _recency_score(bucket: RecencyBucket) -> int:
    if bucket == RecencyBucket.DAYS_0_30:
        return 10
    if bucket == RecencyBucket.DAYS_31_90:
        return 6
    return 2


def _offering_alignment_score(initiative_type: str, role_we_could_fill: str) -> int:
    alignment = 12
    if initiative_type in PRIORITY_INITIATIVE_TYPES:
        alignment += 5
    if role_we_could_fill.strip():
        alignment += 3
    return min(alignment, 20)


def score_opportunity(opportunity: Opportunity, *, today: date) -> ScoredOpportunity:
    """Score qualified finance transformation opportunity deterministically."""

    bucket = recency_bucket(opportunity.trigger_date, today)
    components = score_components(
        trigger_strength=min(25, 8 + len(opportunity.trigger_keywords) * 4),
        company_qualification_fit=20,
        enterprise_scale_strategic_relevance=12,
        offering_alignment=_offering_alignment_score(opportunity.initiative_type, opportunity.role_we_could_fill),
        recency=_recency_score(bucket),
        source_confidence=10 if len(opportunity.source_urls) >= 2 else 8,
    )

    return ScoredOpportunity(opportunity=opportunity, score=components.total, bucket=bucket, components=components)


def score_ipo_opportunity(opportunity: IPOOpportunity, *, today: date) -> ScoredIPOOpportunity:
    """Score qualified IPO opportunity deterministically."""

    bucket = recency_bucket(opportunity.date, today)
    components = score_components(
        trigger_strength=22,
        company_qualification_fit=20,
        enterprise_scale_strategic_relevance=13,
        offering_alignment=20,
        recency=_recency_score(bucket),
        source_confidence=10 if len(opportunity.source_urls) >= 2 else 8,
    )
    return ScoredIPOOpportunity(opportunity=opportunity, score=components.total, components=components)
