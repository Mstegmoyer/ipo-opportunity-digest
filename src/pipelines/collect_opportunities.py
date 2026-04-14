"""Finance opportunity collection pipeline.

Collects raw records from modular adapters and normalizes into shared models.
"""

from __future__ import annotations

from ..models import Opportunity
from ..sources.business_news import collect_business_news_opportunities
from ..sources.press_releases import collect_press_release_opportunities
from ..sources.sec_edgar import collect_finance_signals


def collect_opportunities(
    *,
    sec_records: list[dict[str, str]] | None = None,
    press_release_records: list[dict[str, str]] | None = None,
    business_news_records: list[dict[str, str]] | None = None,
) -> list[Opportunity]:
    """Collect finance opportunities from multiple sources.

    Primary sources are preferred by ordering SEC filings first,
    then press releases, then secondary business news.
    """

    sec_items = collect_finance_signals(sec_records)
    press_items = collect_press_release_opportunities(press_release_records)
    news_items = collect_business_news_opportunities(business_news_records)
    return [*sec_items, *press_items, *news_items]
