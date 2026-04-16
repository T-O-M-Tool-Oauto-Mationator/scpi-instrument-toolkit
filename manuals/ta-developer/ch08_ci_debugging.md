# Chapter 8: CI/CD and Debugging Failures

## CI Workflows

Four GitHub Actions workflows run automatically:

### ci.yml (every push and PR)

Two stages:

**1. Lint stage (must pass first):**

    ruff check lab_instruments/ tests/
    ruff format --check lab_instruments/ tests/

Both must be clean. If formatting fails, run `ruff format lab_instruments/ tests/` locally and commit the changes.

**2. Test stage (runs after lint passes):**

    pytest tests/ --cov=lab_instruments --cov-report=term-missing

Runs on Python 3.10 and 3.12 in a matrix. Coverage gate: 80% line coverage required.

### release.yml (on tag push v*)

Triggered when you push a version tag (e.g., `v1.0.17`):

1. Validates that the tag matches the version in pyproject.toml
2. Runs the full test suite
3. Builds the package
4. Publishes (if configured)

### nightly.yml (daily at 06:00 UTC + manual)

Builds a dev-stamped version from any branch:

    gh workflow run nightly.yml --ref dev/nightly

The version is automatically stamped with the date (e.g., `1.0.17.dev20260416`).

### dependency-review.yml (PRs to main)

Checks for vulnerable dependencies in the PR diff.

## Reading CI Failure Logs

When CI fails:

1. Go to the GitHub Actions tab on the repository
2. Click the failed workflow run
3. Click the failed job (lint or test)
4. Expand the step that failed
5. Read the error output

### Common lint failures

**Unsorted imports:**

    I001 Import block is un-sorted or un-formatted

Fix: `ruff check --fix lab_instruments/ tests/`

**Formatting mismatch:**

    Would reformat: lab_instruments/src/my_file.py

Fix: `ruff format lab_instruments/ tests/`

### Common test failures

**AssertionError with actual vs expected:**

    assert repl.ctx.script_vars["x"] == "5"
    AssertionError: assert 5 == "5"

This means the test expects a string but the code returns a native type. Update the assertion.

**ImportError or ModuleNotFoundError:**

    ModuleNotFoundError: No module named 'lab_instruments.src.my_new_driver'

The driver file was not committed or is not importable.

## Reproducing CI Failures Locally

Always reproduce before trying to fix:

    # Run the exact same checks CI runs:
    ruff check lab_instruments/ tests/
    ruff format --check lab_instruments/ tests/
    pytest tests/ -x --tb=short

If a specific test fails:

    pytest tests/test_my_file.py::TestMyClass::test_my_method -v --tb=long

## The Pre-Push Checklist

Run all three checks before every push:

    ruff check lab_instruments/ tests/
    ruff format --check lab_instruments/ tests/
    pytest tests/ -x --tb=short

Or use the `@pre-push-validator` subagent which runs all three in one shot.

## Claude Code Subagents for CI

### @pre-push-validator

Runs ruff check + ruff format --check + pytest in one command. Use before every push.

### @debug-issue

Follows a 7-phase methodology to investigate bugs: understand, reproduce, isolate, fix, regression-test, document, report. Mention a GitHub issue number or failing test and it handles the rest.

### @scpi-contract-reviewer

Read-only reviewer that checks all driver files for SCPI contract violations. Run before opening a PR that touches `lab_instruments/src/`.

## Fixing a Failed CI Run

1. Read the error in GitHub Actions
2. Reproduce locally with the same command
3. Fix the issue
4. Run the pre-push checklist
5. Commit and push

Do not force-push to bypass CI. Fix the underlying issue.
