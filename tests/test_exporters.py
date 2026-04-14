from __future__ import annotations

import csv
import json
from datetime import date
from pathlib import Path

from src.exporters import export_digest_csv, export_digest_json
from src.models import CompanyQualification, DigestPayload, IPOOpportunity, Opportunity
from src.scoring import score_ipo_opportunity, score_opportunity


def _payload() -> DigestPayload:
    today = date(2026, 4, 14)
    return DigestPayload(
        top_ipos=[
            score_ipo_opportunity(
                IPOOpportunity(
                    company_name="IPO Co",
                    website="https://example.com",
                    ipo_signal="S-1",
                    date=today,
                    why_it_matters="Signal",
                    role_we_could_fill="IPO Readiness",
                    source_urls=["https://example.com/ipo"],
                    company_qualification=CompanyQualification.FORTUNE_1000,
                ),
                today=today,
            )
        ],
        top_opportunities=[
            score_opportunity(
                Opportunity(
                    company_name="Transform Co",
                    website="https://example.com",
                    company_qualification=CompanyQualification.REVENUE_GT_2B,
                    initiative_type="ERP / EPM Transformation",
                    trigger_date=today,
                    publication_date=today,
                    timeline="9 months",
                    summary="Summary",
                    role_we_could_fill="System Implementation",
                    source_urls=["https://example.com/opp"],
                    trigger_keywords={"erp"},
                ),
                today=today,
            )
        ],
    )


def test_export_digest_csv_includes_source_and_source_date(tmp_path: Path) -> None:
    payload = _payload()
    output_path = tmp_path / "digest.csv"
    export_digest_csv(payload=payload, watchlist=[], output_path=output_path)

    with output_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert rows
    assert all(row["source"] for row in rows)
    assert all(row["source_date"] for row in rows)


def test_export_digest_json_preserves_source_and_dates(tmp_path: Path) -> None:
    payload = _payload()
    output_path = tmp_path / "digest.json"
    export_digest_json(payload, output_path)

    parsed = json.loads(output_path.read_text(encoding="utf-8"))
    assert parsed["top_ipos"][0]["opportunity"]["source_urls"][0] == "https://example.com/ipo"
    assert parsed["top_ipos"][0]["opportunity"]["date"] == "2026-04-14"
    assert parsed["top_opportunities"][0]["opportunity"]["publication_date"] == "2026-04-14"
