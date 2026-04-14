"""Press release source adapter for strategic finance opportunities."""

from __future__ import annotations

from datetime import date

from ..models import CompanyQualification, Opportunity


def _qualification(value: str) -> CompanyQualification:
    try:
        return CompanyQualification(value)
    except ValueError:
        return CompanyQualification.REVENUE_GT_2B


def collect_press_release_opportunities(records: list[dict[str, str]] | None = None) -> list[Opportunity]:
    """Normalize press release items into finance opportunities.

    Expected record keys:
    - company_name, source_date (YYYY-MM-DD), source_url, initiative_type,
      timeline, summary, role_we_could_fill, qualification, cfo, cao,
      trigger_keywords
    """

    if not records:
        return []

    normalized: list[Opportunity] = []
    for item in records:
        source_url = item.get("source_url", "").strip()
        source_date = item.get("source_date", "")
        if not source_url or not source_date:
            continue

        normalized.append(
            Opportunity(
                company_name=item.get("company_name", "Unknown Company"),
                website=item.get("website") or None,
                company_qualification=_qualification(item.get("qualification", "revenue_gt_2b")),
                initiative_type=item.get("initiative_type", "Process Enhancement"),
                trigger_date=date.fromisoformat(source_date),
                publication_date=date.fromisoformat(source_date),
                timeline=item.get("timeline", "TBD"),
                summary=item.get("summary", "Press release suggests strategic finance transformation opportunity."),
                role_we_could_fill=item.get("role_we_could_fill", "Process Improvement"),
                source_urls=[source_url],
                trigger_keywords={
                    keyword.strip().lower()
                    for keyword in item.get("trigger_keywords", "").split(",")
                    if keyword.strip()
                },
                cfo=item.get("cfo", "Unknown"),
                cao=item.get("cao", "Unknown"),
                is_us_based=item.get("is_us_based", "true").lower() == "true",
            )
        )
    return normalized
