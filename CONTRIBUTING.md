# Contributing

Contributions should keep the project safe to run in simulation mode and avoid
introducing real credentials or private infrastructure details.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests -v
```

## Pull requests

1. Create a focused branch.
2. Add or update tests for behavior changes.
3. Run the full test suite.
4. Confirm no passwords, tokens, private addresses, or generated logs are
   included.
5. Describe the operational impact of the change.

