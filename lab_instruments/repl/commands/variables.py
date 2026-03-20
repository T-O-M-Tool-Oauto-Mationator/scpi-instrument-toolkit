"""Variable and I/O commands: set, print, pause, input, sleep."""

import builtins
import contextlib
import time

from lab_instruments.src.terminal import ColorPrinter

from ..syntax import safe_eval, substitute_vars
from .base import BaseCommand


class VariableCommands(BaseCommand):
    """Handles set, print, pause, input, sleep commands."""

    def do_print(self, arg: str) -> None:
        """print uses raw arg string (no shlex) to avoid quote stripping."""
        msg = substitute_vars(arg, self.ctx.script_vars, self.ctx.measurements) if arg else ""
        builtins.print(f"{ColorPrinter.CYAN}{msg}{ColorPrinter.RESET}")

    def do_pause(self, arg: str) -> None:
        args = self.parse_args(arg)
        prompt = " ".join(args) if args else "Press Enter to continue..."
        builtins.input(f"{ColorPrinter.YELLOW}{prompt}{ColorPrinter.RESET} ")

    def do_input(self, arg: str) -> None:
        args = self.parse_args(arg)
        if not args:
            ColorPrinter.warning("Usage: input <varname> [prompt]")
            return
        varname = args[0]
        prompt = " ".join(args[1:]) if len(args) > 1 else f"{varname}: "
        value = builtins.input(f"{ColorPrinter.YELLOW}{prompt}{ColorPrinter.RESET} ")
        self.ctx.script_vars[varname] = value
        ColorPrinter.success(f"${varname} = {value!r}")

    def do_set(self, arg: str) -> None:
        args = self.parse_args(arg)
        if len(args) < 2:
            ColorPrinter.warning("Usage: set <varname> <expr>")
            if self.ctx.script_vars:
                ColorPrinter.info("Current variables:")
                for k, v in self.ctx.script_vars.items():
                    print(f"  {k} = {v}")
            return
        key = args[0]
        raw_val = " ".join(args[1:])
        raw_val = substitute_vars(raw_val, self.ctx.script_vars, self.ctx.measurements)
        try:
            num_vars = {}
            for k, v in self.ctx.script_vars.items():
                with contextlib.suppress(TypeError, ValueError):
                    num_vars[k] = float(v)
            result = safe_eval(raw_val, num_vars)
            self.ctx.script_vars[key] = str(result)
        except Exception:
            self.ctx.script_vars[key] = raw_val
        ColorPrinter.success(f"{key} = {self.ctx.script_vars[key]}")

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
