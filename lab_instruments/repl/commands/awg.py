"""AWG command handler for the REPL."""

from typing import Any

from lab_instruments.enums import WaveformType
from lab_instruments.src.terminal import ColorPrinter

from ..capabilities import Capability
from ..context import ReplContext
from .base import BaseCommand
from .safety import SafetySystem

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


class AwgCommand(BaseCommand):
    """Handler for AWG / function generator commands."""

    def __init__(self, ctx: ReplContext) -> None:
        super().__init__(ctx)
        self.safety = SafetySystem(ctx)

    def execute(self, arg: str, dev: Any, dev_name: str) -> None:
        """Execute an AWG command.

        The shell calls this like ``self._awg_cmd.execute(arg, dev, awg_name)``.
        """
        # Detect JDS6600 via capability flag
        is_jds6600 = self.registry.has_cap(dev, Capability.AWG_JDS6600_PROTOCOL)

        args = self.parse_args(arg)
        args, help_flag = self.strip_help(args)

        if not args or help_flag:
            self._show_help()
            return

        cmd_name = args[0].lower()

        try:
            # CHAN COMMAND -- enable/disable a channel output
            if cmd_name == "chan" and len(args) >= 3:
                self._handle_chan(args, dev, dev_name, is_jds6600)

            # WAVE COMMAND
            elif cmd_name == "wave" and len(args) >= 3:
                self._handle_wave(args, dev, dev_name, is_jds6600)

            # FREQ COMMAND
            elif cmd_name == "freq" and len(args) >= 3:
                self._handle_freq(args, dev, dev_name, is_jds6600)

            # AMP COMMAND
            elif cmd_name == "amp" and len(args) >= 3:
                self._handle_amp(args, dev, dev_name, is_jds6600)

            # OFFSET COMMAND
            elif cmd_name == "offset" and len(args) >= 3:
                self._handle_offset(args, dev, dev_name, is_jds6600)

            # DUTY COMMAND
            elif cmd_name == "duty" and len(args) >= 3:
                channels = self.parse_channels(args[1], max_ch=2)
                duty = float(args[2])
                if not is_jds6600 and not hasattr(dev, "set_duty_cycle"):
                    ColorPrinter.warning("Duty cycle not supported independently. Use 'awg wave' with duty=")
                    return
                for channel in channels:
                    dev.set_duty_cycle(channel, duty)
                    ColorPrinter.success(f"CH{channel}: duty {duty}%")

            # PHASE COMMAND
            elif cmd_name == "phase" and len(args) >= 3:
                channels = self.parse_channels(args[1], max_ch=2)
                phase = float(args[2])
                if not is_jds6600 and not hasattr(dev, "set_phase"):
                    ColorPrinter.warning("Phase not supported independently. Use 'awg wave' with phase=")
                    return
                for channel in channels:
                    dev.set_phase(channel, phase)
                    ColorPrinter.success(f"CH{channel}: phase {phase} deg")

            # SYNC COMMAND
            elif cmd_name == "sync" and len(args) >= 2:
                state = args[1].lower() == "on"
                if hasattr(dev, "set_sync_output"):
                    dev.set_sync_output(state)
                    ColorPrinter.success(f"Sync: {'on' if state else 'off'}")
                else:
                    ColorPrinter.warning("Sync output not available on this device.")

            # STATE COMMAND
            elif cmd_name == "state" and len(args) >= 2:
                self._state_callback(dev_name, args[1])

            # ON/OFF SHORTHAND -- "awg on <1|2|all>" / "awg off <1|2|all>"
            elif cmd_name in ("on", "off"):
                if len(args) < 2:
                    ColorPrinter.warning(f"Usage: awg {cmd_name} <1|2|all>")
                    return
                state = cmd_name == "on"
                channels = self.parse_channels(args[1], max_ch=2)
                for channel in channels:
                    if state and not self.safety.check_awg_output_allowed(dev_name, channel):
                        return
                    if is_jds6600:
                        dev.enable_output(
                            ch1=state if channel == 1 else None,
                            ch2=state if channel == 2 else None,
                        )
                    else:
                        dev.enable_output(channel, state)
                    ColorPrinter.success(f"CH{channel}: {'on' if state else 'off'}")

            else:
                ColorPrinter.warning(f"Unknown AWG command: awg {arg}. Type 'awg' for help.")

        except ValueError as e:
            ColorPrinter.error(f"Invalid value: {e}")
        except Exception as exc:
            ColorPrinter.error(str(exc))

    # ------------------------------------------------------------------
    # Callback wiring
    # ------------------------------------------------------------------

    def set_state_callback(self, callback) -> None:
        """Register the shell's ``do_state`` so we can delegate ``awg state`` commands."""
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
                "# AWG",
                "",
                "awg on|off <1|2|all>",
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

    # ------------------------------------------------------------------
    # Sub-handlers
    # ------------------------------------------------------------------

    def _handle_chan(self, args, dev, dev_name, is_jds6600) -> None:
        channels = self.parse_channels(args[1], max_ch=2)
        state = args[2].lower() == "on"
        for channel in channels:
            if state and not self.safety.check_awg_output_allowed(dev_name, channel):
                return
            if is_jds6600:
                dev.enable_output(
                    ch1=state if channel == 1 else None,
                    ch2=state if channel == 2 else None,
                )
            else:
                dev.enable_output(channel, state)
            ColorPrinter.success(f"CH{channel}: {'on' if state else 'off'}")

    def _handle_wave(self, args, dev, dev_name, is_jds6600) -> None:
        channels = self.parse_channels(args[1], max_ch=2)
        waveform = args[2].lower()

        params = {}
        for token in args[3:]:
            if "=" in token:
                key, value = token.split("=", 1)
                params[key.lower()] = float(value)

        param_str = "  " + "  ".join(f"{k}={v}" for k, v in params.items()) if params else ""
        wave_vpp = params.get("amp", params.get("amplitude"))
        wave_offset = params.get("offset")
        wave_freq = params.get("freq", params.get("frequency"))
        for channel in channels:
            if not self.safety.check_awg_limits(
                dev_name, channel, new_vpp=wave_vpp, new_offset=wave_offset, new_freq=wave_freq
            ):
                return
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
                # Normalize to SCPI abbreviations via WaveformType enum
                try:
                    scpi_wave = WaveformType.from_alias(waveform)
                except ValueError:
                    scpi_wave = waveform.upper()
                kwargs = {}
                for key, value in params.items():
                    mapped_key = AWG_WAVE_KEYS.get(key)
                    if mapped_key:
                        kwargs[mapped_key] = value
                dev.set_waveform(channel, scpi_wave, **kwargs)
            self.safety.update_awg_state(dev_name, channel, vpp=wave_vpp, offset=wave_offset)
            try:
                display_wave = WaveformType.from_alias(waveform)
            except ValueError:
                display_wave = waveform.upper()
            ColorPrinter.success(f"CH{channel}: {display_wave}{param_str}")

    def _handle_freq(self, args, dev, dev_name, is_jds6600) -> None:
        channels = self.parse_channels(args[1], max_ch=2)
        frequency = float(args[2])
        if not is_jds6600 and not hasattr(dev, "set_frequency"):
            ColorPrinter.warning("Frequency not supported independently. Use 'awg wave' with freq=")
            return
        for channel in channels:
            if not self.safety.check_awg_limits(dev_name, channel, new_freq=frequency):
                return
            dev.set_frequency(channel, frequency)
            ColorPrinter.success(f"CH{channel}: {frequency} Hz")

    def _handle_amp(self, args, dev, dev_name, is_jds6600) -> None:
        channels = self.parse_channels(args[1], max_ch=2)
        amplitude = float(args[2])
        if not is_jds6600 and not hasattr(dev, "set_amplitude"):
            ColorPrinter.warning("Amplitude not supported independently. Use 'awg wave' with amp=")
            return
        for channel in channels:
            if not self.safety.check_awg_limits(dev_name, channel, new_vpp=amplitude):
                return
            dev.set_amplitude(channel, amplitude)
            self.safety.update_awg_state(dev_name, channel, vpp=amplitude)
            ColorPrinter.success(f"CH{channel}: {amplitude} Vpp")

    def _handle_offset(self, args, dev, dev_name, is_jds6600) -> None:
        channels = self.parse_channels(args[1], max_ch=2)
        offset = float(args[2])
        if not is_jds6600 and not hasattr(dev, "set_offset"):
            ColorPrinter.warning("Offset not supported independently. Use 'awg wave' with offset=")
            return
        for channel in channels:
            if not self.safety.check_awg_limits(dev_name, channel, new_offset=offset):
                return
            dev.set_offset(channel, offset)
            self.safety.update_awg_state(dev_name, channel, offset=offset)
            ColorPrinter.success(f"CH{channel}: offset {offset} V")
