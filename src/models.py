"""Typed domain models for the deterministic shortlist pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum


class RecencyBucket(str, Enum):
    """Allowed recency buckets for final opportunity output."""

    DAYS_0_30 = "0–30 days"
    DAYS_31_90 = "31–90 days"
    DAYS_90_PLUS = ">90 days"


class CompanyQualification(str, Enum):
    """Allowed company qualification classes from AGENTS.md."""

    FORTUNE_1000 = "fortune_1000"
    REVENUE_GT_2B = "revenue_gt_2b"
    PE_BACKED_LARGE_SCALE = "pe_backed_large_scale"


@dataclass(frozen=True, slots=True)
class Opportunity:
    """Raw finance transformation opportunity collected from source adapters."""

    company_name: str
    company_qualification: CompanyQualification
    initiative_type: str
    trigger_date: date
    timeline: str
    summary: str
    role_we_could_fill: str
    source_urls: list[str]
    website: str | None = None
    trigger_keywords: set[str] = field(default_factory=set)
    cfo: str = "Unknown"
    cao: str = "Unknown"
    is_us_based: bool = True
    publication_date: date | None = None


@dataclass(frozen=True, slots=True)
class IPOOpportunity:
    """Raw IPO opportunity collected from source adapters."""

    company_name: str
    ipo_signal: str
    date: date
    why_it_matters: str
    role_we_could_fill: str
    source_urls: list[str]
    company_qualification: CompanyQualification
    website: str | None = None
    is_us_based: bool = True


@dataclass(frozen=True, slots=True)
class QualificationDecision:
    """Result of deterministic qualification for a single candidate."""

    is_qualified: bool
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ScoringComponents:
    """Weighted scoring component set (sum max = 100)."""

    trigger_strength: int
    company_qualification_fit: int
    enterprise_scale_strategic_relevance: int
    offering_alignment: int
    recency: int
    source_confidence: int

    @property
    def total(self) -> int:
        return (
            self.trigger_strength
            + self.company_qualification_fit
            + self.enterprise_scale_strategic_relevance
            + self.offering_alignment
            + self.recency
            + self.source_confidence
        )


@dataclass(frozen=True, slots=True)
class ScoredOpportunity:
    """Qualified finance transformation candidate with deterministic score."""

    opportunity: Opportunity
    score: int
    bucket: RecencyBucket
    components: ScoringComponents


@dataclass(frozen=True, slots=True)
class ScoredIPOOpportunity:
    """Qualified IPO candidate with deterministic score."""

    opportunity: IPOOpportunity
    score: int
    components: ScoringComponents


@dataclass(slots=True)
class DigestPayload:
    """Payload consumed by rendering/sending components."""

    top_ipos: list[ScoredIPOOpportunity] = field(default_factory=list)
    top_opportunities: list[ScoredOpportunity] = field(default_factory=list)
