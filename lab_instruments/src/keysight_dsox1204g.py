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

    # ========================================
    # Basic Control
    # ========================================

    def run(self) -> None:
        """Start running the oscilloscope (continuous acquisition)."""
        self.instrument.write(":RUN")
        print("Oscilloscope running")

    def stop(self) -> None:
        """Stop the oscilloscope acquisition."""
        self.instrument.write(":STOP")
        print("Oscilloscope stopped")

    def single(self) -> None:
        """Set oscilloscope to single trigger mode and arm for one acquisition."""
        self.instrument.write(":SINGle")
        print("Single trigger armed")

    def autoset(self) -> None:
        """Perform an autoscale on the oscilloscope (Keysight uses AUToscale)."""
        self.instrument.write(":AUToscale")
        print("Autoscale executed - optimizing display settings...")

    def force_trigger(self) -> None:
        """Generate a trigger signal forcefully (Keysight uses TRIGger:FORCe)."""
        self.instrument.write(":TRIGger:FORCe")
        print("Trigger forced")

    # ========================================
    # Channel Control
    # ========================================

    def enable_channel(self, channel: int) -> None:
        """Enable a channel."""
        self._validate_channel(channel)
        self.instrument.write(f":CHANnel{channel}:DISPlay ON")
        print(f"CH{channel} enabled")

    def disable_channel(self, channel: int) -> None:
        """Disable a channel."""
        self._validate_channel(channel)
        self.instrument.write(f":CHANnel{channel}:DISPlay OFF")
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
        self.instrument.write(f":CHANnel{channel}:SCALe {volts_per_div}")
        self.instrument.write(f":CHANnel{channel}:OFFSet {offset}")
        print(f"CH{channel}: {volts_per_div} V/div, offset {offset} V")

    def set_vertical_position(self, channel: int, position: float) -> None:
        """
        Set vertical position (offset) of the channel.

        Args:
            channel: Channel number (1-4)
            position: Vertical offset in volts
        """
        self._validate_channel(channel)
        self.instrument.write(f":CHANnel{channel}:OFFSet {position}")
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
        if coupling not in ("DC", "AC"):
            raise ValueError("Coupling must be 'DC' or 'AC'")

        self.instrument.write(f":CHANnel{channel}:COUPling {coupling}")
        print(f"CH{channel} coupling: {coupling}")

    def set_probe_attenuation(self, channel: int, ratio: float) -> None:
        """
        Set probe attenuation ratio.

        Args:
            channel: Channel number (1-4)
            ratio: Probe attenuation ratio (e.g., 1, 10, 100)
        """
        self._validate_channel(channel)
        self.instrument.write(f":CHANnel{channel}:PROBe {ratio}")
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
        self.instrument.write(f':CHANnel{channel}:LABel "{label}"')
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
        self.instrument.write(f":CHANnel{channel}:INVert {value}")
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

        # Map Rigol-style "20M" to Keysight "ON"
        bw_map = {"20M": "ON", "ON": "ON", "OFF": "OFF"}
        if limit not in bw_map:
            raise ValueError(f"Limit must be '20M', 'ON', or 'OFF', got {limit}")

        keysight_limit = bw_map[limit]
        self.instrument.write(f":CHANnel{channel}:BWLimit {keysight_limit}")
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
        self.instrument.write(f":TIMebase:SCALe {seconds_per_div}")
        print(f"Timebase: {seconds_per_div} s/div")

    def set_horizontal_offset(self, offset: float) -> None:
        """
        Set horizontal offset (time position).

        Note: Keysight uses :TIMebase:POSition (not OFFSet).

        Args:
            offset: Time offset in seconds
        """
        self.instrument.write(f":TIMebase:POSition {offset}")
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

        self.instrument.write(":TRIGger:MODE EDGE")
        self.instrument.write(f":TRIGger:EDGE:SOURce CHANnel{channel}")
        self.instrument.write(f":TRIGger:EDGE:SLOPe {slope_cmd}")
        self.instrument.write(f":TRIGger:EDGE:LEVel {level},CHANnel{channel}")
        self.instrument.write(f":TRIGger:SWEep {sweep_cmd}")

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
        if sweep not in ("AUTO", "NORMAL"):
            raise ValueError(f"Sweep must be 'AUTO' or 'NORMal', got {sweep}")

        sweep_cmd = "NORMal" if sweep == "NORMAL" else "AUTO"
        self.instrument.write(f":TRIGger:SWEep {sweep_cmd}")
        print(f"Trigger sweep mode: {sweep}")

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
        self.instrument.write(f":MEASure:{meas_type} CHANnel{channel}")

    def clear_measurements(self) -> None:
        """Clear all measurement items from the display."""
        self.instrument.write(":MEASure:CLEar")
        print("Measurement items cleared from display")

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
        self.instrument.write(f":WAVeform:SOURce CHANnel{channel}")
        # Keysight uses :WAVeform:POINts:MODE (not :WAVeform:MODE)
        self.instrument.write(f":WAVeform:POINts:MODE {mode}")
        self.instrument.write(":WAVeform:FORMat BYTE")

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
        self.instrument.write(":DISPlay:CLEar")
        print("Display cleared")

    def set_waveform_brightness(self, brightness: int) -> None:
        """
        Set the brightness of waveforms on the screen.

        Args:
            brightness: Brightness level in percentage (1-100)
        """
        if brightness < 1 or brightness > 100:
            raise ValueError(f"Brightness must be between 1 and 100, got {brightness}")

        self.instrument.write(f":DISPlay:INTensity:WAVeform {brightness}")
        print(f"Waveform brightness set to {brightness}%")

    def set_persistence(self, time_val: str) -> None:
        """
        Set the waveform persistence time.

        Args:
            time_val: Persistence time value
        """
        self.instrument.write(f":DISPlay:PERSistence {time_val}")
        print(f"Persistence set to {time_val}")

    def set_display_type(self, display_type: str) -> None:
        """
        Set the display type (always vectors on 1000X).

        Args:
            display_type: Display type (e.g., 'VECTORS')
        """
        self.instrument.write(":DISPlay:VECTors ON")
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
        valid_types = ["NORMAL", "AVERAGE", "HRESOLUTION", "PEAK"]
        if acq_type not in valid_types:
            raise ValueError(f"Acquisition type must be one of {valid_types}, got {acq_type}")

        self.instrument.write(f":ACQuire:TYPE {acq_type}")
        print(f"Acquisition type set to {acq_type}")

    def set_average_count(self, count: int) -> None:
        """
        Set the number of averages for AVERAGE acquisition mode.

        Args:
            count: Number of averages
        """
        self.instrument.write(f":ACQuire:COUNt {count}")
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
        self.instrument.write(f":WGEN:OUTPut {state}")
        print(f"AWG output {'enabled' if enable else 'disabled'}")

    def awg_set_function(self, function: str) -> None:
        """
        Set the AWG waveform function type.

        Args:
            function: 'SINusoid', 'SQUare', 'RAMP', 'PULSe', 'DC', or 'NOISe'
        """
        valid_functions = ["SINusoid", "SQUare", "RAMP", "PULSe", "DC", "NOISe"]
        if function not in valid_functions:
            raise ValueError(f"Function must be one of {valid_functions}, got '{function}'")

        self.instrument.write(f":WGEN:FUNCtion {function}")
        print(f"AWG function set to {function}")

    def awg_set_frequency(self, freq: float) -> None:
        """
        Set the AWG output frequency.

        Args:
            freq: Frequency in Hz
        """
        self.instrument.write(f":WGEN:FREQuency {freq}")
        print(f"AWG frequency set to {freq} Hz")

    def awg_set_amplitude(self, amp: float) -> None:
        """
        Set the AWG output amplitude.

        Args:
            amp: Amplitude in volts (Vpp)
        """
        self.instrument.write(f":WGEN:VOLTage {amp}")
        print(f"AWG amplitude set to {amp} Vpp")

    def awg_set_offset(self, offset: float) -> None:
        """
        Set the AWG DC offset.

        Args:
            offset: DC offset in volts
        """
        self.instrument.write(f":WGEN:VOLTage:OFFSet {offset}")
        print(f"AWG offset set to {offset} V")

    def awg_set_square_duty(self, duty: float) -> None:
        """
        Set the AWG square wave duty cycle.

        Args:
            duty: Duty cycle percentage
        """
        self.instrument.write(f":WGEN:FUNCtion:SQUare:DCYCle {duty}")
        print(f"AWG square duty cycle set to {duty}%")

    def awg_set_ramp_symmetry(self, sym: float) -> None:
        """
        Set the AWG ramp symmetry.

        Args:
            sym: Symmetry percentage
        """
        self.instrument.write(f":WGEN:FUNCtion:RAMP:SYMMetry {sym}")
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
        self.instrument.write(f":DVM:ENABle {state}")
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
        if source not in (1, 2, 3, 4):
            raise ValueError(f"Source must be 1-4, got {source}")
        self.instrument.write(f":DVM:SOURce CHANnel{source}")
        print(f"DVM source set to CH{source}")

    def set_dvm_mode(self, mode: str) -> None:
        """
        Set the DVM mode.

        Args:
            mode: DVM mode (e.g., 'DC', 'ACRMs', 'DCRMS')
        """
        self.instrument.write(f":DVM:MODE {mode}")
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
        self.instrument.write(f":FUNCtion:DISPlay {state}")
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

        self.instrument.write(f":FUNCtion:OPERation {scpi_op}")

        # Set sources
        scpi_source1 = source1.upper().replace("CHAN", "CHANnel")
        self.instrument.write(f":FUNCtion:SOURce1 {scpi_source1}")

        if source2:
            scpi_source2 = source2.upper().replace("CHAN", "CHANnel")
            self.instrument.write(f":FUNCtion:SOURce2 {scpi_source2}")

        print(f"Math configured: {source1} {operation} {source2 if source2 else ''}")

    def configure_math_function(self, math_ch: int, function: str, source: str) -> None:
        """
        Configure math channel for a function operation.

        Args:
            math_ch: Math channel (ignored)
            function: 'INTG', 'DIFF', 'SQRT', etc.
            source: Source channel (e.g., 'CHAN1')
        """
        self.instrument.write(f":FUNCtion:OPERation {function}")
        scpi_source = source.upper().replace("CHAN", "CHANnel")
        self.instrument.write(f":FUNCtion:SOURce1 {scpi_source}")
        print(f"Math configured: {function}({source})")

    def configure_fft(self, math_ch: int, source: str, window: str = "RECT") -> None:
        """
        Configure math channel for FFT analysis.

        Args:
            math_ch: Math channel (ignored)
            source: Source channel (e.g., 'CHAN1')
            window: FFT window ('RECT', 'HANN', 'FLAT', 'BLAC')
        """
        self.instrument.write(":FUNCtion:OPERation FFT")
        scpi_source = source.upper().replace("CHAN", "CHANnel")
        self.instrument.write(f":FUNCtion:SOURce1 {scpi_source}")

        window_map = {
            "RECT": "RECTangular",
            "HANN": "HANNing",
            "FLAT": "FLATtop",
            "BLAC": "BLACkman",
            "BLACK": "BLACkman",
        }
        scpi_window = window_map.get(window.upper(), window)
        self.instrument.write(f":FUNCtion:FFT:WINDow {scpi_window}")
        print(f"FFT configured: source={source}, window={window}")

    def set_math_scale(self, math_ch: int, scale: float, offset: float = None) -> None:
        """
        Set vertical scale and offset for math channel.

        Args:
            math_ch: Math channel (ignored)
            scale: Vertical scale (V/div)
            offset: Vertical offset (optional)
        """
        self.instrument.write(f":FUNCtion:SCALe {scale}")
        if offset is not None:
            self.instrument.write(f":FUNCtion:OFFSet {offset}")
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
        self.instrument.write(f":MTESt:ENABle {state}")
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
        self.instrument.write(f":MTESt:SOURce CHANnel{channel}")
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
        self.instrument.write(f":MTESt:AMASk:XDELta {tol}")
        print(f"Mask horizontal tolerance: {tol}")

    def set_mask_tolerance_y(self, tol: float) -> None:
        """
        Set the vertical tolerance for the auto mask.

        Args:
            tol: Vertical tolerance in divisions
        """
        self.instrument.write(f":MTESt:AMASk:YDELta {tol}")
        print(f"Mask vertical tolerance: {tol}")

    def create_mask(self) -> None:
        """Create a mask from the current waveform using auto mask."""
        self.instrument.write(":MTESt:AMASk:CREate")
        print("Mask created from current waveform")

    def start_mask_test(self) -> None:
        """Start the mask test."""
        self.instrument.write(":MTESt:ENABle ON")
        print("Mask test started")

    def stop_mask_test(self) -> None:
        """Stop the mask test."""
        self.instrument.write(":MTESt:ENABle OFF")
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
        """Reset the mask test statistics counters."""
        self.instrument.write(":MTESt:COUNt:RESet")
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
    # System Commands
    # ========================================

    def reset(self) -> None:
        """Reset oscilloscope to factory default settings."""
        self.instrument.write("*RST")
        self.instrument.write("*CLS")
        print("Oscilloscope reset to factory defaults")

    def clear_status(self) -> None:
        """Clear status byte and error queue."""
        self.instrument.write("*CLS")
        print("Status cleared")

    def get_error(self) -> str:
        """
        Read the most recent error from the system error queue.

        Returns:
            str: Error message string
        """
        response = self.instrument.query(":SYSTem:ERRor?")
        return response.strip()
