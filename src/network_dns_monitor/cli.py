"""Command-line entry point for Network DNS Monitor."""

import argparse
import sys
import time
from pathlib import Path

from .inventory import load_inventory
from .monitor import run_scan


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(
        description="Monitor device availability and expected DNS records."
    )
    parser.add_argument(
        "--inventory",
        default=str(PROJECT_ROOT / "config" / "devices.csv"),
        help="Path to the CSV device inventory",
    )
    parser.add_argument(
        "--mode",
        choices=("simulated", "live"),
        default="simulated",
        help="Use repeatable demo checks or live network checks",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=2.0,
        help="Live TCP connection timeout in seconds",
    )
    parser.add_argument(
        "--send-email",
        action="store_true",
        help="Send SMTP alerts using NDM_* environment variables",
    )
    parser.add_argument(
        "--ticket-backend",
        choices=("local", "webhook"),
        default="local",
        help="Write local tickets or POST them to a REST webhook",
    )
    parser.add_argument(
        "--log-directory",
        default=str(PROJECT_ROOT / "logs"),
        help="Directory for generated health, alert, and ticket logs",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=0.0,
        help="Seconds between scans; 0 runs without a delay",
    )
    parser.add_argument(
        "--cycles",
        type=int,
        default=1,
        help="Number of scans; 0 continues until interrupted",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run one monitoring scan and return a process exit code."""
    args = build_parser().parse_args(argv)
    log_directory = Path(args.log_directory)

    if args.interval < 0:
        print("ERROR: --interval cannot be negative", file=sys.stderr)
        return 2
    if args.cycles < 0:
        print("ERROR: --cycles cannot be negative", file=sys.stderr)
        return 2
    if args.cycles == 0 and args.interval == 0:
        print(
            "ERROR: indefinite monitoring requires a positive --interval",
            file=sys.stderr,
        )
        return 2

    try:
        devices = load_inventory(args.inventory)
        print(f"Network DNS Monitor | Mode: {args.mode}")
        print(f"Loaded {len(devices)} devices from {args.inventory}")

        cycle = 0
        incidents_seen = False
        while args.cycles == 0 or cycle < args.cycles:
            cycle += 1
            print(f"\nScan {cycle}")
            summary = run_scan(
                devices=devices,
                mode=args.mode,
                timeout=args.timeout,
                health_log=log_directory / "health.log",
                alert_log=log_directory / "alerts.jsonl",
                ticket_log=log_directory / "tickets.jsonl",
                send_email_alerts=args.send_email,
                ticket_backend=args.ticket_backend,
            )
            incidents_seen = incidents_seen or summary.incidents > 0
            print(
                f"Summary: {summary.healthy} healthy, "
                f"{summary.incidents} incidents, {summary.total} total"
            )

            if args.cycles != 0 and cycle >= args.cycles:
                break
            print(f"Next scan in {args.interval:g} seconds...")
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nMonitoring stopped by operator.")
        return 130
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    print(f"Evidence directory: {log_directory.resolve()}")
    return 1 if incidents_seen else 0


if __name__ == "__main__":
    raise SystemExit(main())
