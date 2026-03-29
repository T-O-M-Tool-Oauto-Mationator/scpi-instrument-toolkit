"""
Driver for the NI PXIe-4139 Source Measure Unit (SMU).
Instrument Type: DC Power Supply / Source Measure Unit

Uses the nidcpower Python package (NI-DCPower driver) instead of PyVISA/SCPI.
Does NOT inherit from DeviceManager.
"""

import contextlib
import datetime

import nidcpower


class NI_PXIe_4139:
    """Driver for the NI PXIe-4139 SMU via nidcpower.

    Exposes the same PSU-like interface that the REPL expects so it can be
    used interchangeably with SCPI-based power supplies.

    Key nidcpower pattern: property changes (voltage_level, output_enabled)
    must be applied while the session is initiated (running). Set properties
    on-the-fly FIRST, then abort() to stop.
    """

    # Hardware limits for the PXIe-4139 (per NI datasheet: ±60 V, 3 A SMU)
    # DC source power capped at 20 W, DC sink power at 12 W (hardware-enforced).
    MAX_VOLTAGE = 60.0       # ±60 V
    MAX_CURRENT = 3.0        # ±3 A DC (10 A pulse only)
    MAX_SOURCE_DELAY = 167.0  # seconds, hardware limit per NI-DCPower spec
    DEFAULT_CURRENT_LIMIT = 0.01  # 10 mA
    DEFAULT_VOLTAGE_LIMIT = 5.0  # V, compliance when in current mode

    def __init__(self, resource_name: str):
        self.resource_name = resource_name
        self._session = None
        self._output_mode = "voltage"  # "voltage" or "current"

    # ------------------------------------------------------------------
    # Connection
    # ------------------------------------------------------------------

    def connect(self):
        """Open an nidcpower session and configure safe defaults."""
        self._session = nidcpower.Session(resource_name=self.resource_name, channels="0")
        self._session.output_function = nidcpower.OutputFunction.DC_VOLTAGE
        self._session.voltage_level_autorange = True
        self._session.current_limit_autorange = True
        self._session.voltage_level = 0.0
        self._session.current_limit = self.DEFAULT_CURRENT_LIMIT
        self._session.output_enabled = True
        self._session.commit()
        # Initiate, zero, disable, abort — ensures hardware is truly at 0 V
        self._session.initiate()
        self._session.voltage_level = 0.0
        self._session.output_enabled = False
        self._session.abort()
        print(f"Connected to {self.resource_name}")

    def disconnect(self):
        """Close the nidcpower session."""
        if self._session is not None:
            try:
                # Zero and disable while running, then abort
                self._session.voltage_level = 0.0
                self._session.output_enabled = False
                self._session.initiate()
                self._session.abort()
            except Exception:
                pass
            self._session.close()
            self._session = None
            print(f"Disconnected from {self.resource_name}")

    # ------------------------------------------------------------------
    # Context manager
    # ------------------------------------------------------------------

    def __enter__(self):
        self.disable_all_channels()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.disable_all_channels()

    # ------------------------------------------------------------------
    # Output control
    # ------------------------------------------------------------------

    def enable_output(self, enabled: bool = True):
        """Enable or disable the output."""
        self._check_session()
        if enabled:
            self._session.output_enabled = True
            self._session.commit()
            self._session.initiate()
        else:
            # Set voltage to 0 and disable while session is still running
            self._session.voltage_level = 0.0
            self._session.output_enabled = False
            self._session.abort()

    def disable_all_channels(self):
        """Set output to safe state: 0 V, low current limit, output off."""
        self._check_session()
        # Set safe values while running, then abort
        self._session.voltage_level = 0.0
        self._session.current_limit = self.DEFAULT_CURRENT_LIMIT
        self._session.output_enabled = False
        with contextlib.suppress(Exception):
            self._session.initiate()
        with contextlib.suppress(Exception):
            self._session.abort()

    # ------------------------------------------------------------------
    # Voltage / current configuration
    # ------------------------------------------------------------------

    def set_voltage(self, voltage: float):
        """Set the DC voltage level."""
        self._check_session()
        if not -self.MAX_VOLTAGE <= voltage <= self.MAX_VOLTAGE:
            raise ValueError(f"Voltage must be between -{self.MAX_VOLTAGE} and {self.MAX_VOLTAGE} V")
        self._session.voltage_level = voltage
        self._session.commit()

    def set_current_limit(self, current: float):
        """Set the current limit."""
        self._check_session()
        if not -self.MAX_CURRENT <= current <= self.MAX_CURRENT:
            raise ValueError(f"Current limit must be between -{self.MAX_CURRENT} and {self.MAX_CURRENT} A")
        self._session.current_limit = current
        self._session.commit()

    def set_output_channel(self, channel, voltage, current_limit=None):
        """Set voltage and current limit (channel arg ignored — single channel)."""
        self.set_voltage(voltage)
        if current_limit is not None:
            self.set_current_limit(current_limit)

    # ------------------------------------------------------------------
    # Measurement
    # ------------------------------------------------------------------

    def measure_vi(self) -> dict:
        """Atomic V+I+compliance measurement in a single session call.

        Returns:
            dict with keys 'voltage' (float), 'current' (float),
            'in_compliance' (bool).
        """
        self._check_session()
        m = self._measure()
        return {
            "voltage": m.voltage,
            "current": m.current,
            # measure_multiple does not populate in_compliance; use the
            # dedicated query which is always accurate.
            "in_compliance": self.query_in_compliance(),
        }

    def measure_voltage(self) -> float:
        """Measure the output voltage."""
        self._check_session()
        return self.measure_vi()["voltage"]

    def measure_current(self) -> float:
        """Measure the output current."""
        self._check_session()
        return self.measure_vi()["current"]

    def _measure(self):
        """Take a single measurement, initiating the session if needed."""
        was_running = self._session.output_enabled
        if not was_running:
            self._session.output_enabled = True
            self._session.commit()
            self._session.initiate()
        try:
            return self._session.measure_multiple()[0]
        finally:
            if not was_running:
                # Disable while running, then abort
                self._session.output_enabled = False
                self._session.abort()

    # ------------------------------------------------------------------
    # Compliance
    # ------------------------------------------------------------------

    def query_in_compliance(self) -> bool:
        """Return True if the output has hit the compliance limit."""
        self._check_session()
        return bool(self._session.query_in_compliance())

    # ------------------------------------------------------------------
    # Source delay
    # ------------------------------------------------------------------

    def set_source_delay(self, seconds: float) -> None:
        """Set the source settle delay before measurement (0 to 167 seconds)."""
        self._check_session()
        if not 0 <= seconds <= self.MAX_SOURCE_DELAY:
            raise ValueError(f"source_delay must be between 0 and {self.MAX_SOURCE_DELAY} seconds")
        self._session.source_delay = datetime.timedelta(seconds=seconds)
        self._session.commit()

    def get_source_delay(self) -> float:
        """Return the current source_delay in seconds."""
        self._check_session()
        return self._session.source_delay.total_seconds()

    # ------------------------------------------------------------------
    # Output mode (voltage / current)
    # ------------------------------------------------------------------

    def set_voltage_mode(self, voltage: float, current_limit: float = None) -> None:
        """Switch to DC_VOLTAGE mode and set the voltage level."""
        self._check_session()
        if not -self.MAX_VOLTAGE <= voltage <= self.MAX_VOLTAGE:
            raise ValueError(f"Voltage must be between -{self.MAX_VOLTAGE} and {self.MAX_VOLTAGE} V")
        if current_limit is not None and not -self.MAX_CURRENT <= current_limit <= self.MAX_CURRENT:
            raise ValueError(f"Current limit must be between -{self.MAX_CURRENT} and {self.MAX_CURRENT} A")
        self._session.output_function = nidcpower.OutputFunction.DC_VOLTAGE
        self._session.voltage_level = voltage
        if current_limit is not None:
            self._session.current_limit = current_limit
        self._output_mode = "voltage"
        self._session.commit()

    def set_current_mode(self, current: float, voltage_limit: float = None) -> None:
        """Switch to DC_CURRENT mode and set the current level."""
        self._check_session()
        if not -self.MAX_CURRENT <= current <= self.MAX_CURRENT:
            raise ValueError(f"Current must be between -{self.MAX_CURRENT} and {self.MAX_CURRENT} A")
        if voltage_limit is None:
            voltage_limit = self.DEFAULT_VOLTAGE_LIMIT
        if not 0 <= voltage_limit <= self.MAX_VOLTAGE:
            raise ValueError(f"Voltage limit must be between 0 and {self.MAX_VOLTAGE} V")
        self._session.output_function = nidcpower.OutputFunction.DC_CURRENT
        self._session.current_level = current
        self._session.voltage_limit = voltage_limit
        self._output_mode = "current"
        self._session.commit()

    def get_output_mode(self) -> str:
        """Return the active output mode: 'voltage' or 'current'."""
        self._check_session()
        return self._output_mode

    # ------------------------------------------------------------------
    # Averaging
    # ------------------------------------------------------------------

    def set_samples_to_average(self, n: int) -> None:
        """Set the averaging count for noise reduction (n >= 1)."""
        self._check_session()
        n = int(n)
        if n < 1:
            raise ValueError("samples_to_average must be >= 1")
        self._session.samples_to_average = n
        self._session.commit()

    def get_samples_to_average(self) -> int:
        """Return the current samples_to_average setting."""
        self._check_session()
        return int(self._session.samples_to_average)

    # ------------------------------------------------------------------
    # Temperature
    # ------------------------------------------------------------------

    def read_temperature(self) -> float:
        """Read the SMU instrument temperature in degrees Celsius."""
        self._check_session()
        return float(self._session.read_current_temperature())

    # ------------------------------------------------------------------
    # Getters
    # ------------------------------------------------------------------

    def get_voltage_setpoint(self) -> float:
        """Return the configured voltage level."""
        self._check_session()
        return self._session.voltage_level

    def get_current_limit(self) -> float:
        """Return the configured current limit."""
        self._check_session()
        return self._session.current_limit

    def get_output_state(self) -> bool:
        """Return whether the output is enabled."""
        self._check_session()
        return self._session.output_enabled

    # ------------------------------------------------------------------
    # Reset / SCPI compatibility stubs
    # ------------------------------------------------------------------

    def reset(self):
        """Reset the instrument to default state."""
        self._check_session()
        self._session.reset()

    def query(self, cmd, **kwargs):
        """Return an IDN-like string (SCPI compatibility stub)."""
        return f"National Instruments,PXIe-4139,{self.resource_name},nidcpower"

    def send_command(self, cmd):
        """No-op SCPI compatibility stub."""
        pass

    def get_error(self) -> str:
        """SCPI compatibility stub — error queue not supported on NI_PXIe_4139."""
        self._check_session()
        return "not supported on NI_PXIe_4139"

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _check_session(self):
        if self._session is None:
            raise ConnectionError("SMU not connected. Call connect() first.")
