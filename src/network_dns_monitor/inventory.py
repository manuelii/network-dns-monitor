"""Load and validate device inventory data."""

import csv
from pathlib import Path

from .models import Device


REQUIRED_COLUMNS = {
    "name",
    "host",
    "port",
    "expected_ipv4",
    "simulated_online",
    "simulated_ipv4",
}


def _split_addresses(value: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in value.split(";") if item.strip())


def _parse_boolean(value: str, row_number: int) -> bool:
    normalized = value.strip().lower()
    if normalized in {"true", "yes", "1"}:
        return True
    if normalized in {"false", "no", "0"}:
        return False
    raise ValueError(
        f"Row {row_number}: simulated_online must be true or false"
    )


def load_inventory(path: str | Path) -> list[Device]:
    """Read devices from a CSV inventory and validate required fields."""
    inventory_path = Path(path)

    with inventory_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - columns
        if missing:
            missing_text = ", ".join(sorted(missing))
            raise ValueError(f"Inventory is missing columns: {missing_text}")

        devices: list[Device] = []
        for row_number, row in enumerate(reader, start=2):
            name = row["name"].strip()
            host = row["host"].strip()
            if not name or not host:
                raise ValueError(f"Row {row_number}: name and host are required")

            try:
                port = int(row["port"])
            except ValueError as error:
                raise ValueError(
                    f"Row {row_number}: port must be an integer"
                ) from error

            if not 1 <= port <= 65535:
                raise ValueError(
                    f"Row {row_number}: port must be between 1 and 65535"
                )

            devices.append(
                Device(
                    name=name,
                    host=host,
                    port=port,
                    expected_ipv4=_split_addresses(row["expected_ipv4"]),
                    simulated_online=_parse_boolean(
                        row["simulated_online"], row_number
                    ),
                    simulated_ipv4=_split_addresses(row["simulated_ipv4"]),
                )
            )

    if not devices:
        raise ValueError("Inventory does not contain any devices")

    return devices
