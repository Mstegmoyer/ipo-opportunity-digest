"""SEC EDGAR source adapter.

This adapter normalizes SEC filing records into shared project models.
"""

from __future__ import annotations

from datetime import date

from ..models import CompanyQualification, IPOOpportunity, Opportunity

PRIMARY_SOURCE_LABEL = "sec_edgar"


def _parse_qualification(value: str) -> CompanyQualification:
    normalized = value.strip().lower()
    mapping = {
        "fortune_1000": CompanyQualification.FORTUNE_1000,
        "revenue_gt_2b": CompanyQualification.REVENUE_GT_2B,
        "pe_backed_large_scale": CompanyQualification.PE_BACKED_LARGE_SCALE,
    }
    return mapping.get(normalized, CompanyQualification.REVENUE_GT_2B)


def collect_ipo_signals(records: list[dict[str, str]] | None = None) -> list[IPOOpportunity]:
    """Normalize SEC IPO-related filing records into IPO opportunities.

    Expected record keys:
    - company_name, filing_date (YYYY-MM-DD), filing_url, ipo_signal,
      role_we_could_fill, qualification, website, is_us_based
    """

    if not records:
        return []

    normalized: list[IPOOpportunity] = []
    for item in records:
        filing_url = item.get("filing_url", "").strip()
        filing_date = item.get("filing_date", "")
        if not filing_url or not filing_date:
            continue

        normalized.append(
            IPOOpportunity(
                company_name=item.get("company_name", "Unknown Company"),
                website=item.get("website") or None,
                ipo_signal=item.get("ipo_signal", "SEC filing signal"),
                date=date.fromisoformat(filing_date),
                why_it_matters=item.get("why_it_matters", "Potential IPO execution and reporting workstream."),
                role_we_could_fill=item.get("role_we_could_fill", "IPO Readiness"),
                source_urls=[filing_url],
                company_qualification=_parse_qualification(item.get("qualification", "revenue_gt_2b")),
                is_us_based=item.get("is_us_based", "true").lower() == "true",
            )
        )
    return normalized


def collect_finance_signals(records: list[dict[str, str]] | None = None) -> list[Opportunity]:
    """Normalize SEC finance-transformation filing records into opportunities.

    Expected record keys:
    - company_name, filing_date, filing_url, initiative_type, timeline,
      summary, role_we_could_fill, qualification, website, cfo, cao,
      trigger_keywords (comma-separated), is_us_based
    """

    if not records:
        return []

    normalized: list[Opportunity] = []
    for item in records:
        filing_url = item.get("filing_url", "").strip()
        filing_date = item.get("filing_date", "")
        if not filing_url or not filing_date:
            continue

        keywords = {
            token.strip().lower()
            for token in item.get("trigger_keywords", "").split(",")
            if token.strip()
        }

        normalized.append(
            Opportunity(
                company_name=item.get("company_name", "Unknown Company"),
                website=item.get("website") or None,
                company_qualification=_parse_qualification(item.get("qualification", "revenue_gt_2b")),
                initiative_type=item.get("initiative_type", "Capital Markets"),
                trigger_date=date.fromisoformat(filing_date),
                publication_date=date.fromisoformat(filing_date),
                timeline=item.get("timeline", "TBD"),
                summary=item.get("summary", "SEC filing indicates strategic finance transformation trigger."),
                role_we_could_fill=item.get("role_we_could_fill", "SEC & Regulatory Reporting"),
                source_urls=[filing_url],
                trigger_keywords=keywords,
                cfo=item.get("cfo", "Unknown"),
                cao=item.get("cao", "Unknown"),
                is_us_based=item.get("is_us_based", "true").lower() == "true",
            )
        )
    return normalized
