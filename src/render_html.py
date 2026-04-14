"""HTML output renderer for the weekly digest email."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from .models import DigestPayload, ScoredOpportunity


def _build_executive_summary(payload: DigestPayload) -> str:
    return (
        f"This week includes {len(payload.top_ipos)} IPO signals and "
        f"{len(payload.top_opportunities)} prioritized finance opportunities."
    )


def _build_methodology() -> str:
    return (
        "Raw opportunities are collected first, then qualified, deduplicated, "
        "scored, and selected deterministically in code. Model usage is limited "
        "to post-selection summarization and does not influence ranking."
    )


def render_weekly_digest_html(
    payload: DigestPayload,
    *,
    watchlist: list[ScoredOpportunity] | None = None,
    generated_on: date | None = None,
    executive_summary: str | None = None,
    methodology: str | None = None,
    template_dir: Path | None = None,
) -> str:
    """Render weekly digest HTML with required output sections."""

    run_date = generated_on or date.today()
    watch = watchlist or []

    try:
        from jinja2 import Environment, FileSystemLoader, select_autoescape

        root = template_dir or Path(__file__).resolve().parent.parent / "templates"
        env = Environment(
            loader=FileSystemLoader(root),
            autoescape=select_autoescape(enabled_extensions=("html", "j2")),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        template = env.get_template("weekly_digest.html.j2")
        return template.render(
            generated_on=run_date.isoformat(),
            executive_summary=executive_summary or _build_executive_summary(payload),
            methodology=methodology or _build_methodology(),
            top_ipos=payload.top_ipos,
            top_opportunities=payload.top_opportunities,
            watchlist=watch,
        )
    except ModuleNotFoundError:
        return (
            "<h1>Weekly IPO & Finance Opportunity Digest</h1>"
            "<h2>Executive Summary</h2>"
            "<h2>Top 5 U.S. IPOs this week</h2>"
            "<h2>Top 10 U.S. opportunities</h2>"
            "<h2>Watchlist / near misses</h2>"
            "<h2>Methodology</h2>"
        )
