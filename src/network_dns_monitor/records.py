"""Structured log writers for health, alert, and ticket records."""

import json
from pathlib import Path
from typing import Any

from .models import CheckResult


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def append_json(path: str | Path, payload: dict[str, Any]) -> None:
    """Append one JSON object to a JSON Lines file."""
    output_path = Path(path)
    _ensure_parent(output_path)
    with output_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


def write_health(path: str | Path, result: CheckResult) -> None:
    """Append one human-readable healthy device entry."""
    output_path = Path(path)
    _ensure_parent(output_path)
    addresses = ", ".join(result.actual_ipv4) or "none"
    line = (
        f"{result.checked_at} | Device: {result.device.name} | "
        f"Status: HEALTHY | IPv4: {addresses}\n"
    )
    with output_path.open("a", encoding="utf-8") as handle:
        handle.write(line)


def result_payload(result: CheckResult) -> dict[str, Any]:
    """Convert a check result to a JSON-serializable incident payload."""
    return {
        "checked_at": result.checked_at,
        "device": result.device.name,
        "host": result.device.host,
        "port": result.device.port,
        "issue_type": result.issue_type,
        "details": result.details,
        "expected_ipv4": list(result.device.expected_ipv4),
        "actual_ipv4": list(result.actual_ipv4),
    }
