from datetime import date

from src.models import CompanyQualification, IPOOpportunity, Opportunity
from src.selectors import shortlist_ipos, shortlist_opportunities, summarize_selected_finalists


class DummySummarizer:
    def summarize_finance_finalists(self, finalists):
        return [f"finance:{item.opportunity.company_name}" for item in finalists]

    def summarize_ipo_finalists(self, finalists):
        return [f"ipo:{item.opportunity.company_name}" for item in finalists]


def test_shortlist_opportunities_runs_deterministic_pipeline() -> None:
    candidates = [
        Opportunity(
            company_name=f"Company {idx}",
            website="https://example.com",
            company_qualification=CompanyQualification.FORTUNE_1000,
            initiative_type="IPO Readiness",
            trigger_date=date(2026, 4, 1),
            timeline="6 months",
            summary="Large finance transformation trigger.",
            role_we_could_fill="Project Management",
            source_urls=["https://example.com/source"],
            trigger_keywords={"ipo", "readiness", "s-1"},
        )
        for idx in range(15)
    ]

    selected = shortlist_opportunities(candidates, today=date(2026, 4, 14))
    assert len(selected) == 10
    assert all(item.score >= 55 for item in selected)


def test_shortlist_ipos_is_capped() -> None:
    candidates = [
        IPOOpportunity(
            company_name=f"IPO {idx}",
            website="https://example.com",
            ipo_signal="Confidential filing reported",
            date=date(2026, 4, 1),
            why_it_matters="Potential IPO readiness support",
            role_we_could_fill="IPO Readiness",
            source_urls=["https://example.com/source"],
            company_qualification=CompanyQualification.REVENUE_GT_2B,
        )
        for idx in range(8)
    ]

    selected = shortlist_ipos(candidates, today=date(2026, 4, 14))
    assert len(selected) == 5


def test_model_summarization_happens_after_selection() -> None:
    finalists = shortlist_opportunities(
        [
            Opportunity(
                company_name="Finalist Co",
                website="https://example.com",
                company_qualification=CompanyQualification.FORTUNE_1000,
                initiative_type="IPO Readiness",
                trigger_date=date(2026, 4, 1),
                timeline="6 months",
                summary="Large finance transformation trigger.",
                role_we_could_fill="Project Management",
                source_urls=["https://example.com/source"],
                trigger_keywords={"ipo", "readiness", "s-1"},
            )
        ],
        today=date(2026, 4, 14),
    )
    ipo_finalists = shortlist_ipos(
        [
            IPOOpportunity(
                company_name="IPO Finalist",
                website="https://example.com",
                ipo_signal="S-1",
                date=date(2026, 4, 2),
                why_it_matters="Support",
                role_we_could_fill="IPO Readiness",
                source_urls=["https://example.com/source"],
                company_qualification=CompanyQualification.REVENUE_GT_2B,
            )
        ],
        today=date(2026, 4, 14),
    )

    finance_summaries, ipo_summaries = summarize_selected_finalists(
        top_opportunities=finalists,
        top_ipos=ipo_finalists,
        summarizer=DummySummarizer(),
    )

    assert finance_summaries == ["finance:Finalist Co"]
    assert ipo_summaries == ["ipo:IPO Finalist"]
