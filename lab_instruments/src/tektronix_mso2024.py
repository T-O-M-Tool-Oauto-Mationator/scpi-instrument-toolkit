# Tektronix MSO2024 (Legacy MSO2000 Series)
"""
Driver for the Tektronix MSO2000 Series Oscilloscope.
Instrument Type: Mixed Signal Oscilloscope (MSO)
"""

from .device_manager import DeviceManager


class Tektronix_MSO2024(DeviceManager):
    """
    Driver for Tektronix MSO2000 Series (Legacy).

    Model: MSO2024
    Firmware: v1.56 (Verified Legacy)
    """

    # BNF: MEASUrement:IMMed:TYPe { <type> }
    # Standard measurement types for MSO/DPO2000 Series
    VALID_BNF_MEASURE_TYPES = {
        "FREQUENCY",
        "MEAN",
        "PERIOD",
        "PK2PK",
        "CRMS",
        "MINIMUM",
        "MAXIMUM",
        "RISE",
        "FALL",
        "PWIDTH",
        "NWIDTH",
        "RMS",
        "AMPLITUDE",
        "HIGH",
        "LOW",
        "POSOVERSHOOT",
        "NEGOVERSHOOT",
        "DELAY",
    }

    # Channel Mapping
    CHANNEL_MAP = {
        1: "CH1",
        2: "CH2",
        3: "CH3",
        4: "CH4",
    }

    # Enum ALLOWLISTs (Rule 6)
    _COUPLING_ALLOWLIST = ("DC", "AC", "GND")
    _ACQ_MODE_ALLOWLIST = ("SAMPLE", "AVERAGE", "PEAKDETECT", "HIRES", "ENVELOPE")
    _ACQ_STOP_ALLOWLIST = ("RUNSTOP", "SEQUENCE")
    _TRIGGER_SLOPE_ALLOWLIST = ("RISE", "FALL")
    _TRIGGER_MODE_ALLOWLIST = ("AUTO", "NORMAL")
    _DELAY_EDGE_ALLOWLIST = ("RISE", "FALL")
    _DELAY_DIRECTION_ALLOWLIST = ("FORWARDS", "BACKWARDS")

    def __init__(self, resource_name):
        """Initialize the Tektronix Oscilloscope."""
        super().__init__(resource_name)
        self._cache = {}

    def _write(self, cmd: str, **cache_updates) -> None:
        """Send a SCPI command and atomically update the cache."""
        self.send_command(cmd)
        if cache_updates:
            self._cache.update(cache_updates)

    def __enter__(self):
        """Context manager entry: clear status and reset channels."""
        self.clear_status()
        self.disable_all_channels()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Context manager exit: ensure safe state."""
        self.disable_all_channels()

    def get_error(self):
        """Reads the most recent error from the system error queue."""
        return self.query("SYSTem:ERRor?")

    def disable_all_channels(self):
        """Disable all channels (Analog + Math)."""
        # 1. Analog Channels
        for channel in self.CHANNEL_MAP:
            self.change_channel_status(channel, False)

        # 2. Math Channel
        self._write("SELect:MATH OFF", math_display=False)

    def enable_all_channels(self):
        """Enable all analog channels."""
        for channel in self.CHANNEL_MAP:
            self.change_channel_status(channel, True)

    def change_channel_status(self, channel, status: bool):
        """Enable or disable the specified channel."""
        if channel not in self.CHANNEL_MAP:
            raise ValueError(f"Invalid channel. Must be one of: {list(self.CHANNEL_MAP.keys())}")

        scpi_name = self.CHANNEL_MAP[channel]
        state = "ON" if status else "OFF"
        self._write(f"SELect:{scpi_name} {state}", **{f"ch{channel}_display": status})

    def enable_channel(self, channel):
        self.change_channel_status(channel, True)

    def disable_channel(self, channel):
        self.change_channel_status(channel, False)

    def set_channel_label(self, channel, label: str):
        """Sets the label for a specific channel (Max 30 chars)."""
        if channel not in self.CHANNEL_MAP:
            raise ValueError(f"Invalid channel. Must be one of: {list(self.CHANNEL_MAP.keys())}")

        scpi_name = self.CHANNEL_MAP[channel]
        self._write(f'{scpi_name}:LABel:NAMe "{label}"', **{f"ch{channel}_label": label})

    def set_probe_attenuation(self, channel, attenuation: float):
        """Sets the probe attenuation (Legacy MSO2000 uses PRObe:GAIN)."""
        if channel not in self.CHANNEL_MAP:
            raise ValueError(f"Invalid channel. Must be one of: {list(self.CHANNEL_MAP.keys())}")

        if attenuation <= 0:
            raise ValueError("Attenuation must be positive.")

        scpi_name = self.CHANNEL_MAP[channel]
        # Gain = 1 / Attenuation (e.g., 10x probe -> 0.1 gain)
        gain = 1.0 / attenuation
        self._write(f"{scpi_name}:PRObe:GAIN {gain}", **{f"ch{channel}_attenuation": attenuation})

    def set_coupling(self, channel, coupling: str):
        """
        Set channel input coupling.

        Args:
            channel (int): Channel number (1-4)
            coupling (str): 'DC', 'AC', or 'GND'
        """
        if channel not in self.CHANNEL_MAP:
            raise ValueError(f"Invalid channel. Must be one of: {list(self.CHANNEL_MAP.keys())}")

        coupling = coupling.upper()
        if coupling not in self._COUPLING_ALLOWLIST:
            raise ValueError(f"Coupling must be one of {self._COUPLING_ALLOWLIST}, got '{coupling}'")

        scpi_name = self.CHANNEL_MAP[channel]
        self._write(f"{scpi_name}:COUPling {coupling}", **{f"ch{channel}_coupling": coupling})
        print(f"{scpi_name} coupling: {coupling}")

    # ==========================================
    # HORIZONTAL & ACQUISITION
    # ==========================================

    def set_horizontal_scale(self, scale):
        """Set the horizontal scale (seconds per division)."""
        if scale <= 0:
            raise ValueError(f"Scale must be positive, got {scale}")
        self._write(f"HORizontal:SCAle {scale}", horizontal_scale=scale)

    def set_horizontal_offset(self, offset: float) -> None:
        """Set horizontal offset (time position) in seconds.

        Enables delay mode and sets the delay time so the trigger point
        is shifted by the given offset. Negative = earlier time visible;
        positive = later time visible; zero = trigger at center.
        """
        self._write("HORizontal:DELay:MODe ON", horizontal_delay_mode=True)
        self._write(f"HORizontal:DELay:TIMe {offset}", horizontal_offset=offset)

    def get_horizontal_offset(self) -> float:
        """Return the current horizontal delay time in seconds."""
        return float(self.query("HORizontal:DELay:TIMe?"))

    def set_horizontal_position(self, position: float):
        """
        Set the horizontal position (percentage 0-100).

        Args:
            position (float): Position as percentage (0-100)
        """
        if position < 0 or position > 100:
            raise ValueError(f"Position must be between 0 and 100, got {position}")
        self._write(f"HORizontal:POSition {position}", horizontal_position=position)

    def get_horizontal_position(self):
        """
        Get the current horizontal position.

        Returns:
            float: Position as percentage (0-100)
        """
        return float(self.query("HORizontal:POSition?"))

    def move_horizontal(self, delta: float):
        """
        Move the horizontal position by a delta amount.

        Args:
            delta (float): Amount to move in percentage (positive = right, negative = left)
        """
        current_pos = self.get_horizontal_position()
        new_pos = current_pos + delta
        # Clamp to valid range 0-100
        new_pos = max(0.0, min(100.0, new_pos))
        self.set_horizontal_position(new_pos)
        print(f"Horizontal position moved to: {new_pos:.2f}%")

    def set_acquisition_mode(self, mode: str, num_averages: int = 16):
        """
        Sets the acquisition mode.
        Legacy MSO2000 Supports: SAMPLE, AVERAGE, PEAKDETECT.
        (HIRES/ENVELOPE might be restricted on some older firmwares, but usually present).
        """
        if mode.upper() not in self._ACQ_MODE_ALLOWLIST:
            raise ValueError(f"Mode must be one of {self._ACQ_MODE_ALLOWLIST}, got '{mode}'")

        self._write(f"ACQuire:MODe {mode.upper()}", acquisition_mode=mode.upper())

        if mode.upper() == "AVERAGE":
            self._write(f"ACQuire:NUMAVg {num_averages}", acquisition_num_averages=num_averages)

    def run(self):
        """Start/resume acquisition (run the oscilloscope)."""
        self._write("ACQuire:STATE RUN", acquisition_state="RUN")
        print("Oscilloscope: Running")

    def stop(self):
        """Stop/pause acquisition (stop the oscilloscope)."""
        self._write("ACQuire:STATE STOP", acquisition_state="STOP")
        print("Oscilloscope: Stopped")

    def single(self):
        """
        Arm single-shot acquisition.
        The scope will wait for a trigger event, capture one acquisition, then stop.
        Perfect for capturing specific events.
        """
        self._write("ACQuire:STOPAfter SEQuence", acquisition_stop_after="SEQUENCE")
        self._write("ACQuire:STATE RUN", acquisition_state="RUN")
        print("Oscilloscope: Armed for single-shot (waiting for trigger)")

    def get_acquisition_state(self):
        """
        Get the current acquisition state.

        Returns:
            int: 1 if running, 0 if stopped
        """
        return int(self.query("ACQuire:STATE?"))

    def is_running(self):
        """
        Check if the oscilloscope is currently running.

        Returns:
            bool: True if running, False if stopped
        """
        return self.get_acquisition_state() == 1

    def set_acquisition_stop_after(self, mode: str):
        """
        Set when acquisition stops.

        Args:
            mode (str): 'RUNSTop' for continuous or 'SEQuence' for single-shot
        """
        mode = mode.upper()
        if mode not in self._ACQ_STOP_ALLOWLIST:
            raise ValueError(f"Mode must be one of {self._ACQ_STOP_ALLOWLIST}, got '{mode}'")
        self._write(f"ACQuire:STOPAfter {mode}", acquisition_stop_after=mode)

    # ==========================================
    # VERTICAL
    # ==========================================

    def set_vertical_scale(self, channel, scale, position=0.0):
        """Set the vertical scale (Volts/div) and position (divs)."""
        if channel not in self.CHANNEL_MAP:
            raise ValueError(f"Invalid channel. Must be one of: {list(self.CHANNEL_MAP.keys())}")
        if scale <= 0:
            raise ValueError(f"Scale must be positive, got {scale}")

        scpi_name = self.CHANNEL_MAP[channel]
        self._write(f"{scpi_name}:SCAle {scale}", **{f"ch{channel}_scale": scale})
        self._write(f"{scpi_name}:POSition {position}", **{f"ch{channel}_position": position})

    def set_vertical_position(self, channel, position: float):
        """
        Set the vertical position of a channel (in divisions from center).

        Args:
            channel (int): Channel number (1-4)
            position (float): Position in divisions (positive = up, negative = down)
        """
        if channel not in self.CHANNEL_MAP:
            raise ValueError(f"Invalid channel. Must be one of: {list(self.CHANNEL_MAP.keys())}")

        scpi_name = self.CHANNEL_MAP[channel]
        self._write(f"{scpi_name}:POSition {position}", **{f"ch{channel}_position": position})

    def get_vertical_position(self, channel):
        """
        Get the current vertical position of a channel.

        Args:
            channel (int): Channel number (1-4)

        Returns:
            float: Position in divisions
        """
        if channel not in self.CHANNEL_MAP:
            raise ValueError(f"Invalid channel. Must be one of: {list(self.CHANNEL_MAP.keys())}")

        scpi_name = self.CHANNEL_MAP[channel]
        return float(self.query(f"{scpi_name}:POSition?"))

    def move_vertical(self, channel, delta: float):
        """
        Move a channel vertically by a delta amount.

        Args:
            channel (int): Channel number (1-4)
            delta (float): Amount to move in divisions (positive = up, negative = down)
        """
        current_pos = self.get_vertical_position(channel)
        new_pos = current_pos + delta
        self.set_vertical_position(channel, new_pos)
        print(f"CH{channel} moved to vertical position: {new_pos:.2f} divs")

    # ==========================================
    # TRIGGER
    # ==========================================

    def configure_trigger(self, source_channel, level, slope="RISE", mode="AUTO"):
        """Configure the Edge Trigger parameters."""
        if source_channel not in self.CHANNEL_MAP:
            raise ValueError(f"Invalid channel. Must be one of: {list(self.CHANNEL_MAP.keys())}")
        slope = slope.upper()
        if slope not in self._TRIGGER_SLOPE_ALLOWLIST:
            raise ValueError(f"Slope must be one of {self._TRIGGER_SLOPE_ALLOWLIST}, got '{slope}'")
        mode = mode.upper()
        if mode not in self._TRIGGER_MODE_ALLOWLIST:
            raise ValueError(f"Mode must be one of {self._TRIGGER_MODE_ALLOWLIST}, got '{mode}'")

        scpi_source = self.CHANNEL_MAP[source_channel]

        self._write("TRIGger:A:TYPe EDGE", trigger_type="EDGE")
        self._write(f"TRIGger:A:EDGE:SOUrce {scpi_source}", trigger_source=source_channel)
        self._write(f"TRIGger:A:EDGE:SLOpe {slope}", trigger_slope=slope)
        self._write(f"TRIGger:A:LEVel:{scpi_source} {level}", trigger_level=level)
        self._write(f"TRIGger:A:MODe {mode}", trigger_mode=mode)

    # ==========================================
    # MATH SUBSYSTEM
    # ==========================================

    def configure_math(self, expression: str, scale: float = None, position: float = None):
        """Configures the Math waveform."""
        cache: dict = {"math_expression": expression}

        # Legacy MSO2000 uses MATH:DEFine
        self.send_command(f'MATH:DEFine "{expression}"')

        if scale is not None:
            self.send_command(f"MATH:VERTical:SCAle {scale}")
            cache["math_scale"] = scale

        if position is not None:
            self.send_command(f"MATH:VERTical:POSition {position}")
            cache["math_position"] = position

        self._write("SELect:MATH ON", **cache)

    def measure_math_bnf(self, measure_type):
        """
        Performs a measurement specifically on the Math waveform.
        Uses Legacy IMMed command (no badges).
        """
        m_type = measure_type.upper()
        if m_type not in self.VALID_BNF_MEASURE_TYPES:
            raise ValueError(f"Invalid BNF Type: {m_type}. Valid: {self.VALID_BNF_MEASURE_TYPES}")

        # 1. Set Source to MATH
        self.send_command("MEASUrement:IMMed:SOUrce1 MATH")

        # 2. Set Type
        self.send_command(f"MEASUrement:IMMed:TYPe {m_type}")

        # 3. Query Value
        try:
            return float(self.query("MEASUrement:IMMed:VALue?"))
        except (ValueError, TypeError):
            return float("nan")

    # ==========================================
    # STANDARD MEASUREMENTS
    # ==========================================

    def configure_measurement(self, channel: int, measurement_type: str) -> None:
        """Configure an immediate measurement without querying the result.

        Sets MEASUrement:IMMed:SOUrce1 and MEASUrement:IMMed:TYPe so the
        measurement is ready to query with measure_bnf() after a trigger.
        """
        if channel not in self.CHANNEL_MAP:
            raise ValueError(f"Invalid channel. Must be one of: {list(self.CHANNEL_MAP.keys())}")

        m_type = measurement_type.upper()
        if m_type not in self.VALID_BNF_MEASURE_TYPES:
            raise ValueError(f"Invalid BNF Type: {m_type}. Valid: {self.VALID_BNF_MEASURE_TYPES}")

        scpi_source = self.CHANNEL_MAP[channel]
        self._write(f"MEASUrement:IMMed:SOUrce1 {scpi_source}", meas_source=channel)
        self._write(f"MEASUrement:IMMed:TYPe {m_type}", meas_type=m_type)

    def measure_bnf(self, channel, measure_type):
        """
        Measure a basic measurement function (BNF) on the specified channel.
        Uses Legacy IMMed command (no badges).
        """
        if channel not in self.CHANNEL_MAP:
            raise ValueError(f"Invalid Channel: {channel}. Must be: {list(self.CHANNEL_MAP.keys())}")

        m_type = measure_type.upper()
        if m_type not in self.VALID_BNF_MEASURE_TYPES:
            raise ValueError(f"Invalid BNF Type: {m_type}. Valid: {self.VALID_BNF_MEASURE_TYPES}")

        scpi_source = self.CHANNEL_MAP[channel]

        # 1. Set Source
        self.send_command(f"MEASUrement:IMMed:SOUrce1 {scpi_source}")

        # 2. Set Type
        self.send_command(f"MEASUrement:IMMed:TYPe {m_type}")

        # 3. Query Value
        try:
            return float(self.query("MEASUrement:IMMed:VALue?"))
        except (ValueError, TypeError):
            return float("nan")

    def get_waveform_data(self, channel):
        """Fetch raw unscaled waveform data points from the scope."""
        if channel not in self.CHANNEL_MAP:
            raise ValueError("Invalid channel.")

        scpi_source = self.CHANNEL_MAP[channel]

        # 1. Select data source
        self.send_command(f"DATa:SOUrce {scpi_source}")

        # 2. Set encoding
        self.send_command("DATa:ENCdg ASCii")
        self.send_command("WFMOutpre:BYT_Nr 1")

        # 3. Request Curve
        raw_data = self.query("CURVe?")

        try:
            return [float(x) for x in raw_data.split(",")]
        except ValueError:
            return []

    # ==========================================
    # HELPERS & SHORTHANDS
    # ==========================================

    def get_waveform_scaled(self, channel):
        """
        Fetch waveform data and scale it to Time (s) and Voltage (V).

        Returns:
            tuple: (time_values, voltage_values)
        """
        if channel not in self.CHANNEL_MAP:
            raise ValueError(f"Invalid channel. Must be one of: {list(self.CHANNEL_MAP.keys())}")

        scpi_source = self.CHANNEL_MAP[channel]

        # 1. Setup Data Transfer
        self.send_command(f"DATa:SOUrce {scpi_source}")
        self.send_command("DATa:ENCdg ASCii")
        self.send_command("WFMOutpre:BYT_Nr 1")

        # 2. Get Scaling Preambles
        # Vertical scaling: Voltage = (Value - YOff) * YMult + YZero
        y_mult = float(self.query("WFMOutpre:YMUlt?"))
        y_off = float(self.query("WFMOutpre:YOff?"))
        y_zero = float(self.query("WFMOutpre:YZero?"))

        # Horizontal scaling: Time = XZero + (Index * XIncr)
        x_incr = float(self.query("WFMOutpre:XINcr?"))
        x_zero = float(self.query("WFMOutpre:XZero?"))

        # 3. Fetch Raw Data
        raw_curve = self.query("CURVe?")

        try:
            raw_data = [float(x) for x in raw_curve.split(",")]
        except ValueError:
            return [], []

        # 4. Apply Scaling
        voltage_values = [((val - y_off) * y_mult) + y_zero for val in raw_data]
        time_values = [x_zero + (i * x_incr) for i in range(len(raw_data))]

        return time_values, voltage_values

    def save_waveform_csv(self, channel, filename, max_points=None, time_window=None):
        """
        Saves the waveform of the specified channel to a CSV file.

        Args:
            channel (int or list): Channel to capture, or a list of channels.
            filename (str): Output filename (e.g., 'data.csv').
            max_points (int, optional): Maximum number of points to save. If None, saves all.
            time_window (float, optional): Time window in seconds to save. If None, saves all.
        """
        if isinstance(channel, (list, tuple)):
            return self.save_waveforms_csv(channel, filename, max_points=max_points, time_window=time_window)

        import csv

        times, volts = self.get_waveform_scaled(channel)

        if not times:
            print("No data captured.")
            return

        # Apply windowing if specified
        if time_window is not None:
            # Calculate sample rate
            dt = times[1] - times[0] if len(times) > 1 else 0
            if dt > 0:
                max_points = int(time_window / dt)

        if max_points is not None and max_points < len(times):
            # Take last max_points samples (most recent data)
            times = times[-max_points:]
            volts = volts[-max_points:]
            actual_time = times[-1] - times[0]
            print(f"Saving {max_points} points ({actual_time:.6f} seconds) - most recent data")

        with open(filename, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Time (s)", f"Channel {channel} Voltage (V)"])
            for t, v in zip(times, volts, strict=True):
                writer.writerow([t, v])
        print(f"Waveform from Channel {channel} saved to {filename}")

    def save_waveforms_csv(self, channels, filename, max_points=None, time_window=None):
        """
        Saves waveforms from multiple channels to a single CSV file.

        Args:
            channels (list): List of channel numbers to capture (e.g., [1, 3]).
            filename (str): Output filename (e.g., 'data.csv').
            max_points (int, optional): Maximum number of points to save. If None, saves all.
            time_window (float, optional): Time window in seconds to save. If None, saves all.
        """
        import csv

        # Fetch data from all channels
        channel_data = {}
        times = None
        for channel in channels:
            if channel not in self.CHANNEL_MAP:
                raise ValueError(f"Invalid channel {channel}. Must be one of: {list(self.CHANNEL_MAP.keys())}")

            t, v = self.get_waveform_scaled(channel)
            if not t:
                print(f"No data captured from Channel {channel}.")
                continue

            channel_data[channel] = v
            if times is None:
                times = t  # Use time base from first valid channel

        if not channel_data:
            print("No data captured from any channel.")
            return

        # Apply windowing if specified
        if time_window is not None:
            # Calculate sample rate
            dt = times[1] - times[0] if len(times) > 1 else 0
            if dt > 0:
                max_points = int(time_window / dt)

        if max_points is not None and max_points < len(times):
            # Trim all data to last max_points (most recent data)
            times = times[-max_points:]
            for ch in channel_data:
                channel_data[ch] = channel_data[ch][-max_points:]
            actual_time = times[-1] - times[0]
            print(f"Saving {max_points} points ({actual_time:.6f} seconds) - most recent data")

        # Write CSV
        with open(filename, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)

            # Header row
            header = ["Time (s)"] + [f"CH{ch} Voltage (V)" for ch in sorted(channel_data.keys())]
            writer.writerow(header)

            # Data rows
            for i, t in enumerate(times):
                row = [t]
                for ch in sorted(channel_data.keys()):
                    row.append(channel_data[ch][i] if i < len(channel_data[ch]) else "")
                writer.writerow(row)

        channels_str = ",".join(str(ch) for ch in sorted(channels))
        print(f"Waveforms from channels {channels_str} saved to {filename}")

    # Measurement Shorthands
    def measure_peak_to_peak(self, channel):
        """Helper: Measure Peak-to-Peak voltage."""
        return self.measure_bnf(channel, "PK2PK")

    def measure_frequency(self, channel):
        """Helper: Measure Frequency."""
        return self.measure_bnf(channel, "FREQUENCY")

    def measure_rms(self, channel):
        """Helper: Measure RMS voltage."""
        return self.measure_bnf(channel, "RMS")

    def measure_mean(self, channel):
        """Helper: Measure Mean voltage."""
        return self.measure_bnf(channel, "MEAN")

    def measure_max(self, channel):
        """Helper: Measure Maximum voltage."""
        return self.measure_bnf(channel, "MAXIMUM")

    def measure_min(self, channel):
        """Helper: Measure Minimum voltage."""
        return self.measure_bnf(channel, "MINIMUM")

    def measure_period(self, channel):
        """Helper: Measure Period."""
        return self.measure_bnf(channel, "PERIOD")

    def measure_delay(self, source1_channel, source2_channel, edge1="RISE", edge2="RISE", direction="FORWARDS"):
        """
        Measure the time delay between two channels.

        Args:
            source1_channel (int): The starting channel.
            source2_channel (int): The ending channel.
            edge1 (str): 'RISE' or 'FALL' for the first source.
            edge2 (str): 'RISE' or 'FALL' for the second source.
            direction (str): 'FORWARDS' or 'BACKWARDS' (default: FORWARDS)
        """
        if source1_channel not in self.CHANNEL_MAP or source2_channel not in self.CHANNEL_MAP:
            raise ValueError(f"Invalid channel. Must be one of: {list(self.CHANNEL_MAP.keys())}")
        edge1 = edge1.upper()
        if edge1 not in self._DELAY_EDGE_ALLOWLIST:
            raise ValueError(f"edge1 must be one of {self._DELAY_EDGE_ALLOWLIST}, got '{edge1}'")
        edge2 = edge2.upper()
        if edge2 not in self._DELAY_EDGE_ALLOWLIST:
            raise ValueError(f"edge2 must be one of {self._DELAY_EDGE_ALLOWLIST}, got '{edge2}'")
        direction = direction.upper()
        if direction not in self._DELAY_DIRECTION_ALLOWLIST:
            raise ValueError(f"direction must be one of {self._DELAY_DIRECTION_ALLOWLIST}, got '{direction}'")

        scpi_source1 = self.CHANNEL_MAP[source1_channel]
        scpi_source2 = self.CHANNEL_MAP[source2_channel]

        # 1. Set Type to DELAY
        self._write("MEASUrement:IMMed:TYPe DELAY", meas_type="DELAY")

        # 2. Set Sources
        self._write(f"MEASUrement:IMMed:SOUrce1 {scpi_source1}", delay_source1=source1_channel)
        self._write(f"MEASUrement:IMMed:SOUrce2 {scpi_source2}", delay_source2=source2_channel)

        # 3. Configure Edges and Direction
        self._write(f"MEASUrement:IMMed:DELay:EDGE1 {edge1}", delay_edge1=edge1)
        self._write(f"MEASUrement:IMMed:DELay:EDGE2 {edge2}", delay_edge2=edge2)
        self._write(f"MEASUrement:IMMed:DELay:DIRection {direction}", delay_direction=direction)

        # 4. Query Value
        try:
            return float(self.query("MEASUrement:IMMed:VALue?"))
        except (ValueError, TypeError):
            return float("nan")

    def measure_rise_time(self, channel):
        """Helper: Measure Rise Time."""
        return self.measure_bnf(channel, "RISE")

    def measure_fall_time(self, channel):
        """Helper: Measure Fall Time."""
        return self.measure_bnf(channel, "FALL")

    def autoset(self):
        """Perform an autoset on the oscilloscope."""
        self._write("AUToset EXECute", autoset=True)
