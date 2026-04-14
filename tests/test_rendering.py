from datetime import date

from src.models import (
    CompanyQualification,
    DigestPayload,
    IPOOpportunity,
    Opportunity,
)
from src.scoring import score_ipo_opportunity, score_opportunity
from src.render_html import render_weekly_digest_html


def test_render_weekly_digest_outputs_required_sections() -> None:
    today = date(2026, 4, 14)
    payload = DigestPayload(
        top_ipos=[
            score_ipo_opportunity(
                IPOOpportunity(
                    company_name="IPO Co",
                    website="https://example.com",
                    ipo_signal="S-1 filing",
                    date=today,
                    why_it_matters="Large-cap IPO candidate",
                    role_we_could_fill="IPO Readiness",
                    source_urls=["https://example.com/source"],
                    company_qualification=CompanyQualification.FORTUNE_1000,
                ),
                today=today,
            )
        ],
        top_opportunities=[
            score_opportunity(
                Opportunity(
                    company_name="Transform Co",
                    website="https://example.com",
                    company_qualification=CompanyQualification.REVENUE_GT_2B,
                    initiative_type="ERP / EPM Transformation",
                    trigger_date=today,
                    timeline="9 months",
                    summary="Finance transformation program announced.",
                    role_we_could_fill="System Implementation",
                    source_urls=["https://example.com/source"],
                    trigger_keywords={"erp", "finance"},
                ),
                today=today,
            )
        ],
    )

    rendered = render_weekly_digest_html(payload)
    assert "Executive Summary" in rendered
    assert "Top 5 U.S. IPOs this week" in rendered
    assert "Top 10 U.S. opportunities" in rendered
    assert "Watchlist / near misses" in rendered
    assert "Methodology" in rendered
