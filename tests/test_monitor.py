"""Tests for the complete monitoring workflow."""

import json
import tempfile
import unittest
from pathlib import Path

from network_dns_monitor.models import Device
from network_dns_monitor.monitor import run_scan


class MonitorTests(unittest.TestCase):
    def test_scan_writes_health_alert_and_ticket_records(self) -> None:
        devices = [
            Device(
                name="Healthy",
                host="healthy.example.net",
                port=443,
                expected_ipv4=("192.0.2.10",),
                simulated_online=True,
                simulated_ipv4=("192.0.2.10",),
            ),
            Device(
                name="Offline",
                host="offline.example.net",
                port=22,
                expected_ipv4=("198.51.100.20",),
                simulated_online=False,
                simulated_ipv4=("198.51.100.20",),
            ),
        ]

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            health = root / "health.log"
            alerts = root / "alerts.jsonl"
            tickets = root / "tickets.jsonl"
            summary = run_scan(
                devices=devices,
                mode="simulated",
                timeout=1.0,
                health_log=health,
                alert_log=alerts,
                ticket_log=tickets,
            )

            self.assertIn("Device: Healthy", health.read_text())
            alert = json.loads(alerts.read_text().strip())
            ticket = json.loads(tickets.read_text().strip())

        self.assertEqual(summary.healthy, 1)
        self.assertEqual(summary.incidents, 1)
        self.assertEqual(alert["issue_type"], "device_unavailable")
        self.assertEqual(ticket["status"], "open")


if __name__ == "__main__":
    unittest.main()
