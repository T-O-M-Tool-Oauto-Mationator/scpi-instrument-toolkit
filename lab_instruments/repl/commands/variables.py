"""Variable and I/O commands: set, print, pause, input, sleep."""

import builtins
import contextlib
import re
import time

from lab_instruments.src.terminal import ColorPrinter

from ..syntax import safe_eval, substitute_vars
from .base import BaseCommand

# Unit auto-detection from last configured instrument mode
_MODE_UNIT_MAP = {
    # DMM modes
    "vdc": "V",
    "vac": "V",
    "idc": "A",
    "iac": "A",
    "res": "ohms",
    "fres": "ohms",
    "freq": "Hz",
    "per": "s",
    "cont": "",
    "diode": "V",
    # PSU modes
    "v": "V",
    "volt": "V",
    "voltage": "V",
    "i": "A",
    "curr": "A",
    "current": "A",
    # SMU modes (same as PSU)
}

# Pattern: <instrument_alias> (read|meas) [args...] [unit=<override>]
_INSTR_READ_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s+(read|meas)(?:\s+(.*))?$")


class VariableCommands(BaseCommand):
    """Handles set, print, pause, input, sleep commands."""

    def do_print(self, arg: str) -> None:
        """print <message> — display text; supports {var} interpolation.

        Quotes are optional but recommended for clarity:
            print "Voltage is {v}V"
            print Voltage is {v}V    # also works
        """
        msg = arg.strip()
        # Strip optional outer quotes: print "hello {v}" or print 'hello {v}'
        if len(msg) >= 2 and msg[0] in ('"', "'") and msg[-1] == msg[0]:
            msg = msg[1:-1]
        # Apply variable substitution ({var} syntax)
        msg = substitute_vars(msg, self.ctx.script_vars, self.ctx.measurements)
        builtins.print(msg)

    def do_pause(self, arg: str) -> None:
        args = self.parse_args(arg)
        prompt = " ".join(args) if args else "Press Enter to continue..."
        builtins.input(f"{ColorPrinter.YELLOW}{prompt}{ColorPrinter.RESET} ")

    def do_input(self, arg: str) -> None:
        """Legacy input command — redirects to var = input syntax."""
        ColorPrinter.error("Use: varname = input [prompt]")

    def try_instrument_read(self, varname: str, rhs: str) -> bool:
        """Attempt to handle ``varname = <instrument> read [unit=X]``.

        Returns True if the RHS matched an instrument read and was handled,
        False otherwise (caller should fall through to normal assignment).
        """
        m = _INSTR_READ_RE.match(rhs.strip())
        if not m:
            return False

        instr_token = m.group(1).lower()
        _verb = m.group(2)  # "read" or "meas" — both handled identically
        extra = m.group(3) or ""

        # Parse extra tokens: mode args and unit= override
        unit_override = ""
        meas_args = []
        for token in extra.split():
            if token.lower().startswith("unit="):
                unit_override = token.split("=", 1)[1]
            else:
                meas_args.append(token.lower())

        # Resolve the instrument: could be "dmm", "psu", "psu1", "smu", etc.
        base_type = re.sub(r"\d+$", "", instr_token)

        # Check if it's a known instrument type
        known_types = ("dmm", "psu", "scope", "awg", "smu", "ev2300")
        if base_type not in known_types:
            return False

        # Resolve device name
        if instr_token in self.ctx.registry.devices:
            dev_name = instr_token
        else:
            dev_name = self.ctx.registry.resolve_type(base_type)

        if not dev_name:
            self.ctx.command_had_error = True
            if not self.ctx.registry.devices:
                ColorPrinter.warning("No instruments connected. Run 'scan' first.")
            else:
                ColorPrinter.error(f"No {base_type.upper()} found. Run 'scan' first.")
            return True

        dev = self.ctx.registry.get_device(dev_name)
        if not dev:
            self.ctx.command_had_error = True
            return True

        # Determine measurement mode from args
        mode_arg = meas_args[0] if meas_args else ""

        # Execute the measurement
        try:
            if base_type == "ev2300":
                value, auto_unit = self._ev2300_read(dev, dev_name, _verb, meas_args)
            elif base_type == "smu":
                value, auto_unit = self._smu_meas(dev, dev_name, mode_arg)
            elif base_type == "psu":
                value, auto_unit = self._psu_meas(dev, dev_name, mode_arg)
            elif base_type == "scope":
                value, auto_unit = self._scope_meas(dev, dev_name, meas_args)
            else:
                # DMM, awg — use .read()
                value = dev.read()
                mode = self.ctx.last_instrument_mode.get(dev_name, "")
                auto_unit = _MODE_UNIT_MAP.get(mode, "")
        except Exception as exc:
            ColorPrinter.error(f"Instrument read failed: {exc}")
            self.ctx.command_had_error = True
            return True

        unit = unit_override or auto_unit

        # Store in both script_vars AND measurement store
        self.ctx.script_vars[varname] = str(value)
        self.ctx.measurements.record(varname, value, unit, dev_name)
        suffix = f" {unit}" if unit else ""
        ColorPrinter.cyan(f"{varname} = {value}{suffix}")
        return True

    def _psu_meas(self, dev, dev_name: str, mode_arg: str) -> tuple:
        """Measure from PSU. Returns (value, auto_unit)."""
        mode = mode_arg or self.ctx.last_instrument_mode.get(dev_name, "v")
        if mode in ("i", "curr", "current"):
            return dev.measure_current(), "A"
        return dev.measure_voltage(), "V"

    def _smu_meas(self, dev, dev_name: str, mode_arg: str) -> tuple:
        """Measure from SMU. Returns (value, auto_unit)."""
        mode = mode_arg or self.ctx.last_instrument_mode.get(dev_name, "v")
        if mode in ("i", "curr", "current"):
            return dev.measure_current(), "A"
        return dev.measure_voltage(), "V"

    def _scope_meas(self, dev, dev_name: str, meas_args: list) -> tuple:
        """Measure from scope. Expects meas_args like ['1', 'frequency'].

        Returns (value, auto_unit).
        """
        _SCOPE_UNIT_MAP = {
            "frequency": "Hz",
            "period": "s",
            "pk2pk": "V",
            "rms": "V",
            "mean": "V",
            "maximum": "V",
            "minimum": "V",
            "amplitude": "V",
        }
        # Parse channel and measurement type from args
        ch = 1
        mtype = "frequency"
        if len(meas_args) >= 2:
            try:
                ch = int(meas_args[0])
            except ValueError:
                ch = 1
            mtype = meas_args[1].lower()
        elif len(meas_args) == 1:
            # Could be just a type or just a channel
            try:
                ch = int(meas_args[0])
            except ValueError:
                mtype = meas_args[0].lower()

        value = dev.measure_bnf(ch, mtype.upper())
        auto_unit = _SCOPE_UNIT_MAP.get(mtype, "")
        return value, auto_unit

    def _ev2300_read(self, dev, dev_name: str, verb: str, meas_args: list) -> tuple:
        """Read from EV2300. Handles read_word, read_byte, read_block.

        meas_args: remaining tokens after the verb, e.g. ['0x08', '0x0c']
        Returns (value, auto_unit).
        """
        if len(meas_args) < 2:
            raise ValueError(f"ev2300 {verb} requires <i2c_addr> <register>")
        addr = int(meas_args[0], 0)
        reg = int(meas_args[1], 0)
        if verb == "read_word":
            result = dev.read_word(addr, reg)
            if result.get("ok") and result.get("value") is not None:
                return result["value"], ""
            raise ValueError(f"read_word failed: {result.get('status_text', 'unknown error')}")
        elif verb == "read_byte":
            result = dev.read_byte(addr, reg)
            if result.get("ok") and result.get("value") is not None:
                return result["value"], ""
            raise ValueError(f"read_byte failed: {result.get('status_text', 'unknown error')}")
        elif verb == "read_block":
            result = dev.read_block(addr, reg)
            if result.get("ok") and result.get("block") is not None:
                block = result["block"]
                return " ".join(f"{b:02X}" for b in block), ""
            raise ValueError(f"read_block failed: {result.get('status_text', 'unknown error')}")
        else:
            raise ValueError(f"Unknown ev2300 verb: {verb}")

    def try_calc_assignment(self, varname: str, rhs: str) -> bool:
        """Attempt to handle ``varname = calc [label] <expr> [unit=X]``.

        Returns True if the RHS starts with 'calc' and was handled,
        False otherwise (caller should fall through to normal assignment).
        """
        stripped = rhs.strip()
        if not stripped.lower().startswith("calc"):
            return False
        # Strip the leading 'calc' keyword
        after_calc = stripped[4:].strip()
        if not after_calc:
            ColorPrinter.warning("calc expects an expression.")
            return True

        # Parse tokens to extract unit= if present
        tokens = after_calc.split()
        unit = ""
        non_unit_tokens = []
        for token in tokens:
            if token.lower().startswith("unit="):
                unit = token.split("=", 1)[1]
            else:
                non_unit_tokens.append(token)

        # Strip unit=... from the raw expression string
        expr = re.sub(r"(?<!\S)unit=\S+", "", after_calc).strip()
        if not expr:
            ColorPrinter.warning("calc expects an expression.")
            return True

        # Substitute {name} variables in expr
        expr = substitute_vars(expr, self.ctx.script_vars, self.ctx.measurements)

        # Build names dict with 'last' from measurement store
        names = {}
        if self.ctx.measurements:
            last_entry = self.ctx.measurements.get_last()
            if last_entry:
                names["last"] = last_entry["value"]

        try:
            value = safe_eval(expr, names)
        except Exception as exc:
            ColorPrinter.error(f"calc failed: {exc}")
            self.ctx.command_had_error = True
            return True

        # Store in both script_vars AND measurement store
        self.ctx.script_vars[varname] = str(value)
        self.ctx.measurements.record(varname, value, unit, "calc")
        suffix = f" {unit}" if unit else ""
        ColorPrinter.cyan(f"{varname} = {value}{suffix}")
        return True

    def _assign_var(self, key: str, raw_val: str) -> None:
        """Core variable assignment — shared by 'var = expr' and 'set var expr'.

        Supports an optional ``unit=<str>`` suffix: if present, the computed value
        is also recorded in the measurement store with the given unit.
        """
        raw_val = substitute_vars(raw_val, self.ctx.script_vars, self.ctx.measurements)
        # Extract optional unit= annotation (must appear at the very end)
        unit = ""
        unit_match = re.search(r"(?<!\S)unit=(\S+)\s*$", raw_val)
        if unit_match:
            unit = unit_match.group(1)
            raw_val = raw_val[: unit_match.start()].strip()
        # input: VAR = input [prompt]
        inp_parts = raw_val.split(None, 1)
        if inp_parts and inp_parts[0] == "input":
            prompt = inp_parts[1] if len(inp_parts) > 1 else f"{key}: "
            value = builtins.input(f"{ColorPrinter.YELLOW}{prompt}{ColorPrinter.RESET} ")
            self.ctx.script_vars[key] = value
            ColorPrinter.success(f"{key} = {value!r}")
            return
        # linspace: VAR = linspace start stop [count]
        ls_parts = raw_val.split()
        if ls_parts and ls_parts[0] == "linspace" and len(ls_parts) >= 3:
            try:
                ls_start = float(ls_parts[1])
                ls_stop = float(ls_parts[2])
                ls_count = int(ls_parts[3]) if len(ls_parts) >= 4 else 11
                if ls_count < 2:
                    raise ValueError("count must be >= 2")
                ls_step = (ls_stop - ls_start) / (ls_count - 1)
                ls_vals = [ls_start + i * ls_step for i in range(ls_count)]
                self.ctx.script_vars[key] = " ".join(f"{v:g}" for v in ls_vals)
                ColorPrinter.success(f"{key} = [{self.ctx.script_vars[key]}]")
                return
            except (ValueError, ZeroDivisionError) as exc:
                ColorPrinter.error(f"linspace: {exc}")
                return
        try:
            num_vars = {}
            for k, v in self.ctx.script_vars.items():
                with contextlib.suppress(TypeError, ValueError):
                    num_vars[k] = float(v)
            result = safe_eval(raw_val, num_vars)
            self.ctx.script_vars[key] = str(result)
        except Exception:
            self.ctx.script_vars[key] = raw_val
        if unit:
            with contextlib.suppress(TypeError, ValueError):
                self.ctx.measurements.record(key, float(self.ctx.script_vars[key]), unit, "assignment")
        suffix = f" {unit}" if unit else ""
        ColorPrinter.success(f"{key} = {self.ctx.script_vars[key]}{suffix}")

    def do_set(self, arg: str) -> None:
        """set -e / set +e — control exit-on-error behavior."""
        args = self.parse_args(arg)
        if args and args[0] in ("-e", "+e"):
            flag = args[0]
            self.ctx.exit_on_error = flag == "-e"
            ColorPrinter.info(f"Exit on error {'enabled' if self.ctx.exit_on_error else 'disabled'}")
            return
        if not args:
            if self.ctx.script_vars:
                ColorPrinter.info("Current variables:")
                for k, v in self.ctx.script_vars.items():
                    print(f"  {k} = {v}")
            else:
                ColorPrinter.info("No variables defined. Use: varname = value")
            return
        ColorPrinter.error(
            f"Unknown: set {arg}. Use 'var = expr' for assignment, 'set -e' / 'set +e' for error control."
        )

    def do_unset(self, arg: str) -> None:
        """unset <varname> — delete a script variable."""
        args = self.parse_args(arg)
        if not args:
            ColorPrinter.warning("Usage: unset <varname>")
            return
        varname = args[0]
        if varname in self.ctx.script_vars:
            del self.ctx.script_vars[varname]
            ColorPrinter.success(f"Unset '{varname}'")
        else:
            ColorPrinter.warning(f"Variable '{varname}' is not defined")

    def do_pyeval(self, arg: str) -> None:
        """pyeval <expr> — evaluate a Python expression with access to REPL variables.

        The expression has access to all script_vars as local names,
        measurements via the ``m`` dict, and common builtins.
        The result is printed and stored in the special variable ``_``.

        Examples:
            pyeval 2 ** 10
            pyeval sum(float(v) for k, v in vars.items() if k.startswith("reading_"))
            pyeval [v for v in sorted(vars.keys())]
            pyeval f"Power: {float(voltage) * float(current):.4f} W"
        """
        args_raw = arg.strip()
        if not args_raw:
            self.print_colored_usage(
                [
                    "# PYEVAL — inline Python expression evaluator",
                    "",
                    "pyeval <expression>",
                    "  - evaluate any Python expression",
                    "  - has access to: vars (script variables), m (measurements dict)",
                    '  - result is printed and stored in variable "_"',
                    "",
                    "  Available names:",
                    "    vars     — dict of all REPL script variables",
                    "    m        — {label: value} from measurements",
                    "    entries  — full measurement entry list",
                    "    pi, e    — math constants",
                    "    sin, cos, tan, sqrt, log, log10, exp, ceil, floor",
                    "    abs, min, max, sum, round, pow, len, int, float, str",
                    "    hex, bin, oct, ord, chr, bool, sorted, reversed, range",
                    "    enumerate, zip, map, filter, list, tuple, dict, set",
                    "",
                    "  Examples:",
                    "    pyeval 2 ** 10",
                    "    pyeval sqrt(float(vars['voltage']) ** 2 + float(vars['current']) ** 2)",
                    "    pyeval f\"Power = {float(vars['v']) * float(vars['i']):.2f} W\"",
                    "    pyeval sorted(vars.keys())",
                    "    pyeval sum(e['value'] for e in entries if e['unit'] == 'V')",
                ]
            )
            return

        import math as _math

        # Build a safe namespace with useful builtins
        ns: dict = {
            # REPL state
            "vars": dict(self.ctx.script_vars),
            "m": self.ctx.measurements.as_value_dict(),
            "entries": self.ctx.measurements.entries,
            # Math constants
            "pi": _math.pi,
            "e": _math.e,
            "inf": _math.inf,
            "nan": _math.nan,
            # Math functions
            "sqrt": _math.sqrt,
            "log": _math.log,
            "log2": _math.log2,
            "log10": _math.log10,
            "exp": _math.exp,
            "sin": _math.sin,
            "cos": _math.cos,
            "tan": _math.tan,
            "asin": _math.asin,
            "acos": _math.acos,
            "atan": _math.atan,
            "atan2": _math.atan2,
            "degrees": _math.degrees,
            "radians": _math.radians,
            "ceil": _math.ceil,
            "floor": _math.floor,
            "hypot": _math.hypot,
            # Builtins
            "abs": abs,
            "min": min,
            "max": max,
            "sum": sum,
            "round": round,
            "pow": pow,
            "len": len,
            "divmod": divmod,
            "int": int,
            "float": float,
            "str": str,
            "bool": bool,
            "hex": hex,
            "bin": bin,
            "oct": oct,
            "ord": ord,
            "chr": chr,
            "sorted": sorted,
            "reversed": reversed,
            "range": range,
            "enumerate": enumerate,
            "zip": zip,
            "map": map,
            "filter": filter,
            "list": list,
            "tuple": tuple,
            "dict": dict,
            "set": set,
            "True": True,
            "False": False,
            "None": None,
        }
        # Also inject vars directly so you can write `voltage` instead of `vars['voltage']`
        for k, v in self.ctx.script_vars.items():
            if k.isidentifier() and k not in ns:
                try:
                    ns[k] = float(v)
                except (ValueError, TypeError):
                    ns[k] = v

        try:
            result = eval(args_raw, {"__builtins__": {}}, ns)  # noqa: S307
            if result is not None:
                builtins.print(result)
            self.ctx.script_vars["_"] = str(result)
        except Exception as exc:
            ColorPrinter.error(f"pyeval: {exc}")

    def do_sleep(self, arg: str) -> None:
        args = self.parse_args(arg)
        if self.is_help(args) or not args:
            self.print_colored_usage(
                [
                    "# SLEEP",
                    "",
                    "sleep <duration>[us|ms|s|m]",
                    "  - pause for a specified time",
                    "  - suffix: us (microseconds), ms (milliseconds), s (seconds), m (minutes)",
                    "  - default unit is seconds",
                    "",
                    "  - example: sleep 0.5",
                    "  - example: sleep 500ms",
                    "  - example: sleep 100us",
                    "  - example: sleep 2m",
                ]
            )
            return
        raw = " ".join(args)
        delay = None
        label = raw
        suffix_map = [("us", 1e-6), ("ms", 1e-3), ("s", 1.0), ("m", 60.0)]
        for suffix, factor in suffix_map:
            if raw.endswith(suffix):
                try:
                    delay = float(raw[: -len(suffix)]) * factor
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
        self.ctx.interrupt_requested = False
        while True:
            if self.ctx.interrupt_requested:
                print()
                return
            remaining = end_time - time.time()
            if remaining <= 0:
                break
            time.sleep(min(0.05, remaining))
