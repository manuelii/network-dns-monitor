"""Tests for CSV inventory loading."""

import tempfile
import unittest
from pathlib import Path

from network_dns_monitor.inventory import load_inventory


class InventoryTests(unittest.TestCase):
    def test_loads_valid_inventory(self) -> None:
        content = (
            "name,host,port,expected_ipv4,simulated_online,simulated_ipv4\n"
            "Web,web.example.net,443,192.0.2.10,true,192.0.2.10\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "devices.csv"
            path.write_text(content, encoding="utf-8")
            devices = load_inventory(path)

        self.assertEqual(len(devices), 1)
        self.assertEqual(devices[0].name, "Web")
        self.assertEqual(devices[0].port, 443)
        self.assertTrue(devices[0].simulated_online)

    def test_rejects_invalid_port(self) -> None:
        content = (
            "name,host,port,expected_ipv4,simulated_online,simulated_ipv4\n"
            "Web,web.example.net,not-a-port,192.0.2.10,true,192.0.2.10\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "devices.csv"
            path.write_text(content, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "port must be an integer"):
                load_inventory(path)


if __name__ == "__main__":
    unittest.main()
