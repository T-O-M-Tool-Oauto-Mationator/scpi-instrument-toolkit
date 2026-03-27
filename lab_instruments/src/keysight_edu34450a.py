# Keysight EDU34450A
"""
Driver for Keysight EDU34450A 5 1/2 Digit Digital Multimeter.
Instrument Type: Digital Multimeter (DMM)

Command Syntax Conventions (from Keysight EDU34450A Programming Reference):
    Square Brackets [ ]: Indicate optional keywords or parameters.
    Braces { }: Enclose parameters within a command string.
    Triangle Brackets < >: Indicate that you must substitute a value for the enclosed parameter.
    Vertical Bar |: Separates one of two or more alternative parameters.

NOTE: This instrument does NOT support NPLC (Number of Power Line Cycles).
      It uses resolution speed (SLOW/MEDIUM/FAST) instead.
      It supports capacitance and temperature modes unlike the HP 34401A.
"""


from .device_manager import DeviceManager


class Keysight_EDU34450A(DeviceManager):
    """
    Driver for Keysight EDU34450A 5 1/2 Digit Digital Multimeter.

    Based on Keysight EDU34450A User's Guide.
    USB + LAN interface. 11 measurement functions.
    No NPLC support -- uses resolution speed (SLOW/MEDIUM/FAST) instead.
    """

    # Valid SCPI measurement functions
    _VALID_MODES = {
        "VOLTage:DC",
        "VOLTage:AC",
        "CURRent:DC",
        "CURRent:AC",
        "RESistance",
        "FRESistance",
        "FREQuency",
        "PERiod",
        "CONTinuity",
        "DIODe",
        "CAPacitance",
        "TEMPerature",
    }

    # Short form modes for command construction
    _MODE_SHORT = {
        "VOLT:DC": "VOLTage:DC",
        "VOLT:AC": "VOLTage:AC",
        "CURR:DC": "CURRent:DC",
        "CURR:AC": "CURRent:AC",
        "RES": "RESistance",
        "FRES": "FRESistance",
        "FREQ": "FREQuency",
        "PER": "PERiod",
        "CONT": "CONTinuity",
        "DIOD": "DIODe",
        "CAP": "CAPacitance",
        "TEMP": "TEMPerature",
    }

    # Modes that do NOT accept range/resolution parameters
    _NO_PARAM_MODES = {"CONT", "DIOD", "CONTinuity", "DIODe", "TEMP", "TEMPerature"}

    def __init__(self, resource_name):
        """Initialize the Keysight EDU34450A DMM."""
        super().__init__(resource_name)

    def __enter__(self):
        """Context manager entry: clear status."""
        self.clear_status()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Context manager exit: reset to known state."""
        self.reset()

    # ==========================================
    # CONFIGURATION METHODS
    # ==========================================

    def configure_dc_voltage(self, range_val="DEF", resolution="DEF"):
        """
        Configures the multimeter for DC Voltage measurement.

        Args:
            range_val (str|float): Measurement range in Volts.
                Valid: 0.1, 1, 10, 100, 1000 (or MIN, MAX, DEF, AUTO).
            resolution (str|float): Resolution of the measurement.
                Specify in same units as range (e.g., 0.0001 for 100uV on 10V range).
        """
        self.send_command(f"CONFigure:VOLTage:DC {range_val},{resolution}")

    def configure_ac_voltage(self, range_val="DEF", resolution="DEF"):
        """
        Configures the multimeter for AC Voltage measurement.

        Args:
            range_val (str|float): Measurement range in Volts.
                Valid: 0.1, 1, 10, 100, 750 (or MIN, MAX, DEF, AUTO).
            resolution (str|float): Resolution of the measurement.
        """
        self.send_command(f"CONFigure:VOLTage:AC {range_val},{resolution}")

    def configure_dc_current(self, range_val="DEF", resolution="DEF"):
        """
        Configures the multimeter for DC Current measurement.

        Args:
            range_val (str|float): Measurement range in Amps.
                Valid: 0.001, 0.01, 0.1, 1, 10 (or MIN, MAX, DEF, AUTO).
            resolution (str|float): Resolution of the measurement.
        """
        self.send_command(f"CONFigure:CURRent:DC {range_val},{resolution}")

    def configure_ac_current(self, range_val="DEF", resolution="DEF"):
        """
        Configures the multimeter for AC Current measurement.

        Args:
            range_val (str|float): Measurement range in Amps.
                Valid: 0.001, 0.01, 0.1, 1, 10 (or MIN, MAX, DEF, AUTO).
            resolution (str|float): Resolution of the measurement.
        """
        self.send_command(f"CONFigure:CURRent:AC {range_val},{resolution}")

    def configure_resistance_2wire(self, range_val="DEF", resolution="DEF"):
        """
        Configures the multimeter for 2-wire resistance measurement.

        Args:
            range_val (str|float): Measurement range in Ohms.
                Valid: 100, 1e3, 10e3, 100e3, 1e6, 10e6, 100e6 (or MIN, MAX, DEF, AUTO).
            resolution (str|float): Resolution of the measurement.
        """
        self.send_command(f"CONFigure:RESistance {range_val},{resolution}")

    def configure_resistance_4wire(self, range_val="DEF", resolution="DEF"):
        """
        Configures the multimeter for 4-wire resistance measurement (Kelvin).

        Args:
            range_val (str|float): Measurement range in Ohms.
                Valid: 100, 1e3, 10e3, 100e3, 1e6, 10e6, 100e6 (or MIN, MAX, DEF, AUTO).
            resolution (str|float): Resolution of the measurement.
        """
        self.send_command(f"CONFigure:FRESistance {range_val},{resolution}")

    def configure_frequency(self, range_val="DEF", resolution="DEF"):
        """
        Configures the multimeter for Frequency measurement.

        Args:
            range_val (str|float): Expected input voltage range in Volts.
                Valid: 0.1, 1, 10, 100, 750 (or MIN, MAX, DEF, AUTO).
            resolution (str|float): Resolution in Hz.
        """
        self.send_command(f"CONFigure:FREQuency {range_val},{resolution}")

    def configure_period(self, range_val="DEF", resolution="DEF"):
        """
        Configures the multimeter for Period measurement.

        Args:
            range_val (str|float): Expected input voltage range in Volts.
                Valid: 0.1, 1, 10, 100, 750 (or MIN, MAX, DEF, AUTO).
            resolution (str|float): Resolution in seconds.
        """
        self.send_command(f"CONFigure:PERiod {range_val},{resolution}")

    def configure_continuity(self):
        """
        Configures the multimeter for Continuity test.
        Range is fixed at 1 kOhm. Beeper sounds if <10 Ohms.
        """
        self.send_command("CONFigure:CONTinuity")

    def configure_diode(self):
        """
        Configures the multimeter for Diode test.
        Uses 1mA test current. Range is fixed at 1 Vdc.
        """
        self.send_command("CONFigure:DIODe")

    def configure_capacitance(self, range_val="DEF"):
        """
        Configures the multimeter for Capacitance measurement.

        Args:
            range_val (str|float): Measurement range in Farads.
                Valid: 1e-9, 10e-9, 100e-9, 1e-6, 10e-6, 100e-6, 1e-3, 10e-3
                (or MIN, MAX, DEF, AUTO).
        """
        self.send_command(f"CONFigure:CAPacitance {range_val}")

    def configure_temperature(self):
        """
        Configures the multimeter for Temperature measurement.
        Uses the configured temperature sensor type (thermocouple or RTD).
        """
        self.send_command("CONFigure:TEMPerature")

    # ==========================================
    # MODE SELECTION
    # ==========================================

    def set_mode(self, mode: str):
        """
        Set the measurement mode using a friendly name.

        Args:
            mode (str): Friendly mode name (case-insensitive).
                Valid: vdc, dc_voltage, vac, ac_voltage, idc, dc_current,
                       iac, ac_current, res, resistance_2wire, fres,
                       resistance_4wire, freq, frequency, per, period,
                       cont, continuity, diode, cap, capacitance,
                       temp, temperature.
        """
        mode_map = {
            "vdc": self.configure_dc_voltage,
            "dc_voltage": self.configure_dc_voltage,
            "vac": self.configure_ac_voltage,
            "ac_voltage": self.configure_ac_voltage,
            "idc": self.configure_dc_current,
            "dc_current": self.configure_dc_current,
            "iac": self.configure_ac_current,
            "ac_current": self.configure_ac_current,
            "res": self.configure_resistance_2wire,
            "resistance_2wire": self.configure_resistance_2wire,
            "fres": self.configure_resistance_4wire,
            "resistance_4wire": self.configure_resistance_4wire,
            "freq": self.configure_frequency,
            "frequency": self.configure_frequency,
            "per": self.configure_period,
            "period": self.configure_period,
            "cont": self.configure_continuity,
            "continuity": self.configure_continuity,
            "diode": self.configure_diode,
            "cap": self.configure_capacitance,
            "capacitance": self.configure_capacitance,
            "temp": self.configure_temperature,
            "temperature": self.configure_temperature,
        }
        if mode.lower() not in mode_map:
            raise ValueError(f"Unknown mode: {mode}. Valid: {list(mode_map.keys())}")
        mode_map[mode.lower()]()

    # ==========================================
    # READING METHODS
    # ==========================================

    def read(self):
        """
        Initiates a measurement and returns the result.
        Use after calling a configure_* method.

        If multiple samples are configured, returns the average of all samples.

        Returns:
            float: The measured value (or average if multiple samples).
        """
        result_str = self.query("READ?")
        try:
            # Handle comma-separated multiple readings (when SAMPle:COUNt > 1)
            if "," in result_str:
                values = [float(val.strip()) for val in result_str.split(",")]
                return sum(values) / len(values)

            # Handle single reading (possibly with units or whitespace)
            value_str = result_str.strip().split()[0]
            return float(value_str)
        except (ValueError, IndexError) as e:
            raise ValueError(f"Failed to convert DMM response '{result_str}' to float: {e}") from e

    def fetch(self):
        """
        Returns the last measurement taken without triggering a new one.

        If multiple samples were configured, returns the average of all samples.

        Returns:
            float: The last measured value (or average if multiple samples).
        """
        result_str = self.query("FETCh?")
        try:
            # Handle comma-separated multiple readings (when SAMPle:COUNt > 1)
            if "," in result_str:
                values = [float(val.strip()) for val in result_str.split(",")]
                return sum(values) / len(values)

            # Handle single reading (possibly with units or whitespace)
            value_str = result_str.strip().split()[0]
            return float(value_str)
        except (ValueError, IndexError) as e:
            raise ValueError(f"Failed to convert DMM response '{result_str}' to float: {e}") from e

    # ==========================================
    # IMMEDIATE MEASUREMENT METHODS (MEASure?)
    # ==========================================

    def measure_dc_voltage(self, range_val="DEF", resolution="DEF"):
        """Measures DC Voltage. Configures, triggers, and returns result."""
        return self._measure("VOLTage:DC", range_val, resolution)

    def measure_ac_voltage(self, range_val="DEF", resolution="DEF"):
        """Measures AC Voltage. Configures, triggers, and returns result."""
        return self._measure("VOLTage:AC", range_val, resolution)

    def measure_dc_current(self, range_val="DEF", resolution="DEF"):
        """Measures DC Current. Configures, triggers, and returns result."""
        return self._measure("CURRent:DC", range_val, resolution)

    def measure_ac_current(self, range_val="DEF", resolution="DEF"):
        """Measures AC Current. Configures, triggers, and returns result."""
        return self._measure("CURRent:AC", range_val, resolution)

    def measure_resistance_2wire(self, range_val="DEF", resolution="DEF"):
        """Measures 2-Wire Resistance. Configures, triggers, and returns result."""
        return self._measure("RESistance", range_val, resolution)

    def measure_resistance_4wire(self, range_val="DEF", resolution="DEF"):
        """Measures 4-Wire Resistance. Configures, triggers, and returns result."""
        return self._measure("FRESistance", range_val, resolution)

    def measure_frequency(self, range_val="DEF", resolution="DEF"):
        """Measures Frequency. Range specifies expected input voltage."""
        return self._measure("FREQuency", range_val, resolution)

    def measure_period(self, range_val="DEF", resolution="DEF"):
        """Measures Period. Range specifies expected input voltage."""
        return self._measure("PERiod", range_val, resolution)

    def measure_continuity(self):
        """
        Tests Continuity. Range fixed at 1 kOhm.

        Returns:
            float: Resistance reading in Ohms.
        """
        result_str = self.query("MEASure:CONTinuity?")
        try:
            value_str = result_str.strip().split()[0]
            return float(value_str)
        except (ValueError, IndexError) as e:
            raise ValueError(f"Failed to convert continuity response '{result_str}' to float: {e}") from e

    def measure_diode(self):
        """
        Tests Diode. Uses 1mA test current, range fixed at 1 Vdc.

        Returns:
            float: Forward voltage reading in Volts.
        """
        result_str = self.query("MEASure:DIODe?")
        try:
            value_str = result_str.strip().split()[0]
            return float(value_str)
        except (ValueError, IndexError) as e:
            raise ValueError(f"Failed to convert diode response '{result_str}' to float: {e}") from e

    def measure_capacitance(self, range_val="DEF"):
        """
        Measures Capacitance. Configures, triggers, and returns result.

        Args:
            range_val (str|float): Measurement range in Farads.

        Returns:
            float: The measured capacitance value.
        """
        cmd = f"MEASure:CAPacitance? {range_val}"
        result_str = self.query(cmd)
        try:
            value_str = result_str.strip().split()[0]
            return float(value_str)
        except (ValueError, IndexError) as e:
            raise ValueError(f"Failed to convert capacitance response '{result_str}' to float: {e}") from e

    def measure_temperature(self):
        """
        Measures Temperature. Configures, triggers, and returns result.

        Returns:
            float: The measured temperature value.
        """
        result_str = self.query("MEASure:TEMPerature?")
        try:
            value_str = result_str.strip().split()[0]
            return float(value_str)
        except (ValueError, IndexError) as e:
            raise ValueError(f"Failed to convert temperature response '{result_str}' to float: {e}") from e

    def _measure(self, function, range_val="DEF", resolution="DEF"):
        """
        Internal helper for MEASure? commands.

        Args:
            function (str): Measurement function (e.g., 'VOLTage:DC').
            range_val: Measurement range.
            resolution: Measurement resolution.

        Returns:
            float: The measured value.
        """
        cmd = f"MEASure:{function}? {range_val},{resolution}"
        result_str = self.query(cmd)
        try:
            value_str = result_str.strip().split()[0]
            return float(value_str)
        except (ValueError, IndexError) as e:
            raise ValueError(f"Failed to convert measurement response '{result_str}' to float: {e}") from e

    # ==========================================
    # TRIGGER CONFIGURATION
    # ==========================================

    def set_trigger_source(self, source="IMM"):
        """
        Sets the trigger source.

        Args:
            source (str): Trigger source.
                IMMediate - Triggers immediately.
                BUS - Triggers on *TRG or Group Execute Trigger.
                EXTernal - Triggers on external trigger input.
        """
        valid_sources = {"IMM", "IMMEDIATE", "BUS", "EXT", "EXTERNAL"}
        if source.upper() not in valid_sources:
            raise ValueError(f"Invalid trigger source. Must be one of: {valid_sources}")
        self.send_command(f"TRIGger:SOURce {source}")

    def set_trigger_delay(self, delay="MIN"):
        """
        Sets the trigger delay.

        Args:
            delay (str|float): Delay in seconds (0 to 3600) or MIN, MAX, DEF.
        """
        self.send_command(f"TRIGger:DELay {delay}")

    def set_sample_count(self, count=1):
        """
        Sets the number of samples per trigger.

        Args:
            count (int): Number of samples (1 to 50000).
        """
        self.send_command(f"SAMPle:COUNt {count}")

    def trigger(self):
        """Sends a software trigger (when trigger source is BUS)."""
        self.send_command("*TRG")

    def init(self):
        """
        Changes the DMM from idle to wait-for-trigger state.
        Use this before sending a trigger when in BUS trigger mode.
        """
        self.send_command("INITiate")

    # ==========================================
    # SYSTEM & UTILITY
    # ==========================================

    def get_error(self):
        """
        Reads the most recent error from the error queue.

        Returns:
            str: Error code and message (e.g., '+0,"No error"').
        """
        return self.query("SYSTem:ERRor?")

    def set_display(self, enabled: bool = True):
        """
        Enable or disable the front panel display.
        Disabling can slightly improve measurement speed.

        Args:
            enabled (bool): True to enable, False to disable.
        """
        state = "ON" if enabled else "OFF"
        self.send_command(f"DISPlay {state}")

    def display_text(self, text: str):
        """
        Display custom text on the front panel (max 12 chars).

        Args:
            text (str): Text to display (up to 12 characters).
        """
        # Truncate to 12 characters
        text = text[:12]
        self.send_command(f'DISPlay:TEXT "{text}"')

    def clear_display_text(self):
        """Clear custom text and return to normal display."""
        self.send_command("DISPlay:TEXT:CLEar")

    def clear_display(self):
        """Clear custom text and return to normal display (alias for clear_display_text)."""
        self.clear_display_text()

    def set_beeper(self, enabled: bool = True):
        """
        Enable or disable the beeper.

        Args:
            enabled (bool): True to enable, False to disable.
        """
        state = "ON" if enabled else "OFF"
        self.send_command(f"SYSTem:BEEPer:STATe {state}")

    def beep(self):
        """Sound the beeper once."""
        self.send_command("SYSTem:BEEPer")
