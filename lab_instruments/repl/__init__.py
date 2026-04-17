"""REPL package — modular replacement for the monolithic repl.py."""

import sys

from lab_instruments.src.terminal import ColorPrinter

from .shell import _REPL_VERSION, InstrumentRepl

_GITHUB_REPO = "T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit"


def _check_for_updates(force=False):
    """Check GitHub for updates. Returns True if an update is available."""
    if _REPL_VERSION == "unknown":
        if force:
            print("Running from source — skipping update check.")
        return False

    # Nightly / dev builds skip the update check — they're ahead of stable
    if "dev" in _REPL_VERSION:
        if force:
            ColorPrinter.info(f"Running nightly build (v{_REPL_VERSION}) — skipping update check.")
        return False

    import json
    import urllib.request

    try:
        url = f"https://api.github.com/repos/{_GITHUB_REPO}/tags"
        req = urllib.request.Request(url, headers={"User-Agent": "scpi-instrument-toolkit"})
        with urllib.request.urlopen(req, timeout=2) as resp:
            tags = json.loads(resp.read())

        import re

        semver_tags = [t for t in tags if re.match(r"^v?\d+\.\d+\.\d+$", t["name"])]
        if not semver_tags:
            return False

        latest_tag = semver_tags[0]["name"]
        latest = latest_tag.lstrip("v")

        def _vtuple(v):
            return tuple(int(x) for x in v.split("."))

        if _vtuple(latest) <= _vtuple(_REPL_VERSION):
            if force:
                ColorPrinter.success(f"Already up to date (v{_REPL_VERSION}).")
            return False

        ColorPrinter.info(f"Update available: v{_REPL_VERSION} → v{latest}. To install, run:")
        git_url = f"git+https://github.com/{_GITHUB_REPO}.git@{latest_tag}#egg=scpi-instrument-toolkit"
        print(f'  pip install --upgrade "{git_url}"')
        return True

    except Exception:
        return False


def main():
    args = sys.argv[1:]

    if "--version" in args or "-V" in args:
        print(f"scpi-instrument-toolkit v{_REPL_VERSION}")
        sys.exit(0)

    if "--no-color" in args:
        from lab_instruments.src.terminal import disable_color

        disable_color()
        args = [a for a in args if a != "--no-color"]

    if "--help" in args or "-h" in args:
        print(
            f"scpi-instrument-toolkit v{_REPL_VERSION}\n"
            "\n"
            "Usage: scpi-repl [--mock] [--no-color] [--update] [--ignore-update] [--version] [--help] [script]\n"
            "\n"
            "Options:\n"
            "  --mock           Run with simulated instruments (no hardware required)\n"
            "  --no-color       Disable colored output (also respects NO_COLOR env var)\n"
            "  --update         Check for updates and display the install command\n"
            "  --ignore-update  Skip the update check and run even if a newer version exists\n"
            "  --version        Print version and exit\n"
            "  --help           Show this help and exit\n"
            "\n"
            "Arguments:\n"
            "  script       Name of a saved script to run non-interactively\n"
            "\n"
            "Examples:\n"
            "  scpi-repl                  Start the interactive REPL\n"
            "  scpi-repl --mock           Start with mock instruments\n"
            "  scpi-repl --no-color       Start without colored output\n"
            "  scpi-repl --update         Check for updates\n"
            "  scpi-repl --ignore-update  Run without checking for updates\n"
            "  scpi-repl my_script        Run 'my_script' and exit\n"
        )
        sys.exit(0)

    if "--update" in args:
        _check_for_updates(force=True)
        sys.exit(0)

    ignore_update = "--ignore-update" in args
    if ignore_update:
        args = [a for a in args if a != "--ignore-update"]

    update_available = _check_for_updates(force=False)
    if update_available and not ignore_update:
        ColorPrinter.error(
            "Please update before using the REPL. Run the command above, or use --ignore-update to skip this check."
        )
        sys.exit(1)

    if "--mock" in args:
        args = [a for a in args if a != "--mock"]
        from lab_instruments import mock_instruments
        from lab_instruments.src import discovery as _disc

        _disc.InstrumentDiscovery.__init__ = lambda self: None
        _disc.InstrumentDiscovery.scan = lambda self, verbose=True: mock_instruments.get_mock_devices(verbose)

    repl = InstrumentRepl()

    if args:
        script_name = args[0]
        if script_name not in repl.scripts:
            ColorPrinter.error(f"Script '{script_name}' not found.")
            sys.exit(1)
        repl._run_script_lines(repl.scripts[script_name])
        return

    repl.cmdloop()


__all__ = ["InstrumentRepl", "main"]
