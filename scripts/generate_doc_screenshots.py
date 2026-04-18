"""Generate terminal-style SVG screenshots for documentation.

Runs REPL commands in mock mode, captures colored output, and renders
each scenario as an SVG file in docs/img/terminal/.

Usage:
    python scripts/generate_doc_screenshots.py
"""

import io
import os
import sys
from pathlib import Path

# Ensure project root is importable
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# Suppress NO_COLOR auto-detection so we get ANSI codes for rendering
os.environ.pop("NO_COLOR", None)
os.environ["FORCE_COLOR"] = "1"

from rich.console import Console
from rich.text import Text
from rich.terminal_theme import DIMMED_MONOKAI

from lab_instruments import mock_instruments
from lab_instruments.repl.shell import InstrumentRepl
from lab_instruments.src import discovery as _disc
from lab_instruments.src.terminal import ColorPrinter

# Force color codes back on after import
ColorPrinter._refresh()

# Output directory
IMG_DIR = _PROJECT_ROOT / "docs" / "img" / "terminal"
IMG_DIR.mkdir(parents=True, exist_ok=True)


def _make_repl():
    """Create a mock-mode REPL instance."""
    _disc.InstrumentDiscovery.__init__ = lambda self: None
    _disc.InstrumentDiscovery.scan = (
        lambda self, verbose=True: mock_instruments.get_mock_devices(verbose)
    )
    repl = InstrumentRepl(register_lifecycle=False)
    repl._scan_thread.join(timeout=5.0)
    return repl


def _capture_commands(repl, commands, include_prompt=True):
    """Run commands and capture stdout output."""
    lines = []
    for cmd in commands:
        if include_prompt:
            lines.append(f"\033[92m>>>\033[0m {cmd}")
        # Capture output
        buf = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = buf
        try:
            repl.onecmd(cmd)
        finally:
            sys.stdout = old_stdout
        output = buf.getvalue()
        if output.strip():
            lines.append(output.rstrip())
    return "\n".join(lines)


def _render_svg(title, content, filename, width=100):
    """Render ANSI content to SVG using rich."""
    console = Console(
        file=io.StringIO(),
        force_terminal=True,
        width=width,
        record=True,
        color_system="truecolor",
    )
    # Title bar
    console.print(f"  [bold white on grey23] {title} [/]", highlight=False)
    console.print()
    # Parse ANSI codes in content
    text = Text.from_ansi(content)
    console.print(text, highlight=False)
    console.print()

    svg = console.export_svg(title=title, theme=DIMMED_MONOKAI)
    outpath = IMG_DIR / filename
    outpath.write_text(svg)
    print(f"  Generated: {outpath.relative_to(_PROJECT_ROOT)}")


# ── Screenshot definitions ──────────────────────────────────────────


SCENARIOS = [
    {
        "title": "Launching the REPL",
        "filename": "01_launch.svg",
        "commands": ["scan"],
        "doc": "index.md",
    },
    {
        "title": "Listing Connected Instruments",
        "filename": "02_list.svg",
        "commands": ["list"],
        "doc": "index.md, general.md",
    },
    {
        "title": "PSU: Set Voltage and Measure",
        "filename": "03_psu_basic.svg",
        "commands": [
            "use psu1",
            "psu chan 1 on",
            "psu set 1 5.0",
            "psu meas 1 v",
            "output_v = psu1 meas v unit=V",
        ],
        "doc": "index.md, psu.md",
    },
    {
        "title": "DMM: Configure and Read",
        "filename": "04_dmm_read.svg",
        "commands": [
            "use dmm1",
            "dmm config vdc",
            "voltage = dmm1 meas unit=V",
            "dmm config res",
            "resistance = dmm1 meas unit=ohms",
        ],
        "doc": "dmm.md",
    },
    {
        "title": "Variables and Arithmetic",
        "filename": "05_variables.svg",
        "commands": [
            "voltage = 5.0",
            "current = 0.25",
            "power = voltage * current",
            'print "Power = {power} W"',
            "doubled = power * 2",
            'print "Doubled = {doubled} W"',
        ],
        "doc": "scripting.md",
    },
    {
        "title": "Calc and Logging",
        "filename": "06_calc_log.svg",
        "commands": [
            "use psu1",
            "psu chan 1 on",
            "psu set 1 3.3",
            "v = psu1 meas v unit=V",
            "i = psu1 meas i unit=A",
            "calc power = v * i unit=W",
            "log print",
        ],
        "doc": "logging.md",
    },
    {
        "title": "Scope: Autoset and Measure",
        "filename": "07_scope.svg",
        "commands": [
            "use scope1",
            "scope autoset",
            "scope chan 1 on",
            "scope vscale 1 1.0",
            "scope hscale 0.001",
            "freq = scope1 meas FREQUENCY unit=Hz",
        ],
        "doc": "scope.md",
    },
    {
        "title": "For Loop: Voltage Sweep",
        "filename": "08_for_loop.svg",
        "commands": [
            "use psu1",
            "psu chan 1 on",
            "for v 1.0 2.0 3.3 5.0",
            '  print "Setting {v} V"',
            "  psu set 1 {v}",
            "  sleep 0.2",
            "  psu_v = psu1 meas v unit=V",
            "end",
            "log print",
        ],
        "doc": "scripting.md",
    },
    {
        "title": "If/Else: Conditional Check",
        "filename": "09_if_else.svg",
        "commands": [
            "voltage = 5.05",
            "if voltage > 5.1",
            '  verdict = "OVER"',
            "elif voltage < 4.9",
            '  verdict = "UNDER"',
            "else",
            '  verdict = "OK"',
            "end",
            'print "Voltage {voltage} V: {verdict}"',
        ],
        "doc": "scripting.md",
    },
    {
        "title": "Assert and Check",
        "filename": "10_assert_check.svg",
        "commands": [
            "voltage = 5.05",
            'assert voltage > 0 "voltage must be positive"',
            'assert voltage < 6.0 "voltage below safety limit"',
            'check voltage > 4.9 "above lower bound"',
            'check voltage < 5.1 "below upper bound"',
            'check voltage > 100 "this will FAIL"',
            "log report",
        ],
        "doc": "scripting.md",
    },
    {
        "title": "Multi-Instrument Workflow",
        "filename": "11_multi_instrument.svg",
        "commands": [
            "use psu1",
            "psu chan 1 on",
            "psu set 1 5.0 0.5",
            "sleep 0.3",
            "psu_v = psu1 meas v unit=V",
            "dmm_v = dmm1 meas unit=V",
            "calc error = psu_v - dmm_v unit=V",
            "calc error_pct = (psu_v - dmm_v) / psu_v * 100 unit=%",
            "log print",
        ],
        "doc": "examples.md",
    },
    {
        "title": "State Management",
        "filename": "12_state.svg",
        "commands": [
            "all off",
            "state safe",
            "idn",
        ],
        "doc": "general.md",
    },
    {
        "title": "AWG: Waveform Setup",
        "filename": "13_awg.svg",
        "commands": [
            "use awg1",
            "awg wave SIN",
            "awg freq 1000",
            "awg amp 2.5",
            "awg offset 0",
            "awg on",
        ],
        "doc": "awg.md",
    },
]


def main():
    print("Generating terminal screenshots for documentation...")
    print(f"Output: {IMG_DIR.relative_to(_PROJECT_ROOT)}/\n")

    repl = _make_repl()

    for scenario in SCENARIOS:
        title = scenario["title"]
        filename = scenario["filename"]
        commands = scenario["commands"]
        print(f"  [{scenario['doc']}] {title}")

        # Fresh REPL per scenario for clean state
        repl = _make_repl()
        repl.onecmd("scan")

        content = _capture_commands(repl, commands)
        _render_svg(title, content, filename)

        try:
            repl.close()
        except Exception:
            pass

    print(f"\nDone! {len(SCENARIOS)} screenshots generated in docs/img/terminal/")
    print("Embed in docs with: ![Title](img/terminal/filename.svg)")


if __name__ == "__main__":
    main()
