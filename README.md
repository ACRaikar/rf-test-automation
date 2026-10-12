# rf-test-automation
Python automation utilities for RF/bench instrument testing — PyVISA instrument control and CSV-based measurement logging, built toward a full pytest test suite.

## Current state
- `src/logging_utils.py` — CSV-based measurement logging: append readings, read them back, and summarize a test run (pass/fail counts against a target with tolerance, min/max/average). Pure logic, no hardware dependency, unit-testable.
- PyVISA instrument wrapper (instrument ID query, voltage check against tolerance) — in progress, not yet in this repo.
- pytest coverage — planned, not yet added.



# rf-test-automation

![CI](https://github.com/ACRaikar/rf-test-automation/actions/workflows/ci.yml/badge.svg)

Python automation utilities for RF/bench instrument testing: PyVISA instrument control, CSV measurement logging, log parsing, and REST result reporting. The logic is separated from the I/O, so it is unit-tested without hardware, and every pull request is tested automatically on GitHub Actions.

## What's in here

- `src/logging_utils.py`
  - CSV measurement logging: append readings, read them back, and summarize a run (pass/fail/error counts, min/max/average voltage).
  - PyVISA voltage checks against a target within a tolerance, including a single check and a full sweep. Each is split into a testable core that takes an open instrument and a thin wrapper that opens the real connection.
  - Regex log parsing for multiple log formats, plus error-code extraction.
- `src/api_utils.py`: REST helpers built on `requests`. Network calls are injected as a parameter, so tests use fakes and never touch the network.
- `tests/`: pytest suite using fake instruments, fake HTTP responses and `tmp_path` fixtures.

## Testing

```bash
pip install -r requirements.txt
pytest -m "not hardware"
```

The suite runs without any instrument. One test is marked `hardware`: it opens a real instrument at `GPIB0::12::INSTR` and needs a VISA backend (NI-VISA or `pyvisa-py`) plus the device on the bench. CI deselects it, and you can run it with `pytest -m hardware`.

## CI

GitHub Actions runs the suite on every pull request into `main` and on every push to `main`, on Python 3.12 and 3.13 with pip caching. The workflow is in `.github/workflows/`.

## Roadmap

- Spectrum analyzer sweep script on top of the existing PyVISA wrapper.
- Handling of instrument connection failures in sweeps.