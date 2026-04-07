"""PSU command handler for the REPL."""

from typing import Any

from lab_instruments.src.terminal import ColorPrinter

from ..context import ReplContext
from .base import BaseCommand
from .safety import SafetySystem


def _resolve_channel(dev, ch_str):
    """Resolve a channel number string to the device's channel object.

    Tries CHANNEL_FROM_NUMBER first (new enum-based protocol), then falls
    back to positional indexing into CHANNEL_MAP (legacy string protocol).
    Returns None if the channel number is out of range or unrecognised.
    """
    # New protocol: CHANNEL_FROM_NUMBER → enum members
    channel_from_num = getattr(dev.__class__, "CHANNEL_FROM_NUMBER", {})
    if channel_from_num:
        try:
            return channel_from_num.get(int(ch_str))
        except ValueError:
            return None

    # Legacy protocol: CHANNEL_MAP → positional string keys
    old_map = getattr(dev, "CHANNEL_MAP", {})
    if old_map and ch_str.isdigit():
        keys = list(old_map.keys())
        idx = int(ch_str) - 1
        if 0 <= idx < len(keys):
            return keys[idx]

    return None


class PsuCommand(BaseCommand):
    """Handler for PSU commands."""

    def __init__(self, ctx: ReplContext) -> None:
        super().__init__(ctx)
        self.safety = SafetySystem(ctx)

    def execute(self, arg: str, dev: Any, psu_name: str) -> None:
        """Execute a PSU command.

        The shell calls this like ``self._psu_cmd.execute(arg, dev, psu_name)``.
        """
        # Detect multi-channel by whether the device has a select_channel method or CHANNEL_MAP.
        # Inspecting parameter names is fragile (mocks use 'ch', real devices may vary).
        is_single_channel = not (
            hasattr(dev, "select_channel")
            or bool(getattr(dev.__class__, "CHANNEL_FROM_NUMBER", None))
            or bool(getattr(dev, "CHANNEL_MAP", None))
        )

        args = self.parse_args(arg)
        args, help_flag = self.strip_help(args)

        if not args:
            self._show_help(is_single_channel)
            return

        cmd_name = args[0].lower()

        try:
            # CHAN COMMAND -- psu chan on|off (single) or psu chan <1|2|3|all> on|off (multi)
            if cmd_name == "chan" and (
                (is_single_channel and len(args) == 2) or (not is_single_channel and len(args) >= 3)
            ):
                if is_single_channel and len(args) == 2 and args[1].lower() not in ("on", "off"):
                    ColorPrinter.warning("Usage: psu chan on|off")
                    return
                state = args[-1].lower() == "on"
                if state and not self.safety.check_psu_output_allowed(psu_name):
                    return
                # Multi-channel: select channel before toggling output
                if not is_single_channel and len(args) >= 3:
                    ch_str = args[1].lower()
                    if ch_str != "all":
                        channel = _resolve_channel(dev, args[1])
                        if not channel:
                            ch_count = len(
                                getattr(dev.__class__, "CHANNEL_FROM_NUMBER", None) or getattr(dev, "CHANNEL_MAP", {})
                            )
                            ColorPrinter.warning(f"Invalid channel. Use 1-{ch_count} or 'all'")
                            return
                        if hasattr(dev, "select_channel"):
                            dev.select_channel(channel)
                dev.enable_output(state)
                ColorPrinter.success(f"Output {'enabled' if state else 'disabled'}")

            # SET COMMAND - unified for both single and multi-channel
            elif cmd_name == "set":
                self._handle_set(args, dev, psu_name, is_single_channel)

            # MEAS COMMAND - unified for both single and multi-channel
            elif cmd_name == "meas":
                self._handle_meas(args, dev, psu_name, is_single_channel)

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
                    "  - or assign: value = psu read [unit=]",
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
                    "  - or assign: value = psu read [unit=]",
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
            channel = _resolve_channel(dev, args[1])
            if channel is None:
                ch_count = len(getattr(dev.__class__, "CHANNEL_FROM_NUMBER", None) or getattr(dev, "CHANNEL_MAP", {}))
                ColorPrinter.warning(f"Invalid channel. Use 1-{ch_count}")
                return
            voltage = float(args[2])
            current = float(args[3]) if len(args) >= 4 else None
            psu_ch = int(args[1]) if args[1].isdigit() else None
            if not self.safety.check_psu_limits(psu_name, psu_ch, voltage=voltage, current=current):
                return
            dev.set_output_channel(channel, voltage, current)
            ColorPrinter.success(f"Set {args[1].upper()}: {voltage}V" + (f" @ {current}A" if current else ""))

    def _handle_meas(self, args, dev, psu_name, is_single_channel) -> None:
        # Track the last measurement mode for unit auto-detection
        if is_single_channel and len(args) >= 2:
            self.ctx.last_instrument_mode[psu_name] = args[1].lower()
        elif not is_single_channel and len(args) >= 3:
            self.ctx.last_instrument_mode[psu_name] = args[2].lower()
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
            channel = _resolve_channel(dev, args[1])
            mode = args[2].lower()
            if channel is None:
                ch_count = len(getattr(dev.__class__, "CHANNEL_FROM_NUMBER", None) or getattr(dev, "CHANNEL_MAP", {}))
                ColorPrinter.warning(f"Invalid channel. Use 1-{ch_count}")
                return
            if mode in ("v", "volt", "voltage"):
                ColorPrinter.cyan(str(dev.measure_voltage(channel)))
            elif mode in ("i", "curr", "current"):
                ColorPrinter.cyan(str(dev.measure_current(channel)))
            else:
                ColorPrinter.warning("psu meas <channel> v|i")
