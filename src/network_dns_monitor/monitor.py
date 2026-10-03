"""Monitoring workflow orchestration."""

from dataclasses import dataclass
from pathlib import Path

from .checks import check_device
from .models import CheckResult, Device
from .notifications import send_email, write_alert
from .records import write_health
from .tickets import create_local_ticket, create_webhook_ticket


@dataclass(frozen=True)
class RunSummary:
    """Counts returned after one complete monitoring scan."""

    total: int
    healthy: int
    incidents: int


def process_result(
    result: CheckResult,
    health_log: str | Path,
    alert_log: str | Path,
    ticket_log: str | Path,
    send_email_alerts: bool,
    ticket_backend: str,
) -> str | None:
    """Record health or create alert and ticket evidence."""
    if result.healthy:
        write_health(health_log, result)
        return None

    write_alert(alert_log, result)
    if send_email_alerts:
        send_email(result)

    if ticket_backend == "webhook":
        ticket = create_webhook_ticket(result)
    else:
        ticket = create_local_ticket(ticket_log, result)

    return str(ticket.get("ticket_id", "created"))


def run_scan(
    devices: list[Device],
    mode: str,
    timeout: float,
    health_log: str | Path,
    alert_log: str | Path,
    ticket_log: str | Path,
    send_email_alerts: bool = False,
    ticket_backend: str = "local",
) -> RunSummary:
    """Check every device once and perform configured responses."""
    healthy_count = 0

    for device in devices:
        result = check_device(device, mode=mode, timeout=timeout)
        state = "HEALTHY" if result.healthy else result.issue_type.upper()
        print(f"{device.name:<16} {state}")

        ticket_id = process_result(
            result=result,
            health_log=health_log,
            alert_log=alert_log,
            ticket_log=ticket_log,
            send_email_alerts=send_email_alerts,
            ticket_backend=ticket_backend,
        )
        if result.healthy:
            healthy_count += 1
        else:
            print(f"  {result.details}")
            print(f"  Ticket: {ticket_id}")

    return RunSummary(
        total=len(devices),
        healthy=healthy_count,
        incidents=len(devices) - healthy_count,
    )
