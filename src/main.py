"""CLI entrypoint for weekly digest orchestration."""

from __future__ import annotations

import argparse
import json
import logging
from datetime import date
from pathlib import Path
from typing import Any

from .config import get_settings
from .emailer import send_digest_email
from .exporters import export_digest_csv, export_digest_json
from .pipelines.build_digest import build_digest
from .scoring import score_opportunity
from .selectors import apply_repeat_suppression, history_updates_from_finalists
from .sources.business_news import collect_business_news_opportunities

LOGGER = logging.getLogger(__name__)


def _configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        LOGGER.warning("Fixture file not found: %s", path)
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _load_history(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    return {str(k).strip().lower(): dict(v) for k, v in raw.items()}


def _save_history(path: Path, history: dict[str, dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(history, indent=2, sort_keys=True), encoding="utf-8")


def _sample_inputs(fixtures_dir: Path | None = None) -> dict[str, list[dict[str, str]]]:
    """Load deterministic sample source inputs for dry-run/test-mode."""

    root = fixtures_dir or Path("data/samples")
    ipos = _load_json(root / "ipos.json")
    opportunities = _load_json(root / "opportunities.json")

    combined: dict[str, list[dict[str, str]]] = {}
    for key in ("sec_ipo_records", "ipo_calendar_records"):
        combined[key] = list(ipos.get(key, []))
    for key in ("sec_opportunity_records", "press_release_records", "business_news_records"):
        combined[key] = list(opportunities.get(key, []))
    return combined


def _sample_watchlist(run_date: date, fixtures_dir: Path | None = None):
    root = fixtures_dir or Path("data/samples")
    opportunities = _load_json(root / "opportunities.json")
    watchlist_records = list(opportunities.get("watchlist_records", []))
    candidates = collect_business_news_opportunities(watchlist_records)
    return [score_opportunity(item, today=run_date) for item in candidates]


def _write_exports(*, payload, html: str, watchlist, output_dir: Path) -> None:
    LOGGER.info("Export stage started: writing outputs to %s", output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "sample_digest.html").write_text(html, encoding="utf-8")
    export_digest_json(payload, output_dir / "sample_digest.json")
    export_digest_csv(payload=payload, watchlist=watchlist, output_path=output_dir / "sample_digest.csv")
    LOGGER.info("Export stage completed")


def _safe_send_email(*, enabled: bool, subject: str, html_body: str) -> bool:
    """Send digest email only when explicitly enabled and safe."""

    if not enabled:
        LOGGER.info("Email send skipped")
        return False

    LOGGER.info("Email stage started")
    settings = get_settings()
    send_digest_email(subject=subject, html_body=html_body, settings=settings)
    LOGGER.info("Email stage completed")
    return True


def run_cli(argv: list[str] | None = None) -> int:
    _configure_logging()

    parser = argparse.ArgumentParser(description="Weekly IPO digest runner")
    parser.add_argument("--dry-run", action="store_true", help="Generate outputs without sending email")
    parser.add_argument("--export-only", action="store_true", help="Write JSON/CSV/HTML previews only")
    parser.add_argument("--test-mode", action="store_true", help="Use deterministic fixture data and fixed date")
    parser.add_argument("--send-email", action="store_true", help="Enable live email send")
    parser.add_argument("--fixtures-dir", type=Path, default=Path("data/samples"), help="Fixture directory")
    parser.add_argument("--output-dir", type=Path, default=Path("sample_output"), help="Export output directory")
    parser.add_argument("--history-file", type=Path, default=Path("sample_output/opportunity_history.json"), help="History JSON path")
    parser.add_argument("--history-cooldown-days", type=int, default=30, help="Repeat suppression cooldown")
    args = parser.parse_args(argv)

    # Email is only allowed when explicitly requested and not in a safe test mode.
    send_email = args.send_email and not args.dry_run and not args.export_only

    LOGGER.info("Pipeline stage started: args=%s", args)
    LOGGER.info(
        "Email safety: requested=%s dry_run=%s export_only=%s final_send_email=%s",
        args.send_email,
        args.dry_run,
        args.export_only,
        send_email,
    )

    run_date = date(2026, 4, 14) if args.test_mode else date.today()

    use_fixtures = args.dry_run or args.export_only or args.test_mode
    inputs = _sample_inputs(args.fixtures_dir) if use_fixtures else {}

    history_by_company = _load_history(args.history_file)
    LOGGER.info("History loaded: %s records", len(history_by_company))

    LOGGER.info("Build stage started")
    payload, html = build_digest(run_date=run_date, history_by_company=history_by_company, **inputs)
    LOGGER.info(
        "Build stage completed: top_ipos=%s top_opportunities=%s",
        len(payload.top_ipos),
        len(payload.top_opportunities),
    )

    if args.dry_run and history_by_company:
        unsuppressed_payload, _ = build_digest(run_date=run_date, history_by_company=None, **inputs)
        retained, suppressed = apply_repeat_suppression(
            unsuppressed_payload.top_opportunities,
            history_by_company=history_by_company,
            today=run_date,
            cooldown_days=args.history_cooldown_days,
        )
        LOGGER.info(
            "Repeat suppression report: retained=%s suppressed=%s",
            [item.opportunity.company_name for item in retained],
            [item.opportunity.company_name for item in suppressed],
        )

    watchlist = _sample_watchlist(run_date, args.fixtures_dir) if use_fixtures else []

    if use_fixtures:
        _write_exports(payload=payload, html=html, watchlist=watchlist, output_dir=args.output_dir)

    if args.test_mode:
        print(f"test_mode=true top_ipos={len(payload.top_ipos)} top_opportunities={len(payload.top_opportunities)}")

    email_sent = _safe_send_email(
        enabled=send_email,
        subject=f"Weekly IPO & Finance Opportunity Digest - {run_date.isoformat()}",
        html_body=html,
    )

    if email_sent:
        updated_history = {**history_by_company, **history_updates_from_finalists(payload.top_opportunities, today=run_date)}
        _save_history(args.history_file, updated_history)
        LOGGER.info("History saved: %s records", len(updated_history))

    if not args.export_only:
        print(html)

    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli())
