"""Scope command handler for the REPL."""

import contextlib
import os
import time
from typing import Any

from lab_instruments.enums import CouplingMode, TriggerEdge, TriggerMode
from lab_instruments.src.terminal import ColorPrinter

from ..context import ReplContext
from .base import BaseCommand


class ScopeCommand(BaseCommand):
    """Handler for oscilloscope commands."""

    def __init__(self, ctx: ReplContext) -> None:
        super().__init__(ctx)

    def execute(self, arg: str, dev: Any, dev_name: str) -> None:
        """Execute a scope command.

        The shell calls this like ``self._scope_cmd.execute(arg, dev, scope_name)``.
        """
        args = self.parse_args(arg)
        args, help_flag = self.strip_help(args)
        if not args:
            self._show_help()
            return

        cmd_name = args[0].lower()
        if help_flag:
            self.print_usage(["scope ... (see main help)"])
            return

        try:
            if cmd_name == "autoset":
                dev.autoset()
                ColorPrinter.success("Autoset complete")

            elif cmd_name == "run":
                dev.run()
                ColorPrinter.success("Acquisition running")

            elif cmd_name == "stop":
                dev.stop()
                ColorPrinter.success("Acquisition stopped")

            elif cmd_name == "single":
                dev.single()
                ColorPrinter.success("Single shot armed")

            elif cmd_name == "wait_stop":
                self._handle_wait_stop(args, dev)

            elif cmd_name == "chan" and len(args) >= 3:
                channels = self.parse_channels(args[1], max_ch=4)
                enable = args[2].lower() == "on"
                for channel in channels:
                    if enable:
                        dev.enable_channel(channel)
                        ColorPrinter.success(f"CH{channel}: on")
                    else:
                        dev.disable_channel(channel)
                        ColorPrinter.info(f"CH{channel}: off")

            elif cmd_name == "coupling" and len(args) >= 3:
                channels = self.parse_channels(args[1], max_ch=4)
                try:
                    coupling_type = CouplingMode(args[2].upper())
                except ValueError:
                    coupling_type = args[2].upper()
                for channel in channels:
                    dev.set_coupling(channel, coupling_type)
                    ColorPrinter.success(f"CH{channel}: coupling {coupling_type}")

            elif cmd_name == "probe" and len(args) >= 3:
                channels = self.parse_channels(args[1], max_ch=4)
                attenuation = float(args[2])
                for channel in channels:
                    dev.set_probe_attenuation(channel, attenuation)
                    ColorPrinter.success(f"CH{channel} probe attenuation set to {attenuation}x")

            elif cmd_name == "hscale" and len(args) >= 2:
                scale = float(args[1])
                dev.set_horizontal_scale(scale)
                ColorPrinter.success(f"Horizontal scale set to {scale} s/div")

            elif cmd_name == "hpos" and len(args) >= 2:
                offset = float(args[1])
                dev.set_horizontal_offset(offset)
                ColorPrinter.success(f"Horizontal offset set to {offset} s")

            elif cmd_name == "hmove" and len(args) >= 2:
                delta = float(args[1])
                try:
                    current = dev.get_horizontal_offset()
                except Exception:
                    current = 0.0
                dev.set_horizontal_offset(current + delta)
                ColorPrinter.success(f"Horizontal offset moved by {delta} s")

            elif cmd_name == "vscale" and len(args) >= 3:
                channels = self.parse_channels(args[1], max_ch=4)
                scale = float(args[2])
                position = float(args[3]) if len(args) >= 4 else 0.0
                for channel in channels:
                    dev.set_vertical_scale(channel, scale, position)
                    ColorPrinter.success(f"CH{channel} vertical scale set to {scale} V/div")

            elif cmd_name == "vpos" and len(args) >= 3:
                channels = self.parse_channels(args[1], max_ch=4)
                position = float(args[2])
                for channel in channels:
                    dev.set_vertical_position(channel, position)
                    ColorPrinter.success(f"CH{channel} vertical position set to {position} div")

            elif cmd_name == "vmove" and len(args) >= 3:
                channels = self.parse_channels(args[1], max_ch=4)
                delta = float(args[2])
                for channel in channels:
                    dev.move_vertical(channel, delta)
                    ColorPrinter.success(f"CH{channel}: moved {delta} div")

            elif cmd_name == "trigger" and len(args) >= 3:
                self._handle_trigger(args, dev)

            elif cmd_name == "meas":
                self._handle_meas(args, dev)

            elif cmd_name == "meas_loop":
                self._handle_meas_loop(args, dev)

            elif cmd_name == "meas_setup" and len(args) >= 3:
                channels = self.parse_channels(args[1], max_ch=4)
                measure_type = args[2]
                for channel in channels:
                    dev.configure_measurement(channel, measure_type)
                    ColorPrinter.info(f"CH{channel} {measure_type} slot configured")

            elif cmd_name == "meas_force":
                self._handle_meas_force(dev)

            elif cmd_name == "meas_clear":
                if hasattr(dev, "clear_measurements"):
                    dev.clear_measurements()
                    ColorPrinter.success("Measurement panel cleared")
                else:
                    ColorPrinter.warning("meas_clear not supported on this oscilloscope model")

            elif cmd_name == "meas_delay" and len(args) >= 3:
                self._handle_meas_delay(args, dev)

            elif cmd_name == "meas_delay_store" and len(args) >= 4:
                self._handle_meas_delay_store(args, dev)

            elif cmd_name == "save" and len(args) >= 2:
                self._handle_save(args, dev)

            elif cmd_name == "awg":
                self._handle_scope_awg(dev, args[1:])

            elif cmd_name == "counter":
                self._handle_scope_counter(dev, args[1:])

            elif cmd_name == "dvm":
                self._handle_scope_dvm(dev, args[1:])

            elif cmd_name == "state" and len(args) >= 2:
                self._state_callback(dev_name, args[1])

            elif cmd_name == "screenshot":
                self._handle_screenshot(args, dev)

            elif cmd_name == "label" and len(args) >= 3:
                channels = self.parse_channels(args[1], max_ch=4)
                label_text = " ".join(args[2:])
                for channel in channels:
                    dev.set_channel_label(channel, label_text)
                    ColorPrinter.success(f"CH{channel} label: {label_text}")

            elif cmd_name == "invert" and len(args) >= 3:
                channels = self.parse_channels(args[1], max_ch=4)
                enable = args[2].lower() == "on"
                for channel in channels:
                    dev.invert_channel(channel, enable)
                    ColorPrinter.success(f"CH{channel} invert: {'on' if enable else 'off'}")

            elif cmd_name == "bwlimit" and len(args) >= 3:
                channels = self.parse_channels(args[1], max_ch=4)
                limit = args[2].upper()
                for channel in channels:
                    dev.set_bandwidth_limit(channel, limit)
                    ColorPrinter.success(f"CH{channel} bandwidth limit: {limit}")

            elif cmd_name == "force":
                dev.force_trigger()
                ColorPrinter.success("Force trigger sent")

            elif cmd_name == "display":
                self._handle_scope_display(dev, args[1:])

            elif cmd_name == "acquire":
                self._handle_scope_acquire(dev, args[1:])

            elif cmd_name == "cursor":
                self._handle_scope_cursor(dev, args[1:])

            elif cmd_name == "math":
                self._handle_scope_math(dev, args[1:])

            elif cmd_name == "record":
                self._handle_scope_record(dev, args[1:])

            elif cmd_name == "mask":
                self._handle_scope_mask(dev, args[1:])

            elif cmd_name == "reset":
                dev.reset()
                ColorPrinter.success("Scope reset to factory defaults")

            else:
                ColorPrinter.warning(f"Unknown scope command: scope {arg}. Type 'scope' for help.")

        except Exception as exc:
            ColorPrinter.error(str(exc))

    # ------------------------------------------------------------------
    # Callback wiring
    # ------------------------------------------------------------------

    def set_state_callback(self, callback) -> None:
        """Register the shell's ``do_state`` so we can delegate ``scope state`` commands."""
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
                "# SCOPE",
                "",
                "scope autoset",
                "scope run - start/resume continuous acquisition",
                "scope stop - pause acquisition (freeze current display)",
                "scope single - arm single-shot trigger (capture one event and stop)",
                "",
                "scope chan <1-4|all> on|off",
                "scope coupling <1-4|all> <DC|AC|GND>",
                "  - example: scope coupling 1 AC",
                "  - example: scope coupling all DC",
                "scope probe <1-4|all> <attenuation> - set probe attenuation (1, 10, 100, etc.)",
                "  - example: scope probe 1 10",
                "",
                "scope hscale <seconds_per_div>",
                "  - example: scope hscale 1e-3",
                "scope hpos <seconds> - set horizontal offset (0 = trigger at center)",
                "scope hmove <delta> - move horizontal offset by delta seconds",
                "",
                "scope vscale <1-4|all> <volts_per_div> [pos]",
                "  - example: scope vscale 1 0.5 0",
                "  - example: scope vscale all 1.0",
                "scope vpos <1-4|all> <divisions> - set vertical position",
                "scope vmove <1-4|all> <delta> - move vertical position by delta",
                "",
                "scope trigger <chan> <level> [slope=RISE] [mode=AUTO]",
                "",
                "scope meas <1-4|all> <type> - measure waveform parameter",
                "scope meas_loop <1-4|all> <type> [interval=1.0] [count=0] [label=] [unit=]",
                "  - continuously measure at an interval; Ctrl+C to stop",
                "  - count=0 means run until stopped",
                "  - label= stores each reading to the measurement log",
                "  - example: scope meas_loop 1 FREQUENCY interval=0.5",
                "  - example: scope meas_loop 1 RMS count=10 label=vrms unit=V",
                "  - types: FREQUENCY, PK2PK, RMS, MEAN, PERIOD, MINIMUM, MAXIMUM",
                "  - types: RISE, FALL, AMPLITUDE, HIGH, LOW, PWIDTH, NWIDTH, CRMS",
                "  - example: scope meas 1 FREQUENCY",
                "  - example: scope meas all PK2PK",
                "scope meas_delay <ch1> <ch2> [edge1=RISE] [edge2=RISE] [direction=FORWARDS]",
                "scope meas_delay_store <ch1> <ch2> <label> [edge1=RISE] [edge2=RISE] [direction=FORWARDS] [unit=]",
                "",
                "scope save <channels> <filename> [record=<secs>] [time=<secs>] [points=<n>]",
                "  - channels: single channel (1-4) or comma-separated list (1,3)",
                "  - record=<secs>: WAIT and record for X seconds before saving",
                "  - time=<secs>: filter to last X seconds of buffer (no waiting)",
                "  - points=<n>: limit to specific number of points",
                "  - example: scope save 1 ch1_data.csv",
                "  - example: scope save 1,3 data.csv record=15  (wait 15s then save)",
                "  - example: scope save 2 output.csv time=5 (filter to last 5s)",
                "  - example: scope save 2 output.csv points=1000",
                "",
                "scope awg <subcmd> - built-in AWG control (type 'scope awg' for help)",
                "scope counter <subcmd> - frequency counter (type 'scope counter' for help)",
                "scope dvm <subcmd> - digital voltmeter (type 'scope dvm' for help)",
                "scope state on|off|safe|reset",
                "",
                "# DHO804-specific",
                "scope screenshot [filename] - save screenshot to PNG",
                "scope label <ch> <text> - set channel label",
                "scope invert <ch> on|off - invert channel display",
                "scope bwlimit <ch> <20M|OFF> - set bandwidth limit",
                "scope force - force trigger",
                "",
                "scope display <subcmd> - display settings (type 'scope display' for help)",
                "scope acquire <subcmd> - acquisition settings (type 'scope acquire' for help)",
                "scope cursor <subcmd> - cursor control (type 'scope cursor' for help)",
                "scope math <subcmd> - math channels (type 'scope math' for help)",
                "scope record <subcmd> - waveform recording (type 'scope record' for help)",
                "scope mask <subcmd> - pass/fail mask testing (type 'scope mask' for help)",
            ]
        )

    # ------------------------------------------------------------------
    # Top-level sub-handlers
    # ------------------------------------------------------------------

    def _handle_wait_stop(self, args, dev) -> None:
        timeout = 10.0
        for tok in args[1:]:
            if tok.lower().startswith("timeout="):
                with contextlib.suppress(ValueError):
                    timeout = float(tok.split("=", 1)[1])
        if hasattr(dev, "wait_for_stop"):
            triggered = dev.wait_for_stop(timeout)
            if triggered:
                ColorPrinter.success("Scope stopped - trigger fired, waveform captured")
            else:
                ColorPrinter.warning(
                    f"Scope still armed after {timeout}s \u2014 trigger did not fire. Measurements may return 9.9e+37."
                )
        else:
            ColorPrinter.warning("wait_stop not supported by this device")

    def _handle_trigger(self, args, dev) -> None:
        channel = int(args[1])
        level = float(args[2])
        kwargs = {k.lower(): v for k, v in (a.split("=", 1) for a in args[3:] if "=" in a)}
        positional = [a for a in args[3:] if "=" not in a]
        slope_str = kwargs.get("slope", positional[0] if positional else "RISE").upper()
        mode_str = kwargs.get("mode", positional[1] if len(positional) > 1 else "AUTO").upper()
        try:
            slope = TriggerEdge(slope_str)
        except ValueError:
            slope = slope_str
        sweep_map = {
            "NORM": "NORMal",
            "NORMAL": "NORMal",
            "AUTO": "AUTO",
            "SINGLE": "SINGle",
            "SING": "SINGle",
        }
        sweep = sweep_map.get(mode_str, mode_str)
        dev.configure_trigger(channel, level, slope)
        if hasattr(dev, "set_trigger_sweep"):
            dev.set_trigger_sweep(sweep)
        ColorPrinter.success(f"Trigger configured: CH{channel} @ {level}V, SLOPE={slope}, MODE={sweep}")

    def _handle_meas_loop(self, args, dev) -> None:
        """scope meas_loop <ch> <type> [interval=<s>] [count=<n>] [label=<name>] [unit=<u>]"""
        if len(args) < 3:
            ColorPrinter.warning("Usage: scope meas_loop <1-4> <type> [interval=1.0] [count=0] [label=] [unit=]")
            return
        channels = self.parse_channels(args[1], max_ch=4)
        measure_type = args[2].upper()
        interval = 1.0
        count = 0
        label = ""
        unit = ""
        for token in args[3:]:
            k, _, v = token.partition("=")
            k = k.lower()
            if k == "interval":
                try:
                    interval = float(v)
                except ValueError:
                    ColorPrinter.warning(f"Invalid interval value: {v!r}. Using default {interval}s.")
            elif k == "count":
                try:
                    count = int(v)
                except ValueError:
                    ColorPrinter.warning(f"Invalid count value: {v!r}. Using default (unlimited).")
            elif k == "label":
                label = v
            elif k == "unit":
                unit = v
        ColorPrinter.info(
            f"Continuous {measure_type} on CH{','.join(str(c) for c in channels)} "
            f"every {interval}s{f', {count} samples' if count else ''} — press Ctrl+C to stop"
        )
        self.ctx.interrupt_requested = False
        iteration = 0
        try:
            while True:
                if self.ctx.interrupt_requested:
                    print()
                    break
                for channel in channels:
                    val = dev.measure_bnf(channel, measure_type)
                    ts = time.strftime("%H:%M:%S")
                    ColorPrinter.cyan(f"[{ts}] CH{channel} {measure_type}: {val}")
                    if label:
                        stored_label = f"{label}_ch{channel}" if len(channels) > 1 else label
                        self.measurements.record(stored_label, val, unit or "", f"scope.meas.{measure_type}")
                iteration += 1
                if count and iteration >= count:
                    break
                end_time = time.time() + interval
                while time.time() < end_time:
                    if self.ctx.interrupt_requested:
                        print()
                        return
                    time.sleep(0.05)
        except KeyboardInterrupt:
            print()

    def _handle_meas(self, args, dev) -> None:
        if len(args) < 3:
            # Show available measurement types
            ColorPrinter.warning("Missing arguments. Usage: scope meas <1-4> <type>")
            self.print_colored_usage(
                [
                    "",
                    "# AVAILABLE MEASUREMENT TYPES",
                    "",
                    "  - FREQUENCY   - signal frequency (Hz)",
                    "  - PK2PK       - peak-to-peak voltage",
                    "  - RMS         - RMS voltage",
                    "  - CRMS        - cyclic RMS voltage",
                    "  - MEAN        - average voltage",
                    "  - PERIOD      - signal period",
                    "  - AMPLITUDE   - signal amplitude",
                    "  - MINIMUM     - minimum voltage",
                    "  - MAXIMUM     - maximum voltage",
                    "  - HIGH        - high state level",
                    "  - LOW         - low state level",
                    "  - RISE        - rise time",
                    "  - FALL        - fall time",
                    "  - PWIDTH      - positive pulse width",
                    "  - NWIDTH      - negative pulse width",
                    "",
                    "  - example: scope meas 1 FREQUENCY",
                    "  - example: scope meas 2 PK2PK",
                ]
            )
        else:
            channels = self.parse_channels(args[1], max_ch=4)
            measure_type = args[2]
            for channel in channels:
                result = dev.measure_bnf(channel, measure_type)
                ColorPrinter.cyan(f"CH{channel} {measure_type}: {result}")

    def _handle_meas_force(self, dev) -> None:
        try:
            dev.get_screenshot()
            ColorPrinter.info("Measurement DSP forced (display refresh complete)")
        except AttributeError:
            ColorPrinter.warning("meas_force not supported on this oscilloscope model")

    def _handle_meas_delay(self, args, dev) -> None:
        ch1 = int(args[1])
        ch2 = int(args[2])
        edge1 = args[3].upper() if len(args) >= 4 else "RISE"
        edge2 = args[4].upper() if len(args) >= 5 else "RISE"
        direction = args[5].upper() if len(args) >= 6 else "FORWARDS"
        ColorPrinter.cyan(str(dev.measure_delay(ch1, ch2, edge1, edge2, direction)))

    def _handle_meas_delay_store(self, args, dev) -> None:
        ch1 = int(args[1])
        ch2 = int(args[2])
        label = args[3]
        edge1 = "RISE"
        edge2 = "RISE"
        direction = "FORWARDS"
        unit = "s"
        # Parse optional args
        optional_args = [a for a in args[4:] if not a.lower().startswith("unit=")]
        unit_args = [a for a in args[4:] if a.lower().startswith("unit=")]
        if unit_args:
            unit = unit_args[0].split("=", 1)[1]

        if len(optional_args) >= 1:
            edge1 = optional_args[0].upper()
        if len(optional_args) >= 2:
            edge2 = optional_args[1].upper()
        if len(optional_args) >= 3:
            direction = optional_args[2].upper()

        val = dev.measure_delay(ch1, ch2, edge1, edge2, direction)
        self.measurements.record(label, val, unit, "scope.meas.delay")
        ColorPrinter.cyan(str(val))

    def _handle_save(self, args, dev) -> None:
        channels_str = args[1]
        filename = args[2] if len(args) >= 3 else f"scope_ch{channels_str}_{time.strftime('%H%M%S')}.csv"
        # Resolve relative paths to data dir
        if not os.path.isabs(filename):
            data_dir = self.ctx.get_data_dir()
            filename = os.path.join(data_dir, filename)
            os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)

        # Parse optional parameters (time=X, points=N, record=X)
        max_points = None
        time_window = None
        record_duration = None
        for token in args[3:]:
            if token.lower().startswith("time="):
                time_window = float(token.split("=", 1)[1])
            elif token.lower().startswith("points="):
                max_points = int(token.split("=", 1)[1])
            elif token.lower().startswith("record="):
                record_duration = float(token.split("=", 1)[1])

        # If record= is specified, run scope and wait before saving
        if record_duration:
            ColorPrinter.info(f"Recording for {record_duration} seconds...")
            dev.run()  # Ensure scope is running
            time.sleep(record_duration)  # Wait for the specified duration
            ColorPrinter.success("Recording complete")

        # Parse channel list (supports single channel or comma-separated)
        if "," in channels_str:
            # Multiple channels
            channels = [int(ch.strip()) for ch in channels_str.split(",")]
            dev.save_waveforms_csv(channels, filename, max_points=max_points, time_window=time_window)
            channels_list = ",".join(str(ch) for ch in sorted(channels))
            ColorPrinter.success(f"Waveforms from CH{channels_list} saved to {filename}")
        else:
            # Single channel
            channel = int(channels_str)
            dev.save_waveform_csv(channel, filename, max_points=max_points, time_window=time_window)
            ColorPrinter.success(f"Waveform from CH{channel} saved to {filename}")

    def _handle_screenshot(self, args, dev) -> None:
        filename = args[1] if len(args) >= 2 else None
        try:
            data = dev.get_screenshot()
        except AttributeError:
            ColorPrinter.warning("Screenshot not supported on this oscilloscope model")
            return
        if filename is None:
            filename = f"screenshot_{time.strftime('%H%M%S')}.png"
        # Resolve path: absolute paths bypass data dir, relative paths use data dir
        if not os.path.isabs(filename):
            data_dir = self.ctx.get_data_dir()
            filepath = os.path.join(data_dir, filename)
        else:
            filepath = filename
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        with open(filepath, "wb") as f:
            f.write(data)
        ColorPrinter.success(f"Screenshot saved to {filepath}")
        self.ctx.report_screenshots.append(os.path.abspath(filepath))

    # ------------------------------------------------------------------
    # Scope AWG sub-handler
    # ------------------------------------------------------------------

    def _handle_scope_awg(self, dev, args) -> None:
        """Handle built-in oscilloscope AWG commands (DHO914S/DHO924S)."""
        if not args:
            self.print_colored_usage(
                [
                    "# SCOPE AWG",
                    "",
                    "scope awg chan on|off - enable/disable AWG output",
                    "scope awg set <func> <freq> <amp> [offset=0] - quick config",
                    "  - func: SINusoid|SQUare|RAMP|DC|NOISe",
                    "  - freq: frequency in Hz",
                    "  - amp: amplitude in Vpp",
                    "  - example: scope awg set SINusoid 1000 2.0",
                    "",
                    "scope awg func <type> - set waveform function",
                    "scope awg freq <Hz> - set frequency",
                    "scope awg amp <Vpp> - set amplitude",
                    "scope awg offset <V> - set DC offset",
                    "scope awg phase <deg> - set phase (0-360)",
                    "scope awg duty <percent> - set square duty cycle",
                    "scope awg sym <percent> - set ramp symmetry",
                    "",
                    "scope awg mod on|off - enable/disable modulation",
                    "scope awg mod_type AM|FM|PM - set modulation type",
                ]
            )
            return

        try:
            cmd = args[0].lower()

            if cmd == "chan" and len(args) >= 2:
                dev.awg_set_output_enable(args[1].lower() == "on")
                ColorPrinter.success(f"AWG output {'enabled' if args[1].lower() == 'on' else 'disabled'}")

            elif cmd == "set" and len(args) >= 4:
                # Quick configuration: scope awg set SINusoid 1000 2.0 [offset=0]
                function = args[1]
                frequency = float(args[2])
                amplitude = float(args[3])
                offset = 0.0
                for token in args[4:]:
                    if token.lower().startswith("offset="):
                        offset = float(token.split("=", 1)[1])
                dev.awg_configure_simple(function, frequency, amplitude, offset, enable=True)
                ColorPrinter.success(f"AWG configured: {function} {frequency}Hz {amplitude}Vpp offset={offset}V")

            elif cmd == "func" and len(args) >= 2:
                dev.awg_set_function(args[1])
                ColorPrinter.success(f"AWG function: {args[1]}")

            elif cmd == "freq" and len(args) >= 2:
                freq = float(args[1])
                dev.awg_set_frequency(freq)
                ColorPrinter.success(f"AWG frequency: {freq} Hz")

            elif cmd == "amp" and len(args) >= 2:
                amp = float(args[1])
                dev.awg_set_amplitude(amp)
                ColorPrinter.success(f"AWG amplitude: {amp} Vpp")

            elif cmd == "offset" and len(args) >= 2:
                offset = float(args[1])
                dev.awg_set_offset(offset)
                ColorPrinter.success(f"AWG offset: {offset} V")

            elif cmd == "phase" and len(args) >= 2:
                phase = float(args[1])
                dev.awg_set_phase(phase)
                ColorPrinter.success(f"AWG phase: {phase}\u00b0")

            elif cmd == "duty" and len(args) >= 2:
                duty = float(args[1])
                dev.awg_set_square_duty(duty)
                ColorPrinter.success(f"AWG square duty: {duty}%")

            elif cmd == "sym" and len(args) >= 2:
                sym = float(args[1])
                dev.awg_set_ramp_symmetry(sym)
                ColorPrinter.success(f"AWG ramp symmetry: {sym}%")

            elif cmd == "mod" and len(args) >= 2:
                dev.awg_set_modulation_enable(args[1].lower() == "on")
                ColorPrinter.success(f"AWG modulation {'enabled' if args[1].lower() == 'on' else 'disabled'}")

            elif cmd == "mod_type" and len(args) >= 2:
                mod_type = args[1].upper()
                dev.awg_set_modulation_type(mod_type)
                ColorPrinter.success(f"AWG modulation type: {mod_type}")

            else:
                ColorPrinter.warning(f"Unknown AWG command: scope awg {' '.join(args)}. Type 'scope awg' for help.")

        except AttributeError:
            ColorPrinter.warning("AWG not supported on this oscilloscope model (requires DHO914S/DHO924S)")
        except Exception as exc:
            ColorPrinter.error(str(exc))

    # ------------------------------------------------------------------
    # Scope counter sub-handler
    # ------------------------------------------------------------------

    def _handle_scope_counter(self, dev, args) -> None:
        """Handle oscilloscope frequency counter commands."""
        if not args:
            self.print_colored_usage(
                [
                    "# SCOPE COUNTER",
                    "",
                    "scope counter on|off - enable/disable counter",
                    "scope counter read - read current frequency",
                    "scope counter source <1-4> - set source channel",
                    "scope counter mode <freq|period|totalize> - set mode",
                ]
            )
            return

        try:
            cmd = args[0].lower()

            if cmd in ("on", "off"):
                dev.set_counter_enable(cmd == "on")
                ColorPrinter.success(f"Counter {'enabled' if cmd == 'on' else 'disabled'}")

            elif cmd == "read":
                value = dev.get_counter_current()
                ColorPrinter.cyan(f"Counter: {value}")

            elif cmd == "source" and len(args) >= 2:
                channel = int(args[1])
                dev.set_counter_source(channel)
                ColorPrinter.success(f"Counter source: CH{channel}")

            elif cmd == "mode" and len(args) >= 2:
                mode = args[1].upper()
                dev.set_counter_mode(mode)
                ColorPrinter.success(f"Counter mode: {mode}")

            else:
                ColorPrinter.warning(
                    f"Unknown counter command: scope counter {' '.join(args)}. Type 'scope counter' for help."
                )

        except AttributeError:
            ColorPrinter.warning("Counter not supported on this oscilloscope")
        except Exception as exc:
            ColorPrinter.error(str(exc))

    # ------------------------------------------------------------------
    # Scope DVM sub-handler
    # ------------------------------------------------------------------

    def _handle_scope_dvm(self, dev, args) -> None:
        """Handle oscilloscope digital voltmeter commands."""
        if not args:
            self.print_colored_usage(
                [
                    "# SCOPE DVM",
                    "",
                    "scope dvm on|off - enable/disable DVM",
                    "scope dvm read - read current voltage",
                    "scope dvm source <1-4> - set source channel",
                ]
            )
            return

        try:
            cmd = args[0].lower()

            if cmd in ("on", "off"):
                dev.set_dvm_enable(cmd == "on")
                ColorPrinter.success(f"DVM {'enabled' if cmd == 'on' else 'disabled'}")

            elif cmd == "read":
                value = dev.get_dvm_current()
                ColorPrinter.cyan(f"DVM: {value} V")

            elif cmd == "source" and len(args) >= 2:
                channel = int(args[1])
                dev.set_dvm_source(channel)
                ColorPrinter.success(f"DVM source: CH{channel}")

            else:
                ColorPrinter.warning(f"Unknown DVM command: scope dvm {' '.join(args)}. Type 'scope dvm' for help.")

        except AttributeError:
            ColorPrinter.warning("DVM not supported on this oscilloscope")
        except Exception as exc:
            ColorPrinter.error(str(exc))

    # ------------------------------------------------------------------
    # Scope display sub-handler
    # ------------------------------------------------------------------

    def _handle_scope_display(self, dev, args) -> None:
        """Handle oscilloscope display commands (DHO804)."""
        if not args:
            self.print_colored_usage(
                [
                    "# SCOPE DISPLAY",
                    "",
                    "scope display clear - clear waveform display",
                    "scope display brightness <0-100> - set waveform brightness",
                    "scope display grid <FULL|HALF|NONE> - set grid style",
                    "scope display gridbright <0-100> - set grid brightness",
                    "scope display persist <MIN|1|5|10|INF|OFF> - set persistence time",
                    "scope display type <VECTORS|DOTS> - set display type",
                ]
            )
            return

        try:
            cmd = args[0].lower()

            if cmd == "clear":
                dev.clear_display()
                ColorPrinter.success("Display cleared")

            elif cmd == "brightness" and len(args) >= 2:
                brightness = int(args[1])
                dev.set_waveform_brightness(brightness)
                ColorPrinter.success(f"Waveform brightness: {brightness}%")

            elif cmd == "grid" and len(args) >= 2:
                grid = args[1].upper()
                dev.set_grid_type(grid)
                ColorPrinter.success(f"Grid type: {grid}")

            elif cmd == "gridbright" and len(args) >= 2:
                brightness = int(args[1])
                dev.set_grid_brightness(brightness)
                ColorPrinter.success(f"Grid brightness: {brightness}%")

            elif cmd == "persist" and len(args) >= 2:
                persist_time = args[1].upper()
                dev.set_persistence(persist_time)
                ColorPrinter.success(f"Persistence: {persist_time}")

            elif cmd == "type" and len(args) >= 2:
                display_type = args[1].upper()
                dev.set_display_type(display_type)
                ColorPrinter.success(f"Display type: {display_type}")

            else:
                ColorPrinter.warning(
                    f"Unknown display command: scope display {' '.join(args)}. Type 'scope display' for help."
                )

        except AttributeError:
            ColorPrinter.warning("Display control not supported on this oscilloscope model")
        except Exception as exc:
            ColorPrinter.error(str(exc))

    # ------------------------------------------------------------------
    # Scope acquire sub-handler
    # ------------------------------------------------------------------

    def _handle_scope_acquire(self, dev, args) -> None:
        """Handle oscilloscope acquisition setup commands."""
        if not args:
            self.print_colored_usage(
                [
                    "# SCOPE ACQUIRE",
                    "",
                    "scope acquire type <NORMAL|AVERAGE|PEAK|HRES> - set acquisition type",
                    "scope acquire averages <count> - set number of averages",
                    "scope acquire depth <AUTO|1K|10K|100K|1M|...> - set memory depth",
                    "scope acquire rate - show current sample rate",
                ]
            )
            return

        try:
            cmd = args[0].lower()

            if cmd == "type" and len(args) >= 2:
                acq_type = args[1].upper()
                dev.set_acquisition_type(acq_type)
                ColorPrinter.success(f"Acquisition type: {acq_type}")

            elif cmd == "averages" and len(args) >= 2:
                count = int(args[1])
                dev.set_average_count(count)
                ColorPrinter.success(f"Average count: {count}")

            elif cmd == "depth" and len(args) >= 2:
                depth = args[1].upper()
                dev.set_memory_depth(depth)
                ColorPrinter.success(f"Memory depth: {depth}")

            elif cmd == "rate":
                rate = dev.get_sample_rate()
                ColorPrinter.cyan(f"Sample rate: {rate} Sa/s")

            else:
                ColorPrinter.warning(
                    f"Unknown acquire command: scope acquire {' '.join(args)}. Type 'scope acquire' for help."
                )

        except AttributeError:
            ColorPrinter.warning("Acquisition setup not supported on this oscilloscope model")
        except Exception as exc:
            ColorPrinter.error(str(exc))

    # ------------------------------------------------------------------
    # Scope cursor sub-handler
    # ------------------------------------------------------------------

    def _handle_scope_cursor(self, dev, args) -> None:
        """Handle oscilloscope cursor commands."""
        if not args:
            self.print_colored_usage(
                [
                    "# SCOPE CURSOR",
                    "",
                    "scope cursor off - disable cursors",
                    "scope cursor manual <type> [source] - enable manual cursors",
                    "  - type: X|Y|XY",
                    "  - source: CH1|CH2|CH3|CH4 (default: CH1)",
                    "scope cursor set <ax> [ay] [bx] [by] - set cursor positions",
                    "scope cursor read - read cursor values",
                ]
            )
            return

        try:
            cmd = args[0].lower()

            if cmd == "off":
                dev.set_cursor_mode("OFF")
                ColorPrinter.success("Cursors disabled")

            elif cmd == "manual" and len(args) >= 2:
                cursor_type = args[1].upper()
                source = args[2].upper() if len(args) >= 3 else "CH1"
                dev.set_cursor_mode("MANUAL")
                dev.set_manual_cursor_type(cursor_type)
                dev.set_manual_cursor_source(source)
                ColorPrinter.success(f"Manual cursor: {cursor_type} on {source}")

            elif cmd == "set" and len(args) >= 2:
                kwargs = {}
                if len(args) >= 2:
                    kwargs["ax"] = float(args[1])
                if len(args) >= 3:
                    kwargs["ay"] = float(args[2])
                if len(args) >= 4:
                    kwargs["bx"] = float(args[3])
                if len(args) >= 5:
                    kwargs["by"] = float(args[4])
                dev.set_manual_cursor_positions(**kwargs)
                ColorPrinter.success("Cursor positions set")

            elif cmd == "read":
                values = dev.get_manual_cursor_values()
                for key, val in values.items():
                    ColorPrinter.cyan(f"  {key}: {val}")

            else:
                ColorPrinter.warning(
                    f"Unknown cursor command: scope cursor {' '.join(args)}. Type 'scope cursor' for help."
                )

        except AttributeError:
            ColorPrinter.warning("Cursor control not supported on this oscilloscope model")
        except Exception as exc:
            ColorPrinter.error(str(exc))

    # ------------------------------------------------------------------
    # Scope math sub-handler
    # ------------------------------------------------------------------

    def _handle_scope_math(self, dev, args) -> None:
        """Handle oscilloscope math channel commands."""
        if not args:
            self.print_colored_usage(
                [
                    "# SCOPE MATH",
                    "",
                    "scope math on|off [ch] - enable/disable math channel (ch: 1-4, default 1)",
                    "scope math op <ch> <ADD|SUB|MUL|DIV|AND|OR|XOR> <src1> [src2]",
                    "scope math func <ch> <ABS|SQRT|LG|LN|EXP|DIFF|INTG> <src>",
                    "scope math fft <ch> <src> [window=RECT]",
                    "scope math filter <ch> <LPAS|HPAS|BPAS|BSTOP> <src> [upper=] [lower=]",
                    "scope math scale <ch> <scale> [offset]",
                ]
            )
            return

        try:
            cmd = args[0].lower()

            if cmd in ("on", "off"):
                math_ch = int(args[1]) if len(args) >= 2 else 1
                dev.enable_math_channel(math_ch, cmd == "on")
                ColorPrinter.success(f"Math{math_ch}: {'enabled' if cmd == 'on' else 'disabled'}")

            elif cmd == "op" and len(args) >= 4:
                math_ch = int(args[1])
                operation = args[2].upper()
                source1 = args[3].upper()
                source2 = args[4].upper() if len(args) >= 5 else None
                dev.configure_math_operation(math_ch, operation, source1, source2)
                ColorPrinter.success(f"Math{math_ch}: {source1} {operation} {source2 or ''}")

            elif cmd == "func" and len(args) >= 4:
                math_ch = int(args[1])
                function = args[2].upper()
                source = args[3].upper()
                dev.configure_math_function(math_ch, function, source)
                ColorPrinter.success(f"Math{math_ch}: {function}({source})")

            elif cmd == "fft" and len(args) >= 3:
                math_ch = int(args[1])
                source = args[2].upper()
                window = "RECT"
                for token in args[3:]:
                    if token.lower().startswith("window="):
                        window = token.split("=", 1)[1].upper()
                dev.configure_fft(math_ch, source, window)
                ColorPrinter.success(f"Math{math_ch}: FFT of {source}, window={window}")

            elif cmd == "filter" and len(args) >= 4:
                math_ch = int(args[1])
                filter_type = args[2].upper()
                source = args[3].upper()
                kwargs = {}
                for token in args[4:]:
                    if token.lower().startswith("upper="):
                        kwargs["upper"] = float(token.split("=", 1)[1])
                    elif token.lower().startswith("lower="):
                        kwargs["lower"] = float(token.split("=", 1)[1])
                dev.configure_digital_filter(math_ch, filter_type, source, **kwargs)
                ColorPrinter.success(f"Math{math_ch}: {filter_type} filter on {source}")

            elif cmd == "scale" and len(args) >= 3:
                math_ch = int(args[1])
                scale = float(args[2])
                offset = float(args[3]) if len(args) >= 4 else None
                dev.set_math_scale(math_ch, scale, offset)
                ColorPrinter.success(f"Math{math_ch} scale: {scale}")

            else:
                ColorPrinter.warning(f"Unknown math command: scope math {' '.join(args)}. Type 'scope math' for help.")

        except AttributeError:
            ColorPrinter.warning("Math channels not supported on this oscilloscope model")
        except Exception as exc:
            ColorPrinter.error(str(exc))

    # ------------------------------------------------------------------
    # Scope record sub-handler
    # ------------------------------------------------------------------

    def _handle_scope_record(self, dev, args) -> None:
        """Handle oscilloscope waveform recording commands."""
        if not args:
            self.print_colored_usage(
                [
                    "# SCOPE RECORD",
                    "",
                    "scope record on|off - enable/disable recording",
                    "scope record frames <count> - set number of frames to record",
                    "scope record start - start recording",
                    "scope record stop - stop recording",
                    "scope record status - show recording status",
                    "scope record play - start playback of recorded frames",
                ]
            )
            return

        try:
            cmd = args[0].lower()

            if cmd in ("on", "off"):
                dev.set_recording_enable(cmd == "on")
                ColorPrinter.success(f"Recording {'enabled' if cmd == 'on' else 'disabled'}")

            elif cmd == "frames" and len(args) >= 2:
                frames = int(args[1])
                dev.set_recording_frames(frames)
                ColorPrinter.success(f"Recording frames: {frames}")

            elif cmd == "start":
                dev.start_recording()
                ColorPrinter.success("Recording started")

            elif cmd == "stop":
                dev.stop_recording()
                ColorPrinter.success("Recording stopped")

            elif cmd == "status":
                status = dev.get_recording_status()
                ColorPrinter.cyan(f"Recording status: {status}")

            elif cmd == "play":
                dev.start_playback()
                ColorPrinter.success("Playback started")

            else:
                ColorPrinter.warning(
                    f"Unknown record command: scope record {' '.join(args)}. Type 'scope record' for help."
                )

        except AttributeError:
            ColorPrinter.warning("Recording not supported on this oscilloscope model")
        except Exception as exc:
            ColorPrinter.error(str(exc))

    # ------------------------------------------------------------------
    # Scope mask sub-handler
    # ------------------------------------------------------------------

    def _handle_scope_mask(self, dev, args) -> None:
        """Handle oscilloscope pass/fail mask test commands."""
        if not args:
            self.print_colored_usage(
                [
                    "# SCOPE MASK",
                    "",
                    "scope mask on|off - enable/disable mask testing",
                    "scope mask source <1-4> - set mask source channel",
                    "scope mask tolerance <x> <y> - set mask tolerance",
                    "scope mask create - auto-create mask from current waveform",
                    "scope mask start - start mask test",
                    "scope mask stop - stop mask test",
                    "scope mask stats - show pass/fail statistics",
                    "scope mask reset - reset mask statistics",
                ]
            )
            return

        try:
            cmd = args[0].lower()

            if cmd in ("on", "off"):
                dev.set_mask_enable(cmd == "on")
                ColorPrinter.success(f"Mask testing {'enabled' if cmd == 'on' else 'disabled'}")

            elif cmd == "source" and len(args) >= 2:
                channel = int(args[1])
                dev.set_mask_source(channel)
                ColorPrinter.success(f"Mask source: CH{channel}")

            elif cmd == "tolerance" and len(args) >= 3:
                x_tol = float(args[1])
                y_tol = float(args[2])
                dev.set_mask_tolerance_x(x_tol)
                dev.set_mask_tolerance_y(y_tol)
                ColorPrinter.success(f"Mask tolerance: X={x_tol}, Y={y_tol}")

            elif cmd == "create":
                dev.create_mask()
                ColorPrinter.success("Mask created from current waveform")

            elif cmd == "start":
                dev.start_mask_test()
                ColorPrinter.success("Mask test started")

            elif cmd == "stop":
                dev.stop_mask_test()
                ColorPrinter.success("Mask test stopped")

            elif cmd == "stats":
                stats = dev.get_mask_statistics()
                ColorPrinter.cyan(f"  Passed: {stats.get('passed', 0)}")
                ColorPrinter.cyan(f"  Failed: {stats.get('failed', 0)}")
                ColorPrinter.cyan(f"  Total:  {stats.get('total', 0)}")

            elif cmd == "reset":
                dev.reset_mask_statistics()
                ColorPrinter.success("Mask statistics reset")

            else:
                ColorPrinter.warning(f"Unknown mask command: scope mask {' '.join(args)}. Type 'scope mask' for help.")

        except AttributeError:
            ColorPrinter.warning("Mask testing not supported on this oscilloscope model")
        except Exception as exc:
            ColorPrinter.error(str(exc))
