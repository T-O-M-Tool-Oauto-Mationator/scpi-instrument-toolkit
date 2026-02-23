#!/usr/bin/env python3
"""
Interactive REPL for ESET lab instruments.

Use to discover instruments, send commands, and place devices into known states.
"""

# Use NI-VISA backend for USB device support (pyvisa-py doesn't support USB-TMC)
# The discovery code has been updated with timeouts to prevent hanging
import os
import pathlib
import re
import sys
# os.environ['PYVISA_LIBRARY'] = '@py'  # Disabled - need NI-VISA for USB

import cmd
import json
import shlex
import subprocess
import tempfile
import threading
import time
import ast
import inspect
import traceback
import signal
import atexit
from typing import Dict, Any, Optional
try:
    from importlib.metadata import version as _pkg_version
    _REPL_VERSION = _pkg_version("scpi-instrument-toolkit")
except Exception:
    _REPL_VERSION = "unknown"

_GITHUB_REPO = "T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit"


def _check_for_updates(force=False):
    """Check GitHub for updates and tell the user what command to run.
    No automatic install — user must run the command manually.
    Returns True if an update is available, False otherwise."""
    if _REPL_VERSION == "unknown":
        if force:
            print("Running from source — skipping update check.")
        return False

    import urllib.request
    import json

    try:
        url = f"https://api.github.com/repos/{_GITHUB_REPO}/tags"
        req = urllib.request.Request(url, headers={"User-Agent": "scpi-instrument-toolkit"})
        with urllib.request.urlopen(req, timeout=2) as resp:
            tags = json.loads(resp.read())

        if not tags:
            return False

        # GitHub returns tags newest-first; first entry is the latest
        latest_tag = tags[0]["name"]        # e.g. "v0.1.70"
        latest = latest_tag.lstrip("v")     # e.g. "0.1.70"

        def _vtuple(v):
            return tuple(int(x) for x in v.split("."))

        if _vtuple(latest) <= _vtuple(_REPL_VERSION):
            if force:
                from lab_instruments.src.terminal import ColorPrinter as _CP
                _CP.success(f"Already up to date (v{_REPL_VERSION}).")
            return False

        # Update available — show the user the command to run
        from lab_instruments.src.terminal import ColorPrinter as _CP
        _CP.info(f"Update available: v{_REPL_VERSION} → v{latest}. To install, run:")
        git_url = f"git+https://github.com/{_GITHUB_REPO}.git@{latest_tag}#egg=scpi-instrument-toolkit"
        print(f'  pip install --upgrade "{git_url}"')
        return True

    except Exception:
        return False  # Network error or no internet — ignore silently

from lab_instruments import InstrumentDiscovery, ColorPrinter


DEVICE_NAMES = ("scope", "psu", "awg", "dmm", "dds")

PSU_CHANNEL_ALIASES = {
    # Unified channel numbers
    "1": "positive_6_volts_channel",
    "2": "positive_25_volts_channel",
    "3": "negative_25_volts_channel",
    # Internal names
    "positive_6_volts_channel": "positive_6_volts_channel",
    "positive_25_volts_channel": "positive_25_volts_channel",
    "negative_25_volts_channel": "negative_25_volts_channel",
}

AWG_WAVE_KEYS = {
    "freq": "frequency",
    "frequency": "frequency",
    "amp": "amplitude",
    "amplitude": "amplitude",
    "offset": "offset",
    "phase": "phase",
    "duty": "duty",
    "sym": "symmetry",
    "symmetry": "symmetry",
}

# Maps user-friendly waveform names → canonical SCPI abbreviations used by SCPI AWGs
AWG_WAVE_ALIASES = {
    "sine":     "SIN",
    "sin":      "SIN",
    "square":   "SQU",
    "squ":      "SQU",
    "ramp":     "RAMP",
    "triangle": "RAMP",
    "tri":      "RAMP",
    "pulse":    "PULS",
    "puls":     "PULS",
    "noise":    "NOIS",
    "nois":     "NOIS",
    "dc":       "DC",
    "arb":      "ARB",
    "prbs":     "PRBS",
}

DMM_MODE_ALIASES = {
    "vdc": "dc_voltage",
    "vac": "ac_voltage",
    "idc": "dc_current",
    "iac": "ac_current",
    "res": "resistance_2wire",
    "fres": "resistance_4wire",
    "freq": "frequency",
    "per": "period",
    "cont": "continuity",
    "diode": "diode",
}


class InstrumentRepl(cmd.Cmd):
    intro = f"ESET Instrument REPL v{_REPL_VERSION}. Type 'help' for commands."
    prompt = "eset> "

    def __init__(self):
        super().__init__()
        self.discovery = InstrumentDiscovery()
        self.devices: Dict[str, Any] = {}
        self.selected: Optional[str] = None
        self.scripts: Dict[str, Any] = self._load_scripts()
        self.measurements = []
        self._dmm_text_loop_active = False
        self._dmm_text_frames = []
        self._dmm_text_index = 0
        self._dmm_text_delay = 0.2
        self._dmm_text_last = 0.0
        self._device_override: Optional[str] = None  # set by default() for awg1, scope2, etc.
        self._cleanup_done = False
        self._script_vars: Dict[str, str] = {}  # runtime variables set by 'input' during scripts
        self._jerminator = False
        
        # Multi-line loop support (for/repeat blocks in interactive mode)
        self._in_loop = False  # True when collecting loop body lines
        self._loop_lines = []  # accumulate lines until 'end'
        self._loop_depth = 0  # track nested depth
        self._loop_header = ""  # the "for" or "repeat" line
        
        # Error handling mode (set -e / set +e)
        self._exit_on_error = False  # If True, stop script on command failure
        self._command_had_error = False  # Flag set when a command encounters an error
        self._in_script = False  # Flag to track if we're running a script
        self._interrupt_requested = False  # Flag set when Ctrl+C is pressed
        self._should_exit = False  # Flag to signal that we should exit the REPL

        # Save terminal state so we can restore it on any exit path
        self._term_fd = None
        self._term_settings = None
        try:
            import termios
            fd = sys.stdin.fileno()
            self._term_fd = fd
            self._term_settings = termios.tcgetattr(fd)
        except Exception:
            pass  # Windows or non-tty stdin — no-op

        # Register cleanup handlers before starting the background scan so
        # Ctrl+C is handled correctly even while discovery is in progress.
        atexit.register(self._cleanup_on_exit)
        signal.signal(signal.SIGINT, self._cleanup_on_interrupt)
        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, self._cleanup_on_interrupt)

        # Kick off discovery in the background so the REPL prompt appears
        # immediately.  Commands that need devices call _wait_for_scan() first.
        self._scan_done = threading.Event()
        self._scan_thread = threading.Thread(
            target=self._background_scan, daemon=True, name="scpi-scan"
        )
        ColorPrinter.info("Scanning for instruments in background — type 'scan' to wait for results.")
        self._scan_thread.start()

    def _background_scan(self):
        """Run discovery + startup safety check in a background thread."""
        try:
            self.scan()
            if self.devices:
                ColorPrinter.success(f"\nScan complete: found {len(self.devices)} device(s).")
            else:
                ColorPrinter.warning(f"\nScan complete: no instruments found.")
            # Put all discovered instruments into a safe/off state on startup
            if self.devices:
                try:
                    ColorPrinter.info("Setting all instruments to safe state...")
                    self._safe_all()
                except Exception as exc:
                    ColorPrinter.error(f"Error during startup safety check: {exc}")
        except Exception as exc:
            ColorPrinter.error(f"\nScan failed: {exc}")
        finally:
            self._scan_done.set()
            # Reprint the prompt so the user sees it after the scan message
            sys.stdout.write(self.prompt)
            sys.stdout.flush()

    def _error(self, message):
        """Report an error message and set the error flag for set -e handling."""
        self._command_had_error = True
        ColorPrinter.error(message)

    def _wait_for_scan(self):
        """Block until the background scan finishes. Prints a one-time notice."""
        if not self._scan_done.is_set():
            ColorPrinter.info("Waiting for instrument scan to finish...")
            self._scan_done.wait()

    def _restore_terminal(self):
        """Restore terminal settings saved at startup (no-op on Windows)."""
        try:
            if self._term_settings is not None:
                import termios
                termios.tcsetattr(self._term_fd, termios.TCSADRAIN, self._term_settings)
        except Exception:
            pass

    def cmdloop(self, intro=None):
        """Override cmdloop to catch KeyboardInterrupt without exiting the REPL."""
        if intro is not None:
            self.intro = intro
        if self.intro:
            print(self.intro)
        self._wait_for_scan()
        stop = None
        try:
            while not stop and not self._should_exit:
                try:
                    if self.cmdqueue:
                        line = self.cmdqueue.pop(0)
                    else:
                        if self.use_rawinput:
                            try:
                                line = input(self.prompt)
                            except EOFError:
                                line = 'EOF'
                        else:
                            self.lastcmd = ''
                            line = self.stdin.readline()
                            if not len(line):
                                line = 'EOF'
                            else:
                                line = line.rstrip('\r\n')
                    line = self.precmd(line)
                    stop = self.onecmd(line)
                    line = self.postcmd(stop, line)
                except KeyboardInterrupt:
                    # Don't exit REPL on Ctrl+C, just print a message and continue
                    if self._in_script:
                        ColorPrinter.warning("Script interrupted by user")
                    else:
                        print()  # Just newline for interactive mode
                    self._in_script = False
                    self._interrupt_requested = False  # Reset for next command
        finally:
            if self._should_exit:
                print("\nGoodbye!")
                self._restore_terminal()
            self.postloop()

    def _cleanup_on_exit(self):
        """Called automatically on normal program exit (via atexit)."""
        self._wait_for_scan()
        if not self._cleanup_done and self.devices:
            self._cleanup_done = True
            ColorPrinter.warning("\n=== Shutting down instruments safely ===")
            try:
                self._safe_all()
            except Exception as exc:
                ColorPrinter.error(f"Error during cleanup: {exc}")
        self._restore_terminal()

    def _cleanup_on_interrupt(self, signum, frame):
        """Called when Ctrl+C or termination signal is received."""
        self._interrupt_requested = True
        
        # Reset loop state if in a multi-line block
        if self._in_loop:
            self._in_loop = False
            self._loop_lines = []
            self._loop_depth = 0
            self.prompt = "eset> "
            print("\n(cancelled loop block)")
        
        # Don't wait for the scan thread on interrupt — if the user is Ctrl+C-ing
        # during a long scan, just cancel it and exit cleanly.
        self._scan_done.set()  # unblock any _wait_for_scan callers
        if not self._cleanup_done and self.devices:
            self._cleanup_done = True
            ColorPrinter.warning("\n\n=== Interrupted! Shutting down instruments safely ===")
            try:
                self._safe_all()
            except Exception as exc:
                ColorPrinter.error(f"Error during cleanup: {exc}")
        
        # If running a script, raise KeyboardInterrupt so the script can stop
        if self._in_script:
            raise KeyboardInterrupt
        
        # If at REPL level, signal that we should exit (without calling sys.exit)
        self._should_exit = True

    # --------------------------
    # Core helpers
    # --------------------------
    def scan(self):
        self.devices = self.discovery.scan(verbose=True)
        if self.selected not in self.devices:
            self.selected = None

    def _get_device(self, name: Optional[str]) -> Optional[Any]:
        self._wait_for_scan()
        if not self.devices:
            ColorPrinter.warning("No instruments connected. Run 'scan' first.")
            self._command_had_error = True
            return None

        if name is None:
            if self.selected is None:
                ColorPrinter.warning("No active instrument. Use 'use <name>'.")
                self._command_had_error = True
                return None
            return self.devices.get(self.selected)

        if name not in self.devices:
            ColorPrinter.warning(
                f"Unknown instrument '{name}'. Available: {list(self.devices.keys())}"
            )
            self._command_had_error = True
            return None
        return self.devices.get(name)

    def _resolve_device_type(self, device_type: str) -> Optional[str]:
        """
        Resolve a generic device type to a specific device instance.

        Discovers candidates dynamically by matching device names against the
        pattern ^<type>\\d*$ so awg, awg1, awg2, scope, scope1, psu, dmm, etc.
        all work.  If a specific device was pre-selected via default() routing
        (e.g. the user typed 'awg1 wave ...'), _device_override is used directly.

        Returns the assigned device name string, or None if not found.
        """
        self._wait_for_scan()
        # If a specific device was pre-selected by default() routing, use it directly
        if self._device_override and self._device_override in self.devices:
            return self._device_override

        # Build candidate list dynamically: names matching ^<type>\d*$
        pattern = re.compile(rf'^{re.escape(device_type)}\d*$')
        candidates = [name for name in self.devices if pattern.match(name)]

        # Legacy: 'awg' command also matches old 'dds' key (JDS6600)
        if device_type == 'awg' and 'dds' in self.devices and 'dds' not in candidates:
            candidates.append('dds')

        if not candidates:
            self._error(f"No {device_type.upper()} found. Run 'scan' first.")
            return None

        if len(candidates) == 1:
            return candidates[0]

        # Multiple devices — if the currently selected instrument is one of the
        # candidates, use it automatically (respects 'use <name>' selection).
        if self.selected and self.selected in candidates:
            return self.selected

        # No active selection matches — require explicit naming
        ColorPrinter.warning(
            f"Multiple {device_type.upper()}s found: {candidates}. "
            f"Use explicit name, e.g. '{candidates[0]}'."
        )
        return None

    def _parse_args(self, arg):
        try:
            return shlex.split(arg)
        except ValueError as exc:
            ColorPrinter.error(f"Parse error: {exc}")
            return []

    def _channels_for_device(self, dev, base_type: str):
        """Return the list of channel numbers for a device, or None if not applicable."""
        if hasattr(dev, 'CHANNEL_MAP'):
            return sorted(dev.CHANNEL_MAP.keys())
        if base_type == 'scope':
            return list(range(1, getattr(dev, 'num_channels', 4) + 1))
        if base_type == 'psu':
            if 'E3631A' in type(dev).__name__:
                return [1, 2, 3]
            return [1]
        if 'JDS6600' in type(dev).__name__:
            return [1, 2]
        return None

    @staticmethod
    def _probe_dir(d, cross_process=True):
        """Return True if *d* is writable and (when cross_process=True) visible to
        other processes.

        On managed/school Windows machines, %APPDATA% writes may be silently
        redirected to a shadow copy that only the Python process can see.  We
        detect this by asking cmd to list the sentinel file with `dir /b` — a
        simpler and more reliable command than `if exist ... (echo)`.

        If the subprocess check itself fails (cmd unavailable, timeout, etc.) we
        fall back to a same-process os.path.exists() check so the probe never
        prevents the tool from starting on machines where spawning cmd is restricted.
        """
        try:
            os.makedirs(d, exist_ok=True)
            if not os.path.isdir(d):
                return False
            probe = os.path.join(d, ".scpi_probe")
            with open(probe, "w") as f:
                f.write("ok")
            try:
                if cross_process and sys.platform == "win32":
                    # `dir /b <file>` exits 0 if the file is visible to cmd,
                    # non-zero if not — simpler and more portable than `if exist`.
                    result = subprocess.run(
                        ["cmd", "/c", "dir", "/b", probe],
                        capture_output=True, timeout=5,
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
                # Subprocess unavailable or timed out — degrade gracefully
                visible = os.path.exists(probe)
            finally:
                try:
                    os.remove(probe)
                except Exception:
                    pass
            return visible
        except Exception:
            return False

    def _get_scripts_dir(self):
        """Return a scripts directory that is genuinely writable on this machine.

        Tries a prioritised candidate list so the tool works on managed school/
        company Windows machines where %APPDATA% writes may be silently redirected
        by filesystem virtualisation (invisible to Explorer and other processes).

        Override via the SCPI_SCRIPTS_DIR environment variable to pin a specific
        location.

        Falls back to same-process checks if the cross-process subprocess probe
        rejects every candidate, so the tool always starts even on locked-down
        machines where spawning cmd is restricted.
        """
        # 1. Explicit user override — respected unconditionally
        override = os.environ.get("SCPI_SCRIPTS_DIR")
        if override:
            try:
                os.makedirs(override, exist_ok=True)
            except Exception as exc:
                raise RuntimeError(
                    f"SCPI_SCRIPTS_DIR is set to '{override}' but that directory "
                    f"cannot be created: {exc}"
                ) from exc
            return override

        # 2. Build a prioritised candidate list
        subpath = os.path.join("scpi-instrument-toolkit", "scripts")
        candidates = []

        if sys.platform == "win32":
            # On managed/school Windows machines %APPDATA% is commonly virtualised:
            # Python sees a shadow copy while Explorer and every other process see
            # a different filesystem.  ~/Documents is almost never virtualised, so
            # try it FIRST.  APPDATA is kept as a secondary option for unmanaged
            # machines where it is the conventional config location.
            docs = os.path.join(os.path.expanduser("~"), "Documents")
            candidates.append(("~/Documents", os.path.join(docs, subpath)))
            appdata = os.environ.get("APPDATA")
            if appdata:
                candidates.append(("APPDATA", os.path.join(appdata, subpath)))
        else:
            xdg = os.environ.get("XDG_CONFIG_HOME",
                                 os.path.join(os.path.expanduser("~"), ".config"))
            candidates.append(("XDG_CONFIG_HOME", os.path.join(xdg, subpath)))

        # Common final fallbacks for both platforms
        candidates.append(("~", os.path.join(os.path.expanduser("~"), subpath)))
        candidates.append(("tempdir",
                           os.path.join(tempfile.gettempdir(), subpath)))

        # Pass 1: cross-process probe (detects APPDATA virtualisation)
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

        # Pass 2: if every cross-process probe failed (cmd restricted / policy),
        # fall back to same-process writability check and warn the user.
        for label, d in candidates:
            if self._probe_dir(d, cross_process=False):
                ColorPrinter.warning(
                    f"Scripts directory: cross-process check failed for all candidates\n"
                    f"  (cmd may be restricted on this machine).\n"
                    f"  Using '{d}' ({label}) based on same-process writability.\n"
                    f"  If scripts don't open in Notepad, set SCPI_SCRIPTS_DIR to a path\n"
                    f"  outside of AppData (e.g. your Desktop or a USB drive)."
                )
                return d

        raise RuntimeError(
            "Cannot find any writable directory for scripts.\n"
            f"  Tried: {', '.join(attempted)}\n"
            "  Set SCPI_SCRIPTS_DIR to a directory you can write to."
        )

    def _script_file(self, name):
        """Return the full path to a script's .scpi file."""
        return os.path.join(self._get_scripts_dir(), f"{name}.scpi")

    def _load_scripts(self):
        """Load all .scpi scripts from the user scripts directory."""
        scripts = {}
        d = self._get_scripts_dir()
        try:
            for fname in sorted(os.listdir(d)):
                if fname.endswith(".scpi"):
                    name = fname[:-5]
                    with open(os.path.join(d, fname), "r", encoding="utf-8") as f:
                        lines = [line.rstrip("\n") for line in f.readlines()]
                    while lines and not lines[-1].strip():
                        lines.pop()
                    scripts[name] = lines
        except Exception as exc:
            ColorPrinter.error(f"Failed to load scripts: {exc}")

        return scripts

    def _save_scripts(self):
        """Save all scripts as individual .scpi files."""
        for name in self.scripts:
            self._save_script(name)

    def _save_script(self, name):
        """Save a single script to its .scpi file."""
        try:
            script_path = self._script_file(name)
            lines = self.scripts[name]
            with open(script_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
                if lines:
                    f.write("\n")
            # Verify the file actually landed on disk
            if not os.path.exists(script_path):
                scripts_dir = os.path.dirname(script_path)
                ColorPrinter.error(
                    f"Script '{name}' was written but '{script_path}' does not exist afterwards.\n"
                    f"  Scripts dir exists: {os.path.isdir(scripts_dir)}\n"
                    f"  Scripts dir path:   '{scripts_dir}'"
                )
        except Exception as exc:
            try:
                scripts_dir = self._get_scripts_dir()
                dir_exists = os.path.isdir(scripts_dir)
            except Exception:
                scripts_dir = "<unavailable>"
                dir_exists = False
            ColorPrinter.error(
                f"Failed to save script '{name}': {exc}\n"
                f"  Scripts dir: '{scripts_dir}' (exists={dir_exists})"
            )
    
    def _edit_script_in_editor(self, name, current_lines):
        if os.name == "nt":
            # Non-blocking on Windows: save to the real .scpi file and open it.
            # IMPORTANT: create the parent directory BEFORE attempting any write so
            # that _save_script() never races against a non-existent directory.
            path = pathlib.Path(self._script_file(name))
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
                if not path.parent.is_dir():
                    raise OSError(f"Directory '{path.parent}' does not exist after mkdir")
            except Exception as exc:
                ColorPrinter.error(
                    f"Cannot create scripts directory '{path.parent}': {exc}\n"
                    f"  Check that APPDATA is set and the drive is writable."
                )
                return None
            self.scripts[name] = list(current_lines)
            self._save_script(name)
            # Guarantee the file exists on disk even if _save_script silently failed
            try:
                path.touch(exist_ok=True)
            except Exception as exc:
                ColorPrinter.error(f"Cannot create script file '{path}': {exc}")
                return None
            if not path.exists():
                ColorPrinter.error(
                    f"Script file '{path}' still does not exist after touch — "
                    f"the filesystem may be read-only or the path is blocked."
                )
                return None
            self._open_file_nonblocking(str(path))
            ColorPrinter.info(f"Opened '{path}' — edit and save it, then run: script load")
            return None  # signals callers to skip their own save/success message
        editor = os.environ.get("EDITOR")
        if not editor:
            editor = "nano"
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", delete=False, suffix=".repl", encoding="utf-8", newline="\n"
            ) as handle:
                tmp_path = handle.name
                handle.write(f"# Script: {name}\n")
                handle.write("# Syntax: set <var> <val>  |  ${var}  |  repeat <n> ... end  |  for <var> v1 v2 ... end  |  call <name>\n")
                handle.write("#\n")
                for line in current_lines:
                    handle.write(f"{line}\n")
            try:
                subprocess.run([editor, tmp_path])
            except FileNotFoundError:
                ColorPrinter.error(f"Editor '{editor}' not found. Set $EDITOR to a valid editor.")
                return list(current_lines)
            with open(tmp_path, "r", encoding="utf-8") as handle:
                lines = [line.rstrip("\n") for line in handle.readlines()]
            # Strip comment header lines added by this editor
            result = []
            for line in lines:
                stripped = line.strip()
                if stripped.startswith("# Script:") or stripped.startswith("# Syntax:") or stripped == "#":
                    continue
                result.append(line)
            return result
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass

    def _open_file_nonblocking(self, path):
        if os.name == "nt":
            os.startfile(path)
            return
        editor = os.environ.get("EDITOR")
        if editor:
            subprocess.Popen([editor, path])
        else:
            subprocess.Popen(["xdg-open", path])

    def _is_help(self, args):
        if not args:
            return False
        return args[-1].lower() in ("help", "-h", "--help")

    def _strip_help(self, args):
        if self._is_help(args):
            return args[:-1], True
        return args, False

    def _parse_channels(self, ch_str, max_ch=4):
        """Parse a channel string into a list of ints.
        '1' / 'ch1' → [1];  'all' → [1 .. max_ch]."""
        s = str(ch_str).lower().strip()
        if s == "all":
            return list(range(1, max_ch + 1))
        if s.startswith("ch"):
            s = s[2:]
        return [int(s)]

    def _print_usage(self, lines):
        for line in lines:
            print(line)

    def _print_colored_usage(self, lines):
        """Print colorful usage help for a command."""
        for line in lines:
            if line.strip().startswith("#"):
                # Section headers
                ColorPrinter.header(line.strip("# ").strip())
            elif line.strip().startswith("-"):
                # Notes and examples in yellow
                print(f"{ColorPrinter.YELLOW}{line}{ColorPrinter.RESET}")
            elif line.strip() and not line.startswith(" "):
                # Top-level command line — first word (command name) cyan, rest plain
                parts = line.split(" ", 1)
                if len(parts) == 2:
                    print(f"{ColorPrinter.CYAN}{parts[0]}{ColorPrinter.RESET} {parts[1]}")
                else:
                    print(f"{ColorPrinter.CYAN}{line}{ColorPrinter.RESET}")
            else:
                # Indented / blank lines
                print(line)

    def _stop_dmm_text_loop(self):
        self._dmm_text_loop_active = False
        self._dmm_text_frames = []
        self._dmm_text_index = 0
        self._dmm_text_last = 0.0

    def _start_dmm_text_loop(self, message, width=12, delay=0.2, pad=4):
        text = str(message)
        width = max(1, int(width))
        pad = max(1, int(pad))
        spacer = " " * pad
        window_text = text + spacer
        cycle_text = window_text + window_text
        frames = []
        for start in range(len(window_text)):
            frames.append(cycle_text[start : start + width])
        if not frames:
            frames = [text[:width]]
        self._dmm_text_frames = frames
        self._dmm_text_index = 0
        self._dmm_text_delay = float(delay)
        self._dmm_text_last = 0.0
        self._dmm_text_loop_active = True

    def _tick_dmm_text_loop(self, force=False):
        if not self._dmm_text_loop_active or not self._dmm_text_frames:
            return
        now = time.time()
        if not force and (now - self._dmm_text_last) < self._dmm_text_delay:
            return
        dev = self._get_device("dmm")
        if not dev:
            return
        frame = self._dmm_text_frames[self._dmm_text_index]
        self._dmm_text_index = (self._dmm_text_index + 1) % len(self._dmm_text_frames)
        self._dmm_text_last = now
        try:
            dev.display_text(frame)
        except Exception:
            self._stop_dmm_text_loop()

    def _record_measurement(self, label, value, unit="", source=""):
        self.measurements.append(
            {
                "label": label,
                "value": value,
                "unit": unit,
                "source": source,
            }
        )

    def _safe_eval(self, expr, names):
        allowed_funcs = {"abs": abs, "min": min, "max": max, "round": round}

        def _eval(node):
            if isinstance(node, ast.Expression):
                return _eval(node.body)
            if isinstance(node, ast.Constant):
                if isinstance(node.value, (int, float)):
                    return node.value
                raise ValueError("Only numeric constants are allowed.")
            if isinstance(node, ast.Name):
                if node.id in names:
                    return names[node.id]
                if node.id in allowed_funcs:
                    return allowed_funcs[node.id]
                raise ValueError(f"Unknown name '{node.id}'.")
            if isinstance(node, ast.BinOp):
                left = _eval(node.left)
                right = _eval(node.right)
                if isinstance(node.op, ast.Add):
                    return left + right
                if isinstance(node.op, ast.Sub):
                    return left - right
                if isinstance(node.op, ast.Mult):
                    return left * right
                if isinstance(node.op, ast.Div):
                    return left / right
                if isinstance(node.op, ast.Pow):
                    return left ** right
                if isinstance(node.op, ast.Mod):
                    return left % right
                raise ValueError("Operator not allowed.")
            if isinstance(node, ast.UnaryOp):
                operand = _eval(node.operand)
                if isinstance(node.op, ast.UAdd):
                    return +operand
                if isinstance(node.op, ast.USub):
                    return -operand
                raise ValueError("Unary operator not allowed.")
            if isinstance(node, ast.Subscript):
                value = _eval(node.value)
                if not isinstance(value, dict):
                    raise ValueError("Subscript base must be a dict.")
                if isinstance(node.slice, ast.Constant):
                    key = node.slice.value
                elif isinstance(node.slice, ast.Name):
                    key = node.slice.id
                else:
                    key = _eval(node.slice)
                return value[key]
            if isinstance(node, ast.Call):
                func = _eval(node.func)
                args = [_eval(arg) for arg in node.args]
                if func in allowed_funcs.values():
                    return func(*args)
                raise ValueError("Function not allowed.")
            raise ValueError("Expression not allowed.")

        parsed = ast.parse(expr, mode="eval")
        return _eval(parsed)

    def _substitute_vars(self, text, variables):
        result = text
        for name, value in variables.items():
            result = result.replace(f"${{{name}}}", str(value))
        return result

    def _expand_script_lines(self, lines, variables, depth=0):
        if depth > 10:
            ColorPrinter.error("Maximum script call depth (10) exceeded.")
            return []
        expanded = []
        idx = 0
        while idx < len(lines):
            raw_line = lines[idx].strip()
            idx += 1
            if not raw_line or raw_line.startswith("#"):
                continue
            tokens = shlex.split(raw_line)
            if not tokens:
                continue
            head = tokens[0].lower()
            if head == "set" and len(tokens) >= 2:
                # Handle set -e / set +e (error mode)
                if len(tokens) == 2 and tokens[1] in ("-e", "+e"):
                    if tokens[1] == "-e":
                        self._exit_on_error = True
                        ColorPrinter.info("Exit on error enabled")
                    else:  # +e
                        self._exit_on_error = False
                        ColorPrinter.info("Exit on error disabled")
                    continue
                # Handle regular set <varname> <value>
                if len(tokens) >= 3:
                    key = tokens[1]
                    raw_val = self._substitute_vars(" ".join(tokens[2:]), variables)
                    try:
                        num_vars = {}
                        for k, v in variables.items():
                            try:
                                num_vars[k] = float(v)
                            except (TypeError, ValueError):
                                pass
                        result = self._safe_eval(raw_val, num_vars)
                        variables[key] = str(result)
                    except Exception:
                        variables[key] = raw_val
                    continue
            if head == "call" and len(tokens) >= 2:
                script_name = tokens[1]
                if script_name not in self.scripts:
                    ColorPrinter.error(f"call: script '{script_name}' not found.")
                    continue
                call_params = dict(variables)
                for token in tokens[2:]:
                    if "=" in token:
                        k, v = token.split("=", 1)
                        call_params[k] = self._substitute_vars(v, variables)
                expanded.extend(self._expand_script_lines(self.scripts[script_name], call_params, depth + 1))
                continue
            if head == "repeat" and len(tokens) >= 2:
                try:
                    count = int(tokens[1])
                except ValueError:
                    ColorPrinter.error(f"repeat: expected integer count, got '{tokens[1]}'")
                    continue
                block = []
                depth_inner = 1
                while idx < len(lines):
                    line = lines[idx].strip()
                    idx += 1
                    if not line or line.startswith("#"):
                        continue
                    line_tokens = shlex.split(line)
                    if not line_tokens:
                        continue
                    if line_tokens[0].lower() in ("repeat", "for"):
                        depth_inner += 1
                    elif line_tokens[0].lower() == "end":
                        depth_inner -= 1
                        if depth_inner == 0:
                            break
                    block.append(line)
                for _ in range(count):
                    expanded.extend(self._expand_script_lines(block, dict(variables), depth))
                continue
            if head == "for" and len(tokens) >= 3:
                key = tokens[1]
                values = tokens[2:]
                block = []
                depth_inner = 1
                while idx < len(lines):
                    line = lines[idx].strip()
                    idx += 1
                    if not line or line.startswith("#"):
                        continue
                    line_tokens = shlex.split(line)
                    if not line_tokens:
                        continue
                    if line_tokens[0].lower() in ("repeat", "for"):
                        depth_inner += 1
                    elif line_tokens[0].lower() == "end":
                        depth_inner -= 1
                        if depth_inner == 0:
                            break
                    block.append(line)
                if "," in key:
                    keys = [name for name in key.split(",") if name]
                    for value in values:
                        parts = value.split(",")
                        if len(parts) != len(keys):
                            ColorPrinter.error("for: var list and value list length mismatch.")
                            break
                        local_vars = dict(variables)
                        for name, val in zip(keys, parts):
                            local_vars[name] = self._substitute_vars(val, variables)
                        expanded.extend(self._expand_script_lines(block, local_vars, depth))
                else:
                    for value in values:
                        local_vars = dict(variables)
                        local_vars[key] = self._substitute_vars(value, variables)
                        expanded.extend(self._expand_script_lines(block, local_vars, depth))
                continue
            if head == "end":
                continue
            expanded.append(self._substitute_vars(raw_line, variables))
        return expanded

    def _run_script_lines(self, lines):
        expanded = self._expand_script_lines(lines, {})
        self._in_script = True
        self._interrupt_requested = False
        try:
            for raw_line in expanded:
                raw_line = self._substitute_vars(raw_line, self._script_vars)
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                self._tick_dmm_text_loop()
                
                # Reset error flag before executing command
                self._command_had_error = False
                
                if self.onecmd(line):
                    return True
                
                # If exit-on-error is enabled and a command failed, stop the script
                if self._exit_on_error and getattr(self, '_command_had_error', False):
                    ColorPrinter.error(f"Script stopped due to error (set -e enabled)")
                    return True
        except KeyboardInterrupt:
            ColorPrinter.warning("Script interrupted by user")
        finally:
            self._in_script = False
            self._interrupt_requested = False
        return False

    def _onecmd_single(self, line):
        # Apply variable substitution using REPL variables
        line = self._substitute_vars(line, self._script_vars)
        
        tokens = self._parse_args(line)
        if len(tokens) >= 3 and tokens[0].lower() == "repeat":
            try:
                count = int(tokens[1])
            except ValueError:
                return super().onecmd(line)
            cmd_line = " ".join(tokens[2:])
            for _ in range(count):
                if super().onecmd(cmd_line):
                    return True
            return False

        # Expand 'all' channel token into one call per channel
        # e.g. "awg wave all sine freq=1000" → "awg wave 1 sine ..." + "awg wave 2 sine ..."
        all_indices = [i for i, t in enumerate(tokens) if t.lower() == 'all']
        if all_indices:
            cmd_token = tokens[0].lower() if tokens else ''
            base_type = re.sub(r'\d+$', '', cmd_token)
            if base_type in ('awg', 'scope', 'psu', 'dds'):
                dev = None
                if self._device_override and self._device_override in self.devices:
                    dev = self.devices[self._device_override]
                elif cmd_token in self.devices:
                    dev = self.devices[cmd_token]
                else:
                    pattern = re.compile(rf'^{re.escape(base_type)}\d*$')
                    for dname, d in self.devices.items():
                        if pattern.match(dname):
                            dev = d
                            break
                    if dev is None and base_type == 'awg' and 'dds' in self.devices:
                        dev = self.devices['dds']
                if dev is not None:
                    channels = self._channels_for_device(dev, base_type)
                    if channels:
                        all_idx = all_indices[0]
                        for ch in channels:
                            new_tokens = list(tokens)
                            new_tokens[all_idx] = str(ch)
                            if super().onecmd(' '.join(new_tokens)):
                                return True
                        return False

        return super().onecmd(line)

    def onecmd(self, line):
        # If we're collecting a loop body, accumulate lines until 'end'
        if self._in_loop:
            stripped = line.strip()
            if stripped.lower() == "end":
                self._loop_depth -= 1
                if self._loop_depth == 0:
                    # Execute the collected for/repeat block
                    self._execute_collected_loop()
                    return False
            else:
                # Track nested loops
                tokens = self._parse_args(stripped)
                if tokens and tokens[0].lower() in ("for", "repeat"):
                    self._loop_depth += 1
                self._loop_lines.append(line)
            return False
        
        # Check if this line starts a for/repeat block in interactive mode
        stripped = line.strip()
        tokens = self._parse_args(stripped)
        if tokens and tokens[0].lower() in ("for", "repeat"):
            # Enter multi-line mode
            self._in_loop = True
            self._loop_depth = 1
            self._loop_header = stripped
            self._loop_lines = []
            self.prompt = "  > "  # Indent prompt to show we're in a block
            ColorPrinter.info("(entering loop block - type 'end' to exit)")
            return False
        
        scan_line = line.replace(";", " ; ")
        tokens = self._parse_args(scan_line)
        if "repeat" in tokens or "repeatall" in tokens:
            try:
                if "repeatall" in tokens:
                    idx = tokens.index("repeatall")
                    repeat_all = True
                else:
                    idx = tokens.index("repeat")
                    repeat_all = False
                if idx + 2 < len(tokens) and "end" in tokens[idx + 2 :]:
                    end_idx = tokens.index("end", idx + 2)
                    count = int(tokens[idx + 1])
                    body_tokens = tokens[idx + 2 : end_idx]
                    body = " ".join(body_tokens).strip()
                    for _ in range(count):
                        if self.onecmd(body):
                            return True
                    remainder = tokens[end_idx + 1 :]
                    while remainder and remainder[0] == ";":
                        remainder = remainder[1:]
                    if remainder:
                        return self.onecmd(" ".join(remainder))
                    return False
                if repeat_all:
                    count = int(tokens[idx + 1])
                    cmd_line = " ".join(tokens[idx + 2 :])
                    for _ in range(count):
                        if self.onecmd(cmd_line):
                            return True
                    return False
            except (ValueError, IndexError):
                pass
        if len(tokens) >= 3 and tokens[0].lower() == "repeatall":
            try:
                count = int(tokens[1])
            except ValueError:
                return super().onecmd(line)
            cmd_line = " ".join(tokens[2:])
            for _ in range(count):
                if super().onecmd(cmd_line):
                    return True
            return False
        if ";" in line:
            should_exit = False
            for chunk in line.split(";"):
                cmd_line = chunk.strip()
                if not cmd_line:
                    continue
                if self._onecmd_single(cmd_line):
                    should_exit = True
                    break
            return should_exit
        return self._onecmd_single(line)

    def _execute_collected_loop(self):
        """Execute the for/repeat block that was collected interactively.
        
        Combines the loop header with the collected body lines and runs
        them through the same expansion logic as script files.
        """
        # Reset prompt before executing
        self.prompt = "eset> "
        self._in_loop = False
        
        # Combine the header with the collected body and 'end'
        all_lines = [self._loop_header] + self._loop_lines + ["end"]
        
        # Use the existing script expansion logic
        try:
            expanded = self._expand_script_lines(all_lines, {})
            for raw_line in expanded:
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                self._tick_dmm_text_loop()
                if self.onecmd(line):
                    return
        except KeyboardInterrupt:
            ColorPrinter.warning("Loop interrupted by user")
        except Exception as e:
            ColorPrinter.error(f"Loop execution error: {e}")
            traceback.print_exc()

    def _print_devices(self):
        if not self.devices:
            ColorPrinter.warning("No instruments connected.")
            return
        C = ColorPrinter.CYAN
        G = ColorPrinter.GREEN
        Y = ColorPrinter.YELLOW
        B = ColorPrinter.BOLD
        R = ColorPrinter.RESET
        for name, dev in self.devices.items():
            if name == self.selected:
                marker = f"{G}*{R}"
                name_str = f"{G}{B}{name}{R}"
            else:
                marker = " "
                name_str = f"{C}{name}{R}"
            print(f" {marker} {name_str}: {Y}{dev.__class__.__name__}{R}")

    def _safe_all(self):
        for name, dev in self.devices.items():
            try:
                # PSU devices (psu, psu1, psu2, ...)
                if name.startswith("psu"):
                    if hasattr(dev, 'disable_all_channels'):
                        dev.disable_all_channels()
                    elif hasattr(dev, 'enable_output'):
                        dev.enable_output(False)
                # AWG/DDS devices (awg, awg1, awg2, dds)
                elif name.startswith("awg") or name == "dds":
                    if hasattr(dev, 'disable_all_channels'):
                        dev.disable_all_channels()
                    elif hasattr(dev, 'enable_output'):
                        dev.enable_output(ch1=False, ch2=False)
                # Oscilloscope (scope, scope1, scope2, ...)
                elif name.startswith("scope"):
                    if hasattr(dev, 'stop'):
                        dev.stop()
                    if hasattr(dev, 'disable_all_channels'):
                        dev.disable_all_channels()
                    elif hasattr(dev, 'disable_channel'):
                        for ch in range(1, 5):
                            try:
                                dev.disable_channel(ch)
                            except Exception:
                                pass
                # DMM devices (dmm, dmm1, dmm2, ...)
                elif name.startswith("dmm"):
                    if hasattr(dev, 'reset'):
                        dev.reset()
                ColorPrinter.success(f"{name}: safe state applied")
            except Exception as exc:
                ColorPrinter.error(f"{name}: {exc}")

    def _reset_all(self):
        for name, dev in self.devices.items():
            try:
                dev.reset()
                ColorPrinter.success(f"{name}: reset")
            except Exception as exc:
                ColorPrinter.error(f"{name}: {exc}")

    def _off_all(self):
        for name, dev in self.devices.items():
            try:
                # PSU devices (psu, psu1, psu2, ...)
                if name.startswith("psu"):
                    if hasattr(dev, 'enable_output'):
                        dev.enable_output(False)
                        ColorPrinter.success(f"{name}: output disabled")
                # AWG/DDS devices (awg, awg1, awg2, dds)
                elif name.startswith("awg") or name == "dds":
                    if hasattr(dev, 'disable_all_channels'):
                        dev.disable_all_channels()
                        ColorPrinter.success(f"{name}: channels disabled")
                    elif hasattr(dev, 'enable_output'):
                        dev.enable_output(ch1=False, ch2=False)
                        ColorPrinter.success(f"{name}: outputs disabled")
                # Oscilloscope (scope, scope1, scope2, ...)
                elif name.startswith("scope"):
                    if hasattr(dev, 'stop'):
                        dev.stop()
                        ColorPrinter.success(f"{name}: acquisition stopped")
                    if hasattr(dev, 'disable_all_channels'):
                        dev.disable_all_channels()
                        ColorPrinter.success(f"{name}: channels disabled")
                    elif hasattr(dev, 'disable_channel'):
                        for ch in range(1, 5):
                            try:
                                dev.disable_channel(ch)
                            except Exception:
                                pass
                        ColorPrinter.success(f"{name}: all channels (1-4) disabled")
                # DMM devices (dmm, dmm1, dmm2, ...)
                elif name.startswith("dmm"):
                    if hasattr(dev, 'reset'):
                        dev.reset()
                        ColorPrinter.success(f"{name}: reset")
            except Exception as exc:
                ColorPrinter.error(f"{name}: {exc}")

    def _on_all(self):
        for name, dev in self.devices.items():
            try:
                # PSU devices (psu, psu1, psu2, ...)
                if name.startswith("psu"):
                    if hasattr(dev, 'enable_output'):
                        dev.enable_output(True)
                        ColorPrinter.success(f"{name}: output enabled")
                # AWG/DDS devices (awg, awg1, awg2, dds)
                elif name.startswith("awg") or name == "dds":
                    if hasattr(dev, 'enable_output'):
                        try:
                            dev.enable_output(ch1=True, ch2=True)
                        except TypeError:
                            dev.enable_output(1, True)
                            dev.enable_output(2, True)
                        ColorPrinter.success(f"{name}: outputs enabled")
                # Oscilloscope (scope, scope1, scope2, ...)
                elif name.startswith("scope"):
                    if hasattr(dev, 'enable_all_channels'):
                        dev.enable_all_channels()
                        ColorPrinter.success(f"{name}: channels enabled")
                # DMM devices - no "on" state, nothing to do
            except Exception as exc:
                ColorPrinter.error(f"{name}: {exc}")

    # --------------------------
    # General commands
    # --------------------------
    def do_scan(self, arg):
        "scan: discover and connect to instruments"
        args = self._parse_args(arg)
        if self._is_help(args):
            self._print_usage(["scan  # rescan and connect to instruments"])
            return
        if not self._scan_done.is_set():
            # Background startup scan still running — just wait for it
            ColorPrinter.info("Waiting for background scan to finish...")
            self._scan_done.wait()
        else:
            # Startup scan already done — run a fresh explicit rescan
            self.scan()
            if self.devices:
                ColorPrinter.success(f"Found {len(self.devices)} device(s).")
            else:
                ColorPrinter.warning("No instruments found.")

    def do_shawn(self, arg):
        "shawn: the only man who can stop jeremie"
        self._jerminator = False
        self._stop_dmm_text_loop()
        dev = self.devices.get("dmm")
        if dev:
            try:
                dev.clear_display()
            except Exception:
                pass
            try:
                dev.set_display(True)
            except Exception:
                pass
        ColorPrinter.success("Shawn has stopped sawing.")

    def do_version(self, arg):
        "version: show the scpi-instrument-toolkit version"
        ColorPrinter.info(f"scpi-instrument-toolkit v{_REPL_VERSION}")

    def do_clear(self, arg):
        "clear: clear the terminal screen"
        os.system('cls' if os.name == 'nt' else 'clear')

    def do_reload(self, arg):
        "reload: restart the REPL process to pick up changes to repl.py and lab_instruments"
        ColorPrinter.info("Disconnecting all instruments...")
        for dev in list(self.devices.values()):
            try:
                dev.disconnect()
            except Exception:
                pass

        ColorPrinter.success("Restarting process...")
        # sys.argv[0] may be an installed entry-point wrapper (e.g. Scripts\scpi-repl),
        # not a .py file Python can run directly. Fall back to -m in that case.
        argv0 = sys.argv[0]
        if os.path.isfile(argv0) and argv0.endswith('.py'):
            os.execv(sys.executable, [sys.executable] + sys.argv)
        else:
            os.execv(sys.executable, [sys.executable, '-m', 'lab_instruments.repl'] + sys.argv[1:])

    def do_list(self, arg):
        "list: show connected instruments"
        args = self._parse_args(arg)
        if self._is_help(args):
            self._print_usage(["list  # show connected instruments"])
            return
        self._print_devices()

    def do_use(self, arg):
        "use <name>: when multiple instruments of the same type are connected, set which one bare commands target"
        args = self._parse_args(arg)
        if self._is_help(args) or not args:
            self._print_colored_usage(
                [
                    "# USE — select active instrument",
                    "",
                    "use <name>",
                    "  - With one PSU connected, bare 'psu' commands work automatically.",
                    "  - With two PSUs (psu1, psu2), you must be explicit:",
                    "    - Either prefix every command:  psu1 set 5.0  /  psu2 set 12.0",
                    "    - Or pick one with 'use':  use psu1  then  psu set 5.0  (acts on psu1)",
                    "  - 'use' only affects bare commands — psu1/psu2 prefixes always work.",
                    "",
                    "  - example: use psu1   then: psu set 5.0   psu meas v",
                    "  - example: use dmm1   then: dmm meas vdc",
                ]
            )
            self._print_devices()
            return
        name = args[0]
        if name not in self.devices:
            ColorPrinter.warning(f"Unknown instrument '{name}'. Connected: {list(self.devices.keys())}")
            return
        self.selected = name
        ColorPrinter.success(f"Active: {name}  (bare commands now target this instrument)")

    def default(self, line):
        """Handle numbered device names like 'awg1', 'scope2', 'psu1', 'dmm3'."""
        parts = line.split(None, 1)
        cmd_token = parts[0]
        rest = parts[1] if len(parts) > 1 else ""

        if cmd_token in self.devices:
            # Strip trailing digits to get the base type ("awg1" → "awg")
            base_type = re.sub(r'\d+$', '', cmd_token)
            handler = getattr(self, f"do_{base_type}", None)
            if handler:
                self._device_override = cmd_token
                try:
                    handler(rest)
                finally:
                    self._device_override = None
                return

        # ---- Easter eggs ----
        normalized = line.strip().lower().rstrip("?").strip()

        if normalized == "who made these drivers":
            print(f"\033[91mYOU DID KING! 👑\033[0m")
            return

        if normalized in ("jeremie", "jhews"):
            self._jerminator = True
            def _jerminator_loop():
                msgs = ["FUCK JEREMIE"]
                i = 0
                while getattr(self, "_jerminator", False):
                    dev = self.devices.get("dmm")
                    if dev:
                        try:
                            dev.display_text(msgs[i % len(msgs)])
                        except Exception:
                            pass
                        try:
                            dev.beep()
                        except Exception:
                            pass
                    i += 1
                    time.sleep(0.5)
            t = threading.Thread(target=_jerminator_loop, daemon=True, name="jerminator")
            t.start()
            ColorPrinter.warning("FUCK YOU JEREMIE")
            return
        # ---- End easter eggs ----

        self._error(f"Unknown syntax: {line}")

    def do_idn(self, arg):
        "idn [name]: query *IDN? for selected or named instrument"
        args = self._parse_args(arg)
        if self._is_help(args):
            self._print_usage(
                [
                    "idn [name]",
                    "  - example: idn",
                    "  - example: idn dmm",
                ]
            )
            return
        name = args[0] if args else None
        dev = self._get_device(name)
        if not dev:
            return
        try:
            ColorPrinter.cyan(dev.query("*IDN?"))
        except Exception as exc:
            self._error(str(exc))

    def do_raw(self, arg):
        "raw [name] <scpi>: send raw SCPI; if ends with ?, query and print"
        args = self._parse_args(arg)
        args, help_flag = self._strip_help(args)
        if not args or help_flag:
            self._print_usage(
                [
                    "raw [name] <scpi>",
                    "  - example: raw *IDN?",
                    "  - example: raw scope MEASUrement:IMMed:VALue?",
                ]
            )
            return
        name = None
        if args[0] in self.devices:
            name = args[0]
            args = args[1:]
        dev = self._get_device(name)
        if not dev or not args:
            return
        cmd_str = " ".join(args)
        try:
            if cmd_str.strip().endswith("?"):
                ColorPrinter.cyan(dev.query(cmd_str))
            else:
                dev.send_command(cmd_str)
                ColorPrinter.success(f"Sent: {cmd_str}")
        except Exception as exc:
            self._error(str(exc))

    def do_state(self, arg):
        "state [safe|reset|list] or state <device> <safe|reset|on|off>"
        args = self._parse_args(arg)
        if self._is_help(args):
            self._print_usage(
                [
                    "state off                # outputs off for all devices",
                    "state on                 # outputs on for all devices",
                    "state safe               # safe state for all devices",
                    "state reset              # *RST for all devices",
                    "state <dev> on|off|safe|reset",
                    "state list",
                ]
            )
            return
        if not args or args[0] == "list":
            self._print_usage(
                [
                    "state off                # outputs off for all devices",
                    "state on                 # outputs on for all devices",
                    "state safe               # safe state for all devices",
                    "state reset              # *RST for all devices",
                    "state <dev> on|off|safe|reset",
                    "state list",
                ]
            )
            return

        if args[0] in ("safe", "reset", "off", "on"):
            if args[0] == "safe":
                self._safe_all()
            elif args[0] == "off":
                self._off_all()
            elif args[0] == "on":
                self._on_all()
            else:
                self._reset_all()
            return

        if len(args) < 2:
            ColorPrinter.warning("Usage: state <device> <safe|reset|on|off>")
            return

        name = args[0]
        state = args[1].lower()
        dev = self._get_device(name)
        if not dev:
            return

        try:
            if name.startswith("psu"):
                if state in ("safe", "off"):
                    dev.disable_all_channels()
                    ColorPrinter.success(f"{name}: output disabled")
                elif state == "on":
                    dev.enable_output(True)
                    ColorPrinter.success(f"{name}: output enabled")
                elif state == "reset":
                    dev.reset()
                    ColorPrinter.success(f"{name}: reset")
                else:
                    ColorPrinter.warning("PSU states: on, off, safe, reset")
            elif name.startswith("awg") or name == "dds":
                if state in ("safe", "off"):
                    dev.disable_all_channels()
                    ColorPrinter.success(f"{name}: outputs disabled")
                elif state == "on":
                    dev.enable_output(1, True)
                    dev.enable_output(2, True)
                    ColorPrinter.success(f"{name}: outputs enabled")
                elif state == "reset":
                    dev.reset()
                    ColorPrinter.success(f"{name}: reset")
                else:
                    ColorPrinter.warning("AWG states: on, off, safe, reset")
            elif name.startswith("scope"):
                if state in ("safe", "off"):
                    dev.disable_all_channels()
                    ColorPrinter.success(f"{name}: channels disabled")
                elif state == "on":
                    dev.enable_all_channels()
                    ColorPrinter.success(f"{name}: channels enabled")
                elif state == "reset":
                    dev.reset()
                    ColorPrinter.success(f"{name}: reset")
                else:
                    ColorPrinter.warning("Scope states: on, off, safe, reset")
            elif name.startswith("dmm"):
                if state in ("safe", "reset"):
                    dev.reset()
                    ColorPrinter.success(f"{name}: reset")
                else:
                    ColorPrinter.warning("DMM states: safe, reset")
        except Exception as exc:
            ColorPrinter.error(str(exc))

    def do_close(self, arg):
        "close: disconnect all instruments"
        args = self._parse_args(arg)
        if self._is_help(args):
            self._print_usage(["close  # disconnect all instruments"])
            return
        for name, dev in self.devices.items():
            try:
                dev.disconnect()
                ColorPrinter.success(f"{name}: disconnected")
            except Exception as exc:
                ColorPrinter.error(f"{name}: {exc}")
        self.devices = {}
        self.selected = None

    def do_status(self, arg):
        "status: show current selection"
        args = self._parse_args(arg)
        if self._is_help(args):
            self._print_usage(["status  # show current selection"])
            return
        if not self.devices:
            ColorPrinter.warning("No instruments connected.")
            return
        ColorPrinter.info(f"Selected: {self.selected}")
        self._print_devices()

    def do_sleep(self, arg):
        "sleep <duration>[us|ms|s|m]: pause between actions"
        args = self._parse_args(arg)
        args, help_flag = self._strip_help(args)
        if not args or help_flag:
            self._print_usage(
                [
                    "sleep <duration>[us|ms|s|m]",
                    "  - sleep 500ms   (500 milliseconds)",
                    "  - sleep 1.5     (1.5 seconds, default unit)",
                    "  - sleep 100us   (100 microseconds)",
                    "  - sleep 2m      (2 minutes)",
                ]
            )
            return
        raw = args[0].strip()
        _suffix_map = [("us", 1e-6), ("ms", 1e-3), ("min", 60.0), ("m", 60.0), ("s", 1.0)]
        delay = None
        label = raw
        for suffix, factor in _suffix_map:
            if raw.lower().endswith(suffix):
                try:
                    delay = float(raw[:-len(suffix)]) * factor
                    label = raw
                    break
                except ValueError:
                    pass
        if delay is None:
            try:
                delay = float(raw)
                label = f"{raw}s"
            except ValueError:
                ColorPrinter.warning(f"sleep: invalid duration '{raw}'. Examples: 0.5  500ms  100us  2m")
                return
        if delay < 0:
            ColorPrinter.warning("sleep expects a non-negative duration.")
            return
        ColorPrinter.info(f"Sleeping {label}...")
        end_time = time.time() + delay
        self._interrupt_requested = False
        while True:
            if self._interrupt_requested:
                print()
                return
            remaining = end_time - time.time()
            if remaining <= 0:
                break
            self._tick_dmm_text_loop()
            time.sleep(min(0.05, remaining))

    def do_wait(self, arg):
        "wait <duration>[us|ms|s|m]: alias for sleep"
        return self.do_sleep(arg)

    def do_print(self, arg):
        "print <message>: display a message (useful in scripts)"
        import builtins
        args = self._parse_args(arg)
        msg = " ".join(args) if args else ""
        builtins.print(f"{ColorPrinter.CYAN}{msg}{ColorPrinter.RESET}")

    def do_pause(self, arg):
        "pause [message]: wait for Enter (useful in scripts to prompt operator)"
        import builtins
        args = self._parse_args(arg)
        prompt = " ".join(args) if args else "Press Enter to continue..."
        builtins.input(f"{ColorPrinter.YELLOW}{prompt}{ColorPrinter.RESET} ")

    def do_input(self, arg):
        "input <varname> [prompt]: read a value from the user and store in ${varname} for use in scripts"
        import builtins
        args = self._parse_args(arg)
        if not args:
            ColorPrinter.warning("Usage: input <varname> [prompt]")
            return
        varname = args[0]
        prompt = " ".join(args[1:]) if len(args) > 1 else f"{varname}: "
        value = builtins.input(f"{ColorPrinter.YELLOW}{prompt}{ColorPrinter.RESET} ")
        self._script_vars[varname] = value
        ColorPrinter.success(f"${{{varname}}} = {value!r}")

    def do_set(self, arg):
        "set <varname> <expr>: define a variable for use in commands (e.g. set v 5.0)"
        args = self._parse_args(arg)
        if len(args) < 2:
            ColorPrinter.warning("Usage: set <varname> <expr>")
            if self._script_vars:
                ColorPrinter.info("Current variables:")
                for k, v in self._script_vars.items():
                    print(f"  {k} = {v}")
            return
        
        key = args[0]
        # Join the rest of arguments to handle expressions with spaces
        raw_val = " ".join(args[1:])
        
        # Perform substitution on the expression itself (e.g. set v2 ${v1} * 2)
        raw_val = self._substitute_vars(raw_val, self._script_vars)
        
        try:
            # Try to evaluate as math expression
            num_vars = {}
            for k, v in self._script_vars.items():
                try:
                    num_vars[k] = float(v)
                except (TypeError, ValueError):
                    pass
            result = self._safe_eval(raw_val, num_vars)
            self._script_vars[key] = str(result)
        except Exception:
            # Fallback to string literal
            self._script_vars[key] = raw_val
            
        ColorPrinter.success(f"{key} = {self._script_vars[key]}")

    def do_script(self, arg):
        "script <new|run|edit|list|rm|show|import|load|save> [args]: manage and run scripts"
        args = self._parse_args(arg)
        args, help_flag = self._strip_help(args)

        if not args or help_flag:
            self._print_colored_usage([
                "# SCRIPT",
                "",
                "script new <name>",
                "script run <name> [key=val ...]",
                "  - example: script run my_test voltage=5.0",
                "script edit <name>",
                "script list",
                "script rm <name>",
                "script show <name>",
                "script import <name> <path>",
                "  - import any text/.scpi file as a named script",
                "script load",
                "  - reload scripts from disk (picks up manual edits)",
                "script save",
                "  - show scripts directory",
                "",
                "# SCRIPT DIRECTIVES",
                "",
                "print <message>",
                "  - display a message to the operator",
                "pause [message]",
                "  - wait for operator to press Enter",
                "input <varname> [prompt]",
                "  - prompt operator for a value, store in ${varname}",
                "  - example: input voltage Enter PSU voltage:",
                "  - use ${varname} in subsequent lines to reference it",
                "set <varname> <expr>",
                "  - compute a value at script build time",
                "  - example: set v2 ${v1} * 2",
                "sleep <seconds>",
                "repeat <N>  ...  end",
                "for <var> <val1> <val2> ...  end",
                "call <name> [key=val ...]",
            ])
            return

        subcmd = args[0].lower()

        if subcmd == "new":
            if len(args) < 2:
                ColorPrinter.warning("Usage: script new <name>")
                return
            name = args[1]
            script_file = self._script_file(name)
            file_exists = os.path.exists(script_file)
            if not file_exists and name in self.scripts:
                # Stale in-memory entry with no backing file — discard it so
                # the user gets a clean new script instead of a false positive.
                del self.scripts[name]
            if file_exists:
                ColorPrinter.warning(f"Script '{name}' already exists — opening for edit. Use 'script rm {name}' first to start fresh.")
            lines = self._edit_script_in_editor(name, self.scripts.get(name, []))
            if lines is not None:
                self.scripts[name] = lines
                self._save_script(name)
                script_path = self._script_file(name)
                if os.path.exists(script_path):
                    ColorPrinter.success(f"Saved script '{name}' ({len(lines)} lines).")
                else:
                    try:
                        scripts_dir = self._get_scripts_dir()
                        dir_ok = os.path.isdir(scripts_dir)
                    except Exception:
                        scripts_dir = "<error retrieving path>"
                        dir_ok = False
                    ColorPrinter.error(
                        f"Script '{name}' could not be written to disk.\n"
                        f"  Expected path: '{script_path}'\n"
                        f"  Scripts dir:   '{scripts_dir}' (exists={dir_ok})\n"
                        f"  Check drive permissions or available disk space."
                    )

        elif subcmd == "run":
            if len(args) < 2:
                ColorPrinter.warning("Usage: script run <name> [key=val ...]")
                return
            name = args[1]
            
            # Hot-load: Reload from disk if file exists
            script_path = self._script_file(name)
            if os.path.exists(script_path):
                try:
                    with open(script_path, "r", encoding="utf-8") as f:
                        lines = [line.rstrip("\n") for line in f.readlines()]
                    while lines and not lines[-1].strip():
                        lines.pop()
                    self.scripts[name] = lines
                except Exception:
                    pass  # Keep existing memory version if read fails

            lines = self.scripts.get(name)
            if lines is None:
                ColorPrinter.warning(f"Script '{name}' not found.")
                return
            params = {}
            for token in args[2:]:
                if "=" in token:
                    key, value = token.split("=", 1)
                    params[key] = value
            
            # Use global variables, overridden by CLI parameters
            run_vars = self._script_vars.copy()
            run_vars.update(params)
            
            expanded = self._expand_script_lines(lines, run_vars)
            
            # Persist any variable changes from the script back to global state
            self._script_vars.update(run_vars)
            
            self._in_script = True
            try:
                for raw_line in expanded:
                    # Variables already substituted by expand, but onecmd_single might do it again
                    line = raw_line.strip()
                    if not line or line.startswith("#"):
                        continue
                    self._tick_dmm_text_loop()
                    
                    # Reset error flag before executing command
                    self._command_had_error = False
                    
                    if self.onecmd(line):
                        return True
                    
                    # If exit-on-error is enabled and a command failed, stop the script
                    if self._exit_on_error and getattr(self, '_command_had_error', False):
                        ColorPrinter.error(f"Script stopped due to error (set -e enabled)")
                        break  # Exit script loop but stay in REPL
            except KeyboardInterrupt:
                ColorPrinter.warning("Script interrupted by user")
            finally:
                self._in_script = False
            return False

        elif subcmd == "edit":
            if len(args) < 2:
                ColorPrinter.warning("Usage: script edit <name>")
                return
            name = args[1]
            if name not in self.scripts:
                ColorPrinter.warning(f"Script '{name}' not found.")
                return
            lines = self._edit_script_in_editor(name, self.scripts[name])
            if lines is not None:
                self.scripts[name] = lines
                self._save_script(name)
                ColorPrinter.success(f"Updated script '{name}' ({len(lines)} lines).")

        elif subcmd == "list":
            if not self.scripts:
                ColorPrinter.warning("No scripts saved.")
                return
            for name in sorted(self.scripts.keys()):
                lines = self.scripts[name]
                count = f"{len(lines)} lines" if lines else "empty"
                print(f"  {ColorPrinter.CYAN}{name}{ColorPrinter.RESET}  {ColorPrinter.YELLOW}({count}){ColorPrinter.RESET}")

        elif subcmd == "rm":
            if len(args) < 2:
                ColorPrinter.warning("Usage: script rm <name>")
                return
            name = args[1]
            if name not in self.scripts:
                ColorPrinter.warning(f"Script '{name}' not found.")
                return
            del self.scripts[name]
            fpath = self._script_file(name)
            if os.path.exists(fpath):
                os.remove(fpath)
            ColorPrinter.success(f"Deleted script '{name}'.")

        elif subcmd == "show":
            if len(args) < 2:
                ColorPrinter.warning("Usage: script show <name>")
                return
            name = args[1]
            if name not in self.scripts:
                ColorPrinter.warning(f"Script '{name}' not found.")
                return
            ColorPrinter.info(f"Script '{name}':")
            for i, line in enumerate(self.scripts[name], 1):
                num = f"{ColorPrinter.YELLOW}{i:3d}{ColorPrinter.RESET}"
                text = f"{ColorPrinter.CYAN}{line}{ColorPrinter.RESET}" if line.strip() and not line.strip().startswith("#") else f"{ColorPrinter.GREEN}{line}{ColorPrinter.RESET}"
                print(f"  {num}  {text}")

        elif subcmd == "import":
            if len(args) < 3:
                ColorPrinter.warning("Usage: script import <name> <path>")
                return
            name = args[1]
            path = args[2]
            try:
                with open(path, "r", encoding="utf-8") as handle:
                    lines = [line.rstrip("\n") for line in handle.readlines()]
                while lines and not lines[-1].strip():
                    lines.pop()
                self.scripts[name] = lines
                self._save_script(name)
                ColorPrinter.success(f"Imported '{name}' ({len(lines)} lines) → {self._script_file(name)}")
            except Exception as exc:
                ColorPrinter.error(f"Failed to import script: {exc}")

        elif subcmd == "load":
            # Reload all scripts from disk (picks up any manually edited .scpi files)
            self.scripts = self._load_scripts()
            ColorPrinter.success(f"Reloaded {len(self.scripts)} scripts from {self._get_scripts_dir()}")

        elif subcmd == "save":
            # Show where scripts live
            ColorPrinter.info(f"Scripts directory: {self._get_scripts_dir()}")

        else:
            ColorPrinter.warning(f"Unknown subcommand '{subcmd}'. Type 'script' for help.")

    def do_examples(self, arg):
        "examples [load <name>|load all]: list or load bundled example scripts"
        try:
            from lab_instruments.examples import EXAMPLES
        except ImportError:
            from examples import EXAMPLES
        args = self._parse_args(arg)
        args, help_flag = self._strip_help(args)

        if not args or help_flag:
            self._print_colored_usage([
                "# EXAMPLES",
                "",
                "examples",
                "  - list all bundled example scripts",
                "examples load <name>",
                "  - copy a bundled example into your scripts (then: script run <name>)",
                "examples load all",
                "  - load every bundled example at once",
            ])
            print()
            ColorPrinter.header("Available Examples")
            for name, entry in EXAMPLES.items():
                print(f"  {ColorPrinter.CYAN}{name}{ColorPrinter.RESET}  {ColorPrinter.YELLOW}{entry['description']}{ColorPrinter.RESET}")
            return

        subcmd = args[0].lower()

        if subcmd == "load":
            if len(args) < 2:
                ColorPrinter.warning("Usage: examples load <name>  or  examples load all")
                return
            target = args[1].lower()
            if target == "all":
                for name, entry in EXAMPLES.items():
                    self.scripts[name] = entry["lines"]
                    self._save_script(name)
                ColorPrinter.success(f"Loaded {len(EXAMPLES)} examples into scripts.")
            elif target in EXAMPLES:
                self.scripts[target] = EXAMPLES[target]["lines"]
                self._save_script(target)
                ColorPrinter.success(f"Loaded '{target}'. Run with: script run {target}")
            else:
                available = list(EXAMPLES.keys())
                ColorPrinter.warning(f"Unknown example '{target}'. Available: {available}")
        else:
            ColorPrinter.warning(f"Unknown subcommand '{subcmd}'. Type 'examples' for help.")

    def do_docs(self, arg):
        "docs: open the full command reference in your browser"
        import subprocess
        import webbrowser
        import threading
        import http.server
        import socket
        from pathlib import Path

        repl_dir = Path(__file__).resolve().parent
        repo_root = repl_dir.parent
        bundled_index = repl_dir / "site" / "index.html"

        # Build if needed (repo dev mode only, not for pip-installed users)
        mkdocs_yml = repo_root / "mkdocs.yml"
        if not bundled_index.exists() and mkdocs_yml.exists():
            ColorPrinter.info("Building docs (first run — takes a few seconds)...")
            result = subprocess.run(
                [sys.executable, "-m", "mkdocs", "build", "--quiet"],
                cwd=str(repo_root),
                capture_output=True,
                env={**os.environ, "PYTHONUTF8": "1"},
            )
            if result.returncode != 0:
                err = result.stderr.decode(errors="replace").strip()
                ColorPrinter.warning(f"mkdocs build failed: {err[:200]}")

        if bundled_index.exists():
            site_dir = str(bundled_index.parent)

            # Reuse existing local server if already started this session
            if not getattr(self, "_docs_port", None):
                with socket.socket() as s:
                    s.bind(("127.0.0.1", 0))
                    port = s.getsockname()[1]

                class _QuietHandler(http.server.SimpleHTTPRequestHandler):
                    def log_message(self, format, *args):
                        pass
                    def __init__(self, *args, **kwargs):
                        super().__init__(*args, directory=site_dir, **kwargs)

                srv = http.server.HTTPServer(("127.0.0.1", port), _QuietHandler)
                threading.Thread(target=srv.serve_forever, daemon=True).start()
                self._docs_port = port

            url = f"http://127.0.0.1:{self._docs_port}/index.html"
            webbrowser.open(url)
            ColorPrinter.success(f"Docs opened at {url}")
            return

        # Fallback: single-page HTML (always works, no dependencies)
        import tempfile
        html = self._generate_docs_html()
        path = Path(tempfile.gettempdir()) / "scpi_toolkit_docs.html"
        path.write_text(html, encoding="utf-8")
        webbrowser.open(path.as_uri())
        ColorPrinter.success("Docs opened in browser.")
        ColorPrinter.info("For the full docs site: pip install mkdocs-material  then  docs")

    def _generate_docs_html(self) -> str:
        try:
            from lab_instruments.examples import EXAMPLES as _EXAMPLES
        except ImportError:
            from examples import EXAMPLES as _EXAMPLES
        import html as _html

        def e(s):
            return _html.escape(str(s))

        try:
            from importlib.metadata import version as _v
            ver = _v("scpi-instrument-toolkit")
        except Exception:
            ver = "dev"

        # ─────────────────────────────────────────────────────────────────────
        # COMMAND DATA
        # Each section: {id, title, intro, commands}
        # Each command: {id, name, brief, syntax, desc, params, examples, notes, see}
        # Each param:   {name, required, values, desc}
        # required values: "required" | "optional" | any other string (shown as context badge)
        # ─────────────────────────────────────────────────────────────────────
        SECTIONS = [
            {
                "id": "general", "title": "General Commands",
                "intro": "These commands work regardless of which instrument is active.",
                "commands": [
                    {
                        "id": "cmd-scan", "name": "scan",
                        "brief": "Discover and connect VISA instruments",
                        "syntax": "scan",
                        "desc": "Scans all VISA resources and auto-identifies instruments by querying <code>*IDN?</code>. Instruments are assigned names like <code>psu1</code>, <code>dmm1</code>, <code>scope1</code>, <code>awg1</code>. When multiple of the same type are found they are numbered: psu1, psu2, etc.",
                        "params": [],
                        "examples": [("scan", "Discover and connect all available instruments")],
                        "notes": [],
                        "see": [],
                    },
                    {
                        "id": "cmd-list", "name": "list",
                        "brief": "Show connected instruments",
                        "syntax": "list",
                        "desc": "Displays all currently connected instruments, their assigned names, and which one is currently active (set via <code>use</code>).",
                        "params": [],
                        "examples": [("list", "Print all connected instruments")],
                        "notes": [],
                        "see": ["cmd-use"],
                    },
                    {
                        "id": "cmd-use", "name": "use",
                        "brief": "Set the active instrument",
                        "syntax": "use <name>",
                        "desc": "Sets the active instrument for subsequent generic commands (e.g. <code>psu set 5.0</code> acts on whatever is active). When only one instrument of a type is connected it is selected automatically. With multiple of the same type you must <code>use</code> the desired one, or address it directly by prefixing commands: <code>psu2 set 12.0</code>.",
                        "params": [
                            {"name": "name", "required": "required", "values": "psu1, dmm2, scope1, …", "desc": "The instrument name as shown by <code>list</code>."},
                        ],
                        "examples": [
                            ("use psu1", "Make psu1 the active PSU"),
                            ("use scope2", "Make scope2 the active oscilloscope"),
                        ],
                        "notes": ["Alternative: prefix any command with the instrument name to address it directly without changing the active selection — e.g. <code>psu2 set 12.0</code>."],
                        "see": ["cmd-list"],
                    },
                    {
                        "id": "cmd-idn", "name": "idn",
                        "brief": "Query instrument identification string",
                        "syntax": "idn [name]",
                        "desc": "Sends <code>*IDN?</code> and prints the response (manufacturer, model, serial, firmware version).",
                        "params": [
                            {"name": "name", "required": "optional", "values": "e.g. psu1, dmm1", "desc": "Instrument to query. Defaults to the currently active instrument if omitted."},
                        ],
                        "examples": [
                            ("idn", "Query IDN of active instrument"),
                            ("idn scope1", "Query IDN of scope1 specifically"),
                        ],
                        "notes": [],
                        "see": ["cmd-raw"],
                    },
                    {
                        "id": "cmd-raw", "name": "raw",
                        "brief": "Send a raw SCPI command or query",
                        "syntax": "raw <command>",
                        "desc": "Sends a raw SCPI string to the active instrument. If the command ends with <code>?</code> the response is printed.",
                        "params": [
                            {"name": "command", "required": "required", "values": "any SCPI string", "desc": "SCPI command or query. Queries (ending with <code>?</code>) print the instrument response."},
                        ],
                        "examples": [
                            ("raw *RST", "Reset the instrument"),
                            ("raw MEAS:VOLT:DC?", "Query DC voltage"),
                            ("raw OUTP:STAT ON", "Turn output on via raw SCPI"),
                        ],
                        "notes": [],
                        "see": ["cmd-idn"],
                    },
                    {
                        "id": "cmd-state", "name": "state",
                        "brief": "Set instrument state",
                        "syntax": "state <on|off|safe|reset>",
                        "desc": "Applies a named state to the active instrument. Behavior depends on instrument type.",
                        "params": [
                            {"name": "on", "required": "—", "values": "on", "desc": "Enable output."},
                            {"name": "off", "required": "—", "values": "off", "desc": "Disable output."},
                            {"name": "safe", "required": "—", "values": "safe", "desc": "Put in safe state: outputs off, returns to safe defaults."},
                            {"name": "reset", "required": "—", "values": "reset", "desc": "Send <code>*RST</code> to restore factory defaults."},
                        ],
                        "examples": [
                            ("state safe", "Put active instrument in safe state"),
                            ("state reset", "Factory-reset active instrument"),
                        ],
                        "notes": [],
                        "see": ["cmd-all"],
                    },
                    {
                        "id": "cmd-all", "name": "all",
                        "brief": "Apply state to every connected instrument",
                        "syntax": "all <on|off|safe|reset>",
                        "desc": "Same as <code>state</code> but applies to all connected instruments simultaneously.",
                        "params": [
                            {"name": "on|off|safe|reset", "required": "required", "values": "on, off, safe, reset", "desc": "State to apply to all instruments. See <code>state</code> for descriptions."},
                        ],
                        "examples": [
                            ("all safe", "Put every instrument in safe state"),
                            ("all off", "Turn off all outputs"),
                        ],
                        "notes": [],
                        "see": ["cmd-state"],
                    },
                    {
                        "id": "cmd-sleep", "name": "sleep / wait",
                        "brief": "Pause execution",
                        "syntax": "sleep <seconds>",
                        "desc": "Pauses the REPL (or script) for the given duration. <code>wait</code> is an alias. Fractional seconds are supported.",
                        "params": [
                            {"name": "seconds", "required": "required", "values": "float ≥ 0", "desc": "Duration to sleep. E.g. <code>0.5</code> = 500 ms, <code>1.0</code> = 1 s."},
                        ],
                        "examples": [
                            ("sleep 1.0", "Pause for 1 second"),
                            ("sleep 0.5", "Pause for 500 ms"),
                            ("wait 2", "Alias: wait 2 seconds"),
                        ],
                        "notes": ["Also valid as a script directive: <code>sleep ${delay}</code> uses a variable for the duration."],
                        "see": [],
                    },
                    {
                        "id": "cmd-reload", "name": "reload / version / clear / exit",
                        "brief": "Utility commands",
                        "syntax": "reload  |  version  |  clear  |  exit  |  quit",
                        "desc": "<code>reload</code> restarts the REPL process. <code>version</code> prints the installed toolkit version. <code>clear</code> clears the terminal. <code>exit</code>/<code>quit</code> close the REPL.",
                        "params": [],
                        "examples": [
                            ("version", "Print installed version"),
                            ("reload", "Restart the REPL"),
                        ],
                        "notes": [],
                        "see": [],
                    },
                ],
            },
            {
                "id": "psu", "title": "PSU — Power Supply",
                "intro": "Controls power supply units. Single-channel PSUs (e.g. HP E3631A) always use channel 1. Multi-channel PSUs (e.g. Matrix MPS-6010H) support channels 1, 2, 3, and all. Multiple PSUs are named psu1, psu2, etc. — address them directly: psu2 set 12.0, or use 'use psu2' first.",
                "commands": [
                    {
                        "id": "psu-chan", "name": "psu chan",
                        "brief": "Enable or disable an output channel",
                        "syntax": "psu chan <channel> <on|off>",
                        "desc": "Turns a PSU output channel on or off. For single-channel PSUs the channel is always <code>1</code>.",
                        "params": [
                            {"name": "channel", "required": "required", "values": "1, 2, 3, all", "desc": "Output channel number. Multi-channel PSUs support 1, 2, 3, or <code>all</code>. Single-channel PSUs always use <code>1</code>."},
                            {"name": "on|off", "required": "required", "values": "on, off", "desc": "<code>on</code> = enable output voltage; <code>off</code> = disable output."},
                        ],
                        "examples": [
                            ("psu chan 1 on", "Enable output on a single-channel PSU"),
                            ("psu chan 2 off", "Disable channel 2 on a multi-channel PSU"),
                            ("psu chan all off", "Disable all channels at once"),
                        ],
                        "notes": [],
                        "see": ["psu-set", "psu-meas_store"],
                    },
                    {
                        "id": "psu-set", "name": "psu set",
                        "brief": "Set output voltage and optional current limit",
                        "syntax": "psu set <voltage> [current]  |  psu set <channel> <voltage> [current]",
                        "desc": "Sets the voltage setpoint and optional current limit. Single-channel PSUs use <code>psu set &lt;V&gt;</code>. Multi-channel PSUs require the channel number first: <code>psu set &lt;ch&gt; &lt;V&gt;</code>.",
                        "params": [
                            {"name": "channel", "required": "multi-ch only", "values": "1, 2, 3", "desc": "Channel number — required for multi-channel PSUs, not used for single-channel PSUs."},
                            {"name": "voltage", "required": "required", "values": "float (V)", "desc": "Target output voltage in volts."},
                            {"name": "current", "required": "optional", "values": "float (A)", "desc": "Current limit in amperes. If omitted, the current limit is unchanged."},
                        ],
                        "examples": [
                            ("psu set 5.0", "Set single-ch output to 5 V"),
                            ("psu set 5.0 0.5", "Set 5 V with 0.5 A current limit"),
                            ("psu set 2 12.0", "Multi-ch: set channel 2 to 12 V"),
                            ("psu set 2 12.0 1.0", "Multi-ch: channel 2, 12 V, 1 A limit"),
                        ],
                        "notes": [],
                        "see": ["psu-chan"],
                    },
                    {
                        "id": "psu-meas", "name": "psu meas",
                        "brief": "Measure and print PSU output",
                        "syntax": "psu meas <v|i> [channel]",
                        "desc": "Takes a live measurement from the PSU and prints the result. Does not store the value — use <code>psu meas_store</code> to record it.",
                        "params": [
                            {"name": "v|i", "required": "required", "values": "v, i", "desc": "<code>v</code> = measure output voltage; <code>i</code> = measure output current."},
                            {"name": "channel", "required": "multi-ch only", "values": "1, 2, 3", "desc": "Channel to measure. Required for multi-channel PSUs."},
                        ],
                        "examples": [
                            ("psu meas v", "Print output voltage"),
                            ("psu meas i", "Print output current"),
                            ("psu meas v 2", "Multi-ch: print channel 2 voltage"),
                        ],
                        "notes": [],
                        "see": ["psu-meas_store"],
                    },
                    {
                        "id": "psu-meas_store", "name": "psu meas_store",
                        "brief": "Measure and record to the measurement log",
                        "syntax": "psu meas_store <v|i> [channel] <label> [unit=<str>]",
                        "desc": "Measures the PSU output and appends the result to the session measurement log. Use <code>log print</code> to view all recorded measurements and <code>calc</code> to compute derived values using stored data.",
                        "params": [
                            {"name": "v|i", "required": "required", "values": "v, i", "desc": "<code>v</code> = measure voltage; <code>i</code> = measure current."},
                            {"name": "channel", "required": "multi-ch only", "values": "1, 2, 3", "desc": "Channel to measure. Required for multi-channel PSUs; omit for single-channel."},
                            {"name": "label", "required": "required", "values": "string, no spaces", "desc": "Name for this measurement entry in the log. Appears as the row identifier in <code>log print</code> output. Also used as the dictionary key in <code>calc</code> expressions — e.g. if label is <code>ch1_v</code> then access it as <code>m[\"ch1_v\"]</code>. Use underscores instead of spaces."},
                            {"name": "unit=", "required": "optional", "values": "string, e.g. V, A", "desc": "Unit label shown in <code>log print</code> output alongside the value (e.g. <code>V</code>, <code>A</code>). This is purely for display — it does not affect the stored numeric value or any <code>calc</code> computation."},
                        ],
                        "examples": [
                            ("psu meas_store v psu_out unit=V", "Store voltage as 'psu_out'; access later as m[\"psu_out\"]"),
                            ("psu meas_store i psu_i unit=A", "Store current as 'psu_i'"),
                            ("psu meas_store v 2 ch2_v unit=V", "Multi-ch: store channel 2 voltage"),
                        ],
                        "notes": [
                            "Access stored values in <code>calc</code>: <code>calc power m[\"psu_out\"]*m[\"psu_i\"] unit=W</code>",
                            "View all stored measurements: <code>log print</code> — Export: <code>log save results.csv</code>",
                        ],
                        "see": ["cmd-log", "cmd-calc"],
                    },
                    {
                        "id": "psu-get", "name": "psu get",
                        "brief": "Show programmed voltage/current setpoints",
                        "syntax": "psu get",
                        "desc": "Reads and displays the <em>programmed</em> setpoints (voltage and current limit) — not the live output. For live measured values use <code>psu meas</code>.",
                        "params": [],
                        "examples": [("psu get", "Print voltage and current setpoints")],
                        "notes": [],
                        "see": ["psu-meas"],
                    },
                    {
                        "id": "psu-track", "name": "psu track",
                        "brief": "Enable/disable channel tracking (multi-channel PSUs)",
                        "syntax": "psu track <on|off>",
                        "desc": "Enables or disables output tracking mode. In tracking mode the two adjustable channels mirror each other (one positive, one negative) for split-supply configurations.",
                        "params": [
                            {"name": "on|off", "required": "required", "values": "on, off", "desc": "<code>on</code> = link channels in tracking mode; <code>off</code> = independent channel control."},
                        ],
                        "examples": [
                            ("psu track on", "Enable tracking (±supply mode)"),
                            ("psu track off", "Return to independent control"),
                        ],
                        "notes": ["Multi-channel PSUs only."],
                        "see": [],
                    },
                    {
                        "id": "psu-save", "name": "psu save / recall",
                        "brief": "Save or restore a state slot",
                        "syntax": "psu save <1-3>  |  psu recall <1-3>",
                        "desc": "Saves the current voltage/current settings to a numbered slot, or restores a previously saved slot. Multi-channel PSUs only.",
                        "params": [
                            {"name": "1-3", "required": "required", "values": "1, 2, 3", "desc": "Slot number to save to or recall from."},
                        ],
                        "examples": [
                            ("psu save 1", "Save current settings to slot 1"),
                            ("psu recall 1", "Restore settings from slot 1"),
                        ],
                        "notes": [],
                        "see": [],
                    },
                ],
            },
            {
                "id": "awg", "title": "AWG — Function Generator",
                "intro": "Controls arbitrary waveform / function generators. Channels 1, 2, or all. Multiple AWGs are named awg1, awg2, etc.",
                "commands": [
                    {
                        "id": "awg-chan", "name": "awg chan",
                        "brief": "Enable or disable an output channel",
                        "syntax": "awg chan <1|2|all> <on|off>",
                        "desc": "Turns an AWG output channel on or off.",
                        "params": [
                            {"name": "1|2|all", "required": "required", "values": "1, 2, all", "desc": "Channel number, or <code>all</code> to affect both channels simultaneously."},
                            {"name": "on|off", "required": "required", "values": "on, off", "desc": "<code>on</code> = enable output; <code>off</code> = disable output."},
                        ],
                        "examples": [
                            ("awg chan 1 on", "Enable channel 1"),
                            ("awg chan all off", "Disable all channels"),
                        ],
                        "notes": [],
                        "see": ["awg-wave"],
                    },
                    {
                        "id": "awg-wave", "name": "awg wave",
                        "brief": "Configure waveform type and parameters",
                        "syntax": "awg wave <1|2|all> <type> [freq=<Hz>] [amp=<Vpp>] [offset=<V>] [duty=<%>] [phase=<deg>]",
                        "desc": "Sets the waveform type and any combination of parameters for one or more channels. Keyword arguments are all optional — omitted parameters retain their current values.",
                        "params": [
                            {"name": "1|2|all", "required": "required", "values": "1, 2, all", "desc": "Channel to configure."},
                            {"name": "type", "required": "required", "values": "sine, square, ramp, triangle, pulse, noise, dc, arb", "desc": "Waveform shape."},
                            {"name": "freq=", "required": "optional", "values": "float (Hz)", "desc": "Output frequency in hertz."},
                            {"name": "amp=", "required": "optional", "values": "float (Vpp)", "desc": "Peak-to-peak amplitude in volts."},
                            {"name": "offset=", "required": "optional", "values": "float (V)", "desc": "DC offset voltage in volts."},
                            {"name": "duty=", "required": "optional", "values": "0.0 – 100.0 (%)", "desc": "Duty cycle percentage. Applies to square and pulse waveforms."},
                            {"name": "phase=", "required": "optional", "values": "float (degrees)", "desc": "Phase offset in degrees."},
                        ],
                        "examples": [
                            ("awg wave 1 sine freq=1000 amp=2.0 offset=0", "1 kHz sine, 2 Vpp, no DC offset"),
                            ("awg wave 1 square freq=500 duty=25", "500 Hz square wave, 25% duty cycle"),
                            ("awg wave all sine freq=10000", "Set both channels to 10 kHz sine"),
                        ],
                        "notes": [],
                        "see": ["awg-freq", "awg-amp", "awg-chan"],
                    },
                    {
                        "id": "awg-freq", "name": "awg freq",
                        "brief": "Set output frequency",
                        "syntax": "awg freq <1|2|all> <Hz>",
                        "desc": "Sets frequency without changing other waveform parameters.",
                        "params": [
                            {"name": "1|2|all", "required": "required", "values": "1, 2, all", "desc": "Channel to configure."},
                            {"name": "Hz", "required": "required", "values": "float > 0", "desc": "Frequency in hertz."},
                        ],
                        "examples": [
                            ("awg freq 1 1000", "Set ch1 to 1 kHz"),
                            ("awg freq all 50000", "Set both channels to 50 kHz"),
                        ],
                        "notes": [],
                        "see": ["awg-wave"],
                    },
                    {
                        "id": "awg-amp", "name": "awg amp / offset / duty / phase",
                        "brief": "Set amplitude, DC offset, duty cycle, or phase",
                        "syntax": "awg amp <1|2|all> <Vpp>  |  awg offset <1|2|all> <V>  |  awg duty <1|2|all> <%>  |  awg phase <1|2|all> <deg>",
                        "desc": "Fine-tune individual waveform parameters without changing other settings.",
                        "params": [
                            {"name": "1|2|all", "required": "required", "values": "1, 2, all", "desc": "Channel to configure."},
                            {"name": "Vpp", "required": "required (amp)", "values": "float (V)", "desc": "Peak-to-peak amplitude in volts."},
                            {"name": "V", "required": "required (offset)", "values": "float (V)", "desc": "DC offset. Negative values shift the waveform below ground."},
                            {"name": "%", "required": "required (duty)", "values": "0.0 – 100.0", "desc": "Duty cycle percentage for square/pulse waveforms."},
                            {"name": "deg", "required": "required (phase)", "values": "0.0 – 360.0", "desc": "Phase offset in degrees. 180° inverts the waveform."},
                        ],
                        "examples": [
                            ("awg amp 1 3.3", "Set ch1 amplitude to 3.3 Vpp"),
                            ("awg offset 1 1.65", "Shift ch1 waveform up by 1.65 V"),
                            ("awg duty 1 25", "Set ch1 duty cycle to 25%"),
                            ("awg phase 2 180", "Invert ch2 (180° phase offset)"),
                        ],
                        "notes": [],
                        "see": ["awg-wave"],
                    },
                    {
                        "id": "awg-sync", "name": "awg sync",
                        "brief": "Enable/disable sync output",
                        "syntax": "awg sync <on|off>",
                        "desc": "Enables or disables the sync/trigger output signal on supported AWGs.",
                        "params": [
                            {"name": "on|off", "required": "required", "values": "on, off", "desc": "Enable or disable sync output."},
                        ],
                        "examples": [("awg sync on", "Enable sync output")],
                        "notes": [],
                        "see": [],
                    },
                ],
            },
            {
                "id": "dmm", "title": "DMM — Multimeter",
                "intro": "Controls digital multimeters. Multiple DMMs are named dmm1, dmm2, etc. Typical workflow: configure mode → read. Or use meas for a single one-shot measurement.",
                "commands": [
                    {
                        "id": "dmm-config", "name": "dmm config",
                        "brief": "Configure the measurement mode",
                        "syntax": "dmm config <mode> [range] [resolution] [nplc=<n>]",
                        "desc": "Configures the DMM for a specific measurement type. After configuring, use <code>dmm read</code> or <code>dmm meas_store</code>. The mode stays active until changed.",
                        "params": [
                            {"name": "mode", "required": "required", "values": "vdc, vac, idc, iac, res, fres, freq, per, cont, diode, cap, temp", "desc": "Measurement mode: <code>vdc</code> = DC voltage, <code>vac</code> = AC voltage, <code>idc</code> = DC current, <code>iac</code> = AC current, <code>res</code> = 2-wire resistance, <code>fres</code> = 4-wire resistance, <code>freq</code> = frequency, <code>per</code> = period, <code>cont</code> = continuity, <code>diode</code> = diode voltage, <code>cap</code> = capacitance, <code>temp</code> = temperature."},
                            {"name": "range", "required": "optional", "values": "float, DEF, MIN, MAX", "desc": "Measurement range (e.g. <code>10</code> for 10 V range). Use <code>DEF</code> for auto-range."},
                            {"name": "resolution", "required": "optional", "values": "float, DEF, MIN, MAX", "desc": "Resolution (number of significant digits). Use <code>DEF</code> for default."},
                            {"name": "nplc=", "required": "optional", "values": "0.02, 0.2, 1, 10, 100", "desc": "Integration time in power line cycles. Higher = slower but lower noise. Only supported on HP 34401A and for DC measurement modes."},
                        ],
                        "examples": [
                            ("dmm config vdc", "Configure for DC voltage, auto-range"),
                            ("dmm config vdc 10 DEF nplc=10", "DC voltage, 10 V range, high-accuracy (slow)"),
                            ("dmm config res DEF DEF nplc=1", "2-wire resistance, auto-range, 1 PLC"),
                        ],
                        "notes": ["For a one-shot measurement without a separate configure step, use <code>dmm meas &lt;mode&gt;</code> instead."],
                        "see": ["dmm-read", "dmm-meas"],
                    },
                    {
                        "id": "dmm-read", "name": "dmm read",
                        "brief": "Take a reading (after dmm config)",
                        "syntax": "dmm read",
                        "desc": "Takes a measurement using the currently configured mode and prints the result. Call <code>dmm config</code> first.",
                        "params": [],
                        "examples": [("dmm read", "Take one reading in the current measurement mode")],
                        "notes": [],
                        "see": ["dmm-config", "dmm-meas_store"],
                    },
                    {
                        "id": "dmm-meas_store", "name": "dmm meas_store",
                        "brief": "Read and record to the measurement log",
                        "syntax": "dmm meas_store <label> [scale=<factor>] [unit=<str>]",
                        "desc": "Takes a reading using the current configuration and appends it to the session measurement log. Requires <code>dmm config</code> to have been called first.",
                        "params": [
                            {"name": "label", "required": "required", "values": "string, no spaces", "desc": "Name for this measurement entry in the log. Appears as the row identifier in <code>log print</code> output. Also used as the dictionary key in <code>calc</code> expressions — e.g. if label is <code>vout</code> then access it as <code>m[\"vout\"]</code>. Use underscores instead of spaces (e.g. <code>vout_mv</code>)."},
                            {"name": "scale=", "required": "optional", "values": "float", "desc": "Multiply the raw reading by this factor before storing. Useful for unit conversion — e.g. <code>scale=1000</code> to convert V → mV, or <code>scale=0.001</code> to convert mA → A. Default: 1.0 (no scaling)."},
                            {"name": "unit=", "required": "optional", "values": "string, e.g. V, mV, A, Ω", "desc": "Unit label shown in <code>log print</code> output alongside the value. This is purely for display — it does not affect the stored numeric value or any <code>calc</code> computation."},
                        ],
                        "examples": [
                            ("dmm meas_store vout unit=V", "Store reading as 'vout' with unit V"),
                            ("dmm meas_store res_low unit=\u03a9", "Store resistance as 'res_low'"),
                            ("dmm meas_store vout_mv scale=1000 unit=mV", "Store in mV by multiplying reading by 1000"),
                        ],
                        "notes": [
                            "You must call <code>dmm config &lt;mode&gt;</code> before using <code>meas_store</code>.",
                            "Access stored values in <code>calc</code>: <code>calc power m[\"vout\"]*m[\"iout\"] unit=W</code>",
                        ],
                        "see": ["dmm-config", "cmd-log", "cmd-calc"],
                    },
                    {
                        "id": "dmm-meas", "name": "dmm meas",
                        "brief": "One-shot measurement (configure + read in one step)",
                        "syntax": "dmm meas <mode> [range] [resolution]",
                        "desc": "Configures the DMM and takes a single reading in one command. Convenient for quick checks; for repeated measurements in the same mode use <code>dmm config</code> + <code>dmm read</code>.",
                        "params": [
                            {"name": "mode", "required": "required", "values": "vdc, vac, idc, iac, res, fres, freq, per, cont, diode", "desc": "Measurement mode. Same values as <code>dmm config</code>."},
                            {"name": "range", "required": "optional", "values": "float or DEF", "desc": "Measurement range. Default: auto-range."},
                            {"name": "resolution", "required": "optional", "values": "float or DEF", "desc": "Resolution. Default: default."},
                        ],
                        "examples": [
                            ("dmm meas vdc", "Quick DC voltage reading"),
                            ("dmm meas res", "Quick 2-wire resistance reading"),
                        ],
                        "notes": [],
                        "see": ["dmm-config"],
                    },
                    {
                        "id": "dmm-fetch", "name": "dmm fetch",
                        "brief": "Fetch the last reading without triggering a new one",
                        "syntax": "dmm fetch",
                        "desc": "Returns the last measurement result without initiating a new measurement. HP 34401A only.",
                        "params": [],
                        "examples": [("dmm fetch", "Retrieve the last reading")],
                        "notes": ["HP 34401A only."],
                        "see": ["dmm-read"],
                    },
                    {
                        "id": "dmm-display", "name": "dmm display / beep / text / ranges",
                        "brief": "Display control, beep, and range info",
                        "syntax": "dmm display <on|off>  |  dmm beep  |  dmm text <msg> [scroll=] [delay=] [loops=]  |  dmm ranges",
                        "desc": "Utility commands. <code>display</code> turns the front panel display on/off. <code>beep</code> triggers an audible beep. <code>text</code> displays a message on the DMM screen with optional scrolling. <code>ranges</code> prints supported measurement ranges for the connected model.",
                        "params": [
                            {"name": "on|off", "required": "required (display)", "values": "on, off", "desc": "Turn the display on or off."},
                            {"name": "msg", "required": "required (text)", "values": "string", "desc": "Text to show on the DMM front panel."},
                            {"name": "scroll=", "required": "optional (text)", "values": "auto, on, off", "desc": "Scroll behavior for long messages."},
                            {"name": "delay=", "required": "optional (text)", "values": "float (s)", "desc": "Delay between scroll steps."},
                            {"name": "loops=", "required": "optional (text)", "values": "int", "desc": "Scroll repetitions."},
                        ],
                        "examples": [
                            ("dmm beep", "Trigger a beep"),
                            ("dmm display off", "Blank the front panel display"),
                            ("dmm text TESTING scroll=auto", "Show scrolling text on DMM"),
                            ("dmm ranges", "Show supported measurement ranges"),
                        ],
                        "notes": ["Text/scroll features: HP 34401A only."],
                        "see": [],
                    },
                ],
            },
            {
                "id": "scope", "title": "Scope — Oscilloscope",
                "intro": "Controls oscilloscopes. Multiple scopes are named scope1, scope2, etc. Channels 1–4 are supported; use all to affect every channel at once.",
                "commands": [
                    {
                        "id": "scope-acq", "name": "scope autoset / run / stop / single",
                        "brief": "Acquisition control",
                        "syntax": "scope autoset  |  scope run  |  scope stop  |  scope single",
                        "desc": "<code>autoset</code> auto-configures time/voltage scales and trigger for the current input. <code>run</code> starts continuous acquisition. <code>stop</code> freezes the display. <code>single</code> arms a single-shot trigger.",
                        "params": [],
                        "examples": [
                            ("scope autoset", "Auto-configure scope for current signal"),
                            ("scope single", "Arm single-shot capture"),
                            ("scope stop", "Freeze acquisition"),
                        ],
                        "notes": [],
                        "see": ["scope-trigger"],
                    },
                    {
                        "id": "scope-chan", "name": "scope chan",
                        "brief": "Enable or disable a channel",
                        "syntax": "scope chan <1-4|all> <on|off>",
                        "desc": "Shows or hides an oscilloscope input channel.",
                        "params": [
                            {"name": "1-4|all", "required": "required", "values": "1, 2, 3, 4, all", "desc": "Channel number, or <code>all</code> to affect all channels."},
                            {"name": "on|off", "required": "required", "values": "on, off", "desc": "<code>on</code> = display channel; <code>off</code> = hide channel."},
                        ],
                        "examples": [
                            ("scope chan 1 on", "Show channel 1"),
                            ("scope chan 3 off", "Hide channel 3"),
                            ("scope chan all on", "Show all channels"),
                        ],
                        "notes": [],
                        "see": ["scope-coupling", "scope-vscale"],
                    },
                    {
                        "id": "scope-coupling", "name": "scope coupling / probe",
                        "brief": "Set input coupling and probe attenuation",
                        "syntax": "scope coupling <1-4|all> <DC|AC|GND>  |  scope probe <1-4|all> <attenuation>",
                        "desc": "<code>coupling</code> sets the input coupling. DC passes all frequencies; AC blocks DC; GND disconnects the input. <code>probe</code> sets the probe attenuation ratio so the scope displays correct voltages.",
                        "params": [
                            {"name": "1-4|all", "required": "required", "values": "1, 2, 3, 4, all", "desc": "Channel number."},
                            {"name": "DC|AC|GND", "required": "required (coupling)", "values": "DC, AC, GND", "desc": "Input coupling mode."},
                            {"name": "attenuation", "required": "required (probe)", "values": "1, 10, 100", "desc": "Probe attenuation ratio (1× for direct connection, 10× for 10× probe, 100× for high-voltage probe)."},
                        ],
                        "examples": [
                            ("scope coupling 1 AC", "AC-couple channel 1"),
                            ("scope coupling all DC", "DC-couple all channels"),
                            ("scope probe 1 10", "Set ch1 for a 10× probe"),
                        ],
                        "notes": [],
                        "see": ["scope-chan"],
                    },
                    {
                        "id": "scope-hscale", "name": "scope hscale / hpos / hmove",
                        "brief": "Horizontal (time) axis control",
                        "syntax": "scope hscale <s/div>  |  scope hpos <pct>  |  scope hmove <delta>",
                        "desc": "<code>hscale</code> sets time per division. <code>hpos</code> sets the trigger position as a percentage. <code>hmove</code> adjusts the position relatively.",
                        "params": [
                            {"name": "s/div", "required": "required (hscale)", "values": "float (s)", "desc": "Time per division (e.g. <code>0.001</code> = 1 ms/div)."},
                            {"name": "pct", "required": "required (hpos)", "values": "float 0–100", "desc": "Trigger position as percentage of screen width."},
                            {"name": "delta", "required": "required (hmove)", "values": "float", "desc": "Relative adjustment amount."},
                        ],
                        "examples": [
                            ("scope hscale 0.001", "Set 1 ms/div"),
                            ("scope hpos 50", "Center trigger at 50%"),
                        ],
                        "notes": [],
                        "see": ["scope-vscale"],
                    },
                    {
                        "id": "scope-vscale", "name": "scope vscale / vpos / vmove",
                        "brief": "Vertical (voltage) axis control",
                        "syntax": "scope vscale <1-4|all> <V/div> [pos]  |  scope vpos <1-4|all> <div>  |  scope vmove <1-4|all> <delta>",
                        "desc": "<code>vscale</code> sets voltage per division. Optional <code>pos</code> sets the vertical position. <code>vpos</code> sets absolute position in divisions. <code>vmove</code> adjusts position relatively.",
                        "params": [
                            {"name": "1-4|all", "required": "required", "values": "1, 2, 3, 4, all", "desc": "Channel number."},
                            {"name": "V/div", "required": "required (vscale)", "values": "float (V)", "desc": "Voltage per division."},
                            {"name": "pos", "required": "optional (vscale)", "values": "float (divisions)", "desc": "Vertical position offset in divisions. Default: 0 (centered)."},
                            {"name": "div", "required": "required (vpos)", "values": "float", "desc": "Absolute vertical position in divisions."},
                            {"name": "delta", "required": "required (vmove)", "values": "float", "desc": "Relative position change in divisions."},
                        ],
                        "examples": [
                            ("scope vscale 1 0.5", "Set ch1 to 0.5 V/div"),
                            ("scope vscale all 1.0 0", "All channels: 1 V/div, centered"),
                        ],
                        "notes": [],
                        "see": ["scope-hscale"],
                    },
                    {
                        "id": "scope-trigger", "name": "scope trigger",
                        "brief": "Configure the trigger",
                        "syntax": "scope trigger <channel> <level> [slope=<RISE|FALL>] [mode=<AUTO|NORM|SINGLE>]",
                        "desc": "Sets the trigger source, voltage level, edge slope, and acquisition mode.",
                        "params": [
                            {"name": "channel", "required": "required", "values": "1, 2, 3, 4", "desc": "Trigger source channel."},
                            {"name": "level", "required": "required", "values": "float (V)", "desc": "Trigger threshold voltage."},
                            {"name": "slope=", "required": "optional", "values": "RISE, FALL", "desc": "Trigger on rising or falling edge. Default: RISE."},
                            {"name": "mode=", "required": "optional", "values": "AUTO, NORM, SINGLE", "desc": "Trigger mode. AUTO = free-run if no trigger; NORM = wait for trigger; SINGLE = one shot. Default: AUTO."},
                        ],
                        "examples": [
                            ("scope trigger 1 0.0", "Trigger on ch1, 0 V, rising edge"),
                            ("scope trigger 1 1.5 slope=FALL mode=NORM", "Ch1, 1.5 V, falling edge, normal mode"),
                        ],
                        "notes": [],
                        "see": ["scope-acq"],
                    },
                    {
                        "id": "scope-meas", "name": "scope meas",
                        "brief": "Take and print a single measurement",
                        "syntax": "scope meas <1-4|all> <type>",
                        "desc": "Queries a measurement from the scope and prints the result. Does not store to the log — use <code>scope meas_store</code> for logging.",
                        "params": [
                            {"name": "1-4|all", "required": "required", "values": "1, 2, 3, 4, all", "desc": "Channel(s) to measure."},
                            {"name": "type", "required": "required", "values": "FREQUENCY, PK2PK, RMS, CRMS, MEAN, PERIOD, AMPLITUDE, MINIMUM, MAXIMUM, HIGH, LOW, RISE, FALL, PWIDTH, NWIDTH", "desc": "Measurement type."},
                        ],
                        "examples": [
                            ("scope meas 1 FREQUENCY", "Print channel 1 frequency"),
                            ("scope meas 1 PK2PK", "Print channel 1 peak-to-peak voltage"),
                        ],
                        "notes": [],
                        "see": ["scope-meas_store"],
                    },
                    {
                        "id": "scope-meas_store", "name": "scope meas_store",
                        "brief": "Measure and record to the log",
                        "syntax": "scope meas_store <1-4|all> <type> <label> [unit=<str>]",
                        "desc": "Queries a measurement from the scope and appends it to the session measurement log.",
                        "params": [
                            {"name": "1-4|all", "required": "required", "values": "1, 2, 3, 4, all", "desc": "Channel to measure."},
                            {"name": "type", "required": "required", "values": "FREQUENCY, PK2PK, RMS, CRMS, MEAN, PERIOD, AMPLITUDE, MINIMUM, MAXIMUM, HIGH, LOW, RISE, FALL, PWIDTH, NWIDTH", "desc": "Type of measurement to take."},
                            {"name": "label", "required": "required", "values": "string, no spaces", "desc": "Name for this measurement entry in the log. Appears as the row identifier in <code>log print</code>. Also used as the dictionary key in <code>calc</code> expressions — e.g. if label is <code>ch1_freq</code> then access it as <code>m[\"ch1_freq\"]</code>. Use underscores instead of spaces."},
                            {"name": "unit=", "required": "optional", "values": "string, e.g. Hz, V", "desc": "Unit label shown in <code>log print</code> output. Display-only — does not affect the stored value or calculations."},
                        ],
                        "examples": [
                            ("scope meas_store 1 FREQUENCY meas_freq unit=Hz", "Store ch1 frequency as 'meas_freq'"),
                            ("scope meas_store 1 PK2PK meas_pk2pk unit=V", "Store ch1 PK2PK"),
                            ("scope meas_store 1 RMS meas_rms unit=V", "Store ch1 RMS"),
                        ],
                        "notes": [
                            "Access stored values in <code>calc</code>: <code>calc ratio m[\"meas_pk2pk\"]/m[\"meas_rms\"]</code>",
                        ],
                        "see": ["scope-meas", "cmd-log", "cmd-calc"],
                    },
                    {
                        "id": "scope-meas_delay", "name": "scope meas_delay / meas_delay_store",
                        "brief": "Measure propagation delay between two channels",
                        "syntax": "scope meas_delay <ch1> <ch2> [edge1=RISE] [edge2=RISE]  |  scope meas_delay_store <ch1> <ch2> <label> [edge1=] [edge2=] [direction=] [unit=]",
                        "desc": "Measures the time delay between trigger events on two channels (propagation delay / phase shift).",
                        "params": [
                            {"name": "ch1 / ch2", "required": "required", "values": "1, 2, 3, 4", "desc": "Source and reference channel numbers."},
                            {"name": "edge1= / edge2=", "required": "optional", "values": "RISE, FALL", "desc": "Which edge to detect on each channel. Default: RISE."},
                            {"name": "direction=", "required": "optional", "values": "FORWARDS, BACKWARDS", "desc": "Search direction. Default: FORWARDS."},
                            {"name": "label", "required": "required (store)", "values": "string, no spaces", "desc": "Log entry name. See <code>scope meas_store</code> for full description of the label parameter."},
                            {"name": "unit=", "required": "optional", "values": "string, e.g. s, ms, us", "desc": "Unit shown in log output."},
                        ],
                        "examples": [
                            ("scope meas_delay 1 2", "Print delay from ch1 to ch2"),
                            ("scope meas_delay_store 1 2 prop_delay unit=s", "Store delay as 'prop_delay'"),
                        ],
                        "notes": [],
                        "see": ["scope-meas_store"],
                    },
                    {
                        "id": "scope-save", "name": "scope save",
                        "brief": "Save waveform data to CSV",
                        "syntax": "scope save <channels> <file.csv> [record=<s>] [time=<s>] [points=<n>]",
                        "desc": "Downloads waveform data from the scope and saves as CSV.",
                        "params": [
                            {"name": "channels", "required": "required", "values": "1, 2, 3, 4, or e.g. 1,2", "desc": "Channel(s) to save. Comma-separated for multiple."},
                            {"name": "file.csv", "required": "required", "values": "file path", "desc": "Output file. Created or overwritten."},
                            {"name": "record= / time=", "required": "optional", "values": "float (s)", "desc": "Record for this many seconds before saving."},
                            {"name": "points=", "required": "optional", "values": "int", "desc": "Number of waveform points to request."},
                        ],
                        "examples": [
                            ("scope save 1 output.csv", "Save ch1 waveform"),
                            ("scope save 1,2 both.csv", "Save ch1 and ch2"),
                            ("scope save 1 data.csv record=2.0", "Record 2 s then save"),
                        ],
                        "notes": [],
                        "see": [],
                    },
                    {
                        "id": "scope-tools", "name": "scope awg / counter / dvm",
                        "brief": "Built-in scope tools",
                        "syntax": "scope awg <subcmd>  |  scope counter <subcmd>  |  scope dvm <subcmd>",
                        "desc": "Access built-in tools. <code>awg</code> controls the built-in waveform generator (DHO914S/DHO924S only). <code>counter</code> controls the built-in frequency counter. <code>dvm</code> controls the built-in digital voltmeter. Run the subcommand alone (e.g. <code>scope awg</code>) for help.",
                        "params": [],
                        "examples": [
                            ("scope counter on", "Enable frequency counter"),
                            ("scope dvm on", "Enable DVM"),
                            ("scope awg", "Show AWG subcommands"),
                        ],
                        "notes": ["Built-in AWG: DHO914S and DHO924S only."],
                        "see": [],
                    },
                ],
            },
            {
                "id": "scripting", "title": "Scripts & Directives",
                "intro": "Scripts are named sequences of REPL commands stored in the session. They support variables, loops, and calling other scripts. Script directives (set, for, repeat, print, input, pause, call) are also valid as interactive REPL commands.",
                "commands": [
                    {
                        "id": "script-new", "name": "script new",
                        "brief": "Create a new script",
                        "syntax": "script new <name>",
                        "desc": "Creates a new empty script and opens it in your configured editor ($EDITOR). Each line you write becomes a REPL command that runs when the script executes.",
                        "params": [
                            {"name": "name", "required": "required", "values": "string, no spaces", "desc": "Script name. Used to reference the script in <code>script run</code> and <code>call</code>."},
                        ],
                        "examples": [("script new my_test", "Create and edit a script called 'my_test'")],
                        "notes": [],
                        "see": ["script-run", "script-edit"],
                    },
                    {
                        "id": "script-run", "name": "script run",
                        "brief": "Execute a script with optional parameter overrides",
                        "syntax": "script run <name> [key=value ...]",
                        "desc": "Runs a named script. Key=value pairs override variables defined with <code>set</code> inside the script, letting you parameterize the same script for different test conditions without editing it.",
                        "params": [
                            {"name": "name", "required": "required", "values": "script name", "desc": "Name of the script to run (as shown in <code>script list</code>)."},
                            {"name": "key=value", "required": "optional", "values": "any key=value pairs", "desc": "Override script variables. These replace the default values from <code>set</code> lines. E.g. <code>voltage=3.3</code> sets <code>${voltage}</code> to 3.3 throughout the script for this run."},
                        ],
                        "examples": [
                            ("script run my_test", "Run 'my_test' with default variable values"),
                            ("script run psu_dmm_test voltage=3.3 label=test_3v3", "Run with custom parameters"),
                        ],
                        "notes": [
                            "Script variables are referenced as <code>${varname}</code> inside script lines.",
                            "Priority order: command-line params &gt; <code>set</code> defaults in the script.",
                        ],
                        "see": ["script-new", "directive-set"],
                    },
                    {
                        "id": "script-edit", "name": "script edit / show / list / rm",
                        "brief": "Manage the script library",
                        "syntax": "script edit <name>  |  script show <name>  |  script list  |  script rm <name>  |  script import <name> <path>  |  script load  |  script save",
                        "desc": "Library management commands. <code>edit</code> opens a script in your editor. <code>show</code> prints it with syntax highlighting. <code>list</code> shows all scripts. <code>rm</code> deletes a script. <code>import</code> loads lines from a .txt file. <code>load</code> reloads all scripts from disk. <code>save</code> displays the scripts directory path.",
                        "params": [
                            {"name": "name", "required": "required (edit/show/rm/import)", "values": "script name", "desc": "Script to operate on."},
                        ],
                        "examples": [
                            ("script list", "Show all scripts with line counts"),
                            ("script show psu_dmm_test", "Print script lines"),
                            ("script rm old_test", "Delete 'old_test'"),
                            ("script save", "Show where scripts are stored"),
                        ],
                        "notes": [],
                        "see": [],
                    },
                    {
                        "id": "directive-set", "name": "set",
                        "brief": "Define a script variable (evaluated at expansion time)",
                        "syntax": "set <varname> <expression>",
                        "desc": "Defines a variable accessible as <code>${varname}</code> in subsequent script lines. Evaluated when the script is expanded (before execution begins), so arithmetic using other variables works: <code>set doubled ${voltage} * 2</code>. Variables set here are overridable from the command line when running the script.",
                        "params": [
                            {"name": "varname", "required": "required", "values": "string, no spaces", "desc": "Variable name. Reference it as <code>${varname}</code> in script lines."},
                            {"name": "expression", "required": "required", "values": "number, string, or math expr", "desc": "Value or arithmetic expression. Supports references to other variables: <code>${v_start} + 1.5</code>. String values are stored as-is."},
                        ],
                        "examples": [
                            ("set voltage 5.0", "Define ${voltage} = 5.0 (overridable at run time)"),
                            ("set label vtest", "Define ${label} = 'vtest'"),
                            ("set doubled ${voltage} * 2", "Compute a derived variable"),
                        ],
                        "notes": [
                            "Override at run time: <code>script run my_test voltage=3.3</code>",
                            "Variables set via <code>input</code> are captured at run time and cannot be overridden from the command line.",
                        ],
                        "see": ["directive-input", "script-run"],
                    },
                    {
                        "id": "directive-print", "name": "print",
                        "brief": "Display a message to the operator",
                        "syntax": "print <message>",
                        "desc": "Prints a message to the terminal. Variable references like <code>${varname}</code> are expanded before printing.",
                        "params": [
                            {"name": "message", "required": "required", "values": "any text", "desc": "Text to display. <code>${varname}</code> references are substituted with their current values."},
                        ],
                        "examples": [
                            ("print === Test Starting ===", "Print a header line"),
                            ("print Setting ${voltage}V", "Print a message with variable substitution"),
                        ],
                        "notes": [],
                        "see": ["directive-pause", "directive-input"],
                    },
                    {
                        "id": "directive-pause", "name": "pause",
                        "brief": "Wait for operator to press Enter",
                        "syntax": "pause [message]",
                        "desc": "Stops script execution and waits for the operator to press Enter. Useful for manual steps — connecting probes, changing DUT, verifying wiring — before the script continues.",
                        "params": [
                            {"name": "message", "required": "optional", "values": "any text", "desc": "Custom prompt shown to the operator. Default: 'Press Enter to continue...'"},
                        ],
                        "examples": [
                            ("pause", "Wait with default prompt"),
                            ("pause Connect probe to TP1 then press Enter", "Wait with custom instruction"),
                        ],
                        "notes": [],
                        "see": ["directive-print", "directive-input"],
                    },
                    {
                        "id": "directive-input", "name": "input",
                        "brief": "Prompt operator for a value and store it as a variable",
                        "syntax": "input <varname> [prompt text]",
                        "desc": "Prompts the operator to type a value at script run time. The entered text is stored as <code>${varname}</code> and substituted into all subsequent script lines. Unlike <code>set</code>, the value is not known until the script runs and cannot be overridden from the command line.",
                        "params": [
                            {"name": "varname", "required": "required", "values": "string, no spaces", "desc": "Variable name. The operator's input will be available as <code>${varname}</code> in all lines after this directive."},
                            {"name": "prompt text", "required": "optional", "values": "any text", "desc": "Prompt shown to the operator. Default: the variable name followed by a colon."},
                        ],
                        "examples": [
                            ("input voltage Enter target voltage (V):", "Prompt for voltage; stored as ${voltage}"),
                            ("input dut_id DUT serial number:", "Prompt for DUT identifier"),
                        ],
                        "notes": [
                            "The entered value is always stored as a string. When used in arithmetic (e.g. via <code>set doubled ${voltage} * 2</code>), it is coerced to a number.",
                            "Unlike <code>set</code>, input values cannot be overridden by command-line parameters at <code>script run</code> time.",
                        ],
                        "see": ["directive-set", "directive-pause"],
                    },
                    {
                        "id": "directive-call", "name": "call",
                        "brief": "Call another script inline",
                        "syntax": "call <name> [key=value ...]",
                        "desc": "Executes another script as a sub-routine. Variables from the current script can be passed as parameters. The called script runs in its own variable scope.",
                        "params": [
                            {"name": "name", "required": "required", "values": "script name", "desc": "Name of the script to call."},
                            {"name": "key=value", "required": "optional", "values": "any key=value", "desc": "Parameters to pass. Variable substitution works in values: <code>voltage=${target_v}</code> passes the current value of <code>${target_v}</code>."},
                        ],
                        "examples": [
                            ("call set_psu voltage=5.0", "Call 'set_psu' passing voltage=5.0"),
                            ("call set_psu voltage=${target_v}", "Pass a variable from the current script"),
                        ],
                        "notes": ["Parameters override <code>set</code> defaults in the called script."],
                        "see": ["directive-set", "script-run"],
                    },
                    {
                        "id": "directive-repeat", "name": "repeat ... end",
                        "brief": "Repeat a block N times",
                        "syntax": "repeat <N>\n  <commands>\nend",
                        "desc": "Executes the enclosed commands a fixed number of times.",
                        "params": [
                            {"name": "N", "required": "required", "values": "int ≥ 1", "desc": "Number of repetitions."},
                        ],
                        "examples": [
                            ("repeat 3\n  psu meas v\n  sleep 0.2\nend", "Measure voltage 3 times, 200 ms apart"),
                        ],
                        "notes": [],
                        "see": ["directive-for"],
                    },
                    {
                        "id": "directive-for", "name": "for ... end",
                        "brief": "Loop over a list of values",
                        "syntax": "for <var> <val1> <val2> ... <valN>\n  <commands>\nend",
                        "desc": "Iterates over a whitespace-separated list of values, setting <code>${var}</code> to each value in turn and executing the block for each.",
                        "params": [
                            {"name": "var", "required": "required", "values": "string", "desc": "Loop variable name, referenced as <code>${var}</code> inside the block."},
                            {"name": "val1 val2 ...", "required": "required", "values": "space-separated", "desc": "Values to iterate over — numbers, strings, or variable references like <code>${start}</code>."},
                        ],
                        "examples": [
                            ("for v 1.0 2.0 3.3 5.0\n  psu1 set ${v}\n  sleep 0.5\n  dmm1 meas_store vdc v_${v} unit=V\nend", "Sweep PSU through voltages and log each"),
                            ("for ch 1 2 3 4\n  scope chan ${ch} on\nend", "Enable all scope channels"),
                        ],
                        "notes": [
                            "The loop variable is substituted in all lines inside the block.",
                            "Variable references work in the value list: <code>for v ${v_start} ${v_mid} ${v_end}</code>",
                        ],
                        "see": ["directive-repeat"],
                    },
                ],
            },
            {
                "id": "log", "title": "Log & Calc",
                "intro": "All meas_store commands write to a shared in-session measurement log. Use log to view or export the results, and calc to derive new values from stored measurements.",
                "commands": [
                    {
                        "id": "cmd-log", "name": "log print / save / clear",
                        "brief": "View, export, or clear the measurement log",
                        "syntax": "log print  |  log save <file> [csv|txt]  |  log clear",
                        "desc": "<code>log print</code> displays all measurements in a table (Label | Value | Unit | Source). <code>log save</code> exports to a file. <code>log clear</code> erases all stored measurements.",
                        "params": [
                            {"name": "file", "required": "required (save)", "values": "file path", "desc": "Output file path (e.g. <code>results.csv</code>)."},
                            {"name": "csv|txt", "required": "optional (save)", "values": "csv, txt", "desc": "File format. Defaults based on file extension."},
                        ],
                        "examples": [
                            ("log print", "Print all stored measurements"),
                            ("log save results.csv", "Export to CSV"),
                            ("log clear", "Erase all measurements before a new test"),
                        ],
                        "notes": [],
                        "see": ["cmd-calc"],
                    },
                    {
                        "id": "cmd-calc", "name": "calc",
                        "brief": "Compute a derived value from stored measurements",
                        "syntax": "calc <label> <expression> [unit=<str>]",
                        "desc": "Evaluates a Python arithmetic expression using stored measurements as inputs. The result is printed and also stored in the log under the given <code>label</code> so it can be used in further <code>calc</code> expressions.",
                        "params": [
                            {"name": "label", "required": "required", "values": "string, no spaces", "desc": "Name for the computed result in the log. Appears in <code>log print</code> and can be referenced in subsequent <code>calc</code> expressions."},
                            {"name": "expression", "required": "required", "values": "Python arithmetic expression", "desc": "Math expression. Access stored measurements by label using <code>m[\"label\"]</code>. Use <code>last</code> for the most recently stored value. Available: <code>abs</code>, <code>min</code>, <code>max</code>, <code>round</code>, <code>pi</code> and other math constants."},
                            {"name": "unit=", "required": "optional", "values": "string", "desc": "Unit label for the result shown in <code>log print</code>. Display-only."},
                        ],
                        "examples": [
                            ("calc power m[\"psu_v\"]*m[\"psu_i\"] unit=W", "Compute power from stored voltage and current"),
                            ("calc ratio m[\"output\"]/m[\"input\"]", "Compute ratio between two measurements"),
                            ("calc err_pct (m[\"meas\"]-m[\"ref\"])/m[\"ref\"]*100 unit=%", "Compute percentage error"),
                        ],
                        "notes": [
                            "Labels used in expressions must have been stored earlier in the session by a <code>meas_store</code> or previous <code>calc</code>.",
                            "The computed result is stored in the log, so chained calculations work: <code>calc efficiency m[\"power_out\"]/m[\"power_in\"]*100 unit=%</code>",
                        ],
                        "see": ["cmd-log"],
                    },
                ],
            },
        ]

        # ─────────────────────────────────────────────────────────────────────
        # RENDERING HELPERS
        # ─────────────────────────────────────────────────────────────────────
        def req_badge(r):
            if r == "required":
                return '<span class="req-badge req">required</span>'
            elif r in ("optional", ""):
                return '<span class="req-badge opt">optional</span>'
            else:
                return f'<span class="req-badge ctx">{e(r)}</span>'

        def render_param_table(params):
            if not params:
                return ""
            rows = ""
            for p in params:
                rows += (
                    f'<tr><td><code>{e(p["name"])}</code></td>'
                    f'<td>{req_badge(p["required"])}</td>'
                    f'<td class="values-cell">{e(p["values"])}</td>'
                    f'<td class="desc-cell">{p["desc"]}</td></tr>'
                )
            return (
                '<table class="param-table">'
                '<thead><tr><th>Parameter</th><th>Required</th>'
                '<th>Values / Type</th><th>Description</th></tr></thead>'
                f'<tbody>{rows}</tbody></table>'
            )

        def render_examples(examples):
            if not examples:
                return ""
            items = ""
            for ex_cmd, ex_desc in examples:
                items += (
                    f'<div class="ex-row">'
                    f'<code class="ex-cmd">{e(ex_cmd)}</code>'
                    f'<span class="ex-desc"># {e(ex_desc)}</span>'
                    f'</div>\n'
                )
            return f'<div class="examples-block"><div class="ex-label">Examples</div>{items}</div>'

        def render_notes(notes):
            if not notes:
                return ""
            items = "".join(f"<li>{n}</li>" for n in notes)
            return f'<ul class="cmd-notes">{items}</ul>'

        def render_see(see_ids):
            if not see_ids:
                return ""
            links = ", ".join(
                f'<a href="#{sid}">{e(sid.replace("-", " "))}</a>'
                for sid in see_ids
            )
            return f'<div class="cmd-see">See also: {links}</div>'

        def render_cmd(cmd):
            # Handle newlines in syntax for multi-line display
            syntax_esc = e(cmd["syntax"])
            return (
                f'<div class="cmd-entry" id="{e(cmd["id"])}">'
                f'<div class="cmd-header">'
                f'<span class="cmd-name">{e(cmd["name"])}</span>'
                f'<span class="cmd-brief"> &mdash; {e(cmd["brief"])}</span>'
                f'</div>'
                f'<div class="cmd-syntax"><code>{syntax_esc}</code></div>'
                f'<p class="cmd-desc">{cmd["desc"]}</p>'
                f'{render_param_table(cmd["params"])}'
                f'{render_examples(cmd["examples"])}'
                f'{render_notes(cmd["notes"])}'
                f'{render_see(cmd["see"])}'
                f'</div>'
            )

        def render_section(sec):
            cmds_html = "\n".join(render_cmd(c) for c in sec["commands"])
            return (
                f'<section id="{e(sec["id"])}">'
                f'<h2>{e(sec["title"])}</h2>'
                f'<p class="section-intro">{e(sec["intro"])}</p>'
                f'{cmds_html}'
                f'</section>'
            )

        # ── Sidebar ──────────────────────────────────────────────────────────
        sidebar_links = '<a href="#quick-start">Quick Start</a>\n'
        for sec in SECTIONS:
            sidebar_links += f'<a href="#{e(sec["id"])}">{e(sec["title"])}</a>\n'
            for cmd in sec["commands"]:
                sidebar_links += (
                    f'<a class="sub-link" href="#{e(cmd["id"])}">'
                    f'{e(cmd["name"])}</a>\n'
                )
        sidebar_links += '<a href="#examples">Examples</a>\n'
        sidebar_links += '<a href="#instruments">Instruments</a>\n'

        # ── Sections HTML ────────────────────────────────────────────────────
        sections_html = "\n".join(render_section(s) for s in SECTIONS)

        # ── Example workflows ────────────────────────────────────────────────
        def example_block(name, entry):
            lines_html = e("\n".join(entry["lines"]))
            return (
                f'<div class="example-block" id="ex-{e(name)}">'
                f'<div class="example-title">{e(name)}</div>'
                f'<div class="example-desc">{e(entry["description"])}</div>'
                f'<pre><code>{lines_html}</code></pre>'
                f'<div class="example-usage">'
                f'Load: <code>examples load {e(name)}</code>'
                f' &nbsp;|&nbsp; '
                f'Run: <code>script run {e(name)}</code>'
                f'</div>'
                f'</div>'
            )

        examples_html = "\n".join(
            example_block(n, ex) for n, ex in _EXAMPLES.items()
        )

        # ── Supported instruments ─────────────────────────────────────────────
        instruments = [
            ("Tektronix MSO2024",    "Oscilloscope",       "USB/GPIB"),
            ("Rigol DHO804",         "Oscilloscope",       "USB"),
            ("HP E3631A",            "Power Supply",       "GPIB"),
            ("Matrix MPS-6010H-1C",  "Power Supply",       "Serial"),
            ("HP 34401A",            "Multimeter",         "GPIB"),
            ("OWON XDM1041",         "Multimeter",         "USB/Serial"),
            ("BK Precision 4063",    "Function Generator", "USB"),
            ("Keysight EDU33212A",   "Function Generator", "USB"),
            ("JDS6600 (Seesii DDS)", "Function Generator", "Serial"),
        ]

        # ── Full HTML ─────────────────────────────────────────────────────────
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SCPI Instrument Toolkit v{e(ver)} &mdash; Command Reference</title>
<style>
  :root {{
    --bg: #0f0f1a; --bg2: #1a1a2e; --bg3: #16213e;
    --cyan: #00d4d4; --yellow: #f0c040; --green: #4ade80;
    --red: #f87171; --text: #d0d0e0; --muted: #7070a0;
    --border: #2a2a4a; --code-bg: #0d0d1a; --sidebar-w: 240px;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: var(--bg); color: var(--text); font-family: 'Consolas','Courier New',monospace; display: flex; min-height: 100vh; font-size: 14px; }}
  a {{ color: var(--cyan); text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  code {{ background: var(--code-bg); color: var(--cyan); padding: 1px 5px; border-radius: 3px; font-size: 0.9em; }}

  /* SIDEBAR */
  nav {{ width: var(--sidebar-w); background: var(--bg2); border-right: 1px solid var(--border); position: fixed; top: 0; left: 0; bottom: 0; overflow-y: auto; padding: 14px 0; z-index: 100; scrollbar-width: thin; }}
  nav .logo {{ padding: 0 14px 12px; border-bottom: 1px solid var(--border); margin-bottom: 6px; }}
  nav .logo .title {{ color: var(--cyan); font-size: 1em; font-weight: bold; }}
  nav .logo .ver {{ color: var(--muted); font-size: 0.72em; }}
  nav a {{ display: block; padding: 3px 14px; color: var(--muted); font-size: 0.8em; border-left: 2px solid transparent; transition: all 0.12s; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
  nav a:hover, nav a.active {{ color: var(--cyan); border-left-color: var(--cyan); background: rgba(0,212,212,0.06); text-decoration: none; }}
  nav a.sub-link {{ padding-left: 26px; font-size: 0.74em; color: #484870; }}
  nav a.sub-link:hover, nav a.sub-link.active {{ color: var(--cyan); }}

  /* MAIN */
  main {{ margin-left: var(--sidebar-w); padding: 30px 48px; max-width: 1020px; flex: 1; }}

  /* HEADINGS */
  h1 {{ color: var(--cyan); font-size: 1.55em; margin-bottom: 4px; }}
  h1 .ver {{ color: var(--muted); font-size: 0.52em; vertical-align: middle; margin-left: 10px; }}
  h2 {{ color: var(--cyan); font-size: 1.1em; margin: 0 0 5px; padding-bottom: 5px; border-bottom: 1px solid var(--border); }}
  p {{ line-height: 1.65; color: var(--text); margin-bottom: 8px; font-size: 0.9em; }}
  section {{ margin-bottom: 44px; scroll-margin-top: 14px; }}
  .section-intro {{ color: var(--muted); margin-bottom: 16px; font-size: 0.85em; }}

  /* COMMAND ENTRY */
  .cmd-entry {{ background: var(--bg2); border: 1px solid var(--border); border-radius: 6px; margin-bottom: 16px; padding: 14px 16px; scroll-margin-top: 14px; }}
  .cmd-header {{ margin-bottom: 7px; }}
  .cmd-name {{ color: var(--cyan); font-weight: bold; font-size: 0.98em; }}
  .cmd-brief {{ color: var(--muted); font-size: 0.85em; }}
  .cmd-syntax {{ background: var(--code-bg); border: 1px solid var(--border); border-radius: 4px; padding: 7px 12px; margin: 6px 0 9px; white-space: pre; overflow-x: auto; }}
  .cmd-syntax code {{ background: none; padding: 0; color: var(--yellow); font-size: 0.87em; }}
  .cmd-desc {{ font-size: 0.87em; margin-bottom: 9px; color: var(--text); line-height: 1.6; }}
  .cmd-desc code {{ background: none; color: var(--cyan); padding: 0; }}

  /* PARAM TABLE */
  .param-table {{ width: 100%; border-collapse: collapse; margin: 6px 0 10px; font-size: 0.82em; }}
  .param-table th {{ background: var(--bg3); color: var(--yellow); padding: 5px 10px; text-align: left; border: 1px solid var(--border); font-weight: normal; }}
  .param-table td {{ padding: 5px 10px; border: 1px solid var(--border); vertical-align: top; }}
  .param-table tr:nth-child(even) td {{ background: rgba(255,255,255,0.02); }}
  .param-table td:first-child {{ color: var(--cyan); white-space: nowrap; }}
  .param-table td code {{ background: none; color: var(--cyan); padding: 0; }}
  .param-table .values-cell {{ color: #9090c0; white-space: nowrap; font-size: 0.95em; }}
  .param-table .desc-cell {{ color: var(--text); line-height: 1.5; }}
  .param-table .desc-cell code {{ background: none; color: var(--cyan); padding: 0; }}

  /* REQUIRED BADGES */
  .req-badge {{ display: inline-block; padding: 1px 7px; border-radius: 8px; font-size: 0.78em; font-weight: bold; white-space: nowrap; }}
  .req-badge.req {{ background: rgba(248,113,113,0.12); color: var(--red); border: 1px solid var(--red); }}
  .req-badge.opt {{ background: rgba(74,222,128,0.08); color: var(--green); border: 1px solid var(--green); }}
  .req-badge.ctx {{ background: rgba(240,192,64,0.08); color: var(--yellow); border: 1px solid var(--yellow); }}

  /* EXAMPLES */
  .examples-block {{ background: var(--code-bg); border: 1px solid var(--border); border-radius: 4px; padding: 9px 12px; margin: 7px 0; }}
  .ex-label {{ color: var(--yellow); font-size: 0.78em; margin-bottom: 5px; }}
  .ex-row {{ display: flex; gap: 14px; margin-bottom: 2px; align-items: baseline; flex-wrap: wrap; }}
  .ex-cmd {{ color: var(--green); background: none; font-size: 0.85em; white-space: pre; padding: 0; }}
  .ex-desc {{ color: var(--muted); font-size: 0.82em; }}

  /* NOTES */
  .cmd-notes {{ margin: 7px 0; padding-left: 18px; font-size: 0.83em; }}
  .cmd-notes li {{ color: var(--text); margin-bottom: 3px; line-height: 1.5; }}
  .cmd-notes li code {{ background: none; color: var(--cyan); padding: 0; }}

  /* SEE ALSO */
  .cmd-see {{ font-size: 0.78em; color: var(--muted); margin-top: 7px; }}
  .cmd-see a {{ color: var(--cyan); }}

  /* QUICK START */
  .step {{ display: flex; gap: 12px; margin-bottom: 10px; padding: 11px 14px; background: var(--bg2); border-radius: 6px; border: 1px solid var(--border); align-items: flex-start; }}
  .step-num {{ flex-shrink: 0; width: 24px; height: 24px; background: var(--cyan); color: #000; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 0.8em; }}
  .step-body p {{ margin: 0; font-size: 0.87em; }}

  /* EXAMPLE WORKFLOWS */
  .example-block {{ background: var(--bg2); border: 1px solid var(--border); border-radius: 6px; margin-bottom: 16px; overflow: hidden; }}
  .example-title {{ background: var(--bg3); color: var(--cyan); font-weight: bold; padding: 8px 14px; font-size: 0.88em; }}
  .example-desc {{ color: var(--yellow); padding: 6px 14px 0; font-size: 0.8em; }}
  .example-block pre {{ margin: 7px 14px 0; border: none; background: var(--code-bg); padding: 9px; font-size: 0.8em; border-radius: 4px; overflow-x: auto; }}
  .example-block pre code {{ background: none; color: var(--text); padding: 0; }}
  .example-usage {{ color: var(--muted); font-size: 0.76em; padding: 6px 14px 10px; }}
  .example-usage code {{ color: var(--green); background: none; }}

  /* INSTRUMENTS TABLE */
  table.inst-table {{ width: 100%; border-collapse: collapse; margin: 8px 0; font-size: 0.84em; }}
  table.inst-table th {{ background: var(--bg3); color: var(--yellow); padding: 6px 12px; text-align: left; border: 1px solid var(--border); font-weight: normal; }}
  table.inst-table td {{ padding: 5px 12px; border: 1px solid var(--border); }}
  table.inst-table tr:nth-child(even) td {{ background: rgba(255,255,255,0.02); }}
  table.inst-table td:first-child {{ color: var(--cyan); }}
</style>
</head>
<body>

<nav>
  <div class="logo">
    <div class="title">SCPI Toolkit</div>
    <div class="ver">v{e(ver)} &mdash; Command Reference</div>
  </div>
  {sidebar_links}
</nav>

<main>
  <h1>SCPI Instrument Toolkit <span class="ver">v{e(ver)}</span></h1>
  <p>Python REPL for controlling lab instruments over VISA (USB, GPIB, Serial). Type <code>docs</code> in the REPL to open this page, or <code>help &lt;cmd&gt;</code> for quick inline help.</p>

  <section id="quick-start">
    <h2>Quick Start</h2>
    <div class="step"><div class="step-num">1</div><div class="step-body">
      <p><strong>Install:</strong> <code>pip install git+https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git</code></p>
    </div></div>
    <div class="step"><div class="step-num">2</div><div class="step-body">
      <p><strong>Launch:</strong> <code>scpi-repl</code> (auto-discovers instruments) &nbsp;&mdash;&nbsp; <code>scpi-repl --mock</code> (no hardware, for testing)</p>
    </div></div>
    <div class="step"><div class="step-num">3</div><div class="step-body">
      <p><strong>Identify:</strong> <code>list</code> shows connected instruments &mdash; <code>use psu1</code> makes psu1 active</p>
    </div></div>
    <div class="step"><div class="step-num">4</div><div class="step-body">
      <p><strong>Control:</strong> <code>psu chan 1 on</code> &rarr; <code>psu set 5.0</code> &rarr; <code>psu meas v</code></p>
    </div></div>
    <div class="step"><div class="step-num">5</div><div class="step-body">
      <p><strong>Log:</strong> <code>psu meas_store v reading unit=V</code> &rarr; <code>log print</code> &rarr; <code>log save results.csv</code></p>
    </div></div>
  </section>

  {sections_html}

  <section id="examples">
    <h2>Example Workflows</h2>
    <p>Load any example into your session with <code>examples load &lt;name&gt;</code>, then run with <code>script run &lt;name&gt;</code>. Use as starting points for your own scripts.</p>
    {examples_html}
  </section>

  <section id="instruments">
    <h2>Supported Instruments</h2>
    <table class="inst-table">
      <tr><th>Model</th><th>Type</th><th>Interface</th></tr>
      {"".join(f"<tr><td>{e(m)}</td><td>{e(t)}</td><td>{e(i)}</td></tr>" for m, t, i in instruments)}
    </table>
    <p style="color:var(--muted);font-size:0.8em;margin-top:6px;">Auto-detected on <code>scan</code>. Serial resources are probed with multiple baud rates automatically.</p>
  </section>
</main>

<script>
const allLinks = document.querySelectorAll('nav a[href^="#"]');
const allTargets = [...document.querySelectorAll('section[id], .cmd-entry[id]')];
const io = new IntersectionObserver(entries => {{
  entries.forEach(entry => {{
    if (entry.isIntersecting) {{
      allLinks.forEach(l => l.classList.remove('active'));
      const link = document.querySelector(`nav a[href="#${{entry.target.id}}"]`);
      if (link) link.classList.add('active');
    }}
  }});
}}, {{ threshold: 0.15, rootMargin: '-30px 0px -65% 0px' }});
allTargets.forEach(t => io.observe(t));
</script>
</body>
</html>"""

    def do_all(self, arg):
        "all <on|off|safe|reset>: apply a state to all instruments"
        args = self._parse_args(arg)
        args, help_flag = self._strip_help(args)
        if not args or help_flag:
            self._print_usage(
                [
                    "all on",
                    "all off",
                    "all safe",
                    "all reset",
                ]
            )
            return
        state = args[0].lower()
        if state == "on":
            self._on_all()
        elif state == "off":
            self._off_all()
        elif state == "safe":
            self._safe_all()
        elif state == "reset":
            self._reset_all()
        else:
            ColorPrinter.warning("Use: all on|off|safe|reset")

    def do_exit(self, arg):
        "exit: quit the REPL"
        return True

    def do_EOF(self, arg):
        print()
        return True

    def do_help(self, arg):
        "help [command]: show help for a command, or list all commands"
        if arg:
            # Per-command help: show docstring, colorized
            try:
                func = getattr(self, f"help_{arg}")
                func()
                return
            except AttributeError:
                pass
            try:
                doc = getattr(self, f"do_{arg}").__doc__
            except AttributeError:
                doc = None
            if doc:
                # First token of docstring is the usage signature — print it in cyan
                lines = doc.strip().splitlines()
                first = lines[0]
                rest = lines[1:]
                print(f"{ColorPrinter.CYAN}{first}{ColorPrinter.RESET}")
                for line in rest:
                    print(line)
            else:
                ColorPrinter.warning(f"No help for '{arg}'.")
            return

        # Full listing — grouped by category
        C = ColorPrinter.CYAN
        Y = ColorPrinter.YELLOW
        B = ColorPrinter.BOLD
        R = ColorPrinter.RESET

        def section(title):
            print(f"\n{Y}{B}{title}{R}")

        def cmd_line(name, desc):
            print(f"  {C}{name:<12}{R} {desc}")

        print(f"{B}ESET Instrument REPL{R} {Y}v{_REPL_VERSION}{R}  —  type {C}help <command>{R} for details\n")

        section("GENERAL")
        cmd_line("scan",    "discover and connect to instruments")
        cmd_line("reload",  "restart the REPL process")
        cmd_line("list",    "show connected instruments")
        cmd_line("use",     "set active instrument  (use <name>)")
        cmd_line("status",  "show current selection")
        cmd_line("state",   "set instrument state  (safe/reset/on/off)")
        cmd_line("all",     "apply state to all instruments")
        cmd_line("idn",     "query *IDN?")
        cmd_line("raw",     "send raw SCPI command or query")
        cmd_line("sleep",   "pause between actions  (sleep <seconds>)")
        cmd_line("wait",    "alias for sleep")
        cmd_line("version", "show toolkit version")
        cmd_line("close",   "disconnect all instruments")
        cmd_line("exit",    "quit the REPL")
        cmd_line("quit",    "quit the REPL")

        section("INSTRUMENTS")
        cmd_line("psu",     "power supply  (chan, set, meas, track, save, recall)")
        cmd_line("awg",     "function generator  (chan, wave, freq, amp, offset, duty, phase)")
        cmd_line("dmm",     "multimeter  (config, read, fetch, meas, beep, display)")
        cmd_line("scope",   "oscilloscope  (chan, meas, save, trigger, awg, dvm, counter)")

        section("SCRIPTING")
        cmd_line("script",    "manage and run named scripts  (new, run, edit, list, rm, show, import, load, save)")
        cmd_line("examples",  "list or load bundled example workflows  (load <name> | load all)")
        cmd_line("python",    "execute an external Python script with REPL context")
        cmd_line("docs",      "open full HTML documentation in your browser")

        section("LOGGING & MATH")
        cmd_line("log",     "show or save recorded measurements  (print, save, clear)")
        cmd_line("calc",    "compute a value from logged measurements")

        print()

    # --------------------------
    # PSU commands
    # --------------------------
    def do_psu(self, arg):
        "psu <cmd>: control the power supply (output, set, meas, track, save, recall)"
        # Resolve which PSU to use (auto-select if only one)
        psu_name = self._resolve_device_type("psu")
        if not psu_name:
            return

        dev = self._get_device(psu_name)
        if not dev:
            return

        # Detect single-channel by checking if measure_voltage() takes a channel arg
        try:
            sig = inspect.signature(dev.measure_voltage)
            is_single_channel = "channel" not in sig.parameters
        except (ValueError, TypeError):
            is_single_channel = False
        return self._handle_psu_unified(arg, dev, psu_name, is_single_channel)

    def _handle_psu_unified(self, arg, dev, psu_name, is_single_channel):
        """Unified PSU command handler for all PSU types"""
        args = self._parse_args(arg)
        args, help_flag = self._strip_help(args)

        if not args:
            if is_single_channel:
                self._print_colored_usage(
                    [
                        "# PSU",
                        "",
                        "psu chan 1 on|off",
                        "psu set <voltage> [current]",
                        "  - voltage: 0-60V, current: 0-10A",
                        "  - example: psu set 5.0 1.0",
                        "psu meas v|i",
                        "psu meas_store v|i <label> [unit=]",
                        "psu get  (show setpoints)",
                        "psu state on|off|safe|reset",
                    ]
                )
            else:
                self._print_colored_usage(
                    [
                        "# PSU",
                        "",
                        "psu chan <1|2|3|all> on|off",
                        "psu set <channel> <voltage> [current]",
                        "  - channels: 1 (6V), 2 (25V+), 3 (25V-)",
                        "  - example: psu set 1 5.0 0.2",
                        "  - example: psu set 2 12.0 0.5",
                        "psu meas v|i <channel>",
                        "  - example: psu meas v 1",
                        "psu meas_store v|i <channel> <label> [unit=]",
                        "psu track on|off",
                        "psu save <1-3>",
                        "psu recall <1-3>",
                        "psu state on|off|safe|reset",
                    ]
                )
            return

        cmd_name = args[0].lower()

        try:
            # CHAN COMMAND — psu chan 1 on|off (single) or psu chan <1|2|3|all> on|off (multi)
            if cmd_name == "chan" and len(args) >= 3:
                state = args[-1].lower() == "on"
                dev.enable_output(state)
                ColorPrinter.success(f"Output {'enabled' if state else 'disabled'}")

            # SET COMMAND - unified for both single and multi-channel
            elif cmd_name == "set":
                if is_single_channel:
                    # Single-channel: psu set <voltage> [current]
                    if len(args) < 2:
                        ColorPrinter.warning("Usage: psu set <voltage> [current]")
                        return
                    voltage = float(args[1])
                    current = float(args[2]) if len(args) >= 3 else None
                    dev.set_voltage(voltage)
                    if current is not None:
                        dev.set_current_limit(current)
                    ColorPrinter.success(
                        f"Set: {voltage}V @ {current if current else dev.get_current_limit()}A"
                    )
                else:
                    # Multi-channel: psu set <channel> <voltage> [current]
                    if len(args) < 3:
                        ColorPrinter.warning("Usage: psu set <channel> <voltage> [current]")
                        ColorPrinter.warning("Channels: 1 (6V), 2 (25V+), 3 (25V-)")
                        return
                    channel = PSU_CHANNEL_ALIASES.get(args[1].lower())
                    if not channel:
                        ColorPrinter.warning("Invalid channel. Use 1, 2, or 3")
                        return
                    voltage = float(args[2])
                    current = float(args[3]) if len(args) >= 4 else None
                    dev.set_output_channel(channel, voltage, current)
                    ColorPrinter.success(f"Set {args[1].upper()}: {voltage}V" + (f" @ {current}A" if current else ""))

            # MEAS COMMAND - unified for both single and multi-channel
            elif cmd_name == "meas":
                if is_single_channel:
                    # Single-channel: psu meas v|i
                    if len(args) < 2:
                        ColorPrinter.warning("Usage: psu meas v|i")
                        return
                    mode = args[1].lower()
                    if mode in ("v", "volt", "voltage"):
                        value = dev.measure_voltage()
                        ColorPrinter.cyan(f"{value:.6f}V")
                    elif mode in ("i", "curr", "current"):
                        value = dev.measure_current()
                        ColorPrinter.cyan(f"{value:.6f}A")
                    else:
                        ColorPrinter.warning("psu meas v|i")
                else:
                    # Multi-channel: psu meas v|i <channel>
                    if len(args) < 3:
                        ColorPrinter.warning("Usage: psu meas v|i <channel>")
                        return
                    mode = args[1].lower()
                    channel = PSU_CHANNEL_ALIASES.get(args[2].lower())
                    if not channel:
                        ColorPrinter.warning("Invalid channel. Use 1, 2, or 3")
                        return
                    if mode in ("v", "volt", "voltage"):
                        ColorPrinter.cyan(str(dev.measure_voltage(channel)))
                    elif mode in ("i", "curr", "current"):
                        ColorPrinter.cyan(str(dev.measure_current(channel)))
                    else:
                        ColorPrinter.warning("psu meas v|i <channel>")

            # MEAS_STORE COMMAND - unified for both single and multi-channel
            elif cmd_name == "meas_store":
                unit = ""
                if is_single_channel:
                    # Single-channel: psu meas_store v|i <label> [unit=]
                    if len(args) < 3:
                        ColorPrinter.warning("Usage: psu meas_store v|i <label> [unit=]")
                        return
                    mode = args[1].lower()
                    label = args[2]
                    for token in args[3:]:
                        if token.lower().startswith("unit="):
                            unit = token.split("=", 1)[1]
                    if mode in ("v", "volt", "voltage"):
                        value = dev.measure_voltage()
                        unit = unit or "V"
                    elif mode in ("i", "curr", "current"):
                        value = dev.measure_current()
                        unit = unit or "A"
                    else:
                        ColorPrinter.warning("psu meas_store v|i <label>")
                        return
                    self._record_measurement(label, value, unit, "psu.meas")
                    ColorPrinter.cyan(str(value))
                else:
                    # Multi-channel: psu meas_store v|i <channel> <label> [unit=]
                    if len(args) < 4:
                        ColorPrinter.warning("Usage: psu meas_store v|i <channel> <label> [unit=]")
                        return
                    mode = args[1].lower()
                    channel = PSU_CHANNEL_ALIASES.get(args[2].lower())
                    label = args[3]
                    for token in args[4:]:
                        token_lower = token.lower()
                        if token_lower.startswith("unit="):
                            unit = token.split("=", 1)[1]
                    if not channel:
                        ColorPrinter.warning("Invalid channel. Use 1, 2, or 3")
                        return
                    if mode in ("v", "volt", "voltage"):
                        value = dev.measure_voltage(channel)
                    elif mode in ("i", "curr", "current"):
                        value = dev.measure_current(channel)
                    else:
                        ColorPrinter.warning("psu meas_store v|i <channel> <label>")
                        return
                    self._record_measurement(label, value, unit, "psu.meas")
                    ColorPrinter.cyan(str(value))

            # GET COMMAND (single-channel only)
            elif cmd_name == "get":
                if is_single_channel:
                    v = dev.get_voltage_setpoint()
                    i = dev.get_current_limit()
                    out = "ON" if dev.get_output_state() else "OFF"
                    ColorPrinter.info(f"Setpoint: {v}V @ {i}A, Output: {out}")
                else:
                    ColorPrinter.warning("'get' command not available for multi-channel PSU")

            # TRACK COMMAND (multi-channel only)
            elif cmd_name == "track" and len(args) >= 2:
                if not is_single_channel:
                    dev.set_tracking(args[1].lower() == "on")
                else:
                    ColorPrinter.warning("'track' command not available for single-channel PSU")

            # SAVE/RECALL COMMANDS (multi-channel only)
            elif cmd_name == "save" and len(args) >= 2:
                if not is_single_channel:
                    dev.save_state(int(args[1]))
                else:
                    ColorPrinter.warning("'save' command not available for single-channel PSU")
            elif cmd_name == "recall" and len(args) >= 2:
                if not is_single_channel:
                    dev.recall_state(int(args[1]))
                else:
                    ColorPrinter.warning("'recall' command not available for single-channel PSU")

            # STATE COMMAND
            elif cmd_name == "state" and len(args) >= 2:
                self.do_state(f"{psu_name} {args[1]}")

            else:
                ColorPrinter.warning(f"Unknown PSU command: psu {arg}. Type 'psu' for help.")

        except Exception as exc:
            ColorPrinter.error(str(exc))

    # --------------------------
    # AWG commands
    # --------------------------
    def do_awg(self, arg):
        "awg <cmd>: control the function generator (output, wave, freq, amp, etc.)"
        # Resolve which AWG/DDS to use (auto-select if only one)
        awg_name = self._resolve_device_type("awg")
        if not awg_name:
            return

        dev = self._get_device(awg_name)
        if not dev:
            return

        # Detect device type to route commands appropriately
        is_jds6600 = awg_name == 'dds' or 'JDS6600' in str(type(dev).__name__)

        args = self._parse_args(arg)
        args, help_flag = self._strip_help(args)

        if not args or help_flag:
            self._print_colored_usage(
                [
                    "# AWG",
                    "",
                    "awg chan <1|2|all> on|off",
                    "awg wave <1|2|all> <type> [freq=] [amp=] [offset=] [duty=] [phase=]",
                    "  - type: sine|square|ramp|triangle|pulse|noise|dc|arb",
                    "  - example: awg wave 1 sine freq=1000 amp=5.0 offset=2.5",
                    "  - example: awg wave all sine freq=1000",
                    "",
                    "awg freq <1|2|all> <Hz>",
                    "awg amp <1|2|all> <Vpp>",
                    "awg offset <1|2|all> <V>",
                    "awg duty <1|2|all> <%>",
                    "awg phase <1|2|all> <deg>",
                    "",
                    "awg sync on|off",
                    "awg state on|off|safe|reset",
                ]
            )
            return

        cmd_name = args[0].lower()

        try:
            # CHAN COMMAND — enable/disable a channel output
            if cmd_name == "chan" and len(args) >= 3:
                channels = self._parse_channels(args[1], max_ch=2)
                state = args[2].lower() == "on"
                for channel in channels:
                    if is_jds6600:
                        dev.enable_output(
                            ch1=state if channel == 1 else None,
                            ch2=state if channel == 2 else None,
                        )
                    else:
                        dev.enable_output(channel, state)
                    ColorPrinter.success(f"CH{channel}: {'on' if state else 'off'}")

            # WAVE COMMAND
            elif cmd_name == "wave" and len(args) >= 3:
                channels = self._parse_channels(args[1], max_ch=2)
                waveform = args[2].lower()

                params = {}
                for token in args[3:]:
                    if "=" in token:
                        key, value = token.split("=", 1)
                        params[key.lower()] = float(value)

                param_str = "  " + "  ".join(f"{k}={v}" for k, v in params.items()) if params else ""
                for channel in channels:
                    if is_jds6600:
                        dev.set_waveform(channel, waveform)
                        if "freq" in params or "frequency" in params:
                            dev.set_frequency(channel, params.get("freq", params.get("frequency")))
                        if "amp" in params or "amplitude" in params:
                            dev.set_amplitude(channel, params.get("amp", params.get("amplitude")))
                        if "offset" in params:
                            dev.set_offset(channel, params["offset"])
                        if "duty" in params:
                            dev.set_duty_cycle(channel, params["duty"])
                        if "phase" in params:
                            dev.set_phase(channel, params["phase"])
                    else:
                        # Normalize to SCPI abbreviations: "sine" → "SIN", "square" → "SQU", etc.
                        scpi_wave = AWG_WAVE_ALIASES.get(waveform, waveform.upper())
                        kwargs = {}
                        for key, value in params.items():
                            mapped_key = AWG_WAVE_KEYS.get(key)
                            if mapped_key:
                                kwargs[mapped_key] = value
                        dev.set_waveform(channel, scpi_wave, **kwargs)
                    ColorPrinter.success(f"CH{channel}: {AWG_WAVE_ALIASES.get(waveform, waveform.upper())}{param_str}")

            # FREQ COMMAND
            elif cmd_name == "freq" and len(args) >= 3:
                channels = self._parse_channels(args[1], max_ch=2)
                frequency = float(args[2])
                if not is_jds6600 and not hasattr(dev, 'set_frequency'):
                    ColorPrinter.warning("Frequency not supported independently. Use 'awg wave' with freq=")
                    return
                for channel in channels:
                    dev.set_frequency(channel, frequency)
                    ColorPrinter.success(f"CH{channel}: {frequency} Hz")

            # AMP COMMAND
            elif cmd_name == "amp" and len(args) >= 3:
                channels = self._parse_channels(args[1], max_ch=2)
                amplitude = float(args[2])
                if not is_jds6600 and not hasattr(dev, 'set_amplitude'):
                    ColorPrinter.warning("Amplitude not supported independently. Use 'awg wave' with amp=")
                    return
                for channel in channels:
                    dev.set_amplitude(channel, amplitude)
                    ColorPrinter.success(f"CH{channel}: {amplitude} Vpp")

            # OFFSET COMMAND
            elif cmd_name == "offset" and len(args) >= 3:
                channels = self._parse_channels(args[1], max_ch=2)
                offset = float(args[2])
                if not is_jds6600 and not hasattr(dev, 'set_offset'):
                    ColorPrinter.warning("Offset not supported independently. Use 'awg wave' with offset=")
                    return
                for channel in channels:
                    dev.set_offset(channel, offset)
                    ColorPrinter.success(f"CH{channel}: offset {offset} V")

            # DUTY COMMAND
            elif cmd_name == "duty" and len(args) >= 3:
                channels = self._parse_channels(args[1], max_ch=2)
                duty = float(args[2])
                if not is_jds6600 and not hasattr(dev, 'set_duty_cycle'):
                    ColorPrinter.warning("Duty cycle not supported independently. Use 'awg wave' with duty=")
                    return
                for channel in channels:
                    dev.set_duty_cycle(channel, duty)
                    ColorPrinter.success(f"CH{channel}: duty {duty}%")

            # PHASE COMMAND
            elif cmd_name == "phase" and len(args) >= 3:
                channels = self._parse_channels(args[1], max_ch=2)
                phase = float(args[2])
                if not is_jds6600 and not hasattr(dev, 'set_phase'):
                    ColorPrinter.warning("Phase not supported independently. Use 'awg wave' with phase=")
                    return
                for channel in channels:
                    dev.set_phase(channel, phase)
                    ColorPrinter.success(f"CH{channel}: phase {phase} deg")

            # SYNC COMMAND
            elif cmd_name == "sync" and len(args) >= 2:
                state = args[1].lower() == "on"
                if hasattr(dev, 'set_sync_output'):
                    dev.set_sync_output(state)
                    ColorPrinter.success(f"Sync: {'on' if state else 'off'}")
                else:
                    ColorPrinter.warning("Sync output not available on this device.")

            # STATE COMMAND
            elif cmd_name == "state" and len(args) >= 2:
                self.do_state(f"{awg_name} {args[1]}")

            else:
                ColorPrinter.warning(f"Unknown AWG command: awg {arg}. Type 'awg' for help.")

        except ValueError as e:
            ColorPrinter.error(f"Invalid value: {e}")
        except Exception as exc:
            ColorPrinter.error(str(exc))

    # --------------------------
    # DMM commands
    # --------------------------
    def do_dmm(self, arg):
        "dmm <cmd>: control the multimeter (config, read, fetch, meas, beep, display)"
        # Resolve which DMM to use (auto-select if only one)
        dmm_name = self._resolve_device_type("dmm")
        if not dmm_name:
            return

        dev = self._get_device(dmm_name)
        if not dev:
            return

        # Use unified handler for all DMM types
        is_owon = dmm_name == "dmm_owon" or type(dev).__name__ == "Owon_XDM1041"
        return self._handle_dmm_unified(arg, dev, dmm_name, is_owon)

    def _handle_dmm_unified(self, arg, dev, dmm_name, is_owon):
        """Unified DMM command handler for all DMM types"""
        args = self._parse_args(arg)
        args, help_flag = self._strip_help(args)

        if not args:
            self._print_colored_usage(
                [
                    "# DMM",
                    "",
                    "dmm config <vdc|vac|idc|iac|res|fres|freq|per|cont|diode|cap|temp> [range] [res] [nplc=]",
                    "  - range/res/nplc are optional (auto-configured if not specified)",
                    "  - nplc=0.02|0.2|1|10|100 (DC only, if supported)",
                    "  - example: dmm config vdc",
                    "  - example: dmm config vdc 10 0.001 nplc=10",
                    "",
                    "dmm read",
                    "dmm meas_store <label> [scale=] [unit=]",
                    "dmm fetch",
                    "dmm meas <mode> [range] [res]",
                    "dmm beep",
                    "dmm display on|off",
                    "dmm text <message> [scroll=auto|on|off] [delay=] [loops=] [pad=] [width=]",
                    "dmm ranges",
                    "dmm state safe|reset",
                ]
            )
            return

        cmd_name = args[0].lower()

        # Show ranges (HP DMM only)
        if cmd_name in ("ranges", "limits"):
            if not is_owon:
                C = ColorPrinter.CYAN
                Y = ColorPrinter.YELLOW
                G = ColorPrinter.GREEN
                R = ColorPrinter.RESET
                B = ColorPrinter.BOLD
                print(f"\n{B}Valid DMM ranges / res / nplc  (HP 34401A){R}\n")
                rows = [
                    ("vdc",      "0.1 | 1 | 10 | 100 | 1000",          "numeric",  "0.02 | 0.2 | 1 | 10 | 100"),
                    ("vac",      "0.1 | 1 | 10 | 100 | 750",           "numeric",  "—"),
                    ("idc",      "0.01 | 0.1 | 1 | 3",                 "numeric",  "0.02 | 0.2 | 1 | 10 | 100"),
                    ("iac",      "0.01 | 0.1 | 1 | 3",                 "numeric",  "—"),
                    ("res/fres", "100 | 1k | 10k | 100k | 1M | 10M | 100M", "numeric", "—"),
                    ("freq/per", "0.1 | 1 | 10 | 100 | 750",           "numeric",  "—"),
                    ("cont/diode","fixed (no args)",                    "—",        "—"),
                ]
                hdr = f"  {Y}{'Mode':<10}{R} {G}{'Range':<42}{R} {'Res':<10} {'nplc'}"
                print(hdr)
                print(f"  {Y}{'-'*10}{R} {G}{'-'*42}{R} {'-'*10} {'-'*26}")
                for mode, rng, res, nplc in rows:
                    print(f"  {C}{mode:<10}{R} {rng:<42} {res:<10} {nplc}")
                print(f"\n  All range/res args also accept: {Y}MIN | MAX | DEF | AUTO{R}\n")
            else:
                ColorPrinter.info("Owon DMM auto-configures ranges. No manual range specification needed.")
            return

        try:
            # CONFIG COMMAND - unified for both HP and Owon
            if cmd_name in ("config", "mode") and len(args) >= 2:
                mode_arg = args[1].lower()
                mode = DMM_MODE_ALIASES.get(mode_arg, mode_arg)

                if is_owon:
                    # Owon: Simple mode setting only
                    dev.set_mode(mode_arg)
                    ColorPrinter.success(f"Mode set to: {mode_arg}")
                else:
                    # HP: Support range/resolution/nplc parameters (optional)
                    if not mode or mode not in DMM_MODE_ALIASES.values():
                        # Try without alias
                        mode = mode_arg

                    func = getattr(dev, f"configure_{mode}", None)
                    if not func:
                        ColorPrinter.warning(f"Invalid mode '{mode_arg}'. Type 'dmm' for options.")
                        return

                    # Handle modes that don't take parameters
                    if mode in ("continuity", "diode"):
                        func()
                        ColorPrinter.success(f"Configured for {mode}")
                        return

                    # Parse optional parameters
                    range_val = "DEF"
                    resolution = "DEF"
                    nplc = None
                    positional = []

                    for token in args[2:]:
                        token_lower = token.lower()
                        if token_lower.startswith("nplc="):
                            nplc = float(token.split("=", 1)[1])
                        elif token_lower.startswith("range="):
                            range_val = token.split("=", 1)[1]
                        elif token_lower.startswith(("res=", "resolution=")):
                            resolution = token.split("=", 1)[1]
                        else:
                            positional.append(token)

                    if positional:
                        range_val = positional[0]
                    if len(positional) >= 2:
                        resolution = positional[1]

                    # Call configure function with appropriate parameters
                    if nplc is not None:
                        func(range_val, resolution, nplc)
                    else:
                        func(range_val, resolution)
                    ColorPrinter.success(f"Configured for {mode}")

            # READ COMMAND
            elif cmd_name == "read":
                ColorPrinter.cyan(str(dev.read()))

            # MEAS_STORE COMMAND
            elif cmd_name == "meas_store" and len(args) >= 2:
                label = args[1]
                scale = 1.0
                unit = ""
                for token in args[2:]:
                    token_lower = token.lower()
                    if token_lower.startswith("scale="):
                        scale = float(token.split("=", 1)[1])
                    elif token_lower.startswith("unit="):
                        unit = token.split("=", 1)[1]
                value = dev.read()
                scaled = value * scale
                self._record_measurement(label, scaled, unit, "dmm.read")
                ColorPrinter.cyan(str(scaled))

            # FETCH COMMAND (HP only)
            elif cmd_name == "fetch":
                if hasattr(dev, 'fetch'):
                    ColorPrinter.cyan(str(dev.fetch()))
                else:
                    ColorPrinter.warning("'fetch' command not available on this DMM")

            # MEAS COMMAND
            elif cmd_name == "meas" and len(args) >= 2:
                mode_arg = args[1].lower()
                mode = DMM_MODE_ALIASES.get(mode_arg, mode_arg)

                if is_owon:
                    # Owon: Set mode then read
                    dev.set_mode(mode_arg)
                    ColorPrinter.cyan(str(dev.read()))
                else:
                    # HP: Use measure function
                    if not mode or mode not in DMM_MODE_ALIASES.values():
                        mode = mode_arg

                    func = getattr(dev, f"measure_{mode}", None)
                    if not func:
                        ColorPrinter.warning(f"Invalid mode '{mode_arg}'. Type 'dmm' for options.")
                        return

                    # Parse optional range/resolution parameters
                    range_val = args[2] if len(args) >= 3 else "DEF"
                    resolution = args[3] if len(args) >= 4 else "DEF"

                    if "continuity" in mode or "diode" in mode:
                        ColorPrinter.cyan(str(func()))
                    else:
                        ColorPrinter.cyan(str(func(range_val, resolution)))

            # BEEP COMMAND
            elif cmd_name == "beep":
                if hasattr(dev, 'beep'):
                    dev.beep()
                else:
                    ColorPrinter.warning("'beep' command not available on this DMM")

            # DISPLAY COMMAND
            elif cmd_name == "display" and len(args) >= 2:
                if hasattr(dev, 'set_display'):
                    dev.set_display(args[1].lower() == "on")
                else:
                    ColorPrinter.warning("'display' command not available on this DMM")

            # TEXT COMMAND (HP only)
            elif cmd_name == "text":
                if not is_owon and hasattr(dev, 'display_text'):
                    if len(args) < 2:
                        ColorPrinter.warning("Usage: dmm text <message> [scroll=] [delay=] [loops=] [pad=] [width=]")
                        return
                    msg_parts = []
                    options = {}
                    for token in args[1:]:
                        if "=" in token:
                            key, value = token.split("=", 1)
                            options[key.lower()] = value
                        else:
                            msg_parts.append(token)
                    message = " ".join(msg_parts)
                    scroll_mode = options.get("scroll", "auto").lower()
                    width = int(options.get("width", 12))
                    delay = float(options.get("delay", 0.2))
                    pad = int(options.get("pad", 4))
                    loops = int(options.get("loops", 1))
                    if scroll_mode == "off":
                        dev.display_text(message)
                    elif scroll_mode == "on":
                        dev.display_text_scroll(message, delay, pad, width, loops)
                    else:
                        if len(message) > width:
                            dev.display_text_scroll(message, delay, pad, width, loops)
                        else:
                            dev.display_text(message)
                else:
                    ColorPrinter.warning("'text' command not available on this DMM")

            # TEXT_LOOP COMMAND (HP only)
            elif cmd_name == "text_loop":
                if not is_owon:
                    if len(args) >= 2 and args[1].lower() == "off":
                        self._dmm_text_loop_active = False
                        if hasattr(dev, 'clear_display'):
                            dev.clear_display()
                        ColorPrinter.info("Text loop stopped")
                    elif len(args) >= 2:
                        msg_parts = []
                        options = {}
                        for token in args[1:]:
                            if "=" in token:
                                key, value = token.split("=", 1)
                                options[key.lower()] = value
                            else:
                                msg_parts.append(token)
                        message = " ".join(msg_parts)
                        delay = float(options.get("delay", 0.2))
                        pad = int(options.get("pad", 4))
                        width = int(options.get("width", 12))
                        # Generate scroll frames
                        padded = (" " * pad) + message + (" " * pad)
                        frames = [padded[i:i+width] for i in range(len(padded) - width + 1)]
                        self._dmm_text_frames = frames
                        self._dmm_text_index = 0
                        self._dmm_text_delay = delay
                        self._dmm_text_last = time.time()
                        self._dmm_text_loop_active = True
                        ColorPrinter.info(f"Text loop started: '{message}'")
                    else:
                        ColorPrinter.warning("Usage: dmm text_loop <message> [delay=] [pad=] [width=]")
                else:
                    ColorPrinter.warning("'text_loop' command not available on this DMM")

            # CLEARTEXT COMMAND (HP only)
            elif cmd_name == "cleartext":
                if not is_owon and hasattr(dev, 'clear_display'):
                    dev.clear_display()
                else:
                    ColorPrinter.warning("'cleartext' command not available on this DMM")

            # STATE COMMAND
            elif cmd_name == "state" and len(args) >= 2:
                self.do_state(f"{dmm_name} {args[1]}")

            else:
                ColorPrinter.warning(f"Unknown DMM command: dmm {arg}. Type 'dmm' for help.")

        except Exception as exc:
            ColorPrinter.error(str(exc))

    # --------------------------
    # Scope commands
    # --------------------------
    def do_scope(self, arg):
        "scope <cmd>: control the oscilloscope (autoset, run, stop, single, chan, coupling, probe, hscale, vscale, vpos, vmove, hpos, hmove, meas, save, trigger, awg)"
        # Resolve which scope to use (auto-select if only one)
        scope_name = self._resolve_device_type("scope")
        if not scope_name:
            return

        dev = self._get_device(scope_name)
        if not dev:
            return

        args = self._parse_args(arg)
        args, help_flag = self._strip_help(args)
        if not args:
            self._print_colored_usage(
                [
                    "# SCOPE",
                    "",
                    "scope autoset",
                    "scope run - start/resume continuous acquisition",
                    "scope stop - pause acquisition (freeze current display)",
                    "scope single - arm single-shot trigger (capture one event and stop)",
                    "",
                    "scope chan <1-4|all> on|off",
                    "scope coupling <1-4|all> <DC|AC|GND>",
                    "  - example: scope coupling 1 AC",
                    "  - example: scope coupling all DC",
                    "scope probe <1-4|all> <attenuation> - set probe attenuation (1, 10, 100, etc.)",
                    "  - example: scope probe 1 10",
                    "",
                    "scope hscale <seconds_per_div>",
                    "  - example: scope hscale 1e-3",
                    "scope hpos <percentage> - set horizontal position (0-100%)",
                    "scope hmove <delta> - move horizontal position by delta",
                    "",
                    "scope vscale <1-4|all> <volts_per_div> [pos]",
                    "  - example: scope vscale 1 0.5 0",
                    "  - example: scope vscale all 1.0",
                    "scope vpos <1-4|all> <divisions> - set vertical position",
                    "scope vmove <1-4|all> <delta> - move vertical position by delta",
                    "",
                    "scope trigger <chan> <level> [slope=RISE] [mode=AUTO]",
                    "",
                    "scope meas <1-4|all> <type> - measure waveform parameter",
                    "  - types: FREQUENCY, PK2PK, RMS, MEAN, PERIOD, MINIMUM, MAXIMUM",
                    "  - types: RISE, FALL, AMPLITUDE, HIGH, LOW, PWIDTH, NWIDTH, CRMS",
                    "  - example: scope meas 1 FREQUENCY",
                    "  - example: scope meas all PK2PK",
                    "scope meas_store <1-4|all> <type> <label> [unit=]",
                    "scope meas_delay <ch1> <ch2> [edge1=RISE] [edge2=RISE] [direction=FORWARDS]",
                    "scope meas_delay_store <ch1> <ch2> <label> [edge1=RISE] [edge2=RISE] [direction=FORWARDS] [unit=]",
                    "",
                    "scope save <channels> <filename> [record=<secs>] [time=<secs>] [points=<n>]",
                    "  - channels: single channel (1-4) or comma-separated list (1,3)",
                    "  - record=<secs>: WAIT and record for X seconds before saving",
                    "  - time=<secs>: filter to last X seconds of buffer (no waiting)",
                    "  - points=<n>: limit to specific number of points",
                    "  - example: scope save 1 ch1_data.csv",
                    "  - example: scope save 1,3 data.csv record=15  (wait 15s then save)",
                    "  - example: scope save 2 output.csv time=5 (filter to last 5s)",
                    "  - example: scope save 2 output.csv points=1000",
                    "",
                    "scope awg <subcmd> - built-in AWG control (type 'scope awg' for help)",
                    "scope counter <subcmd> - frequency counter (type 'scope counter' for help)",
                    "scope dvm <subcmd> - digital voltmeter (type 'scope dvm' for help)",
                    "scope state on|off|safe|reset",
                ]
            )
            return

        cmd_name = args[0].lower()
        if help_flag:
            self._print_usage(["scope ... (see main help)"])
            return
        try:
            if cmd_name == "autoset":
                dev.autoset()
                ColorPrinter.success("Autoset complete")
            elif cmd_name == "run":
                dev.run()
                ColorPrinter.success("Acquisition running")
            elif cmd_name == "stop":
                dev.stop()
                ColorPrinter.success("Acquisition stopped")
            elif cmd_name == "single":
                dev.single()
                ColorPrinter.success("Single shot armed")
            elif cmd_name == "chan" and len(args) >= 3:
                channels = self._parse_channels(args[1], max_ch=4)
                enable = args[2].lower() == "on"
                for channel in channels:
                    if enable:
                        dev.enable_channel(channel)
                        ColorPrinter.success(f"CH{channel}: on")
                    else:
                        dev.disable_channel(channel)
                        ColorPrinter.info(f"CH{channel}: off")
            elif cmd_name == "coupling" and len(args) >= 3:
                channels = self._parse_channels(args[1], max_ch=4)
                coupling_type = args[2].upper()
                for channel in channels:
                    dev.set_coupling(channel, coupling_type)
                    ColorPrinter.success(f"CH{channel}: coupling {coupling_type}")
            elif cmd_name == "probe" and len(args) >= 3:
                channels = self._parse_channels(args[1], max_ch=4)
                attenuation = float(args[2])
                for channel in channels:
                    dev.set_probe_attenuation(channel, attenuation)
                    ColorPrinter.success(f"CH{channel} probe attenuation set to {attenuation}x")
            elif cmd_name == "hscale" and len(args) >= 2:
                scale = float(args[1])
                dev.set_horizontal_scale(scale)
                ColorPrinter.success(f"Horizontal scale set to {scale} s/div")
            elif cmd_name == "hpos" and len(args) >= 2:
                position = float(args[1])
                dev.set_horizontal_position(position)
                ColorPrinter.success(f"Horizontal position set to {position}%")
            elif cmd_name == "hmove" and len(args) >= 2:
                delta = float(args[1])
                dev.move_horizontal(delta)
                ColorPrinter.success(f"Horizontal position moved by {delta}")
            elif cmd_name == "vscale" and len(args) >= 3:
                channels = self._parse_channels(args[1], max_ch=4)
                scale = float(args[2])
                position = float(args[3]) if len(args) >= 4 else 0.0
                for channel in channels:
                    dev.set_vertical_scale(channel, scale, position)
                    ColorPrinter.success(f"CH{channel} vertical scale set to {scale} V/div")
            elif cmd_name == "vpos" and len(args) >= 3:
                channels = self._parse_channels(args[1], max_ch=4)
                position = float(args[2])
                for channel in channels:
                    dev.set_vertical_position(channel, position)
                    ColorPrinter.success(f"CH{channel} vertical position set to {position} div")
            elif cmd_name == "vmove" and len(args) >= 3:
                channels = self._parse_channels(args[1], max_ch=4)
                delta = float(args[2])
                for channel in channels:
                    dev.move_vertical(channel, delta)
                    ColorPrinter.success(f"CH{channel}: moved {delta} div")
            elif cmd_name == "trigger" and len(args) >= 3:
                channel = int(args[1])
                level = float(args[2])
                slope = args[3].upper() if len(args) >= 4 else "RISE"
                mode = args[4].upper() if len(args) >= 5 else "AUTO"
                dev.configure_trigger(channel, level, slope, mode)
                ColorPrinter.success(f"Trigger configured: CH{channel} @ {level}V, {slope}, {mode}")
            elif cmd_name == "meas":
                if len(args) < 3:
                    # Show available measurement types
                    ColorPrinter.warning("Missing arguments. Usage: scope meas <1-4> <type>")
                    self._print_colored_usage([
                        "",
                        "# AVAILABLE MEASUREMENT TYPES",
                        "",
                        "  - FREQUENCY   - signal frequency (Hz)",
                        "  - PK2PK       - peak-to-peak voltage",
                        "  - RMS         - RMS voltage",
                        "  - CRMS        - cyclic RMS voltage",
                        "  - MEAN        - average voltage",
                        "  - PERIOD      - signal period",
                        "  - AMPLITUDE   - signal amplitude",
                        "  - MINIMUM     - minimum voltage",
                        "  - MAXIMUM     - maximum voltage",
                        "  - HIGH        - high state level",
                        "  - LOW         - low state level",
                        "  - RISE        - rise time",
                        "  - FALL        - fall time",
                        "  - PWIDTH      - positive pulse width",
                        "  - NWIDTH      - negative pulse width",
                        "",
                        "  - example: scope meas 1 FREQUENCY",
                        "  - example: scope meas 2 PK2PK",
                    ])
                else:
                    channels = self._parse_channels(args[1], max_ch=4)
                    measure_type = args[2]
                    for channel in channels:
                        result = dev.measure_bnf(channel, measure_type)
                        ColorPrinter.cyan(f"CH{channel} {measure_type}: {result}")
            elif cmd_name == "meas_store" and len(args) >= 4:
                channels = self._parse_channels(args[1], max_ch=4)
                measure_type = args[2]
                label = args[3]
                unit = ""
                for token in args[4:]:
                    if token.lower().startswith("unit="):
                        unit = token.split("=", 1)[1]
                for channel in channels:
                    stored_label = f"{label}_ch{channel}" if len(channels) > 1 else label
                    val = dev.measure_bnf(channel, measure_type)
                    self._record_measurement(stored_label, val, unit, f"scope.meas.{measure_type}")
                    ColorPrinter.success(f"CH{channel} {measure_type}: {val} → stored as '{stored_label}'")
            elif cmd_name == "meas_delay" and len(args) >= 3:
                ch1 = int(args[1])
                ch2 = int(args[2])
                edge1 = args[3].upper() if len(args) >= 4 else "RISE"
                edge2 = args[4].upper() if len(args) >= 5 else "RISE"
                direction = args[5].upper() if len(args) >= 6 else "FORWARDS"
                ColorPrinter.cyan(str(dev.measure_delay(ch1, ch2, edge1, edge2, direction)))
            elif cmd_name == "meas_delay_store" and len(args) >= 4:
                ch1 = int(args[1])
                ch2 = int(args[2])
                label = args[3]
                edge1 = "RISE"
                edge2 = "RISE"
                direction = "FORWARDS"
                unit = "s"
                # Parse optional args
                # Expected order after label: [edge1] [edge2] [dir] [unit=]
                # But unit= can be anywhere
                optional_args = [a for a in args[4:] if not a.lower().startswith("unit=")]
                unit_args = [a for a in args[4:] if a.lower().startswith("unit=")]
                if unit_args:
                    unit = unit_args[0].split("=", 1)[1]

                if len(optional_args) >= 1: edge1 = optional_args[0].upper()
                if len(optional_args) >= 2: edge2 = optional_args[1].upper()
                if len(optional_args) >= 3: direction = optional_args[2].upper()

                val = dev.measure_delay(ch1, ch2, edge1, edge2, direction)
                self._record_measurement(label, val, unit, "scope.meas.delay")
                ColorPrinter.cyan(str(val))
            elif cmd_name == "save" and len(args) >= 3:
                channels_str = args[1]
                filename = args[2]

                # Parse optional parameters (time=X, points=N, record=X)
                max_points = None
                time_window = None
                record_duration = None
                for token in args[3:]:
                    if token.lower().startswith("time="):
                        time_window = float(token.split("=", 1)[1])
                    elif token.lower().startswith("points="):
                        max_points = int(token.split("=", 1)[1])
                    elif token.lower().startswith("record="):
                        record_duration = float(token.split("=", 1)[1])

                # If record= is specified, run scope and wait before saving
                if record_duration:
                    ColorPrinter.info(f"Recording for {record_duration} seconds...")
                    dev.run()  # Ensure scope is running
                    time.sleep(record_duration)  # Wait for the specified duration
                    ColorPrinter.success(f"Recording complete")

                # Parse channel list (supports single channel or comma-separated)
                if "," in channels_str:
                    # Multiple channels
                    channels = [int(ch.strip()) for ch in channels_str.split(",")]
                    dev.save_waveforms_csv(channels, filename, max_points=max_points, time_window=time_window)
                    channels_list = ",".join(str(ch) for ch in sorted(channels))
                    ColorPrinter.success(f"Waveforms from CH{channels_list} saved to {filename}")
                else:
                    # Single channel
                    channel = int(channels_str)
                    dev.save_waveform_csv(channel, filename, max_points=max_points, time_window=time_window)
                    ColorPrinter.success(f"Waveform from CH{channel} saved to {filename}")
            elif cmd_name == "awg":
                self._handle_scope_awg(dev, args[1:])
            elif cmd_name == "counter":
                self._handle_scope_counter(dev, args[1:])
            elif cmd_name == "dvm":
                self._handle_scope_dvm(dev, args[1:])
            elif cmd_name == "state" and len(args) >= 2:
                self.do_state(f"{scope_name} {args[1]}")
            else:
                ColorPrinter.warning(f"Unknown scope command: scope {arg}. Type 'scope' for help.")
        except Exception as exc:
            ColorPrinter.error(str(exc))

    def _handle_scope_awg(self, dev, args):
        """Handle built-in oscilloscope AWG commands (DHO914S/DHO924S)"""
        if not args:
            self._print_colored_usage(
                [
                    "# SCOPE AWG",
                    "",
                    "scope awg chan on|off - enable/disable AWG output",
                    "scope awg set <func> <freq> <amp> [offset=0] - quick config",
                    "  - func: SINusoid|SQUare|RAMP|DC|NOISe",
                    "  - freq: frequency in Hz",
                    "  - amp: amplitude in Vpp",
                    "  - example: scope awg set SINusoid 1000 2.0",
                    "",
                    "scope awg func <type> - set waveform function",
                    "scope awg freq <Hz> - set frequency",
                    "scope awg amp <Vpp> - set amplitude",
                    "scope awg offset <V> - set DC offset",
                    "scope awg phase <deg> - set phase (0-360)",
                    "scope awg duty <percent> - set square duty cycle",
                    "scope awg sym <percent> - set ramp symmetry",
                    "",
                    "scope awg mod on|off - enable/disable modulation",
                    "scope awg mod_type AM|FM|PM - set modulation type",
                ]
            )
            return

        try:
            cmd = args[0].lower()

            if cmd == "chan" and len(args) >= 2:
                dev.awg_set_output_enable(args[1].lower() == "on")
                ColorPrinter.success(f"AWG output {'enabled' if args[1].lower() == 'on' else 'disabled'}")

            elif cmd == "set" and len(args) >= 4:
                # Quick configuration: scope awg set SINusoid 1000 2.0 [offset=0]
                function = args[1]
                frequency = float(args[2])
                amplitude = float(args[3])
                offset = 0.0
                for token in args[4:]:
                    if token.lower().startswith("offset="):
                        offset = float(token.split("=", 1)[1])
                dev.awg_configure_simple(function, frequency, amplitude, offset, enable=True)
                ColorPrinter.success(f"AWG configured: {function} {frequency}Hz {amplitude}Vpp offset={offset}V")

            elif cmd == "func" and len(args) >= 2:
                dev.awg_set_function(args[1])
                ColorPrinter.success(f"AWG function: {args[1]}")

            elif cmd == "freq" and len(args) >= 2:
                freq = float(args[1])
                dev.awg_set_frequency(freq)
                ColorPrinter.success(f"AWG frequency: {freq} Hz")

            elif cmd == "amp" and len(args) >= 2:
                amp = float(args[1])
                dev.awg_set_amplitude(amp)
                ColorPrinter.success(f"AWG amplitude: {amp} Vpp")

            elif cmd == "offset" and len(args) >= 2:
                offset = float(args[1])
                dev.awg_set_offset(offset)
                ColorPrinter.success(f"AWG offset: {offset} V")

            elif cmd == "phase" and len(args) >= 2:
                phase = float(args[1])
                dev.awg_set_phase(phase)
                ColorPrinter.success(f"AWG phase: {phase}°")

            elif cmd == "duty" and len(args) >= 2:
                duty = float(args[1])
                dev.awg_set_square_duty(duty)
                ColorPrinter.success(f"AWG square duty: {duty}%")

            elif cmd == "sym" and len(args) >= 2:
                sym = float(args[1])
                dev.awg_set_ramp_symmetry(sym)
                ColorPrinter.success(f"AWG ramp symmetry: {sym}%")

            elif cmd == "mod" and len(args) >= 2:
                dev.awg_set_modulation_enable(args[1].lower() == "on")
                ColorPrinter.success(f"AWG modulation {'enabled' if args[1].lower() == 'on' else 'disabled'}")

            elif cmd == "mod_type" and len(args) >= 2:
                mod_type = args[1].upper()
                dev.awg_set_modulation_type(mod_type)
                ColorPrinter.success(f"AWG modulation type: {mod_type}")

            else:
                ColorPrinter.warning(f"Unknown AWG command: scope awg {' '.join(args)}. Type 'scope awg' for help.")

        except AttributeError:
            ColorPrinter.warning("AWG not supported on this oscilloscope model (requires DHO914S/DHO924S)")
        except Exception as exc:
            ColorPrinter.error(str(exc))

    def _handle_scope_counter(self, dev, args):
        """Handle oscilloscope frequency counter commands"""
        if not args:
            self._print_colored_usage(
                [
                    "# SCOPE COUNTER",
                    "",
                    "scope counter on|off - enable/disable counter",
                    "scope counter read - read current frequency",
                    "scope counter source <1-4> - set source channel",
                    "scope counter mode <freq|period|totalize> - set mode",
                ]
            )
            return

        try:
            cmd = args[0].lower()

            if cmd in ("on", "off"):
                dev.set_counter_enable(cmd == "on")
                ColorPrinter.success(f"Counter {'enabled' if cmd == 'on' else 'disabled'}")

            elif cmd == "read":
                value = dev.get_counter_current()
                ColorPrinter.cyan(f"Counter: {value}")

            elif cmd == "source" and len(args) >= 2:
                channel = int(args[1])
                dev.set_counter_source(channel)
                ColorPrinter.success(f"Counter source: CH{channel}")

            elif cmd == "mode" and len(args) >= 2:
                mode = args[1].upper()
                dev.set_counter_mode(mode)
                ColorPrinter.success(f"Counter mode: {mode}")

            else:
                ColorPrinter.warning(f"Unknown counter command: scope counter {' '.join(args)}. Type 'scope counter' for help.")

        except AttributeError:
            ColorPrinter.warning("Counter not supported on this oscilloscope")
        except Exception as exc:
            ColorPrinter.error(str(exc))

    def _handle_scope_dvm(self, dev, args):
        """Handle oscilloscope digital voltmeter commands"""
        if not args:
            self._print_colored_usage(
                [
                    "# SCOPE DVM",
                    "",
                    "scope dvm on|off - enable/disable DVM",
                    "scope dvm read - read current voltage",
                    "scope dvm source <1-4> - set source channel",
                ]
            )
            return

        try:
            cmd = args[0].lower()

            if cmd in ("on", "off"):
                dev.set_dvm_enable(cmd == "on")
                ColorPrinter.success(f"DVM {'enabled' if cmd == 'on' else 'disabled'}")

            elif cmd == "read":
                value = dev.get_dvm_current()
                ColorPrinter.cyan(f"DVM: {value} V")

            elif cmd == "source" and len(args) >= 2:
                channel = int(args[1])
                dev.set_dvm_source(channel)
                ColorPrinter.success(f"DVM source: CH{channel}")

            else:
                ColorPrinter.warning(f"Unknown DVM command: scope dvm {' '.join(args)}. Type 'scope dvm' for help.")

        except AttributeError:
            ColorPrinter.warning("DVM not supported on this oscilloscope")
        except Exception as exc:
            ColorPrinter.error(str(exc))

    # --------------------------
    # Logging commands
    # --------------------------
    def do_log(self, arg):
        "log <print|save|clear>: show or save measurements"
        args = self._parse_args(arg)
        args, help_flag = self._strip_help(args)
        if help_flag or not args:
            self._print_usage(
                [
                    "log print",
                    "log save <path> [csv|txt]",
                    "log clear",
                ]
            )
            return
        cmd_name = args[0].lower()
        if cmd_name == "clear":
            self.measurements = []
            ColorPrinter.success("Cleared measurements.")
            return
        if cmd_name == "print":
            if not self.measurements:
                ColorPrinter.warning("No measurements recorded.")
                return
            C = ColorPrinter.CYAN
            G = ColorPrinter.GREEN
            Y = ColorPrinter.YELLOW
            R = ColorPrinter.RESET
            header = f"{'Label':<24} {'Value':>14} {'Unit':<8} {'Source':<12}"
            print(f"{Y}{header}{R}")
            print(f"{Y}{'-' * len(header)}{R}")
            for entry in self.measurements:
                label = entry.get("label", "")
                value = entry.get("value", "")
                unit = entry.get("unit", "")
                source = entry.get("source", "")
                print(f"{C}{label:<24}{R} {G}{value:>14}{R} {Y}{unit:<8}{R} {source:<12}")
            return
        if cmd_name == "save" and len(args) >= 2:
            path = args[1]
            fmt = args[2].lower() if len(args) >= 3 else ""
            if not fmt:
                _, ext = os.path.splitext(path)
                fmt = ext.lstrip(".").lower()
            if fmt not in ("csv", "txt"):
                ColorPrinter.warning("log save expects format csv or txt (or use .csv/.txt).")
                return
            if not self.measurements:
                ColorPrinter.warning("No measurements recorded.")
                return
            try:
                with open(path, "w", encoding="utf-8", newline="") as handle:
                    if fmt == "csv":
                        handle.write("label,value,unit,source\n")
                        for entry in self.measurements:
                            handle.write(
                                f"{entry.get('label','')},{entry.get('value','')},{entry.get('unit','')},{entry.get('source','')}\n"
                            )
                    else:
                        header = f"{'Label':<24} {'Value':>14} {'Unit':<8} {'Source':<12}"
                        handle.write(header + "\n")
                        handle.write("-" * len(header) + "\n")
                        for entry in self.measurements:
                            label = entry.get("label", "")
                            value = entry.get("value", "")
                            unit = entry.get("unit", "")
                            source = entry.get("source", "")
                            handle.write(f"{label:<24} {value:>14} {unit:<8} {source:<12}\n")
                ColorPrinter.success(f"Saved measurements to {path}.")
            except Exception as exc:
                ColorPrinter.error(f"Failed to save measurements: {exc}")
            return
        ColorPrinter.warning(f"Unknown log command: log {arg}. Use: log print|save|clear")

    def do_calc(self, arg):
        "calc is short for calculator: compute a value from logged measurements"
        args = self._parse_args(arg)
        args, help_flag = self._strip_help(args)
        if help_flag or len(args) < 2:
            self._print_colored_usage(
                [
                    "# CALC (short for calculator)",
                    "",
                    "calc <label> <expr> [unit=]",
                    "  - expr can use m[\"label\"], last, and variables like pi",
                    "  - functions: abs, min, max, round",
                    "  - example: calc ron_ohm m[\"vout_5_mV\"]/1000/m[\"psu_i_5_A\"] unit=ohm",
                ]
            )
            return
        label = args[0]
        unit = ""
        expr_parts = []
        for token in args[1:]:
            token_lower = token.lower()
            if token_lower.startswith("unit="):
                unit = token.split("=", 1)[1]
            else:
                expr_parts.append(token)
        expr = " ".join(expr_parts)
        if not expr:
            ColorPrinter.warning("calc expects an expression.")
            return
        if not self.measurements:
            ColorPrinter.warning("No measurements recorded. Use meas_store first.")
            return
        m = {entry["label"]: entry["value"] for entry in self.measurements}
        last = self.measurements[-1]["value"]
        names = {"m": m, "last": last}
        try:
            value = self._safe_eval(expr, names)
            self._record_measurement(label, value, unit, "calc")
            suffix = f" {unit}" if unit else ""
            C = ColorPrinter.CYAN
            G = ColorPrinter.GREEN
            Y = ColorPrinter.YELLOW
            R = ColorPrinter.RESET
            print(f"{C}{label}{R} = {G}{value}{R}{Y}{suffix}{R}")
        except Exception as exc:
            ColorPrinter.error(f"calc failed: {exc}")

    # --------------------------
    def do_python(self, arg):
        "python <file.py>: execute external Python script with REPL context"
        args = self._parse_args(arg)
        args, help_flag = self._strip_help(args)

        if help_flag or not args:
            self._print_colored_usage(
                [
                    "# PYTHON SCRIPT EXECUTION",
                    "",
                    "python <file.py> - execute external Python script",
                    "  - The script has access to REPL context:",
                    "  - repl: the REPL instance",
                    "  - devices: dictionary of connected instruments",
                    "  - measurements: list of recorded measurements",
                    "  - ColorPrinter: for colored output",
                    "",
                    "  - example: python process_data.py",
                    "  - example: python analysis.py",
                ]
            )
            return

        filename = args[0]

        # Check if file exists
        if not os.path.exists(filename):
            ColorPrinter.error(f"File not found: {filename}")
            return

        # Read the file
        try:
            with open(filename, 'r') as f:
                script_code = f.read()
        except Exception as exc:
            ColorPrinter.error(f"Failed to read file: {exc}")
            return

        # Prepare execution context
        # Provide access to REPL, devices, measurements, and utilities
        exec_globals = {
            '__name__': '__main__',
            '__file__': filename,
            'repl': self,
            'devices': self.devices,
            'measurements': self.measurements,
            'ColorPrinter': ColorPrinter,
            # Common libraries that might be useful
            'os': os,
            'json': json,
            'time': time,
        }

        # Execute the script
        try:
            ColorPrinter.info(f"Executing {filename}...")
            exec(script_code, exec_globals)
            ColorPrinter.success(f"Script {filename} executed successfully")
        except Exception as exc:
            ColorPrinter.error(f"Script execution failed: {exc}")
            traceback.print_exc()


def main():
    args = sys.argv[1:]

    if "--version" in args or "-V" in args:
        print(f"scpi-instrument-toolkit v{_REPL_VERSION}")
        sys.exit(0)

    if "--help" in args or "-h" in args:
        print(
            f"scpi-instrument-toolkit v{_REPL_VERSION}\n"
            "\n"
            "Usage: scpi-repl [--mock] [--update] [--ignore-update] [--version] [--help] [script]\n"
            "\n"
            "Options:\n"
            "  --mock           Run with simulated instruments (no hardware required)\n"
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

    # Check for updates on startup; block if one is available unless --ignore-update
    update_available = _check_for_updates(force=False)
    if update_available and not ignore_update:
        ColorPrinter.error("Please update before using the REPL. Run the command above, or use --ignore-update to skip this check.")
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


if __name__ == "__main__":
    main()
