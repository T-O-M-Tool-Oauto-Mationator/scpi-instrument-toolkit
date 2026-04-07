"""Auto-generate reference documentation at mkdocs build time.

This script runs via the mkdocs-gen-files plugin and produces:
  - generated/instruments.md   — capability matrix from DRIVER_CAPABILITIES
  - generated/repl-ref.md      — REPL command quick-reference from _show_help()
"""

import inspect
import io
import re
import sys
from contextlib import redirect_stdout
from pathlib import Path

import mkdocs_gen_files

# Ensure the project root is importable
_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from lab_instruments.repl.capabilities import (  # noqa: E402
    DISPLAY_NAMES,
    DRIVER_CAPABILITIES,
    Capability,
)

# ---------------------------------------------------------------------------
# Device metadata not available in capabilities.py (one-time manual mapping)
# ---------------------------------------------------------------------------
DEVICE_INFO = {
    "HP_E3631A": {"type": "Power Supply", "interface": "GPIB"},
    "Keysight_EDU36311A": {"type": "Power Supply", "interface": "USB / LAN"},
    "MATRIX_MPS6010H": {"type": "Power Supply", "interface": "Serial"},
    "NI_PXIe_4139": {"type": "SMU", "interface": "PXIe (nidcpower)"},
    "Keysight_EDU33212A": {"type": "Function Generator", "interface": "USB"},
    "BK_4063": {"type": "Function Generator", "interface": "USB"},
    "JDS6600_Generator": {"type": "Function Generator", "interface": "Serial"},
    "HP_34401A": {"type": "Multimeter", "interface": "GPIB"},
    "Keysight_EDU34450A": {"type": "Multimeter", "interface": "USB / LAN"},
    "Owon_XDM1041": {"type": "Multimeter", "interface": "USB / Serial"},
    "Rigol_DHO804": {"type": "Oscilloscope", "interface": "USB"},
    "Keysight_DSOX1204G": {"type": "Oscilloscope", "interface": "USB / LAN"},
    "Tektronix_MSO2024": {"type": "Oscilloscope", "interface": "USB / GPIB"},
    "TI_EV2300": {"type": "USB-to-I2C Adapter", "interface": "USB HID"},
}

# Human-readable capability names
CAPABILITY_LABELS = {
    Capability.PSU_MULTI_CHANNEL: "Multi-channel",
    Capability.PSU_READBACK: "Readback",
    Capability.PSU_TRACKING: "Tracking",
    Capability.PSU_SAVE_RECALL: "Save/Recall",
    Capability.AWG_SYNC: "Sync output",
    Capability.AWG_JDS6600_PROTOCOL: "DDS protocol",
    Capability.AWG_INDEPENDENT_PARAMS: "Independent params",
    Capability.DMM_NPLC: "NPLC",
    Capability.DMM_DISPLAY_CONTROL: "Display control",
    Capability.DMM_DISPLAY_TEXT: "Display text",
    Capability.DMM_FETCH: "Fetch",
    Capability.DMM_BEEP: "Beep",
    Capability.DMM_RANGES: "Ranges",
    Capability.SCOPE_SCREENSHOT: "Screenshot",
    Capability.SCOPE_BUILTIN_AWG: "Built-in AWG",
    Capability.SCOPE_COUNTER: "Counter",
    Capability.SCOPE_DVM: "DVM",
    Capability.SCOPE_DISPLAY_CONTROL: "Display control",
    Capability.SCOPE_ACQUIRE_CONTROL: "Acquire control",
    Capability.SCOPE_CURSOR: "Cursor",
    Capability.SCOPE_MATH: "Math",
    Capability.SCOPE_RECORD: "Record",
    Capability.SCOPE_MASK: "Mask",
    Capability.SCOPE_LABEL: "Label",
    Capability.SCOPE_INVERT: "Invert",
    Capability.SCOPE_BWLIMIT: "BW limit",
    Capability.SCOPE_FORCE_TRIGGER: "Force trigger",
    Capability.SCOPE_WAIT_STOP: "Wait/stop",
    Capability.SCOPE_MEAS_FORCE: "Meas force",
    Capability.SCOPE_MEAS_CLEAR: "Meas clear",
}

# ANSI escape code stripper
_ANSI_RE = re.compile(r"\033\[[0-9;]*m")


def _strip_ansi(text: str) -> str:
    return _ANSI_RE.sub("", text)


def _caps_to_features(caps: Capability) -> str:
    """Convert a Capability flags value to a comma-separated feature string."""
    if caps == Capability.NONE:
        return "Basic"
    features = []
    for flag, label in CAPABILITY_LABELS.items():
        if flag in caps:
            features.append(label)
    return ", ".join(features) if features else "Basic"


# ---------------------------------------------------------------------------
# Part A: Generate instruments capability matrix
# ---------------------------------------------------------------------------
def _generate_instruments_page() -> str:
    lines = [
        "# Supported Instruments — Auto-Generated",
        "",
        "!!! info",
        "    This table is **auto-generated** from "
        "[`capabilities.py`](https://github.com/T-O-M-Tool-Oauto-Mationator/"
        "scpi-instrument-toolkit/blob/main/lab_instruments/repl/capabilities.py) "
        "at build time. It cannot go stale.",
        "",
        "| Model | Type | Interface | Key Features |",
        "|-------|------|-----------|--------------|",
    ]

    for class_name, caps in DRIVER_CAPABILITIES.items():
        # Skip mock entries
        if class_name.startswith("Mock"):
            continue
        if class_name not in DEVICE_INFO:
            raise KeyError(
                f"DEVICE_INFO is missing entry for '{class_name}'. "
                f"Add it to scripts/gen_ref_pages.py so auto-generated docs stay accurate."
            )
        display = DISPLAY_NAMES.get(class_name, class_name)
        info = DEVICE_INFO[class_name]
        features = _caps_to_features(caps)
        lines.append(f"| {display} | {info['type']} | {info['interface']} | {features} |")

    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Part B: Generate REPL command quick-reference
# ---------------------------------------------------------------------------
def _extract_subcommands(handler_class) -> list[str]:
    """Extract subcommand names from execute() by parsing its source."""
    try:
        source = inspect.getsource(handler_class.execute)
    except (TypeError, OSError):
        return []

    # Match patterns like: cmd_name == "xxx" or cmd_name in ("xxx", "yyy")
    eq_matches = re.findall(r'cmd_name\s*==\s*["\'](\w+)["\']', source)
    in_matches = re.findall(r"cmd_name\s+in\s+\(([^)]+)\)", source)

    cmds = list(dict.fromkeys(eq_matches))  # deduplicate, preserve order
    for match in in_matches:
        for name in re.findall(r'["\'](\w+)["\']', match):
            if name not in cmds:
                cmds.append(name)
    return cmds


def _capture_help(handler_instance, *args) -> str:
    """Capture stdout from _show_help()."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        handler_instance._show_help(*args)
    return _strip_ansi(buf.getvalue()).strip()


def _generate_repl_ref_page() -> str:
    from lab_instruments.repl.commands.awg import AwgCommand
    from lab_instruments.repl.commands.dmm import DmmCommand
    from lab_instruments.repl.commands.psu import PsuCommand
    from lab_instruments.repl.commands.scope import ScopeCommand
    from lab_instruments.repl.commands.smu import SmuCommand
    from lab_instruments.repl.context import ReplContext

    lines = [
        "# REPL Command Reference — Auto-Generated",
        "",
        "!!! info",
        "    This page is **auto-generated** from the REPL source code at build time. "
        "Subcommands are extracted from the command handlers, and help text is captured "
        "from the built-in `_show_help()` methods.",
        "",
        "For detailed usage guides with examples, see the individual instrument pages "
        "([PSU](../psu.md), [AWG](../awg.md), [DMM](../dmm.md), "
        "[Scope](../scope.md), [SMU](../smu.md)).",
        "",
    ]

    ctx = ReplContext()

    handlers = [
        ("PSU — Power Supply", PsuCommand, "psu"),
        ("AWG — Function Generator", AwgCommand, "awg"),
        ("DMM — Multimeter", DmmCommand, "dmm"),
        ("Scope — Oscilloscope", ScopeCommand, "scope"),
        ("SMU — Source Measure Unit", SmuCommand, "smu"),
    ]

    for title, handler_cls, prefix in handlers:
        lines.append(f"## {title}")
        lines.append("")

        # Extract subcommands
        subcmds = _extract_subcommands(handler_cls)
        if subcmds:
            lines.append("**Subcommands:** " + ", ".join(f"`{prefix} {c}`" for c in subcmds))
            lines.append("")

        # Capture help text
        instance = handler_cls(ctx)
        if handler_cls == PsuCommand:
            # PSU has two help variants
            lines.append("### Single-channel PSU")
            lines.append("")
            lines.append("```")
            lines.append(_capture_help(instance, True))
            lines.append("```")
            lines.append("")
            lines.append("### Multi-channel PSU")
            lines.append("")
            lines.append("```")
            lines.append(_capture_help(instance, False))
            lines.append("```")
        else:
            lines.append("```")
            lines.append(_capture_help(instance))
            lines.append("```")

        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Write generated files
# ---------------------------------------------------------------------------
with mkdocs_gen_files.open("generated/instruments.md", "w") as f:
    f.write(_generate_instruments_page())

with mkdocs_gen_files.open("generated/repl-ref.md", "w") as f:
    f.write(_generate_repl_ref_page())
