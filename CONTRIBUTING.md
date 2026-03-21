# Contributing & Development Guide

## Release Channels

This project has two install channels:

| Channel | Who it's for | Install command |
|---------|-------------|-----------------|
| **Stable** | End users, lab machines | `pip install "git+https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git@v0.1.138"` |
| **Nightly** | Developers, testers, anyone who wants bleeding-edge features | `pip install "git+https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git@nightly"` |

### Stable

- Tagged releases like `v0.1.138`
- Only created manually by pushing a version tag
- Tested, reviewed, and merged to `main` before release
- The REPL checks for stable updates on startup and prompts users to upgrade

### Nightly

- A rolling pre-release that always points to the latest `main`
- Built automatically every night at midnight CST (06:00 UTC)
- Can also be triggered manually from **any branch** (see below)
- Version is stamped as `0.1.138.dev20260321` so pip knows it's a dev build
- The REPL skips the update nag for dev builds

## How to Publish

### Stable Release

1. Bump the version in `pyproject.toml`
2. Commit and push to `main`
3. Tag and push:
   ```bash
   git tag v0.1.139
   git push origin v0.1.139
   ```
4. The `release.yml` workflow validates the tag matches `pyproject.toml`, runs tests, builds, and creates a GitHub Release

### Nightly Release (from main)

Happens automatically every night. No action needed.

### Nightly Release (from a feature branch)

To publish a nightly build from a branch like `repl-rewrite`:

1. Go to **Actions** → **Nightly** → **Run workflow**
2. In the "Branch to build from" field, type the branch name (e.g. `repl-rewrite`)
3. Click **Run workflow**

Or from the CLI:
```bash
gh workflow run nightly.yml --ref repl-rewrite
```

This runs tests on that branch, stamps a dev version, and updates the `nightly` tag + GitHub pre-release. Users on nightly will get your branch's code the next time they install.

## Development Setup

```bash
# Clone and install in dev mode
git clone https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git
cd scpi-instrument-toolkit
pip install -e ".[test,lint]"

# Run tests
pytest tests/ -v

# Run linter
ruff check lab_instruments/ tests/
ruff format --check lab_instruments/ tests/

# Start REPL with mock instruments (no hardware needed)
python -m lab_instruments --mock
```

## Project Structure

```
lab_instruments/
├── __init__.py              # Package exports
├── __main__.py              # Entry point for python -m lab_instruments
├── mock_instruments.py      # Mock devices for testing without hardware
├── repl/                    # REPL package (modular replacement for old repl.py)
│   ├── __init__.py          # main() entry point, update checker
│   ├── shell.py             # cmd.Cmd subclass — command routing
│   ├── context.py           # Shared state container
│   ├── device_registry.py   # Device resolution + capability queries
│   ├── capabilities.py      # Per-driver capability flags
│   ├── measurement_store.py # Measurement recording
│   ├── syntax.py            # $name variable resolution + safe_eval
│   ├── commands/            # One module per command group
│   │   ├── general.py       # scan, list, use, state, idn, raw, etc.
│   │   ├── psu.py           # Power supply commands
│   │   ├── awg.py           # Function generator commands
│   │   ├── dmm.py           # Multimeter commands
│   │   ├── scope.py         # Oscilloscope commands
│   │   ├── variables.py     # set, print, pause, input, sleep
│   │   ├── logging_cmd.py   # log, calc, check, report, data
│   │   ├── scripting.py     # script, record, examples, python, limits
│   │   ├── safety.py        # Safety limit system
│   │   └── base.py          # BaseCommand shared utilities
│   └── script_engine/       # Script expansion + execution
│       ├── expander.py      # for/repeat/array/call expansion
│       ├── runner.py        # Execution + step debugger
│       ├── evaluator.py     # Safe math eval
│       └── variables.py     # Variable substitution
└── src/                     # Instrument drivers
    ├── device_manager.py    # Base SCPI driver class
    ├── discovery.py         # Auto-discovery via PyVISA
    ├── hp_e3631a.py         # HP E3631A PSU
    ├── matrix_mps6010h.py   # MATRIX MPS-6010H PSU
    ├── hp_34401a.py         # HP 34401A DMM
    ├── owon_xdm1041.py      # Owon XDM1041 DMM
    ├── keysight_edu33212a.py # Keysight EDU33212A AWG
    ├── jds6600_generator.py  # JDS6600 AWG
    ├── bk_4063.py           # BK Precision 4063 AWG
    ├── rigol_dho804.py      # Rigol DHO804 Scope
    ├── tektronix_mso2024.py # Tektronix MSO2024 Scope
    └── terminal.py          # ColorPrinter utility
```

## CI Workflows

| Workflow | Trigger | What it does |
|----------|---------|--------------|
| `ci.yml` | Every push + PR | Lint (ruff), test (3.8/3.10/3.12), coverage gate (80%) |
| `release.yml` | Tag push `v*` | Validate version, test, build, create GitHub Release |
| `nightly.yml` | Daily 06:00 UTC + manual | Test, build with dev version, update `nightly` tag + pre-release |
| `dependency-review.yml` | PR to main | Check for vulnerable dependencies |
