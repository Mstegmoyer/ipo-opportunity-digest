"""End-to-end weekly digest orchestration."""

from __future__ import annotations

from datetime import date

from ..models import DigestPayload
from ..rendering import render_weekly_digest
from .collect_ipos import collect_ipos
from .collect_opportunities import collect_opportunities
from .score_and_select import score_and_select


def build_digest(
    *,
    run_date: date,
    sec_ipo_records: list[dict[str, str]] | None = None,
    ipo_calendar_records: list[dict[str, str]] | None = None,
    sec_opportunity_records: list[dict[str, str]] | None = None,
    press_release_records: list[dict[str, str]] | None = None,
    business_news_records: list[dict[str, str]] | None = None,
    history_by_company: dict[str, dict[str, str]] | None = None,
) -> tuple[DigestPayload, str]:
    """Build digest payload and rendered HTML from normalized source inputs."""

    raw_ipos = collect_ipos(sec_records=sec_ipo_records, calendar_records=ipo_calendar_records)
    raw_opportunities = collect_opportunities(
        sec_records=sec_opportunity_records,
        press_release_records=press_release_records,
        business_news_records=business_news_records,
    )

    top_ipos, top_opportunities = score_and_select(
        raw_ipos=raw_ipos,
        raw_opportunities=raw_opportunities,
        today=run_date,
        history_by_company=history_by_company,
    )

    payload = DigestPayload(top_ipos=top_ipos, top_opportunities=top_opportunities)
    html = render_weekly_digest(payload)
    return payload, html
