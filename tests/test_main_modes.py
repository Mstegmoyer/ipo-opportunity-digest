from __future__ import annotations

import json
from pathlib import Path

from src.config import Settings
from src.main import run_cli


def test_dry_run_with_send_email_flag_does_not_send(monkeypatch, tmp_path: Path) -> None:
    called = {"send": False}

    def _fake_send_email(*, subject: str, html_body: str, settings) -> None:
        called["send"] = True

    monkeypatch.setattr("src.main.send_digest_email", _fake_send_email)

    history_file = tmp_path / "history.json"
    exit_code = run_cli(
        [
            "--dry-run",
            "--send-email",
            "--fixtures-dir",
            "data/samples",
            "--output-dir",
            str(tmp_path),
            "--history-file",
            str(history_file),
        ]
    )

    assert exit_code == 0
    assert called["send"] is False
    assert not history_file.exists()
    assert (tmp_path / "sample_digest.json").exists()
    assert (tmp_path / "sample_digest.csv").exists()
    assert (tmp_path / "sample_digest.html").exists()


def test_export_only_suppresses_html_stdout(capsys, tmp_path: Path) -> None:
    exit_code = run_cli(
        [
            "--export-only",
            "--fixtures-dir",
            "data/samples",
            "--output-dir",
            str(tmp_path),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "<h1>" not in captured.out
    assert (tmp_path / "sample_digest.json").exists()


def test_send_email_mode_persists_history(monkeypatch, tmp_path: Path) -> None:
    def _fake_send_email(*, subject: str, html_body: str, settings) -> None:
        return None

    def _fake_get_settings() -> Settings:
        return Settings(
            environment="test",
            digest_timezone="UTC",
            log_level="INFO",
            smtp_host="smtp.example.com",
            smtp_port=587,
            smtp_username="u",
            smtp_password="p",
            email_from="from@example.com",
            email_to="to@example.com",
            openai_api_key=None,
            openai_model="gpt-5-mini",
        )

    monkeypatch.setattr("src.main.send_digest_email", _fake_send_email)
    monkeypatch.setattr("src.main.get_settings", _fake_get_settings)

    history_file = tmp_path / "history.json"
    exit_code = run_cli(
        [
            "--send-email",
            "--test-mode",
            "--fixtures-dir",
            "data/samples",
            "--output-dir",
            str(tmp_path),
            "--history-file",
            str(history_file),
        ]
    )

    assert exit_code == 0
    history = json.loads(history_file.read_text(encoding="utf-8"))
    assert history
    assert all("last_alerted" in value and "signature" in value for value in history.values())
