"""Manual entrypoint for weekly digest orchestration."""

from __future__ import annotations

from datetime import date

from .pipelines.build_digest import build_digest


def generate_weekly_digest(*, run_date: date | None = None) -> str:
    """Generate digest HTML from source adapters and deterministic selection pipeline."""

    today = run_date or date.today()
    _, html = build_digest(run_date=today)
    return html


if __name__ == "__main__":
    print(generate_weekly_digest())
