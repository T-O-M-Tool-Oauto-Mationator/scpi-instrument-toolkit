"""
Driver for Owon XDM1041 Digital Multimeter
Instrument Type: 7½-digit bench DMM

NOTE: This device uses non-standard SCPI syntax:
- Configuration uses standard SCPI (:CONFigure:VOLTage:DC, etc.)
- Measurement uses simplified syntax (MEAS? instead of :READ?)
"""

from .device_manager import DeviceManager
import pyvisa


class Owon_XDM1041(DeviceManager):
    """
    Driver for Owon XDM1041 7½-digit Digital Multimeter.

    Features:
    - DC/AC Voltage measurement (up to 1000V)
    - DC/AC Current measurement (up to 10A)
    - 2-wire and 4-wire resistance
    - Frequency, capacitance, temperature
    - 7½ digits resolution

    IMPORTANT: Uses non-standard measurement syntax (MEAS? instead of :READ?)
    """

    def __init__(self, resource_name):
        """Initialize the Owon XDM1041 DMM."""
        super().__init__(resource_name)

    def connect(self):
        """Override to set serial communication parameters."""
        try:
            self.instrument = self.rm.open_resource(self.resource_name)
            self.instrument.timeout = 5000
            self.instrument.baud_rate = 115200
            self.instrument.data_bits = 8
            self.instrument.parity = pyvisa.constants.Parity.none
            self.instrument.stop_bits = pyvisa.constants.StopBits.one
            self.instrument.read_termination = '\n'
            self.instrument.write_termination = '\r\n'
            print(f"Connected to {self.resource_name}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to connect to {self.resource_name}: {e}")
            raise

    def __enter__(self):
        """Context manager entry: reset and prepare for measurements."""
        import time
        self.reset()
        time.sleep(0.5)  # Device needs time after reset
        self.clear_status()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Context manager exit: no special cleanup needed for DMM."""
        pass

    # ========================================================================
    # Configuration Methods
    # ========================================================================

    def configure_dc_voltage(self, range_val: float = None):
        """
        Configure for DC voltage measurement.

        Args:
            range_val (float, optional): Voltage range in volts.
                                        If None, uses auto-range.
        """
        self.send_command(":CONFigure:VOLTage:DC")
        if range_val is None:
            self.send_command(":SENSe:VOLTage:DC:RANGe:AUTO ON")
        else:
            self.send_command(f":SENSe:VOLTage:DC:RANGe {range_val}")

    def configure_ac_voltage(self, range_val: float = None):
        """
        Configure for AC voltage measurement.

        Args:
            range_val (float, optional): Voltage range in volts.
                                        If None, uses auto-range.
        """
        self.send_command(":CONFigure:VOLTage:AC")
        if range_val is None:
            self.send_command(":SENSe:VOLTage:AC:RANGe:AUTO ON")
        else:
            self.send_command(f":SENSe:VOLTage:AC:RANGe {range_val}")

    def configure_dc_current(self, range_val: float = None):
        """
        Configure for DC current measurement.

        Args:
            range_val (float, optional): Current range in amps.
                                        If None, uses auto-range.
        """
        self.send_command(":CONFigure:CURRent:DC")
        if range_val is None:
            self.send_command(":SENSe:CURRent:DC:RANGe:AUTO ON")
        else:
            self.send_command(f":SENSe:CURRent:DC:RANGe {range_val}")

    def configure_ac_current(self, range_val: float = None):
        """
        Configure for AC current measurement.

        Args:
            range_val (float, optional): Current range in amps.
                                        If None, uses auto-range.
        """
        self.send_command(":CONFigure:CURRent:AC")
        if range_val is None:
            self.send_command(":SENSe:CURRent:AC:RANGe:AUTO ON")
        else:
            self.send_command(f":SENSe:CURRent:AC:RANGe {range_val}")

    def configure_resistance_2wire(self, range_val: float = None):
        """
        Configure for 2-wire resistance measurement.

        Args:
            range_val (float, optional): Resistance range in ohms.
                                        If None, uses auto-range.
        """
        self.send_command(":CONFigure:RESistance")
        if range_val is None:
            self.send_command(":SENSe:RESistance:RANGe:AUTO ON")
        else:
            self.send_command(f":SENSe:RESistance:RANGe {range_val}")

    def configure_resistance_4wire(self, range_val: float = None):
        """
        Configure for 4-wire resistance measurement.

        Args:
            range_val (float, optional): Resistance range in ohms.
                                        If None, uses auto-range.
        """
        self.send_command(":CONFigure:FRESistance")
        if range_val is None:
            self.send_command(":SENSe:FRESistance:RANGe:AUTO ON")
        else:
            self.send_command(f":SENSe:FRESistance:RANGe {range_val}")

    def configure_frequency(self):
        """Configure for frequency measurement."""
        self.send_command(":CONFigure:FREQuency")

    def configure_capacitance(self, range_val: float = None):
        """
        Configure for capacitance measurement.

        Args:
            range_val (float, optional): Capacitance range in farads.
                                        If None, uses auto-range.
        """
        self.send_command(":CONFigure:CAPacitance")
        if range_val is None:
            self.send_command(":SENSe:CAPacitance:RANGe:AUTO ON")
        else:
            self.send_command(f":SENSe:CAPacitance:RANGe {range_val}")

    def configure_temperature(self):
        """Configure for temperature measurement."""
        self.send_command(":CONFigure:TEMPerature")

    # ========================================================================
    # Measurement Methods (using Owon's simplified syntax)
    # ========================================================================

    def measure(self) -> float:
        """
        Take a measurement using current configuration.

        Uses Owon's simplified MEAS? command (not standard :READ?).

        Returns:
            float: Measurement value
        """
        import time
        time.sleep(0.2)  # Device needs time to settle after configuration
        result = self.query("MEAS?")
        return float(result.strip())

    def measure_dc_voltage(self, range_val: float = None) -> float:
        """
        Measure DC voltage.

        Args:
            range_val (float, optional): Voltage range. If None, uses auto-range.

        Returns:
            float: DC voltage in volts
        """
        self.configure_dc_voltage(range_val)
        return self.measure()

    def measure_ac_voltage(self, range_val: float = None) -> float:
        """
        Measure AC voltage.

        Args:
            range_val (float, optional): Voltage range. If None, uses auto-range.

        Returns:
            float: AC voltage in volts (RMS)
        """
        self.configure_ac_voltage(range_val)
        return self.measure()

    def measure_dc_current(self, range_val: float = None) -> float:
        """
        Measure DC current.

        Args:
            range_val (float, optional): Current range. If None, uses auto-range.

        Returns:
            float: DC current in amps
        """
        self.configure_dc_current(range_val)
        return self.measure()

    def measure_ac_current(self, range_val: float = None) -> float:
        """
        Measure AC current.

        Args:
            range_val (float, optional): Current range. If None, uses auto-range.

        Returns:
            float: AC current in amps (RMS)
        """
        self.configure_ac_current(range_val)
        return self.measure()

    def measure_resistance_2wire(self, range_val: float = None) -> float:
        """
        Measure resistance (2-wire).

        Args:
            range_val (float, optional): Resistance range. If None, uses auto-range.

        Returns:
            float: Resistance in ohms
        """
        self.configure_resistance_2wire(range_val)
        return self.measure()

    def measure_resistance_4wire(self, range_val: float = None) -> float:
        """
        Measure resistance (4-wire).

        Args:
            range_val (float, optional): Resistance range. If None, uses auto-range.

        Returns:
            float: Resistance in ohms
        """
        self.configure_resistance_4wire(range_val)
        return self.measure()

    def measure_frequency(self) -> float:
        """
        Measure frequency.

        Returns:
            float: Frequency in Hz
        """
        self.configure_frequency()
        return self.measure()

    def measure_capacitance(self, range_val: float = None) -> float:
        """
        Measure capacitance.

        Args:
            range_val (float, optional): Capacitance range. If None, uses auto-range.

        Returns:
            float: Capacitance in farads
        """
        self.configure_capacitance(range_val)
        return self.measure()

    def measure_temperature(self) -> float:
        """
        Measure temperature.

        Returns:
            float: Temperature in degrees Celsius
        """
        self.configure_temperature()
        return self.measure()

    # ========================================================================
    # Compatibility Methods (for REPL and HP 34401A compatibility)
    # ========================================================================

    def set_mode(self, mode: str):
        """
        Set measurement mode (for compatibility with REPL).

        Args:
            mode (str): Mode name (vdc, vac, idc, iac, res, fres, freq, cap, temp)
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
            "cap": self.configure_capacitance,
            "capacitance": self.configure_capacitance,
            "temp": self.configure_temperature,
            "temperature": self.configure_temperature,
        }

        if mode.lower() not in mode_map:
            raise ValueError(f"Unknown mode: {mode}. Valid modes: {list(mode_map.keys())}")

        mode_map[mode.lower()]()

    def read(self) -> float:
        """
        Read current measurement (for compatibility).

        Returns:
            float: Current measurement value
        """
        return self.measure()

    def get_error(self) -> str:
        """
        Read error queue.

        NOTE: Error queries may not work reliably on this device.

        Returns:
            str: Error message or indication that queries don't work
        """
        try:
            return self.query(":SYSTem:ERRor?")
        except:
            return "Error queries not supported by Owon XDM1041"

    def __repr__(self):
        """String representation for debugging."""
        return f"Owon_XDM1041(resource={self.resource_name})"
