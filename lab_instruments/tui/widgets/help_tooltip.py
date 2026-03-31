"""Contextual help tooltip - shows usage hints as the user types commands."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label

_COMMAND_HINTS: dict[str, str] = {
    "psu": "psu set <V> [I] | psu chan on|off | psu meas [v|i] | psu get",
    "psu set": "psu set <voltage> [current_limit]",
    "psu chan": "psu chan on|off -- toggle output",
    "psu meas": "psu meas [v|i] -- measure voltage or current",
    "psu get": "psu get -- show voltage/current setpoints",
    "dmm": "dmm config <mode> | dmm read | dmm meas <mode>",
    "dmm config": "dmm config <mode> [range] [res] -- modes: vdc vac idc iac res fres freq",
    "dmm read": "dmm read -- take a measurement",
    "dmm meas": "dmm meas <mode> -- quick measure in given mode",
    "scope": "scope run|stop|single|autoset | scope chan <n> on|off | scope meas <ch> <type>",
    "scope chan": "scope chan <1-8> on|off",
    "scope meas": "scope meas <ch> <type> -- vpp vrms freq period amplitude",
    "scope autoset": "scope autoset -- auto-configure",
    "awg": "awg chan <ch> on|off | awg wave/freq/amp/offset <ch> <val>",
    "awg chan": "awg chan <1-2> on|off",
    "awg wave": "awg wave <ch> sine|square|ramp|pulse|noise|dc",
    "awg freq": "awg freq <ch> <Hz>",
    "awg amp": "awg amp <ch> <Vpp>",
    "awg offset": "awg offset <ch> <V>",
    "smu": "smu on|off | smu set <V> [I] | smu meas [v|i|vi] | smu compliance",
    "smu set": "smu set <voltage> [current_limit]",
    "smu meas": "smu meas [v|i|vi] -- measure voltage/current/both",
    "ev2300": "ev2300 info | read_word/write_word <addr> <reg> [val] | scan | probe <addr>",
    "log": "log <label> <value> [unit] [source] | log clear | log export",
    "log clear": "log clear -- erase all measurements",
    "plot": "plot [pattern ...] [--title text] [--save path.png]",
    "use": "use <device_name> -- select active instrument",
    "scan": "scan -- discover connected instruments",
    "list": "list -- show all connected instruments",
    "status": "status -- show active instrument status",
    "upper_limit": "upper_limit <device> <param> <value> -- set upper safety bound",
    "lower_limit": "lower_limit <device> <param> <value> -- set lower safety bound",
    "limit": "limit <device> [chan N] [voltage_upper=V] [current_upper=A] ...",
    "run": "run <script_name> -- execute a saved script",
    "record": "record start <name> | record stop -- record commands to script",
    "set": "set <var> = <value> -- assign a variable",
    "calc": "calc <label> = <expr> [unit=U] -- compute and log a value",
    "check": "check <label> <min> <max> | check <label> <expected> tol=N",
    "state": "state on|off|safe|reset [device] -- bulk instrument control",
    "raw": "raw <scpi_command> -- send raw SCPI to active instrument",
    "report": "report save [path] -- generate test report",
    "help": "help [command] -- show help",
}


def get_hint(text: str) -> str:
    """Return the most specific hint matching the typed text prefix."""
    if not text:
        return ""
    words = text.strip().lower().split()
    for n in range(len(words), 0, -1):
        key = " ".join(words[:n])
        if key in _COMMAND_HINTS:
            return _COMMAND_HINTS[key]
    return ""


class HelpTooltip(Widget):
    """Single-line widget showing context-sensitive help for the current input."""

    DEFAULT_CSS = """
    HelpTooltip {
        height: 1;
        dock: bottom;
        background: $panel;
        padding: 0 1;
    }
    HelpTooltip Label {
        width: 1fr;
        color: $text-muted;
        text-style: italic;
    }
    """

    text: reactive[str] = reactive("")

    def compose(self) -> ComposeResult:
        yield Label("", id="tooltip-label")

    def watch_text(self, text: str) -> None:
        self.query_one("#tooltip-label", Label).update(text)
