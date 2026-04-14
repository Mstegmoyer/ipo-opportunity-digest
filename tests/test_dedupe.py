from datetime import date

from src.dedupe import dedupe_ipos_by_company, dedupe_opportunities_by_company
from src.models import CompanyQualification, IPOOpportunity, Opportunity


def test_dedupe_opportunities_keeps_latest_trigger_date() -> None:
    older = Opportunity(
        company_name="Acme Corp",
        company_qualification=CompanyQualification.FORTUNE_1000,
        initiative_type="IPO Readiness",
        trigger_date=date(2026, 3, 1),
        timeline="Q3",
        summary="Older trigger",
        role_we_could_fill="IPO Readiness",
        source_urls=["https://example.com/1"],
    )
    newer = Opportunity(
        company_name="acme corp",
        company_qualification=CompanyQualification.FORTUNE_1000,
        initiative_type="IPO Readiness",
        trigger_date=date(2026, 4, 1),
        timeline="Q4",
        summary="Newer trigger",
        role_we_could_fill="IPO Readiness",
        source_urls=["https://example.com/2"],
    )

    deduped = dedupe_opportunities_by_company([older, newer])
    assert len(deduped) == 1
    assert deduped[0].trigger_date == date(2026, 4, 1)


def test_dedupe_ipos_keeps_latest_signal_date() -> None:
    older = IPOOpportunity(
        company_name="Nova IPO",
        ipo_signal="Rumor",
        date=date(2026, 2, 1),
        why_it_matters="Older",
        role_we_could_fill="IPO Readiness",
        source_urls=["https://example.com/1"],
        company_qualification=CompanyQualification.REVENUE_GT_2B,
    )
    newer = IPOOpportunity(
        company_name="nova ipo",
        ipo_signal="S-1 filing",
        date=date(2026, 4, 1),
        why_it_matters="Newer",
        role_we_could_fill="IPO Readiness",
        source_urls=["https://example.com/2"],
        company_qualification=CompanyQualification.REVENUE_GT_2B,
    )

    deduped = dedupe_ipos_by_company([older, newer])
    assert len(deduped) == 1
    assert deduped[0].date == date(2026, 4, 1)
