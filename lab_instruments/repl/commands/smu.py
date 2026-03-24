"""SMU (Source Measure Unit) command handler for the REPL."""

from typing import Any

from lab_instruments.src.terminal import ColorPrinter

from ..context import ReplContext
from .base import BaseCommand
from .safety import SafetySystem


class SmuCommand(BaseCommand):
    """Handler for SMU commands (NI PXIe-4139 and similar)."""

    def __init__(self, ctx: ReplContext) -> None:
        super().__init__(ctx)
        self.safety = SafetySystem(ctx)

    def execute(self, arg: str, dev: Any, smu_name: str) -> None:
        """Execute an SMU command."""
        args = self.parse_args(arg)
        args, help_flag = self.strip_help(args)

        if not args:
            self._show_help()
            return

        cmd_name = args[0].lower()

        try:
            if cmd_name in ("on", "off"):
                state = cmd_name == "on"
                if state and not self.safety.check_psu_output_allowed(smu_name):
                    return
                dev.enable_output(state)
                ColorPrinter.success(f"Output {'enabled' if state else 'disabled'}")

            elif cmd_name == "set":
                self._handle_set(args, dev, smu_name)

            elif cmd_name == "meas":
                self._handle_meas(args, dev)

            elif cmd_name == "meas_store":
                self._handle_meas_store(args, dev)

            elif cmd_name == "get":
                v = dev.get_voltage_setpoint()
                i = dev.get_current_limit()
                out = "ON" if dev.get_output_state() else "OFF"
                ColorPrinter.info(f"Setpoint: {v}V @ {i}A, Output: {out}")

            elif cmd_name == "state" and len(args) >= 2:
                self._state_callback(smu_name, args[1])

            else:
                ColorPrinter.warning(f"Unknown SMU command: smu {arg}. Type 'smu' for help.")

        except Exception as exc:
            ColorPrinter.error(str(exc))

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def set_state_callback(self, callback) -> None:
        """Register the shell's ``do_state`` so we can delegate ``smu state`` commands."""
        self._state_callback = callback

    def _state_callback(self, dev_name: str, state_arg: str) -> None:
        """Default no-op; overridden by set_state_callback."""
        ColorPrinter.warning("state command not wired up")

    def _show_help(self) -> None:
        self.print_colored_usage(
            [
                "# SMU (Source Measure Unit)",
                "",
                "smu on|off",
                "smu set <voltage> [current_limit]",
                "  - voltage: -60 to 60V, current_limit: 0 to 1A",
                "  - example: smu set 5.0 0.01",
                "smu meas v|i",
                "smu meas_store v|i <label> [unit=]",
                "smu get  (show setpoints)",
                "smu state on|off|safe|reset",
            ]
        )

    def _handle_set(self, args, dev, smu_name) -> None:
        if len(args) < 2:
            ColorPrinter.warning("Usage: smu set <voltage> [current_limit]")
            return
        voltage = float(args[1])
        current = float(args[2]) if len(args) >= 3 else None
        if not self.safety.check_psu_limits(smu_name, None, voltage=voltage, current=current):
            return
        dev.set_voltage(voltage)
        if current is not None:
            dev.set_current_limit(current)
        ColorPrinter.success(
            f"Set: {voltage}V @ {current if current else dev.get_current_limit()}A"
        )

    def _handle_meas(self, args, dev) -> None:
        if len(args) < 2:
            ColorPrinter.warning("Usage: smu meas v|i")
            return
        mode = args[1].lower()
        if mode in ("v", "volt", "voltage"):
            value = dev.measure_voltage()
            ColorPrinter.cyan(f"{value:.6f}V")
        elif mode in ("i", "curr", "current"):
            value = dev.measure_current()
            ColorPrinter.cyan(f"{value:.6f}A")
        else:
            ColorPrinter.warning("smu meas v|i")

    def _handle_meas_store(self, args, dev) -> None:
        if len(args) < 3:
            ColorPrinter.warning("Usage: smu meas_store v|i <label> [unit=]")
            return
        mode = args[1].lower()
        label = args[2]
        unit = ""
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
            ColorPrinter.warning("smu meas_store v|i <label>")
            return
        self.measurements.record(label, value, unit, "smu.meas")
        ColorPrinter.cyan(str(value))
