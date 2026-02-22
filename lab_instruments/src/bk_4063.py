# BK Precision 4063
"""
Driver for the B&K Precision 4063 Function/Arbitrary Waveform Generator.
Instrument Type: Arbitrary Waveform Generator (AWG)
"""

from .device_manager import DeviceManager


class BK_4063(DeviceManager):
    """
    Driver for B&K Precision 4063 Dual Channel Arbitrary Waveform Generator.

    Based on 4060 Series Programming Manual.
    """

    CHANNEL_MAP = {1: "C1", 2: "C2"}

    VALID_WAVEFORMS = {"SINE", "SQUARE", "RAMP", "PULSE", "NOISE", "DC", "ARB"}

    # Accept SCPI abbreviations and common aliases in addition to full names
    _WAVE_ALIASES = {
        "SIN":      "SINE",
        "SQU":      "SQUARE",
        "PULS":     "PULSE",
        "NOIS":     "NOISE",
        "TRI":      "RAMP",
        "TRIANGLE": "RAMP",
    }

    def __init__(self, resource_name):
        """Initialize the BK 4063 AWG."""
        super().__init__(resource_name)

    def __enter__(self):
        """Context manager entry: clear status and reset."""
        self.clear_status()
        self.disable_all_channels()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Context manager exit: ensure safe state (outputs off)."""
        self.disable_all_channels()

    # ==========================================
    # OUTPUT CONTROL
    # ==========================================

    def disable_all_channels(self):
        """Disables output for all channels."""
        for channel in self.CHANNEL_MAP:
            self.enable_output(channel, False)

    def enable_output(self, channel, enabled: bool = True):
        """Enable or disable the output of the specified channel.

        Args:
            channel (int): Channel number (1 or 2).
            enabled (bool): True to enable, False to disable.
        """
        if channel not in self.CHANNEL_MAP:
            raise ValueError(
                f"Invalid channel. Must be one of: {list(self.CHANNEL_MAP.keys())}"
            )

        scpi_name = self.CHANNEL_MAP[channel]
        state = "ON" if enabled else "OFF"
        self.send_command(f"{scpi_name}:OUTPut {state}")

    def set_output_impedance(self, channel, load):
        """Set the output load impedance.

        Args:
            channel (int): Channel number (1 or 2).
            load (str|int): Load impedance in Ohms (e.g. 50) or 'HZ' for High-Z.
        """
        if channel not in self.CHANNEL_MAP:
            raise ValueError(
                f"Invalid channel. Must be one of: {list(self.CHANNEL_MAP.keys())}"
            )

        scpi_name = self.CHANNEL_MAP[channel]
        self.send_command(f"{scpi_name}:OUTPut LOAD,{load}")

    def set_sync_output(self, channel, enabled: bool):
        """Enable or disable sync output for the specified channel."""
        if channel not in self.CHANNEL_MAP:
            raise ValueError(
                f"Invalid channel. Must be one of: {list(self.CHANNEL_MAP.keys())}"
            )

        scpi_name = self.CHANNEL_MAP[channel]
        state = "ON" if enabled else "OFF"
        self.send_command(f"{scpi_name}:SYNC {state}")

    # ==========================================
    # WAVEFORM CONFIGURATION
    # ==========================================

    def set_waveform(
        self,
        channel,
        wave_type,
        frequency=None,
        amplitude=None,
        offset=None,
        phase=None,
        duty=None,
        symmetry=None,
    ):
        """
        Set waveform parameters for the specified channel.

        Args:
            channel (int): Channel number (1 or 2).
            wave_type (str): Waveform type (SINE, SQUARE, RAMP, PULSE, NOISE, DC, ARB).
            frequency (float): Frequency in Hz (not for NOISE/DC).
            amplitude (float): Amplitude in Vpp (not for NOISE/DC).
            offset (float): Offset in V (not for NOISE).
            phase (float): Phase in degrees (0-360).
            duty (float): Duty cycle in % (SQUARE/PULSE only).
            symmetry (float): Symmetry in % (RAMP only).
        """
        if channel not in self.CHANNEL_MAP:
            raise ValueError(
                f"Invalid channel. Must be one of: {list(self.CHANNEL_MAP.keys())}"
            )

        w_type = self._WAVE_ALIASES.get(wave_type.upper(), wave_type.upper())
        if w_type not in self.VALID_WAVEFORMS:
            raise ValueError(
                f"Invalid waveform type. Must be one of: {self.VALID_WAVEFORMS}"
            )

        scpi_name = self.CHANNEL_MAP[channel]

        # Build command string with all parameters
        cmd_parts = [f"{scpi_name}:BSWV WVTP,{w_type}"]

        if frequency is not None:
            cmd_parts.append(f"FRQ,{frequency}")
        if amplitude is not None:
            cmd_parts.append(f"AMP,{amplitude}")
        if offset is not None:
            cmd_parts.append(f"OFST,{offset}")
        if phase is not None:
            cmd_parts.append(f"PHSE,{phase}")
        if duty is not None:
            cmd_parts.append(f"DUTY,{duty}")
        if symmetry is not None:
            cmd_parts.append(f"SYM,{symmetry}")

        # Join with commas
        full_command = ",".join(cmd_parts)
        self.send_command(full_command)

    def set_dc_output(self, channel, voltage):
        """Configure channel for DC output."""
        self.set_waveform(channel, "DC", offset=voltage)

    # ==========================================
    # MODULATION, SWEEP & BURST
    # ==========================================

    def set_modulation(
        self, channel, state: bool, mod_type="AM", source="INT", **kwargs
    ):
        """
        Configure modulation for the specified channel.

        Args:
            channel (int): Channel number.
            state (bool): Enable or disable modulation.
            mod_type (str): AM, FM, PM, FSK, ASK, DSBAM, PWM.
            source (str): INT or EXT.
            **kwargs: Type-specific parameters (e.g., FRQ, DEPTH, DEVI).
        """
        if channel not in self.CHANNEL_MAP:
            raise ValueError("Invalid channel.")

        scpi_name = self.CHANNEL_MAP[channel]

        # 1. Set State
        st = "ON" if state else "OFF"
        self.send_command(f"{scpi_name}:MDWV STATE,{st}")

        if not state:
            return

        # 2. Configure Type and Parameters
        cmd_parts = [f"{scpi_name}:MDWV {mod_type.upper()}"]
        cmd_parts.append(f"SRC,{source.upper()}")

        for key, value in kwargs.items():
            cmd_parts.append(f"{key.upper()},{value}")

        self.send_command(",".join(cmd_parts))

    def set_sweep(self, channel, state: bool, **kwargs):
        """
        Configure frequency sweep.

        Args:
            channel (int): Channel number.
            state (bool): Enable or disable sweep.
            **kwargs: Sweep parameters (TIME, START, STOP, SOUCE, etc.).
        """
        if channel not in self.CHANNEL_MAP:
            raise ValueError("Invalid channel.")

        scpi_name = self.CHANNEL_MAP[channel]
        st = "ON" if state else "OFF"
        self.send_command(f"{scpi_name}:SWWV STATE,{st}")

        if state and kwargs:
            cmd_parts = [f"{scpi_name}:SWWV"]
            for key, value in kwargs.items():
                cmd_parts.append(f"{key.upper()},{value}")
            self.send_command(",".join(cmd_parts))

    def set_burst(self, channel, state: bool, **kwargs):
        """
        Configure burst mode.

        Args:
            channel (int): Channel number.
            state (bool): Enable or disable burst.
            **kwargs: Burst parameters (MODE, PRD, STPS, etc.).
        """
        if channel not in self.CHANNEL_MAP:
            raise ValueError("Invalid channel.")

        scpi_name = self.CHANNEL_MAP[channel]
        st = "ON" if state else "OFF"
        self.send_command(f"{scpi_name}:BTWV STATE,{st}")

        if state and kwargs:
            cmd_parts = [f"{scpi_name}:BTWV"]
            for key, value in kwargs.items():
                cmd_parts.append(f"{key.upper()},{value}")
            self.send_command(",".join(cmd_parts))

    # ==========================================
    # SYSTEM & UTILITY
    # ==========================================

    def copy_channel(self, dest_channel, src_channel):
        """Copy parameters from source channel to destination channel."""
        if dest_channel not in self.CHANNEL_MAP or src_channel not in self.CHANNEL_MAP:
            raise ValueError("Invalid channel.")

        dest = self.CHANNEL_MAP[dest_channel]
        src = self.CHANNEL_MAP[src_channel]
        self.send_command(f"PACP {dest},{src}")

    def get_error(self):
        """Reads the most recent error from the system error queue."""
        return self.query("SYSTem:ERRor?")
