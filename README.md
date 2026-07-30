# rf-test-automation
Python automation utilities for RF/bench instrument testing — PyVISA instrument control and CSV-based measurement logging, built toward a full pytest test suite.

## Current state
- `src/logging_utils.py` — CSV-based measurement logging: append readings, read them back, and summarize a test run (pass/fail counts against a target with tolerance, min/max/average). Pure logic, no hardware dependency, unit-testable.
- PyVISA instrument wrapper (instrument ID query, voltage check against tolerance) — in progress, not yet in this repo.
- pytest coverage — planned, not yet added.
