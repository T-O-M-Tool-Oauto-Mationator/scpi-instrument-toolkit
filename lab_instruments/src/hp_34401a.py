# HP 34401A
"""
Driver for HP/Agilent 34401A Digital Multimeter.
Instrument Type: Digital Multimeter (DMM)

Command Syntax Conventions (from HP 34401A Programming Reference):
    Square Brackets [ ]: Indicate optional keywords or parameters.
    Braces { }: Enclose parameters within a command string.
    Triangle Brackets < >: Indicate that you must substitute a value for the enclosed parameter.
    Vertical Bar |: Separates one of two or more alternative parameters.
"""

import time

from .device_manager import DeviceManager


class HP_34401A(DeviceManager):
    """
    Driver for HP/Agilent 34401A Digital Multimeter.

    Based on HP 34401A User's Guide (34401-90004).
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
    }

    # Modes that do NOT accept range/resolution parameters
    _NO_PARAM_MODES = {"CONT", "DIOD", "CONTinuity", "DIODe"}

    # Valid NPLC values: 0.02, 0.2, 1, 10, 100 (or MIN, MAX, DEF)
    _VALID_NPLC = {0.02, 0.2, 1, 10, 100}

    def __init__(self, resource_name):
        """Initialize the HP 34401A DMM."""
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

    def configure_dc_voltage(self, range_val="DEF", resolution="DEF", nplc=None):
        """
        Configures the multimeter for DC Voltage measurement.

        Args:
            range_val (str|float): Measurement range in Volts.
                Valid: 0.1, 1, 10, 100, 1000 (or MIN, MAX, DEF, AUTO).
            resolution (str|float): Resolution of the measurement.
                Specify in same units as range (e.g., 0.0001 for 100µV on 10V range).
            nplc (float): Integration time in Number of Power Line Cycles.
                Valid: 0.02, 0.2, 1, 10, 100 (or MIN, MAX, DEF).
                Higher NPLC = better noise rejection but slower.
        """
        self.send_command(f"CONFigure:VOLTage:DC {range_val},{resolution}")
        if nplc is not None:
            self.send_command(f"SENSe:VOLTage:DC:NPLCycles {nplc}")

    def configure_ac_voltage(self, range_val="DEF", resolution="DEF"):
        """
        Configures the multimeter for AC Voltage measurement.

        Args:
            range_val (str|float): Measurement range in Volts.
                Valid: 0.1, 1, 10, 100, 750 (or MIN, MAX, DEF, AUTO).
            resolution (str|float): Resolution of the measurement.
        """
        self.send_command(f"CONFigure:VOLTage:AC {range_val},{resolution}")

    def configure_dc_current(self, range_val="DEF", resolution="DEF", nplc=None):
        """
        Configures the multimeter for DC Current measurement.

        Args:
            range_val (str|float): Measurement range in Amps.
                Valid: 0.01, 0.1, 1, 3 (or MIN, MAX, DEF, AUTO).
            resolution (str|float): Resolution of the measurement.
            nplc (float): Integration time in Number of Power Line Cycles.
        """
        self.send_command(f"CONFigure:CURRent:DC {range_val},{resolution}")
        if nplc is not None:
            self.send_command(f"SENSe:CURRent:DC:NPLCycles {nplc}")

    def configure_ac_current(self, range_val="DEF", resolution="DEF"):
        """
        Configures the multimeter for AC Current measurement.

        Args:
            range_val (str|float): Measurement range in Amps.
                Valid: 0.01, 0.1, 1, 3 (or MIN, MAX, DEF, AUTO).
            resolution (str|float): Resolution of the measurement.
        """
        self.send_command(f"CONFigure:CURRent:AC {range_val},{resolution}")

    def configure_resistance_2wire(self, range_val="DEF", resolution="DEF", nplc=None):
        """
        Configures the multimeter for 2-wire resistance measurement.

        Args:
            range_val (str|float): Measurement range in Ohms.
                Valid: 100, 1e3, 10e3, 100e3, 1e6, 10e6, 100e6 (or MIN, MAX, DEF, AUTO).
            resolution (str|float): Resolution of the measurement.
            nplc (float): Integration time in Number of Power Line Cycles.
        """
        self.send_command(f"CONFigure:RESistance {range_val},{resolution}")
        if nplc is not None:
            self.send_command(f"SENSe:RESistance:NPLCycles {nplc}")

    def configure_resistance_4wire(self, range_val="DEF", resolution="DEF", nplc=None):
        """
        Configures the multimeter for 4-wire resistance measurement (Kelvin).

        Args:
            range_val (str|float): Measurement range in Ohms.
                Valid: 100, 1e3, 10e3, 100e3, 1e6, 10e6, 100e6 (or MIN, MAX, DEF, AUTO).
            resolution (str|float): Resolution of the measurement.
            nplc (float): Integration time in Number of Power Line Cycles.
        """
        self.send_command(f"CONFigure:FRESistance {range_val},{resolution}")
        if nplc is not None:
            self.send_command(f"SENSe:FRESistance:NPLCycles {nplc}")

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
            if ',' in result_str:
                values = [float(val.strip()) for val in result_str.split(',')]
                return sum(values) / len(values)
            
            # Handle single reading (possibly with units or whitespace)
            value_str = result_str.strip().split()[0]
            return float(value_str)
        except (ValueError, IndexError) as e:
            raise ValueError(f"Failed to convert DMM response '{result_str}' to float: {e}")

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
            if ',' in result_str:
                values = [float(val.strip()) for val in result_str.split(',')]
                return sum(values) / len(values)
            
            # Handle single reading (possibly with units or whitespace)
            value_str = result_str.strip().split()[0]
            return float(value_str)
        except (ValueError, IndexError) as e:
            raise ValueError(f"Failed to convert DMM response '{result_str}' to float: {e}")

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
            raise ValueError(f"Failed to convert continuity response '{result_str}' to float: {e}")

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
            raise ValueError(f"Failed to convert diode response '{result_str}' to float: {e}")

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
            raise ValueError(f"Failed to convert measurement response '{result_str}' to float: {e}")

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

    def set_trigger_count(self, count=1):
        """
        Sets the number of triggers to accept.

        Args:
            count (int): Number of triggers (1 to 50000) or INF for infinite.
        """
        self.send_command(f"TRIGger:COUNt {count}")

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

    def display_text_rolling(
        self,
        text: str,
        width: int = 12,
        delay: float = 0.2,
        pad: int = 4,
        loops: int = 1,
    ):
        """
        Scroll text across the front panel if it exceeds the display width.

        Args:
            text (str): Text to display.
            width (int): Display width in characters (default 12).
            delay (float): Delay between frames in seconds.
            pad (int): Number of spaces appended between loops.
            loops (int): Number of times to scroll.
        """
        text = str(text)
        if width <= 0:
            raise ValueError("width must be > 0")
        if loops <= 0:
            loops = 1
        if len(text) <= width:
            self.display_text(text)
            return

        spacer = " " * max(1, pad)
        window_text = text + spacer
        cycle_text = window_text + window_text
        frame_count = len(window_text)
        for _ in range(loops):
            for start in range(frame_count):
                frame = cycle_text[start : start + width]
                self.send_command(f'DISPlay:TEXT "{frame}"')
                time.sleep(delay)

    def clear_display_text(self):
        """Clear custom text and return to normal display."""
        self.send_command("DISPlay:TEXT:CLEar")

    def display_text_scroll(
        self,
        text: str,
        delay: float = 0.2,
        pad: int = 4,
        width: int = 12,
        loops: int = 1,
    ):
        """Scroll text across the display (matches the repl.py call signature).

        Delegates to display_text_rolling with arguments reordered to match
        how repl.py invokes: display_text_scroll(message, delay, pad, width, loops).
        """
        self.display_text_rolling(text, width=width, delay=delay, pad=pad, loops=loops)

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
