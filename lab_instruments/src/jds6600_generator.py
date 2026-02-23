"""
Driver for JDS6600/Seesii DDS Signal Generator
Instrument Type: Dual-channel DDS Function/Arbitrary Waveform Generator

Protocol: ASCII commands over USB serial at 115200 baud
Based on JDS6600 communication protocol
"""

from .device_manager import DeviceManager
import pyvisa
import time


class JDS6600_Generator(DeviceManager):
    """
    Driver for JDS6600/Seesii DDS Signal Generator (Dual-channel, up to 60MHz).

    Uses ASCII protocol over USB serial at 115200 baud.
    Command format: :wNN=DATA.<CR><LF>
    """

    # Waveform types — codes per Joy-IT JDS6600 communication protocol
    WAVEFORMS = {
        'sine': 0,
        'square': 1,
        'pulse': 2,
        'triangle': 3,
        'partial_sine': 4,
        'cmos': 5,
        'dc': 6,
        'half_wave': 7,
        'full_wave': 8,
        'pos_ladder': 9,
        'neg_ladder': 10,
        'noise': 11,
        'exp_rise': 12,
        'exp_decay': 13,
        'multitone': 14,
        'sinc': 15,
        'lorenz': 16,
    }

    # Frequency units
    FREQ_UNITS = {
        'hz': 0,
        'khz': 1,
        'mhz': 2,
    }

    def __init__(self, resource_name):
        """Initialize the JDS6600 Generator."""
        super().__init__(resource_name)
        self._ch1_enabled = False
        self._ch2_enabled = False

    def connect(self):
        """Override to set serial communication parameters."""
        try:
            self.instrument = self.rm.open_resource(self.resource_name)
            self.instrument.timeout = 2000
            self.instrument.baud_rate = 115200
            self.instrument.data_bits = 8
            self.instrument.parity = pyvisa.constants.Parity.none
            self.instrument.stop_bits = pyvisa.constants.StopBits.one
            self.instrument.read_termination = "\r\n"
            self.instrument.write_termination = "\r\n"
            print(f"Connected to {self.resource_name}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to connect to {self.resource_name}: {e}")
            raise

    def _send_command(self, cmd: str) -> str:
        """
        Send a command and get response.

        Args:
            cmd: Command string (without terminator)

        Returns:
            Response string
        """
        self.instrument.write(cmd)

        # Only try to read response for read commands (:r)
        # Write commands (:w) typically just return :ok or nothing
        if cmd.startswith(':r'):
            time.sleep(0.05)  # Small delay for device to process
            try:
                response = self.instrument.read()
                return response.strip()
            except pyvisa.errors.VisaIOError:
                # Some commands don't respond
                return ""
        else:
            # For write commands, just give device time to process
            time.sleep(0.1)  # Slightly longer delay for write commands
            return ""

    def enable_output(self, ch1: bool = None, ch2: bool = None):
        """
        Enable or disable channel outputs.

        Args:
            ch1: Enable channel 1 if True, disable if False, keep current if None
            ch2: Enable channel 2 if True, disable if False, keep current if None
        """
        if ch1 is None:
            ch1 = self._ch1_enabled
        if ch2 is None:
            ch2 = self._ch2_enabled

        self._ch1_enabled = ch1
        self._ch2_enabled = ch2

        val1 = 1 if ch1 else 0
        val2 = 1 if ch2 else 0
        response = self._send_command(f":w20={val1},{val2}.")
        print(f"Output: CH1={'ON' if ch1 else 'OFF'}, CH2={'ON' if ch2 else 'OFF'}")

    def set_waveform(self, channel: int, waveform: str):
        """
        Set waveform type for a channel.

        Args:
            channel: Channel number (1 or 2)
            waveform: Waveform type (sine, square, triangle, pulse, dc, noise, etc.)
        """
        if channel not in (1, 2):
            raise ValueError("Channel must be 1 or 2")

        waveform = waveform.lower()
        if waveform not in self.WAVEFORMS:
            raise ValueError(f"Unknown waveform '{waveform}'. Valid: {list(self.WAVEFORMS.keys())}")

        code = self.WAVEFORMS[waveform]
        func_code = 21 if channel == 1 else 22
        response = self._send_command(f":w{func_code}={code}.")
        print(f"CH{channel} waveform: {waveform}")

    def set_frequency(self, channel: int, freq_hz: float):
        """
        Set frequency for a channel.

        Args:
            channel: Channel number (1 or 2)
            freq_hz: Frequency in Hz (0.01 Hz to 60 MHz depending on model)
        """
        if channel not in (1, 2):
            raise ValueError("Channel must be 1 or 2")

        # Use unit 0 (Hz mode with 0.01 Hz resolution) for most frequencies
        # Only switch to higher units if value would overflow
        # Unit 0: value * 0.01 Hz, max ~20 MHz with 32-bit int
        # Unit 1: value * 0.01 kHz (seems unreliable on some devices)
        # Unit 2: value * 0.01 MHz

        if freq_hz >= 20_000_000:
            # Very high frequency - use MHz mode
            # value * 0.01 MHz = freq_hz
            # value = freq_hz / 0.01 MHz = freq_hz / 10000
            value = int(freq_hz / 10_000)  # 0.01 MHz resolution
            unit = 2
            unit_str = "MHz"
            display_freq = freq_hz / 1_000_000
        else:
            # Use Hz mode for everything else (up to 20 MHz)
            # value * 0.01 Hz = freq_hz
            # value = freq_hz / 0.01 = freq_hz * 100
            value = int(freq_hz * 100)  # 0.01 Hz resolution
            unit = 0
            unit_str = "Hz" if freq_hz < 1000 else ("kHz" if freq_hz < 1_000_000 else "MHz")
            if freq_hz >= 1_000_000:
                display_freq = freq_hz / 1_000_000
                unit_str = "MHz"
            elif freq_hz >= 1_000:
                display_freq = freq_hz / 1_000
                unit_str = "kHz"
            else:
                display_freq = freq_hz
                unit_str = "Hz"

        func_code = 23 if channel == 1 else 24
        response = self._send_command(f":w{func_code}={value},{unit}.")
        print(f"CH{channel} frequency: {display_freq:.4f} {unit_str}")

    def set_amplitude(self, channel: int, amplitude_v: float):
        """
        Set amplitude (Vpp) for a channel.

        Args:
            channel: Channel number (1 or 2)
            amplitude_v: Amplitude in volts peak-to-peak (0.001V to ~20V depending on model)
        """
        if channel not in (1, 2):
            raise ValueError("Channel must be 1 or 2")

        # Value is in 0.001V (millivolt) steps
        value = int(amplitude_v * 1000)

        func_code = 25 if channel == 1 else 26
        response = self._send_command(f":w{func_code}={value}.")
        print(f"CH{channel} amplitude: {amplitude_v:.3f} Vpp")

    def set_duty_cycle(self, channel: int, duty_percent: float):
        """
        Set duty cycle for pulse/square waveforms.

        Args:
            channel: Channel number (1 or 2)
            duty_percent: Duty cycle percentage (0.1% to 99.9%)
        """
        if channel not in (1, 2):
            raise ValueError("Channel must be 1 or 2")

        if not (0.1 <= duty_percent <= 99.9):
            raise ValueError("Duty cycle must be between 0.1% and 99.9%")

        # Value is in 0.1% steps
        value = int(duty_percent * 10)

        func_code = 29 if channel == 1 else 30
        response = self._send_command(f":w{func_code}={value}.")
        print(f"CH{channel} duty cycle: {duty_percent:.1f}%")

    def set_offset(self, channel: int, offset_v: float):
        """
        Set DC offset for a channel.

        Args:
            channel: Channel number (1 or 2)
            offset_v: DC offset in volts (-10V to +10V typical range)
        """
        if channel not in (1, 2):
            raise ValueError("Channel must be 1 or 2")

        # Offset is encoded as unsigned value with 0.01V resolution
        # Range: 0 to 1999 maps to approximately -9.99V to +9.99V
        # Center (0V) is at value 1000
        # Formula: value = (offset_v + 10.0) * 100
        value = int((offset_v + 10.0) * 100)

        # Clamp to valid range
        value = max(0, min(1999, value))

        func_code = 27 if channel == 1 else 28
        response = self._send_command(f":w{func_code}={value}.")
        print(f"CH{channel} offset: {offset_v:.3f} V")

    def set_phase(self, channel: int, phase_deg: float):
        """
        Set phase for a channel.

        Args:
            channel: Channel number (1 or 2)
            phase_deg: Phase in degrees (0 to 359.9)
        """
        if channel not in (1, 2):
            raise ValueError("Channel must be 1 or 2")

        if not (0 <= phase_deg < 360):
            raise ValueError("Phase must be between 0 and 360 degrees")

        # Value is in 0.1 degree steps
        value = int(phase_deg * 10)

        func_code = 31 if channel == 1 else 32
        response = self._send_command(f":w{func_code}={value}.")
        print(f"CH{channel} phase: {phase_deg:.1f} degrees")

    def set_sync(self, freq: bool = False, waveform: bool = False,
                 amplitude: bool = False, offset: bool = False, duty: bool = False):
        """
        Set channel synchronization (CH2 follows CH1).

        Args:
            freq: Synchronize frequency
            waveform: Synchronize waveform type
            amplitude: Synchronize amplitude
            offset: Synchronize DC offset
            duty: Synchronize duty cycle
        """
        val_freq = 1 if freq else 0
        val_wave = 1 if waveform else 0
        val_amp = 1 if amplitude else 0
        val_offset = 1 if offset else 0
        val_duty = 1 if duty else 0

        response = self._send_command(
            f":w54={val_freq},{val_wave},{val_amp},{val_offset},{val_duty}."
        )

        sync_list = []
        if freq: sync_list.append("frequency")
        if waveform: sync_list.append("waveform")
        if amplitude: sync_list.append("amplitude")
        if offset: sync_list.append("offset")
        if duty: sync_list.append("duty")

        if sync_list:
            print(f"Sync enabled: {', '.join(sync_list)}")
        else:
            print("Sync disabled (channels independent)")

    def disable_output(self):
        """Disable both channel outputs for safety."""
        self.enable_output(False, False)

    def __repr__(self):
        """String representation for debugging."""
        return f"JDS6600_Generator(resource={self.resource_name})"
