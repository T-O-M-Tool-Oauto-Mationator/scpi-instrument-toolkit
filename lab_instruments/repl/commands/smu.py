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

            elif cmd_name == "set_mode":
                self._handle_set_mode(args, dev, smu_name)

            elif cmd_name == "meas":
                self._handle_meas(args, dev, smu_name)

            elif cmd_name == "compliance":
                self._handle_compliance(args, dev)

            elif cmd_name == "source_delay":
                self._handle_source_delay(args, dev)

            elif cmd_name == "avg":
                self._handle_avg(args, dev)

            elif cmd_name == "temp":
                self._handle_temp(args, dev)

            elif cmd_name == "get":
                v = dev.get_voltage_setpoint()
                i = dev.get_current_limit()
                out = "ON" if dev.get_output_state() else "OFF"
                ColorPrinter.info(f"Setpoint: {v}V @ {i}A, Output: {out}")

            elif cmd_name == "state":
                if len(args) < 2:
                    self._show_help()
                    return
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
                "  - voltage: -60 to 60V, current_limit: -3 to 3A",
                "  - example: smu set 5.0 0.01",
                "smu set_mode voltage <v> [current_limit]",
                "smu set_mode current <i> [voltage_limit]",
                "  - example: smu set_mode current 0.05 5.0",
                "smu meas [v|i|vi]",
                "  - no arg or vi: atomic V+I+compliance in one call",
                "  - or assign: value = smu read [unit=]",
                "smu compliance  (query compliance state)",
                "smu source_delay [<seconds>]  (get/set settle delay)",
                "smu avg [<N>]  (get/set samples_to_average)",
                "smu temp  (read instrument temperature)",
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
        ColorPrinter.success(f"Set: {voltage}V @ {current if current else dev.get_current_limit()}A")

    def _handle_meas(self, args, dev, smu_name: str = "") -> None:
        # Track the last measurement mode for unit auto-detection
        if smu_name and len(args) >= 2:
            self.ctx.last_instrument_mode[smu_name] = args[1].lower()
        if len(args) < 2 or args[1].lower() in ("vi", "both", "all"):
            result = dev.measure_vi()
            compliance_str = " [COMPLIANCE]" if result["in_compliance"] else ""
            ColorPrinter.cyan(f"V={result['voltage']:.6f}V  I={result['current']:.6f}A{compliance_str}")
            return
        mode = args[1].lower()
        if mode in ("v", "volt", "voltage"):
            value = dev.measure_voltage()
            ColorPrinter.cyan(f"{value:.6f}V")
        elif mode in ("i", "curr", "current"):
            value = dev.measure_current()
            ColorPrinter.cyan(f"{value:.6f}A")
        else:
            ColorPrinter.warning("smu meas [v|i|vi]")

    def _handle_set_mode(self, args, dev, smu_name) -> None:
        if len(args) < 3:
            ColorPrinter.warning("Usage: smu set_mode voltage <v> [current_limit]")
            ColorPrinter.warning("       smu set_mode current <i> [voltage_limit]")
            return
        mode = args[1].lower()
        if mode in ("voltage", "v"):
            voltage = float(args[2])
            current_limit = float(args[3]) if len(args) >= 4 else None
            if not self.safety.check_psu_limits(smu_name, None, voltage=voltage, current=current_limit):
                return
            dev.set_voltage_mode(voltage, current_limit)
            suffix = f" @ {current_limit}A" if current_limit is not None else ""
            ColorPrinter.success(f"Mode: DC_VOLTAGE  {voltage}V{suffix}")
        elif mode in ("current", "i"):
            current = float(args[2])
            voltage_limit = float(args[3]) if len(args) >= 4 else None
            if not self.safety.check_psu_limits(smu_name, None, voltage=voltage_limit, current=current):
                return
            dev.set_current_mode(current, voltage_limit)
            suffix = f"  voltage_limit={voltage_limit}V" if voltage_limit is not None else ""
            ColorPrinter.success(f"Mode: DC_CURRENT  {current}A{suffix}")
        else:
            ColorPrinter.warning("smu set_mode voltage|current ...")

    def _handle_compliance(self, args, dev) -> None:
        state = dev.query_in_compliance()
        if state:
            ColorPrinter.warning("IN COMPLIANCE - output is current-limited")
        else:
            ColorPrinter.success("Not in compliance")

    def _handle_source_delay(self, args, dev) -> None:
        if len(args) < 2:
            val = dev.get_source_delay()
            ColorPrinter.info(f"source_delay = {val:.4f} s")
        else:
            seconds = float(args[1])
            dev.set_source_delay(seconds)
            ColorPrinter.success(f"source_delay set to {seconds:.4f} s")

    def _handle_avg(self, args, dev) -> None:
        if len(args) < 2:
            n = dev.get_samples_to_average()
            ColorPrinter.info(f"samples_to_average = {n}")
        else:
            n = int(args[1])
            dev.set_samples_to_average(n)
            ColorPrinter.success(f"samples_to_average set to {n}")

    def _handle_temp(self, args, dev) -> None:
        temp = dev.read_temperature()
        ColorPrinter.cyan(f"{temp:.1f} degrees C")
