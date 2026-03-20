"""PSU command handler for the REPL."""

import inspect
from typing import Any

from lab_instruments.src.terminal import ColorPrinter

from ..context import ReplContext
from .base import BaseCommand
from .safety import SafetySystem

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


class PsuCommand(BaseCommand):
    """Handler for PSU commands."""

    def __init__(self, ctx: ReplContext) -> None:
        super().__init__(ctx)
        self.safety = SafetySystem(ctx)

    def execute(self, arg: str, dev: Any, psu_name: str) -> None:
        """Execute a PSU command.

        The shell calls this like ``self._psu_cmd.execute(arg, dev, psu_name)``.
        """
        # Detect single-channel by checking if measure_voltage() takes a channel arg
        try:
            sig = inspect.signature(dev.measure_voltage)
            is_single_channel = "channel" not in sig.parameters
        except (ValueError, TypeError):
            is_single_channel = False

        args = self.parse_args(arg)
        args, help_flag = self.strip_help(args)

        if not args:
            self._show_help(is_single_channel)
            return

        cmd_name = args[0].lower()

        try:
            # CHAN COMMAND -- psu chan on|off (single) or psu chan <1|2|3|all> on|off (multi)
            if cmd_name == "chan" and (
                (is_single_channel and len(args) >= 2)
                or (not is_single_channel and len(args) >= 3)
            ):
                state = args[-1].lower() == "on"
                if state and not self.safety.check_psu_output_allowed(psu_name):
                    return
                dev.enable_output(state)
                ColorPrinter.success(f"Output {'enabled' if state else 'disabled'}")

            # SET COMMAND - unified for both single and multi-channel
            elif cmd_name == "set":
                self._handle_set(args, dev, psu_name, is_single_channel)

            # MEAS COMMAND - unified for both single and multi-channel
            elif cmd_name == "meas":
                self._handle_meas(args, dev, psu_name, is_single_channel)

            # MEAS_STORE COMMAND - unified for both single and multi-channel
            elif cmd_name == "meas_store":
                self._handle_meas_store(args, dev, psu_name, is_single_channel)

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

            # ON / OFF SHORTHAND -- psu on / psu off
            elif cmd_name in ("on", "off") and len(args) == 1:
                state = cmd_name == "on"
                if state and not self.safety.check_psu_output_allowed(psu_name):
                    return
                dev.enable_output(state)
                ColorPrinter.success(f"Output {'enabled' if state else 'disabled'}")

            # STATE COMMAND -- delegated to shell
            elif cmd_name == "state" and len(args) >= 2:
                self._state_callback(psu_name, args[1])

            else:
                ColorPrinter.warning(f"Unknown PSU command: psu {arg}. Type 'psu' for help.")

        except Exception as exc:
            ColorPrinter.error(str(exc))

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def set_state_callback(self, callback) -> None:
        """Register the shell's ``do_state`` so we can delegate ``psu state`` commands."""
        self._state_callback = callback

    def _state_callback(self, dev_name: str, state_arg: str) -> None:
        """Default no-op; overridden by set_state_callback."""
        ColorPrinter.warning("state command not wired up")

    def _show_help(self, is_single_channel: bool) -> None:
        if is_single_channel:
            self.print_colored_usage(
                [
                    "# PSU",
                    "",
                    "psu on|off",
                    "psu chan on|off",
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
            self.print_colored_usage(
                [
                    "# PSU",
                    "",
                    "psu chan <1|2|3|all> on|off",
                    "psu set <channel> <voltage> [current]",
                    "  - channels: 1 (6V), 2 (25V+), 3 (25V-)",
                    "  - example: psu set 1 5.0 0.2",
                    "  - example: psu set 2 12.0 0.5",
                    "psu meas <channel> v|i",
                    "  - example: psu meas 1 v",
                    "psu meas_store <channel> v|i <label> [unit=]",
                    "psu track on|off",
                    "psu save <1-3>",
                    "psu recall <1-3>",
                    "psu state on|off|safe|reset",
                ]
            )

    def _handle_set(self, args, dev, psu_name, is_single_channel) -> None:
        if is_single_channel:
            # Single-channel: psu set <voltage> [current]
            if len(args) < 2:
                ColorPrinter.warning("Usage: psu set <voltage> [current]")
                return
            voltage = float(args[1])
            current = float(args[2]) if len(args) >= 3 else None
            if not self.safety.check_psu_limits(psu_name, None, voltage=voltage, current=current):
                return
            dev.set_voltage(voltage)
            if current is not None:
                dev.set_current_limit(current)
            ColorPrinter.success(f"Set: {voltage}V @ {current if current else dev.get_current_limit()}A")
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
            psu_ch = int(args[1]) if args[1].isdigit() else None
            if not self.safety.check_psu_limits(psu_name, psu_ch, voltage=voltage, current=current):
                return
            dev.set_output_channel(channel, voltage, current)
            ColorPrinter.success(f"Set {args[1].upper()}: {voltage}V" + (f" @ {current}A" if current else ""))

    def _handle_meas(self, args, dev, psu_name, is_single_channel) -> None:
        no_readback = getattr(dev, "SUPPORTS_READBACK", True) is False
        if no_readback:
            ColorPrinter.warning(
                f"{psu_name}: this device has no readback support — "
                "use an external DMM for real measurements. "
                "Use 'psu get' to see cached setpoints."
            )
            return
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
            # Multi-channel: psu meas <channel> v|i
            if len(args) < 3:
                ColorPrinter.warning("Usage: psu meas <channel> v|i")
                return
            channel = PSU_CHANNEL_ALIASES.get(args[1].lower())
            mode = args[2].lower()
            if not channel:
                ColorPrinter.warning("Invalid channel. Use 1, 2, or 3")
                return
            if mode in ("v", "volt", "voltage"):
                ColorPrinter.cyan(str(dev.measure_voltage(channel)))
            elif mode in ("i", "curr", "current"):
                ColorPrinter.cyan(str(dev.measure_current(channel)))
            else:
                ColorPrinter.warning("psu meas <channel> v|i")

    def _handle_meas_store(self, args, dev, psu_name, is_single_channel) -> None:
        if getattr(dev, "SUPPORTS_READBACK", True) is False:
            ColorPrinter.warning(
                f"{psu_name}: this device has no readback support — "
                "cannot store measurements. Use an external DMM."
            )
            return
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
            self.measurements.record(label, value, unit, "psu.meas")
            ColorPrinter.cyan(str(value))
        else:
            # Multi-channel: psu meas_store <channel> v|i <label> [unit=]
            if len(args) < 4:
                ColorPrinter.warning("Usage: psu meas_store <channel> v|i <label> [unit=]")
                return
            channel = PSU_CHANNEL_ALIASES.get(args[1].lower())
            mode = args[2].lower()
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
                ColorPrinter.warning("psu meas_store <channel> v|i <label>")
                return
            self.measurements.record(label, value, unit, "psu.meas")
            ColorPrinter.cyan(str(value))
