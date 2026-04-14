"""IPO calendar source adapter.

This adapter is a secondary source; SEC filings remain primary when available.
"""

from __future__ import annotations

from datetime import date

from ..models import CompanyQualification, IPOOpportunity

SECONDARY_SOURCE_LABEL = "ipo_calendar"


def collect_ipo_calendar(records: list[dict[str, str]] | None = None) -> list[IPOOpportunity]:
    """Normalize IPO calendar entries into IPO opportunities.

    Expected record keys:
    - company_name, source_date (YYYY-MM-DD), source_url, signal,
      qualification, website
    """

    if not records:
        return []

    normalized: list[IPOOpportunity] = []
    for item in records:
        source_url = item.get("source_url", "").strip()
        source_date = item.get("source_date", "")
        if not source_url or not source_date:
            continue

        normalized.append(
            IPOOpportunity(
                company_name=item.get("company_name", "Unknown Company"),
                website=item.get("website") or None,
                ipo_signal=item.get("signal", "IPO calendar listing"),
                date=date.fromisoformat(source_date),
                why_it_matters=item.get("why_it_matters", "Upcoming IPO timeline may require readiness support."),
                role_we_could_fill=item.get("role_we_could_fill", "IPO Readiness"),
                source_urls=[source_url],
                company_qualification=CompanyQualification(item.get("qualification", "revenue_gt_2b")),
                is_us_based=item.get("is_us_based", "true").lower() == "true",
            )
        )
    return normalized
