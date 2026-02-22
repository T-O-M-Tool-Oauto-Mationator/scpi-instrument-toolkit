"""
Driver for Owon XDM1041 Digital Multimeter
Instrument Type: 7½-digit bench DMM

NOTE: Non-standard SCPI implementation:
- Range is passed as a parameter to CONFigure commands (SENSe:*:RANGe not supported)
- Measurement uses simplified syntax (MEAS? instead of :READ?)
- Run/Stop is hardware-only; no SCPI command exists to control it remotely
"""

from .device_manager import DeviceManager
import pyvisa


class Owon_XDM1041(DeviceManager):
    """
    Driver for Owon XDM1041 7½-digit Digital Multimeter.

    Features:
    - DC/AC Voltage measurement (up to 1000V DC, 750V AC)
    - DC/AC Current measurement (up to 10A)
    - 2-wire and 4-wire resistance (4-wire max 50kΩ)
    - Frequency, period, capacitance, temperature, diode, continuity
    - 7½ digits resolution

    IMPORTANT: Non-standard SCPI implementation:
    - Range is passed directly to CONFigure commands, not via SENSe subsystem
    - Measurement uses MEAS? (not :READ?)
    - Run/Stop cannot be controlled via SCPI (physical button only)
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
                                        Valid: 500e-3, 5, 50, 500, 1000
                                        If None, uses auto-range.
        """
        if range_val is None:
            self.send_command("CONFigure:VOLTage:DC AUTO")
        else:
            self.send_command(f"CONFigure:VOLTage:DC {range_val}")

    def configure_ac_voltage(self, range_val: float = None):
        """
        Configure for AC voltage measurement.

        Args:
            range_val (float, optional): Voltage range in volts.
                                        Valid: 500e-3, 5, 50, 500, 750
                                        If None, uses auto-range.
        """
        if range_val is None:
            self.send_command("CONFigure:VOLTage:AC AUTO")
        else:
            self.send_command(f"CONFigure:VOLTage:AC {range_val}")

    def configure_dc_current(self, range_val: float = None):
        """
        Configure for DC current measurement.

        Args:
            range_val (float, optional): Current range in amps.
                                        Valid: 500e-6, 5e-3, 50e-3, 500e-3, 5, 10
                                        If None, uses auto-range.
        """
        if range_val is None:
            self.send_command("CONFigure:CURRent:DC AUTO")
        else:
            self.send_command(f"CONFigure:CURRent:DC {range_val}")

    def configure_ac_current(self, range_val: float = None):
        """
        Configure for AC current measurement.

        Args:
            range_val (float, optional): Current range in amps.
                                        Valid: 500e-6, 5e-3, 50e-3, 500e-3, 5, 10
                                        If None, uses auto-range.
        """
        if range_val is None:
            self.send_command("CONFigure:CURRent:AC AUTO")
        else:
            self.send_command(f"CONFigure:CURRent:AC {range_val}")

    def configure_resistance_2wire(self, range_val: float = None):
        """
        Configure for 2-wire resistance measurement.

        Args:
            range_val (float, optional): Resistance range in ohms.
                                        Valid: 500, 5e3, 50e3, 500e3, 5e6, 50e6
                                        If None, uses auto-range.
        """
        if range_val is None:
            self.send_command("CONFigure:RESistance AUTO")
        else:
            self.send_command(f"CONFigure:RESistance {range_val}")

    def configure_resistance_4wire(self, range_val: float = None):
        """
        Configure for 4-wire resistance measurement.

        Note: Maximum range is 50kΩ.

        Args:
            range_val (float, optional): Resistance range in ohms.
                                        Valid: 500, 5e3, 50e3
                                        If None, uses auto-range.
        """
        if range_val is None:
            self.send_command("CONFigure:FRESistance AUTO")
        else:
            self.send_command(f"CONFigure:FRESistance {range_val}")

    def configure_frequency(self):
        """Configure for frequency measurement."""
        self.send_command("CONFigure:FREQuency")

    def configure_period(self):
        """Configure for period measurement."""
        self.send_command("CONFigure:PERiod")

    def configure_capacitance(self, range_val: float = None):
        """
        Configure for capacitance measurement.

        Args:
            range_val (float, optional): Capacitance range in farads.
                                        Valid: 50e-9, 500e-9, 5e-6, 50e-6, 500e-6, 5e-3, 50e-3
                                        If None, uses auto-range.
        """
        if range_val is None:
            self.send_command("CONFigure:CAPacitance AUTO")
        else:
            self.send_command(f"CONFigure:CAPacitance {range_val}")

    def configure_temperature(self, rtd_type: str = "KITS90"):
        """
        Configure for temperature measurement.

        Args:
            rtd_type (str): RTD sensor type. Valid: 'KITS90' (K-type, default), 'PT100'
        """
        self.send_command(f"CONFigure:TEMPerature:RTD {rtd_type}")

    def configure_diode(self):
        """Configure for diode measurement."""
        self.send_command("CONFigure:DIODe")

    def configure_continuity(self):
        """Configure for continuity test."""
        self.send_command("CONFigure:CONTinuity")

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
        time.sleep(2.0)  # Device needs time to settle after configuration
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

    def measure_period(self) -> float:
        """
        Measure period.

        Returns:
            float: Period in seconds
        """
        self.configure_period()
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

    def measure_temperature(self, rtd_type: str = "KITS90") -> float:
        """
        Measure temperature.

        Args:
            rtd_type (str): RTD type. Valid: 'KITS90' (K-type, default), 'PT100'

        Returns:
            float: Temperature in degrees Celsius
        """
        self.configure_temperature(rtd_type)
        return self.measure()

    def measure_diode(self) -> float:
        """
        Measure diode forward voltage.

        Returns:
            float: Diode voltage in volts
        """
        self.configure_diode()
        return self.measure()

    # ========================================================================
    # Compatibility Methods (for REPL and HP 34401A compatibility)
    # ========================================================================

    def set_mode(self, mode: str):
        """
        Set measurement mode (for compatibility with REPL).

        Args:
            mode (str): Mode name (vdc, vac, idc, iac, res, fres, freq, per,
                        cap, temp, diod, cont)
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
            "cap": self.configure_capacitance,
            "capacitance": self.configure_capacitance,
            "temp": self.configure_temperature,
            "temperature": self.configure_temperature,
            "diod": self.configure_diode,
            "diode": self.configure_diode,
            "cont": self.configure_continuity,
            "continuity": self.configure_continuity,
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
        Error query stub.

        NOTE: SYSTem:ERRor? is not supported on the XDM1041.

        Returns:
            str: Not supported message
        """
        return "Error query not supported by Owon XDM1041"

    def __repr__(self):
        """String representation for debugging."""
        return f"Owon_XDM1041(resource={self.resource_name})"
