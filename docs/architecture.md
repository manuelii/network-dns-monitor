# Architecture and Design Decisions

## Components

| Module | Responsibility |
| --- | --- |
| `inventory.py` | Load and validate CSV device records |
| `checks.py` | Perform simulated or live availability and DNS checks |
| `models.py` | Represent devices and check results with data classes |
| `monitor.py` | Coordinate checks, alerts, health records, and tickets |
| `notifications.py` | Write local alerts and optionally send SMTP email |
| `records.py` | Append human-readable and JSON Lines evidence |
| `tickets.py` | Create local tickets or submit them to a REST webhook |
| `cli.py` | Parse options and run one-time or continuous monitoring |

## Data flow

1. The CLI loads `config/devices.csv`.
2. Each row is validated and converted into an immutable `Device` object.
3. A simulated or live check produces an immutable `CheckResult`.
4. Healthy results are appended to `health.log`.
5. Failed results are written to `alerts.jsonl`.
6. Optional email notification is sent through SMTP.
7. A ticket is written locally or submitted to a configured REST endpoint.

## Design decisions

### Safe demonstration mode

Simulation is the default. It makes the project immediately testable and
prevents accidental traffic to unknown systems. Live monitoring requires an
explicit `--mode live` option.

### Standard-library implementation

The runtime has no third-party dependencies. CSV handling, TCP checks, DNS
resolution, SMTP, HTTP requests, JSON records, and tests use Python's standard
library. This keeps deployment simple and makes the implementation easy to
audit.

### Append-only evidence

Health, alert, and ticket records are append-only. JSON Lines was selected for
incidents because each line is independently parseable and can be shipped to a
log processor or SIEM.

### Pluggable response backends

Email and webhook ticket integrations are optional. Local records remain the
default, allowing the full workflow to run without external services.

### Secrets outside source control

Credentials and tokens are read from environment variables. `.env` files and
generated logs are excluded from Git.

## Possible extensions

- asynchronous checks for larger inventories
- exponential retry and alert deduplication
- Prometheus metrics and Grafana dashboards
- TLS certificate expiration checks
- ICMP or SNMP backends
- SQLite incident history
- ticket resolution when a failed device recovers

