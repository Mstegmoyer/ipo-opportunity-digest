"""Backwards-compatible rendering wrapper."""

from __future__ import annotations

from pathlib import Path

from .models import DigestPayload
from .render_html import render_weekly_digest_html


def render_weekly_digest(payload: DigestPayload, *, template_dir: Path | None = None) -> str:
    """Render digest HTML using the output-layer renderer."""

    return render_weekly_digest_html(payload, template_dir=template_dir)
