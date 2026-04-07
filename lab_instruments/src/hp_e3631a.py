# HP E3631A
"""Driver for the HP E3631A Power Supply Unit (PSU).
Instrument Type: DC Power Supply — triple-output (+6V/+25V/-25V)
"""

import enum

from .device_manager import DeviceManager  # noqa: E402


class HP_E3631A(DeviceManager):
    class Channel(enum.Enum):
        POSITIVE_6V = "P6V"
        POSITIVE_25V = "P25V"
        NEGATIVE_25V = "N25V"

    # Maps integer channel numbers (as used in the REPL) to Channel members.
    CHANNEL_FROM_NUMBER = {
        1: Channel.POSITIVE_6V,
        2: Channel.POSITIVE_25V,
        3: Channel.NEGATIVE_25V,
    }

    DEFAULT_CURRENT_LIMIT = {
        Channel.POSITIVE_6V: 1.0,
        Channel.POSITIVE_25V: 0.5,
        Channel.NEGATIVE_25V: 0.5,
    }

    # Hardware limits: (max_voltage_V, max_current_A)
    CHANNEL_LIMITS = {
        Channel.POSITIVE_6V: (6.0, 5.0),
        Channel.POSITIVE_25V: (25.0, 1.0),
        Channel.NEGATIVE_25V: (25.0, 1.0),
    }

    @classmethod
    def _check_channel(cls, channel) -> None:
        """Raise TypeError if *channel* is not an HP_E3631A.Channel member."""
        if not isinstance(channel, cls.Channel):
            valid = ", ".join(f"HP_E3631A.Channel.{m.name}" for m in cls.Channel)
            raise TypeError(f"channel must be HP_E3631A.Channel, got {type(channel).__name__!r}. Valid: {valid}")

    def __init__(self, resource_name):
        """Initialize the HP E3631A PSU."""
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
        """Disable output and zero all channel setpoints."""
        self.enable_output(False)
        for ch in HP_E3631A.Channel:
            self.send_command(f"APPLY {ch.value}, 0.0, 0.0")

    def enable_output(self, enabled: bool = True):
        """Enable or disable the power supply output."""
        state = "ON" if enabled else "OFF"
        self.send_command(f"OUTPUT:STATE {state}")

    def select_channel(self, channel: Channel):
        """Select the active channel.

        Args:
            channel: An HP_E3631A.Channel enum member.
        """
        self._check_channel(channel)
        self.send_command(f"INSTRUMENT:SELECT {channel.value}")

    def set_output_channel(self, channel: Channel, voltage, current_limit=None):
        """Set voltage and current limit for a channel using the APPLy shorthand.

        Args:
            channel: An HP_E3631A.Channel enum member.
            voltage: Desired output voltage.
            current_limit: Current limit — defaults to DEFAULT_CURRENT_LIMIT if omitted.
        """
        self._check_channel(channel)
        if current_limit is None:
            current_limit = self.DEFAULT_CURRENT_LIMIT[channel]
        self.send_command(f"APPLY {channel.value}, {voltage}, {current_limit}")

    def measure_voltage(self, channel: Channel) -> float:
        """Measure output voltage on *channel*.

        Args:
            channel: An HP_E3631A.Channel enum member.
        """
        self._check_channel(channel)
        self.select_channel(channel)
        response = self.query("MEASURE:VOLTAGE?")
        try:
            return float(response.strip().split()[0])
        except (ValueError, IndexError) as e:
            raise ValueError(f"Failed to convert voltage response '{response}' to float: {e}") from e

    def measure_current(self, channel: Channel) -> float:
        """Measure output current on *channel*.

        Args:
            channel: An HP_E3631A.Channel enum member.
        """
        self._check_channel(channel)
        self.select_channel(channel)
        response = self.query("MEASURE:CURRENT?")
        try:
            return float(response.strip().split()[0])
        except (ValueError, IndexError) as e:
            raise ValueError(f"Failed to convert current response '{response}' to float: {e}") from e

    def set_voltage(self, channel: Channel, voltage):
        """Set only the voltage for *channel* (does not change current limit).

        Args:
            channel: An HP_E3631A.Channel enum member.
            voltage: Desired voltage.
        """
        self._check_channel(channel)
        self.select_channel(channel)
        self.send_command(f"VOLTAGE {voltage}")

    def set_current_limit(self, channel: Channel, current):
        """Set only the current limit for *channel*.

        Args:
            channel: An HP_E3631A.Channel enum member.
            current: Desired current limit.
        """
        self._check_channel(channel)
        self.select_channel(channel)
        self.send_command(f"CURRENT {current}")

    def get_voltage_setpoint(self, channel: Channel | None = None) -> float:
        """Query the voltage setpoint for *channel* (or the currently selected channel).

        Args:
            channel: An HP_E3631A.Channel enum member, or None to use the
                     currently selected channel.
        """
        if channel is not None:
            self._check_channel(channel)
            self.select_channel(channel)
        resp = self.query("VOLTAGE?")
        return float(resp.strip().split()[0])

    def get_current_limit(self, channel: Channel | None = None) -> float:
        """Query the current limit for *channel* (or the currently selected channel).

        Args:
            channel: An HP_E3631A.Channel enum member, or None to use the
                     currently selected channel.
        """
        if channel is not None:
            self._check_channel(channel)
            self.select_channel(channel)
        resp = self.query("CURRENT?")
        return float(resp.strip().split()[0])

    def get_output_state(self) -> bool:
        """Query whether the output is enabled."""
        resp = self.query("OUTPUT:STATE?").strip()
        return resp in ("1", "ON")

    def get_error(self) -> str:
        """Read the most recent error from the error queue."""
        return self.query("SYSTEM:ERROR?")

    def set_tracking(self, enable: bool):
        """Enable or disable tracking mode for the ±25V supplies."""
        state = "ON" if enable else "OFF"
        self.send_command(f"OUTPUT:TRACK {state}")

    def save_state(self, location: int):
        """Save the current state to memory location 1, 2, or 3."""
        if location not in [1, 2, 3]:
            raise ValueError("Location must be 1, 2, or 3.")
        self.send_command(f"*SAV {location}")

    def recall_state(self, location: int):
        """Recall a saved state from memory location 1, 2, or 3."""
        if location not in [1, 2, 3]:
            raise ValueError("Location must be 1, 2, or 3.")
        self.send_command(f"*RCL {location}")
