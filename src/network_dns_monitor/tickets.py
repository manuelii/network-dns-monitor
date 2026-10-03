"""Local JSON and REST webhook ticket backends."""

import json
import os
import urllib.request
import uuid
from pathlib import Path
from typing import Any

from .models import CheckResult
from .records import append_json, result_payload


def build_ticket(result: CheckResult) -> dict[str, Any]:
    """Build a generic incident ticket from a failed check."""
    ticket = result_payload(result)
    ticket.update(
        {
            "ticket_id": str(uuid.uuid4()),
            "status": "open",
            "priority": "high" if not result.online else "medium",
            "title": f"{result.issue_type}: {result.device.name}",
        }
    )
    return ticket


def create_local_ticket(
    path: str | Path, result: CheckResult
) -> dict[str, Any]:
    """Persist a ticket to a local JSON Lines file."""
    ticket = build_ticket(result)
    append_json(path, ticket)
    return ticket


def create_webhook_ticket(result: CheckResult) -> dict[str, Any]:
    """POST a ticket to a configurable REST webhook."""
    endpoint = os.environ.get("NDM_TICKET_WEBHOOK")
    if not endpoint:
        raise ValueError("NDM_TICKET_WEBHOOK is required for webhook tickets")

    ticket = build_ticket(result)
    headers = {"Content-Type": "application/json"}
    token = os.environ.get("NDM_TICKET_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(
        endpoint,
        data=json.dumps(ticket).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        response_body = response.read().decode("utf-8")

    if response_body:
        try:
            remote_ticket = json.loads(response_body)
        except json.JSONDecodeError:
            ticket["webhook_response"] = response_body
        else:
            if isinstance(remote_ticket, dict):
                ticket.update(remote_ticket)

    return ticket
