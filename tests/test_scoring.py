from datetime import date, timedelta

import pytest

from src.models import CompanyQualification, Opportunity
from src.scoring import recency_bucket, score_components, score_opportunity


def _sample_opportunity(days_ago: int) -> Opportunity:
    return Opportunity(
        company_name="Example Corp",
        website="https://example.com",
        company_qualification=CompanyQualification.FORTUNE_1000,
        initiative_type="IPO Readiness",
        trigger_date=date(2026, 4, 14) - timedelta(days=days_ago),
        timeline="6 months",
        summary="IPO readiness program with controllership uplift.",
        role_we_could_fill="IPO Readiness",
        source_urls=["https://example.com/source"],
        trigger_keywords={"ipo", "s-1"},
    )


def test_bucket_assignment_boundaries() -> None:
    today = date(2026, 4, 14)
    assert recency_bucket(today - timedelta(days=30), today).value == "0–30 days"
    assert recency_bucket(today - timedelta(days=31), today).value == "31–90 days"
    assert recency_bucket(today - timedelta(days=91), today).value == ">90 days"


def test_score_opportunity_within_range() -> None:
    scored = score_opportunity(_sample_opportunity(12), today=date(2026, 4, 14))
    assert 0 <= scored.score <= 100


def test_score_components_sum_matches_total() -> None:
    components = score_components(
        trigger_strength=20,
        company_qualification_fit=20,
        enterprise_scale_strategic_relevance=12,
        offering_alignment=18,
        recency=10,
        source_confidence=8,
    )
    assert components.total == 88


def test_score_component_bounds_are_enforced() -> None:
    with pytest.raises(ValueError):
        score_components(
            trigger_strength=26,
            company_qualification_fit=20,
            enterprise_scale_strategic_relevance=15,
            offering_alignment=20,
            recency=10,
            source_confidence=10,
        )
