"""
Driver for Keysight DSOX1204G Digital Oscilloscope
Instrument Type: 4-channel 70 MHz oscilloscope with built-in waveform generator (WaveGen)

Protocol: SCPI over USB-TMC/VISA
Based on InfiniiVision 1000 X-Series Programmer's Guide
"""

import time

import numpy as np

from .device_manager import DeviceManager
from .rigol_dho804 import WaveformData


class Keysight_DSOX1204G(DeviceManager):
    """
    Driver for Keysight InfiniiVision 1000 X-Series oscilloscope.

    Model: DSOX1204G (4-channel, 70 MHz, with WaveGen)
    """

    num_channels = 4

    # ---- ALLOWLIST constants (SCPI Driver Contract) ----
    _COUPLING_ALLOWLIST = ("DC", "AC")
    _ACQ_TYPE_ALLOWLIST = ("NORMAL", "AVERAGE", "HRESOLUTION", "PEAK")
    _TRIGGER_SWEEP_ALLOWLIST = ("AUTO", "NORMAL")
    _AWG_FUNC_ALLOWLIST = ("SINusoid", "SQUare", "RAMP", "PULSe", "DC", "NOISe")
    _BW_LIMIT_MAP = {"20M": "ON", "ON": "ON", "OFF": "OFF"}

    # Measurement type mapping for Keysight InfiniiVision 1000X
    _MEAS_MAP = {
        "vpp": "VPP",
        "pk2pk": "VPP",
        "vrms": "VRMS",
        "rms": "VRMS",
        "vmax": "VMAX",
        "maximum": "VMAX",
        "vmin": "VMIN",
        "minimum": "VMIN",
        "vtop": "VTOp",
        "top": "VTOp",
        "vbase": "VBASe",
        "base": "VBASe",
        "vamp": "VAMPlitude",
        "amplitude": "VAMPlitude",
        "mean": "VAVerage",
        "average": "VAVerage",
        "vavg": "VAVerage",
        "frequency": "FREQuency",
        "freq": "FREQuency",
        "period": "PERiod",
        "rise": "RISetime",
        "risetime": "RISetime",
        "fall": "FALLtime",
        "falltime": "FALLtime",
        "pwidth": "PWIDth",
        "nwidth": "NWIDth",
        "pduty": "DUTYcycle",
        "posduty": "DUTYcycle",
        "duty": "DUTYcycle",
        "overshoot": "OVERshoot",
        "over": "OVERshoot",
        "preshoot": "PREShoot",
        "pre": "PREShoot",
    }

    def __init__(self, resource_name):
        """Initialize the Keysight DSOX1204G oscilloscope."""
        super().__init__(resource_name)
        self._cache = {}

    def __enter__(self):
        """Context manager entry: clear status, disable channels and AWG."""
        self.clear_status()
        self.disable_all_channels()
        self.awg_set_output_enable(False)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Context manager exit: ensure safe state (fires even after exceptions)."""
        self.disable_all_channels()
        self.awg_set_output_enable(False)

    # ========================================
    # Connection
    # ========================================

    def connect(self):
        """Connect to the Keysight DSOX1204G oscilloscope."""
        super().connect()
        self.instrument.timeout = 10000

    def disconnect(self):
        """Disconnect from the oscilloscope."""
        super().disconnect()

    # ========================================
    # Validation Helpers
    # ========================================

    def _validate_channel(self, channel: int) -> None:
        """Validate channel number is 1-4."""
        if channel not in (1, 2, 3, 4):
            raise ValueError(f"Channel must be 1-4, got {channel}")

    def _resolve_meas_type(self, measurement_type: str) -> str:
        """Map a user-facing measurement name to its Keysight SCPI measurement string."""
        return self._MEAS_MAP.get(measurement_type.lower(), measurement_type)

    def _write(self, cmd: str, **cache_updates) -> None:
        """Write a SCPI command and atomically update the cache."""
        self.instrument.write(cmd)
        if cache_updates:
            self._cache.update(cache_updates)

    # ========================================
    # Basic Control
    # ========================================

    def run(self) -> None:
        """Start running the oscilloscope (continuous acquisition)."""
        self._write(":RUN", state="running")
        print("Oscilloscope running")

    def stop(self) -> None:
        """Stop the oscilloscope acquisition."""
        self._write(":STOP", state="stopped")
        print("Oscilloscope stopped")

    def single(self) -> None:
        """Set oscilloscope to single trigger mode and arm for one acquisition."""
        self._write(":SINGle", state="single")
        print("Single trigger armed")

    def autoset(self) -> None:
        """Perform an autoscale on the oscilloscope (Keysight uses AUToscale)."""
        self._write(":AUToscale")
        print("Autoscale executed - optimizing display settings...")

    def force_trigger(self) -> None:
        """Generate a trigger signal forcefully (Keysight uses TRIGger:FORCe)."""
        self._write(":TRIGger:FORCe")
        print("Trigger forced")

    def digitize(self, channel: int = None) -> None:
        """
        Blocking acquisition -- stops when acquisition completes.

        Args:
            channel: Channel number (1-4) or None for all displayed channels
        """
        if channel is not None:
            self._validate_channel(channel)

        saved_timeout = self.instrument.timeout
        self.instrument.timeout = 60000  # 60s for slow triggers
        try:
            if channel is not None:
                self._write(f":DIGitize CHANnel{channel}")
                print(f"Digitize CH{channel} complete")
            else:
                self._write(":DIGitize")
                print("Digitize complete")
        finally:
            self.instrument.timeout = saved_timeout

    # ========================================
    # Channel Control
    # ========================================

    def enable_channel(self, channel: int) -> None:
        """Enable a channel."""
        self._validate_channel(channel)
        self._write(f":CHANnel{channel}:DISPlay ON", **{f"ch{channel}_display": True})
        print(f"CH{channel} enabled")

    def disable_channel(self, channel: int) -> None:
        """Disable a channel."""
        self._validate_channel(channel)
        self._write(f":CHANnel{channel}:DISPlay OFF", **{f"ch{channel}_display": False})
        print(f"CH{channel} disabled")

    def enable_all_channels(self) -> None:
        """Enable all analog channels."""
        for ch in range(1, self.num_channels + 1):
            self.enable_channel(ch)

    def disable_all_channels(self) -> None:
        """Disable all analog channels."""
        for ch in range(1, self.num_channels + 1):
            self.disable_channel(ch)

    def set_vertical_scale(self, channel: int, volts_per_div: float, offset: float = 0.0) -> None:
        """
        Set vertical scale and offset for a channel.

        Args:
            channel: Channel number (1-4)
            volts_per_div: Vertical scale in volts per division
            offset: Vertical offset in volts
        """
        self._validate_channel(channel)
        self._write(f":CHANnel{channel}:SCALe {volts_per_div}", **{f"ch{channel}_scale": volts_per_div})
        self._write(f":CHANnel{channel}:OFFSet {offset}", **{f"ch{channel}_offset": offset})
        print(f"CH{channel}: {volts_per_div} V/div, offset {offset} V")

    def set_vertical_position(self, channel: int, position: float) -> None:
        """
        Set vertical position (offset) of the channel.

        Args:
            channel: Channel number (1-4)
            position: Vertical offset in volts
        """
        self._validate_channel(channel)
        self._write(f":CHANnel{channel}:OFFSet {position}", **{f"ch{channel}_offset": position})
        print(f"CH{channel} vertical offset: {position} V")

    def get_vertical_position(self, channel: int) -> float:
        """
        Get vertical position (offset) of the channel.

        Args:
            channel: Channel number (1-4)

        Returns:
            float: Current vertical offset in volts
        """
        self._validate_channel(channel)
        response = self.instrument.query(f":CHANnel{channel}:OFFSet?")
        return float(response.strip())

    def move_vertical(self, channel: int, delta: float) -> None:
        """
        Move a channel vertically by a delta amount.

        Args:
            channel: Channel number (1-4)
            delta: Amount to move in volts (positive = up, negative = down)
        """
        current_pos = self.get_vertical_position(channel)
        new_pos = current_pos + delta
        self.set_vertical_position(channel, new_pos)

    def set_coupling(self, channel: int, coupling: str) -> None:
        """
        Set channel coupling.

        Args:
            channel: Channel number (1-4)
            coupling: 'DC' or 'AC' (Keysight 1000X does NOT support GND)
        """
        self._validate_channel(channel)
        coupling = coupling.upper()
        if coupling == "GND":
            raise ValueError("Keysight DSOX1204G does not support GND coupling. Use DC or AC.")
        if coupling not in self._COUPLING_ALLOWLIST:
            raise ValueError(f"Coupling must be one of {self._COUPLING_ALLOWLIST}, got '{coupling}'")

        self._write(f":CHANnel{channel}:COUPling {coupling}", **{f"ch{channel}_coupling": coupling})
        print(f"CH{channel} coupling: {coupling}")

    def set_probe_attenuation(self, channel: int, ratio: float) -> None:
        """
        Set probe attenuation ratio.

        Args:
            channel: Channel number (1-4)
            ratio: Probe attenuation ratio (e.g., 1, 10, 100)
        """
        self._validate_channel(channel)
        self._write(f":CHANnel{channel}:PROBe {ratio}", **{f"ch{channel}_probe": ratio})
        print(f"CH{channel} probe ratio: {ratio}X")

    def set_channel_label(self, channel: int, label: str, show: bool = True) -> None:
        """
        Set channel label text.

        Args:
            channel: Channel number (1-4)
            label: Label text to display
            show: True to show label (Keysight shows label when set)
        """
        self._validate_channel(channel)
        if show:
            self._write(":DISPlay:LABel ON")
        self._write(f':CHANnel{channel}:LABel "{label}"', **{f"ch{channel}_label": label})
        print(f'CH{channel} label: "{label}"')

    def invert_channel(self, channel: int, enable: bool) -> None:
        """
        Invert the waveform display.

        Args:
            channel: Channel number (1-4)
            enable: True to invert waveform, False for normal display
        """
        self._validate_channel(channel)
        value = "ON" if enable else "OFF"
        self._write(f":CHANnel{channel}:INVert {value}", **{f"ch{channel}_inverted": enable})
        state = "inverted" if enable else "normal"
        print(f"CH{channel} display: {state}")

    def set_bandwidth_limit(self, channel: int, limit: str) -> None:
        """
        Set bandwidth limit for a channel.

        Keysight 1000X uses ON/OFF instead of 20M/OFF.
        For compatibility, '20M' is mapped to 'ON'.

        Args:
            channel: Channel number (1-4)
            limit: '20M' or 'ON' for 20MHz limit, 'OFF' to disable
        """
        self._validate_channel(channel)
        limit = limit.upper()

        if limit not in self._BW_LIMIT_MAP:
            raise ValueError(f"Limit must be one of {tuple(self._BW_LIMIT_MAP.keys())}, got '{limit}'")

        keysight_limit = self._BW_LIMIT_MAP[limit]
        self._write(
            f":CHANnel{channel}:BWLimit {keysight_limit}",
            **{f"ch{channel}_bwlimit": keysight_limit},
        )
        print(f"CH{channel} bandwidth limit: {keysight_limit}")

    # ========================================
    # Horizontal Control
    # ========================================

    def set_horizontal_scale(self, seconds_per_div: float) -> None:
        """
        Set horizontal timebase scale.

        Args:
            seconds_per_div: Time per division in seconds
        """
        self._write(f":TIMebase:SCALe {seconds_per_div}", timebase_scale=seconds_per_div)
        print(f"Timebase: {seconds_per_div} s/div")

    def set_horizontal_offset(self, offset: float) -> None:
        """
        Set horizontal offset (time position).

        Note: Keysight uses :TIMebase:POSition (not OFFSet).

        Args:
            offset: Time offset in seconds
        """
        self._write(f":TIMebase:POSition {offset}", timebase_position=offset)
        print(f"Horizontal position: {offset} s")

    def set_horizontal_position(self, offset: float) -> None:
        """Alias for set_horizontal_offset."""
        self.set_horizontal_offset(offset)

    def get_horizontal_offset(self) -> float:
        """
        Get the current horizontal offset (time position).

        Returns:
            float: Time offset in seconds
        """
        response = self.instrument.query(":TIMebase:POSition?")
        return float(response.strip())

    def move_horizontal(self, delta: float) -> None:
        """
        Move the horizontal position by a delta amount.

        Args:
            delta: Amount to move in seconds (positive = right, negative = left)
        """
        current_pos = self.get_horizontal_offset()
        new_pos = current_pos + delta
        self.set_horizontal_offset(new_pos)
        print(f"Horizontal position moved to: {new_pos:.6f} s")

    _TIMEBASE_MODE_ALLOWLIST = ("MAIN", "WINDOW", "XY", "ROLL")
    _TIMEBASE_REF_ALLOWLIST = ("LEFT", "CENTER", "RIGHT")

    def set_timebase_mode(self, mode: str) -> None:
        """
        Set the timebase mode.

        Args:
            mode: 'MAIN', 'WINDow', 'XY', or 'ROLL'
        """
        mode_upper = mode.upper()
        if mode_upper not in self._TIMEBASE_MODE_ALLOWLIST:
            raise ValueError(f"Timebase mode must be one of {self._TIMEBASE_MODE_ALLOWLIST}, got '{mode}'")
        mode_map = {"MAIN": "MAIN", "WINDOW": "WINDow", "XY": "XY", "ROLL": "ROLL"}
        self._write(f":TIMebase:MODE {mode_map[mode_upper]}", timebase_mode=mode_upper)
        print(f"Timebase mode: {mode_upper}")

    def get_timebase_mode(self) -> str:
        """Query the current timebase mode."""
        response = self.instrument.query(":TIMebase:MODE?")
        return response.strip()

    def set_timebase_reference(self, ref: str) -> None:
        """
        Set the timebase reference position.

        Args:
            ref: 'LEFT', 'CENTer', or 'RIGHt'
        """
        ref_upper = ref.upper()
        if ref_upper not in self._TIMEBASE_REF_ALLOWLIST:
            raise ValueError(f"Timebase reference must be one of {self._TIMEBASE_REF_ALLOWLIST}, got '{ref}'")
        ref_map = {"LEFT": "LEFT", "CENTER": "CENTer", "RIGHT": "RIGHt"}
        self._write(f":TIMebase:REFerence {ref_map[ref_upper]}", timebase_reference=ref_upper)
        print(f"Timebase reference: {ref_upper}")

    def get_timebase_reference(self) -> str:
        """Query the current timebase reference position."""
        response = self.instrument.query(":TIMebase:REFerence?")
        return response.strip()

    # ========================================
    # Trigger Control
    # ========================================

    def configure_trigger(self, channel: int, level: float, slope: str = "RISE", mode: str = "AUTO") -> None:
        """
        Configure edge trigger.

        Args:
            channel: Trigger source channel (1-4)
            level: Trigger level in volts
            slope: 'RISE', 'FALL', 'RFALL', or 'EITHER'
            mode: 'AUTO', 'NORMAL', or 'SINGLE'
        """
        self._validate_channel(channel)

        # Map slope names to Keysight SCPI
        slope_map = {
            "RISE": "POSitive",
            "FALL": "NEGative",
            "RFALL": "EITHer",
            "EITHER": "EITHer",
            "POSITIVE": "POSitive",
            "NEGATIVE": "NEGative",
        }
        slope_cmd = slope_map.get(slope.upper(), "POSitive")

        # Map mode
        mode_upper = mode.upper()
        mode_map = {"AUTO": "AUTO", "NORMAL": "NORMal", "SINGLE": "NORMal"}
        sweep_cmd = mode_map.get(mode_upper, "AUTO")

        self._write(":TRIGger:MODE EDGE", trigger_mode="EDGE")
        self._write(f":TRIGger:EDGE:SOURce CHANnel{channel}", trigger_source=channel)
        self._write(f":TRIGger:EDGE:SLOPe {slope_cmd}", trigger_slope=slope_cmd)
        self._write(f":TRIGger:EDGE:LEVel {level},CHANnel{channel}", trigger_level=level)
        self._write(f":TRIGger:SWEep {sweep_cmd}", trigger_sweep=sweep_cmd)

        # If SINGLE mode requested, also arm single shot
        if mode_upper == "SINGLE":
            self.single()

        print(f"Trigger: CH{channel}, {level}V, {slope}")

    def set_trigger_sweep(self, sweep: str) -> None:
        """
        Set trigger sweep mode.

        Args:
            sweep: 'AUTO' or 'NORMal'
        """
        sweep = sweep.upper()
        if sweep not in self._TRIGGER_SWEEP_ALLOWLIST:
            raise ValueError(f"Sweep must be one of {self._TRIGGER_SWEEP_ALLOWLIST}, got '{sweep}'")

        sweep_cmd = "NORMal" if sweep == "NORMAL" else "AUTO"
        self._write(f":TRIGger:SWEep {sweep_cmd}", trigger_sweep=sweep_cmd)
        print(f"Trigger sweep mode: {sweep}")

    _TRIGGER_COUPLING_ALLOWLIST = ("AC", "DC", "LFREJECT")

    def set_trigger_holdoff(self, holdoff: float) -> None:
        """
        Set trigger holdoff time.

        Args:
            holdoff: Holdoff time in seconds (minimum 60 ns)
        """
        if holdoff < 60e-9:
            raise ValueError(f"Holdoff must be >= 60 ns, got {holdoff}")
        self._write(f":TRIGger:HOLDoff {holdoff}", trigger_holdoff=holdoff)
        print(f"Trigger holdoff: {holdoff} s")

    def get_trigger_holdoff(self) -> float:
        """Query the current trigger holdoff time."""
        response = self.instrument.query(":TRIGger:HOLDoff?")
        return float(response.strip())

    def set_trigger_noise_reject(self, enable: bool) -> None:
        """Enable or disable trigger noise reject filter."""
        val = 1 if enable else 0
        self._write(f":TRIGger:NREJect {val}", trigger_nreject=enable)
        print(f"Trigger noise reject: {'ON' if enable else 'OFF'}")

    def set_trigger_hf_reject(self, enable: bool) -> None:
        """Enable or disable trigger high-frequency reject filter."""
        val = 1 if enable else 0
        self._write(f":TRIGger:HFReject {val}", trigger_hfreject=enable)
        print(f"Trigger HF reject: {'ON' if enable else 'OFF'}")

    def set_trigger_coupling(self, coupling: str) -> None:
        """
        Set trigger coupling mode.

        Args:
            coupling: 'AC', 'DC', or 'LFReject'
        """
        coupling_upper = coupling.upper()
        if coupling_upper not in self._TRIGGER_COUPLING_ALLOWLIST:
            raise ValueError(f"Trigger coupling must be one of {self._TRIGGER_COUPLING_ALLOWLIST}, got '{coupling}'")
        coupling_map = {"AC": "AC", "DC": "DC", "LFREJECT": "LFReject"}
        self._write(
            f":TRIGger:EDGE:COUPling {coupling_map[coupling_upper]}",
            trigger_coupling=coupling_upper,
        )
        print(f"Trigger coupling: {coupling_upper}")

    def get_trigger_status(self) -> str:
        """
        Query current trigger status.

        Keysight 1000X does not have :TRIGger:STATus? -- uses :TER? instead.
        :TER? returns 1 if a trigger event has occurred, 0 otherwise.

        Returns:
            str: 'TD' if triggered, 'RUN' otherwise
        """
        response = self.instrument.query(":TER?")
        value = response.strip()
        if value == "1":
            return "TD"
        return "RUN"

    def wait_for_stop(self, timeout: float = 10.0) -> bool:
        """
        Poll trigger status until the scope has triggered.

        Call after single() to block until the trigger fires.

        Args:
            timeout: Maximum seconds to wait (default 10.0)

        Returns:
            bool: True if scope triggered, False if timed out
        """
        time.sleep(0.1)  # Let the scope process :SINGle before polling
        deadline = time.time() + timeout
        while time.time() < deadline:
            response = self.instrument.query(":TER?")
            if response.strip() == "1":
                time.sleep(0.5)
                return True
            time.sleep(0.2)
        return False

    # ========================================
    # Measurements
    # ========================================

    def measure(self, channel: int, measurement_type: str) -> float:
        """
        Measure any waveform parameter.

        Keysight uses :MEASure:{TYPE}? CHANnel{n} format (not :MEASure:ITEM?).

        Args:
            channel: Channel number (1-4)
            measurement_type: Measurement parameter (case-insensitive)

        Returns:
            float: Measurement value
        """
        self._validate_channel(channel)
        meas_type = self._resolve_meas_type(measurement_type)

        try:
            response = self.instrument.query(f":MEASure:{meas_type}? CHANnel{channel}")
            value = float(response.strip())
            return value
        except (ValueError, TypeError):
            return float("nan")

    def measure_bnf(self, channel: int, measurement_type: str) -> float:
        """Alias for measure() for compatibility with REPL code."""
        return self.measure(channel, measurement_type)

    def configure_measurement(self, channel: int, measurement_type: str) -> None:
        """
        Configure a measurement slot without querying the result.

        Args:
            channel: Channel number (1-4)
            measurement_type: Measurement parameter
        """
        self._validate_channel(channel)
        meas_type = self._resolve_meas_type(measurement_type)
        self._write(f":MEASure:{meas_type} CHANnel{channel}")

    def clear_measurements(self) -> None:
        """Clear all measurement items from the display."""
        self._write(":MEASure:CLEar")
        print("Measurement items cleared from display")

    def set_measurement_statistics(self, enable: bool) -> None:
        """Enable or disable measurement statistics display."""
        # Keysight 1000X uses :MEASure:STATistics:DISPlay ON|OFF
        state = "ON" if enable else "OFF"
        self._write(f":MEASure:STATistics:DISPlay {state}", meas_statistics=enable)
        print(f"Measurement statistics: {state}")

    def reset_measurement_statistics(self) -> None:
        """Reset all measurement statistics."""
        self._write(":MEASure:STATistics:RESet")
        print("Measurement statistics reset")

    def get_measurement_results(self) -> str:
        """
        Query all active measurement results.

        Returns:
            str: Raw results string from the instrument
        """
        response = self.instrument.query(":MEASure:RESults?")
        return response.strip()

    def measure_delay(
        self,
        ch1: int,
        ch2: int,
        edge1: str = "RISE",
        edge2: str = "RISE",
        direction: str = "FORWARDS",
    ) -> float:
        """
        Measure delay between two channels.

        Args:
            ch1: First channel (1-4)
            ch2: Second channel (1-4)
            edge1: Edge type for ch1 ('RISE' or 'FALL')
            edge2: Edge type for ch2 ('RISE' or 'FALL')
            direction: Direction ('FORWARDS' or 'BACKWARDS')

        Returns:
            float: Delay in seconds
        """
        self._validate_channel(ch1)
        self._validate_channel(ch2)

        try:
            response = self.instrument.query(f":MEASure:DELay? CHANnel{ch1},CHANnel{ch2}")
            return float(response.strip())
        except (ValueError, TypeError):
            return float("nan")

    # Convenience measurement methods

    def measure_vpp(self, channel: int) -> float:
        """Measure peak-to-peak voltage."""
        return self.measure(channel, "VPP")

    def measure_vrms(self, channel: int) -> float:
        """Measure RMS voltage."""
        return self.measure(channel, "VRMS")

    def measure_frequency(self, channel: int) -> float:
        """Measure frequency in Hz."""
        return self.measure(channel, "FREQuency")

    def measure_period(self, channel: int) -> float:
        """Measure period in seconds."""
        return self.measure(channel, "PERiod")

    def measure_amplitude(self, channel: int) -> float:
        """Measure amplitude (Vtop - Vbase)."""
        return self.measure(channel, "VAMPlitude")

    def measure_peak_to_peak(self, channel: int) -> float:
        """Measure peak-to-peak voltage (alias for measure_vpp)."""
        return self.measure(channel, "VPP")

    def measure_rms(self, channel: int) -> float:
        """Measure RMS voltage (alias for measure_vrms)."""
        return self.measure(channel, "VRMS")

    def measure_mean(self, channel: int) -> float:
        """Measure mean (average) voltage."""
        return self.measure(channel, "VAVerage")

    def measure_rise_time(self, channel: int) -> float:
        """Measure rise time."""
        return self.measure(channel, "RISetime")

    def measure_fall_time(self, channel: int) -> float:
        """Measure fall time."""
        return self.measure(channel, "FALLtime")

    def measure_duty_cycle(self, channel: int) -> float:
        """Measure duty cycle in percent."""
        return self.measure(channel, "DUTYcycle")

    def measure_pos_width(self, channel: int) -> float:
        """Measure positive pulse width."""
        return self.measure(channel, "PWIDth")

    def measure_neg_width(self, channel: int) -> float:
        """Measure negative pulse width."""
        return self.measure(channel, "NWIDth")

    def measure_overshoot(self, channel: int) -> float:
        """Measure overshoot in percent."""
        return self.measure(channel, "OVERshoot")

    def measure_preshoot(self, channel: int) -> float:
        """Measure preshoot in percent."""
        return self.measure(channel, "PREShoot")

    def measure_counter(self, channel: int = None) -> float:
        """
        Read the hardware frequency counter (higher accuracy than measure_frequency).

        Args:
            channel: Channel number (1-4) or None for current source

        Returns:
            float: Frequency in Hz
        """
        if channel is not None:
            self._validate_channel(channel)
            response = self.instrument.query(f":MEASure:COUNter? CHANnel{channel}")
        else:
            response = self.instrument.query(":MEASure:COUNter?")
        try:
            return float(response.strip())
        except (ValueError, TypeError):
            return float("nan")

    # ========================================
    # Waveform Acquisition
    # ========================================

    def get_waveform_preamble(self) -> dict:
        """
        Get all waveform scaling parameters.

        Returns:
            dict: Waveform parameters with 10 comma-separated values:
                - format, type, points, count
                - xincrement, xorigin, xreference
                - yincrement, yorigin, yreference
        """
        response = self.instrument.query(":WAVeform:PREamble?")
        values = [float(v) for v in response.strip().split(",")]

        preamble = {
            "format": int(values[0]),
            "type": int(values[1]),
            "points": int(values[2]),
            "count": int(values[3]),
            "xincrement": values[4],
            "xorigin": values[5],
            "xreference": values[6],
            "yincrement": values[7],
            "yorigin": values[8],
            "yreference": values[9],
        }
        return preamble

    def acquire_waveform(self, channel: int, mode: str = "NORMAL") -> WaveformData:
        """
        Acquire complete waveform with proper scaling.

        Args:
            channel: Channel number (1-4)
            mode: Acquisition mode ('NORMAL', 'MAXIMUM', 'RAW')

        Returns:
            WaveformData object with time and voltage arrays
        """
        self._validate_channel(channel)
        mode = mode.upper()

        # Configure waveform acquisition
        self._write(f":WAVeform:SOURce CHANnel{channel}", waveform_source=channel)
        # Keysight uses :WAVeform:POINts:MODE (not :WAVeform:MODE)
        self._write(f":WAVeform:POINts:MODE {mode}", waveform_points_mode=mode)
        self._write(":WAVeform:FORMat BYTE", waveform_format="BYTE")

        # Get preamble (scaling parameters)
        preamble = self.get_waveform_preamble()

        # Get waveform data
        print(f"Acquiring waveform data ({preamble['points']} points)...")
        raw_data = self.instrument.query_binary_values(
            ":WAVeform:DATA?",
            datatype="B",  # Unsigned byte
            is_big_endian=False,
        )
        raw_data = np.array(raw_data)

        # Convert to voltage
        voltage = (raw_data.astype(float) - preamble["yreference"]) * preamble["yincrement"] + preamble["yorigin"]

        # Generate time axis
        indices = np.arange(len(raw_data))
        time_arr = preamble["xorigin"] + (indices - preamble["xreference"]) * preamble["xincrement"]

        # Calculate sample rate
        sample_rate = 1.0 / preamble["xincrement"] if preamble["xincrement"] > 0 else 0.0

        waveform = WaveformData(
            time=time_arr,
            voltage=voltage,
            channel=channel,
            sample_rate=sample_rate,
            points=len(raw_data),
        )

        print(f"Acquired {len(waveform)} points from CH{channel}")
        return waveform

    def save_waveform_csv(
        self,
        channel: int,
        filename: str,
        max_points: int | None = None,
        time_window: float | None = None,
    ) -> None:
        """
        Save waveform from a single channel to a CSV file.

        Args:
            channel: Channel number (1-4)
            filename: Output CSV filename
            max_points: Maximum number of points to save
            time_window: Time window in seconds to save
        """
        import csv

        waveform = self.acquire_waveform(channel, mode="NORMAL")
        times = waveform.time
        volts = waveform.voltage

        if len(times) == 0:
            print("No data captured.")
            return

        # Apply windowing if specified
        if time_window is not None:
            dt = times[1] - times[0] if len(times) > 1 else 0
            if dt > 0:
                max_points = int(time_window / dt)

        if max_points is not None and max_points < len(times):
            times = times[-max_points:]
            volts = volts[-max_points:]
            actual_time = times[-1] - times[0]
            print(f"Saving {max_points} points ({actual_time:.6f} seconds) - most recent data")

        with open(filename, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Time (s)", f"CH{channel} Voltage (V)"])
            for t, v in zip(times, volts, strict=True):
                writer.writerow([t, v])

        print(f"Waveform from CH{channel} saved to {filename}")

    def save_waveforms_csv(
        self,
        channels: list,
        filename: str,
        max_points: int | None = None,
        time_window: float | None = None,
    ) -> None:
        """
        Save waveforms from multiple channels to a single CSV file.

        Args:
            channels: List of channel numbers to capture
            filename: Output CSV filename
            max_points: Maximum number of points to save
            time_window: Time window in seconds to save
        """
        import csv

        channel_data = {}
        times = None

        for channel in channels:
            self._validate_channel(channel)
            waveform = self.acquire_waveform(channel, mode="NORMAL")

            if len(waveform.time) == 0:
                print(f"No data captured from CH{channel}.")
                continue

            channel_data[channel] = waveform.voltage
            if times is None:
                times = waveform.time

        if not channel_data:
            print("No data captured from any channel.")
            return

        # Apply windowing if specified
        if time_window is not None:
            dt = times[1] - times[0] if len(times) > 1 else 0
            if dt > 0:
                max_points = int(time_window / dt)

        if max_points is not None and max_points < len(times):
            times = times[-max_points:]
            for ch in channel_data:
                channel_data[ch] = channel_data[ch][-max_points:]
            actual_time = times[-1] - times[0]
            print(f"Saving {max_points} points ({actual_time:.6f} seconds) - most recent data")

        with open(filename, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            header = ["Time (s)"] + [f"CH{ch} Voltage (V)" for ch in sorted(channel_data.keys())]
            writer.writerow(header)

            for i in range(len(times)):
                row = [times[i]]
                for ch in sorted(channel_data.keys()):
                    row.append(channel_data[ch][i])
                writer.writerow(row)

        channels_list = ",".join(str(ch) for ch in sorted(channel_data.keys()))
        print(f"Waveforms from CH{channels_list} saved to {filename}")

    def get_waveform_data(self, channel: int) -> list:
        """
        Get raw waveform data as a list of byte values (REPL-compatible).

        Args:
            channel: Channel number (1-4)

        Returns:
            list: Raw byte values (0-255)
        """
        waveform = self.acquire_waveform(channel)
        return waveform.voltage.tolist()

    def get_waveform_scaled(self, channel: int) -> tuple:
        """
        Get scaled waveform data as (time_list, voltage_list) tuple (REPL-compatible).

        Args:
            channel: Channel number (1-4)

        Returns:
            tuple: (time_values, voltage_values) as Python lists
        """
        waveform = self.acquire_waveform(channel)
        return waveform.time.tolist(), waveform.voltage.tolist()

    # ========================================
    # Display Control
    # ========================================

    def get_screenshot(self) -> bytes:
        """
        Capture the current screen image as PNG data.

        Returns:
            bytes: PNG image data
        """
        print("Capturing screenshot (this may take several seconds)...")
        screenshot_data = self.instrument.query_binary_values(":DISPlay:DATA? PNG,COLor", datatype="B", container=bytes)
        print(f"Screenshot captured ({len(screenshot_data)} bytes)")
        return screenshot_data

    def clear_display(self) -> None:
        """Clear all waveforms on the screen."""
        self._write(":DISPlay:CLEar")
        print("Display cleared")

    def set_waveform_brightness(self, brightness: int) -> None:
        """
        Set the brightness of waveforms on the screen.

        Args:
            brightness: Brightness level in percentage (1-100)
        """
        if brightness < 1 or brightness > 100:
            raise ValueError(f"Brightness must be between 1 and 100, got {brightness}")

        self._write(f":DISPlay:INTensity:WAVeform {brightness}", display_brightness=brightness)
        print(f"Waveform brightness set to {brightness}%")

    _PERSISTENCE_MAP = {
        "MIN": "MINimum",
        "MINIMUM": "MINimum",
        "INF": "INFinite",
        "INFINITE": "INFinite",
        "OFF": "MINimum",
        "CLEAR": "MINimum",
    }

    def set_persistence(self, time_val: str) -> None:
        """
        Set the waveform persistence time.

        Args:
            time_val: 'MIN', 'INF', or a numeric seconds value
        """
        mapped = self._PERSISTENCE_MAP.get(time_val.upper(), time_val)
        self._write(f":DISPlay:PERSistence {mapped}", display_persistence=mapped)
        print(f"Persistence set to {mapped}")

    def set_display_type(self, display_type: str) -> None:
        """
        Set the display type (always vectors on 1000X).

        Args:
            display_type: Display type (e.g., 'VECTORS')
        """
        self._write(":DISPlay:VECTors ON", display_vectors=True)
        print("Display type set to VECTORS")

    # ========================================
    # Acquisition Control
    # ========================================

    def set_acquisition_type(self, acq_type: str) -> None:
        """
        Set the acquisition type.

        Args:
            acq_type: 'NORMal', 'AVERage', 'HRESolution', or 'PEAK'
        """
        acq_type = acq_type.upper()
        if acq_type not in self._ACQ_TYPE_ALLOWLIST:
            raise ValueError(f"Acquisition type must be one of {self._ACQ_TYPE_ALLOWLIST}, got '{acq_type}'")

        self._write(f":ACQuire:TYPE {acq_type}", acq_type=acq_type)
        print(f"Acquisition type set to {acq_type}")

    def set_average_count(self, count: int) -> None:
        """
        Set the number of averages for AVERAGE acquisition mode.

        Args:
            count: Number of averages
        """
        self._write(f":ACQuire:COUNt {count}", acq_count=count)
        print(f"Average count set to {count}")

    def get_sample_rate(self) -> float:
        """
        Query the current sample rate.

        Returns:
            float: Sample rate in Sa/s
        """
        response = self.instrument.query(":ACQuire:SRATe?")
        sample_rate = float(response.strip())
        print(f"Sample rate: {sample_rate:.3e} Sa/s")
        return sample_rate

    _ACQ_MODE_ALLOWLIST = ("RTIM", "SEGM")

    def set_acquisition_mode(self, mode: str) -> None:
        """
        Set acquisition mode.

        Args:
            mode: 'RTIM' (real-time) or 'SEGM' (segmented)
        """
        mode = mode.upper()
        if mode not in self._ACQ_MODE_ALLOWLIST:
            raise ValueError(f"Acquisition mode must be one of {self._ACQ_MODE_ALLOWLIST}, got '{mode}'")
        self._write(f":ACQuire:MODE {mode}", acq_mode=mode)
        print(f"Acquisition mode: {mode}")

    def set_segment_count(self, count: int) -> None:
        """
        Set the number of segments for segmented acquisition.

        Args:
            count: Number of segments (>= 2)
        """
        if count < 2:
            raise ValueError(f"Segment count must be >= 2, got {count}")
        self._write(f":ACQuire:SEGMented:COUNt {count}", segment_count=count)
        print(f"Segment count: {count}")

    def get_segment_count(self) -> int:
        """Query the current segment count."""
        response = self.instrument.query(":ACQuire:SEGMented:COUNt?")
        return int(float(response.strip()))

    def set_segment_index(self, index: int) -> None:
        """
        Select a segment for waveform readback.

        Args:
            index: Segment index (1-based)
        """
        if index < 1:
            raise ValueError(f"Segment index must be >= 1, got {index}")
        self._write(f":ACQuire:SEGMented:INDex {index}", segment_index=index)
        print(f"Segment index: {index}")

    def get_segment_index(self) -> int:
        """Query the current segment index."""
        response = self.instrument.query(":ACQuire:SEGMented:INDex?")
        return int(float(response.strip()))

    # ========================================
    # AWG (WGEN subsystem -- G-suffix models)
    # ========================================

    def awg_set_output_enable(self, enable: bool) -> None:
        """
        Enable or disable the AWG output.

        Args:
            enable: True to enable output, False to disable
        """
        state = 1 if enable else 0
        self._write(f":WGEN:OUTPut {state}", awg_output=enable)
        print(f"AWG output {'enabled' if enable else 'disabled'}")

    def awg_set_function(self, function: str) -> None:
        """
        Set the AWG waveform function type.

        Args:
            function: 'SINusoid', 'SQUare', 'RAMP', 'PULSe', 'DC', or 'NOISe'
        """
        if function not in self._AWG_FUNC_ALLOWLIST:
            raise ValueError(f"Function must be one of {self._AWG_FUNC_ALLOWLIST}, got '{function}'")

        self._write(f":WGEN:FUNCtion {function}", awg_function=function)
        print(f"AWG function set to {function}")

    def awg_set_frequency(self, freq: float) -> None:
        """
        Set the AWG output frequency.

        Args:
            freq: Frequency in Hz
        """
        self._write(f":WGEN:FREQuency {freq}", awg_frequency=freq)
        print(f"AWG frequency set to {freq} Hz")

    def awg_set_amplitude(self, amp: float) -> None:
        """
        Set the AWG output amplitude.

        Args:
            amp: Amplitude in volts (Vpp)
        """
        self._write(f":WGEN:VOLTage {amp}", awg_amplitude=amp)
        print(f"AWG amplitude set to {amp} Vpp")

    def awg_set_offset(self, offset: float) -> None:
        """
        Set the AWG DC offset.

        Args:
            offset: DC offset in volts
        """
        self._write(f":WGEN:VOLTage:OFFSet {offset}", awg_offset=offset)
        print(f"AWG offset set to {offset} V")

    def awg_set_square_duty(self, duty: float) -> None:
        """
        Set the AWG square wave duty cycle.

        Args:
            duty: Duty cycle percentage
        """
        self._write(f":WGEN:FUNCtion:SQUare:DCYCle {duty}", awg_square_duty=duty)
        print(f"AWG square duty cycle set to {duty}%")

    def awg_set_ramp_symmetry(self, sym: float) -> None:
        """
        Set the AWG ramp symmetry.

        Args:
            sym: Symmetry percentage
        """
        self._write(f":WGEN:FUNCtion:RAMP:SYMMetry {sym}", awg_ramp_symmetry=sym)
        print(f"AWG ramp symmetry set to {sym}%")

    def awg_configure_simple(
        self,
        func: str,
        freq: float,
        amp: float,
        offset: float = 0.0,
        enable: bool = True,
    ) -> None:
        """
        High-level method to quickly configure and enable the AWG.

        Args:
            func: Waveform type
            freq: Output frequency in Hz
            amp: Output amplitude in volts (Vpp)
            offset: DC offset in volts (default: 0.0)
            enable: Enable output after configuration (default: True)
        """
        print(f"Configuring AWG: {func}, {freq} Hz, {amp} Vpp, {offset} V offset")

        # Disable output first for safety
        self.awg_set_output_enable(False)

        # Configure waveform parameters
        self.awg_set_function(func)
        self.awg_set_frequency(freq)
        self.awg_set_amplitude(amp)
        self.awg_set_offset(offset)

        # Enable output if requested
        if enable:
            self.awg_set_output_enable(True)

        print("AWG configured successfully")

    _WGEN_MOD_TYPE_ALLOWLIST = ("AM", "FM", "FSK")

    def awg_set_modulation_enable(self, enable: bool) -> None:
        """Enable or disable AWG modulation."""
        val = 1 if enable else 0
        self._write(f":WGEN:MODulation:STATe {val}", awg_mod_enable=enable)
        print(f"AWG modulation: {'ON' if enable else 'OFF'}")

    def awg_set_modulation_type(self, mod_type: str) -> None:
        """
        Set AWG modulation type.

        Args:
            mod_type: 'AM', 'FM', or 'FSK'
        """
        mod_type = mod_type.upper()
        if mod_type not in self._WGEN_MOD_TYPE_ALLOWLIST:
            raise ValueError(f"Modulation type must be one of {self._WGEN_MOD_TYPE_ALLOWLIST}, got '{mod_type}'")
        self._write(f":WGEN:MODulation:TYPE {mod_type}", awg_mod_type=mod_type)
        print(f"AWG modulation type: {mod_type}")

    def awg_set_pulse_width(self, width: float) -> None:
        """
        Set AWG pulse width.

        Args:
            width: Pulse width in seconds (must be > 0)
        """
        if width <= 0:
            raise ValueError(f"Pulse width must be > 0, got {width}")
        self._write(f":WGEN:FUNCtion:PULSe:WIDTh {width}", awg_pulse_width=width)
        print(f"AWG pulse width: {width} s")

    # ========================================
    # DVM (Digital Voltmeter)
    # ========================================

    def set_dvm_enable(self, enable: bool) -> None:
        """
        Enable or disable the digital voltmeter.

        Args:
            enable: True to enable, False to disable
        """
        state = "ON" if enable else "OFF"
        self._write(f":DVM:ENABle {state}", dvm_enable=enable)
        print(f"DVM {'enabled' if enable else 'disabled'}")

    def get_dvm_current(self) -> float:
        """
        Query the current voltage value from DVM.

        Returns:
            float: Current voltage value
        """
        response = self.instrument.query(":DVM:CURRent?")
        value = float(response.strip())
        print(f"DVM current value: {value} V")
        return value

    def set_dvm_source(self, source: int) -> None:
        """
        Set the DVM source channel.

        Args:
            source: Channel number (1-4)
        """
        self._validate_channel(source)
        self._write(f":DVM:SOURce CHANnel{source}", dvm_source=source)
        print(f"DVM source set to CH{source}")

    def set_dvm_mode(self, mode: str) -> None:
        """
        Set the DVM mode.

        Args:
            mode: DVM mode (e.g., 'DC', 'ACRMs', 'DCRMS')
        """
        self._write(f":DVM:MODE {mode}", dvm_mode=mode)
        print(f"DVM mode set to {mode}")

    # ========================================
    # Math (single channel via :FUNCtion)
    # ========================================

    def enable_math_channel(self, math_ch: int = 1, enable: bool = True) -> None:
        """
        Enable or disable the math channel.

        Keysight 1000X has a single math channel via :FUNCtion subsystem.

        Args:
            math_ch: Math channel number (ignored, Keysight 1000X has one math channel)
            enable: True to enable, False to disable
        """
        state = "ON" if enable else "OFF"
        self._write(f":FUNCtion:DISPlay {state}", math_display=enable)
        print(f"Math channel {'enabled' if enable else 'disabled'}")

    def configure_math_operation(self, math_ch: int, operation: str, source1: str, source2: str = None) -> None:
        """
        Configure math channel for arithmetic operation.

        Args:
            math_ch: Math channel (ignored, Keysight 1000X has one math channel)
            operation: 'ADD', 'SUBTRACT', 'MULTIPLY'
            source1: Source A (e.g., 'CHAN1')
            source2: Source B (e.g., 'CHAN2')
        """
        op_map = {
            "ADD": "ADD",
            "SUBTRACT": "SUBTract",
            "MULTIPLY": "MULTiply",
        }
        operation = operation.upper()
        scpi_op = op_map.get(operation, operation)

        self._write(f":FUNCtion:OPERation {scpi_op}", math_operation=scpi_op)

        # Set sources
        scpi_source1 = source1.upper().replace("CHAN", "CHANnel")
        self._write(f":FUNCtion:SOURce1 {scpi_source1}", math_source1=scpi_source1)

        if source2:
            scpi_source2 = source2.upper().replace("CHAN", "CHANnel")
            self._write(f":FUNCtion:SOURce2 {scpi_source2}", math_source2=scpi_source2)

        print(f"Math configured: {source1} {operation} {source2 if source2 else ''}")

    def configure_math_function(self, math_ch: int, function: str, source: str) -> None:
        """
        Configure math channel for a function operation.

        Args:
            math_ch: Math channel (ignored)
            function: 'INTG', 'DIFF', 'SQRT', etc.
            source: Source channel (e.g., 'CHAN1')
        """
        self._write(f":FUNCtion:OPERation {function}", math_operation=function)
        scpi_source = source.upper().replace("CHAN", "CHANnel")
        self._write(f":FUNCtion:SOURce1 {scpi_source}", math_source1=scpi_source)
        print(f"Math configured: {function}({source})")

    def configure_fft(self, math_ch: int, source: str, window: str = "RECT") -> None:
        """
        Configure math channel for FFT analysis.

        Args:
            math_ch: Math channel (ignored)
            source: Source channel (e.g., 'CHAN1')
            window: FFT window ('RECT', 'HANN', 'FLAT', 'BLAC')
        """
        self._write(":FUNCtion:OPERation FFT", math_operation="FFT")
        scpi_source = source.upper().replace("CHAN", "CHANnel")
        self._write(f":FUNCtion:SOURce1 {scpi_source}", math_source1=scpi_source)

        window_map = {
            "RECT": "RECTangular",
            "HANN": "HANNing",
            "FLAT": "FLATtop",
            "BLAC": "BLACkman",
            "BLACK": "BLACkman",
        }
        scpi_window = window_map.get(window.upper(), window)
        self._write(f":FUNCtion:FFT:WINDow {scpi_window}", math_fft_window=scpi_window)
        print(f"FFT configured: source={source}, window={window}")

    def set_math_scale(self, math_ch: int, scale: float, offset: float = None) -> None:
        """
        Set vertical scale and offset for math channel.

        Args:
            math_ch: Math channel (ignored)
            scale: Vertical scale (V/div)
            offset: Vertical offset (optional)
        """
        self._write(f":FUNCtion:SCALe {scale}", math_scale=scale)
        if offset is not None:
            self._write(f":FUNCtion:OFFSet {offset}", math_offset=offset)
            print(f"Math scale: {scale} V/div, offset: {offset} V")
        else:
            print(f"Math scale: {scale} V/div")

    # ========================================
    # Mask Test (:MTESt subsystem)
    # ========================================

    def set_mask_enable(self, enable: bool) -> None:
        """
        Enable or disable mask testing.

        Args:
            enable: True to enable, False to disable
        """
        state = "ON" if enable else "OFF"
        self._write(f":MTESt:ENABle {state}", mask_enable=enable)
        status = "enabled" if enable else "disabled"
        print(f"Mask testing {status}")

    def get_mask_enable(self) -> bool:
        """
        Query whether mask testing is enabled.

        Returns:
            bool: True if enabled, False if disabled
        """
        response = self.instrument.query(":MTESt:ENABle?")
        enabled = response.strip() == "1"
        return enabled

    def set_mask_source(self, channel: int) -> None:
        """
        Set the source channel for mask testing.

        Args:
            channel: Channel number (1-4)
        """
        self._validate_channel(channel)
        self._write(f":MTESt:SOURce CHANnel{channel}", mask_source=channel)
        print(f"Mask test source set to CH{channel}")

    def get_mask_source(self) -> str:
        """
        Query the source channel for mask testing.

        Returns:
            str: Source channel string
        """
        response = self.instrument.query(":MTESt:SOURce?")
        return response.strip()

    def set_mask_tolerance_x(self, tol: float) -> None:
        """
        Set the horizontal tolerance for the auto mask.

        Args:
            tol: Horizontal tolerance in divisions
        """
        self._write(f":MTESt:AMASk:XDELta {tol}", mask_tolerance_x=tol)
        print(f"Mask horizontal tolerance: {tol}")

    def set_mask_tolerance_y(self, tol: float) -> None:
        """
        Set the vertical tolerance for the auto mask.

        Args:
            tol: Vertical tolerance in divisions
        """
        self._write(f":MTESt:AMASk:YDELta {tol}", mask_tolerance_y=tol)
        print(f"Mask vertical tolerance: {tol}")

    def create_mask(self) -> None:
        """Create a mask from the current waveform using auto mask."""
        self._write(":MTESt:AMASk:CREate")
        print("Mask created from current waveform")

    def start_mask_test(self) -> None:
        """Start the mask test."""
        self._write(":MTESt:ENABle ON", mask_enable=True)
        print("Mask test started")

    def stop_mask_test(self) -> None:
        """Stop the mask test."""
        self._write(":MTESt:ENABle OFF", mask_enable=False)
        print("Mask test stopped")

    def get_mask_failed_count(self) -> int:
        """
        Query the number of waveforms that failed the mask test.

        Returns:
            int: Number of failed waveforms
        """
        response = self.instrument.query(":MTESt:COUNt:FAILures?")
        failed = int(response.strip())
        print(f"Failed waveforms: {failed}")
        return failed

    def get_mask_total_count(self) -> int:
        """
        Query the total number of waveforms tested.

        Returns:
            int: Total number of waveforms tested
        """
        response = self.instrument.query(":MTESt:COUNt:WAVeforms?")
        total = int(response.strip())
        print(f"Total waveforms tested: {total}")
        return total

    def get_mask_passed_count(self) -> int:
        """
        Get the number of waveforms that passed the mask test.

        Returns:
            int: Number of passed waveforms (total - failed)
        """
        total = self.get_mask_total_count()
        failed = self.get_mask_failed_count()
        passed = total - failed
        print(f"Passed waveforms: {passed}")
        return passed

    def get_mask_statistics(self) -> dict:
        """
        Query all mask test statistics.

        Returns:
            dict: Dictionary with 'passed', 'failed', 'total' counts
        """
        total = int(self.instrument.query(":MTESt:COUNt:WAVeforms?").strip())
        failed = int(self.instrument.query(":MTESt:COUNt:FAILures?").strip())
        passed = total - failed

        print(f"Mask statistics: {passed} passed, {failed} failed, {total} total")
        return {"passed": passed, "failed": failed, "total": total}

    def reset_mask_statistics(self) -> None:
        """Reset the mask test statistics by toggling mask off and on."""
        self._write(":MTESt:ENABle OFF", mask_enable=False)
        self._write(":MTESt:ENABle ON", mask_enable=True)
        print("Mask statistics reset")

    def get_mask_test_status(self) -> str:
        """
        Query the mask test status.

        Returns:
            str: 'RUN' if enabled, 'STOP' if disabled
        """
        enabled = self.get_mask_enable()
        status = "RUN" if enabled else "STOP"
        print(f"Mask test status: {status}")
        return status

    # ========================================
    # Cursor Measurements (:MARKer subsystem)
    # ========================================

    _CURSOR_MODE_ALLOWLIST = ("OFF", "MANual", "WAVeform", "MEASurement")

    def set_cursor_mode(self, mode: str) -> None:
        """
        Set cursor mode.

        Args:
            mode: 'OFF', 'MANual', 'WAVeform', or 'MEASurement'
        """
        if mode not in self._CURSOR_MODE_ALLOWLIST:
            raise ValueError(f"Cursor mode must be one of {self._CURSOR_MODE_ALLOWLIST}, got '{mode}'")
        self._write(f":MARKer:MODE {mode}", cursor_mode=mode)
        print(f"Cursor mode: {mode}")

    def set_cursor_source(self, channel: int) -> None:
        """
        Set cursor source channel (both X1Y1 and X2Y2).

        Args:
            channel: Channel number (1-4)
        """
        self._validate_channel(channel)
        self._write(f":MARKer:X1Y1source CHANnel{channel}", cursor_source=channel)
        self._write(f":MARKer:X2Y2source CHANnel{channel}")

    def set_cursor_x1_position(self, position: float) -> None:
        """Set X1 cursor position in seconds."""
        self._write(f":MARKer:X1Position {position}", cursor_x1=position)

    def set_cursor_x2_position(self, position: float) -> None:
        """Set X2 cursor position in seconds."""
        self._write(f":MARKer:X2Position {position}", cursor_x2=position)

    def set_cursor_y1_position(self, position: float) -> None:
        """Set Y1 cursor position in volts."""
        self._write(f":MARKer:Y1Position {position}", cursor_y1=position)

    def set_cursor_y2_position(self, position: float) -> None:
        """Set Y2 cursor position in volts."""
        self._write(f":MARKer:Y2Position {position}", cursor_y2=position)

    def get_cursor_x_delta(self) -> float:
        """Get the delta between X1 and X2 cursors in seconds."""
        response = self.instrument.query(":MARKer:XDELta?")
        return float(response.strip())

    def get_cursor_y_delta(self) -> float:
        """Get the delta between Y1 and Y2 cursors in volts."""
        response = self.instrument.query(":MARKer:YDELta?")
        return float(response.strip())

    def set_manual_cursor_positions(
        self,
        x1: float = None,
        y1: float = None,
        x2: float = None,
        y2: float = None,
    ) -> None:
        """
        Set one or more cursor positions at once.

        Args:
            x1: X1 cursor position in seconds
            y1: Y1 cursor position in volts
            x2: X2 cursor position in seconds
            y2: Y2 cursor position in volts
        """
        if x1 is not None:
            self.set_cursor_x1_position(x1)
        if y1 is not None:
            self.set_cursor_y1_position(y1)
        if x2 is not None:
            self.set_cursor_x2_position(x2)
        if y2 is not None:
            self.set_cursor_y2_position(y2)

    def get_manual_cursor_values(self) -> dict:
        """
        Query all cursor positions and deltas.

        Returns:
            dict: Keys x1, y1, x2, y2, dx, dy
        """
        x1 = float(self.instrument.query(":MARKer:X1Position?").strip())
        y1 = float(self.instrument.query(":MARKer:Y1Position?").strip())
        x2 = float(self.instrument.query(":MARKer:X2Position?").strip())
        y2 = float(self.instrument.query(":MARKer:Y2Position?").strip())
        dx = float(self.instrument.query(":MARKer:XDELta?").strip())
        dy = float(self.instrument.query(":MARKer:YDELta?").strip())
        return {"x1": x1, "y1": y1, "x2": x2, "y2": y2, "dx": dx, "dy": dy}

    # ========================================
    # System Commands
    # ========================================

    def reset(self) -> None:
        """Reset oscilloscope to factory default settings."""
        self._write("*RST")
        self._write("*CLS")
        self._cache.clear()
        print("Oscilloscope reset to factory defaults")

    def clear_status(self) -> None:
        """Clear status byte and error queue."""
        self._write("*CLS")
        print("Status cleared")

    def get_error(self) -> str:
        """
        Read the most recent error from the system error queue.

        Returns:
            str: Error message string
        """
        response = self.instrument.query(":SYSTem:ERRor?")
        return response.strip()

    def save_setup(self, slot: int) -> None:
        """
        Save the current instrument setup to a memory slot.

        Args:
            slot: Memory slot (0-9)
        """
        if not 0 <= slot <= 9:
            raise ValueError(f"Slot must be 0-9, got {slot}")
        self._write(f"*SAV {slot}")
        print(f"Setup saved to slot {slot}")

    def recall_setup(self, slot: int) -> None:
        """
        Recall an instrument setup from a memory slot.

        Args:
            slot: Memory slot (0-9)
        """
        if not 0 <= slot <= 9:
            raise ValueError(f"Slot must be 0-9, got {slot}")
        self._write(f"*RCL {slot}")
        print(f"Setup recalled from slot {slot}")

    def self_test(self) -> int:
        """
        Run instrument self-test.

        Returns:
            int: 0 for pass, non-zero for fail
        """
        response = self.instrument.query("*TST?")
        return int(response.strip())

    def set_system_lock(self, enable: bool) -> None:
        """Lock or unlock the front panel."""
        state = "ON" if enable else "OFF"
        self._write(f":SYSTem:LOCK {state}", system_lock=enable)
        print(f"Front panel {'locked' if enable else 'unlocked'}")

    def set_system_message(self, message: str) -> None:
        """
        Display a message on the oscilloscope screen.

        Args:
            message: Text to display (empty string clears)
        """
        if message:
            self._write(f':SYSTem:DSP "{message}"')
        else:
            self._write(':SYSTem:DSP ""')
        print(f"System message: {message!r}")

    def set_display_vectors(self, enable: bool) -> None:
        """Enable or disable connect-the-dots waveform display."""
        val = "ON" if enable else "OFF"
        self._write(f":DISPlay:VECtors {val}", display_vectors=enable)
        print(f"Display vectors: {val}")

    def set_display_annotation(self, text: str) -> None:
        """
        Display an annotation on screen.

        Args:
            text: Annotation text
        """
        self._write(f':DISPlay:ANNotation:TEXT "{text}"')
        self._write(":DISPlay:ANNotation ON", display_annotation=True)
        print(f"Annotation: {text}")

    def clear_display_annotation(self) -> None:
        """Remove the on-screen annotation."""
        self._write(":DISPlay:ANNotation OFF", display_annotation=False)
        print("Annotation cleared")

    _CHANNEL_UNITS_ALLOWLIST = ("VOLT", "AMPERE")

    def set_channel_units(self, channel: int, units: str) -> None:
        """
        Set vertical axis units for a channel.

        Args:
            channel: Channel number (1-4)
            units: 'VOLT' or 'AMPere'
        """
        self._validate_channel(channel)
        units_upper = units.upper()
        if units_upper not in self._CHANNEL_UNITS_ALLOWLIST:
            raise ValueError(f"Units must be one of {self._CHANNEL_UNITS_ALLOWLIST}, got '{units}'")
        units_map = {"VOLT": "VOLT", "AMPERE": "AMPere"}
        self._write(
            f":CHANnel{channel}:UNITs {units_map[units_upper]}",
            **{f"ch{channel}_units": units_upper},
        )
        print(f"CH{channel} units: {units_upper}")

    def get_channel_units(self, channel: int) -> str:
        """
        Query the vertical axis units for a channel.

        Args:
            channel: Channel number (1-4)

        Returns:
            str: 'VOLT' or 'AMP'
        """
        self._validate_channel(channel)
        response = self.instrument.query(f":CHANnel{channel}:UNITs?")
        return response.strip()
