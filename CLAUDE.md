# Claude Code Instructions

## Commit Style
- No `Co-Authored-By: Claude` line — omit it from all commits
- Commit messages follow: `Fix #N: <short description>; bump to X.Y.Z`

## Branch / Environment Rules

### On `dev/nightly` (current development branch)
- Work here for all in-progress features
- PRs target `main`
- Do NOT tag or create stable releases from this branch
- Nightly builds are triggered automatically or via:
  `gh workflow run nightly.yml --ref dev/nightly`
- Version in `pyproject.toml` should be bumped (patch) with each commit so nightly stamps correctly (e.g. `0.1.139.dev20260322`)

### On `main`
- Only merged, reviewed code lands here
- Nightly builds run automatically from `main` every night at midnight CST (06:00 UTC)
- Stable releases are cut from `main` only (see below)

## Releasing a New Version

### Stable release (from `main` only)
1. Ensure you are on `main` and it is clean
2. Bump `version` in `pyproject.toml` (patch increment unless told otherwise)
3. Stage and commit the relevant files with a message referencing the issue/change and the new version
4. Tag: `git tag vX.Y.Z`
5. Push branch + tag: `git push origin main --tags`
6. Create GitHub release: `gh release create vX.Y.Z --title "vX.Y.Z" --notes "<summary>"`
7. The `release.yml` CI workflow validates the tag matches `pyproject.toml`, runs tests, builds, and publishes

### Nightly release (manual trigger from any branch)
1. Run: `gh workflow run nightly.yml --ref <branch-name>`
2. No tagging or version bumping needed — the workflow stamps the version automatically

## URL / Org References
- All GitHub URLs must point to `T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit`
- Never leave references to the old fork `bsikar/scpi-instrument-toolkit`

## SCPI Driver Contract (enforced on every PR)
- NEVER return a hardcoded value from any getter — always return self._attr
- NEVER use `from time import sleep` — always `import time; time.sleep(...)`
- NEVER omit get_error() — stub it with "not supported on <ClassName>" if needed
- NEVER call instrument.write() for a command that returns a value — use query()
- ALWAYS validate numeric inputs against min/max; raise ValueError on violation
- ALWAYS validate enum inputs against a class-level ALLOWLIST constant
- ALWAYS implement __enter__ / __exit__; __exit__ must fire after exceptions
- ALWAYS update self._cache atomically with every write() call

## Test Rules
- Every driver fix ships WITH its tesdid  in the same commit — never separate
- Mock classes must track state, not return constants
- Use `monkeypatch.setattr(module.time, "sleep", lambda _: None)` for timing

## Commands
- Run tests:  pytest tests/ -x --tb=short
- Full suite:  pytest tests/ -v --cov=lab_instruments --cov-report=term-missing
- Lint:        ruff check lab_instruments/ tests/
- Format check: ruff format --check lab_instruments/ tests/
- Format fix:   ruff format lab_instruments/ tests/

## Pre-Push Checklist (ALWAYS run before any git push)
1. `ruff check lab_instruments/ tests/`          — must be clean
2. `ruff format --check lab_instruments/ tests/` — must be clean (run `ruff format` to fix)
3. `pytest tests/ -x --tb=short`                 — must pass

CI runs both `ruff check` AND `ruff format --check`. Forgetting the format check is the most common cause of CI failures.

## Docs Rules (`docs/*.md`)
The `docs/` folder is built by MkDocs and served to users. Keep it in sync with code changes:
- When adding or changing REPL syntax, update `docs/scripting.md` AND `docs/examples.md`
- Variable syntax in all docs must use `{var}` (not `${var}`) and `var = value` (not `set var value`)
- `print` examples must use quoted strings: `print "message {var}"`
- `set -e` / `set +e` are NOT deprecated -- keep them as-is in docs

## Official Docs Site
- URL: https://t-o-m-tool-oauto-mationator.github.io/scpi-instrument-toolkit/
- When the user says "official docs" or "the docs", this site is what they mean
- ALWAYS rebuild and deploy docs after any change to `docs/*.md` or `mkdocs.yml`
  so students always have access to the most recent version
- Deploy command: `mkdocs gh-deploy --force`
- Never leave doc changes uncommitted or undeployed -- deploy in the same step as the commit

## Available Subagents

The project ships five Claude Code subagents under `.claude/agents/`. Claude Code will auto-delegate based on these descriptions, or you can @-mention them explicitly. Run `/agents` in a session to see them in the Library tab.

- **`@debug-issue`** -- 7-phase GitHub issue debugger (understand, reproduce, isolate, fix, test, document, PR). Use for any bug with an issue number or failing test.
- **`@scpi-contract-reviewer`** -- Read-only Driver Contract enforcer. Run after any edit under `lab_instruments/src/` or before opening a PR touching driver code.
- **`@pre-push-validator`** -- Runs `ruff check`, `ruff format --check`, and `pytest tests/ -x` in one shot. Run before every push to avoid the most common CI failure.
- **`@driver-test-writer`** -- Generates pytest tests for SCPI driver methods following the project's state-tracking-mock conventions.
- **`@docs-sync`** -- Keeps `docs/*.md` consistent, rebuilds MkDocs, and deploys to the official site. Run after any doc edit.