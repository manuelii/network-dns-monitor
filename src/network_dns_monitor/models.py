"""Data models shared across the monitoring application."""

from dataclasses import dataclass
from datetime import datetime, timezone


def utc_timestamp() -> str:
    """Return a readable UTC timestamp."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


@dataclass(frozen=True)
class Device:
    """A device and the expected state used by the monitor."""

    name: str
    host: str
    port: int
    expected_ipv4: tuple[str, ...]
    simulated_online: bool
    simulated_ipv4: tuple[str, ...]


@dataclass(frozen=True)
class CheckResult:
    """The result of one device availability and DNS check."""

    device: Device
    online: bool
    actual_ipv4: tuple[str, ...]
    checked_at: str
    error: str | None = None

    @property
    def dns_correct(self) -> bool:
        """Return True when actual and expected DNS records match."""
        return set(self.actual_ipv4) == set(self.device.expected_ipv4)

    @property
    def healthy(self) -> bool:
        """Return True when the device is online and DNS is correct."""
        return self.online and self.dns_correct

    @property
    def issue_type(self) -> str:
        """Return a short incident classification."""
        if not self.online:
            return "device_unavailable"
        if not self.dns_correct:
            return "dns_drift"
        return "healthy"

    @property
    def details(self) -> str:
        """Return human-readable check details."""
        if not self.online:
            suffix = f" Error: {self.error}" if self.error else ""
            return (
                f"{self.device.name} did not respond on "
                f"{self.device.host}:{self.device.port}.{suffix}"
            )

        if not self.dns_correct:
            actual = ", ".join(self.actual_ipv4) or "none"
            expected = ", ".join(self.device.expected_ipv4) or "none"
            return (
                f"{self.device.name} resolved to [{actual}] instead of "
                f"the expected [{expected}]."
            )

        return f"{self.device.name} is online and its DNS records are correct."
