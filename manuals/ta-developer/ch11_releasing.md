# Chapter 11: Releasing New Versions

## Two Release Channels

### Stable releases (from main only)

Published versions that students install. Tagged with semver (e.g., v1.0.17).

### Nightly builds (from any branch)

Dev-stamped versions for testing. Version is automatically stamped with the date (e.g., 1.0.17.dev20260416).

## Publishing a Stable Release

### Prerequisites

- You are on the `main` branch
- The branch is clean (no uncommitted changes)
- All tests pass
- dev/nightly has been merged to main

### Steps

1. Bump the version in `pyproject.toml`:

       [project]
       version = "1.0.18"    # increment patch number

2. Commit the version bump:

       git add pyproject.toml
       git commit -m "Bump to v1.0.18"

3. Tag the release:

       git tag v1.0.18

4. Push the branch and tag:

       git push origin main --tags

5. Create the GitHub release:

       gh release create v1.0.18 --title "v1.0.18" --notes "Summary of changes"

6. The `release.yml` workflow will:
   - Validate that the tag matches `pyproject.toml`
   - Run the full test suite
   - Build the package
   - Publish (if configured)

### Version numbering

- **Patch** (1.0.X): bug fixes, test additions, doc updates
- **Minor** (1.X.0): new features, new instrument support
- **Major** (X.0.0): breaking changes (rare)

Increment patch for most commits on dev/nightly. Use minor/major only when told.

## Publishing a Nightly Build

Nightly builds run automatically from main every night at midnight CST (06:00 UTC).

To trigger manually from any branch:

    gh workflow run nightly.yml --ref dev/nightly

No tagging or version bumping needed -- the workflow stamps the version automatically.

## Merging dev/nightly to main

1. Ensure dev/nightly is clean:

       git checkout dev/nightly
       ruff check lab_instruments/ tests/
       ruff format --check lab_instruments/ tests/
       pytest tests/ -x --tb=short

2. Merge to main:

       git checkout main
       git merge dev/nightly -m "Merge dev/nightly for v1.0.18 release"

3. Follow the stable release steps above.

## Version in pyproject.toml

The version field in `pyproject.toml` is the single source of truth:

    [project]
    version = "1.0.18"

Every commit on dev/nightly should bump the patch version so nightly stamps correctly.

## What Happens After a Release

Students update with:

    pip install --upgrade "git+https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git@v1.0.18"

Or the REPL's built-in update check tells them to update on next launch.

## Hotfix Process

For urgent fixes that cannot wait for the normal release cycle:

1. Branch from main: `git checkout -b hotfix/fix-name main`
2. Fix the issue, add tests
3. Bump patch version
4. Merge to main: `git checkout main && git merge hotfix/fix-name`
5. Tag and release
6. Merge the fix back to dev/nightly: `git checkout dev/nightly && git merge main`

## Commit Message Convention

    Fix #N: <short description>; bump to X.Y.Z

Examples:

    Fix #78: save_waveform_csv now accepts list/tuple of channels; bump to 1.0.9
    Add 77 variable type edge-case tests; fix calc names dict bug; bump to 1.0.14

No Co-Authored-By line (project convention).
