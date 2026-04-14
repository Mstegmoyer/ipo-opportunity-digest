"""SMTP email sender for weekly digest output."""

from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage

from .config import Settings

LOGGER = logging.getLogger(__name__)


def build_digest_email(*, subject: str, html_body: str, settings: Settings) -> EmailMessage:
    """Build MIME email message for digest delivery."""

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.email_from
    msg["To"] = settings.email_to
    msg.set_content("This email contains HTML content. Please view in an HTML-compatible client.")
    msg.add_alternative(html_body, subtype="html")
    return msg


def send_digest_email(*, subject: str, html_body: str, settings: Settings) -> None:
    """Send digest email through configured SMTP relay."""

    LOGGER.info("Connecting to SMTP relay host=%s port=%s", settings.smtp_host, settings.smtp_port)
    msg = build_digest_email(subject=subject, html_body=html_body, settings=settings)
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=30) as smtp:
        smtp.starttls()
        smtp.login(settings.smtp_username, settings.smtp_password)
        smtp.send_message(msg)
    LOGGER.info("Email sent to %s", settings.email_to)
