"""CLI entrypoint for weekly digest orchestration."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from .exporters import export_digest_json, export_opportunities_csv
from .pipelines.build_digest import build_digest
from .scoring import score_opportunity
from .sources.business_news import collect_business_news_opportunities


def _sample_inputs() -> dict[str, list[dict[str, str]]]:
    """Return deterministic sample source inputs for dry-run/test-mode."""

    return {
        "sec_ipo_records": [
            {
                "company_name": "Atlas Robotics",
                "filing_date": "2026-04-10",
                "filing_url": "https://www.sec.gov/ixviewer/atlas-s1",
                "ipo_signal": "S-1 filed",
                "why_it_matters": "Large-scale IPO readiness effort likely underway.",
                "role_we_could_fill": "IPO Readiness",
                "qualification": "revenue_gt_2b",
                "website": "https://atlas.example.com",
                "is_us_based": "true",
            }
        ],
        "ipo_calendar_records": [
            {
                "company_name": "Northwind Data",
                "source_date": "2026-04-08",
                "source_url": "https://example.com/ipo-calendar/northwind",
                "signal": "Targeting NYSE listing window",
                "why_it_matters": "Creates near-term finance transformation demand.",
                "role_we_could_fill": "SEC & Regulatory Reporting",
                "qualification": "fortune_1000",
                "website": "https://northwind.example.com",
                "is_us_based": "true",
            }
        ],
        "sec_opportunity_records": [
            {
                "company_name": "Apex Manufacturing",
                "filing_date": "2026-04-09",
                "filing_url": "https://www.sec.gov/ixviewer/apex-8k",
                "initiative_type": "Material Weakness / Restatement",
                "timeline": "2 quarters",
                "summary": "Disclosed internal control remediation with expanded transformation scope.",
                "role_we_could_fill": "SOX / Internal Audit / Controls",
                "qualification": "fortune_1000",
                "website": "https://apex.example.com",
                "cfo": "Jordan Lee",
                "cao": "Morgan Diaz",
                "trigger_keywords": "material weakness,restatement,controls",
                "is_us_based": "true",
            }
        ],
        "press_release_records": [
            {
                "company_name": "Helios Energy",
                "source_date": "2026-04-06",
                "source_url": "https://investor.helios.example.com/news/erp-program",
                "initiative_type": "ERP / EPM Transformation",
                "timeline": "18 months",
                "summary": "Announced enterprise ERP transformation and close modernization.",
                "role_we_could_fill": "System Implementation",
                "qualification": "revenue_gt_2b",
                "website": "https://helios.example.com",
                "cfo": "Casey Smith",
                "cao": "Unknown",
                "trigger_keywords": "erp,close,transformation",
                "is_us_based": "true",
            }
        ],
        "business_news_records": [
            {
                "company_name": "BlueRiver Health",
                "source_date": "2026-04-04",
                "source_url": "https://news.example.com/blueriver-carveout",
                "initiative_type": "M&A / Integration",
                "timeline": "9 months",
                "summary": "Divestiture and carve-out program announced with finance separation work.",
                "role_we_could_fill": "Divestitures / Carve-Outs",
                "qualification": "revenue_gt_2b",
                "website": "https://blueriver.example.com",
                "cfo": "Avery Patel",
                "cao": "Taylor Kim",
                "trigger_keywords": "divestiture,carve-out,separation",
                "is_us_based": "true",
            }
        ],
    }


def _sample_watchlist(run_date: date):
    candidates = collect_business_news_opportunities(
        [
            {
                "company_name": "Crestline Foods",
                "source_date": "2026-03-10",
                "source_url": "https://news.example.com/crestline-restructuring",
                "initiative_type": "Restructuring",
                "timeline": "12 months",
                "summary": "Restructuring announced; likely near-miss due to lower urgency.",
                "role_we_could_fill": "Restructuring",
                "qualification": "revenue_gt_2b",
                "website": "https://crestline.example.com",
                "cfo": "Unknown",
                "cao": "Unknown",
                "trigger_keywords": "restructuring",
                "is_us_based": "true",
            }
        ]
    )
    return [score_opportunity(candidates[0], today=run_date)] if candidates else []


def _write_exports(*, payload, html: str, watchlist, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "sample_digest.html").write_text(html, encoding="utf-8")
    export_digest_json(payload, output_dir / "sample_digest.json")
    export_opportunities_csv(
        top_opportunities=payload.top_opportunities,
        watchlist=watchlist,
        output_path=output_dir / "sample_digest.csv",
    )


def run_cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Weekly IPO digest runner")
    parser.add_argument("--dry-run", action="store_true", help="Generate sample outputs without sending email")
    parser.add_argument("--export-only", action="store_true", help="Export outputs only; suppress HTML stdout")
    parser.add_argument("--test-mode", action="store_true", help="Run deterministic sample fixture mode")
    args = parser.parse_args(argv)

    run_date = date(2026, 4, 14) if args.test_mode else date.today()

    inputs = _sample_inputs() if (args.dry_run or args.export_only or args.test_mode) else {}
    payload, html = build_digest(run_date=run_date, **inputs)

    if args.dry_run or args.export_only or args.test_mode:
        watchlist = _sample_watchlist(run_date)
        _write_exports(payload=payload, html=html, watchlist=watchlist, output_dir=Path("sample_output"))

    if args.test_mode:
        print(f"test_mode=true top_ipos={len(payload.top_ipos)} top_opportunities={len(payload.top_opportunities)}")

    if not args.export_only:
        print(html)

    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli())
