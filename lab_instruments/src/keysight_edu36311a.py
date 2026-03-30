# Keysight EDU36311A
"""
Driver for the Keysight EDU36311A Triple Output DC Power Supply.
Instrument Type: DC Power Supply
"""

"""
TODO: Update docstring.
Command Syntax Conventions:
Square Brackets [ ]: Indicate optional keywords or parameters.
Braces { }: Enclose parameters within a command string.
Triangle Brackets < >: Indicate that you must substitute a value or a code for the enclosed parameter.
Vertical Bar |: Separates one of two or more alternative parameters.
"""

from .device_manager import DeviceManager  # noqa: E402


class Keysight_EDU36311A(DeviceManager):
    # Output Channels
    CHANNEL_MAP = {
        "p6v_channel": "P6V",  # 0-6.18V, 5.15A max
        "p30v_channel": "P30V",  # 0-30.9V, 1.03A max
        "n30v_channel": "N30V",  # 0-30.9V, 1.03A max
    }

    _CHANNEL_NUM = {
        "p6v_channel": 1,
        "p30v_channel": 2,
        "n30v_channel": 3,
    }

    DEFAULT_CURRENT_LIMIT = {
        "p6v_channel": 1.0,  # Default current limit for P6V channel
        "p30v_channel": 0.5,  # Default current limit for P30V channel
        "n30v_channel": 0.5,  # Default current limit for N30V channel
    }

    # Hardware limits: (max_voltage_V, max_current_A)
    CHANNEL_LIMITS = {
        "p6v_channel": (6.0, 5.0),
        "p30v_channel": (30.0, 1.0),
        "n30v_channel": (30.0, 1.0),
    }

    def __init__(self, resource_name):
        """Initialize the Keysight EDU36311A PSU."""
        super().__init__(resource_name)

    def connect(self):
        """Connect to the instrument and initialize it."""
        super().connect()
        self.clear_status()
        self.disable_all_channels()

    def __enter__(self):
        self.disable_all_channels()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.disable_all_channels()

    def disable_all_channels(self):
        """
        Disables output and sets all channels to 0V, 0A.
        """
        # 1. Disable Output (Priority)
        self.enable_output(False)

        # 2. Zero all setpoints (0V, 0A)
        for _, scpi_name in self.CHANNEL_MAP.items():
            # APPLy {output}, {voltage}, {current}
            self.send_command(f"APPLy {scpi_name}, 0.0, 0.0")

    def enable_output(self, enabled: bool = True):
        """Enable or disable the output of the power supply.

        Args:
            enabled (bool): True to enable output, False to disable.
        """
        state = "ON" if enabled else "OFF"
        self.send_command(f"OUTPut {state}")

    def select_channel(self, channel):
        """Select the channel to control.

        Args:
            channel (str): The channel to select. Must be one of the keys in CHANNEL_MAP.
        """
        if channel not in self.CHANNEL_MAP:
            raise ValueError(f"Invalid channel. Must be one of: {list(self.CHANNEL_MAP.keys())}")
        command = f"INSTrument:NSELect {self._CHANNEL_NUM[channel]}"
        self.send_command(command)

    def set_output_channel(self, channel, voltage, current_limit=None):
        """Set the output voltage and current limit for a specific channel.

        Args:
            channel (str): The channel to set. Must be one of the keys in CHANNEL_MAP.
            voltage (float): The desired output voltage.
            current_limit (float): The desired current limit.
        """
        # Validate channel
        if channel not in self.CHANNEL_MAP:
            raise ValueError(f"Invalid channel. Must be one of: {list(self.CHANNEL_MAP.keys())}")

        # Use default current limit if none provided
        if current_limit is None:
            current_limit = self.DEFAULT_CURRENT_LIMIT[channel]

        scpi_name = self.CHANNEL_MAP[channel]
        self.send_command(f"APPLy {scpi_name}, {voltage}, {current_limit}")

    def measure_voltage(self, channel):
        """Measure the output voltage of a specific channel.

        Args:
            channel (str): The channel to measure. Must be one of the keys in CHANNEL_MAP.

        Returns:
            float: The measured voltage.
        """
        if channel not in self.CHANNEL_MAP:
            raise ValueError(f"Invalid channel. Must be one of: {list(self.CHANNEL_MAP.keys())}")
        self.select_channel(channel)
        response = self.query("MEASure:VOLTage:DC?")
        try:
            # Remove any units or extra whitespace and convert to float
            # Split on whitespace and take the first element (the number)
            value_str = response.strip().split()[0]
            return float(value_str)
        except (ValueError, IndexError) as e:
            raise ValueError(f"Failed to convert voltage response '{response}' to float: {e}") from e

    def measure_current(self, channel):
        """Measure the output current of a specific channel.

        Args:
            channel (str): The channel to measure. Must be one of the keys in CHANNEL_MAP.

        Returns:
            float: The measured current.
        """
        if channel not in self.CHANNEL_MAP:
            raise ValueError(f"Invalid channel. Must be one of: {list(self.CHANNEL_MAP.keys())}")
        self.select_channel(channel)
        response = self.query("MEASure:CURRent:DC?")
        try:
            # Remove any units or extra whitespace and convert to float
            # Split on whitespace and take the first element (the number)
            value_str = response.strip().split()[0]
            return float(value_str)
        except (ValueError, IndexError) as e:
            raise ValueError(f"Failed to convert current response '{response}' to float: {e}") from e

    def set_voltage(self, channel, voltage):
        """Set only the voltage for the specified channel."""
        self.select_channel(channel)
        self.send_command(f"SOURce:VOLTage {voltage}")

    def set_current_limit(self, channel, current):
        """Set only the current limit for the specified channel."""
        self.select_channel(channel)
        self.send_command(f"SOURce:CURRent {current}")

    def get_voltage_setpoint(self, channel=None):
        """Query the voltage setpoint for the currently selected (or specified) channel."""
        if channel is not None:
            self.select_channel(channel)
        resp = self.query("SOURce:VOLTage?")
        return float(resp.strip().split()[0])

    def get_current_limit(self, channel=None):
        """Query the current limit for the currently selected (or specified) channel."""
        if channel is not None:
            self.select_channel(channel)
        resp = self.query("SOURce:CURRent?")
        return float(resp.strip().split()[0])

    def get_output_state(self):
        """Query whether the output is enabled."""
        resp = self.query("OUTPut?").strip()
        return resp in ("1", "ON")

    def get_error(self):
        """Reads the most recent error from the error queue."""
        return self.query("SYSTem:ERRor?")

    def set_tracking(self, enable: bool):
        """Enable or disable tracking mode for the +/-30V supplies."""
        state = "ON" if enable else "OFF"
        self.send_command(f"OUTPut:TRACk {state}")

    def save_state(self, location: int):
        """Save the current state to memory location 1-5."""
        if location not in [1, 2, 3, 4, 5]:
            raise ValueError("Location must be between 1 and 5.")
        self.send_command(f"*SAV {location}")

    def recall_state(self, location: int):
        """Recall a saved state from memory location 1-5."""
        if location not in [1, 2, 3, 4, 5]:
            raise ValueError("Location must be between 1 and 5.")
        self.send_command(f"*RCL {location}")
