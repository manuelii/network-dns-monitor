"""Tests for simulated monitoring behavior."""

import unittest

from network_dns_monitor.checks import check_simulated
from network_dns_monitor.models import Device


class CheckTests(unittest.TestCase):
    def test_healthy_device(self) -> None:
        device = Device(
            name="Healthy",
            host="healthy.example.net",
            port=443,
            expected_ipv4=("192.0.2.10",),
            simulated_online=True,
            simulated_ipv4=("192.0.2.10",),
        )
        result = check_simulated(device)
        self.assertTrue(result.healthy)
        self.assertEqual(result.issue_type, "healthy")

    def test_dns_drift(self) -> None:
        device = Device(
            name="Drifted",
            host="drifted.example.net",
            port=53,
            expected_ipv4=("192.0.2.53",),
            simulated_online=True,
            simulated_ipv4=("203.0.113.99",),
        )
        result = check_simulated(device)
        self.assertFalse(result.healthy)
        self.assertEqual(result.issue_type, "dns_drift")

    def test_unavailable_device(self) -> None:
        device = Device(
            name="Offline",
            host="offline.example.net",
            port=22,
            expected_ipv4=("198.51.100.20",),
            simulated_online=False,
            simulated_ipv4=("198.51.100.20",),
        )
        result = check_simulated(device)
        self.assertFalse(result.healthy)
        self.assertEqual(result.issue_type, "device_unavailable")


if __name__ == "__main__":
    unittest.main()
