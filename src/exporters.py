"""CSV/JSON exporters for digest outputs."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict
from enum import Enum
from pathlib import Path
from typing import Any

from .models import DigestPayload, ScoredOpportunity


def _to_jsonable(value: Any) -> Any:
    """Convert nested dataclass output to stable JSON-serializable primitives."""

    if isinstance(value, dict):
        return {key: _to_jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, set):
        return sorted(_to_jsonable(item) for item in value)
    if isinstance(value, Enum):
        return value.value
    return value


def export_digest_json(payload: DigestPayload, output_path: Path) -> None:
    """Export digest payload as JSON."""

    serializable = {
        "top_ipos": [_to_jsonable(asdict(item)) for item in payload.top_ipos],
        "top_opportunities": [_to_jsonable(asdict(item)) for item in payload.top_opportunities],
    }
    output_path.write_text(json.dumps(serializable, indent=2, default=str), encoding="utf-8")


def export_digest_csv(
    *,
    payload: DigestPayload,
    watchlist: list[ScoredOpportunity],
    output_path: Path,
) -> None:
    """Export IPO, top opportunities, and watchlist rows to CSV.

    Preserves source URL and source date in every row.
    """

    fieldnames = [
        "section",
        "bucket",
        "company_name",
        "website",
        "cfo",
        "cao",
        "initiative_type_or_signal",
        "timeline_or_date",
        "source_date",
        "summary_or_why_it_matters",
        "role_we_could_fill",
        "source",
        "score",
    ]

    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()

        for item in payload.top_ipos:
            writer.writerow(
                {
                    "section": "ipo",
                    "bucket": "",
                    "company_name": item.opportunity.company_name,
                    "website": item.opportunity.website or "",
                    "cfo": "",
                    "cao": "",
                    "initiative_type_or_signal": item.opportunity.ipo_signal,
                    "timeline_or_date": item.opportunity.date.isoformat(),
                    "source_date": item.opportunity.date.isoformat(),
                    "summary_or_why_it_matters": item.opportunity.why_it_matters,
                    "role_we_could_fill": item.opportunity.role_we_could_fill,
                    "source": "; ".join(item.opportunity.source_urls),
                    "score": item.score,
                }
            )

        for section, items in (("top10", payload.top_opportunities), ("watchlist", watchlist)):
            for item in items:
                source_date = (item.opportunity.publication_date or item.opportunity.trigger_date).isoformat()
                writer.writerow(
                    {
                        "section": section,
                        "bucket": item.bucket.value,
                        "company_name": item.opportunity.company_name,
                        "website": item.opportunity.website or "",
                        "cfo": item.opportunity.cfo,
                        "cao": item.opportunity.cao,
                        "initiative_type_or_signal": item.opportunity.initiative_type,
                        "timeline_or_date": item.opportunity.timeline,
                        "source_date": source_date,
                        "summary_or_why_it_matters": item.opportunity.summary,
                        "role_we_could_fill": item.opportunity.role_we_could_fill,
                        "source": "; ".join(item.opportunity.source_urls),
                        "score": item.score,
                    }
                )
