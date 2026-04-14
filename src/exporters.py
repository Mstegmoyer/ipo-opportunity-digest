"""CSV/JSON exporters for digest outputs."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path

from .models import DigestPayload, ScoredOpportunity


def export_digest_json(payload: DigestPayload, output_path: Path) -> None:
    """Export digest payload as JSON."""

    serializable = {
        "top_ipos": [asdict(item) for item in payload.top_ipos],
        "top_opportunities": [asdict(item) for item in payload.top_opportunities],
    }
    output_path.write_text(json.dumps(serializable, indent=2, default=str), encoding="utf-8")


def export_opportunities_csv(
    *,
    top_opportunities: list[ScoredOpportunity],
    watchlist: list[ScoredOpportunity],
    output_path: Path,
) -> None:
    """Export top opportunities and watchlist rows to CSV."""

    fieldnames = [
        "section",
        "bucket",
        "company_name",
        "website",
        "cfo",
        "cao",
        "initiative_type",
        "timeline",
        "summary",
        "role_we_could_fill",
        "source",
        "score",
    ]

    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()

        for section, items in (("top10", top_opportunities), ("watchlist", watchlist)):
            for item in items:
                writer.writerow(
                    {
                        "section": section,
                        "bucket": item.bucket.value,
                        "company_name": item.opportunity.company_name,
                        "website": item.opportunity.website or "",
                        "cfo": item.opportunity.cfo,
                        "cao": item.opportunity.cao,
                        "initiative_type": item.opportunity.initiative_type,
                        "timeline": item.opportunity.timeline,
                        "summary": item.opportunity.summary,
                        "role_we_could_fill": item.opportunity.role_we_could_fill,
                        "source": "; ".join(item.opportunity.source_urls),
                        "score": item.score,
                    }
                )
