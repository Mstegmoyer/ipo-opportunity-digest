"""IPO collection pipeline.

Collects raw records from adapters and normalizes into shared IPO models.
"""

from __future__ import annotations

from ..models import IPOOpportunity
from ..sources.ipo_calendar import collect_ipo_calendar
from ..sources.sec_edgar import collect_ipo_signals


def collect_ipos(
    *,
    sec_records: list[dict[str, str]] | None = None,
    calendar_records: list[dict[str, str]] | None = None,
) -> list[IPOOpportunity]:
    """Collect IPO opportunities from multiple sources.

    Primary sources are preferred by ordering SEC records first.
    """

    sec_items = collect_ipo_signals(sec_records)
    calendar_items = collect_ipo_calendar(calendar_records)
    return [*sec_items, *calendar_items]
