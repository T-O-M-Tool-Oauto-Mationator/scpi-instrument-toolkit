"""Help overlay screen - shows keybindings and command reference."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Static

_HELP_TEXT = """\
[bold underline]Keyboard Shortcuts[/bold underline]

  [bold cyan]Ctrl+L[/bold cyan]   Clear output log
  [bold cyan]Alt+D[/bold cyan]    Toggle device sidebar
  [bold cyan]Alt+E[/bold cyan]    Script editor
  [bold cyan]Alt+C[/bold cyan]    Raw SCPI console
  [bold cyan]Alt+I[/bold cyan]    Instrument detail panel
  [bold cyan]Alt+L[/bold cyan]    Safety limits panel
  [bold cyan]Alt+M[/bold cyan]    Measurements table
  [bold cyan]Alt+N[/bold cyan]    Notification center
  [bold cyan]Alt+O[/bold cyan]    Live monitor
  [bold cyan]Alt+P[/bold cyan]    Plot panel
  [bold cyan]Alt+S[/bold cyan]    Script browser
  [bold cyan]Alt+V[/bold cyan]    Variable inspector
  [bold cyan]Alt+W[/bold cyan]    Waveform viewer
  [bold cyan]Ctrl+P[/bold cyan]   Command palette
  [bold cyan]Ctrl+R[/bold cyan]   Retry last command
  [bold cyan]F1[/bold cyan]       This help screen
  [bold cyan]F2[/bold cyan]       Save screenshot (SVG)
  [bold cyan]F3[/bold cyan]       Connection wizard
  [bold cyan]Ctrl+Q[/bold cyan]   Quit

[bold underline]PSU Commands[/bold underline]

  psu set <voltage> [current]   Set output
  psu chan on|off               Toggle output
  psu meas [v|i]                Measure
  psu get                       Show setpoints

[bold underline]DMM Commands[/bold underline]

  dmm config <mode> [range]     Configure mode
  dmm read                      Take measurement
  dmm meas <mode>               Quick measure

[bold underline]Scope Commands[/bold underline]

  scope run | stop | single     Acquisition control
  scope autoset                 Auto-configure
  scope chan <n> on|off          Channel enable
  scope meas <ch> <type>        Measure parameter

[bold underline]AWG Commands[/bold underline]

  awg chan <ch> on|off           Output toggle
  awg wave <ch> <waveform>      Set waveform
  awg freq <ch> <Hz>            Set frequency
  awg amp <ch> <V>              Set amplitude

[bold underline]SMU Commands[/bold underline]

  smu on|off                    Output toggle
  smu set <V> [I_limit]         Set voltage
  smu meas [v|i|vi]             Measure
  smu compliance                Check compliance

[bold underline]General Commands[/bold underline]

  scan                          Discover instruments
  list                          Show connected devices
  use <name>                    Select active device
  status                        Show device status
  raw <scpi_cmd>                Send raw SCPI

[dim]Press Escape or F1 to close[/dim]
"""


class HelpScreen(ModalScreen[None]):
    """Modal overlay showing keybindings and command reference."""

    BINDINGS = [
        ("escape", "dismiss", "Close"),
        ("f1", "dismiss", "Close"),
    ]

    DEFAULT_CSS = """
    HelpScreen {
        align: center middle;
    }
    #help-dialog {
        width: 60;
        height: 80%;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
    }
    """

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="help-dialog"):
            yield Static(_HELP_TEXT, markup=True)

    def action_dismiss(self) -> None:
        self.dismiss(None)
