"""Availability and DNS checking functions."""

import socket

from .models import CheckResult, Device, utc_timestamp


def resolve_ipv4(host: str) -> tuple[str, ...]:
    """Resolve unique IPv4 records for a hostname."""
    records = {
        result[4][0]
        for result in socket.getaddrinfo(
            host,
            None,
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
        )
    }
    return tuple(sorted(records))


def check_live(device: Device, timeout: float = 2.0) -> CheckResult:
    """Perform a live TCP availability check and DNS lookup."""
    checked_at = utc_timestamp()

    try:
        actual_ipv4 = resolve_ipv4(device.host)
    except OSError as error:
        return CheckResult(
            device=device,
            online=False,
            actual_ipv4=(),
            checked_at=checked_at,
            error=f"DNS lookup failed: {error}",
        )

    try:
        with socket.create_connection(
            (device.host, device.port), timeout=timeout
        ):
            pass
    except OSError as error:
        return CheckResult(
            device=device,
            online=False,
            actual_ipv4=actual_ipv4,
            checked_at=checked_at,
            error=str(error),
        )

    return CheckResult(
        device=device,
        online=True,
        actual_ipv4=actual_ipv4,
        checked_at=checked_at,
    )


def check_simulated(device: Device) -> CheckResult:
    """Return deterministic demo data without touching a network."""
    error = None if device.simulated_online else "simulated timeout"
    return CheckResult(
        device=device,
        online=device.simulated_online,
        actual_ipv4=device.simulated_ipv4,
        checked_at=utc_timestamp(),
        error=error,
    )


def check_device(
    device: Device, mode: str, timeout: float = 2.0
) -> CheckResult:
    """Select the simulated or live check implementation."""
    if mode == "simulated":
        return check_simulated(device)
    if mode == "live":
        return check_live(device, timeout=timeout)
    raise ValueError(f"Unsupported monitoring mode: {mode}")
