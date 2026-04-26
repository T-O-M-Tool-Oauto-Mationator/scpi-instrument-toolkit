# Chapter 2: Development Setup

## Clone the Repository

    git clone https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git
    cd scpi-instrument-toolkit

## Create a Virtual Environment

    python -m venv .venv
    source .venv/bin/activate        # macOS/Linux
    .venv\Scripts\activate           # Windows

## Install in Development Mode

    pip install -e ".[dev]"

The `-e` flag installs in "editable" mode -- changes to source files take effect immediately without reinstalling.

## Verify the Installation

### Run the linter

    ruff check lab_instruments/ tests/

Must produce no errors.

### Check formatting

    ruff format --check lab_instruments/ tests/

Must report all files already formatted.

### Run tests

    pytest tests/ -x --tb=short

All tests must pass. The `-x` flag stops on first failure.

### Full coverage report

    pytest tests/ -v --cov=lab_instruments --cov-report=term-missing

Shows which lines are not covered by tests. Target: 80%+ coverage.

## The Pre-Push Checklist

Before every `git push`, run all three checks:

    ruff check lab_instruments/ tests/
    ruff format --check lab_instruments/ tests/
    pytest tests/ -x --tb=short

CI runs both `ruff check` AND `ruff format --check`. Forgetting the format check is the most common cause of CI failures.

If formatting is off, fix it with:

    ruff format lab_instruments/ tests/

## Branch Strategy

- `dev/nightly` -- active development branch. Work here.
- `main` -- stable releases only. Merged from dev/nightly after review.
- Feature branches -- for large changes that need review before merging to dev/nightly.

## Project Structure

    scpi-instrument-toolkit/
    ├── lab_instruments/
    │   ├── __init__.py              # Package entry point
    │   ├── enums.py                 # Shared enumerations
    │   ├── mock_instruments.py      # Mock devices for testing
    │   ├── examples.py              # Bundled example scripts
    │   ├── src/                     # Instrument drivers
    │   │   ├── device_manager.py    # Base class for SCPI drivers
    │   │   ├── discovery.py         # Auto-detection logic
    │   │   ├── hp_e3631a.py         # HP E3631A PSU driver
    │   │   ├── rigol_dho804.py      # Rigol DHO804 scope driver
    │   │   └── ...                  # More drivers
    │   └── repl/                    # REPL layer
    │       ├── __init__.py          # CLI entry point (main())
    │       ├── shell.py             # cmd.Cmd subclass, dispatch
    │       ├── context.py           # Shared session state
    │       ├── syntax.py            # Variable substitution, safe_eval
    │       ├── device_registry.py   # Device name management
    │       ├── measurement_store.py # Log storage
    │       ├── commands/            # Command handlers
    │       │   ├── base.py          # BaseCommand interface
    │       │   ├── psu.py           # PSU commands
    │       │   ├── dmm.py           # DMM commands
    │       │   ├── scope.py         # Scope commands
    │       │   └── ...              # More handlers
    │       └── script_engine/       # Script expansion & execution
    │           ├── expander.py      # For/repeat loop expansion
    │           └── runner.py        # Runtime execution (while/if)
    ├── tests/                       # pytest test suite
    ├── docs/                        # MkDocs documentation source
    ├── scripts/                     # Build/validation utilities
    ├── manuals/                     # Standalone DOCX manuals
    ├── CLAUDE.md                    # Project conventions for Claude Code
    ├── CONTRIBUTING.md              # Contributor guide
    ├── pyproject.toml               # Package metadata & dependencies
    └── mkdocs.yml                   # Documentation site config

## IDE Setup

### VS Code (recommended)

Install extensions:
- Python (Microsoft)
- Ruff (Astral Software)

Settings (`.vscode/settings.json`):

    {
        "python.defaultInterpreterPath": ".venv/bin/python",
        "editor.formatOnSave": true,
        "[python]": {
            "editor.defaultFormatter": "charliermarsh.ruff"
        }
    }

### PyCharm

- Set the project interpreter to `.venv/bin/python`
- Install the Ruff plugin
- Enable "Reformat code on save"

## Working with Claude Code

The project uses Claude Code subagents for common tasks:

- `@pre-push-validator` -- runs ruff + pytest before push
- `@debug-issue` -- investigates GitHub issues
- `@scpi-contract-reviewer` -- checks driver contract compliance
- `@driver-test-writer` -- generates tests for driver methods
- `@docs-sync` -- keeps docs in sync with code

Run `/agents` in a Claude Code session to see them in the Library tab.
