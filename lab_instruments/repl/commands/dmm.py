"""DMM command handler for the REPL."""

import time
from typing import Any

from lab_instruments.src.terminal import ColorPrinter

from ..capabilities import Capability
from ..context import ReplContext
from .base import BaseCommand

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
    "cap": "capacitance",
    "temp": "temperature",
}


class DmmCommand(BaseCommand):
    """Handler for DMM (digital multimeter) commands."""

    def __init__(self, ctx: ReplContext) -> None:
        super().__init__(ctx)

    def execute(self, arg: str, dev: Any, dev_name: str) -> None:
        """Execute a DMM command.

        The shell calls this like ``self._dmm_cmd.execute(arg, dev, dmm_name)``.
        """
        # Detect capabilities
        caps = self.registry.get_caps(dev)
        has_display_control = bool(caps & Capability.DMM_DISPLAY_CONTROL)
        has_display_text = bool(caps & Capability.DMM_DISPLAY_TEXT)
        has_fetch = bool(caps & Capability.DMM_FETCH)
        has_beep = bool(caps & Capability.DMM_BEEP)
        has_ranges = bool(caps & Capability.DMM_RANGES)
        # "is_owon" equivalent: device has NONE capabilities (no NPLC, no display text, etc.)
        is_basic = caps == Capability.NONE

        args = self.parse_args(arg)
        args, help_flag = self.strip_help(args)

        if not args:
            self._show_help()
            return

        cmd_name = args[0].lower()

        # Show ranges
        if cmd_name in ("ranges", "limits"):
            self._handle_ranges(has_ranges, is_basic)
            return

        try:
            # CONFIG COMMAND - unified for all DMM types
            if cmd_name in ("config", "mode") and len(args) >= 2:
                self._handle_config(args, dev, dev_name, is_basic)

            # READ COMMAND
            elif cmd_name == "read":
                ColorPrinter.cyan(str(dev.read()))

            # FETCH COMMAND
            elif cmd_name == "fetch":
                if has_fetch and hasattr(dev, "fetch"):
                    ColorPrinter.cyan(str(dev.fetch()))
                else:
                    ColorPrinter.warning("'fetch' command not available on this DMM")

            # MEAS COMMAND
            elif cmd_name == "meas" and len(args) >= 2:
                self._handle_meas(args, dev, is_basic)

            # BEEP COMMAND
            elif cmd_name == "beep":
                if has_beep and hasattr(dev, "beep"):
                    dev.beep()
                else:
                    ColorPrinter.warning("'beep' command not available on this DMM")

            # DISPLAY COMMAND
            elif cmd_name == "display" and len(args) >= 2:
                if has_display_control and hasattr(dev, "set_display"):
                    dev.set_display(args[1].lower() == "on")
                else:
                    ColorPrinter.warning("'display' command not available on this DMM")

            # TEXT COMMAND
            elif cmd_name == "text":
                if has_display_text and hasattr(dev, "display_text"):
                    self._handle_text(args, dev)
                else:
                    ColorPrinter.warning("'text' command not available on this DMM")

            # TEXT_LOOP COMMAND
            elif cmd_name == "text_loop":
                if has_display_text:
                    self._handle_text_loop(args, dev)
                else:
                    ColorPrinter.warning("'text_loop' command not available on this DMM")

            # CLEARTEXT COMMAND
            elif cmd_name == "cleartext":
                if has_display_text and hasattr(dev, "clear_display"):
                    dev.clear_display()
                else:
                    ColorPrinter.warning("'cleartext' command not available on this DMM")

            # STATE COMMAND
            elif cmd_name == "state" and len(args) >= 2:
                self._state_callback(dev_name, args[1])

            else:
                ColorPrinter.warning(f"Unknown DMM command: dmm {arg}. Type 'dmm' for help.")

        except Exception as exc:
            ColorPrinter.error(str(exc))

    # ------------------------------------------------------------------
    # Callback wiring
    # ------------------------------------------------------------------

    def set_state_callback(self, callback) -> None:
        """Register the shell's ``do_state`` so we can delegate ``dmm state`` commands."""
        self._state_callback = callback

    def _state_callback(self, dev_name: str, state_arg: str) -> None:
        """Default no-op; overridden by set_state_callback."""
        ColorPrinter.warning("state command not wired up")

    # ------------------------------------------------------------------
    # Help
    # ------------------------------------------------------------------

    def _show_help(self) -> None:
        self.print_colored_usage(
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
                "  - or assign: value = dmm read [unit=]",
                "dmm fetch",
                "dmm meas <mode> [range] [res]",
                "dmm beep",
                "dmm display on|off",
                "dmm text <message> [scroll=auto|on|off] [delay=] [loops=] [pad=] [width=]",
                "dmm ranges",
                "dmm state safe|reset",
            ]
        )

    # ------------------------------------------------------------------
    # Sub-handlers
    # ------------------------------------------------------------------

    def _handle_ranges(self, has_ranges: bool, is_basic: bool) -> None:
        if has_ranges and not is_basic:
            C = ColorPrinter.CYAN
            Y = ColorPrinter.YELLOW
            G = ColorPrinter.GREEN
            R = ColorPrinter.RESET
            B = ColorPrinter.BOLD
            print(f"\n{B}Valid DMM ranges / res / nplc  (HP 34401A){R}\n")
            rows = [
                ("vdc", "0.1 | 1 | 10 | 100 | 1000", "numeric", "0.02 | 0.2 | 1 | 10 | 100"),
                ("vac", "0.1 | 1 | 10 | 100 | 750", "numeric", "\u2014"),
                ("idc", "0.01 | 0.1 | 1 | 3", "numeric", "0.02 | 0.2 | 1 | 10 | 100"),
                ("iac", "0.01 | 0.1 | 1 | 3", "numeric", "\u2014"),
                ("res/fres", "100 | 1k | 10k | 100k | 1M | 10M | 100M", "numeric", "\u2014"),
                ("freq/per", "0.1 | 1 | 10 | 100 | 750", "numeric", "\u2014"),
                ("cont/diode", "fixed (no args)", "\u2014", "\u2014"),
            ]
            hdr = f"  {Y}{'Mode':<10}{R} {G}{'Range':<42}{R} {'Res':<10} {'nplc'}"
            print(hdr)
            print(f"  {Y}{'-' * 10}{R} {G}{'-' * 42}{R} {'-' * 10} {'-' * 26}")
            for mode, rng, res, nplc in rows:
                print(f"  {C}{mode:<10}{R} {rng:<42} {res:<10} {nplc}")
            print(f"\n  All range/res args also accept: {Y}MIN | MAX | DEF | AUTO{R}\n")
        else:
            ColorPrinter.info("Owon DMM auto-configures ranges. No manual range specification needed.")

    def _handle_config(self, args, dev, dev_name: str, is_basic: bool) -> None:
        mode_arg = args[1].lower()
        mode = DMM_MODE_ALIASES.get(mode_arg, mode_arg)

        # Track last configured mode for unit auto-detection
        self.ctx.last_instrument_mode[dev_name] = mode_arg

        if is_basic:
            # Basic DMM: Simple mode setting only
            dev.set_mode(mode_arg)
            ColorPrinter.success(f"Mode set to: {mode_arg}")
        else:
            # Full-featured DMM: Support range/resolution/nplc parameters (optional)
            if not mode or mode not in DMM_MODE_ALIASES.values():
                # Try without alias
                mode = mode_arg

            func = getattr(dev, f"configure_{mode}", None)
            if not func:
                ColorPrinter.warning(f"Invalid mode '{mode_arg}'. Type 'dmm' for options.")
                return

            # Handle modes that don't take parameters
            if mode in ("continuity", "diode", "temperature"):
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

    def _handle_meas(self, args, dev, is_basic: bool) -> None:
        mode_arg = args[1].lower()
        mode = DMM_MODE_ALIASES.get(mode_arg, mode_arg)

        if is_basic:
            # Basic DMM: Set mode then read
            dev.set_mode(mode_arg)
            ColorPrinter.cyan(str(dev.read()))
        else:
            # Full-featured DMM: Use measure function
            if not mode or mode not in DMM_MODE_ALIASES.values():
                mode = mode_arg

            func = getattr(dev, f"measure_{mode}", None)
            if not func:
                ColorPrinter.warning(f"Invalid mode '{mode_arg}'. Type 'dmm' for options.")
                return

            # Parse optional range/resolution parameters
            range_val = args[2] if len(args) >= 3 else "DEF"
            resolution = args[3] if len(args) >= 4 else "DEF"

            if "continuity" in mode or "diode" in mode or "temperature" in mode:
                ColorPrinter.cyan(str(func()))
            elif "capacitance" in mode:
                ColorPrinter.cyan(str(func(range_val)))
            else:
                ColorPrinter.cyan(str(func(range_val, resolution)))

    def _handle_text(self, args, dev) -> None:
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

    def _handle_text_loop(self, args, dev) -> None:
        if len(args) >= 2 and args[1].lower() == "off":
            self.ctx.dmm_text_loop_active = False
            if hasattr(dev, "clear_display"):
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
            frames = [padded[i : i + width] for i in range(len(padded) - width + 1)]
            self.ctx.dmm_text_frames = frames
            self.ctx.dmm_text_index = 0
            self.ctx.dmm_text_delay = delay
            self.ctx.dmm_text_last = time.time()
            self.ctx.dmm_text_loop_active = True
            ColorPrinter.info(f"Text loop started: '{message}'")
        else:
            ColorPrinter.warning("Usage: dmm text_loop <message> [delay=] [pad=] [width=]")
