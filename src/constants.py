"""Project constants and deterministic scoring weights."""

from __future__ import annotations

from typing import Final

RECENCY_BUCKETS: Final[tuple[str, str, str]] = ("0–30 days", "31–90 days", ">90 days")

IPO_LIMIT: Final[int] = 5
OPPORTUNITY_LIMIT: Final[int] = 10

SCORING_WEIGHTS: Final[dict[str, int]] = {
    "trigger_strength": 25,
    "company_qualification_fit": 20,
    "enterprise_scale_strategic_relevance": 15,
    "offering_alignment": 20,
    "recency": 10,
    "source_confidence": 10,
}

MINIMUM_WATCHLIST_SCORE: Final[int] = 55

ALLOWED_COMPANY_TYPES: Final[tuple[str, ...]] = (
    "fortune_1000",
    "revenue_gt_2b",
    "pe_backed_large_scale",
)

PRIORITY_INITIATIVE_TYPES: Final[tuple[str, ...]] = (
    "IPO Readiness",
    "M&A / Integration",
    "ERP / EPM Transformation",
    "Restructuring",
    "Process Enhancement",
    "Capital Markets",
    "Material Weakness / Restatement",
    "Regulatory / ESG Modernization",
    "Strategic Capex",
    "Advisory RFP",
)

DEFAULT_UNKNOWN_LABEL: Final[str] = "Unknown"
