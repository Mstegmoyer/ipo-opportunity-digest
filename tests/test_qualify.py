from datetime import date

from src.models import CompanyQualification, Opportunity
from src.qualify import qualify_opportunity


def _candidate(*, is_us_based: bool = True, initiative_type: str = "IPO Readiness") -> Opportunity:
    return Opportunity(
        company_name="Alpha Inc",
        website="https://example.com",
        company_qualification=CompanyQualification.REVENUE_GT_2B,
        initiative_type=initiative_type,
        trigger_date=date(2026, 4, 1),
        timeline="12 months",
        summary="Finance systems modernization with reporting redesign.",
        role_we_could_fill="System Implementation",
        source_urls=["https://example.com/source"],
        is_us_based=is_us_based,
    )


def test_qualify_opportunity_accepts_valid_candidate() -> None:
    decision = qualify_opportunity(_candidate())
    assert decision.is_qualified is True
    assert decision.reasons == ()


def test_qualify_opportunity_rejects_non_us_candidate() -> None:
    decision = qualify_opportunity(_candidate(is_us_based=False))
    assert decision.is_qualified is False
    assert "company_not_us_based" in decision.reasons


def test_qualify_opportunity_rejects_non_priority_initiative() -> None:
    decision = qualify_opportunity(_candidate(initiative_type="Routine Audit"))
    assert decision.is_qualified is False
    assert "initiative_not_priority" in decision.reasons
