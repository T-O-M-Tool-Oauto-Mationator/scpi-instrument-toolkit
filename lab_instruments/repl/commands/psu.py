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
    For single-channel PSUs (no CHANNEL_MAP/CHANNEL_FROM_NUMBER), channel "1"
    returns a sentinel so callers can use a uniform code path.
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

    # Single-channel PSU: only channel 1 is valid
    if ch_str.isdigit() and int(ch_str) == 1:
        return 1  # sentinel — callers use set_output_channel which ignores it

    return None


def _channel_count(dev):
    """Return the number of channels for a device."""
    cfn = getattr(dev.__class__, "CHANNEL_FROM_NUMBER", None)
    if cfn:
        return len(cfn)
    old_map = getattr(dev, "CHANNEL_MAP", None)
    if old_map:
        return len(old_map)
    return 1


def _is_multi_channel(dev):
    return (
        hasattr(dev, "select_channel")
        or bool(getattr(dev.__class__, "CHANNEL_FROM_NUMBER", None))
        or bool(getattr(dev, "CHANNEL_MAP", None))
    )


class PsuCommand(BaseCommand):
    """Handler for PSU commands."""

    def __init__(self, ctx: ReplContext) -> None:
        super().__init__(ctx)
        self.safety = SafetySystem(ctx)

    def execute(self, arg: str, dev: Any, psu_name: str) -> None:
        """Execute a PSU command."""
        args = self.parse_args(arg)
        args, help_flag = self.strip_help(args)

        if not args:
            self._show_help(dev)
            return

        cmd_name = args[0].lower()
        ch_count = _channel_count(dev)

        try:
            # CHAN COMMAND -- psu chan <channel|all> on|off
            if cmd_name == "chan":
                if len(args) < 3:
                    ColorPrinter.warning(f"Usage: psu chan <1-{ch_count}|all> on|off")
                    return
                state = args[2].lower() == "on"
                if state and not self.safety.check_psu_output_allowed(psu_name):
                    return
                ch_str = args[1].lower()
                if ch_str != "all":
                    channel = _resolve_channel(dev, args[1])
                    if not channel:
                        ColorPrinter.warning(f"Invalid channel. Use 1-{ch_count} or 'all'")
                        return
                    if hasattr(dev, "select_channel"):
                        dev.select_channel(channel)
                dev.enable_output(state)
                ColorPrinter.success(f"Output {'enabled' if state else 'disabled'}")

            # SET COMMAND -- psu set <channel> <voltage> [current]
            elif cmd_name == "set":
                self._handle_set(args, dev, psu_name)

            # MEAS COMMAND -- psu meas <channel> v|i
            elif cmd_name == "meas":
                self._handle_meas(args, dev, psu_name)

            # GET COMMAND (single-channel only)
            elif cmd_name == "get":
                if not _is_multi_channel(dev):
                    v = dev.get_voltage_setpoint()
                    i = dev.get_current_limit()
                    out = "ON" if dev.get_output_state() else "OFF"
                    ColorPrinter.info(f"Setpoint: {v}V @ {i}A, Output: {out}")
                else:
                    ColorPrinter.warning("'get' command not available for multi-channel PSU")

            # TRACK COMMAND (multi-channel only)
            elif cmd_name == "track" and len(args) >= 2:
                if _is_multi_channel(dev):
                    dev.set_tracking(args[1].lower() == "on")
                else:
                    ColorPrinter.warning("'track' command not available for single-channel PSU")

            # SAVE/RECALL COMMANDS (multi-channel only)
            elif cmd_name == "save" and len(args) >= 2:
                if _is_multi_channel(dev):
                    dev.save_state(int(args[1]))
                else:
                    ColorPrinter.warning("'save' command not available for single-channel PSU")
            elif cmd_name == "recall" and len(args) >= 2:
                if _is_multi_channel(dev):
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

    def _show_help(self, dev) -> None:
        ch_count = _channel_count(dev)
        lines = [
            "# PSU",
            "",
            "psu on|off",
            f"psu chan <1-{ch_count}|all> on|off",
            f"psu set <channel> <voltage> [current]",
            f"  - channels: 1-{ch_count}",
            "  - example: psu set 1 5.0 0.2",
            f"psu meas <channel> v|i",
            "  - example: psu meas 1 v",
            "  - or assign: value = psu read [unit=]",
        ]
        if _is_multi_channel(dev):
            lines += [
                "psu track on|off",
                "psu save <1-3>",
                "psu recall <1-3>",
            ]
        else:
            lines.append("psu get  (show setpoints)")
        lines.append("psu state on|off|safe|reset")
        self.print_colored_usage(lines)

    def _handle_set(self, args, dev, psu_name) -> None:
        # Always: psu set <channel> <voltage> [current]
        ch_count = _channel_count(dev)
        if len(args) < 3:
            ColorPrinter.warning(f"Usage: psu set <channel> <voltage> [current]")
            ColorPrinter.warning(f"Channels: 1-{ch_count}")
            return
        channel = _resolve_channel(dev, args[1])
        if channel is None:
            ColorPrinter.warning(f"Invalid channel. Use 1-{ch_count}")
            return
        voltage = float(args[2])
        current = float(args[3]) if len(args) >= 4 else None
        psu_ch = int(args[1]) if args[1].isdigit() else None
        if not self.safety.check_psu_limits(psu_name, psu_ch, voltage=voltage, current=current):
            return
        dev.set_output_channel(channel, voltage, current)
        ColorPrinter.success(f"Set {args[1]}: {voltage}V" + (f" @ {current}A" if current else ""))

    def _handle_meas(self, args, dev, psu_name) -> None:
        # Always: psu meas <channel> v|i
        ch_count = _channel_count(dev)
        if len(args) >= 3:
            self.ctx.last_instrument_mode[psu_name] = args[2].lower()

        no_readback = getattr(dev, "SUPPORTS_READBACK", True) is False
        if no_readback:
            ColorPrinter.warning(
                f"{psu_name}: this device has no readback support — "
                "use an external DMM for real measurements. "
                "Use 'psu get' to see cached setpoints."
            )
            return

        if len(args) < 3:
            ColorPrinter.warning(f"Usage: psu meas <channel> v|i")
            return
        channel = _resolve_channel(dev, args[1])
        mode = args[2].lower()
        if channel is None:
            ColorPrinter.warning(f"Invalid channel. Use 1-{ch_count}")
            return
        if mode in ("v", "volt", "voltage"):
            if _is_multi_channel(dev):
                ColorPrinter.cyan(str(dev.measure_voltage(channel)))
            else:
                ColorPrinter.cyan(f"{dev.measure_voltage():.6f}V")
        elif mode in ("i", "curr", "current"):
            if _is_multi_channel(dev):
                ColorPrinter.cyan(str(dev.measure_current(channel)))
            else:
                ColorPrinter.cyan(f"{dev.measure_current():.6f}A")
        else:
            ColorPrinter.warning("psu meas <channel> v|i")
