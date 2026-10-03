"""Local and SMTP alert notification backends."""

import os
import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path

from .models import CheckResult
from .records import append_json, result_payload


def write_alert(path: str | Path, result: CheckResult) -> None:
    """Write an alert to the local JSON Lines evidence log."""
    append_json(path, result_payload(result))


def send_email(result: CheckResult) -> None:
    """Send an SMTP email using environment-based configuration."""
    required = {
        "NDM_SMTP_HOST": os.environ.get("NDM_SMTP_HOST"),
        "NDM_EMAIL_FROM": os.environ.get("NDM_EMAIL_FROM"),
        "NDM_EMAIL_TO": os.environ.get("NDM_EMAIL_TO"),
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise ValueError(
            "Missing email environment variables: " + ", ".join(missing)
        )

    host = required["NDM_SMTP_HOST"]
    sender = required["NDM_EMAIL_FROM"]
    recipient = required["NDM_EMAIL_TO"]
    assert host and sender and recipient

    port = int(os.environ.get("NDM_SMTP_PORT", "25"))
    username = os.environ.get("NDM_SMTP_USERNAME")
    password = os.environ.get("NDM_SMTP_PASSWORD")
    use_starttls = os.environ.get("NDM_SMTP_STARTTLS", "false").lower()
    use_starttls = use_starttls in {"true", "yes", "1"}

    message = EmailMessage()
    message["From"] = sender
    message["To"] = recipient
    message["Subject"] = (
        f"Network alert: {result.device.name} ({result.issue_type})"
    )
    message.set_content(
        f"Network monitoring detected an issue.\n\n"
        f"Device: {result.device.name}\n"
        f"Host: {result.device.host}\n"
        f"Issue: {result.issue_type}\n"
        f"Checked: {result.checked_at}\n"
        f"Details: {result.details}\n"
    )

    with smtplib.SMTP(host, port, timeout=10) as smtp:
        if use_starttls:
            smtp.starttls(context=ssl.create_default_context())
        if username and password:
            smtp.login(username, password)
        smtp.send_message(message)
