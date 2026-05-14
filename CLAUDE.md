# Claude Code Instructions

## Behavioral Guidelines

Adapted from https://github.com/forrestchang/andrej-karpathy-skills/blob/main/CLAUDE.md.
These bias toward caution over speed. For trivial tasks, use judgment.

### 1. Think Before Coding
Don't assume. Don't hide confusion. Surface tradeoffs.
- State assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### 2. Simplicity First
Minimum code that solves the problem. Nothing speculative.
- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

### 3. Surgical Changes
Touch only what you must. Clean up only your own mess.
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.
- Test: every changed line should trace directly to the user's request.

### 4. Goal-Driven Execution
Define success criteria. Loop until verified.
- "Add validation" -> "Write tests for invalid inputs, then make them pass"
- "Fix the bug" -> "Write a test that reproduces it, then make it pass"
- "Refactor X" -> "Ensure tests pass before and after"

For multi-step tasks, state a brief plan with a verify check per step.

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

## LabVIEW bridge install layout (read this BEFORE editing the bridge for a LabVIEW user)

The LabVIEW Python Node loads modules by **import-by-name**, not by file path: it takes the basename of the module path constant (e.g. `labview_bridge`) and runs `import labview_bridge`. The file path is essentially advisory — Python's import machinery has to be able to resolve the bare name. This means **two things have to be true** for a LabVIEW user to pick up bridge edits:

1. `import labview_bridge` must succeed in the same Python interpreter LabVIEW launches. This requires the shim `labview_bridge.py` (the top-level file at the repo root) to live somewhere on that interpreter's `sys.path` — typically `site-packages/labview_bridge.py`.
2. The shim must re-export every function the user's VI calls. The shim does `from lab_instruments.src.labview_bridge import (...)` and lists each function explicitly, so adding a new bridge function means **also** adding it to the shim's import block AND `__all__`.

### Recommended setup for any LabVIEW dev machine

```powershell
cd C:\path\to\scpi-instrument-toolkit
pip install -e .
copy labview_bridge.py "$($(python -c 'import site; print(site.getsitepackages()[0])'))\labview_bridge.py"
```

- `pip install -e .` installs the `lab_instruments` package as editable. Edits under `lab_instruments/src/` flow through to LabVIEW automatically (no re-copy needed).
- `copy ... labview_bridge.py` puts the shim at site-packages so `import labview_bridge` works for LabVIEW. Only re-copy this file if you change the shim's export list (added a new bridge function name).

### Symptoms that mean the install is broken

- `Hex 0x683 / ModuleNotFoundError: No module named 'labview_bridge'` — shim missing from site-packages. Re-copy.
- `Hex 0x687 / AttributeError: module has no attribute '<new_function>'` — shim's import list is out of sync with the bridge. Add the new function to the shim and re-copy.
- LabVIEW silently runs old code with no validation errors despite repo edits — `pip show scpi-instrument-toolkit` returns "not found", meaning the install was wiped. Reinstall editable.
- After a successful run, edits don't take effect — Python Session has the module cached in memory. Restart LabVIEW (File > Exit, reopen). The bridge file change alone is not enough; the running interpreter has to be killed.

### When you add a new bridge function in this codebase

Three places must update together (otherwise LabVIEW users hit `AttributeError`):

1. `lab_instruments/src/labview_bridge.py` — the actual function
2. `labview_bridge.py` (repo root shim) — add to the import block AND `__all__`
3. `docs/labview.md` Function Reference — add a row so students can discover it

After committing, re-copy the shim to any active dev machine's site-packages so LabVIEW sees the new export. The site-packages copy is NOT auto-synced by the editable install (because the shim isn't part of the package; it's a top-level convenience file).

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