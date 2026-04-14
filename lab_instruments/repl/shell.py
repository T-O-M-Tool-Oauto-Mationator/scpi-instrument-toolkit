"""Thin cmd.Cmd subclass that delegates to command handler modules."""

import atexit
import cmd
import contextlib
import os
import re
import shlex
import signal
import sys
import threading

try:
    import readline
except ImportError:
    readline = None  # type: ignore[assignment]

_HISTORY_FILE = os.path.join(os.path.expanduser("~"), ".scpi_history")
_HISTORY_LENGTH = 1000
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version
from typing import Any

from lab_instruments import ColorPrinter, InstrumentDiscovery

from .commands.awg import AwgCommand
from .commands.dmm import DmmCommand
from .commands.ev2300 import Ev2300Command
from .commands.general import GeneralCommands
from .commands.logging_cmd import LoggingCommands
from .commands.plot import PlotCommand
from .commands.psu import PsuCommand
from .commands.safety import SafetySystem
from .commands.scope import ScopeCommand
from .commands.scripting import ScriptingCommands
from .commands.smu import SmuCommand
from .commands.variables import VariableCommands
from .context import ReplContext
from .syntax import safe_eval, substitute_vars


def get_version():
    try:
        return _pkg_version("scpi-instrument-toolkit")
    except PackageNotFoundError:
        return "unknown"


_REPL_VERSION = get_version()


def _split_on_semicolons(line):
    """Split *line* on semicolons that are not inside single or double quotes."""
    chunks = []
    current = []
    in_quote = None
    for ch in line:
        if ch in ('"', "'"):
            if in_quote is None:
                in_quote = ch
            elif in_quote == ch:
                in_quote = None
            current.append(ch)
        elif ch == ";" and in_quote is None:
            chunks.append("".join(current))
            current = []
        else:
            current.append(ch)
    chunks.append("".join(current))
    return chunks


class InstrumentRepl(cmd.Cmd):
    intro = f"ESET Instrument REPL v{_REPL_VERSION}. Type 'help' for commands."
    prompt = "eset> "

    def __init__(self, *, auto_scan: bool = True):
        super().__init__()

        # Shared state
        self.ctx = ReplContext()
        self.discovery = InstrumentDiscovery()

        # Load scripts
        self.ctx.scripts = self.ctx.load_scripts()

        # Command handlers
        self._safety = SafetySystem(self.ctx)
        self._general = GeneralCommands(self.ctx, self._safety)
        self._psu_cmd = PsuCommand(self.ctx)
        self._awg_cmd = AwgCommand(self.ctx)
        self._dmm_cmd = DmmCommand(self.ctx)
        self._scope_cmd = ScopeCommand(self.ctx)
        self._smu_cmd = SmuCommand(self.ctx)
        self._ev2300_cmd = Ev2300Command(self.ctx)
        self._var_cmd = VariableCommands(self.ctx)
        self._log_cmd = LoggingCommands(self.ctx)
        self._plot_cmd = PlotCommand(self.ctx)
        self._script_cmd = ScriptingCommands(self.ctx, self._safety, shell=self)

        # Wire up state callback for instrument commands that delegate to do_state
        self._psu_cmd.set_state_callback(lambda name, st: self.do_state(f"{name} {st}"))
        self._awg_cmd.set_state_callback(lambda name, st: self.do_state(f"{name} {st}"))
        self._dmm_cmd.set_state_callback(lambda name, st: self.do_state(f"{name} {st}"))
        self._scope_cmd.set_state_callback(lambda name, st: self.do_state(f"{name} {st}"))
        self._smu_cmd.set_state_callback(lambda name, st: self.do_state(f"{name} {st}"))
        self._ev2300_cmd.set_state_callback(lambda name, st: self.do_state(f"{name} {st}"))

        # Multi-line loop support
        self._in_loop = False
        self._loop_lines = []
        self._loop_depth = 0
        self._loop_header = ""

        # Flags
        self._cleanup_done = False
        self._should_exit = False

        # Terminal state preservation
        self._term_fd = None
        self._term_settings = None
        try:
            import termios

            fd = sys.stdin.fileno()
            self._term_fd = fd
            self._term_settings = termios.tcgetattr(fd)
        except Exception:
            pass

        # Load command history from disk so arrow keys recall previous commands
        if readline is not None:
            readline.set_history_length(_HISTORY_LENGTH)
            try:
                readline.read_history_file(_HISTORY_FILE)
            except FileNotFoundError:
                pass
            except Exception:
                pass

        # Register cleanup
        atexit.register(self._cleanup_on_exit)
        signal.signal(signal.SIGINT, self._cleanup_on_interrupt)
        if hasattr(signal, "SIGTERM"):
            signal.signal(signal.SIGTERM, self._cleanup_on_interrupt)

        # Background scan
        self._scan_done = threading.Event()
        if auto_scan:
            self._scan_thread = threading.Thread(target=self._background_scan, daemon=True, name="scpi-scan")
            ColorPrinter.info("Scanning for instruments in background — type 'scan' to wait for results.")
            self._scan_thread.start()
        else:
            self._scan_done.set()

    # ------------------------------------------------------------------
    # Backward-compatibility properties
    # ------------------------------------------------------------------
    @property
    def devices(self) -> dict[str, Any]:
        return self.ctx.registry.devices

    @devices.setter
    def devices(self, value: dict[str, Any]):
        self.ctx.registry.devices = value

    @property
    def selected(self):
        return self.ctx.registry.selected

    @selected.setter
    def selected(self, value):
        self.ctx.registry.selected = value

    @property
    def measurements(self):
        return self.ctx.measurements.entries

    @measurements.setter
    def measurements(self, value):
        self.ctx.measurements._entries = value

    @property
    def _script_vars(self):
        return self.ctx.script_vars

    @_script_vars.setter
    def _script_vars(self, value):
        self.ctx.script_vars = value

    @property
    def _command_had_error(self):
        return self.ctx.command_had_error

    @_command_had_error.setter
    def _command_had_error(self, value):
        self.ctx.command_had_error = value

    @property
    def _exit_on_error(self):
        return self.ctx.exit_on_error

    @_exit_on_error.setter
    def _exit_on_error(self, value):
        self.ctx.exit_on_error = value

    @property
    def _in_script(self):
        return self.ctx.in_script

    @_in_script.setter
    def _in_script(self, value):
        self.ctx.in_script = value

    @property
    def _in_debugger(self):
        return self.ctx.in_debugger

    @_in_debugger.setter
    def _in_debugger(self, value):
        self.ctx.in_debugger = value

    @property
    def _interrupt_requested(self):
        return self.ctx.interrupt_requested

    @_interrupt_requested.setter
    def _interrupt_requested(self, value):
        self.ctx.interrupt_requested = value

    @property
    def _safety_limits(self):
        return self.ctx.safety_limits

    @_safety_limits.setter
    def _safety_limits(self, value):
        self.ctx.safety_limits = value

    @property
    def _awg_channel_state(self):
        return self.ctx.awg_channel_state

    @_awg_channel_state.setter
    def _awg_channel_state(self, value):
        self.ctx.awg_channel_state = value

    @property
    def scripts(self):
        return self.ctx.scripts

    @scripts.setter
    def scripts(self, value):
        self.ctx.scripts = value

    @property
    def _record_script(self):
        return self.ctx.record_script

    @_record_script.setter
    def _record_script(self, value):
        self.ctx.record_script = value

    @property
    def test_results(self):
        return self.ctx.test_results

    @test_results.setter
    def test_results(self, value):
        self.ctx.test_results = value

    @property
    def _report_title(self):
        return self.ctx.report_title

    @_report_title.setter
    def _report_title(self, value):
        self.ctx.report_title = value

    @property
    def _report_operator(self):
        return self.ctx.report_operator

    @_report_operator.setter
    def _report_operator(self, value):
        self.ctx.report_operator = value

    @property
    def _report_screenshots(self):
        return self.ctx.report_screenshots

    @_report_screenshots.setter
    def _report_screenshots(self, value):
        self.ctx.report_screenshots = value

    # ------------------------------------------------------------------
    # Background scan + lifecycle
    # ------------------------------------------------------------------
    def _background_scan(self):
        try:
            self.ctx.registry.devices = self.discovery.scan(verbose=True)
            if self.ctx.registry.selected not in self.ctx.registry.devices:
                self.ctx.registry.selected = None
            if self.ctx.registry.devices:
                ColorPrinter.success(f"\nScan complete: found {len(self.ctx.registry.devices)} device(s).")
                try:
                    ColorPrinter.info("Setting all instruments to safe state...")
                    self._general.safe_all()
                except Exception as exc:
                    ColorPrinter.error(f"Error during startup safety check: {exc}")
            else:
                ColorPrinter.warning("\nScan complete: no instruments found.")
        except Exception as exc:
            ColorPrinter.error(f"\nScan failed: {exc}")
        finally:
            self._scan_done.set()

    def _wait_for_scan(self):
        if not self._scan_done.is_set():
            ColorPrinter.info("Waiting for instrument scan to finish...")
            self._scan_done.wait()

    def _restore_terminal(self):
        try:
            if sys.stdout.isatty():
                # Reset extended keyboard reporting modes that readline may have
                # enabled.  These are no-ops on terminals that don't support them:
                #   ?2004l  disable bracketed paste
                #   >4m     reset XTerm modifyOtherKeys (fixes 9;5u spam on Ctrl+C)
                #   <u      pop kitty keyboard protocol stack
                sys.stdout.write("\x1b[?2004l\x1b[>4m\x1b[<u")
                sys.stdout.flush()
        except Exception:
            pass
        try:
            if self._term_settings is not None:
                import termios

                termios.tcsetattr(self._term_fd, termios.TCSADRAIN, self._term_settings)
        except Exception:
            pass

    def _cleanup_on_exit(self):
        # Save command history before shutdown
        if readline is not None:
            with contextlib.suppress(Exception):
                readline.write_history_file(_HISTORY_FILE)
        self._wait_for_scan()
        if not self._cleanup_done and self.ctx.registry.devices:
            self._cleanup_done = True
            ColorPrinter.warning("\n=== Shutting down instruments safely ===")
            try:
                self._general.safe_all()
            except Exception as exc:
                ColorPrinter.error(f"Error during cleanup: {exc}")
        self._restore_terminal()

    def _cleanup_on_interrupt(self, signum, frame):
        self.ctx.interrupt_requested = True
        if self._in_loop:
            self._in_loop = False
            self._loop_lines = []
            self._loop_depth = 0
            self.prompt = "eset> "
            print("\n(cancelled loop block)")
        self._scan_done.set()
        if not self._cleanup_done and self.ctx.registry.devices and not self.ctx.in_debugger:
            self._cleanup_done = True
            ColorPrinter.warning("\n\n=== Interrupted! Shutting down instruments safely ===")
            try:
                self._general.safe_all()
            except Exception as exc:
                ColorPrinter.error(f"Error during cleanup: {exc}")
        self._restore_terminal()
        if self.ctx.in_script:
            raise KeyboardInterrupt
        self._should_exit = True

    # ------------------------------------------------------------------
    # cmd.Cmd overrides
    # ------------------------------------------------------------------
    def cmdloop(self, intro=None):
        if intro is not None:
            self.intro = intro
        self._scan_done.wait()
        if self.intro:
            print(self.intro)
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
                                line = "EOF"
                        else:
                            self.lastcmd = ""
                            line = self.stdin.readline()
                            line = "EOF" if not len(line) else line.rstrip("\r\n")
                    line = self.precmd(line)
                    stop = self.onecmd(line)
                    line = self.postcmd(stop, line)
                except KeyboardInterrupt:
                    if self.ctx.in_script:
                        ColorPrinter.warning("Script interrupted by user")
                    else:
                        print()
                    self.ctx.in_script = False
                    self.ctx.interrupt_requested = False
        finally:
            if self._should_exit:
                print("\nGoodbye!")
                self._restore_terminal()
            self.postloop()

    def precmd(self, line):
        if not self.ctx.in_script:
            self.ctx.command_had_error = False
        return line

    def postcmd(self, stop, line):
        stripped = line.strip()
        if (
            self.ctx.record_script
            and stripped
            and not self.ctx.in_script
            and not self.ctx.in_debugger
            and not self.ctx.command_had_error
            and not stripped.lower().startswith("record")
        ):
            name = self.ctx.record_script
            if name not in self.ctx.scripts:
                self.ctx.scripts[name] = []
            self.ctx.scripts[name].append(stripped)
            try:
                with open(self.ctx.script_file(name), "a", encoding="utf-8") as fh:
                    fh.write(stripped + "\n")
            except Exception:
                pass
        return stop

    _ASSIGN_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_.]*)\s*=\s*(.+)$")

    def default(self, line):
        """Handle numbered device names ('awg1', 'scope2') and var = expr assignment."""
        parts = line.split(None, 1)
        cmd_token = parts[0]
        rest = parts[1] if len(parts) > 1 else ""

        # Resolve the device name: exact match, or "psu1" -> "psu" when only one exists
        resolved = cmd_token
        if cmd_token not in self.ctx.registry.devices:
            base_type = re.sub(r"\d+$", "", cmd_token)
            if base_type != cmd_token and base_type in self.ctx.registry.devices:
                # "psu1" typed but device is registered as "psu" (only one of its type)
                resolved = base_type

        if resolved in self.ctx.registry.devices:
            base_type = re.sub(r"\d+$", "", resolved)
            handler = getattr(self, f"do_{base_type}", None)
            if handler:
                self.ctx.registry._device_override = resolved
                try:
                    handler(rest)
                finally:
                    self.ctx.registry._device_override = None
                return

        # Increment / decrement: x++  x--
        stripped = line.strip()
        inc_m = re.match(r"^([A-Za-z_][A-Za-z0-9_.]*)\s*\+\+$", stripped)
        if inc_m:
            varname = inc_m.group(1)
            cur = self.ctx.script_vars.get(varname, "0")
            try:
                self.ctx.script_vars[varname] = str(float(cur) + 1)
            except ValueError:
                self.ctx.script_vars[varname] = str(float(0) + 1)
            ColorPrinter.success(f"{varname} = {self.ctx.script_vars[varname]}")
            return
        dec_m = re.match(r"^([A-Za-z_][A-Za-z0-9_.]*)\s*--$", stripped)
        if dec_m:
            varname = dec_m.group(1)
            cur = self.ctx.script_vars.get(varname, "0")
            try:
                self.ctx.script_vars[varname] = str(float(cur) - 1)
            except ValueError:
                self.ctx.script_vars[varname] = str(float(0) - 1)
            ColorPrinter.success(f"{varname} = {self.ctx.script_vars[varname]}")
            return

        # Compound assignment: x += 5  x -= 2  x *= 3  x /= 4  x //= 2  x **= 3  x %= 2
        compound_m = re.match(r"^([A-Za-z_][A-Za-z0-9_.]*)\s*(\+|-|\*\*|\*|//|/|%)=\s*(.+)$", stripped)
        if compound_m:
            varname = compound_m.group(1)
            op = compound_m.group(2)
            rhs_raw = compound_m.group(3).strip()
            rhs_val = substitute_vars(rhs_raw, self.ctx.script_vars, self.ctx.measurements)
            cur = self.ctx.script_vars.get(varname, "0")
            try:
                expr = f"{cur} {op} ({rhs_val})"
                from .syntax import safe_eval

                result = safe_eval(expr, {k: float(v) for k, v in self.ctx.script_vars.items() if k != varname})
                self.ctx.script_vars[varname] = str(result)
                ColorPrinter.success(f"{varname} = {self.ctx.script_vars[varname]}")
            except Exception as exc:
                ColorPrinter.error(f"Compound assignment failed: {exc}")
            return

        # Python-style assignment: voltage = 5.0  /  label = "mytest"
        # Also handles: value = dmm read  /  value = psu1 read unit=V
        m = self._ASSIGN_RE.match(stripped)
        if m:
            varname = m.group(1)
            rhs = m.group(2).strip()
            # Try instrument read first; fall through to calc, then plain assignment
            if self._var_cmd.try_instrument_read(varname, rhs):
                return
            if self._var_cmd.try_calc_assignment(varname, rhs):
                return
            self._var_cmd._assign_var(varname, rhs)
            return

        self.ctx.command_had_error = True
        ColorPrinter.error(f"Unknown syntax: {line}")

    def _error(self, message):
        """Backward-compat error reporter."""
        self.ctx.error(message)

    # ------------------------------------------------------------------
    # onecmd — semicolons, repeat, for/repeat block collection
    # ------------------------------------------------------------------
    def _onecmd_single(self, line):
        line = substitute_vars(line, self.ctx.script_vars, self.ctx.measurements)
        try:
            tokens = shlex.split(line)
        except ValueError:
            tokens = line.split()
        if len(tokens) >= 3 and tokens[0].lower() == "repeat":
            try:
                count = int(tokens[1])
            except ValueError:
                return super().onecmd(line)
            cmd_line = " ".join(tokens[2:])
            return any(super().onecmd(cmd_line) for _ in range(count))

        all_indices = [i for i, t in enumerate(tokens) if t.lower() == "all"]
        if all_indices:
            cmd_token = tokens[0].lower() if tokens else ""
            base_type = re.sub(r"\d+$", "", cmd_token)
            if base_type in ("awg", "scope", "psu"):
                dev = None
                if (
                    self.ctx.registry._device_override
                    and self.ctx.registry._device_override in self.ctx.registry.devices
                ):
                    dev = self.ctx.registry.devices[self.ctx.registry._device_override]
                elif cmd_token in self.ctx.registry.devices:
                    dev = self.ctx.registry.devices[cmd_token]
                else:
                    pattern = re.compile(rf"^{re.escape(base_type)}\d*$")
                    for dname, d in self.ctx.registry.devices.items():
                        if pattern.match(dname):
                            dev = d
                            break
                if dev is not None:
                    channels = self.ctx.registry.channels_for(dev, base_type)
                    if channels:
                        all_idx = all_indices[0]
                        for ch in channels:
                            new_tokens = list(tokens)
                            new_tokens[all_idx] = str(ch)
                            if super().onecmd(" ".join(new_tokens)):
                                return True
                        return False

        return super().onecmd(line)

    # Block-opening keywords that require an 'end' to close
    _BLOCK_KEYWORDS = frozenset(("for", "repeat", "while", "if"))

    def onecmd(self, line):
        if self._in_loop:
            stripped = line.strip()
            if stripped.lower() == "end":
                self._loop_depth -= 1
                if self._loop_depth == 0:
                    self._execute_collected_loop()
                    return False
                # Inner 'end' (for nested blocks) — must be kept in the body
                self._loop_lines.append(line)
            else:
                try:
                    tokens = shlex.split(stripped)
                except ValueError:
                    tokens = stripped.split()
                if tokens and tokens[0].lower() in self._BLOCK_KEYWORDS:
                    self._loop_depth += 1
                self._loop_lines.append(line)
            return False

        stripped = line.strip()
        try:
            tokens = shlex.split(stripped)
        except ValueError:
            tokens = stripped.split()

        # Block collection for interactive use (for/repeat go through expander,
        # while/if go through runtime execution)
        if tokens and tokens[0].lower() in self._BLOCK_KEYWORDS:
            self._in_loop = True
            self._loop_depth = 1
            self._loop_header = stripped
            self._loop_lines = []
            self.prompt = "  > "
            ColorPrinter.info("(entering block - type 'end' to finish)")
            return False

        # Handle condition-form check: ``check <cond> ["msg"]``
        # Falls through to do_check (measurement form) if no comparison operators found
        if tokens and tokens[0].lower() == "check":
            rest = stripped[len("check") :].strip()
            if rest and self._COND_CHECK_RE.search(rest):
                return self._execute_check(stripped)

        if ";" in line:
            should_exit = False
            for chunk in _split_on_semicolons(line):
                cmd_line = chunk.strip()
                if not cmd_line:
                    continue
                if self._onecmd_single(cmd_line):
                    should_exit = True
                    break
            return should_exit
        return self._onecmd_single(line)

    def _execute_collected_loop(self):
        self.prompt = "eset> "
        self._in_loop = False
        all_lines = [self._loop_header] + self._loop_lines + ["end"]

        # Determine if this is a while/if block (runtime) or for/repeat (expander)
        try:
            header_tokens = shlex.split(self._loop_header)
        except ValueError:
            header_tokens = self._loop_header.split()
        head = header_tokens[0].lower() if header_tokens else ""

        if head == "while":
            try:
                self._execute_while_block(self._loop_header, self._loop_lines)
            except self._AssertFailure as exc:
                ColorPrinter.error(f"Script aborted: {exc.message}")
                self.ctx.command_had_error = True
            except KeyboardInterrupt:
                ColorPrinter.warning("While loop interrupted by user")
            except Exception as e:
                ColorPrinter.error(f"While loop execution error: {e}")
            return

        if head == "if":
            try:
                self._execute_if_block(all_lines)
            except self._AssertFailure as exc:
                ColorPrinter.error(f"Script aborted: {exc.message}")
                self.ctx.command_had_error = True
            except KeyboardInterrupt:
                ColorPrinter.warning("If block interrupted by user")
            except Exception as e:
                ColorPrinter.error(f"If block execution error: {e}")
            return

        # for/repeat: use the expander
        from .script_engine.expander import expand_script_lines

        try:
            expanded = expand_script_lines(all_lines, {}, self.ctx)
            for item in expanded:
                cmd_item, _ = item if isinstance(item, tuple) else (item, item)
                line = cmd_item.strip()
                if not line or line.startswith("#"):
                    continue
                if self.onecmd(line):
                    return
        except KeyboardInterrupt:
            ColorPrinter.warning("Loop interrupted by user")
        except Exception as e:
            ColorPrinter.error(f"Loop execution error: {e}")

    # ------------------------------------------------------------------
    # Runtime block execution: while, if/elif/else, assert
    # ------------------------------------------------------------------

    _WHILE_MAX_ITERATIONS = 10000

    # Import control-flow exceptions from runner (module-level definitions)
    from .script_engine.runner import _AssertFailure, _BreakSignal, _ContinueSignal

    # Detects comparison/boolean operators → condition-form check vs measurement check
    _COND_CHECK_RE = re.compile(r"(?:>=|<=|!=|==|>|<|&&|\|\||(?<![a-zA-Z0-9_])(?:and|or|not)(?![a-zA-Z0-9_]))")

    def _build_names_dict(self) -> dict:
        """Build a names dict from script_vars for safe_eval (float where possible)."""
        names: dict = {}
        for k, v in self.ctx.script_vars.items():
            with contextlib.suppress(TypeError, ValueError):
                names[k] = float(v)
                continue
            names[k] = v
        return names

    def _eval_condition(self, condition_str: str) -> bool:
        """Evaluate a condition string using safe_eval with script variables."""
        cond = substitute_vars(condition_str, self.ctx.script_vars, self.ctx.measurements)
        names = self._build_names_dict()
        return bool(safe_eval(cond, names))

    def _collect_block_from_lines(self, lines: list[str], start: int) -> tuple[list[str], int]:
        """Collect lines from *start* until a matching 'end', tracking nesting depth.

        Returns (block_lines, next_index_after_end).
        """
        block: list[str] = []
        depth = 1
        idx = start
        while idx < len(lines):
            line = lines[idx].strip()
            idx += 1
            if not line or line.startswith("#"):
                block.append(line)
                continue
            try:
                toks = shlex.split(line)
            except ValueError:
                toks = line.split()
            if toks and toks[0].lower() in self._BLOCK_KEYWORDS:
                depth += 1
            elif toks and toks[0].lower() == "end":
                depth -= 1
                if depth == 0:
                    return block, idx
            block.append(line)
        return block, idx

    def _execute_block_lines(self, block: list[str]) -> None:
        """Execute a list of command lines, handling nested while/if/assert."""
        idx = 0
        while idx < len(block):
            if self.ctx.interrupt_requested:
                return
            raw_line = block[idx].strip()
            idx += 1
            if not raw_line or raw_line.startswith("#"):
                continue
            try:
                toks = shlex.split(raw_line)
            except ValueError:
                toks = raw_line.split()
            if not toks:
                continue
            head = toks[0].lower()

            if head == "while":
                condition = raw_line[len("while") :].strip()
                inner_block, idx = self._collect_block_from_lines(block, idx)
                self._execute_while_block(f"while {condition}", inner_block)
                continue

            if head == "if":
                # Re-collect the full if/elif/else/end from remaining lines
                if_lines = [raw_line]
                depth = 1
                j = idx
                while j < len(block):
                    bline = block[j].strip()
                    j += 1
                    try:
                        lt = shlex.split(bline)
                    except ValueError:
                        lt = bline.split()
                    if lt and lt[0].lower() in self._BLOCK_KEYWORDS:
                        depth += 1
                    elif lt and lt[0].lower() == "end":
                        depth -= 1
                        if depth == 0:
                            if_lines.append(bline)
                            break
                    if_lines.append(bline)
                idx = j
                self._execute_if_block(if_lines)
                continue

            if head == "assert":
                self._execute_assert(raw_line)
                continue

            if head == "check":
                rest = raw_line[len("check") :].strip()
                if rest and self._COND_CHECK_RE.search(rest):
                    self._execute_check(raw_line)
                    continue
                # Fall through to onecmd for measurement-form check

            if head == "break":
                raise self._BreakSignal()

            if head == "continue":
                raise self._ContinueSignal()

            # Regular command — run through onecmd
            self.onecmd(raw_line)

    def _execute_while_block(self, header: str, body_lines: list[str]) -> None:
        """Execute a while block: ``while <condition>`` with body_lines."""
        condition = header[len("while") :].strip()
        if not condition:
            ColorPrinter.error("while: missing condition")
            return

        iteration = 0
        while iteration < self._WHILE_MAX_ITERATIONS:
            if self.ctx.interrupt_requested:
                ColorPrinter.warning("While loop interrupted")
                return
            try:
                result = self._eval_condition(condition)
            except Exception as exc:
                ColorPrinter.error(f"while condition error: {exc}")
                return
            if not result:
                break
            iteration += 1
            try:
                self._execute_block_lines(list(body_lines))
            except self._BreakSignal:
                break
            except self._ContinueSignal:
                continue
        else:
            ColorPrinter.warning(f"While loop hit maximum iteration limit ({self._WHILE_MAX_ITERATIONS})")

    def _execute_if_block(self, all_lines: list[str]) -> None:
        """Execute an if/elif/else/end block from a list of all lines including header and end."""
        # Parse the block into branches: [(condition_or_None, body_lines), ...]
        branches: list[tuple[str | None, list[str]]] = []
        current_condition: str | None = None
        current_body: list[str] = []
        depth = 0

        for raw_line in all_lines:
            line = raw_line.strip()
            if not line:
                if depth == 1:
                    current_body.append(raw_line)
                continue
            try:
                toks = shlex.split(line)
            except ValueError:
                toks = line.split()
            head = toks[0].lower() if toks else ""

            if head == "if" and depth == 0:
                depth = 1
                current_condition = line[len("if") :].strip()
                current_body = []
                continue

            if depth == 1 and head == "elif":
                branches.append((current_condition, current_body))
                current_condition = line[len("elif") :].strip()
                current_body = []
                continue

            if depth == 1 and head == "else":
                branches.append((current_condition, current_body))
                current_condition = None  # else branch
                current_body = []
                continue

            if head == "end":
                depth -= 1
                if depth == 0:
                    branches.append((current_condition, current_body))
                    break
                else:
                    current_body.append(raw_line)
                    continue

            if head in self._BLOCK_KEYWORDS:
                depth += 1

            if depth >= 1:
                current_body.append(raw_line)

        # Evaluate branches in order
        for condition, body in branches:
            if condition is None:
                # else branch — always execute
                self._execute_block_lines(body)
                return
            try:
                result = self._eval_condition(condition)
            except Exception as exc:
                ColorPrinter.error(f"if/elif condition error: {exc}")
                return
            if result:
                self._execute_block_lines(body)
                return

    def _parse_condition_and_message(self, text: str) -> tuple[str, str | None]:
        """Extract ``(condition, optional_message)`` from text after assert/check."""
        message = None
        msg_match = re.search(r"""(["'])(.*?)\1\s*$""", text)
        if msg_match:
            message = msg_match.group(2)
            condition = text[: msg_match.start()].strip()
        else:
            condition = text
        return condition, message

    def _execute_assert(self, line: str) -> bool:
        """Execute an assert statement: ``assert <condition> ["message"]``.

        Hard assertion — always raises ``_AssertFailure`` on fail, stopping
        the current script or block.
        """
        after_assert = line[len("assert") :].strip()
        if not after_assert:
            ColorPrinter.error("assert: missing condition")
            return False

        condition, message = self._parse_condition_and_message(after_assert)
        if not condition:
            ColorPrinter.error("assert: missing condition")
            return False

        try:
            result = self._eval_condition(condition)
        except Exception as exc:
            ColorPrinter.error(f"assert evaluation error: {exc}")
            label = message or condition
            raise self._AssertFailure(f"assert failed: {label} ({exc})") from exc

        label = message or condition
        if result:
            ColorPrinter.success(f"PASS: {label}")
        else:
            ColorPrinter.error(f"FAIL: {label}")
            raise self._AssertFailure(f"assert failed: {label}")
        return False

    def _execute_check(self, line: str) -> bool:
        """Execute a check statement: ``check <condition> ["message"]``.

        Soft test step — logs PASS/FAIL, records in test report, continues
        execution regardless.
        """
        after_check = line[len("check") :].strip()
        if not after_check:
            ColorPrinter.error("check: missing condition")
            return False

        condition, message = self._parse_condition_and_message(after_check)
        if not condition:
            ColorPrinter.error("check: missing condition")
            return False

        try:
            result = self._eval_condition(condition)
        except Exception as exc:
            ColorPrinter.error(f"check evaluation error: {exc}")
            self.ctx.command_had_error = True
            label = message or condition
            self.ctx.test_results.append({"test": label, "passed": False, "detail": str(exc)})
            return False

        label = message or condition
        if result:
            ColorPrinter.success(f"PASS: {label}")
            self.ctx.test_results.append({"test": label, "passed": True})
        else:
            ColorPrinter.error(f"FAIL: {label}")
            self.ctx.command_had_error = True
            self.ctx.test_results.append({"test": label, "passed": False})
        return False

    # ------------------------------------------------------------------
    # Backward-compat method used by test_safety_limits.py
    # ------------------------------------------------------------------
    def _expand_script_lines(self, lines, variables, depth=0, parent_vars=None, exports=None, _loop_ctx=""):
        from .script_engine.expander import expand_script_lines

        return expand_script_lines(
            lines,
            variables,
            self.ctx,
            depth=depth,
            parent_vars=parent_vars,
            exports=exports,
            _loop_ctx=_loop_ctx,
        )

    def _run_expanded(self, expanded, debug=False):
        from .script_engine.runner import run_expanded

        return run_expanded(expanded, self, self.ctx, debug=debug)

    def _run_script_lines(self, lines):
        expanded = self._expand_script_lines(lines, {})
        return self._run_expanded(expanded)

    def _record_measurement(self, label, value, unit="", source=""):
        self.ctx.measurements.record(label, value, unit, source)

    def _update_awg_state(self, device_name, channel, vpp=None, offset=None):
        self._safety.update_awg_state(device_name, channel, vpp=vpp, offset=offset)

    def _check_psu_limits(self, device_name, channel, voltage=None, current=None):
        return self._safety.check_psu_limits(device_name, channel, voltage=voltage, current=current)

    def _check_awg_limits(self, device_name, channel, new_vpp=None, new_offset=None, new_freq=None):
        return self._safety.check_awg_limits(
            device_name, channel, new_vpp=new_vpp, new_offset=new_offset, new_freq=new_freq
        )

    def _check_psu_output_allowed(self, device_name):
        return self._safety.check_psu_output_allowed(device_name)

    def _check_awg_output_allowed(self, device_name, channel):
        return self._safety.check_awg_output_allowed(device_name, channel)

    def _retroactive_limit_check_all(self):
        self._safety.retroactive_limit_check_all()

    def _collect_limits(self, device_name, device_type, channel):
        return self._safety.collect_limits(device_name, device_type, channel)

    def _query_awg_state(self, device_name, channel):
        return self._safety.query_awg_state(device_name, channel)

    def _query_psu_state(self, device_name):
        return self._safety.query_psu_state(device_name)

    @property
    def _data_dir_override(self):
        return self.ctx._data_dir_override

    @_data_dir_override.setter
    def _data_dir_override(self, value):
        self.ctx._data_dir_override = value

    @property
    def _scripts_dir_override(self):
        return self.ctx._scripts_dir_override

    @_scripts_dir_override.setter
    def _scripts_dir_override(self, value):
        self.ctx._scripts_dir_override = value

    def _get_data_dir(self):
        return self.ctx.get_data_dir()

    def _get_scripts_dir(self):
        return self.ctx.get_scripts_dir()

    def _generate_pdf_report(self, path):
        self._log_cmd._generate_pdf_report(path)

    # ------------------------------------------------------------------
    # Command dispatch — delegates to command handler objects
    # ------------------------------------------------------------------
    def do_scan(self, arg):
        """scan: discover and connect to instruments"""
        self._wait_for_scan()
        self._general.do_scan(arg, self.discovery, self._scan_done)

    def do_force_scan(self, arg):
        """force-scan: disconnect all and re-scan from scratch (resets outputs to 0)"""
        self._wait_for_scan()
        self._general.do_force_scan(arg, self.discovery, self._scan_done)

    def do_disconnect(self, arg):
        """disconnect <name>: remove a scanned device from the session"""
        self._general.do_disconnect(arg)

    def do_list(self, arg):
        """list: show connected instruments"""
        self._general.do_list(arg)

    def do_use(self, arg):
        """use <name>: set active instrument"""
        self._general.do_use(arg)

    def do_status(self, arg):
        """status: show current selection"""
        self._general.do_status(arg)

    def do_idn(self, arg):
        """idn [name]: query *IDN?"""
        self._wait_for_scan()
        self._general.do_idn(arg)

    def do_raw(self, arg):
        """raw [name] <scpi>: send raw SCPI command"""
        self._wait_for_scan()
        self._general.do_raw(arg)

    def do_state(self, arg):
        """state [safe|reset|on|off] or state <device> <state>"""
        self._wait_for_scan()
        self._general.do_state(arg)

    def do_close(self, arg):
        """close: disconnect all instruments"""
        self._general.do_close(arg)

    def do_docs(self, arg):
        """docs: open full HTML documentation in your browser"""
        self._general.do_docs(arg)

    def do_version(self, arg):
        """version: show version"""
        self._general.do_version(arg, _REPL_VERSION)

    def do_clear(self, arg):
        """clear: clear terminal"""
        self._general.do_clear(arg)

    def do_reload(self, arg):
        """reload: restart REPL process"""
        self._general.do_reload(arg)

    def do_all(self, arg):
        """all <on|off|safe|reset>: apply state to all instruments"""
        self._wait_for_scan()
        self._general.do_all(arg)

    def do_exit(self, arg):
        """exit: quit the REPL"""
        return True

    def do_EOF(self, arg):
        print()
        return True

    # Instrument commands
    def do_psu(self, arg):
        """psu <cmd>: control the power supply"""
        self._wait_for_scan()
        psu_name = self.ctx.registry.resolve_type("psu")
        if not psu_name:
            self.ctx.command_had_error = True
            if not self.ctx.registry.devices:
                ColorPrinter.warning("No instruments connected. Run 'scan' first.")
            else:
                self._error("No PSU found. Run 'scan' first.")
            return
        dev = self.ctx.registry.get_device(psu_name)
        if not dev:
            self.ctx.command_had_error = True
            return
        self._psu_cmd.execute(arg, dev, psu_name)

    def do_awg(self, arg):
        """awg <cmd>: control the function generator"""
        self._wait_for_scan()
        awg_name = self.ctx.registry.resolve_type("awg")
        if not awg_name:
            self.ctx.command_had_error = True
            if not self.ctx.registry.devices:
                ColorPrinter.warning("No instruments connected. Run 'scan' first.")
            else:
                self._error("No AWG found. Run 'scan' first.")
            return
        dev = self.ctx.registry.get_device(awg_name)
        if not dev:
            self.ctx.command_had_error = True
            return
        self._awg_cmd.execute(arg, dev, awg_name)

    def do_dmm(self, arg):
        """dmm <cmd>: control the multimeter"""
        self._wait_for_scan()
        dmm_name = self.ctx.registry.resolve_type("dmm")
        if not dmm_name:
            self.ctx.command_had_error = True
            if not self.ctx.registry.devices:
                ColorPrinter.warning("No instruments connected. Run 'scan' first.")
            else:
                self._error("No DMM found. Run 'scan' first.")
            return
        dev = self.ctx.registry.get_device(dmm_name)
        if not dev:
            self.ctx.command_had_error = True
            return
        self._dmm_cmd.execute(arg, dev, dmm_name)

    def do_scope(self, arg):
        """scope <cmd>: control the oscilloscope"""
        self._wait_for_scan()
        scope_name = self.ctx.registry.resolve_type("scope")
        if not scope_name:
            self.ctx.command_had_error = True
            if not self.ctx.registry.devices:
                ColorPrinter.warning("No instruments connected. Run 'scan' first.")
            else:
                self._error("No scope found. Run 'scan' first.")
            return
        dev = self.ctx.registry.get_device(scope_name)
        if not dev:
            self.ctx.command_had_error = True
            return
        self._scope_cmd.execute(arg, dev, scope_name)

    def do_smu(self, arg):
        """smu <cmd>: control the source measure unit"""
        self._wait_for_scan()
        smu_name = self.ctx.registry.resolve_type("smu")
        if not smu_name:
            self.ctx.command_had_error = True
            if not self.ctx.registry.devices:
                ColorPrinter.warning("No instruments connected. Run 'scan' first.")
            else:
                self._error("No SMU found. Run 'scan' first.")
            return
        dev = self.ctx.registry.get_device(smu_name)
        if not dev:
            self.ctx.command_had_error = True
            return
        self._smu_cmd.execute(arg, dev, smu_name)

    def do_ev2300(self, arg):
        """ev2300 <cmd>: control the EV2300 USB-to-I2C adapter"""
        self._wait_for_scan()
        ev_name = self.ctx.registry.resolve_type("ev2300")
        if not ev_name:
            self.ctx.command_had_error = True
            if not self.ctx.registry.devices:
                ColorPrinter.warning("No instruments connected. Run 'scan' first.")
            else:
                self._error("No EV2300 found. Run 'scan' first.")
            return
        dev = self.ctx.registry.get_device(ev_name)
        if not dev:
            self.ctx.command_had_error = True
            return
        self._ev2300_cmd.execute(arg, dev, ev_name)

    # Variable/IO commands
    def do_print(self, arg):
        """print <message>: display a message"""
        self._var_cmd.do_print(arg)

    def do_pause(self, arg):
        """pause [message]: wait for Enter"""
        self._var_cmd.do_pause(arg)

    def do_input(self, arg):
        """input <varname> [prompt]: read a value from user"""
        self._var_cmd.do_input(arg)

    def do_set(self, arg):
        """set <varname> <expr>: define a variable"""
        self._var_cmd.do_set(arg)

    def do_unset(self, arg):
        """unset <varname>: delete a script variable"""
        self._var_cmd.do_unset(arg)

    def do_pyeval(self, arg):
        """pyeval <expr>: evaluate a Python expression"""
        self._var_cmd.do_pyeval(arg)

    def do_sleep(self, arg):
        """sleep <duration>[us|ms|s|m]: pause execution"""
        self._var_cmd.do_sleep(arg)

    # Logging commands
    def do_data(self, arg):
        """data dir [path|reset]: manage data directory"""
        self._log_cmd.do_data(arg)

    def do_log(self, arg):
        """log <print|save|clear>: manage measurements"""
        self._log_cmd.do_log(arg)

    def do_calc(self, arg):
        """calc <label> = <expr> [unit=]: compute from measurements"""
        self._log_cmd.do_calc(arg)

    def do_check(self, arg):
        """check <label> <min> <max>: pass/fail assertion"""
        self._log_cmd.do_check(arg)

    def do_report(self, arg):
        """report <print|save|clear|title|operator>: manage reports"""
        self._log_cmd.do_report(arg)

    def do_assert(self, arg):
        """assert <condition> ["message"]: hard assertion — stops script on failure."""
        try:
            self._execute_assert(f"assert {arg}")
        except self._AssertFailure as exc:
            if self.ctx.in_script:
                raise
            ColorPrinter.error(f"Script aborted: {exc.message}")
            self.ctx.command_had_error = True

    def do_break(self, arg):
        """break: exit the innermost while/for loop."""
        raise self._BreakSignal()

    def do_continue(self, arg):
        """continue: skip to the next iteration of the innermost loop."""
        raise self._ContinueSignal()

    def do_plot(self, arg):
        """plot [pattern ...] [--title "text"]: plot measurement log data"""
        self._plot_cmd.execute(arg)

    def do_liveplot(self, arg):
        """liveplot <pattern> [--title "text"]: live-updating chart"""
        self._plot_cmd.execute_liveplot(arg)

    # Scripting commands
    def do_script(self, arg):
        """script <new|run|debug|edit|list|rm|show|dir|import|load|save>: manage scripts"""
        self._script_cmd.do_script(arg)

    def do_record(self, arg):
        """record <start|stop|status>: record commands to a script"""
        self._script_cmd.do_record(arg)

    def do_examples(self, arg):
        """examples [load <name|all>]: list or load example scripts"""
        self._script_cmd.do_examples(arg)

    def do_python(self, arg):
        """python <file.py>: execute external Python script"""
        self._script_cmd.do_python(arg)

    def do_upper_limit(self, arg):
        """upper_limit <device> [chan <N>] <param> <value>: set upper safety limit"""
        self._wait_for_scan()
        self._script_cmd.do_upper_limit(arg)

    def do_lower_limit(self, arg):
        """lower_limit <device> [chan <N>] <param> <value>: set lower safety limit"""
        self._wait_for_scan()
        self._script_cmd.do_lower_limit(arg)

    # ------------------------------------------------------------------
    # Help system
    # ------------------------------------------------------------------
    def do_help(self, arg):
        """help [command|all]: show help"""
        if arg:
            if arg.strip().lower() == "all":
                for cmd_name in [
                    "scan",
                    "force_scan",
                    "list",
                    "use",
                    "status",
                    "state",
                    "idn",
                    "raw",
                    "sleep",
                    "close",
                    "all",
                    "upper_limit",
                    "lower_limit",
                    "log",
                    "calc",
                    "data",
                    "plot",
                    "script",
                ]:
                    fn = getattr(self, f"help_{cmd_name}", None)
                    if fn:
                        fn()
                C = ColorPrinter.CYAN
                Y = ColorPrinter.YELLOW
                B = ColorPrinter.BOLD
                R = ColorPrinter.RESET
                print(f"\n{Y}{B}INSTRUMENT COMMANDS{R}  (type the command with no args for full help)")
                for name, desc in [
                    ("psu", "power supply  — chan, set, meas, track, save, recall, state"),
                    ("awg", "function gen  — chan, wave, freq, amp, offset, duty, phase, sync, state"),
                    ("dmm", "multimeter    — config, read, fetch, meas, beep, display"),
                    ("scope", "oscilloscope  — chan, meas, save, screenshot, trigger, awg, dvm, counter"),
                ]:
                    print(f"  {C}{name:<8}{R} {desc}")
                print()
                return

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
                lines = doc.strip().splitlines()
                first = lines[0]
                rest = lines[1:]
                print(f"{ColorPrinter.CYAN}{first}{ColorPrinter.RESET}")
                for line in rest:
                    print(line)
            else:
                ColorPrinter.warning(f"No help for '{arg}'.")
            return

        C = ColorPrinter.CYAN
        Y = ColorPrinter.YELLOW
        B = ColorPrinter.BOLD
        R = ColorPrinter.RESET

        def section(title):
            print(f"\n{Y}{B}{title}{R}")

        def cmd_line(name, desc):
            print(f"  {C}{name:<14}{R} {desc}")

        print(f"{B}ESET Instrument REPL{R} {Y}v{_REPL_VERSION}{R}  —  type {C}help <command>{R} for full details\n")

        section("GENERAL")
        cmd_line("scan", "discover and connect to instruments")
        cmd_line("force_scan", "re-scan from scratch, reset all outputs to 0")
        cmd_line("disconnect", "remove a device from the session  (disconnect <name>)")
        cmd_line("reload", "restart the REPL process")
        cmd_line("list", "show connected instruments")
        cmd_line("use", "set active instrument  (use <name>)")
        cmd_line("status", "show current selection")
        cmd_line("state", "set instrument state  (safe/reset/on/off)")
        cmd_line("all", "apply state to all instruments")
        cmd_line("idn", "query *IDN?")
        cmd_line("raw", "send raw SCPI command or query")
        cmd_line("sleep", "pause between actions  (sleep <seconds>)")
        cmd_line("version", "show toolkit version")
        cmd_line("close", "disconnect all instruments")
        cmd_line("docs", "open full HTML documentation in your browser")
        cmd_line("exit", "quit the REPL")

        section("INSTRUMENTS  (run with no args for full sub-command help)")
        cmd_line("psu", "power supply  — chan, set, meas, track, save, recall")
        cmd_line("awg", "function generator  — chan, wave, freq, amp, offset, duty, phase")
        cmd_line("dmm", "multimeter  — config, read, fetch, meas, beep, display")
        cmd_line("scope", "oscilloscope  — chan, meas, meas_loop, save, trigger, awg, dvm, counter")
        cmd_line("smu", "source measure unit  — set, meas, get, on, off")

        section("SCRIPTING")
        cmd_line("script", "manage and run named scripts  — new, run, debug, edit, list, rm, show, dir")
        cmd_line("examples", "list or load bundled example workflows  (load <name> | load all)")
        cmd_line("python", "execute an external Python script with REPL context")
        cmd_line("upper_limit", "set an upper safety bound  — psu/awg, optional chan, param, value")
        cmd_line("lower_limit", "set a lower safety bound  — psu/awg, optional chan, param, value")
        cmd_line("unset", "delete a saved script variable  (unset <varname>)")

        section("LOGGING & MATH")
        cmd_line("log", "show or save recorded measurements  — print, save, clear")
        cmd_line("calc", "compute a value from logged measurements")
        cmd_line("check", "pass/fail assertion on measurements")
        cmd_line("report", "view or export lab test report  — print, save, clear, title, operator")
        cmd_line("plot", "plot measurement log data  (plot [pattern] [--title ...])")
        cmd_line("data dir", "get or set the data output directory  (data dir [path|reset])")

        print(f"\n  {Y}help <command>{R}  for full documentation   {Y}help all{R}  for everything at once\n")

    def help_upper_limit(self):
        self.do_upper_limit("")

    def help_lower_limit(self):
        self.do_lower_limit("")

    def help_log(self):
        self.do_log("")

    def help_calc(self):
        self.do_calc("")

    def help_plot(self):
        self._plot_cmd.execute("--help")

    def help_script(self):
        self.do_script("")

    def help_raw(self):
        self.do_raw("")

    def help_state(self):
        self.do_state("")

    def help_sleep(self):
        self.do_sleep("")

    def help_all(self):
        self.do_all("")

    def help_data(self):
        self.do_data("")

    def help_scan(self):
        self._general.print_colored_usage(
            [
                "# SCAN",
                "",
                "scan",
                "  - discover and connect to all VISA instruments",
                "  - instruments are assigned names: psu1, awg1, dmm1, scope1, …",
                "  - re-run at any time to pick up newly connected devices",
                "  - already-connected instruments keep their current state",
                "",
                "  see also: force_scan (resets all outputs to 0)",
            ]
        )

    def help_force_scan(self):
        self._general.print_colored_usage(
            [
                "# FORCE_SCAN",
                "",
                "force_scan",
                "  - disconnect all instruments and re-scan from scratch",
                "  - all outputs are set to safe defaults (0 V, off)",
                "  - use when you want a clean slate",
            ]
        )

    def help_list(self):
        self._general.print_colored_usage(
            [
                "# LIST",
                "",
                "list",
                "  - show all connected instruments and their assigned names",
                "  - the active instrument (set via 'use') is highlighted",
            ]
        )

    def help_idn(self):
        self._general.print_colored_usage(
            [
                "# IDN",
                "",
                "idn",
                "  - query *IDN? on the active instrument",
                "idn <name>",
                "  - query *IDN? on a specific named instrument",
            ]
        )

    def help_close(self):
        self._general.print_colored_usage(
            [
                "# CLOSE",
                "",
                "close",
                "  - disconnect all instruments and release VISA resources",
                "  - use 'scan' to reconnect",
            ]
        )

    def help_status(self):
        self._general.print_colored_usage(
            [
                "# STATUS",
                "",
                "status",
                "  - show all connected instruments and their assigned names",
                "  - indicates which instrument is currently active (set via 'use')",
            ]
        )

    def help_docs(self):
        self._general.do_docs("help")

    def help_check(self):
        self.do_check("")

    def help_report(self):
        self.do_report("")
