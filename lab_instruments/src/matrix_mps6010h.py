"""
Driver for MATRIX MPS-6010H-1C Power Supply
Instrument Type: DC Power Supply (60V/10A, single channel)

IMPORTANT: This device requires enabling remote mode first with REM:ON
- Must send REM:ON before remote commands will work
- Commands: VOLT (not VSET), CURR (not ISET), OUTP (not OUTPUT)
- Device DOES support query commands (VOLT?, MEAS:VOLT?, MEAS:CURR?)
- Use REM:OFF or press Shift+7 on front panel to return to local mode
"""

from .device_manager import DeviceManager
import pyvisa


class MATRIX_MPS6010H(DeviceManager):
    """
    Driver for MATRIX MPS-6010H-1C Power Supply (60V/10A).

    WARNING: This device does not support query commands. All measurement
    methods return cached values from the last set command, NOT actual
    measured values from the device. Use an external DMM for accurate
    measurements.
    """

    # Specifications
    MAX_VOLTAGE = 60.0  # Volts
    MAX_CURRENT = 10.0  # Amps

    def __init__(self, resource_name):
        """Initialize the MATRIX MPS-6010H-1C PSU."""
        super().__init__(resource_name)

        # Internal state cache (since device doesn't support queries)
        self._voltage_setpoint = 0.0
        self._current_limit = 0.1
        self._output_enabled = False

    def connect(self):
        """Override to set serial communication parameters and enable remote mode."""
        try:
            self.instrument = self.rm.open_resource(self.resource_name)
            self.instrument.timeout = 10000  # 10 seconds for reliable measurement queries
            self.instrument.baud_rate = 9600
            self.instrument.data_bits = 8
            self.instrument.parity = pyvisa.constants.Parity.none
            self.instrument.stop_bits = pyvisa.constants.StopBits.one
            self.instrument.read_termination = "\n"
            self.instrument.write_termination = "\n"  # LF only, not CR+LF
            print(f"Connected to {self.resource_name}")

            # Enable remote mode (required for commands to work)
            self.send_command("REM:ON")
            print("Remote mode enabled")
        except pyvisa.VisaIOError as e:
            print(f"Failed to connect to {self.resource_name}: {e}")
            raise

    def __enter__(self):
        """Context manager entry: disable output for safety."""
        self.clear_status()
        self.disable_output()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Context manager exit: disable output and return to local mode."""
        self.disable_output()
        # Return to local mode
        self.send_command("REM:OFF")
        print("Returned to local mode")

    def disable_output(self):
        """
        Disable output and set to safe state (0V, 0.1A limit).

        Safety first: Always call this before disconnecting or on error.
        """
        self.enable_output(False)
        self.set_voltage(0.0)
        self.set_current_limit(0.1)

    def set_voltage(self, voltage: float):
        """
        Set output voltage.

        Args:
            voltage (float): Desired output voltage (0-60V).

        Raises:
            ValueError: If voltage is out of range.
        """
        if not (0.0 <= voltage <= self.MAX_VOLTAGE):
            raise ValueError(
                f"Voltage must be between 0 and {self.MAX_VOLTAGE}V. Got {voltage}V."
            )

        self.send_command(f"VOLT {voltage:.3f}")
        self._voltage_setpoint = voltage

    def set_current_limit(self, current: float):
        """
        Set current limit.

        Args:
            current (float): Desired current limit (0-10A).

        Raises:
            ValueError: If current is out of range.
        """
        if not (0.0 <= current <= self.MAX_CURRENT):
            raise ValueError(
                f"Current must be between 0 and {self.MAX_CURRENT}A. Got {current}A."
            )

        self.send_command(f"CURR {current:.3f}")
        self._current_limit = current

    def set_output(self, voltage: float, current_limit: float):
        """
        Set both voltage and current limit in one call.

        Args:
            voltage (float): Desired output voltage (0-60V).
            current_limit (float): Desired current limit (0-10A).
        """
        self.set_voltage(voltage)
        self.set_current_limit(current_limit)

    def enable_output(self, enabled: bool = True):
        """
        Enable or disable the output.

        Args:
            enabled (bool): True to enable output, False to disable.
        """
        state = "1" if enabled else "0"
        self.send_command(f"OUTP {state}")
        self._output_enabled = enabled

    def get_voltage_setpoint(self) -> float:
        """
        Get the voltage setpoint (cached value, not measured).

        Returns:
            float: Last voltage setpoint sent to device.

        WARNING: This returns the CACHED value from the last set_voltage() call,
        NOT the actual measured voltage. Use an external DMM for measurements.
        """
        return self._voltage_setpoint

    def get_current_limit(self) -> float:
        """
        Get the current limit setpoint (cached value, not measured).

        Returns:
            float: Last current limit sent to device.

        WARNING: This returns the CACHED value from the last set_current_limit() call,
        NOT the actual measured current. Use an external DMM for measurements.
        """
        return self._current_limit

    def get_output_state(self) -> bool:
        """
        Get the output state (cached value, not queried from device).

        Returns:
            bool: Last output state sent to device.

        WARNING: This returns the CACHED value from the last enable_output() call,
        NOT the actual device state. Check the front panel for confirmation.
        """
        return self._output_enabled

    def measure_voltage(self):
        """
        Measure output voltage.

        Returns:
            float: Actual measured output voltage in volts.
        """
        try:
            # Use query() instead of write/sleep/read pattern - more reliable
            response = self.query("MEAS:VOLT?")
            return float(response)
        except Exception as e:
            print(f"Warning: Could not measure voltage: {e}")
            print("Returning cached setpoint")
            return self._voltage_setpoint

    def measure_current(self):
        """
        Measure output current.

        Returns:
            float: Actual measured output current in amps.
        """
        try:
            # Use query() instead of write/sleep/read pattern - more reliable
            response = self.query("MEAS:CURR?")
            return float(response)
        except Exception as e:
            print(f"Warning: Could not measure current: {e}")
            return 0.0

    def get_error(self):
        """
        Read error queue.

        WARNING: This device does not support error queries.

        Returns:
            str: Message indicating error queries are not supported.
        """
        return "Error queries not supported by MATRIX MPS-6010H"

    # ========================================================================
    # REPL Compatibility Methods (to work with multi-channel PSU commands)
    # ========================================================================

    def set_output_channel(self, channel, voltage, current_limit=None):
        """
        Compatibility method for REPL - ignores channel (single channel PSU).

        Args:
            channel: Ignored (MATRIX has only one channel)
            voltage (float): Desired output voltage (0-60V)
            current_limit (float): Desired current limit (0-10A)
        """
        self.set_voltage(voltage)
        if current_limit is not None:
            self.set_current_limit(current_limit)

    def measure_voltage_channel(self, channel=None):
        """
        Compatibility method for REPL - ignores channel.

        Args:
            channel: Ignored (MATRIX has only one channel)

        Returns:
            float: Measured voltage
        """
        return self.measure_voltage()

    def measure_current_channel(self, channel=None):
        """
        Compatibility method for REPL - ignores channel.

        Args:
            channel: Ignored (MATRIX has only one channel)

        Returns:
            float: Measured current
        """
        return self.measure_current()

    # ========================================================================

    def __repr__(self):
        """String representation for debugging."""
        return (
            f"MATRIX_MPS6010H(resource={self.resource_name}, "
            f"V_set={self._voltage_setpoint}V, "
            f"I_limit={self._current_limit}A, "
            f"output={'ON' if self._output_enabled else 'OFF'})"
        )
