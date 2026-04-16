"""ReplContext: shared state container for the REPL."""

import os
import sys
import tempfile
from typing import Any

from .device_registry import DeviceRegistry
from .measurement_store import MeasurementStore


class ReplContext:
    """Shared state passed to all command handlers."""

    def __init__(self) -> None:
        self.registry = DeviceRegistry()
        self.measurements = MeasurementStore()

        # Script variables (values may be str, int, float, bool, or list)
        self.script_vars: dict[str, Any] = {}

        # Error handling
        self.command_had_error: bool = False
        self.exit_on_error: bool = False
        self.in_script: bool = False
        self.in_debugger: bool = False
        self.interrupt_requested: bool = False

        # Safety limits: (device_str, channel_or_none) -> {param_direction: value}
        self.safety_limits: dict[tuple[str, int | None], dict[str, float]] = {}
        # AWG channel state cache: (dev_name, channel) -> {vpp, offset}
        self.awg_channel_state: dict[tuple, dict[str, float | None]] = {}

        # Report state
        self.test_results: list = []
        self.report_title: str = "Lab Test Report"
        self.report_operator: str = ""
        self.report_screenshots: list = []

        # Script management
        self.scripts: dict[str, Any] = {}
        self.record_script: str | None = None

        # Directory overrides
        self._data_dir_override: str | None = None
        self._scripts_dir_override: str | None = None

        # Last configured instrument mode (for unit auto-detection)
        # Keyed by device name, e.g. {"dmm": "vdc", "psu": "v"}
        self.last_instrument_mode: dict[str, str] = {}

        # GUI callbacks (set by dispatcher when running inside the GUI)
        self.on_liveplot: Any | None = None  # (patterns, title, xlabel, ylabel) -> None

        # DMM text loop state
        self.dmm_text_loop_active: bool = False
        self.dmm_text_frames: list = []
        self.dmm_text_index: int = 0
        self.dmm_text_delay: float = 0.2
        self.dmm_text_last: float = 0.0

    def error(self, message: str) -> None:
        """Report an error message and set the error flag."""
        from lab_instruments.src.terminal import ColorPrinter

        self.command_had_error = True
        ColorPrinter.error(message)

    # ------------------------------------------------------------------
    # Directory helpers (ported from original repl.py)
    # ------------------------------------------------------------------

    @staticmethod
    def _probe_dir(d: str, cross_process: bool = True) -> bool:
        """Return True if *d* is writable and visible to other processes."""
        import contextlib
        import subprocess

        try:
            os.makedirs(d, exist_ok=True)
            if not os.path.isdir(d):
                return False
            probe = os.path.join(d, ".scpi_probe")
            with open(probe, "w") as f:
                f.write("ok")
            try:
                if cross_process and sys.platform == "win32":
                    result = subprocess.run(
                        ["cmd", "/c", "dir", "/b", probe],
                        capture_output=True,
                        timeout=5,
                    )
                    visible = result.returncode == 0
                elif cross_process:
                    result = subprocess.run(
                        ["sh", "-c", f"test -f '{probe}'"],
                        timeout=5,
                    )
                    visible = result.returncode == 0
                else:
                    visible = os.path.exists(probe)
            except Exception:
                visible = os.path.exists(probe)
            finally:
                with contextlib.suppress(Exception):
                    os.remove(probe)
            return visible
        except Exception:
            return False

    def get_scripts_dir(self) -> str:
        """Return a scripts directory that is genuinely writable."""
        from lab_instruments.src.terminal import ColorPrinter

        if self._scripts_dir_override:
            return self._scripts_dir_override

        override = os.environ.get("SCPI_SCRIPTS_DIR")
        if override:
            try:
                os.makedirs(override, exist_ok=True)
            except Exception as exc:
                raise RuntimeError(
                    f"SCPI_SCRIPTS_DIR is set to '{override}' but that directory cannot be created: {exc}"
                ) from exc
            return override

        subpath = os.path.join("scpi-instrument-toolkit", "scripts")
        candidates = []

        if sys.platform == "win32":
            docs = os.path.join(os.path.expanduser("~"), "Documents")
            candidates.append(("~/Documents", os.path.join(docs, subpath)))
            appdata = os.environ.get("APPDATA")
            if appdata:
                candidates.append(("APPDATA", os.path.join(appdata, subpath)))
        else:
            xdg = os.environ.get("XDG_CONFIG_HOME", os.path.join(os.path.expanduser("~"), ".config"))
            candidates.append(("XDG_CONFIG_HOME", os.path.join(xdg, subpath)))

        candidates.append(("~", os.path.join(os.path.expanduser("~"), subpath)))
        candidates.append(("tempdir", os.path.join(tempfile.gettempdir(), subpath)))

        attempted = []
        for label, d in candidates:
            if self._probe_dir(d, cross_process=True):
                if attempted:
                    ColorPrinter.warning(
                        f"Scripts directory: using '{d}' ({label}).\n"
                        f"  Primary location(s) failed cross-process check: {', '.join(attempted)}\n"
                        f"  To pin this path permanently: set SCPI_SCRIPTS_DIR={d}"
                    )
                return d
            attempted.append(f"'{d}'")

        for label, d in candidates:
            if self._probe_dir(d, cross_process=False):
                ColorPrinter.warning(
                    f"Scripts directory: cross-process check failed for all candidates\n"
                    f"  Using '{d}' ({label}) based on same-process writability."
                )
                return d

        raise RuntimeError(
            "Cannot find any writable directory for scripts.\n"
            f"  Tried: {', '.join(attempted)}\n"
            "  Set SCPI_SCRIPTS_DIR to a directory you can write to."
        )

    def script_file(self, name: str) -> str:
        """Return the full path to a script's .scpi file."""
        return os.path.join(self.get_scripts_dir(), f"{name}.scpi")

    def get_data_dir(self) -> str:
        """Return a directory for saving data files."""
        override = self._data_dir_override or os.environ.get("SCPI_DATA_DIR")
        if override:
            try:
                os.makedirs(override, exist_ok=True)
            except Exception as exc:
                raise RuntimeError(
                    f"SCPI_DATA_DIR is set to '{override}' but that directory cannot be created: {exc}"
                ) from exc
            return override

        subpath = os.path.join("scpi-instrument-toolkit", "data")
        candidates = []

        if sys.platform == "win32":
            docs = os.path.join(os.path.expanduser("~"), "Documents")
            candidates.append(os.path.join(docs, subpath))
        else:
            xdg = os.environ.get("XDG_CONFIG_HOME", os.path.join(os.path.expanduser("~"), ".config"))
            candidates.append(os.path.join(xdg, subpath))

        candidates.append(os.path.join(os.path.expanduser("~"), subpath))
        candidates.append(os.path.join(tempfile.gettempdir(), subpath))

        for d in candidates:
            try:
                os.makedirs(d, exist_ok=True)
                return d
            except Exception:
                continue

        fallback = os.path.join(tempfile.gettempdir(), subpath)
        os.makedirs(fallback, exist_ok=True)
        return fallback

    def load_scripts(self) -> dict[str, Any]:
        """Load all .scpi scripts from the user scripts directory."""
        from lab_instruments.src.terminal import ColorPrinter

        scripts = {}
        d = self.get_scripts_dir()
        try:
            for fname in sorted(os.listdir(d)):
                if fname.endswith(".scpi"):
                    name = fname[:-5]
                    with open(os.path.join(d, fname), encoding="utf-8") as f:
                        lines = [line.rstrip("\n") for line in f.readlines()]
                    while lines and not lines[-1].strip():
                        lines.pop()
                    scripts[name] = lines
        except Exception as exc:
            ColorPrinter.error(f"Failed to load scripts: {exc}")
        return scripts
