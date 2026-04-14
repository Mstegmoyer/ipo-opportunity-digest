from datetime import date

from src.models import CompanyQualification, Opportunity
from src.qualify import qualify_opportunity
from src.sources.business_news import collect_business_news_opportunities


def _candidate(*, is_us_based: bool = True, initiative_type: str = "IPO Readiness", source_urls: list[str] | None = None) -> Opportunity:
    return Opportunity(
        company_name="Alpha Inc",
        website="https://example.com",
        company_qualification=CompanyQualification.REVENUE_GT_2B,
        initiative_type=initiative_type,
        trigger_date=date(2026, 4, 1),
        timeline="12 months",
        summary="Finance systems modernization with reporting redesign.",
        role_we_could_fill="System Implementation",
        source_urls=source_urls or ["https://example.com/source"],
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


def test_qualify_opportunity_rejects_missing_source_url() -> None:
    decision = qualify_opportunity(_candidate(source_urls=[""]))
    assert decision.is_qualified is False
    assert "missing_source_url" in decision.reasons


def test_fixture_records_include_valid_and_excluded_opportunities(sample_opportunities_records) -> None:
    valid_items = collect_business_news_opportunities(sample_opportunities_records["business_news_records"])
    assert valid_items
    assert qualify_opportunity(valid_items[0]).is_qualified is True

    excluded_item = Opportunity(
        company_name="Excluded Co",
        company_qualification=CompanyQualification.REVENUE_GT_2B,
        initiative_type="Routine Audit",
        trigger_date=date(2026, 4, 1),
        timeline="TBD",
        summary="Not strategic.",
        role_we_could_fill="Process Improvement",
        source_urls=["https://example.com/excluded"],
    )
    assert qualify_opportunity(excluded_item).is_qualified is False
