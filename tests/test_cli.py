"""Tests for command-line validation and repeated scans."""

import tempfile
import unittest
from pathlib import Path

from network_dns_monitor.cli import main


class CliTests(unittest.TestCase):
    def test_rejects_indefinite_run_without_interval(self) -> None:
        exit_code = main(["--cycles", "0"])
        self.assertEqual(exit_code, 2)

    def test_runs_multiple_simulated_scans(self) -> None:
        inventory = (
            "name,host,port,expected_ipv4,simulated_online,simulated_ipv4\n"
            "Web,web.example.net,443,192.0.2.10,true,192.0.2.10\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            inventory_path = root / "devices.csv"
            inventory_path.write_text(inventory, encoding="utf-8")

            exit_code = main(
                [
                    "--inventory",
                    str(inventory_path),
                    "--log-directory",
                    str(root / "logs"),
                    "--cycles",
                    "2",
                    "--interval",
                    "0",
                ]
            )

            entries = (root / "logs" / "health.log").read_text().splitlines()

        self.assertEqual(exit_code, 0)
        self.assertEqual(len(entries), 2)


if __name__ == "__main__":
    unittest.main()

