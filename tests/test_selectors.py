from datetime import date

from src.models import CompanyQualification, IPOOpportunity, Opportunity
from src.selectors import (
    apply_repeat_suppression,
    history_updates_from_finalists,
    opportunity_signature,
    shortlist_ipos,
    shortlist_opportunities,
    summarize_selected_finalists,
)


class DummySummarizer:
    def summarize_finance_finalists(self, finalists):
        return [f"finance:{item.opportunity.company_name}" for item in finalists]

    def summarize_ipo_finalists(self, finalists):
        return [f"ipo:{item.opportunity.company_name}" for item in finalists]


def _opp(name: str, trigger_date: date, summary: str = "Large finance transformation trigger.") -> Opportunity:
    return Opportunity(
        company_name=name,
        website="https://example.com",
        company_qualification=CompanyQualification.FORTUNE_1000,
        initiative_type="IPO Readiness",
        trigger_date=trigger_date,
        timeline="6 months",
        summary=summary,
        role_we_could_fill="Project Management",
        source_urls=["https://example.com/source"],
        trigger_keywords={"ipo", "readiness", "s-1"},
    )


def test_top_10_selected_in_code_from_scored_candidates() -> None:
    candidates = [_opp(f"Company {idx}", date(2026, 4, 1)) for idx in range(15)]
    selected = shortlist_opportunities(candidates, today=date(2026, 4, 14))
    assert len(selected) == 10
    assert all(item.score >= 55 for item in selected)


def test_top_5_ipos_selected_in_code_from_scored_candidates() -> None:
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
        for idx in range(9)
    ]
    selected = shortlist_ipos(candidates, today=date(2026, 4, 14))
    assert len(selected) == 5


def test_repeat_suppression_history_handling() -> None:
    selected = shortlist_opportunities(
        [_opp("Repeat Co", date(2026, 4, 1)), _opp("Fresh Co", date(2026, 4, 1))],
        today=date(2026, 4, 14),
        history_by_company={
            "repeat co": {
                "last_alerted": "2026-04-10",
                "signature": opportunity_signature(shortlist_opportunities([_opp("Repeat Co", date(2026, 4, 1))], today=date(2026, 4, 14))[0]),
            }
        },
        cooldown_days=30,
    )
    names = {item.opportunity.company_name for item in selected}
    assert "Repeat Co" not in names
    assert "Fresh Co" in names


def test_materially_updated_repeat_can_reappear() -> None:
    baseline = shortlist_opportunities([_opp("Repeat Co", date(2026, 4, 1), summary="Original summary")], today=date(2026, 4, 14))[0]
    updated = shortlist_opportunities(
        [_opp("Repeat Co", date(2026, 4, 1), summary="Materially updated summary with new trigger")],
        today=date(2026, 4, 14),
        history_by_company={
            "repeat co": {
                "last_alerted": "2026-04-10",
                "signature": opportunity_signature(baseline),
            }
        },
        cooldown_days=30,
    )
    assert len(updated) == 1


def test_history_updates_are_deterministic() -> None:
    finalists = shortlist_opportunities([_opp("Stable Co", date(2026, 4, 1))], today=date(2026, 4, 14))
    a = history_updates_from_finalists(finalists, today=date(2026, 4, 14))
    b = history_updates_from_finalists(finalists, today=date(2026, 4, 14))
    assert a == b


def test_model_summarization_happens_after_selection_only() -> None:
    finalists = shortlist_opportunities([_opp("Finalist Co", date(2026, 4, 1))], today=date(2026, 4, 14))
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
