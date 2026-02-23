"""
Driver for Rigol DHO804 Digital Oscilloscope
Instrument Type: 4-channel 70 MHz oscilloscope

Protocol: SCPI over USB-TMC/VISA
Based on DHO800/DHO900 Programming Guide
"""

from .device_manager import DeviceManager
import pyvisa
import time
import numpy as np
from dataclasses import dataclass
from typing import Optional


@dataclass
class WaveformData:
    """
    Container for oscilloscope waveform data.

    Attributes:
        time: Time values in seconds (numpy array)
        voltage: Voltage values in volts (numpy array)
        channel: Source channel number (1-4) or string ('MATH1', etc.)
        sample_rate: Effective sample rate in samples per second
        points: Number of data points
        time_per_div: Horizontal scale in seconds per division
        volts_per_div: Vertical scale in volts per division
    """
    time: np.ndarray
    voltage: np.ndarray
    channel: int
    sample_rate: float
    points: int
    time_per_div: float = 0.0
    volts_per_div: float = 0.0

    def __len__(self) -> int:
        """Return number of points in waveform."""
        return len(self.time)

    def plot(self, title: Optional[str] = None):
        """
        Plot waveform using matplotlib.

        Args:
            title: Optional custom title for the plot
        """
        try:
            import matplotlib.pyplot as plt

            plt.figure(figsize=(12, 6))
            plt.plot(self.time * 1e3, self.voltage)  # time in ms
            plt.xlabel('Time (ms)')
            plt.ylabel('Voltage (V)')
            plt.title(title or f'Channel {self.channel} Waveform')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.show()
        except ImportError:
            print("matplotlib not installed. Install with: pip install matplotlib")


class Rigol_DHO804(DeviceManager):
    """
    Driver for Rigol DHO804 4-channel digital oscilloscope.

    Uses standard SCPI commands over USB-TMC/VISA.
    """

    def connect(self):
        """Connect to the Rigol DHO804 oscilloscope."""
        try:
            self.instrument = self.rm.open_resource(self.resource_name)
            self.instrument.timeout = 5000  # 5 second timeout
            self.instrument.write_termination = "\n"
            self.instrument.read_termination = "\n"
            print(f"Connected to {self.resource_name}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to connect to {self.resource_name}: {e}")
            raise

    def disconnect(self):
        """Disconnect from the oscilloscope."""
        if self.instrument:
            self.instrument.close()
            print(f"Disconnected from {self.resource_name}")

    # Channel control
    def enable_channel(self, channel: int):
        """Enable a channel."""
        if channel not in (1, 2, 3, 4):
            raise ValueError("Channel must be 1-4")
        self.instrument.write(f":CHANnel{channel}:DISPlay ON")
        print(f"CH{channel} enabled")

    def disable_channel(self, channel: int):
        """Disable a channel."""
        if channel not in (1, 2, 3, 4):
            raise ValueError("Channel must be 1-4")
        self.instrument.write(f":CHANnel{channel}:DISPlay OFF")
        print(f"CH{channel} disabled")

    def set_vertical_scale(self, channel: int, volts_per_div: float, offset: float = 0.0):
        """
        Set vertical scale and offset for a channel.

        Args:
            channel: Channel number (1-4)
            volts_per_div: Vertical scale in volts per division
            offset: Vertical offset in volts
        """
        if channel not in (1, 2, 3, 4):
            raise ValueError("Channel must be 1-4")

        self.instrument.write(f":CHANnel{channel}:SCALe {volts_per_div}")
        self.instrument.write(f":CHANnel{channel}:OFFSet {offset}")
        print(f"CH{channel}: {volts_per_div} V/div, offset {offset} V")

    def set_coupling(self, channel: int, coupling: str):
        """
        Set channel coupling.

        Args:
            channel: Channel number (1-4)
            coupling: 'DC', 'AC', or 'GND'
        """
        if channel not in (1, 2, 3, 4):
            raise ValueError("Channel must be 1-4")
        coupling = coupling.upper()
        if coupling not in ('DC', 'AC', 'GND'):
            raise ValueError("Coupling must be 'DC', 'AC', or 'GND'")

        self.instrument.write(f":CHANnel{channel}:COUPling {coupling}")
        print(f"CH{channel} coupling: {coupling}")

    def set_bandwidth_limit(self, channel: int, limit: str) -> None:
        """
        Set bandwidth limit for a channel.

        Reference: pdf_chapters/3.6.1_CHANnel_n__BWLimit.pdf

        Args:
            channel: Channel number (1-4)
            limit: '20M' for 20MHz limit, 'OFF' to disable

        Notes:
            Bandwidth limiting reduces noise and high-frequency components.
            Useful for cleaner signal display and measurements.

        Raises:
            ValueError: If channel or limit is invalid
            pyvisa.VisaIOError: If communication fails
        """
        if channel not in (1, 2, 3, 4):
            raise ValueError(f"Channel must be 1-4, got {channel}")

        limit = limit.upper()
        if limit not in ('20M', 'OFF'):
            raise ValueError(f"Limit must be '20M' or 'OFF', got {limit}")

        try:
            self.instrument.write(f":CHANnel{channel}:BWLimit {limit}")
            print(f"CH{channel} bandwidth limit: {limit}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set bandwidth limit: {e}")
            raise

    def invert_channel(self, channel: int, enable: bool) -> None:
        """
        Invert the waveform display.

        Reference: pdf_chapters/3.6.4_CHANnel_n__INVert.pdf

        Args:
            channel: Channel number (1-4)
            enable: True to invert waveform, False for normal display

        Notes:
            When enabled, voltage values are inverted (flipped vertically).
            Useful for comparing signals or viewing negative logic.

        Raises:
            ValueError: If channel is invalid
            pyvisa.VisaIOError: If communication fails
        """
        if channel not in (1, 2, 3, 4):
            raise ValueError(f"Channel must be 1-4, got {channel}")

        value = 'ON' if enable else 'OFF'

        try:
            self.instrument.write(f":CHANnel{channel}:INVert {value}")
            state = "inverted" if enable else "normal"
            print(f"CH{channel} display: {state}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set invert: {e}")
            raise

    def set_probe_ratio(self, channel: int, ratio: float) -> None:
        """
        Set probe attenuation ratio.

        Reference: pdf_chapters/3.6.8_CHANnel_n__PROBe.pdf

        Args:
            channel: Channel number (1-4)
            ratio: Probe attenuation ratio
                  Common values: 1, 10, 100, 1000
                  Valid: 0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2,
                        0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000,
                        2000, 5000, 10000, 20000, 50000

        Notes:
            - Display amplitude = Actual amplitude × Probe ratio
            - 1X probe: Direct connection (ratio = 1)
            - 10X probe: 10:1 attenuation (ratio = 10)
            - 100X probe: 100:1 attenuation (ratio = 100)
            - Probe ratio affects vertical scale range

        Raises:
            ValueError: If channel or ratio is invalid
            pyvisa.VisaIOError: If communication fails
        """
        if channel not in (1, 2, 3, 4):
            raise ValueError(f"Channel must be 1-4, got {channel}")

        valid_ratios = [
            0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5,
            10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000
        ]
        if ratio not in valid_ratios:
            raise ValueError(f"Invalid probe ratio: {ratio}")

        try:
            self.instrument.write(f":CHANnel{channel}:PROBe {ratio:g}")
            print(f"CH{channel} probe ratio: {ratio:g}X")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set probe ratio: {e}")
            raise

    def set_probe_attenuation(self, channel: int, ratio: float) -> None:
        """Alias for set_probe_ratio."""
        self.set_probe_ratio(channel, ratio)

    def set_channel_position(self, channel: int, position: float) -> None:
        """
        Set vertical position (bias voltage) of the channel.

        Reference: pdf_chapters/3.6.13_CHANnel_n__POSition.pdf

        Args:
            channel: Channel number (1-4)
            position: Vertical position offset in volts
                     Moves waveform up (positive) or down (negative)

        Notes:
            - Adjusts where the waveform appears vertically on screen
            - Does not affect actual signal or measurements
            - Useful for separating multiple waveforms

        Raises:
            ValueError: If channel is invalid
            pyvisa.VisaIOError: If communication fails
        """
        if channel not in (1, 2, 3, 4):
            raise ValueError(f"Channel must be 1-4, got {channel}")

        try:
            self.instrument.write(f":CHANnel{channel}:POSition {position}")
            print(f"CH{channel} vertical position: {position} V")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set position: {e}")
            raise

    def get_channel_position(self, channel: int) -> float:
        """
        Get vertical position (bias voltage) of the channel.

        Reference: pdf_chapters/3.6.13_CHANnel_n__POSition.pdf

        Args:
            channel: Channel number (1-4)

        Returns:
            float: Current vertical position offset in volts

        Raises:
            ValueError: If channel is invalid
            pyvisa.VisaIOError: If communication fails
        """
        if channel not in (1, 2, 3, 4):
            raise ValueError(f"Channel must be 1-4, got {channel}")

        try:
            response = self.instrument.query(f":CHANnel{channel}:POSition?")
            return float(response.strip())
        except pyvisa.VisaIOError as e:
            print(f"Failed to get position: {e}")
            raise

    def set_vertical_position(self, channel: int, position: float) -> None:
        """
        Alias for set_channel_position for API compatibility.

        Args:
            channel: Channel number (1-4)
            position: Vertical position offset in volts
        """
        self.set_channel_position(channel, position)

    def get_vertical_position(self, channel: int) -> float:
        """
        Alias for get_channel_position for API compatibility.

        Args:
            channel: Channel number (1-4)

        Returns:
            float: Current vertical position offset in volts
        """
        return self.get_channel_position(channel)

    def move_vertical(self, channel: int, delta: float) -> None:
        """
        Move a channel vertically by a delta amount.

        Args:
            channel: Channel number (1-4)
            delta: Amount to move in volts (positive = up, negative = down)

        Raises:
            ValueError: If channel is invalid
            pyvisa.VisaIOError: If communication fails
        """
        current_pos = self.get_channel_position(channel)
        new_pos = current_pos + delta
        self.set_channel_position(channel, new_pos)

    def set_channel_label(self, channel: int, label: str, show: bool = True) -> None:
        """
        Set channel label text and visibility.

        Reference:
            - pdf_chapters/3.6.9_CHANnel_n__LABel_SHOW.pdf
            - pdf_chapters/3.6.10_CHANnel_n__LABel_CONTent.pdf

        Args:
            channel: Channel number (1-4)
            label: Label text to display
            show: True to show label, False to hide

        Notes:
            Labels appear on the waveform display for easy identification.
            Useful for marking signals in multi-channel setups.

        Raises:
            ValueError: If channel is invalid
            pyvisa.VisaIOError: If communication fails
        """
        if channel not in (1, 2, 3, 4):
            raise ValueError(f"Channel must be 1-4, got {channel}")

        try:
            # Set label content
            self.instrument.write(f':CHANnel{channel}:LABel:CONTent "{label}"')

            # Set label visibility
            show_value = 'ON' if show else 'OFF'
            self.instrument.write(f":CHANnel{channel}:LABel:SHOW {show_value}")

            state = "visible" if show else "hidden"
            print(f'CH{channel} label: "{label}" ({state})')
        except pyvisa.VisaIOError as e:
            print(f"Failed to set channel label: {e}")
            raise

    def set_vernier(self, channel: int, enable: bool) -> None:
        """
        Enable/disable fine vertical scale adjustment.

        Reference: pdf_chapters/3.6.12_CHANnel_n__VERNier.pdf

        Args:
            channel: Channel number (1-4)
            enable: True for fine adjustment, False for coarse (1-2-5 steps)

        Notes:
            When enabled, allows finer control of vertical scale between
            standard 1-2-5 sequence steps. Improves vertical resolution
            for viewing waveform details.

        Raises:
            ValueError: If channel is invalid
            pyvisa.VisaIOError: If communication fails
        """
        if channel not in (1, 2, 3, 4):
            raise ValueError(f"Channel must be 1-4, got {channel}")

        value = 'ON' if enable else 'OFF'

        try:
            self.instrument.write(f":CHANnel{channel}:VERNier {value}")
            mode = "fine" if enable else "coarse"
            print(f"CH{channel} vertical scale mode: {mode}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set vernier: {e}")
            raise

    # ========================================
    # Timebase Control (Section 3.26)
    # Reference: pdf_chapters/3.26*.pdf
    # ========================================

    def set_horizontal_scale(self, seconds_per_div: float) -> None:
        """
        Set horizontal timebase scale.

        Reference: pdf_chapters/3.26.5_TIMebase[_MAIN]_SCALe.pdf

        Args:
            seconds_per_div: Time per division in seconds
                           Common values: 1ns to 1000s (1-2-5 sequence)

        Raises:
            pyvisa.VisaIOError: If communication fails
        """
        try:
            self.instrument.write(f":TIMebase:SCALe {seconds_per_div}")
            print(f"Timebase: {seconds_per_div} s/div")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set horizontal scale: {e}")
            raise

    def set_horizontal_offset(self, offset: float) -> None:
        """
        Set horizontal offset (time position).

        Reference: pdf_chapters/3.26.4_TIMebase[_MAIN][_OFFSet].pdf

        Args:
            offset: Time offset in seconds
                   Negative = waveform shifts left (earlier time visible)
                   Positive = waveform shifts right (later time visible)
                   Zero = trigger point at center

        Notes:
            Offset range depends on timebase scale and memory depth.

        Raises:
            pyvisa.VisaIOError: If communication fails
        """
        try:
            self.instrument.write(f":TIMebase:MAIN:OFFSet {offset}")
            print(f"Horizontal offset: {offset} s")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set horizontal offset: {e}")
            raise

    def set_timebase_mode(self, mode: str) -> None:
        """
        Set horizontal timebase mode.

        Reference: pdf_chapters/3.26.6_TIMebase_MODE.pdf

        Args:
            mode: 'MAIN' (YT mode - voltage vs time, default)
                  'XY' (XY mode - voltage vs voltage)
                  'ROLL' (roll mode - continuous scrolling)

        Notes:
            - MAIN/YT: Standard oscilloscope display (Y=voltage, X=time)
            - XY: Phase measurement mode (both axes show voltage)
            - ROLL: Auto-enabled at timebase ≥50ms/div
                   Waveform scrolls right to left continuously
                   Trigger disabled in ROLL mode

        Raises:
            ValueError: If mode is invalid
            pyvisa.VisaIOError: If communication fails
        """
        mode = mode.upper()
        if mode not in ('MAIN', 'XY', 'ROLL'):
            raise ValueError(f"Mode must be 'MAIN', 'XY', or 'ROLL', got {mode}")

        try:
            self.instrument.write(f":TIMebase:MODE {mode}")
            print(f"Timebase mode: {mode}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set timebase mode: {e}")
            raise

    def enable_delayed_timebase(self, enable: bool) -> None:
        """
        Enable/disable delayed (zoom) timebase.

        Reference: pdf_chapters/3.26.1_TIMebase_DELay_ENABle.pdf

        Args:
            enable: True to enable zoom window, False to disable

        Notes:
            Delayed sweep (zoom) allows you to magnify a portion of the
            main waveform for detailed viewing. Use set_delayed_scale()
            and set_delayed_offset() to control the zoom window.

        Raises:
            pyvisa.VisaIOError: If communication fails
        """
        value = 'ON' if enable else 'OFF'

        try:
            self.instrument.write(f":TIMebase:DELay:ENABle {value}")
            state = "enabled" if enable else "disabled"
            print(f"Delayed timebase (zoom): {state}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set delayed timebase: {e}")
            raise

    def set_delayed_offset(self, offset: float) -> None:
        """
        Set delayed timebase offset (zoom window position).

        Reference: pdf_chapters/3.26.2_TIMebase_DELay_OFFSet.pdf

        Args:
            offset: Position of zoom window in seconds

        Notes:
            Controls where the zoomed region appears on the main waveform.
            Range formula:
            - LeftTime = 5 × MainScale - MainOffset
            - RightTime = 5 × MainScale + MainOffset
            - DelayRange = 10 × DelayScale
            - Range: -(LeftTime - DelayRange/2) to (RightTime - DelayRange/2)

        Raises:
            pyvisa.VisaIOError: If communication fails
        """
        try:
            self.instrument.write(f":TIMebase:DELay:OFFSet {offset}")
            print(f"Delayed offset: {offset} s")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set delayed offset: {e}")
            raise

    def set_delayed_scale(self, scale: float) -> None:
        """
        Set delayed timebase scale (zoom level).

        Reference: pdf_chapters/3.26.3_TIMebase_DELay_SCALe.pdf

        Args:
            scale: Time per division for zoom window (seconds)
                  Must be ≤ current main timebase scale
                  Uses 1-2-5 step sequence

        Notes:
            Smaller scale = higher magnification (more zoom).
            Maximum value is the current main timebase scale.

        Raises:
            pyvisa.VisaIOError: If communication fails
        """
        try:
            self.instrument.write(f":TIMebase:DELay:SCALe {scale}")
            print(f"Delayed scale: {scale} s/div (zoom)")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set delayed scale: {e}")
            raise

    def enable_xy_mode(self, enable: bool = True, x_channel: int = 1,
                      y_channel: int = 2) -> None:
        """
        Enable/disable XY display mode.

        Reference: pdf_chapters/3.26.12_TIMebase_XY_ENABle.pdf

        Args:
            enable: True to enable XY mode, False for normal time display
            x_channel: Channel for X axis (1-4), only used when enabling
            y_channel: Channel for Y axis (1-4), only used when enabling

        Notes:
            XY mode displays voltage vs voltage (instead of voltage vs time).
            Useful for:
            - Phase measurements (Lissajous patterns)
            - Transfer function analysis
            - Frequency comparison

            X and Y channel assignments require separate commands if needed.
            See :TIMebase:XY:X and :TIMebase:XY:Y commands.

        Raises:
            ValueError: If channel numbers are invalid
            pyvisa.VisaIOError: If communication fails
        """
        if x_channel not in (1, 2, 3, 4) or y_channel not in (1, 2, 3, 4):
            raise ValueError("Channels must be 1-4")

        value = 'ON' if enable else 'OFF'

        try:
            self.instrument.write(f":TIMebase:XY:ENABle {value}")

            if enable:
                # Note: X and Y channel configuration would go here
                # if the commands :TIMebase:XY:X and :TIMebase:XY:Y are needed
                print(f"XY mode enabled (X=CH{x_channel}, Y=CH{y_channel})")
            else:
                print("XY mode disabled (back to time display)")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set XY mode: {e}")
            raise

    # Trigger control
    def configure_trigger(self, channel: int, level: float, slope: str = 'RISE', mode: str = 'AUTO'):
        """
        Configure edge trigger.

        Args:
            channel: Trigger source channel (1-4)
            level: Trigger level in volts
            slope: 'RISE' (POSitive), 'FALL' (NEGative), or 'RFALL'
            mode: Trigger mode (not directly settable via simple command, scope uses sweep mode)
        """
        if channel not in (1, 2, 3, 4):
            raise ValueError("Channel must be 1-4")

        # Map common slope names to Rigol SCPI
        slope_map = {
            'RISE': 'POSitive',
            'FALL': 'NEGative',
            'RFALL': 'RFALl',
            'POSITIVE': 'POSitive',
            'NEGATIVE': 'NEGative'
        }
        slope_cmd = slope_map.get(slope.upper(), 'POSitive')

        self.instrument.write(":TRIGger:MODE EDGE")
        self.instrument.write(f":TRIGger:EDGE:SOURce CHAN{channel}")
        self.instrument.write(f":TRIGger:EDGE:SLOPe {slope_cmd}")
        self.instrument.write(f":TRIGger:EDGE:LEVel {level}")
        print(f"Trigger: CH{channel}, {level}V, {slope}")

    # ========================================
    # Trigger Control (Section 3.27)
    # Reference: pdf_chapters/3.27*.pdf
    # ========================================

    def set_trigger_sweep(self, sweep: str) -> None:
        """
        Set trigger sweep mode.

        Reference: pdf_chapters/3.27.4_TRIGger_SWEep.pdf

        Args:
            sweep: Trigger sweep mode
                   'AUTO' - Auto trigger, always displays waveforms
                   'NORMal' - Normal trigger, only when conditions met
                   'SINGle' - Single trigger, one acquisition then stop

        Notes:
            - AUTO: Waveforms displayed regardless of trigger conditions
            - NORMal: Only displays when triggered, waits otherwise
            - SINGle: Same as single() method, one shot acquisition

        Raises:
            ValueError: If sweep mode is invalid
            pyvisa.VisaIOError: If communication fails
        """
        sweep = sweep.upper()
        if sweep not in ('AUTO', 'NORMAL', 'SINGLE'):
            raise ValueError(f"Sweep must be 'AUTO', 'NORMAL', or 'SINGLE', got {sweep}")

        try:
            self.instrument.write(f":TRIGger:SWEep {sweep}")
            print(f"Trigger sweep mode: {sweep}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set trigger sweep: {e}")
            raise

    def set_trigger_coupling(self, coupling: str) -> None:
        """
        Set trigger coupling type.

        Reference: pdf_chapters/3.27.2_TRIGger_COUPling.pdf

        Args:
            coupling: Trigger coupling type
                     'DC' - DC and AC components pass (default)
                     'AC' - Blocks DC components
                     'LFReject' - Rejects low frequency components
                     'HFReject' - Rejects high frequency components

        Notes:
            - Only available for Edge trigger with analog channel source
            - AC coupling blocks DC offset
            - LF reject blocks DC and low frequencies
            - HF reject attenuates high frequencies

        Raises:
            ValueError: If coupling type is invalid
            pyvisa.VisaIOError: If communication fails
        """
        coupling = coupling.upper()
        if coupling not in ('DC', 'AC', 'LFREJECT', 'HFREJECT'):
            raise ValueError(f"Coupling must be 'DC', 'AC', 'LFReject', or 'HFReject', got {coupling}")

        try:
            self.instrument.write(f":TRIGger:COUPling {coupling}")
            print(f"Trigger coupling: {coupling}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set trigger coupling: {e}")
            raise

    def set_trigger_holdoff(self, time: float) -> None:
        """
        Set trigger holdoff time.

        Reference: pdf_chapters/3.27.5_TRIGger_HOLDoff.pdf

        Args:
            time: Holdoff time in seconds (8ns to 10s)
                  Oscilloscope ignores triggers during holdoff period

        Notes:
            - Useful for stable triggering on complex waveforms (e.g., pulse trains)
            - Oscilloscope waits for holdoff time before re-arming trigger
            - Not available for: Video, Timeout, Setup&Hold, Nth Edge, and
              serial protocol triggers (RS232, I2C, SPI, CAN, LIN)

        Raises:
            ValueError: If time is out of range
            pyvisa.VisaIOError: If communication fails
        """
        if not (8e-9 <= time <= 10.0):
            raise ValueError(f"Holdoff time must be 8ns to 10s, got {time}s")

        try:
            self.instrument.write(f":TRIGger:HOLDoff {time}")
            print(f"Trigger holdoff: {time} s")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set trigger holdoff: {e}")
            raise

    def get_trigger_status(self) -> str:
        """
        Query current trigger status.

        Reference: pdf_chapters/3.27.3_TRIGger_STATus_.pdf

        Returns:
            str: Trigger status
                 'TD' - Triggered
                 'WAIT' - Waiting for trigger
                 'RUN' - Running (AUTO mode, no trigger)
                 'AUTO' - Auto trigger
                 'STOP' - Stopped

        Raises:
            pyvisa.VisaIOError: If communication fails
        """
        try:
            status = self.instrument.query(":TRIGger:STATus?").strip()
            return status
        except pyvisa.VisaIOError as e:
            print(f"Failed to query trigger status: {e}")
            raise

    def configure_pulse_trigger(self, source: int, polarity: str,
                               when: str, width_lower: float,
                               width_upper: float = None,
                               level: float = 0.0) -> None:
        """
        Configure pulse width trigger.

        Reference: pdf_chapters/3.27.9_TRIGger_PULSe.pdf

        Triggers on positive or negative pulses of specified width.
        Positive pulse width is time between two trigger level crossings
        on positive pulse. Negative pulse width is for negative pulse.

        Args:
            source: Trigger source channel (1-4)
            polarity: Pulse polarity
                     'POSitive' - Positive pulses
                     'NEGative' - Negative pulses
            when: Width condition
                  'GREater' - Pulse width > lower limit
                  'LESS' - Pulse width < upper limit
                  'GLESs' - Lower limit < pulse width < upper limit
            width_lower: Lower width limit in seconds (1ns minimum)
            width_upper: Upper width limit in seconds (required for LESS/GLESs)
            level: Trigger level in volts (default 0.0)

        Notes:
            - GREater: width > width_lower
            - LESS: width < width_upper
            - GLESs: width_lower < width < width_upper

        Raises:
            ValueError: If parameters are invalid
            pyvisa.VisaIOError: If communication fails
        """
        if source not in (1, 2, 3, 4):
            raise ValueError(f"Source must be 1-4, got {source}")

        polarity = polarity.upper()
        if polarity not in ('POSITIVE', 'NEGATIVE'):
            raise ValueError(f"Polarity must be 'POSitive' or 'NEGative', got {polarity}")

        when = when.upper()
        if when not in ('GREATER', 'LESS', 'GLESS'):
            raise ValueError(f"When must be 'GREater', 'LESS', or 'GLESs', got {when}")

        try:
            self.instrument.write(":TRIGger:MODE PULSe")
            self.instrument.write(f":TRIGger:PULSe:SOURce CHAN{source}")
            self.instrument.write(f":TRIGger:PULSe:POLarity {polarity}")
            self.instrument.write(f":TRIGger:PULSe:WHEN {when}")

            if when in ('GREATER', 'GLESS'):
                self.instrument.write(f":TRIGger:PULSe:LWIDth {width_lower}")

            if when in ('LESS', 'GLESS'):
                if width_upper is None:
                    raise ValueError("width_upper required for LESS/GLESs mode")
                self.instrument.write(f":TRIGger:PULSe:UWIDth {width_upper}")

            self.instrument.write(f":TRIGger:PULSe:LEVel {level}")

            print(f"Pulse trigger: CH{source}, {polarity}, {when}, lower={width_lower}s")
            if width_upper:
                print(f"  Upper width: {width_upper}s")
        except pyvisa.VisaIOError as e:
            print(f"Failed to configure pulse trigger: {e}")
            raise

    def configure_timeout_trigger(self, source: int, slope: str,
                                  timeout: float, level: float = 0.0) -> None:
        """
        Configure timeout trigger.

        Reference: pdf_chapters/3.27.14_TRIGger_TIMeout.pdf

        Triggers when time interval between edges exceeds timeout value.
        The interval (ΔT) is from when one edge passes through trigger level
        to when the opposite edge passes through trigger level.

        Args:
            source: Trigger source channel (1-4)
            slope: Edge type to start timing
                   'POSitive' - Start on rising edge
                   'NEGative' - Start on falling edge
                   'RFALl' - Start on either edge
            timeout: Timeout period in seconds (1ns to 10s)
            level: Trigger level in volts (default 0.0)

        Notes:
            - POSitive: Times from rising edge to next falling edge
            - NEGative: Times from falling edge to next rising edge
            - RFALl: Times from any edge to next opposite edge
            - Triggers when ΔT > timeout value

        Raises:
            ValueError: If parameters are invalid
            pyvisa.VisaIOError: If communication fails
        """
        if source not in (1, 2, 3, 4):
            raise ValueError(f"Source must be 1-4, got {source}")

        slope = slope.upper()
        if slope not in ('POSITIVE', 'NEGATIVE', 'RFALL'):
            raise ValueError(f"Slope must be 'POSitive', 'NEGative', or 'RFALl', got {slope}")

        if not (1e-9 <= timeout <= 10.0):
            raise ValueError(f"Timeout must be 1ns to 10s, got {timeout}s")

        try:
            self.instrument.write(":TRIGger:MODE TIMeout")
            self.instrument.write(f":TRIGger:TIMeout:SOURce CHAN{source}")
            self.instrument.write(f":TRIGger:TIMeout:SLOPe {slope}")
            self.instrument.write(f":TRIGger:TIMeout:TIME {timeout}")
            self.instrument.write(f":TRIGger:TIMeout:LEVel {level}")

            print(f"Timeout trigger: CH{source}, {slope}, timeout={timeout}s, level={level}V")
        except pyvisa.VisaIOError as e:
            print(f"Failed to configure timeout trigger: {e}")
            raise

    # ========================================
    # Root Commands (Section 3.1)
    # Reference: pdf_chapters/3.1*.pdf
    # ========================================

    def clear(self) -> None:
        """
        Clear all waveforms on the screen.

        Reference: pdf_chapters/3.1.1_CLEar.pdf

        This command functions the same as the front-panel CLEAR key.
        Clears all displayed waveforms without affecting instrument settings.

        Raises:
            pyvisa.VisaIOError: If communication fails
        """
        try:
            self.instrument.write(":CLEar")
            print("Display cleared")
        except pyvisa.VisaIOError as e:
            print(f"Failed to clear display: {e}")
            raise

    def run(self) -> None:
        """
        Start running the oscilloscope (continuous acquisition).

        Reference: pdf_chapters/3.1.2_RUN.pdf

        Starts the oscilloscope in continuous acquisition mode. The scope will
        continuously acquire and display waveforms based on the current trigger settings.

        This command functions the same as the RUN button on the front panel.

        Raises:
            pyvisa.VisaIOError: If communication fails
        """
        try:
            self.instrument.write(":RUN")
            print("Oscilloscope running")
        except pyvisa.VisaIOError as e:
            print(f"Failed to start acquisition: {e}")
            raise

    def stop(self) -> None:
        """
        Stop the oscilloscope acquisition.

        Reference: pdf_chapters/3.1.3_STOP.pdf

        Stops the oscilloscope from acquiring new waveforms. The current waveform
        remains displayed on screen and can be analyzed.

        This command functions the same as the STOP button on the front panel.

        Raises:
            pyvisa.VisaIOError: If communication fails
        """
        try:
            self.instrument.write(":STOP")
            print("Oscilloscope stopped")
        except pyvisa.VisaIOError as e:
            print(f"Failed to stop acquisition: {e}")
            raise

    def single(self) -> None:
        """
        Set oscilloscope to single trigger mode and arm for one acquisition.

        Reference: pdf_chapters/3.1.4_SINGle.pdf

        Sets the trigger mode to "Single" and arms the oscilloscope. The scope will
        wait for a trigger event, capture one waveform when triggered, then stop.

        This command is equivalent to :TRIGger:SWEep SINGle and functions the
        same as the SINGLE button on the front panel.

        Notes:
            - In single trigger mode, the oscilloscope performs a single trigger
              when conditions are met and then stops
            - Invalid when waveform recording is enabled or during playback
            - Use force_trigger() to generate a trigger by force in single mode

        Raises:
            pyvisa.VisaIOError: If communication fails
        """
        try:
            self.instrument.write(":SINGle")
            print("Single trigger armed")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set single trigger: {e}")
            raise

    def wait_for_stop(self, timeout: float = 10.0) -> bool:
        """Poll trigger status until the scope stops (TD or STOP state).

        Call after single() to block until the trigger fires and the scope
        has captured and frozen the waveform. Returns True if the scope
        stopped within the timeout, False if the timeout expired while the
        scope was still armed (WAIT state).

        Args:
            timeout: Maximum seconds to wait (default 10.0)

        Returns:
            bool: True if scope stopped (trigger fired), False if timed out
        """
        import time
        time.sleep(0.1)  # Let the scope process :SINGle before polling
        deadline = time.time() + timeout
        while time.time() < deadline:
            status = self.get_trigger_status()
            if status == 'STOP':
                # Scope stopped; give DSP a moment to begin computing measurements
                time.sleep(0.5)
                return True
            time.sleep(0.2)
        return False

    def force_trigger(self) -> None:
        """
        Generate a trigger signal forcefully.

        Reference: pdf_chapters/3.1.5_TFORce.pdf

        Forces a trigger event regardless of the actual trigger conditions.
        This command is only applicable in NORMAL and SINGLE trigger modes
        (not AUTO mode).

        This command functions the same as the FORCE button in the trigger
        control area of the front panel.

        Notes:
            - Only works in NORMAL or SINGLE trigger sweep modes
            - Useful for capturing one-shot events or testing
            - See :TRIGger:SWEep command for sweep mode settings

        Raises:
            pyvisa.VisaIOError: If communication fails
        """
        try:
            self.instrument.write(":TFORce")
            print("Trigger forced")
        except pyvisa.VisaIOError as e:
            print(f"Failed to force trigger: {e}")
            raise

    # ========================================
    # Waveform Data Acquisition (Section 3.28)
    # Reference: pdf_chapters/3.28*.pdf
    # ========================================

    def set_waveform_source(self, source: str) -> None:
        """
        Set source channel for waveform data acquisition.

        Reference: pdf_chapters/3.28.1_WAVeform_SOURce.pdf

        Args:
            source: Source channel
                   'CHAN1', 'CHAN2', 'CHAN3', 'CHAN4' - Analog channels
                   'MATH1', 'MATH2', 'MATH3', 'MATH4' - Math waveforms
                   For DHO900: 'D0' through 'D15' - Digital channels

        Notes:
            - When source is MATH1-MATH4, only NORMal mode is available
            - Digital channels only supported on DHO900 series

        Raises:
            ValueError: If source is invalid
            pyvisa.VisaIOError: If communication fails
        """
        source = source.upper()
        valid_sources = ['CHAN1', 'CHAN2', 'CHAN3', 'CHAN4',
                        'MATH1', 'MATH2', 'MATH3', 'MATH4']
        if source not in valid_sources:
            raise ValueError(f"Source must be one of {valid_sources}, got {source}")

        try:
            self.instrument.write(f":WAVeform:SOURce {source}")
            print(f"Waveform source: {source}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set waveform source: {e}")
            raise

    def set_waveform_mode(self, mode: str) -> None:
        """
        Set waveform data acquisition mode.

        Reference: pdf_chapters/3.28.2_WAVeform_MODE.pdf

        Args:
            mode: Acquisition mode
                 'NORMal' - Screen data (~1000 points)
                 'MAXimum' - Screen when running, memory when stopped
                 'RAW' - Internal memory (only when stopped)

        Notes:
            - NORMAL: Fast, gets displayed waveform
            - MAXIMUM: Screen data when running, deep memory when stopped
            - RAW: Full internal memory, scope must be stopped
            - MATH sources only support NORMal mode

        Raises:
            ValueError: If mode is invalid
            pyvisa.VisaIOError: If communication fails
        """
        mode = mode.upper()
        if mode not in ('NORMAL', 'MAXIMUM', 'RAW'):
            raise ValueError(f"Mode must be 'NORMAL', 'MAXIMUM', or 'RAW', got {mode}")

        try:
            self.instrument.write(f":WAVeform:MODE {mode}")
            print(f"Waveform mode: {mode}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set waveform mode: {e}")
            raise

    def set_waveform_format(self, format: str) -> None:
        """
        Set waveform data format.

        Reference: pdf_chapters/3.28.3_WAVeform_FORMat.pdf

        Args:
            format: Data format
                   'BYTE' - 8-bit (fast, less precision)
                   'WORD' - 16-bit (slower, more precision)
                   'ASCii' - ASCII text (slow, human readable)

        Notes:
            - BYTE: Recommended for speed
            - WORD: Use for maximum precision
            - ASCii: Only for debugging/manual inspection

        Raises:
            ValueError: If format is invalid
            pyvisa.VisaIOError: If communication fails
        """
        format = format.upper()
        if format not in ('BYTE', 'WORD', 'ASCII'):
            raise ValueError(f"Format must be 'BYTE', 'WORD', or 'ASCII', got {format}")

        try:
            self.instrument.write(f":WAVeform:FORMat {format}")
            print(f"Waveform format: {format}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set waveform format: {e}")
            raise

    def get_waveform_preamble(self) -> dict:
        """
        Get all waveform scaling parameters.

        Reference: pdf_chapters/3.28.14_WAVeform_PREamble_.pdf

        Returns:
            dict: Waveform parameters
                - format: 0 (BYTE), 1 (WORD), 2 (ASCii)
                - type: 0 (NORMal), 1 (MAXimum), 2 (RAW)
                - points: Number of data points
                - count: Average count (1 if not averaging)
                - xincrement: Time between samples (seconds)
                - xorigin: Time of first sample (seconds)
                - xreference: Reference time index
                - yincrement: Voltage per ADC count (volts)
                - yorigin: Voltage origin/offset (volts)
                - yreference: Reference ADC value

        Notes:
            - Returns 10 comma-separated values
            - Use for converting raw data to real units

        Raises:
            pyvisa.VisaIOError: If communication fails
        """
        try:
            response = self.instrument.query(":WAVeform:PREamble?")
            values = [float(v) for v in response.strip().split(',')]

            preamble = {
                'format': int(values[0]),
                'type': int(values[1]),
                'points': int(values[2]),
                'count': int(values[3]),
                'xincrement': values[4],
                'xorigin': values[5],
                'xreference': values[6],
                'yincrement': values[7],
                'yorigin': values[8],
                'yreference': values[9]
            }
            return preamble
        except pyvisa.VisaIOError as e:
            print(f"Failed to get waveform preamble: {e}")
            raise

    def _convert_raw_to_voltage(self, raw_data: np.ndarray, preamble: dict) -> np.ndarray:
        """
        Convert raw ADC counts to voltage values.

        Args:
            raw_data: Raw ADC values from oscilloscope
            preamble: Preamble dictionary with scaling parameters

        Returns:
            numpy array of voltage values in volts

        Formula:
            voltage[i] = (data[i] - yreference) * yincrement + yorigin
        """
        voltage = (raw_data.astype(float) - preamble['yreference']) * \
                  preamble['yincrement'] + preamble['yorigin']
        return voltage

    def _generate_time_axis(self, num_points: int, preamble: dict) -> np.ndarray:
        """
        Generate time axis for waveform.

        Args:
            num_points: Number of data points
            preamble: Preamble dictionary with scaling parameters

        Returns:
            numpy array of time values in seconds

        Formula:
            time[i] = xorigin + (i - xreference) * xincrement
        """
        indices = np.arange(num_points)
        time = preamble['xorigin'] + \
               (indices - preamble['xreference']) * \
               preamble['xincrement']
        return time

    def acquire_waveform(self, channel: int, mode: str = 'NORMAL') -> WaveformData:
        """
        Acquire complete waveform with proper scaling.

        High-level method that handles all steps of waveform acquisition:
        1. Sets waveform source
        2. Configures format and mode
        3. Gets waveform data
        4. Gets scaling parameters
        5. Converts to real units
        6. Returns WaveformData object

        Args:
            channel: Channel number (1-4)
            mode: Acquisition mode
                  'NORMAL' - Screen data (~1000 points, fast)
                  'MAXIMUM' - Deep memory when stopped
                  'RAW' - Full internal memory (must be stopped)

        Returns:
            WaveformData object with time and voltage arrays

        Example:
            >>> scope.stop()  # For deep memory acquisition
            >>> waveform = scope.acquire_waveform(1, mode='MAXIMUM')
            >>> print(f"Captured {len(waveform)} points")
            >>> waveform.plot()

        Raises:
            ValueError: If channel or mode is invalid
            pyvisa.VisaIOError: If communication fails
        """
        if channel not in (1, 2, 3, 4):
            raise ValueError(f"Channel must be 1-4, got {channel}")

        mode = mode.upper()

        try:
            # Configure waveform acquisition
            self.set_waveform_source(f'CHAN{channel}')
            self.set_waveform_mode(mode)
            self.set_waveform_format('BYTE')

            # Get preamble (scaling parameters)
            preamble = self.get_waveform_preamble()

            # Get waveform data
            print(f"Acquiring waveform data ({preamble['points']} points)...")
            raw_data = self.instrument.query_binary_values(
                ':WAVeform:DATA?',
                datatype='B',  # Unsigned byte
                is_big_endian=False
            )
            raw_data = np.array(raw_data)

            # Convert to voltage
            voltage = self._convert_raw_to_voltage(raw_data, preamble)

            # Generate time axis
            time = self._generate_time_axis(len(raw_data), preamble)

            # Calculate sample rate
            sample_rate = 1.0 / preamble['xincrement'] if preamble['xincrement'] > 0 else 0.0

            # Create WaveformData object
            waveform = WaveformData(
                time=time,
                voltage=voltage,
                channel=channel,
                sample_rate=sample_rate,
                points=len(raw_data)
            )

            print(f"Acquired {len(waveform)} points from CH{channel}")
            print(f"Time range: {time[0]:.6f} to {time[-1]:.6f} s")
            print(f"Voltage range: {voltage.min():.3f} to {voltage.max():.3f} V")

            return waveform

        except pyvisa.VisaIOError as e:
            print(f"Failed to acquire waveform: {e}")
            raise

    def save_waveform_csv(self, channel: int, filename: str, max_points: Optional[int] = None,
                          time_window: Optional[float] = None) -> None:
        """
        Save waveform from a single channel to a CSV file.

        Args:
            channel: Channel number (1-4)
            filename: Output CSV filename (e.g., 'data.csv')
            max_points: Maximum number of points to save. If None, saves all.
            time_window: Time window in seconds to save. If None, saves all.
                        Takes the most recent (last) time_window seconds of data.

        Example:
            >>> scope.save_waveform_csv(1, 'ch1_data.csv')
            >>> scope.save_waveform_csv(1, 'ch1_recent.csv', time_window=10)

        Raises:
            ValueError: If channel is invalid
            pyvisa.VisaIOError: If communication fails
        """
        import csv

        # Acquire waveform data
        waveform = self.acquire_waveform(channel, mode='NORMAL')

        times = waveform.time
        volts = waveform.voltage

        if len(times) == 0:
            print("No data captured.")
            return

        # Apply windowing if specified
        if time_window is not None:
            # Calculate sample rate
            dt = times[1] - times[0] if len(times) > 1 else 0
            if dt > 0:
                max_points = int(time_window / dt)

        if max_points is not None and max_points < len(times):
            # Take last max_points samples (most recent data)
            times = times[-max_points:]
            volts = volts[-max_points:]
            actual_time = times[-1] - times[0]
            print(f"Saving {max_points} points ({actual_time:.6f} seconds) - most recent data")

        # Write CSV file
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Time (s)', f'CH{channel} Voltage (V)'])
            for t, v in zip(times, volts):
                writer.writerow([t, v])

        print(f"Waveform from CH{channel} saved to {filename}")

    def save_waveforms_csv(self, channels: list, filename: str, max_points: Optional[int] = None,
                           time_window: Optional[float] = None) -> None:
        """
        Save waveforms from multiple channels to a single CSV file.

        Args:
            channels: List of channel numbers to capture (e.g., [1, 3])
            filename: Output CSV filename (e.g., 'data.csv')
            max_points: Maximum number of points to save. If None, saves all.
            time_window: Time window in seconds to save. If None, saves all.
                        Takes the most recent (last) time_window seconds of data.

        Example:
            >>> scope.save_waveforms_csv([1, 3], 'multi_channel.csv')
            >>> scope.save_waveforms_csv([1, 3], 'recent.csv', time_window=10)

        Raises:
            ValueError: If any channel is invalid
            pyvisa.VisaIOError: If communication fails
        """
        import csv

        # Fetch data from all channels
        channel_data = {}
        times = None

        for channel in channels:
            if channel not in (1, 2, 3, 4):
                raise ValueError(f"Invalid channel {channel}. Must be 1-4.")

            waveform = self.acquire_waveform(channel, mode='NORMAL')

            if len(waveform.time) == 0:
                print(f"No data captured from CH{channel}.")
                continue

            channel_data[channel] = waveform.voltage
            if times is None:
                times = waveform.time  # Use time base from first valid channel

        if not channel_data:
            print("No data captured from any channel.")
            return

        # Apply windowing if specified
        if time_window is not None:
            # Calculate sample rate
            dt = times[1] - times[0] if len(times) > 1 else 0
            if dt > 0:
                max_points = int(time_window / dt)

        if max_points is not None and max_points < len(times):
            # Trim all data to last max_points (most recent data)
            times = times[-max_points:]
            for ch in channel_data:
                channel_data[ch] = channel_data[ch][-max_points:]
            actual_time = times[-1] - times[0]
            print(f"Saving {max_points} points ({actual_time:.6f} seconds) - most recent data")

        # Write CSV file
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)

            # Write header
            header = ['Time (s)']
            for ch in sorted(channel_data.keys()):
                header.append(f'CH{ch} Voltage (V)')
            writer.writerow(header)

            # Write data rows
            for i in range(len(times)):
                row = [times[i]]
                for ch in sorted(channel_data.keys()):
                    row.append(channel_data[ch][i])
                writer.writerow(row)

        channels_list = ','.join(str(ch) for ch in sorted(channel_data.keys()))
        print(f"Waveforms from CH{channels_list} saved to {filename}")

    # Autoset
    def autoset(self):
        """
        Perform autoset to automatically configure scope for signal.
        Note: DHO804 uses :AUToscale command.
        """
        print("Running autoset...")
        self.instrument.write(":AUToscale")
        time.sleep(2)  # Give scope time to autoset
        print("Autoset complete")

    # ========================================
    # Automated Measurements (Section 3.17)
    # Reference: pdf_chapters/3.17*.pdf
    # ========================================

    def set_measure_source(self, source: str) -> None:
        """
        Set measurement source channel.

        Reference: pdf_chapters/3.17.1_MEASure_SOURce.pdf

        Args:
            source: Source channel
                   'CHAN1', 'CHAN2', 'CHAN3', 'CHAN4' - Analog channels
                   'MATH1', 'MATH2', 'MATH3', 'MATH4' - Math waveforms

        Raises:
            ValueError: If source is invalid
            pyvisa.VisaIOError: If communication fails
        """
        source = source.upper()
        valid_sources = ['CHAN1', 'CHAN2', 'CHAN3', 'CHAN4',
                        'MATH1', 'MATH2', 'MATH3', 'MATH4']
        if source not in valid_sources:
            raise ValueError(f"Source must be one of {valid_sources}, got {source}")

        try:
            self.instrument.write(f":MEASure:SOURce {source}")
            print(f"Measurement source: {source}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set measurement source: {e}")
            raise

    def measure(self, channel: int, measurement_type: str) -> float:
        """
        Measure any waveform parameter.

        Reference: pdf_chapters/3.17.2_MEASure_ITEM.pdf

        Comprehensive measurement method supporting all DHO804 measurement types.

        Args:
            channel: Channel number (1-4)
            measurement_type: Measurement parameter (case-insensitive):

                **Voltage Measurements:**
                - 'VMAX' - Maximum voltage
                - 'VMIN' - Minimum voltage
                - 'VPP' - Peak-to-peak voltage
                - 'VTOP' - Top voltage level
                - 'VBASe' - Base voltage level
                - 'VAMP' - Amplitude
                - 'VAVG' - Average voltage
                - 'VRMS' - RMS voltage
                - 'VMID' - Mid-level voltage
                - 'VUPPer' - Upper voltage
                - 'VLOWer' - Lower voltage

                **Time Measurements:**
                - 'PERiod' - Period
                - 'FREQuency' - Frequency
                - 'RTIMe' - Rise time (10%-90%)
                - 'FTIMe' - Fall time (90%-10%)
                - 'PWIDth' - Positive pulse width
                - 'NWIDth' - Negative pulse width

                **Duty Cycle:**
                - 'PDUTy' - Positive duty cycle
                - 'NDUTy' - Negative duty cycle

                **Overshoot:**
                - 'OVERshoot' - Overshoot percentage
                - 'PREShoot' - Preshoot percentage

                **Slew Rate:**
                - 'PSLewrate' - Positive slew rate
                - 'NSLewrate' - Negative slew rate

                **Shape:**
                - 'OVERshoot' - Overshoot percentage
                - 'PREShoot' - Preshoot percentage
                - 'PSLewrate' - Positive slew rate
                - 'NSLewrate' - Negative slew rate

                **Area:**
                - 'MARea' - Waveform area
                - 'MPARea' - Period area

                **Additional Voltage:**
                - 'ACRMs' - AC RMS voltage
                - 'VARiance' - Voltage variance
                - 'PVRMs' - Per-period RMS
                - 'TVMAX' - Time at voltage maximum
                - 'TVMIN' - Time at voltage minimum

                **Counts:**
                - 'PPULses' - Positive pulse count
                - 'NPULses' - Negative pulse count
                - 'PEDGes' - Positive edge count
                - 'NEDGes' - Negative edge count

        Returns:
            float: Measurement value

        Example:
            >>> vpp = scope.measure(1, 'VPP')
            >>> freq = scope.measure(1, 'FREQuency')
            >>> risetime = scope.measure(1, 'RTIMe')

        Raises:
            ValueError: If channel or measurement type is invalid
            pyvisa.VisaIOError: If communication fails
        """
        if channel not in (1, 2, 3, 4):
            raise ValueError(f"Channel must be 1-4, got {channel}")

        meas_type = self._resolve_meas_type(measurement_type)

        try:
            # Query measurement
            response = self.instrument.query(f":MEASure:ITEM? {meas_type},CHAN{channel}")
            value = float(response.strip())
            return value
        except pyvisa.VisaIOError as e:
            print(f"Failed to measure {meas_type}: {e}")
            raise
        except ValueError as e:
            print(f"Invalid measurement value for {meas_type}: {e}")
            raise

    def _resolve_meas_type(self, measurement_type: str) -> str:
        """Map a user-facing measurement name to its Rigol SCPI item string."""
        meas_map = {
            # Voltage
            'vpp': 'VPP', 'pk2pk': 'VPP',
            'vrms': 'VRMS', 'rms': 'VRMS',
            'vmax': 'VMAX', 'maximum': 'VMAX',
            'vmin': 'VMIN', 'minimum': 'VMIN',
            'vtop': 'VTOP', 'top': 'VTOP',
            'vbase': 'VBASe', 'base': 'VBASe',
            'vamp': 'VAMP', 'amplitude': 'VAMP',
            'vavg': 'VAVG', 'mean': 'VAVG', 'average': 'VAVG',
            'vmid': 'VMID', 'mid': 'VMID',
            'vupper': 'VUPPer', 'upper': 'VUPPer',
            'vlower': 'VLOWer', 'lower': 'VLOWer',
            'acrms': 'ACRMs',
            'variance': 'VARiance', 'var': 'VARiance',
            'pvrms': 'PVRMs',
            'tvmax': 'TVMAX',
            'tvmin': 'TVMIN',
            # Time
            'frequency': 'FREQuency', 'freq': 'FREQuency',
            'period': 'PERiod',
            'rise': 'RTIMe', 'risetime': 'RTIMe',
            'fall': 'FTIMe', 'falltime': 'FTIMe',
            'pwidth': 'PWIDth', 'ppulsewidth': 'PWIDth',
            'nwidth': 'NWIDth', 'npulsewidth': 'NWIDth',
            # Duty cycle
            'pduty': 'PDUTy', 'posduty': 'PDUTy',
            'nduty': 'NDUTy', 'negduty': 'NDUTy',
            # Shape
            'overshoot': 'OVERshoot', 'over': 'OVERshoot',
            'preshoot': 'PREShoot', 'pre': 'PREShoot',
            'pslewrate': 'PSLewrate', 'posslew': 'PSLewrate',
            'nslewrate': 'NSLewrate', 'negslew': 'NSLewrate',
            # Area
            'marea': 'MARea', 'area': 'MARea',
            'mparea': 'MPARea', 'periodarea': 'MPARea',
            # Counts
            'ppulses': 'PPULses', 'posedges': 'PEDGes',
            'npulses': 'NPULses', 'negedges': 'NEDGes',
            'pedges': 'PEDGes', 'nedges': 'NEDGes',
        }
        return meas_map.get(measurement_type.lower(), measurement_type)

    def configure_measurement(self, channel: int, measurement_type: str) -> None:
        """Configure a measurement slot without querying (call before scope single).

        Writes :MEASure:ITEM to open the slot while the scope is in RUN/armed state,
        so the value is computed when the trigger fires. Query with measure() after capture.
        """
        if channel not in (1, 2, 3, 4):
            raise ValueError(f"Channel must be 1-4, got {channel}")
        meas_type = self._resolve_meas_type(measurement_type)
        self.instrument.write(f":MEASure:ITEM {meas_type},CHAN{channel}")

    def clear_measurements(self) -> None:
        """Clear all measurement items from the display panel.

        Sends :MEASure:CLEar to remove all configured measurement slots
        from the on-screen results panel. Use before taking a clean screenshot.
        The DSP-computed values remain available until the next acquisition.
        """
        try:
            self.instrument.write(":MEASure:CLEar")
            print("Measurement items cleared from display")
        except pyvisa.VisaIOError as e:
            print(f"Failed to clear measurement display: {e}")
            raise

    # Convenience methods for common measurements

    def measure_vpp(self, channel: int) -> float:
        """Measure peak-to-peak voltage."""
        return self.measure(channel, 'VPP')

    def measure_vrms(self, channel: int) -> float:
        """Measure RMS voltage."""
        return self.measure(channel, 'VRMS')

    def measure_frequency(self, channel: int) -> float:
        """Measure frequency in Hz."""
        return self.measure(channel, 'FREQuency')

    def measure_period(self, channel: int) -> float:
        """Measure period in seconds."""
        return self.measure(channel, 'PERiod')

    def measure_rise_time(self, channel: int) -> float:
        """Measure rise time (10% to 90%)."""
        return self.measure(channel, 'RTIMe')

    def measure_fall_time(self, channel: int) -> float:
        """Measure fall time (90% to 10%)."""
        return self.measure(channel, 'FTIMe')

    def measure_duty_cycle(self, channel: int) -> float:
        """Measure positive duty cycle percentage."""
        return self.measure(channel, 'PDUTy')

    def measure_amplitude(self, channel: int) -> float:
        """Measure amplitude (Vtop - Vbase)."""
        return self.measure(channel, 'VAMP')

    # Compatibility aliases

    def measure_bnf(self, channel: int, measurement_type: str) -> float:
        """
        Measure a parameter (alias for compatibility with existing REPL code).
        BNF = "Built-iN Function" measurement.
        """
        return self.measure(channel, measurement_type)

    def measure_delay(self, ch1: int, ch2: int, edge1: str = 'RISE',
                     edge2: str = 'RISE') -> float:
        """
        Measure delay between two channels.

        Args:
            ch1: First channel (1-4)
            ch2: Second channel (1-4)
            edge1: Edge type for ch1 ('RISE' or 'FALL')
            edge2: Edge type for ch2 ('RISE' or 'FALL')

        Returns:
            Delay in seconds

        Example:
            >>> delay = scope.measure_delay(1, 2, 'RISE', 'RISE')
        """
        # Determine delay measurement type based on edges
        delay_map = {
            ('RISE', 'RISE'): 'RRDelay',
            ('RISE', 'FALL'): 'RFDelay',
            ('FALL', 'RISE'): 'FRDelay',
            ('FALL', 'FALL'): 'FFDelay',
        }

        edge1 = edge1.upper()
        edge2 = edge2.upper()
        delay_type = delay_map.get((edge1, edge2), 'RRDelay')

        try:
            response = self.instrument.query(f":MEASure:ITEM? {delay_type},CHAN{ch1},CHAN{ch2}")
            delay = float(response.strip())
            return delay
        except pyvisa.VisaIOError as e:
            print(f"Failed to measure delay: {e}")
            raise

    # ====================================================================
    # CURSOR MEASUREMENTS
    # ====================================================================

    def set_cursor_mode(self, mode: str) -> None:
        """
        Set cursor measurement mode.

        Reference: pdf_chapters/3.8.1_CURSor_MODE.pdf

        Args:
            mode: Cursor mode - 'OFF', 'MANUAL', 'TRACK', or 'XY'

        Raises:
            ValueError: If mode is invalid
            pyvisa.VisaIOError: If communication fails

        Example:
            scope.set_cursor_mode('MANUAL')
            scope.set_cursor_mode('OFF')
        """
        mode = mode.upper()
        if mode not in ('OFF', 'MANUAL', 'TRACK', 'XY'):
            raise ValueError(f"Mode must be 'OFF', 'MANUAL', 'TRACK', or 'XY', got {mode}")

        try:
            self.instrument.write(f":CURSor:MODE {mode}")
            print(f"Cursor mode set to {mode}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set cursor mode: {e}")
            raise

    # Manual Cursor Methods

    def set_manual_cursor_type(self, cursor_type: str) -> None:
        """
        Set cursor type in manual mode.

        Reference: pdf_chapters/3.8.3.1_CURSor_MANual_TYPE.pdf

        Args:
            cursor_type: 'TIME' for X cursor (horizontal) or 'AMPLITUDE' for Y cursor (vertical)

        Raises:
            ValueError: If cursor type is invalid
            pyvisa.VisaIOError: If communication fails

        Example:
            scope.set_manual_cursor_type('TIME')      # X cursor for time measurements
            scope.set_manual_cursor_type('AMPLITUDE') # Y cursor for voltage measurements
        """
        cursor_type = cursor_type.upper()
        if cursor_type not in ('TIME', 'AMPLITUDE'):
            raise ValueError(f"Cursor type must be 'TIME' or 'AMPLITUDE', got {cursor_type}")

        try:
            self.instrument.write(f":CURSor:MANual:TYPE {cursor_type}")
            print(f"Manual cursor type set to {cursor_type}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set manual cursor type: {e}")
            raise

    def set_manual_cursor_source(self, source: str) -> None:
        """
        Set channel source for manual cursor measurements.

        Reference: pdf_chapters/3.8.3.2_CURSor_MANual_SOURce.pdf

        Args:
            source: Channel source - 'CHAN1', 'CHAN2', 'CHAN3', 'CHAN4',
                   'MATH1', 'MATH2', 'MATH3', 'MATH4', or 'NONE'

        Raises:
            ValueError: If source is invalid
            pyvisa.VisaIOError: If communication fails

        Example:
            scope.set_manual_cursor_source('CHAN1')
            scope.set_manual_cursor_source('NONE')  # Disable manual cursors
        """
        source = source.upper()
        valid_sources = ['CHAN1', 'CHAN2', 'CHAN3', 'CHAN4',
                        'MATH1', 'MATH2', 'MATH3', 'MATH4', 'NONE']

        if source not in valid_sources:
            raise ValueError(f"Source must be one of {valid_sources}, got {source}")

        try:
            # Convert CHAN to CHANnel for SCPI command
            scpi_source = source.replace('CHAN', 'CHANnel')
            self.instrument.write(f":CURSor:MANual:SOURce {scpi_source}")
            print(f"Manual cursor source set to {source}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set manual cursor source: {e}")
            raise

    def set_manual_cursor_positions(self, ax: float = None, ay: float = None,
                                    bx: float = None, by: float = None) -> None:
        """
        Set manual cursor positions (horizontal and/or vertical).

        Reference: pdf_chapters/3.8.3.3-3.8.3.6_CURSor_MANual_C*.pdf

        Args:
            ax: Cursor A X position in seconds (None = don't change)
            ay: Cursor A Y position in volts (None = don't change)
            bx: Cursor B X position in seconds (None = don't change)
            by: Cursor B Y position in volts (None = don't change)

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            # Set both cursors for time measurement (10us and 20us)
            scope.set_manual_cursor_positions(ax=10e-6, bx=20e-6)

            # Set both cursors for voltage measurement (1V and 2V)
            scope.set_manual_cursor_positions(ay=1.0, by=2.0)

            # Set all four positions
            scope.set_manual_cursor_positions(ax=10e-6, ay=1.0, bx=20e-6, by=2.0)
        """
        try:
            if ax is not None:
                self.instrument.write(f":CURSor:MANual:CAX {ax}")
            if ay is not None:
                self.instrument.write(f":CURSor:MANual:CAY {ay}")
            if bx is not None:
                self.instrument.write(f":CURSor:MANual:CBX {bx}")
            if by is not None:
                self.instrument.write(f":CURSor:MANual:CBY {by}")

            positions = []
            if ax is not None: positions.append(f"AX={ax*1e6:.2f}us")
            if ay is not None: positions.append(f"AY={ay:.3f}V")
            if bx is not None: positions.append(f"BX={bx*1e6:.2f}us")
            if by is not None: positions.append(f"BY={by:.3f}V")

            if positions:
                print(f"Manual cursor positions set: {', '.join(positions)}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set manual cursor positions: {e}")
            raise

    def get_manual_cursor_values(self) -> dict:
        """
        Get all manual cursor measurement values.

        Reference: pdf_chapters/3.8.3.7-3.8.3.13_CURSor_MANual_*Value*.pdf

        Returns:
            Dictionary with cursor measurements:
            {
                'ax': Cursor A X value (seconds),
                'ay': Cursor A Y value (volts),
                'bx': Cursor B X value (seconds),
                'by': Cursor B Y value (volts),
                'delta_x': Horizontal spacing ΔX (seconds),
                'delta_y': Vertical spacing ΔY (volts),
                'inv_delta_x': Reciprocal 1/ΔX (Hz)
            }

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            values = scope.get_manual_cursor_values()
            print(f"Time difference: {values['delta_x']*1e6:.2f} us")
            print(f"Voltage difference: {values['delta_y']:.3f} V")
            print(f"Frequency (1/ΔX): {values['inv_delta_x']:.2f} Hz")
        """
        try:
            values = {}

            # Query all cursor values
            ax_resp = self.instrument.query(":CURSor:MANual:AXValue?")
            values['ax'] = float(ax_resp.strip())

            ay_resp = self.instrument.query(":CURSor:MANual:AYValue?")
            values['ay'] = float(ay_resp.strip())

            bx_resp = self.instrument.query(":CURSor:MANual:BXValue?")
            values['bx'] = float(bx_resp.strip())

            by_resp = self.instrument.query(":CURSor:MANual:BYValue?")
            values['by'] = float(by_resp.strip())

            # Query delta values
            dx_resp = self.instrument.query(":CURSor:MANual:XDELta?")
            values['delta_x'] = float(dx_resp.strip())

            dy_resp = self.instrument.query(":CURSor:MANual:YDELta?")
            values['delta_y'] = float(dy_resp.strip())

            idx_resp = self.instrument.query(":CURSor:MANual:IXDelta?")
            values['inv_delta_x'] = float(idx_resp.strip())

            return values
        except pyvisa.VisaIOError as e:
            print(f"Failed to get manual cursor values: {e}")
            raise

    # Track Cursor Methods

    def set_track_cursor_sources(self, source1: str, source2: str) -> None:
        """
        Set channel sources for track cursor measurements.

        Reference: pdf_chapters/3.8.4.1-3.8.4.2_CURSor_TRACk_SOURce*.pdf

        Args:
            source1: Source for Cursor A - 'CHAN1', 'CHAN2', 'CHAN3', 'CHAN4',
                    'MATH1', 'MATH2', 'MATH3', 'MATH4', or 'NONE'
            source2: Source for Cursor B (same options as source1)

        Raises:
            ValueError: If source is invalid
            pyvisa.VisaIOError: If communication fails

        Example:
            # Compare two channels
            scope.set_track_cursor_sources('CHAN1', 'CHAN2')

            # Compare channel and math waveform
            scope.set_track_cursor_sources('CHAN1', 'MATH1')
        """
        source1 = source1.upper()
        source2 = source2.upper()

        valid_sources = ['CHAN1', 'CHAN2', 'CHAN3', 'CHAN4',
                        'MATH1', 'MATH2', 'MATH3', 'MATH4', 'NONE']

        if source1 not in valid_sources:
            raise ValueError(f"Source1 must be one of {valid_sources}, got {source1}")
        if source2 not in valid_sources:
            raise ValueError(f"Source2 must be one of {valid_sources}, got {source2}")

        try:
            # Convert CHAN to CHANnel for SCPI command
            scpi_source1 = source1.replace('CHAN', 'CHANnel')
            scpi_source2 = source2.replace('CHAN', 'CHANnel')

            self.instrument.write(f":CURSor:TRACk:SOURce1 {scpi_source1}")
            self.instrument.write(f":CURSor:TRACk:SOURce2 {scpi_source2}")
            print(f"Track cursor sources set: Cursor A={source1}, Cursor B={source2}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set track cursor sources: {e}")
            raise

    def set_track_cursor_positions(self, ax: float, bx: float) -> None:
        """
        Set track cursor horizontal positions.

        Reference: pdf_chapters/3.8.4.3-3.8.4.4_CURSor_TRACk_C*X.pdf

        Args:
            ax: Cursor A X position in seconds
            bx: Cursor B X position in seconds

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            # Position cursors at 10us and 20us
            scope.set_track_cursor_positions(ax=10e-6, bx=20e-6)
        """
        try:
            self.instrument.write(f":CURSor:TRACk:CAX {ax}")
            self.instrument.write(f":CURSor:TRACk:CBX {bx}")
            print(f"Track cursor positions: AX={ax*1e6:.2f}us, BX={bx*1e6:.2f}us")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set track cursor positions: {e}")
            raise

    def set_track_cursor_mode(self, mode: str) -> None:
        """
        Set axis for track cursor measurement.

        Reference: pdf_chapters/3.8.4.14_CURSor_TRACk_MODE.pdf

        Args:
            mode: 'X' for X-axis or 'Y' for Y-axis

        Raises:
            ValueError: If mode is invalid
            pyvisa.VisaIOError: If communication fails

        Example:
            scope.set_track_cursor_mode('X')  # Track along X-axis
            scope.set_track_cursor_mode('Y')  # Track along Y-axis
        """
        mode = mode.upper()
        if mode not in ('X', 'Y'):
            raise ValueError(f"Mode must be 'X' or 'Y', got {mode}")

        try:
            self.instrument.write(f":CURSor:TRACk:MODE {mode}")
            print(f"Track cursor mode set to {mode}-axis")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set track cursor mode: {e}")
            raise

    def get_track_cursor_values(self) -> dict:
        """
        Get all track cursor measurement values.

        Reference: pdf_chapters/3.8.4.7-3.8.4.13_CURSor_TRACk_*Value*.pdf

        Returns:
            Dictionary with cursor measurements:
            {
                'ax': Cursor A X value (seconds),
                'ay': Cursor A Y value (volts),
                'bx': Cursor B X value (seconds),
                'by': Cursor B Y value (volts),
                'delta_x': Horizontal spacing ΔX (seconds),
                'delta_y': Vertical spacing ΔY (volts),
                'inv_delta_x': Reciprocal 1/ΔX (Hz)
            }

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            values = scope.get_track_cursor_values()
            print(f"Cursor A: X={values['ax']*1e6:.2f}us, Y={values['ay']:.3f}V")
            print(f"Cursor B: X={values['bx']*1e6:.2f}us, Y={values['by']:.3f}V")
            print(f"ΔX={values['delta_x']*1e6:.2f}us, ΔY={values['delta_y']:.3f}V")
        """
        try:
            values = {}

            # Query all cursor values
            ax_resp = self.instrument.query(":CURSor:TRACk:AXValue?")
            values['ax'] = float(ax_resp.strip())

            ay_resp = self.instrument.query(":CURSor:TRACk:AYValue?")
            values['ay'] = float(ay_resp.strip())

            bx_resp = self.instrument.query(":CURSor:TRACk:BXValue?")
            values['bx'] = float(bx_resp.strip())

            by_resp = self.instrument.query(":CURSor:TRACk:BYValue?")
            values['by'] = float(by_resp.strip())

            # Query delta values
            dx_resp = self.instrument.query(":CURSor:TRACk:XDELta?")
            values['delta_x'] = float(dx_resp.strip())

            dy_resp = self.instrument.query(":CURSor:TRACk:YDELta?")
            values['delta_y'] = float(dy_resp.strip())

            idx_resp = self.instrument.query(":CURSor:TRACk:IXDelta?")
            values['inv_delta_x'] = float(idx_resp.strip())

            return values
        except pyvisa.VisaIOError as e:
            print(f"Failed to get track cursor values: {e}")
            raise

    # XY Cursor Methods

    def set_xy_cursor_positions(self, ax: float, ay: float, bx: float, by: float) -> None:
        """
        Set XY cursor positions (only available when timebase mode is XY).

        Reference: pdf_chapters/3.8.5.1-3.8.5.4_CURSor_XY_A*.pdf

        Args:
            ax: Cursor A X position in volts
            ay: Cursor A Y position in volts
            bx: Cursor B X position in volts
            by: Cursor B Y position in volts

        Raises:
            pyvisa.VisaIOError: If communication fails

        Note:
            XY mode is only available when horizontal timebase mode is set to XY.

        Example:
            # Position cursors in XY mode
            scope.set_timebase_mode('XY')
            scope.set_cursor_mode('XY')
            scope.set_xy_cursor_positions(ax=0.5, ay=1.0, bx=1.5, by=2.0)
        """
        try:
            self.instrument.write(f":CURSor:XY:AX {ax}")
            self.instrument.write(f":CURSor:XY:AY {ay}")
            self.instrument.write(f":CURSor:XY:BX {bx}")
            self.instrument.write(f":CURSor:XY:BY {by}")
            print(f"XY cursor positions: A=({ax:.3f}V,{ay:.3f}V), B=({bx:.3f}V,{by:.3f}V)")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set XY cursor positions: {e}")
            raise

    def get_xy_cursor_values(self) -> dict:
        """
        Get all XY cursor measurement values.

        Reference: pdf_chapters/3.8.5.5-3.8.5.10_CURSor_XY_*Value*.pdf

        Returns:
            Dictionary with cursor measurements:
            {
                'ax': Cursor A X value (volts),
                'ay': Cursor A Y value (volts),
                'bx': Cursor B X value (volts),
                'by': Cursor B Y value (volts),
                'delta_x': Horizontal spacing ΔX (volts),
                'delta_y': Vertical spacing ΔY (volts)
            }

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            values = scope.get_xy_cursor_values()
            print(f"Cursor A: ({values['ax']:.3f}V, {values['ay']:.3f}V)")
            print(f"Cursor B: ({values['bx']:.3f}V, {values['by']:.3f}V)")
            print(f"Δ: ({values['delta_x']:.3f}V, {values['delta_y']:.3f}V)")
        """
        try:
            values = {}

            # Query all cursor values
            ax_resp = self.instrument.query(":CURSor:XY:AXValue?")
            values['ax'] = float(ax_resp.strip())

            ay_resp = self.instrument.query(":CURSor:XY:AYValue?")
            values['ay'] = float(ay_resp.strip())

            bx_resp = self.instrument.query(":CURSor:XY:BXValue?")
            values['bx'] = float(bx_resp.strip())

            by_resp = self.instrument.query(":CURSor:XY:BYValue?")
            values['by'] = float(by_resp.strip())

            # Query delta values
            dx_resp = self.instrument.query(":CURSor:XY:XDELta?")
            values['delta_x'] = float(dx_resp.strip())

            dy_resp = self.instrument.query(":CURSor:XY:YDELta?")
            values['delta_y'] = float(dy_resp.strip())

            return values
        except pyvisa.VisaIOError as e:
            print(f"Failed to get XY cursor values: {e}")
            raise

    # ====================================================================
    # MATH OPERATIONS
    # ====================================================================

    def enable_math_channel(self, math_ch: int, enable: bool = True) -> None:
        """
        Enable or disable a math channel.

        Reference: pdf_chapters/3.16.1_MATH_n__DISPlay.pdf

        Args:
            math_ch: Math channel number (1-4)
            enable: True to enable, False to disable

        Raises:
            ValueError: If math_ch is invalid
            pyvisa.VisaIOError: If communication fails

        Example:
            scope.enable_math_channel(1, True)   # Enable MATH1
            scope.enable_math_channel(1, False)  # Disable MATH1
        """
        if math_ch not in (1, 2, 3, 4):
            raise ValueError(f"Math channel must be 1-4, got {math_ch}")

        try:
            state = 'ON' if enable else 'OFF'
            self.instrument.write(f":MATH{math_ch}:DISPlay {state}")
            print(f"MATH{math_ch} {'enabled' if enable else 'disabled'}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to enable/disable math channel: {e}")
            raise

    def set_math_scale(self, math_ch: int, scale: float, offset: float = None) -> None:
        """
        Set vertical scale and offset for math channel.

        Reference: pdf_chapters/3.16.7_MATH_n__SCALe.pdf
        Reference: pdf_chapters/3.16.8_MATH_n__OFFSet.pdf

        Args:
            math_ch: Math channel number (1-4)
            scale: Vertical scale (V/div)
            offset: Vertical offset in volts (optional)

        Raises:
            ValueError: If math_ch is invalid
            pyvisa.VisaIOError: If communication fails

        Example:
            scope.set_math_scale(1, 1.0)          # 1V/div
            scope.set_math_scale(1, 0.5, 0.0)     # 0.5V/div, 0V offset
        """
        if math_ch not in (1, 2, 3, 4):
            raise ValueError(f"Math channel must be 1-4, got {math_ch}")

        try:
            self.instrument.write(f":MATH{math_ch}:SCALe {scale}")
            if offset is not None:
                self.instrument.write(f":MATH{math_ch}:OFFSet {offset}")
                print(f"MATH{math_ch} scale: {scale} V/div, offset: {offset} V")
            else:
                print(f"MATH{math_ch} scale: {scale} V/div")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set math scale: {e}")
            raise

    def configure_math_operation(self, math_ch: int, operation: str,
                                 source1: str, source2: str = None) -> None:
        """
        Configure math channel for arithmetic operation.

        Reference: pdf_chapters/3.16.2_MATH_n__OPERator.pdf
        Reference: pdf_chapters/3.16.3_MATH_n__SOURce1.pdf
        Reference: pdf_chapters/3.16.4_MATH_n__SOURce2.pdf

        Args:
            math_ch: Math channel number (1-4)
            operation: Operation type:
                      'ADD' (A+B), 'SUBTRACT' (A-B),
                      'MULTIPLY' (A×B), 'DIVISION' (A÷B)
            source1: Source A - 'CHAN1', 'CHAN2', 'CHAN3', 'CHAN4'
            source2: Source B (required for arithmetic operations)

        Raises:
            ValueError: If parameters are invalid
            pyvisa.VisaIOError: If communication fails

        Example:
            # Add two channels: MATH1 = CH1 + CH2
            scope.configure_math_operation(1, 'ADD', 'CHAN1', 'CHAN2')
            scope.enable_math_channel(1, True)

            # Subtract channels: MATH1 = CH1 - CH2
            scope.configure_math_operation(1, 'SUBTRACT', 'CHAN1', 'CHAN2')
        """
        if math_ch not in (1, 2, 3, 4):
            raise ValueError(f"Math channel must be 1-4, got {math_ch}")

        operation = operation.upper()
        valid_ops = ['ADD', 'SUBTRACT', 'MULTIPLY', 'DIVISION']
        if operation not in valid_ops:
            raise ValueError(f"Operation must be one of {valid_ops}, got {operation}")

        source1 = source1.upper()
        if source2:
            source2 = source2.upper()

        # Arithmetic operations require two sources
        if operation in valid_ops and source2 is None:
            raise ValueError(f"{operation} requires two sources")

        try:
            # Set operator
            op_map = {'SUBTRACT': 'SUBTract', 'MULTIPLY': 'MULTiply'}
            scpi_op = op_map.get(operation, operation)
            self.instrument.write(f":MATH{math_ch}:OPERator {scpi_op}")

            # Set sources (convert CHAN to CHANnel for SCPI)
            scpi_source1 = source1.replace('CHAN', 'CHANnel')
            self.instrument.write(f":MATH{math_ch}:SOURce1 {scpi_source1}")

            if source2:
                scpi_source2 = source2.replace('CHAN', 'CHANnel')
                self.instrument.write(f":MATH{math_ch}:SOURce2 {scpi_source2}")

            print(f"MATH{math_ch} configured: {source1} {operation} {source2 if source2 else ''}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to configure math operation: {e}")
            raise

    def configure_math_function(self, math_ch: int, function: str, source: str) -> None:
        """
        Configure math channel for function operation.

        Reference: pdf_chapters/3.16.2_MATH_n__OPERator.pdf
        Reference: pdf_chapters/3.16.3_MATH_n__SOURce1.pdf

        Args:
            math_ch: Math channel number (1-4)
            function: Function type:
                     'INTG' (integrate), 'DIFF' (differentiate),
                     'SQRT' (square root), 'LG' (log base 10),
                     'LN' (natural log), 'EXP', 'ABS' (absolute value)
            source: Source channel - 'CHAN1', 'CHAN2', 'CHAN3', 'CHAN4'

        Raises:
            ValueError: If parameters are invalid
            pyvisa.VisaIOError: If communication fails

        Example:
            # Integrate CH1: MATH1 = ∫(CH1)
            scope.configure_math_function(1, 'INTG', 'CHAN1')
            scope.enable_math_channel(1, True)

            # Differentiate CH1: MATH1 = d/dt(CH1)
            scope.configure_math_function(1, 'DIFF', 'CHAN1')

            # Square root: MATH1 = √(CH1)
            scope.configure_math_function(1, 'SQRT', 'CHAN1')
        """
        if math_ch not in (1, 2, 3, 4):
            raise ValueError(f"Math channel must be 1-4, got {math_ch}")

        function = function.upper()
        valid_funcs = ['INTG', 'DIFF', 'SQRT', 'LG', 'LN', 'EXP', 'ABS']
        if function not in valid_funcs:
            raise ValueError(f"Function must be one of {valid_funcs}, got {function}")

        source = source.upper()

        try:
            # Set operator
            self.instrument.write(f":MATH{math_ch}:OPERator {function}")

            # Set source (convert CHAN to CHANnel for SCPI)
            scpi_source = source.replace('CHAN', 'CHANnel')
            self.instrument.write(f":MATH{math_ch}:SOURce1 {scpi_source}")

            print(f"MATH{math_ch} configured: {function}({source})")
        except pyvisa.VisaIOError as e:
            print(f"Failed to configure math function: {e}")
            raise

    def configure_fft(self, math_ch: int, source: str, window: str = 'RECT') -> None:
        """
        Configure math channel for FFT (Fast Fourier Transform) analysis.

        Reference: pdf_chapters/3.16.2_MATH_n__OPERator.pdf
        Reference: pdf_chapters/3.16.14_MATH_n__FFT_SOURce.pdf
        Reference: pdf_chapters/3.16.15_MATH_n__FFT_WINDow.pdf

        Args:
            math_ch: Math channel number (1-4)
            source: Source channel - 'CHAN1', 'CHAN2', 'CHAN3', 'CHAN4'
            window: FFT window function:
                   'RECT' (rectangular), 'BLACK' (Blackman),
                   'HANN' (Hanning), 'HAMM' (Hamming),
                   'FLAT' (Flattop), 'TRI' (Triangle)
                   Default: 'RECT'

        Raises:
            ValueError: If parameters are invalid
            pyvisa.VisaIOError: If communication fails

        Note:
            Different window functions trade off frequency resolution vs
            spectral leakage. RECT has best frequency resolution but most
            leakage. BLACKMAN has least leakage but poorer resolution.

        Example:
            # FFT of CH1 with Hanning window
            scope.configure_fft(1, 'CHAN1', 'HANN')
            scope.enable_math_channel(1, True)

            # FFT with default rectangular window
            scope.configure_fft(1, 'CHAN1')
        """
        if math_ch not in (1, 2, 3, 4):
            raise ValueError(f"Math channel must be 1-4, got {math_ch}")

        source = source.upper()
        window = window.upper()

        valid_windows = ['RECT', 'BLACK', 'HANN', 'HAMM', 'FLAT', 'TRI']
        if window not in valid_windows:
            raise ValueError(f"Window must be one of {valid_windows}, got {window}")

        try:
            # Set operator to FFT
            self.instrument.write(f":MATH{math_ch}:OPERator FFT")

            # Set FFT source (convert CHAN to CHANnel for SCPI)
            scpi_source = source.replace('CHAN', 'CHANnel')
            self.instrument.write(f":MATH{math_ch}:FFT:SOURce {scpi_source}")

            # Set FFT window
            self.instrument.write(f":MATH{math_ch}:FFT:WINDow {window}")

            print(f"MATH{math_ch} configured: FFT({source}) with {window} window")
        except pyvisa.VisaIOError as e:
            print(f"Failed to configure FFT: {e}")
            raise

    def configure_digital_filter(self, math_ch: int, filter_type: str, source: str,
                                 cutoff_freq1: float, cutoff_freq2: float = None) -> None:
        """
        Configure math channel for digital filtering.

        Reference: pdf_chapters/3.16.2_MATH_n__OPERator.pdf
        Reference: pdf_chapters/3.16.29_MATH_n__FILTer_TYPE.pdf
        Reference: pdf_chapters/3.16.30_MATH_n__FILTer_W1.pdf
        Reference: pdf_chapters/3.16.31_MATH_n__FILTer_W2.pdf

        Args:
            math_ch: Math channel number (1-4)
            filter_type: Filter type:
                        'LPASS' (low-pass): Pass f < cutoff_freq1
                        'HPASS' (high-pass): Pass f > cutoff_freq1
                        'BPASS' (band-pass): Pass cutoff_freq1 < f < cutoff_freq2
                        'BSTOP' (band-stop): Stop cutoff_freq1 < f < cutoff_freq2
            source: Source channel - 'CHAN1', 'CHAN2', 'CHAN3', 'CHAN4'
            cutoff_freq1: Cutoff frequency in Hz (or lower cutoff for band filters)
            cutoff_freq2: Upper cutoff frequency in Hz (required for BPASS/BSTOP)

        Raises:
            ValueError: If parameters are invalid
            pyvisa.VisaIOError: If communication fails

        Note:
            For band-pass and band-stop filters, cutoff_freq1 must be less
            than cutoff_freq2.

        Example:
            # Low-pass filter at 1kHz
            scope.configure_digital_filter(1, 'LPASS', 'CHAN1', 1000)
            scope.enable_math_channel(1, True)

            # High-pass filter at 100Hz
            scope.configure_digital_filter(1, 'HPASS', 'CHAN1', 100)

            # Band-pass filter 100Hz - 1kHz
            scope.configure_digital_filter(1, 'BPASS', 'CHAN1', 100, 1000)

            # Band-stop (notch) filter 50Hz - 60Hz
            scope.configure_digital_filter(1, 'BSTOP', 'CHAN1', 50, 60)
        """
        if math_ch not in (1, 2, 3, 4):
            raise ValueError(f"Math channel must be 1-4, got {math_ch}")

        filter_type = filter_type.upper()
        valid_filters = ['LPASS', 'HPASS', 'BPASS', 'BSTOP']
        if filter_type not in valid_filters:
            raise ValueError(f"Filter type must be one of {valid_filters}, got {filter_type}")

        # Band filters require two cutoff frequencies
        if filter_type in ['BPASS', 'BSTOP']:
            if cutoff_freq2 is None:
                raise ValueError(f"{filter_type} requires two cutoff frequencies")
            if cutoff_freq1 >= cutoff_freq2:
                raise ValueError(f"cutoff_freq1 ({cutoff_freq1}) must be less than cutoff_freq2 ({cutoff_freq2})")

        source = source.upper()

        try:
            # Set operator to filter type (map to SCPI names)
            filter_map = {
                'LPASS': 'LPASs',
                'HPASS': 'HPASs',
                'BPASS': 'BPASs',
                'BSTOP': 'BSTop'
            }
            scpi_filter = filter_map[filter_type]
            self.instrument.write(f":MATH{math_ch}:OPERator {scpi_filter}")

            # Set filter source (uses FFT:SOURce command for filters)
            scpi_source = source.replace('CHAN', 'CHANnel')
            self.instrument.write(f":MATH{math_ch}:FFT:SOURce {scpi_source}")

            # Set filter type explicitly
            self.instrument.write(f":MATH{math_ch}:FILTer:TYPE {scpi_filter}")

            # Set cutoff frequency/frequencies
            self.instrument.write(f":MATH{math_ch}:FILTer:W1 {cutoff_freq1}")
            if cutoff_freq2 is not None:
                self.instrument.write(f":MATH{math_ch}:FILTer:W2 {cutoff_freq2}")

            if cutoff_freq2:
                print(f"MATH{math_ch} configured: {filter_type} filter on {source}, {cutoff_freq1:.0f}Hz - {cutoff_freq2:.0f}Hz")
            else:
                print(f"MATH{math_ch} configured: {filter_type} filter on {source}, cutoff {cutoff_freq1:.0f}Hz")
        except pyvisa.VisaIOError as e:
            print(f"Failed to configure digital filter: {e}")
            raise

    # ========================================================================
    # ACQUISITION MODES
    # ========================================================================

    def set_acquisition_type(self, acq_type: str) -> None:
        """
        Set the acquisition type.

        Reference: pdf_chapters/3.3.3_ACQuire_TYPE.pdf

        Args:
            acq_type: Acquisition type:
                     'NORMAL' - Normal sampling mode (default)
                     'PEAK' - Peak detect mode (captures min/max values)
                     'AVERAGE' - Average mode (reduces noise, use set_average_count())
                     'ULTRA' - Ultra acquisition mode (high refresh rate segmented memory)

        Raises:
            ValueError: If acquisition type is invalid
            pyvisa.VisaIOError: If communication fails

        Note:
            - NORMAL: Standard sampling, best for general purpose measurements
            - PEAK: Useful for detecting glitches and narrow pulses
            - AVERAGE: Reduces random noise, requires set_average_count()
            - ULTRA: Enables segmented memory for high waveform capture rate

        Example:
            # Set to average mode
            scope.set_acquisition_type('AVERAGE')
            scope.set_average_count(64)

            # Set to peak detect mode
            scope.set_acquisition_type('PEAK')
        """
        acq_type = acq_type.upper()
        valid_types = ['NORMAL', 'PEAK', 'AVERAGE', 'ULTRA']

        if acq_type not in valid_types:
            raise ValueError(f"Acquisition type must be one of {valid_types}, got {acq_type}")

        try:
            self.instrument.write(f":ACQuire:TYPE {acq_type}")
            print(f"Acquisition type set to {acq_type}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set acquisition type: {e}")
            raise

    def set_average_count(self, count: int) -> None:
        """
        Set the number of averages for AVERAGE acquisition mode.

        Reference: pdf_chapters/3.3.1_ACQuire_AVERages.pdf

        Args:
            count: Number of averages (must be power of 2: 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536)
                  Range: 2 to 65536 (2^1 to 2^16)

        Raises:
            ValueError: If count is not a valid power of 2 in range
            pyvisa.VisaIOError: If communication fails

        Note:
            - Higher average counts reduce noise but slow down waveform update rate
            - Only applies when acquisition type is set to AVERAGE
            - Count must be exact power of 2 (2^n where n = 1 to 16)

        Example:
            # Set to 64 averages
            scope.set_acquisition_type('AVERAGE')
            scope.set_average_count(64)
        """
        # Check if count is power of 2
        import math
        if count < 2 or count > 65536:
            raise ValueError(f"Average count must be between 2 and 65536, got {count}")

        # Check if it's a power of 2
        log_val = math.log2(count)
        if not log_val.is_integer():
            raise ValueError(f"Average count must be a power of 2 (2, 4, 8, 16, ..., 65536), got {count}")

        try:
            self.instrument.write(f":ACQuire:AVERages {count}")
            print(f"Average count set to {count}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set average count: {e}")
            raise

    def set_memory_depth(self, depth: str) -> None:
        """
        Set the memory depth (number of waveform points stored).

        Reference: pdf_chapters/3.3.2_ACQuire_MDEPth.pdf

        Args:
            depth: Memory depth setting:
                  'AUTO' - Automatic memory depth (recommended)
                  Or specific values: '1k', '10k', '100k', '1M', '5M', '10M', '25M', '50M'

        Raises:
            ValueError: If memory depth value is invalid
            pyvisa.VisaIOError: If communication fails

        Note:
            - Available depths depend on number of enabled channels
            - More memory depth = higher resolution but slower waveform update
            - AUTO mode automatically selects optimal depth
            - 1 channel enabled: up to 50M points
            - 2 channels enabled: up to 25M points each
            - 3-4 channels enabled: up to 10M points each

        Example:
            # Set to automatic
            scope.set_memory_depth('AUTO')

            # Set to 10M points
            scope.set_memory_depth('10M')
        """
        depth = depth.upper()
        valid_depths = ['AUTO', '1K', '10K', '100K', '1M', '5M', '10M', '25M', '50M']

        if depth not in valid_depths:
            raise ValueError(f"Memory depth must be one of {valid_depths}, got {depth}")

        try:
            self.instrument.write(f":ACQuire:MDEPth {depth}")
            print(f"Memory depth set to {depth}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set memory depth: {e}")
            raise

    def get_memory_depth(self) -> str:
        """
        Query the current memory depth setting.

        Reference: pdf_chapters/3.3.2_ACQuire_MDEPth.pdf

        Returns:
            str: Current memory depth ('AUTO', '1K', '10K', '100K', '1M', '5M', '10M', '25M', or '50M')

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            depth = scope.get_memory_depth()
            print(f"Current memory depth: {depth}")
        """
        try:
            response = self.instrument.query(":ACQuire:MDEPth?")
            depth = response.strip()
            print(f"Memory depth: {depth}")
            return depth
        except pyvisa.VisaIOError as e:
            print(f"Failed to query memory depth: {e}")
            raise

    def get_sample_rate(self) -> float:
        """
        Query the current sample rate.

        Reference: pdf_chapters/3.3.4_ACQuire_SRATe_.pdf

        Returns:
            float: Current sample rate in Sa/s (samples per second)

        Raises:
            pyvisa.VisaIOError: If communication fails

        Note:
            - Sample rate depends on horizontal scale and memory depth
            - Returns actual sampling frequency in scientific notation
            - Higher sample rates provide better time resolution

        Example:
            rate = scope.get_sample_rate()
            print(f"Sample rate: {rate/1e9:.2f} GSa/s")
        """
        try:
            response = self.instrument.query(":ACQuire:SRATe?")
            sample_rate = float(response.strip())
            print(f"Sample rate: {sample_rate:.3e} Sa/s ({sample_rate/1e9:.3f} GSa/s)")
            return sample_rate
        except pyvisa.VisaIOError as e:
            print(f"Failed to query sample rate: {e}")
            raise

    # ========================================================================
    # DISPLAY CONTROL
    # ========================================================================

    def clear_display(self) -> None:
        """
        Clear all waveforms on the screen.

        Reference: pdf_chapters/3.9.1_DISPlay_CLEar.pdf

        Raises:
            pyvisa.VisaIOError: If communication fails

        Note:
            - If oscilloscope is in RUN state, new waveforms continue after clearing
            - Same as pressing the CLEAR button on the front panel
            - Can also use the :CLEar command directly

        Example:
            scope.clear_display()
        """
        try:
            self.instrument.write(":DISPlay:CLEar")
            print("Display cleared")
        except pyvisa.VisaIOError as e:
            print(f"Failed to clear display: {e}")
            raise

    def set_display_type(self, display_type: str) -> None:
        """
        Set the display type of waveforms on the screen.

        Reference: pdf_chapters/3.9.2_DISPlay_TYPE.pdf

        Args:
            display_type: Display type - 'VECTORS' (sample points connected by lines)

        Raises:
            ValueError: If display type is invalid
            pyvisa.VisaIOError: If communication fails

        Note:
            - VECTORS mode provides the most vivid waveform display
            - Best for viewing steep edges (e.g., square waves)
            - Currently only VECTORS mode is supported by DHO804

        Example:
            scope.set_display_type('VECTORS')
        """
        display_type = display_type.upper()
        valid_types = ['VECTORS', 'VECT']

        if display_type not in valid_types:
            raise ValueError(f"Display type must be 'VECTORS', got {display_type}")

        try:
            self.instrument.write(":DISPlay:TYPE VECTors")
            print("Display type set to VECTORS")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set display type: {e}")
            raise

    def set_grid_type(self, grid: str) -> None:
        """
        Set the display type of the screen grid.

        Reference: pdf_chapters/3.9.5_DISPlay_GRID.pdf

        Args:
            grid: Grid type:
                 'FULL' - Background grid and coordinates on (default)
                 'HALF' - Background grid off, coordinates on
                 'NONE' - Background grid and coordinates off

        Raises:
            ValueError: If grid type is invalid
            pyvisa.VisaIOError: If communication fails

        Note:
            - FULL: Shows complete grid with divisions and coordinates
            - HALF: Shows only coordinate axes without grid lines
            - NONE: Clean display with no reference lines

        Example:
            # Full grid
            scope.set_grid_type('FULL')

            # Coordinates only, no grid
            scope.set_grid_type('HALF')

            # Clean display
            scope.set_grid_type('NONE')
        """
        grid = grid.upper()
        valid_grids = ['FULL', 'HALF', 'NONE']

        if grid not in valid_grids:
            raise ValueError(f"Grid type must be one of {valid_grids}, got {grid}")

        try:
            self.instrument.write(f":DISPlay:GRID {grid}")
            print(f"Grid type set to {grid}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set grid type: {e}")
            raise

    def set_persistence(self, time: str) -> None:
        """
        Set the waveform persistence time.

        Reference: pdf_chapters/3.9.3_DISPlay_GRADing_TIME.pdf

        Args:
            time: Persistence time:
                 'MIN' - Minimum persistence (high refresh rate)
                 '0.1', '0.2', '0.5', '1', '2', '5', '10' - Time in seconds
                 'INFINITE' - Infinite persistence (no clearing)

        Raises:
            ValueError: If time value is invalid
            pyvisa.VisaIOError: If communication fails

        Note:
            - MIN: Best for viewing rapidly changing waveforms
            - Specific values (0.1-10s): Good for observing slow glitches
            - INFINITE: Accumulates all waveforms, useful for jitter/noise analysis
                       and capturing rare events

        Example:
            # High refresh rate
            scope.set_persistence('MIN')

            # 100ms persistence to catch glitches
            scope.set_persistence('0.1')

            # Infinite persistence for jitter analysis
            scope.set_persistence('INFINITE')
        """
        time = time.upper()
        valid_times = ['MIN', '0.1', '0.2', '0.5', '1', '2', '5', '10', 'INFINITE', 'INF']

        if time not in valid_times:
            raise ValueError(f"Persistence time must be one of {valid_times}, got {time}")

        # Map INFINITE to INFinite for SCPI
        if time == 'INFINITE':
            time = 'INFinite'

        try:
            self.instrument.write(f":DISPlay:GRADing:TIME {time}")
            print(f"Persistence time set to {time}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set persistence time: {e}")
            raise

    def get_screenshot(self) -> bytes:
        """
        Capture the current screen image as bitmap data.

        Reference: pdf_chapters/3.9.7_DISPlay_DATA_.pdf

        Returns:
            bytes: Bitmap data stream of the currently displayed image

        Raises:
            pyvisa.VisaIOError: If communication fails

        Note:
            - Returns raw bitmap data of the screen
            - Data format is typically BMP or PNG depending on oscilloscope
            - Can be saved directly to a file with .bmp or .png extension
            - Large data transfer - may take several seconds

        Example:
            # Capture and save screenshot
            screenshot_data = scope.get_screenshot()
            with open('screenshot.bmp', 'wb') as f:
                f.write(screenshot_data)
        """
        try:
            print("Capturing screenshot (this may take several seconds)...")
            # Query screenshot data - returns binary data
            screenshot_data = self.instrument.query_binary_values(
                ":DISPlay:DATA?",
                datatype='B',
                container=bytes
            )
            print(f"Screenshot captured ({len(screenshot_data)} bytes)")
            return screenshot_data
        except pyvisa.VisaIOError as e:
            print(f"Failed to capture screenshot: {e}")
            raise

    def set_waveform_brightness(self, brightness: int) -> None:
        """
        Set the brightness of waveforms on the screen.

        Reference: pdf_chapters/3.9.4_DISPlay_WBRightness.pdf

        Args:
            brightness: Brightness level in percentage (1-100)

        Raises:
            ValueError: If brightness is out of range
            pyvisa.VisaIOError: If communication fails

        Note:
            - Higher values make waveforms brighter and more visible
            - Lower values reduce waveform intensity
            - Default is 50%
            - Range: 1% to 100%

        Example:
            # Default brightness
            scope.set_waveform_brightness(50)

            # Very bright for photos
            scope.set_waveform_brightness(100)

            # Dim for low-light viewing
            scope.set_waveform_brightness(20)
        """
        if brightness < 1 or brightness > 100:
            raise ValueError(f"Brightness must be between 1 and 100, got {brightness}")

        try:
            self.instrument.write(f":DISPlay:WBRightness {brightness}")
            print(f"Waveform brightness set to {brightness}%")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set waveform brightness: {e}")
            raise

    def set_grid_brightness(self, brightness: int) -> None:
        """
        Set the brightness of the screen grid.

        Reference: pdf_chapters/3.9.6_DISPlay_GBRightness.pdf

        Args:
            brightness: Grid brightness level in percentage (0-100)

        Raises:
            ValueError: If brightness is out of range
            pyvisa.VisaIOError: If communication fails

        Note:
            - Higher values make grid lines brighter
            - 0% makes grid invisible (same as NONE grid type)
            - Default is 50%
            - Range: 0% to 100%

        Example:
            # Default brightness
            scope.set_grid_brightness(50)

            # Bright grid
            scope.set_grid_brightness(80)

            # Subtle grid
            scope.set_grid_brightness(20)

            # Invisible grid
            scope.set_grid_brightness(0)
        """
        if brightness < 0 or brightness > 100:
            raise ValueError(f"Grid brightness must be between 0 and 100, got {brightness}")

        try:
            self.instrument.write(f":DISPlay:GBRightness {brightness}")
            print(f"Grid brightness set to {brightness}%")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set grid brightness: {e}")
            raise

    # ========================================================================
    # SAVE/RECALL FUNCTIONS
    # ========================================================================

    def save_screenshot_to_scope(self, path: str) -> None:
        """
        Save screenshot to oscilloscope's internal or external storage.

        Reference: pdf_chapters/3.21.6_SAVE_IMAGe.pdf

        Args:
            path: File path on oscilloscope storage
                 - Internal storage: 'C:/filename.png'
                 - External USB: 'D:/filename.png' or 'E:/filename.png'
                 - Supported formats: .bmp, .png, .jpg
                 - Filename max 16 characters (non-Chinese)

        Raises:
            ValueError: If path format is invalid
            pyvisa.VisaIOError: If communication fails or path is invalid

        Note:
            - Saves to oscilloscope's storage, not PC
            - Use get_screenshot() to transfer image data to PC
            - Set :SAVE:OVERlap ON to overwrite existing files
            - Image format can be configured with :SAVE:IMAGe:FORMat

        Example:
            # Save to internal storage
            scope.save_screenshot_to_scope('C:/screenshot1.png')

            # Save to USB drive
            scope.save_screenshot_to_scope('D:/test.jpg')
        """
        if not path:
            raise ValueError("Path cannot be empty")

        # Validate file extension
        valid_extensions = ['.bmp', '.png', '.jpg']
        if not any(path.lower().endswith(ext) for ext in valid_extensions):
            raise ValueError(f"File must have extension: {', '.join(valid_extensions)}")

        try:
            self.instrument.write(f":SAVE:IMAGe {path}")
            print(f"Screenshot saved to oscilloscope storage: {path}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to save screenshot: {e}")
            raise

    def save_setup(self, path: str) -> None:
        """
        Save current oscilloscope setup/configuration to file.

        Reference: pdf_chapters/3.21.7_SAVE_SETup.pdf

        Args:
            path: File path on oscilloscope storage
                 - Internal storage: 'C:/filename.stp'
                 - External USB: 'D:/filename.stp' or 'E:/filename.stp'
                 - File format must be: .stp
                 - Filename max 16 characters (non-Chinese)

        Raises:
            ValueError: If path format is invalid
            pyvisa.VisaIOError: If communication fails or path is invalid

        Note:
            - Saves all current settings (channels, timebase, trigger, etc.)
            - Can be recalled with load_setup()
            - Set :SAVE:OVERlap ON to overwrite existing files

        Example:
            # Save current configuration
            scope.save_setup('C:/my_config.stp')

            # Save to USB drive
            scope.save_setup('D:/test_setup.stp')
        """
        if not path:
            raise ValueError("Path cannot be empty")

        # Validate file extension
        if not path.lower().endswith('.stp'):
            raise ValueError("Setup file must have .stp extension")

        try:
            self.instrument.write(f":SAVE:SETup {path}")
            print(f"Setup saved to oscilloscope storage: {path}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to save setup: {e}")
            raise

    def load_setup(self, path: str) -> None:
        """
        Load oscilloscope setup/configuration from file.

        Reference: pdf_chapters/3.21.20_LOAD_SETup.pdf

        Args:
            path: File path on oscilloscope storage
                 - Internal storage: 'C:/filename.stp'
                 - External USB: 'D:/filename.stp' or 'E:/filename.stp'
                 - File format must be: .stp

        Raises:
            ValueError: If path format is invalid
            pyvisa.VisaIOError: If communication fails, file not found, or invalid file

        Note:
            - Loads all settings from previously saved setup file
            - Overwrites current oscilloscope configuration
            - File must have been saved with save_setup()

        Example:
            # Load configuration from internal storage
            scope.load_setup('C:/my_config.stp')

            # Load from USB drive
            scope.load_setup('D:/test_setup.stp')
        """
        if not path:
            raise ValueError("Path cannot be empty")

        # Validate file extension
        if not path.lower().endswith('.stp'):
            raise ValueError("Setup file must have .stp extension")

        try:
            self.instrument.write(f":LOAD:SETup {path}")
            print(f"Setup loaded from oscilloscope storage: {path}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to load setup: {e}")
            raise

    def save_waveform_to_scope(self, path: str) -> None:
        """
        Save screen waveform data to oscilloscope storage.

        Reference: pdf_chapters/3.21.8_SAVE_WAVeform.pdf

        Args:
            path: File path on oscilloscope storage
                 - Internal storage: 'C:/filename.csv' or 'C:/filename.bin'
                 - External USB: 'D:/filename.csv' or 'D:/filename.bin'
                 - Supported formats: .csv (text), .bin (binary)
                 - Filename max 16 characters (non-Chinese)

        Raises:
            ValueError: If path format is invalid
            pyvisa.VisaIOError: If communication fails or path is invalid

        Note:
            - Saves waveform data from currently displayed channels
            - CSV format: Human-readable, larger file size
            - BIN format: Binary, smaller file size
            - Set :SAVE:OVERlap ON to overwrite existing files

        Example:
            # Save as CSV for analysis in Excel
            scope.save_waveform_to_scope('C:/data.csv')

            # Save as binary for compact storage
            scope.save_waveform_to_scope('D:/waveform.bin')
        """
        if not path:
            raise ValueError("Path cannot be empty")

        # Validate file extension
        valid_extensions = ['.csv', '.bin']
        if not any(path.lower().endswith(ext) for ext in valid_extensions):
            raise ValueError(f"Waveform file must have extension: {', '.join(valid_extensions)}")

        try:
            self.instrument.write(f":SAVE:WAVeform {path}")
            print(f"Waveform data saved to oscilloscope storage: {path}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to save waveform: {e}")
            raise

    # ========================================================================
    # IEEE 488.2 COMMON COMMANDS
    # ========================================================================

    def get_identity(self) -> str:
        """
        Query instrument identification string.

        Reference: pdf_chapters/3.12.1_IDN_.pdf

        Returns:
            str: Identification string in format:
                RIGOL TECHNOLOGIES,<model>,<serial number>,<software version>

        Raises:
            pyvisa.VisaIOError: If communication fails

        Note:
            - Standard IEEE 488.2 command
            - Returns manufacturer, model, serial number, and firmware version
            - Useful for instrument identification and version checking

        Example:
            idn = scope.get_identity()
            print(idn)
            # Output: RIGOL TECHNOLOGIES,DHO804,DHO8A264M00015,00.01.02.00.01
        """
        try:
            response = self.instrument.query("*IDN?")
            identity = response.strip()
            print(f"Instrument ID: {identity}")
            return identity
        except pyvisa.VisaIOError as e:
            print(f"Failed to query identity: {e}")
            raise

    def reset(self) -> None:
        """
        Reset oscilloscope to factory default settings.

        Reference: pdf_chapters/3.12.2_RST.pdf

        Raises:
            pyvisa.VisaIOError: If communication fails

        Note:
            - Standard IEEE 488.2 command
            - Resets all settings to factory defaults
            - Clears all measurements and waveform data
            - Does NOT clear error queue (use clear_status() for that)
            - Oscilloscope will take a few seconds to complete reset

        WARNING:
            This command will erase all current settings!
            Save your configuration first if needed.

        Example:
            # Save current config before reset
            scope.save_setup('C:/backup.stp')

            # Reset to defaults
            scope.reset()
            time.sleep(3)  # Wait for reset to complete
        """
        try:
            self.instrument.write("*RST")
            print("Oscilloscope reset to factory defaults")
            print("WARNING: All settings have been erased!")
        except pyvisa.VisaIOError as e:
            print(f"Failed to reset oscilloscope: {e}")
            raise

    def clear_status(self) -> None:
        """
        Clear status byte and error queue.

        Reference: pdf_chapters/3.12.3_CLS.pdf

        Raises:
            pyvisa.VisaIOError: If communication fails

        Note:
            - Standard IEEE 488.2 command
            - Clears the status byte register
            - Clears the standard event status register
            - Clears the error queue
            - Does NOT reset instrument settings (use reset() for that)

        Example:
            # Clear any previous errors
            scope.clear_status()

            # Perform operations
            scope.configure_trigger(1, 1.0, 'RISE')

            # Check for errors
            status = scope.get_status_byte()
        """
        try:
            self.instrument.write("*CLS")
            print("Status and error queue cleared")
        except pyvisa.VisaIOError as e:
            print(f"Failed to clear status: {e}")
            raise

    def operation_complete(self) -> None:
        """
        Set Operation Complete bit when all pending operations finish.

        Reference: pdf_chapters/3.12.6_OPC.pdf

        Raises:
            pyvisa.VisaIOError: If communication fails

        Note:
            - Standard IEEE 488.2 command
            - Sets bit 0 in Standard Event Status Register when complete
            - Use for synchronization in command sequences
            - Query form (*OPC?) waits and returns 1 when complete

        Example:
            # Start a long operation
            scope.set_memory_depth('50M')
            scope.operation_complete()

            # Or use query form to wait
            result = scope.instrument.query('*OPC?')
            # Returns '1' when operation completes
        """
        try:
            self.instrument.write("*OPC")
            print("Operation complete flag set")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set operation complete: {e}")
            raise

    def get_status_byte(self) -> int:
        """
        Query the status byte register.

        Reference: pdf_chapters/3.12.10_STB_.pdf

        Returns:
            int: Status byte value (0-255)
                Bit 4 (16): Message Available (MAV)
                Bit 5 (32): Event Status Bit (ESB)
                Bit 6 (64): Master Summary Status (MSS)
                Bit 7 (128): Operation Status Register

        Raises:
            pyvisa.VisaIOError: If communication fails

        Note:
            - Standard IEEE 488.2 command
            - Returns status byte register value
            - Bits indicate various status conditions
            - Check specific bits to determine status

        Example:
            status = scope.get_status_byte()

            # Check Message Available bit
            if status & 16:
                print("Data available in output buffer")

            # Check Event Status bit
            if status & 32:
                print("Event occurred")
        """
        try:
            response = self.instrument.query("*STB?")
            status = int(response.strip())
            print(f"Status byte: {status} (0x{status:02X})")
            return status
        except pyvisa.VisaIOError as e:
            print(f"Failed to query status byte: {e}")
            raise

    def self_test(self) -> bool:
        """
        Perform oscilloscope self-test.

        Reference: pdf_chapters/3.12.12_TST_.pdf

        Returns:
            bool: True if self-test passes, False if it fails

        Raises:
            pyvisa.VisaIOError: If communication fails

        Note:
            - Standard IEEE 488.2 command
            - Performs internal self-test
            - Returns 0 if passes, 1 if fails
            - If fails, check error queue with :SYSTem:ERRor[:NEXT]?
            - Self-test may take several seconds

        Example:
            print("Running self-test...")
            if scope.self_test():
                print("Self-test PASSED")
            else:
                print("Self-test FAILED - check error queue")
                # Query error details if needed
        """
        try:
            print("Performing self-test (may take several seconds)...")
            response = self.instrument.query("*TST?")
            result = int(response.strip())

            if result == 0:
                print("Self-test PASSED")
                return True
            else:
                print("Self-test FAILED (one or more tests failed)")
                print("Use :SYSTem:ERRor[:NEXT]? to read error details")
                return False
        except pyvisa.VisaIOError as e:
            print(f"Failed to perform self-test: {e}")
            raise

    # ========================================================================
    # AUTOSET FUNCTIONS
    # ========================================================================

    def autoset(self) -> None:
        """
        Execute autoset to automatically optimize display settings.

        Reference: pdf_chapters/3.2.1_AUToset.pdf

        Raises:
            pyvisa.VisaIOError: If communication fails

        Note:
            - Automatically adjusts vertical scale, horizontal timebase, and trigger mode
            - Optimizes waveform display based on input signal
            - Same as pressing AUTO button on front panel
            - Only works if AUTO function is enabled (see set_autoset_enable())
            - Disables pass/fail test and waveform recording if they are active
            - May take a few seconds to complete

        Example:
            # Enable autoset function
            scope.set_autoset_enable(True)

            # Execute autoset
            scope.autoset()
            time.sleep(2)  # Wait for autoset to complete
        """
        try:
            self.instrument.write(":AUToset")
            print("Autoset executed - optimizing display settings...")
        except pyvisa.VisaIOError as e:
            print(f"Failed to execute autoset: {e}")
            raise

    def autoset_peak(self) -> None:
        """
        Execute autoset with peak detection optimization.

        Reference: pdf_chapters/3.2.2_AUToset_PEAK.pdf

        Raises:
            pyvisa.VisaIOError: If communication fails

        Note:
            - Similar to autoset() but optimized for peak detection
            - Useful for detecting glitches and transient signals
            - Automatically adjusts settings for optimal peak visibility
            - May take a few seconds to complete

        Example:
            # Execute peak detect autoset
            scope.autoset_peak()
            time.sleep(2)  # Wait for completion
        """
        try:
            self.instrument.write(":AUToset:PEAK")
            print("Peak detect autoset executed...")
        except pyvisa.VisaIOError as e:
            print(f"Failed to execute peak autoset: {e}")
            raise

    def set_autoset_enable(self, enable: bool) -> None:
        """
        Enable or disable the AUTO function.

        Reference: pdf_chapters/3.2.7_AUToset_ENAble.pdf

        Args:
            enable: True to enable AUTO function, False to disable

        Raises:
            pyvisa.VisaIOError: If communication fails

        Note:
            - Enables/disables the AUTO button functionality
            - When disabled, autoset() command will have no effect
            - Same as :AUToset:LOCK command (inverted logic)
            - Default is enabled (True)

        Example:
            # Enable autoset function
            scope.set_autoset_enable(True)

            # Disable autoset to prevent accidental triggering
            scope.set_autoset_enable(False)
        """
        state = 'ON' if enable else 'OFF'
        try:
            self.instrument.write(f":AUToset:ENAble {state}")
            status = "enabled" if enable else "disabled"
            print(f"Autoset function {status}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set autoset enable: {e}")
            raise

    def get_autoset_enable(self) -> bool:
        """
        Query whether the AUTO function is enabled.

        Reference: pdf_chapters/3.2.7_AUToset_ENAble.pdf

        Returns:
            bool: True if AUTO function is enabled, False if disabled

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            if scope.get_autoset_enable():
                print("AUTO function is enabled")
                scope.autoset()
            else:
                print("AUTO function is disabled")
        """
        try:
            response = self.instrument.query(":AUToset:ENAble?")
            enabled = response.strip() == '1'
            status = "enabled" if enabled else "disabled"
            print(f"Autoset function is {status}")
            return enabled
        except pyvisa.VisaIOError as e:
            print(f"Failed to query autoset enable: {e}")
            raise

    # ===================================================================
    # Phase 5.1: System Commands
    # ===================================================================

    def set_beeper_enable(self, enable: bool) -> None:
        """
        Enable or disable the oscilloscope beeper.

        Reference: pdf_chapters/3.24.2_SYSTem_BEEPer.pdf

        Args:
            enable: True to enable beeper, False to disable

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            # Enable beeper
            scope.set_beeper_enable(True)

            # Disable beeper for quiet operation
            scope.set_beeper_enable(False)
        """
        try:
            state = 'ON' if enable else 'OFF'
            self.instrument.write(f":SYSTem:BEEPer {state}")
            status = "enabled" if enable else "disabled"
            print(f"Beeper {status}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set beeper enable: {e}")
            raise

    def get_beeper_enable(self) -> bool:
        """
        Query whether the beeper is enabled.

        Reference: pdf_chapters/3.24.2_SYSTem_BEEPer.pdf

        Returns:
            bool: True if beeper is enabled, False if disabled

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            if scope.get_beeper_enable():
                print("Beeper is enabled")
            else:
                print("Beeper is disabled")
        """
        try:
            response = self.instrument.query(":SYSTem:BEEPer?")
            enabled = response.strip() == '1'
            status = "enabled" if enabled else "disabled"
            print(f"Beeper is {status}")
            return enabled
        except pyvisa.VisaIOError as e:
            print(f"Failed to query beeper enable: {e}")
            raise

    def get_next_error(self) -> dict:
        """
        Query and clear the next error from the error queue.

        Reference: pdf_chapters/3.24.3_SYSTem_ERRor[_NEXT]_.pdf

        Returns:
            dict: Dictionary with 'code' (int) and 'message' (str)
                  Returns {'code': 0, 'message': 'No error'} if queue is empty

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            error = scope.get_next_error()
            if error['code'] != 0:
                print(f"Error {error['code']}: {error['message']}")
            else:
                print("No errors in queue")
        """
        try:
            response = self.instrument.query(":SYSTem:ERRor:NEXT?")
            # Response format: <error_code>,"<error_message>"
            # Example: -113,"Undefined header; command cannot be found"
            # Example: 0,"No error"
            parts = response.strip().split(',', 1)
            error_code = int(parts[0])
            error_message = parts[1].strip('"') if len(parts) > 1 else ""

            if error_code != 0:
                print(f"Error {error_code}: {error_message}")
            else:
                print("No errors in queue")

            return {
                'code': error_code,
                'message': error_message
            }
        except pyvisa.VisaIOError as e:
            print(f"Failed to query error queue: {e}")
            raise

    def set_front_panel_lock(self, locked: bool) -> None:
        """
        Lock or unlock the front panel keys and touchscreen.

        Reference: pdf_chapters/3.24.9_SYSTem_LOCKed.pdf

        Args:
            locked: True to lock front panel, False to unlock

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            # Lock front panel during automated testing
            scope.set_front_panel_lock(True)

            # Perform automated measurements
            # ...

            # Unlock when done
            scope.set_front_panel_lock(False)
        """
        try:
            state = 'ON' if locked else 'OFF'
            self.instrument.write(f":SYSTem:LOCKed {state}")
            status = "locked" if locked else "unlocked"
            print(f"Front panel {status}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set front panel lock: {e}")
            raise

    def get_front_panel_lock(self) -> bool:
        """
        Query whether the front panel is locked.

        Reference: pdf_chapters/3.24.9_SYSTem_LOCKed.pdf

        Returns:
            bool: True if front panel is locked, False if unlocked

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            if scope.get_front_panel_lock():
                print("Front panel is locked")
            else:
                print("Front panel is unlocked")
        """
        try:
            response = self.instrument.query(":SYSTem:LOCKed?")
            locked = response.strip() == '1'
            status = "locked" if locked else "unlocked"
            print(f"Front panel is {status}")
            return locked
        except pyvisa.VisaIOError as e:
            print(f"Failed to query front panel lock: {e}")
            raise

    def get_scpi_version(self) -> str:
        """
        Query the SCPI version number used by the oscilloscope.

        Reference: pdf_chapters/3.24.13_SYSTem_VERSion_.pdf

        Returns:
            str: SCPI version number (e.g., "3.0")

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            version = scope.get_scpi_version()
            print(f"SCPI version: {version}")
        """
        try:
            response = self.instrument.query(":SYSTem:VERSion?")
            version = response.strip()
            print(f"SCPI version: {version}")
            return version
        except pyvisa.VisaIOError as e:
            print(f"Failed to query SCPI version: {e}")
            raise

    def get_channel_count(self) -> int:
        """
        Query the number of analog channels on the oscilloscope.

        Reference: pdf_chapters/3.24.6_SYSTem_RAMount_.pdf

        Returns:
            int: Number of analog channels (typically 2 or 4)

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            channels = scope.get_channel_count()
            print(f"This oscilloscope has {channels} analog channels")
        """
        try:
            response = self.instrument.query(":SYSTem:RAMount?")
            channel_count = int(response.strip())
            print(f"Analog channels: {channel_count}")
            return channel_count
        except pyvisa.VisaIOError as e:
            print(f"Failed to query channel count: {e}")
            raise

    # ===================================================================
    # Phase 4.3: Waveform Recording & Playback
    # ===================================================================

    def set_recording_enable(self, enable: bool) -> None:
        """
        Enable or disable the waveform recording function.

        Reference: pdf_chapters/3.19.1_RECord_WRECord_ENABle.pdf

        Args:
            enable: True to enable recording, False to disable

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            # Enable recording function
            scope.set_recording_enable(True)

            # Disable recording function
            scope.set_recording_enable(False)
        """
        try:
            state = 'ON' if enable else 'OFF'
            self.instrument.write(f":RECord:WRECord:ENABle {state}")
            status = "enabled" if enable else "disabled"
            print(f"Waveform recording {status}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set recording enable: {e}")
            raise

    def get_recording_enable(self) -> bool:
        """
        Query whether the waveform recording function is enabled.

        Reference: pdf_chapters/3.19.1_RECord_WRECord_ENABle.pdf

        Returns:
            bool: True if recording is enabled, False if disabled

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            if scope.get_recording_enable():
                print("Recording is enabled")
            else:
                print("Recording is disabled")
        """
        try:
            response = self.instrument.query(":RECord:WRECord:ENABle?")
            enabled = response.strip() == '1'
            status = "enabled" if enabled else "disabled"
            print(f"Waveform recording is {status}")
            return enabled
        except pyvisa.VisaIOError as e:
            print(f"Failed to query recording enable: {e}")
            raise

    def set_recording_frames(self, frames: int) -> None:
        """
        Set the number of frames to record.

        Reference: pdf_chapters/3.19.5_RECord_WRECord_FRAMes.pdf

        Args:
            frames: Number of frames to record (1 to max available)

        Raises:
            ValueError: If frames is less than 1
            pyvisa.VisaIOError: If communication fails

        Example:
            # Record 1000 frames
            scope.set_recording_frames(1000)

            # Record 100 frames
            scope.set_recording_frames(100)
        """
        if frames < 1:
            raise ValueError(f"Frames must be at least 1, got {frames}")

        try:
            self.instrument.write(f":RECord:WRECord:FRAMes {frames}")
            print(f"Recording frames set to {frames}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set recording frames: {e}")
            raise

    def get_recording_frames(self) -> int:
        """
        Query the number of frames configured for recording.

        Reference: pdf_chapters/3.19.5_RECord_WRECord_FRAMes.pdf

        Returns:
            int: Number of frames configured for recording

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            frames = scope.get_recording_frames()
            print(f"Will record {frames} frames")
        """
        try:
            response = self.instrument.query(":RECord:WRECord:FRAMes?")
            frames = int(response.strip())
            print(f"Recording frames: {frames}")
            return frames
        except pyvisa.VisaIOError as e:
            print(f"Failed to query recording frames: {e}")
            raise

    def get_max_recording_frames(self) -> int:
        """
        Query the maximum number of frames that can be recorded.

        Reference: pdf_chapters/3.19.8_RECord_WRECord_FMAX_.pdf

        Returns:
            int: Maximum number of frames available for recording

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            max_frames = scope.get_max_recording_frames()
            print(f"Can record up to {max_frames} frames")
        """
        try:
            response = self.instrument.query(":RECord:WRECord:FMAX?")
            max_frames = int(response.strip())
            print(f"Maximum recording frames: {max_frames}")
            return max_frames
        except pyvisa.VisaIOError as e:
            print(f"Failed to query max recording frames: {e}")
            raise

    def start_recording(self) -> None:
        """
        Start waveform recording.

        Reference: pdf_chapters/3.19.3_RECord_WRECord_OPERate.pdf

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            # Enable recording and start
            scope.set_recording_enable(True)
            scope.set_recording_frames(1000)
            scope.start_recording()
            # Wait for recording to complete
            time.sleep(5)
            scope.stop_recording()
        """
        try:
            self.instrument.write(":RECord:WRECord:OPERate RUN")
            print("Waveform recording started")
        except pyvisa.VisaIOError as e:
            print(f"Failed to start recording: {e}")
            raise

    def stop_recording(self) -> None:
        """
        Stop waveform recording.

        Reference: pdf_chapters/3.19.3_RECord_WRECord_OPERate.pdf

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            # Stop ongoing recording
            scope.stop_recording()
        """
        try:
            self.instrument.write(":RECord:WRECord:OPERate STOP")
            print("Waveform recording stopped")
        except pyvisa.VisaIOError as e:
            print(f"Failed to stop recording: {e}")
            raise

    def get_recording_status(self) -> str:
        """
        Query whether waveform recording is running or stopped.

        Reference: pdf_chapters/3.19.3_RECord_WRECord_OPERate.pdf

        Returns:
            str: 'RUN' if recording is active, 'STOP' if not

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            status = scope.get_recording_status()
            if status == 'RUN':
                print("Recording in progress")
            else:
                print("Recording stopped")
        """
        try:
            response = self.instrument.query(":RECord:WRECord:OPERate?")
            status = response.strip()
            print(f"Recording status: {status}")
            return status
        except pyvisa.VisaIOError as e:
            print(f"Failed to query recording status: {e}")
            raise

    def set_playback_current_frame(self, frame: int) -> None:
        """
        Set the current frame for playback.

        Reference: pdf_chapters/3.19.11_RECord_WREPlay_FCURrent.pdf

        Args:
            frame: Frame number to display (1 to number of recorded frames)

        Raises:
            ValueError: If frame is less than 1
            pyvisa.VisaIOError: If communication fails

        Example:
            # Jump to frame 500
            scope.set_playback_current_frame(500)
        """
        if frame < 1:
            raise ValueError(f"Frame must be at least 1, got {frame}")

        try:
            self.instrument.write(f":RECord:WREPlay:FCURrent {frame}")
            print(f"Playback frame set to {frame}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set playback frame: {e}")
            raise

    def get_playback_current_frame(self) -> int:
        """
        Query the current frame in playback.

        Reference: pdf_chapters/3.19.11_RECord_WREPlay_FCURrent.pdf

        Returns:
            int: Current frame number

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            frame = scope.get_playback_current_frame()
            print(f"Currently viewing frame {frame}")
        """
        try:
            response = self.instrument.query(":RECord:WREPlay:FCURrent?")
            frame = int(response.strip())
            print(f"Current playback frame: {frame}")
            return frame
        except pyvisa.VisaIOError as e:
            print(f"Failed to query playback frame: {e}")
            raise

    def start_playback(self) -> None:
        """
        Start automatic playback of recorded waveforms.

        Reference: pdf_chapters/3.19.20_RECord_WREPlay_OPERate.pdf

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            # Start automatic playback
            scope.start_playback()
            # Playback will cycle through recorded frames
            time.sleep(10)
            scope.stop_playback()
        """
        try:
            self.instrument.write(":RECord:WREPlay:OPERate RUN")
            print("Waveform playback started")
        except pyvisa.VisaIOError as e:
            print(f"Failed to start playback: {e}")
            raise

    def stop_playback(self) -> None:
        """
        Stop automatic playback of recorded waveforms.

        Reference: pdf_chapters/3.19.20_RECord_WREPlay_OPERate.pdf

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            # Stop playback
            scope.stop_playback()
        """
        try:
            self.instrument.write(":RECord:WREPlay:OPERate STOP")
            print("Waveform playback stopped")
        except pyvisa.VisaIOError as e:
            print(f"Failed to stop playback: {e}")
            raise

    def get_playback_status(self) -> str:
        """
        Query whether automatic playback is running or stopped.

        Reference: pdf_chapters/3.19.20_RECord_WREPlay_OPERate.pdf

        Returns:
            str: 'RUN' if playback is active, 'STOP' if not

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            status = scope.get_playback_status()
            if status == 'RUN':
                print("Playback in progress")
            else:
                print("Playback stopped")
        """
        try:
            response = self.instrument.query(":RECord:WREPlay:OPERate?")
            status = response.strip()
            print(f"Playback status: {status}")
            return status
        except pyvisa.VisaIOError as e:
            print(f"Failed to query playback status: {e}")
            raise

    def playback_next_frame(self) -> None:
        """
        Manually step to the next frame in playback.

        Reference: pdf_chapters/3.19.23_RECord_WREPlay_NEXT.pdf

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            # Step through frames manually
            for i in range(10):
                scope.playback_next_frame()
                time.sleep(0.5)
        """
        try:
            self.instrument.write(":RECord:WREPlay:NEXT")
            print("Stepped to next frame")
        except pyvisa.VisaIOError as e:
            print(f"Failed to step to next frame: {e}")
            raise

    def playback_previous_frame(self) -> None:
        """
        Manually step to the previous frame in playback.

        Reference: pdf_chapters/3.19.22_RECord_WREPlay_BACK.pdf

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            # Step backward through frames
            for i in range(10):
                scope.playback_previous_frame()
                time.sleep(0.5)
        """
        try:
            self.instrument.write(":RECord:WREPlay:BACK")
            print("Stepped to previous frame")
        except pyvisa.VisaIOError as e:
            print(f"Failed to step to previous frame: {e}")
            raise

    # ===================================================================
    # Phase 4.5: Pass/Fail Mask Testing
    # ===================================================================

    def set_mask_enable(self, enable: bool) -> None:
        """
        Enable or disable the pass/fail mask testing function.

        Reference: pdf_chapters/3.15.1_MASK_ENABle.pdf

        Args:
            enable: True to enable mask testing, False to disable

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            # Enable mask testing
            scope.set_mask_enable(True)

            # Disable mask testing
            scope.set_mask_enable(False)
        """
        try:
            state = 'ON' if enable else 'OFF'
            self.instrument.write(f":MASK:ENABle {state}")
            status = "enabled" if enable else "disabled"
            print(f"Mask testing {status}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set mask enable: {e}")
            raise

    def get_mask_enable(self) -> bool:
        """
        Query whether the pass/fail mask testing function is enabled.

        Reference: pdf_chapters/3.15.1_MASK_ENABle.pdf

        Returns:
            bool: True if mask testing is enabled, False if disabled

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            if scope.get_mask_enable():
                print("Mask testing is enabled")
            else:
                print("Mask testing is disabled")
        """
        try:
            response = self.instrument.query(":MASK:ENABle?")
            enabled = response.strip() == '1'
            status = "enabled" if enabled else "disabled"
            print(f"Mask testing is {status}")
            return enabled
        except pyvisa.VisaIOError as e:
            print(f"Failed to query mask enable: {e}")
            raise

    def set_mask_source(self, channel: int) -> None:
        """
        Set the source channel for pass/fail mask testing.

        Reference: pdf_chapters/3.15.2_MASK_SOURce.pdf

        Args:
            channel: Channel number (1-4)

        Raises:
            ValueError: If channel is not 1-4
            pyvisa.VisaIOError: If communication fails

        Example:
            # Test channel 1 against mask
            scope.set_mask_source(1)

            # Test channel 2 against mask
            scope.set_mask_source(2)
        """
        if channel not in (1, 2, 3, 4):
            raise ValueError(f"Channel must be 1-4, got {channel}")

        try:
            self.instrument.write(f":MASK:SOURce CHANnel{channel}")
            print(f"Mask test source set to CH{channel}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set mask source: {e}")
            raise

    def get_mask_source(self) -> int:
        """
        Query the source channel for pass/fail mask testing.

        Reference: pdf_chapters/3.15.2_MASK_SOURce.pdf

        Returns:
            int: Channel number (1-4)

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            channel = scope.get_mask_source()
            print(f"Testing channel {channel}")
        """
        try:
            response = self.instrument.query(":MASK:SOURce?")
            # Response format: CHAN1, CHAN2, etc.
            channel_str = response.strip()
            channel = int(channel_str.replace('CHAN', ''))
            print(f"Mask test source: CH{channel}")
            return channel
        except pyvisa.VisaIOError as e:
            print(f"Failed to query mask source: {e}")
            raise

    def set_mask_tolerance_x(self, tolerance: float) -> None:
        """
        Set the horizontal (time) tolerance for the mask.

        Reference: pdf_chapters/3.15.4_MASK_X.pdf

        Args:
            tolerance: Horizontal tolerance in divisions (0.01 to 2.0)

        Raises:
            ValueError: If tolerance is out of range
            pyvisa.VisaIOError: If communication fails

        Example:
            # Set horizontal tolerance to 0.3 divisions
            scope.set_mask_tolerance_x(0.3)
        """
        if tolerance < 0.01 or tolerance > 2.0:
            raise ValueError(f"Tolerance must be 0.01-2.0 div, got {tolerance}")

        try:
            self.instrument.write(f":MASK:X {tolerance}")
            print(f"Mask horizontal tolerance: {tolerance} div")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set mask X tolerance: {e}")
            raise

    def get_mask_tolerance_x(self) -> float:
        """
        Query the horizontal (time) tolerance for the mask.

        Reference: pdf_chapters/3.15.4_MASK_X.pdf

        Returns:
            float: Horizontal tolerance in divisions

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            tolerance = scope.get_mask_tolerance_x()
            print(f"Horizontal tolerance: {tolerance} div")
        """
        try:
            response = self.instrument.query(":MASK:X?")
            tolerance = float(response.strip())
            print(f"Mask horizontal tolerance: {tolerance} div")
            return tolerance
        except pyvisa.VisaIOError as e:
            print(f"Failed to query mask X tolerance: {e}")
            raise

    def set_mask_tolerance_y(self, tolerance: float) -> None:
        """
        Set the vertical (voltage) tolerance for the mask.

        Reference: pdf_chapters/3.15.5_MASK_Y.pdf

        Args:
            tolerance: Vertical tolerance in divisions (0.04 to 2.0)

        Raises:
            ValueError: If tolerance is out of range
            pyvisa.VisaIOError: If communication fails

        Example:
            # Set vertical tolerance to 0.5 divisions
            scope.set_mask_tolerance_y(0.5)
        """
        if tolerance < 0.04 or tolerance > 2.0:
            raise ValueError(f"Tolerance must be 0.04-2.0 div, got {tolerance}")

        try:
            self.instrument.write(f":MASK:Y {tolerance}")
            print(f"Mask vertical tolerance: {tolerance} div")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set mask Y tolerance: {e}")
            raise

    def get_mask_tolerance_y(self) -> float:
        """
        Query the vertical (voltage) tolerance for the mask.

        Reference: pdf_chapters/3.15.5_MASK_Y.pdf

        Returns:
            float: Vertical tolerance in divisions

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            tolerance = scope.get_mask_tolerance_y()
            print(f"Vertical tolerance: {tolerance} div")
        """
        try:
            response = self.instrument.query(":MASK:Y?")
            tolerance = float(response.strip())
            print(f"Mask vertical tolerance: {tolerance} div")
            return tolerance
        except pyvisa.VisaIOError as e:
            print(f"Failed to query mask Y tolerance: {e}")
            raise

    def create_mask(self) -> None:
        """
        Create a pass/fail mask from the current waveform.

        Reference: pdf_chapters/3.15.6_MASK_CREate.pdf

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            # Setup ideal waveform
            scope.enable_channel(1)
            scope.run()
            time.sleep(1)

            # Set tolerances
            scope.set_mask_tolerance_x(0.3)
            scope.set_mask_tolerance_y(0.5)

            # Create mask from current waveform
            scope.create_mask()
        """
        try:
            self.instrument.write(":MASK:CREate")
            print("Mask created from current waveform")
        except pyvisa.VisaIOError as e:
            print(f"Failed to create mask: {e}")
            raise

    def start_mask_test(self) -> None:
        """
        Start the pass/fail mask test.

        Reference: pdf_chapters/3.15.3_MASK_OPERate.pdf

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            # Enable and start mask testing
            scope.set_mask_enable(True)
            scope.start_mask_test()

            # Wait for testing
            time.sleep(10)

            # Check results
            stats = scope.get_mask_statistics()
            print(f"Passed: {stats['passed']}, Failed: {stats['failed']}")

            scope.stop_mask_test()
        """
        try:
            self.instrument.write(":MASK:OPERate RUN")
            print("Mask test started")
        except pyvisa.VisaIOError as e:
            print(f"Failed to start mask test: {e}")
            raise

    def stop_mask_test(self) -> None:
        """
        Stop the pass/fail mask test.

        Reference: pdf_chapters/3.15.3_MASK_OPERate.pdf

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            # Stop mask testing
            scope.stop_mask_test()
        """
        try:
            self.instrument.write(":MASK:OPERate STOP")
            print("Mask test stopped")
        except pyvisa.VisaIOError as e:
            print(f"Failed to stop mask test: {e}")
            raise

    def get_mask_test_status(self) -> str:
        """
        Query whether the mask test is running or stopped.

        Reference: pdf_chapters/3.15.3_MASK_OPERate.pdf

        Returns:
            str: 'RUN' if testing is active, 'STOP' if not

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            status = scope.get_mask_test_status()
            if status == 'RUN':
                print("Mask test in progress")
            else:
                print("Mask test stopped")
        """
        try:
            response = self.instrument.query(":MASK:OPERate?")
            status = response.strip()
            print(f"Mask test status: {status}")
            return status
        except pyvisa.VisaIOError as e:
            print(f"Failed to query mask test status: {e}")
            raise

    def reset_mask_statistics(self) -> None:
        """
        Reset the pass/fail test statistics counters.

        Reference: pdf_chapters/3.15.7_MASK_RESet.pdf

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            # Reset counters before starting new test
            scope.reset_mask_statistics()
            scope.start_mask_test()
        """
        try:
            self.instrument.write(":MASK:RESet")
            print("Mask statistics reset")
        except pyvisa.VisaIOError as e:
            print(f"Failed to reset mask statistics: {e}")
            raise

    def get_mask_failed_count(self) -> int:
        """
        Query the number of frames that failed the mask test.

        Reference: pdf_chapters/3.15.8_MASK_FAILed_.pdf

        Returns:
            int: Number of failed frames

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            failed = scope.get_mask_failed_count()
            print(f"{failed} frames failed the test")
        """
        try:
            response = self.instrument.query(":MASK:FAILed?")
            failed = int(response.strip())
            print(f"Failed frames: {failed}")
            return failed
        except pyvisa.VisaIOError as e:
            print(f"Failed to query mask failed count: {e}")
            raise

    def get_mask_passed_count(self) -> int:
        """
        Query the number of frames that passed the mask test.

        Reference: pdf_chapters/3.15.9_MASK_PASSed_.pdf

        Returns:
            int: Number of passed frames

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            passed = scope.get_mask_passed_count()
            print(f"{passed} frames passed the test")
        """
        try:
            response = self.instrument.query(":MASK:PASSed?")
            passed = int(response.strip())
            print(f"Passed frames: {passed}")
            return passed
        except pyvisa.VisaIOError as e:
            print(f"Failed to query mask passed count: {e}")
            raise

    def get_mask_total_count(self) -> int:
        """
        Query the total number of frames tested.

        Reference: pdf_chapters/3.15.10_MASK_TOTal_.pdf

        Returns:
            int: Total number of frames tested

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            total = scope.get_mask_total_count()
            print(f"{total} total frames tested")
        """
        try:
            response = self.instrument.query(":MASK:TOTal?")
            total = int(response.strip())
            print(f"Total frames tested: {total}")
            return total
        except pyvisa.VisaIOError as e:
            print(f"Failed to query mask total count: {e}")
            raise

    def get_mask_statistics(self) -> dict:
        """
        Query all pass/fail test statistics at once.

        Returns:
            dict: Dictionary with 'passed', 'failed', 'total' counts

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            stats = scope.get_mask_statistics()
            print(f"Results: {stats['passed']} passed, {stats['failed']} failed")
            print(f"Pass rate: {stats['passed']/stats['total']*100:.1f}%")
        """
        try:
            passed = int(self.instrument.query(":MASK:PASSed?").strip())
            failed = int(self.instrument.query(":MASK:FAILed?").strip())
            total = int(self.instrument.query(":MASK:TOTal?").strip())

            print(f"Mask statistics: {passed} passed, {failed} failed, {total} total")

            return {
                'passed': passed,
                'failed': failed,
                'total': total
            }
        except pyvisa.VisaIOError as e:
            print(f"Failed to query mask statistics: {e}")
            raise

    # =========================================================================
    # PHASE 4.7: Counter/DVM Commands
    # =========================================================================
    # Counter Commands - Frequency counter measurements

    def get_counter_current(self) -> float:
        """
        Query the current measurement value of the frequency counter.

        Returns:
            float: Current counter measurement value in scientific notation

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            freq = scope.get_counter_current()
            print(f"Current measurement: {freq} Hz")
        """
        try:
            response = self.instrument.query(":COUNter:CURRent?")
            value = float(response.strip())
            print(f"Counter current value: {value}")
            return value
        except pyvisa.VisaIOError as e:
            print(f"Failed to query counter current value: {e}")
            raise

    def set_counter_enable(self, enable: bool) -> None:
        """
        Enable or disable the frequency counter.

        Args:
            enable: True to enable, False to disable

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            scope.set_counter_enable(True)  # Enable counter
        """
        try:
            state = 'ON' if enable else 'OFF'
            self.instrument.write(f":COUNter:ENABle {state}")
            print(f"Counter {'enabled' if enable else 'disabled'}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set counter enable: {e}")
            raise

    def get_counter_enable(self) -> bool:
        """
        Query the on/off status of the frequency counter.

        Returns:
            bool: True if enabled, False if disabled

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            if scope.get_counter_enable():
                print("Counter is enabled")
        """
        try:
            response = self.instrument.query(":COUNter:ENABle?")
            enabled = bool(int(response.strip()))
            print(f"Counter enable: {enabled}")
            return enabled
        except pyvisa.VisaIOError as e:
            print(f"Failed to query counter enable: {e}")
            raise

    def set_counter_source(self, source: int) -> None:
        """
        Set the source of the frequency counter.

        Args:
            source: Channel number (1-4) for analog channels

        Raises:
            pyvisa.VisaIOError: If communication fails
            ValueError: If source is invalid

        Example:
            scope.set_counter_source(1)  # Set to CH1
        """
        try:
            if source not in [1, 2, 3, 4]:
                raise ValueError("Source must be 1, 2, 3, or 4")

            self.instrument.write(f":COUNter:SOURce CHANnel{source}")
            print(f"Counter source set to CH{source}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set counter source: {e}")
            raise

    def get_counter_source(self) -> int:
        """
        Query the source of the frequency counter.

        Returns:
            int: Channel number (1-4)

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            source = scope.get_counter_source()
            print(f"Counter source: CH{source}")
        """
        try:
            response = self.instrument.query(":COUNter:SOURce?")
            # Response is like "CHAN1" or "CHAN2"
            source_str = response.strip()
            if source_str.startswith('CHAN'):
                source = int(source_str[4:])
            else:
                source = 1  # Default
            print(f"Counter source: CH{source}")
            return source
        except pyvisa.VisaIOError as e:
            print(f"Failed to query counter source: {e}")
            raise

    def set_counter_mode(self, mode: str) -> None:
        """
        Set the mode of the frequency counter.

        Args:
            mode: Counter mode ('FREQuency', 'PERiod', or 'TOTalize')

        Raises:
            pyvisa.VisaIOError: If communication fails
            ValueError: If mode is invalid

        Example:
            scope.set_counter_mode('FREQuency')  # Measure frequency
            scope.set_counter_mode('PERiod')     # Measure period
        """
        try:
            valid_modes = ['FREQuency', 'PERiod', 'TOTalize']
            if mode not in valid_modes:
                raise ValueError(f"Mode must be one of {valid_modes}")

            self.instrument.write(f":COUNter:MODE {mode}")
            print(f"Counter mode set to {mode}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set counter mode: {e}")
            raise

    def get_counter_mode(self) -> str:
        """
        Query the mode of the frequency counter.

        Returns:
            str: Counter mode ('FREQ', 'PER', or 'TOT')

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            mode = scope.get_counter_mode()
            print(f"Counter mode: {mode}")
        """
        try:
            response = self.instrument.query(":COUNter:MODE?")
            mode = response.strip()
            print(f"Counter mode: {mode}")
            return mode
        except pyvisa.VisaIOError as e:
            print(f"Failed to query counter mode: {e}")
            raise

    def set_counter_resolution(self, digits: int) -> None:
        """
        Set the resolution of the frequency counter.

        Args:
            digits: Number of digits (3-6)

        Raises:
            pyvisa.VisaIOError: If communication fails
            ValueError: If digits is out of range

        Example:
            scope.set_counter_resolution(5)  # 5-digit resolution
        """
        try:
            if digits < 3 or digits > 6:
                raise ValueError("Resolution must be between 3 and 6 digits")

            self.instrument.write(f":COUNter:NDIGits {digits}")
            print(f"Counter resolution set to {digits} digits")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set counter resolution: {e}")
            raise

    def get_counter_resolution(self) -> int:
        """
        Query the resolution of the frequency counter.

        Returns:
            int: Number of digits (3-6)

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            digits = scope.get_counter_resolution()
            print(f"Counter resolution: {digits} digits")
        """
        try:
            response = self.instrument.query(":COUNter:NDIGits?")
            digits = int(response.strip())
            print(f"Counter resolution: {digits} digits")
            return digits
        except pyvisa.VisaIOError as e:
            print(f"Failed to query counter resolution: {e}")
            raise

    def set_counter_totalize_enable(self, enable: bool) -> None:
        """
        Enable or disable the statistical function of the frequency counter.

        Args:
            enable: True to enable totalize statistics, False to disable

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            scope.set_counter_totalize_enable(True)  # Enable totalize
        """
        try:
            state = 'ON' if enable else 'OFF'
            self.instrument.write(f":COUNter:TOTalize:ENABle {state}")
            print(f"Counter totalize {'enabled' if enable else 'disabled'}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set counter totalize enable: {e}")
            raise

    def get_counter_totalize_enable(self) -> bool:
        """
        Query the on/off status of the totalize function.

        Returns:
            bool: True if enabled, False if disabled

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            if scope.get_counter_totalize_enable():
                print("Totalize is enabled")
        """
        try:
            response = self.instrument.query(":COUNter:TOTalize:ENABle?")
            enabled = bool(int(response.strip()))
            print(f"Counter totalize enable: {enabled}")
            return enabled
        except pyvisa.VisaIOError as e:
            print(f"Failed to query counter totalize enable: {e}")
            raise

    def clear_counter_totalize(self) -> None:
        """
        Clear the totalize statistics of the frequency counter.

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            scope.clear_counter_totalize()  # Reset totalize count
        """
        try:
            self.instrument.write(":COUNter:TOTalize:CLEar")
            print("Counter totalize cleared")
        except pyvisa.VisaIOError as e:
            print(f"Failed to clear counter totalize: {e}")
            raise

    # DVM Commands - Digital voltmeter measurements

    def get_dvm_current(self) -> float:
        """
        Query the current voltage value under test.

        Returns:
            float: Current voltage value

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            voltage = scope.get_dvm_current()
            print(f"Current voltage: {voltage} V")
        """
        try:
            response = self.instrument.query(":DVM:CURRent?")
            value = float(response.strip())
            print(f"DVM current value: {value} V")
            return value
        except pyvisa.VisaIOError as e:
            print(f"Failed to query DVM current value: {e}")
            raise

    def set_dvm_enable(self, enable: bool) -> None:
        """
        Enable or disable the digital voltmeter.

        Args:
            enable: True to enable, False to disable

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            scope.set_dvm_enable(True)  # Enable DVM
        """
        try:
            state = 'ON' if enable else 'OFF'
            self.instrument.write(f":DVM:ENABle {state}")
            print(f"DVM {'enabled' if enable else 'disabled'}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set DVM enable: {e}")
            raise

    def get_dvm_enable(self) -> bool:
        """
        Query the on/off status of the digital voltmeter.

        Returns:
            bool: True if enabled, False if disabled

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            if scope.get_dvm_enable():
                print("DVM is enabled")
        """
        try:
            response = self.instrument.query(":DVM:ENABle?")
            enabled = bool(int(response.strip()))
            print(f"DVM enable: {enabled}")
            return enabled
        except pyvisa.VisaIOError as e:
            print(f"Failed to query DVM enable: {e}")
            raise

    def set_dvm_source(self, source: int) -> None:
        """
        Set the source of the digital voltmeter.

        Args:
            source: Channel number (1-4)

        Raises:
            pyvisa.VisaIOError: If communication fails
            ValueError: If source is invalid

        Example:
            scope.set_dvm_source(2)  # Set to CH2
        """
        try:
            if source not in [1, 2, 3, 4]:
                raise ValueError("Source must be 1, 2, 3, or 4")

            self.instrument.write(f":DVM:SOURce CHANnel{source}")
            print(f"DVM source set to CH{source}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set DVM source: {e}")
            raise

    def get_dvm_source(self) -> int:
        """
        Query the source of the digital voltmeter.

        Returns:
            int: Channel number (1-4)

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            source = scope.get_dvm_source()
            print(f"DVM source: CH{source}")
        """
        try:
            response = self.instrument.query(":DVM:SOURce?")
            # Response is like "CHAN1" or "CHAN2"
            source_str = response.strip()
            if source_str.startswith('CHAN'):
                source = int(source_str[4:])
            else:
                source = 1  # Default
            print(f"DVM source: CH{source}")
            return source
        except pyvisa.VisaIOError as e:
            print(f"Failed to query DVM source: {e}")
            raise

    def set_dvm_mode(self, mode: str) -> None:
        """
        Set the mode of the digital voltmeter.

        Args:
            mode: DVM mode (typically 'DC', 'AC', etc.)

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            scope.set_dvm_mode('DC')  # DC voltage measurement
        """
        try:
            self.instrument.write(f":DVM:MODE {mode}")
            print(f"DVM mode set to {mode}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set DVM mode: {e}")
            raise

    def get_dvm_mode(self) -> str:
        """
        Query the mode of the digital voltmeter.

        Returns:
            str: DVM mode

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            mode = scope.get_dvm_mode()
            print(f"DVM mode: {mode}")
        """
        try:
            response = self.instrument.query(":DVM:MODE?")
            mode = response.strip()
            print(f"DVM mode: {mode}")
            return mode
        except pyvisa.VisaIOError as e:
            print(f"Failed to query DVM mode: {e}")
            raise

    # =========================================================================
    # PHASE 4.4: Histogram Analysis Commands
    # =========================================================================
    # NOTE: Histogram analysis is only supported on DHO900 series, not DHO800

    def set_histogram_enable(self, enable: bool) -> None:
        """
        Enable or disable the histogram function.

        Note: Histogram analysis is only supported on DHO900 series.

        Args:
            enable: True to enable, False to disable

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            scope.set_histogram_enable(True)  # Enable histogram
        """
        try:
            state = 'ON' if enable else 'OFF'
            self.instrument.write(f":HISTogram:ENABle {state}")
            print(f"Histogram {'enabled' if enable else 'disabled'}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set histogram enable: {e}")
            raise

    def get_histogram_enable(self) -> bool:
        """
        Query the on/off status of the histogram.

        Returns:
            bool: True if enabled, False if disabled

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            if scope.get_histogram_enable():
                print("Histogram is enabled")
        """
        try:
            response = self.instrument.query(":HISTogram:ENABle?")
            enabled = bool(int(response.strip()))
            print(f"Histogram enable: {enabled}")
            return enabled
        except pyvisa.VisaIOError as e:
            print(f"Failed to query histogram enable: {e}")
            raise

    def set_histogram_type(self, hist_type: str) -> None:
        """
        Set the type of the histogram.

        Args:
            hist_type: Histogram type ('HORizontal' or 'VERTical')

        Raises:
            pyvisa.VisaIOError: If communication fails
            ValueError: If type is invalid

        Example:
            scope.set_histogram_type('VERTical')  # Vertical histogram
            scope.set_histogram_type('HORizontal')  # Horizontal histogram
        """
        try:
            valid_types = ['HORizontal', 'VERTical']
            if hist_type not in valid_types:
                raise ValueError(f"Type must be one of {valid_types}")

            self.instrument.write(f":HISTogram:TYPE {hist_type}")
            print(f"Histogram type set to {hist_type}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set histogram type: {e}")
            raise

    def get_histogram_type(self) -> str:
        """
        Query the type of the histogram.

        Returns:
            str: Histogram type ('HOR' or 'VERT')

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            hist_type = scope.get_histogram_type()
            print(f"Histogram type: {hist_type}")
        """
        try:
            response = self.instrument.query(":HISTogram:TYPE?")
            hist_type = response.strip()
            print(f"Histogram type: {hist_type}")
            return hist_type
        except pyvisa.VisaIOError as e:
            print(f"Failed to query histogram type: {e}")
            raise

    def set_histogram_source(self, source: int) -> None:
        """
        Set the source of the histogram.

        Args:
            source: Channel number (1-4)

        Raises:
            pyvisa.VisaIOError: If communication fails
            ValueError: If source is invalid

        Example:
            scope.set_histogram_source(1)  # Set to CH1
        """
        try:
            if source not in [1, 2, 3, 4]:
                raise ValueError("Source must be 1, 2, 3, or 4")

            self.instrument.write(f":HISTogram:SOURce CHANnel{source}")
            print(f"Histogram source set to CH{source}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set histogram source: {e}")
            raise

    def get_histogram_source(self) -> int:
        """
        Query the source of the histogram.

        Returns:
            int: Channel number (1-4)

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            source = scope.get_histogram_source()
            print(f"Histogram source: CH{source}")
        """
        try:
            response = self.instrument.query(":HISTogram:SOURce?")
            # Response is like "CHAN1" or "CHAN2"
            source_str = response.strip()
            if source_str.startswith('CHAN'):
                source = int(source_str[4:])
            else:
                source = 1  # Default
            print(f"Histogram source: CH{source}")
            return source
        except pyvisa.VisaIOError as e:
            print(f"Failed to query histogram source: {e}")
            raise

    def set_histogram_height(self, height: int) -> None:
        """
        Set the height of the histogram.

        Args:
            height: Height in divisions (1-4)

        Raises:
            pyvisa.VisaIOError: If communication fails
            ValueError: If height is out of range

        Example:
            scope.set_histogram_height(2)  # 2 divisions height
        """
        try:
            if height < 1 or height > 4:
                raise ValueError("Height must be between 1 and 4 divisions")

            self.instrument.write(f":HISTogram:HEIGht {height}")
            print(f"Histogram height set to {height} div")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set histogram height: {e}")
            raise

    def get_histogram_height(self) -> int:
        """
        Query the height of the histogram.

        Returns:
            int: Height in divisions (1-4)

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            height = scope.get_histogram_height()
            print(f"Histogram height: {height} div")
        """
        try:
            response = self.instrument.query(":HISTogram:HEIGht?")
            height = int(response.strip())
            print(f"Histogram height: {height} div")
            return height
        except pyvisa.VisaIOError as e:
            print(f"Failed to query histogram height: {e}")
            raise

    def set_histogram_range_left(self, value: float) -> None:
        """
        Set the left limit of the histogram.

        Args:
            value: Left limit in seconds
                   Range: (-5 × timebase + offset) to (5 × timebase + offset)

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            scope.set_histogram_range_left(-0.002)  # -2 ms
        """
        try:
            self.instrument.write(f":HISTogram:RANGe:LEFT {value}")
            print(f"Histogram left limit set to {value} s")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set histogram left limit: {e}")
            raise

    def get_histogram_range_left(self) -> float:
        """
        Query the left limit of the histogram.

        Returns:
            float: Left limit in seconds

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            left = scope.get_histogram_range_left()
            print(f"Histogram left limit: {left} s")
        """
        try:
            response = self.instrument.query(":HISTogram:RANGe:LEFT?")
            value = float(response.strip())
            print(f"Histogram left limit: {value} s")
            return value
        except pyvisa.VisaIOError as e:
            print(f"Failed to query histogram left limit: {e}")
            raise

    def set_histogram_range_right(self, value: float) -> None:
        """
        Set the right limit of the histogram.

        Args:
            value: Right limit in seconds
                   Range: (-5 × timebase + offset) to (5 × timebase + offset)

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            scope.set_histogram_range_right(0.002)  # 2 ms
        """
        try:
            self.instrument.write(f":HISTogram:RANGe:RIGHt {value}")
            print(f"Histogram right limit set to {value} s")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set histogram right limit: {e}")
            raise

    def get_histogram_range_right(self) -> float:
        """
        Query the right limit of the histogram.

        Returns:
            float: Right limit in seconds

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            right = scope.get_histogram_range_right()
            print(f"Histogram right limit: {right} s")
        """
        try:
            response = self.instrument.query(":HISTogram:RANGe:RIGHt?")
            value = float(response.strip())
            print(f"Histogram right limit: {value} s")
            return value
        except pyvisa.VisaIOError as e:
            print(f"Failed to query histogram right limit: {e}")
            raise

    def set_histogram_range_top(self, value: float) -> None:
        """
        Set the top limit of the histogram.

        Args:
            value: Top limit in volts
                   Range: (-4 × vertical scale - offset) to (4 × vertical scale - offset)

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            scope.set_histogram_range_top(2.0)  # 2 V
        """
        try:
            self.instrument.write(f":HISTogram:RANGe:TOP {value}")
            print(f"Histogram top limit set to {value} V")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set histogram top limit: {e}")
            raise

    def get_histogram_range_top(self) -> float:
        """
        Query the top limit of the histogram.

        Returns:
            float: Top limit in volts

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            top = scope.get_histogram_range_top()
            print(f"Histogram top limit: {top} V")
        """
        try:
            response = self.instrument.query(":HISTogram:RANGe:TOP?")
            value = float(response.strip())
            print(f"Histogram top limit: {value} V")
            return value
        except pyvisa.VisaIOError as e:
            print(f"Failed to query histogram top limit: {e}")
            raise

    def set_histogram_range_bottom(self, value: float) -> None:
        """
        Set the bottom limit of the histogram.

        Args:
            value: Bottom limit in volts
                   Range: (-4 × vertical scale - offset) to (4 × vertical scale - offset)

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            scope.set_histogram_range_bottom(-2.0)  # -2 V
        """
        try:
            self.instrument.write(f":HISTogram:RANGe:BOTTom {value}")
            print(f"Histogram bottom limit set to {value} V")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set histogram bottom limit: {e}")
            raise

    def get_histogram_range_bottom(self) -> float:
        """
        Query the bottom limit of the histogram.

        Returns:
            float: Bottom limit in volts

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            bottom = scope.get_histogram_range_bottom()
            print(f"Histogram bottom limit: {bottom} V")
        """
        try:
            response = self.instrument.query(":HISTogram:RANGe:BOTTom?")
            value = float(response.strip())
            print(f"Histogram bottom limit: {value} V")
            return value
        except pyvisa.VisaIOError as e:
            print(f"Failed to query histogram bottom limit: {e}")
            raise

    def get_histogram_statistics(self) -> dict:
        """
        Query all histogram statistical results.

        Returns:
            dict: Dictionary containing all histogram statistics with keys:
                  - 'sum': Sum of all bins
                  - 'peaks': Maximum hits in any single bin
                  - 'max': Maximum value
                  - 'min': Minimum value
                  - 'pk_pk': Peak-to-peak (max - min)
                  - 'mean': Average value
                  - 'median': Median value
                  - 'mode': Mode value
                  - 'bin_width': Width of each bin
                  - 'sigma': Standard deviation
                  - 'xscale': Horizontal scale (100 × bin width)

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            stats = scope.get_histogram_statistics()
            print(f"Mean: {stats['mean']}, Sigma: {stats['sigma']}")
            print(f"Peak-to-peak: {stats['pk_pk']}")
        """
        try:
            response = self.instrument.query(":HISTogram:STATistics:RESult?")

            # Parse the response - format is comma-separated values
            values = response.strip().split(',')

            # Map values to dictionary
            # Based on the PDF documentation order
            stats = {
                'sum': float(values[0]) if len(values) > 0 else 0.0,
                'peaks': float(values[1]) if len(values) > 1 else 0.0,
                'max': float(values[2]) if len(values) > 2 else 0.0,
                'min': float(values[3]) if len(values) > 3 else 0.0,
                'pk_pk': float(values[4]) if len(values) > 4 else 0.0,
                'mean': float(values[5]) if len(values) > 5 else 0.0,
                'median': float(values[6]) if len(values) > 6 else 0.0,
                'mode': float(values[7]) if len(values) > 7 else 0.0,
                'bin_width': float(values[8]) if len(values) > 8 else 0.0,
                'sigma': float(values[9]) if len(values) > 9 else 0.0,
                'xscale': float(values[10]) if len(values) > 10 else 0.0
            }

            print(f"Histogram statistics: Mean={stats['mean']:.6f}, Sigma={stats['sigma']:.6f}, "
                  f"Pk-Pk={stats['pk_pk']:.6f}")

            return stats
        except pyvisa.VisaIOError as e:
            print(f"Failed to query histogram statistics: {e}")
            raise

    # ===================================================================
    # PHASE 4.6: BUILT-IN AWG/SOURCE COMMANDS
    # Reference PDFs: pdf_chapters/3.25*.pdf
    # ===================================================================

    # --- Basic AWG Control ---

    def awg_set_output_enable(self, enable: bool) -> None:
        """
        Enable or disable the AWG output.

        Reference: pdf_chapters/3.25.1_SOURce_OUTPut_STATe.pdf

        Args:
            enable: True to enable output, False to disable

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            scope.awg_set_output_enable(True)  # Enable AWG output
        """
        try:
            state = 'ON' if enable else 'OFF'
            self.instrument.write(f":SOURce:OUTPut:STATe {state}")
            print(f"AWG output {'enabled' if enable else 'disabled'}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set AWG output state: {e}")
            raise

    def awg_get_output_enable(self) -> bool:
        """
        Query the AWG output enable state.

        Reference: pdf_chapters/3.25.1_SOURce_OUTPut_STATe.pdf

        Returns:
            True if output is enabled, False if disabled

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            enabled = scope.awg_get_output_enable()
        """
        try:
            response = self.instrument.query(":SOURce:OUTPut:STATe?")
            enabled = response.strip() == '1'
            print(f"AWG output enable: {enabled}")
            return enabled
        except pyvisa.VisaIOError as e:
            print(f"Failed to query AWG output state: {e}")
            raise

    def awg_set_function(self, function: str) -> None:
        """
        Set the AWG waveform function type.

        Reference: pdf_chapters/3.25.2_SOURce_FUNCtion.pdf

        Args:
            function: Waveform type - 'SINusoid', 'SQUare', 'RAMP', 'DC', 'NOISe', or 'ARB'

        Raises:
            ValueError: If function type is invalid
            pyvisa.VisaIOError: If communication fails

        Example:
            scope.awg_set_function('SINusoid')  # Sine wave
            scope.awg_set_function('SQUare')    # Square wave
        """
        valid_functions = ['SINusoid', 'SQUare', 'RAMP', 'DC', 'NOISe', 'ARB']
        if function not in valid_functions:
            raise ValueError(f"Function must be one of {valid_functions}, got '{function}'")

        try:
            self.instrument.write(f":SOURce:FUNCtion {function}")
            print(f"AWG function set to {function}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set AWG function: {e}")
            raise

    def awg_get_function(self) -> str:
        """
        Query the AWG waveform function type.

        Reference: pdf_chapters/3.25.2_SOURce_FUNCtion.pdf

        Returns:
            Waveform type - 'SIN', 'SQU', 'RAMP', 'DC', 'NOIS', or 'ARB'

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            function = scope.awg_get_function()
        """
        try:
            response = self.instrument.query(":SOURce:FUNCtion?")
            function = response.strip()
            print(f"AWG function: {function}")
            return function
        except pyvisa.VisaIOError as e:
            print(f"Failed to query AWG function: {e}")
            raise

    def awg_set_frequency(self, frequency: float) -> None:
        """
        Set the AWG output frequency.

        Reference: pdf_chapters/3.25.3_SOURce_FREQuency.pdf

        Args:
            frequency: Frequency in Hz

        Note:
            Frequency affects the valid amplitude range:
            - Frequency ≤ 10 MHz: Amplitude range is 2 mV to 10 V
            - Frequency > 10 MHz: Amplitude range is 2 mV to 5 V

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            scope.awg_set_frequency(1000)  # 1 kHz
        """
        try:
            self.instrument.write(f":SOURce:FREQuency {frequency}")
            print(f"AWG frequency set to {frequency} Hz")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set AWG frequency: {e}")
            raise

    def awg_get_frequency(self) -> float:
        """
        Query the AWG output frequency.

        Reference: pdf_chapters/3.25.3_SOURce_FREQuency.pdf

        Returns:
            Frequency in Hz

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            freq = scope.awg_get_frequency()
        """
        try:
            response = self.instrument.query(":SOURce:FREQuency?")
            frequency = float(response.strip())
            print(f"AWG frequency: {frequency} Hz")
            return frequency
        except pyvisa.VisaIOError as e:
            print(f"Failed to query AWG frequency: {e}")
            raise

    def awg_set_amplitude(self, amplitude: float) -> None:
        """
        Set the AWG output amplitude (peak-to-peak voltage).

        Reference: pdf_chapters/3.25.7_SOURce_VOLTage_AMPLitude.pdf

        Args:
            amplitude: Amplitude in volts (Vpp)

        Amplitude Range (frequency-dependent):
            - 2 mV to 10 V when frequency ≤ 10 MHz
            - 2 mV to 5 V when frequency > 10 MHz

        Default: 6 V

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            scope.awg_set_amplitude(1.0)  # 1 Vpp
        """
        try:
            self.instrument.write(f":SOURce:VOLTage:AMPLitude {amplitude}")
            print(f"AWG amplitude set to {amplitude} V")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set AWG amplitude: {e}")
            raise

    def awg_get_amplitude(self) -> float:
        """
        Query the AWG output amplitude.

        Reference: pdf_chapters/3.25.7_SOURce_VOLTage_AMPLitude.pdf

        Returns:
            Amplitude in volts (Vpp)

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            amp = scope.awg_get_amplitude()
        """
        try:
            response = self.instrument.query(":SOURce:VOLTage:AMPLitude?")
            amplitude = float(response.strip())
            print(f"AWG amplitude: {amplitude} V")
            return amplitude
        except pyvisa.VisaIOError as e:
            print(f"Failed to query AWG amplitude: {e}")
            raise

    def awg_set_offset(self, offset: float) -> None:
        """
        Set the AWG DC offset voltage.

        Reference: pdf_chapters/3.25.8_SOURce_VOLTage_OFFSet.pdf

        Args:
            offset: DC offset in volts

        Offset Range (amplitude-dependent):
            Offset range = ± (maximum amplitude - current amplitude) / 2

            Examples:
            - At 5 MHz with 6 V amplitude (max 10 V): ±(10-6)/2 = ±2 V
            - At 15 MHz with 3 V amplitude (max 5 V): ±(5-3)/2 = ±1 V

        Default: 0 V

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            scope.awg_set_offset(0.5)  # +0.5 V DC offset
        """
        try:
            self.instrument.write(f":SOURce:VOLTage:OFFSet {offset}")
            print(f"AWG offset set to {offset} V")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set AWG offset: {e}")
            raise

    def awg_get_offset(self) -> float:
        """
        Query the AWG DC offset voltage.

        Reference: pdf_chapters/3.25.8_SOURce_VOLTage_OFFSet.pdf

        Returns:
            DC offset in volts

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            offset = scope.awg_get_offset()
        """
        try:
            response = self.instrument.query(":SOURce:VOLTage:OFFSet?")
            offset = float(response.strip())
            print(f"AWG offset: {offset} V")
            return offset
        except pyvisa.VisaIOError as e:
            print(f"Failed to query AWG offset: {e}")
            raise

    # --- Waveform Shape Control ---

    def awg_set_phase(self, phase: float) -> None:
        """
        Set the starting phase of the AWG waveform.

        Reference: pdf_chapters/3.25.4_SOURce_PHASe.pdf

        Args:
            phase: Starting phase in degrees (0° to 360°)

        Default: 0°

        Applies to: All basic waveforms (Sine, Square, Ramp, Arb)

        Raises:
            ValueError: If phase is out of range
            pyvisa.VisaIOError: If communication fails

        Example:
            scope.awg_set_phase(90)  # 90° phase shift
        """
        if not 0 <= phase <= 360:
            raise ValueError(f"Phase must be 0-360 degrees, got {phase}")

        try:
            self.instrument.write(f":SOURce:PHASe {phase}")
            print(f"AWG phase set to {phase}°")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set AWG phase: {e}")
            raise

    def awg_get_phase(self) -> float:
        """
        Query the starting phase of the AWG waveform.

        Reference: pdf_chapters/3.25.4_SOURce_PHASe.pdf

        Returns:
            Starting phase in degrees

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            phase = scope.awg_get_phase()
        """
        try:
            response = self.instrument.query(":SOURce:PHASe?")
            phase = float(response.strip())
            print(f"AWG phase: {phase}°")
            return phase
        except pyvisa.VisaIOError as e:
            print(f"Failed to query AWG phase: {e}")
            raise

    def awg_set_ramp_symmetry(self, symmetry: float) -> None:
        """
        Set the symmetry of the ramp waveform.

        Reference: pdf_chapters/3.25.5_SOURce_FUNCtion_RAMP_SYMMetry.pdf

        Args:
            symmetry: Symmetry percentage (0% to 100%)
                     Symmetry = (rise time / period) × 100%

        Default: 50%

        Note: Only applies when waveform function is set to RAMP

        Raises:
            ValueError: If symmetry is out of range
            pyvisa.VisaIOError: If communication fails

        Example:
            scope.awg_set_function('RAMP')
            scope.awg_set_ramp_symmetry(25)  # 25% rise, 75% fall
        """
        if not 0 <= symmetry <= 100:
            raise ValueError(f"Symmetry must be 0-100%, got {symmetry}")

        try:
            self.instrument.write(f":SOURce:FUNCtion:RAMP:SYMMetry {symmetry}")
            print(f"AWG ramp symmetry set to {symmetry}%")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set AWG ramp symmetry: {e}")
            raise

    def awg_get_ramp_symmetry(self) -> float:
        """
        Query the symmetry of the ramp waveform.

        Reference: pdf_chapters/3.25.5_SOURce_FUNCtion_RAMP_SYMMetry.pdf

        Returns:
            Symmetry percentage (0% to 100%)

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            symmetry = scope.awg_get_ramp_symmetry()
        """
        try:
            response = self.instrument.query(":SOURce:FUNCtion:RAMP:SYMMetry?")
            symmetry = float(response.strip())
            print(f"AWG ramp symmetry: {symmetry}%")
            return symmetry
        except pyvisa.VisaIOError as e:
            print(f"Failed to query AWG ramp symmetry: {e}")
            raise

    def awg_set_square_duty(self, duty: float) -> None:
        """
        Set the duty cycle of the square waveform.

        Reference: pdf_chapters/3.25.6_SOURce_FUNCtion_SQUare_DUTY.pdf

        Args:
            duty: Duty cycle percentage (0 to 100)
                  Duty cycle = (high time / period) × 100%

        Default: 50

        Note: Only applies when waveform function is set to SQUare

        Raises:
            ValueError: If duty cycle is out of range
            pyvisa.VisaIOError: If communication fails

        Example:
            scope.awg_set_function('SQUare')
            scope.awg_set_square_duty(25)  # 25% high, 75% low
        """
        if not 0 <= duty <= 100:
            raise ValueError(f"Duty cycle must be 0-100%, got {duty}")

        try:
            self.instrument.write(f":SOURce:FUNCtion:SQUare:DUTY {duty}")
            print(f"AWG square duty cycle set to {duty}%")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set AWG square duty cycle: {e}")
            raise

    def awg_get_square_duty(self) -> float:
        """
        Query the duty cycle of the square waveform.

        Reference: pdf_chapters/3.25.6_SOURce_FUNCtion_SQUare_DUTY.pdf

        Returns:
            Duty cycle percentage (0 to 100)

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            duty = scope.awg_get_square_duty()
        """
        try:
            response = self.instrument.query(":SOURce:FUNCtion:SQUare:DUTY?")
            duty = float(response.strip())
            print(f"AWG square duty cycle: {duty}%")
            return duty
        except pyvisa.VisaIOError as e:
            print(f"Failed to query AWG square duty cycle: {e}")
            raise

    # --- Modulation Control ---

    def awg_set_modulation_enable(self, enable: bool) -> None:
        """
        Enable or disable AWG modulation.

        Reference: pdf_chapters/3.25.9_SOURce_MOD_STATe.pdf

        Args:
            enable: True to enable modulation, False to disable

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            scope.awg_set_modulation_enable(True)
        """
        try:
            state = 'ON' if enable else 'OFF'
            self.instrument.write(f":SOURce:MOD:STATe {state}")
            print(f"AWG modulation {'enabled' if enable else 'disabled'}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set AWG modulation state: {e}")
            raise

    def awg_get_modulation_enable(self) -> bool:
        """
        Query the AWG modulation enable state.

        Reference: pdf_chapters/3.25.9_SOURce_MOD_STATe.pdf

        Returns:
            True if modulation is enabled, False if disabled

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            enabled = scope.awg_get_modulation_enable()
        """
        try:
            response = self.instrument.query(":SOURce:MOD:STATe?")
            enabled = response.strip() == '1'
            print(f"AWG modulation enable: {enabled}")
            return enabled
        except pyvisa.VisaIOError as e:
            print(f"Failed to query AWG modulation state: {e}")
            raise

    def awg_set_modulation_type(self, mod_type: str) -> None:
        """
        Set the AWG modulation type.

        Reference: pdf_chapters/3.25.10_SOURce_MOD_TYPe.pdf

        Args:
            mod_type: Modulation type - 'AM', 'FM', or 'PM'
                     AM = Amplitude Modulation
                     FM = Frequency Modulation
                     PM = Phase Modulation

        Default: 'AM'

        Raises:
            ValueError: If modulation type is invalid
            pyvisa.VisaIOError: If communication fails

        Example:
            scope.awg_set_modulation_type('AM')  # Amplitude modulation
        """
        valid_types = ['AM', 'FM', 'PM']
        if mod_type not in valid_types:
            raise ValueError(f"Modulation type must be one of {valid_types}, got '{mod_type}'")

        try:
            self.instrument.write(f":SOURce:MOD:TYPe {mod_type}")
            print(f"AWG modulation type set to {mod_type}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set AWG modulation type: {e}")
            raise

    def awg_get_modulation_type(self) -> str:
        """
        Query the AWG modulation type.

        Reference: pdf_chapters/3.25.10_SOURce_MOD_TYPe.pdf

        Returns:
            Modulation type - 'AM', 'FM', or 'PM'

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            mod_type = scope.awg_get_modulation_type()
        """
        try:
            response = self.instrument.query(":SOURce:MOD:TYPe?")
            mod_type = response.strip()
            print(f"AWG modulation type: {mod_type}")
            return mod_type
        except pyvisa.VisaIOError as e:
            print(f"Failed to query AWG modulation type: {e}")
            raise

    # --- AM Modulation ---

    def awg_set_am_depth(self, depth: float) -> None:
        """
        Set the AM (Amplitude Modulation) depth.

        Reference: pdf_chapters/3.25.11_SOURce_MOD_AM_DEPTh.pdf

        Args:
            depth: Modulation depth percentage (0% to 120%)
                  0% = amplitude is half of carrier
                  100% = amplitude equals carrier
                  >100% = envelope distortion

        Default: 100%

        Raises:
            ValueError: If depth is out of range
            pyvisa.VisaIOError: If communication fails

        Example:
            scope.awg_set_am_depth(80)  # 80% modulation depth
        """
        if not 0 <= depth <= 120:
            raise ValueError(f"AM depth must be 0-120%, got {depth}")

        try:
            self.instrument.write(f":SOURce:MOD:AM:DEPTh {depth}")
            print(f"AWG AM depth set to {depth}%")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set AWG AM depth: {e}")
            raise

    def awg_get_am_depth(self) -> float:
        """
        Query the AM modulation depth.

        Reference: pdf_chapters/3.25.11_SOURce_MOD_AM_DEPTh.pdf

        Returns:
            Modulation depth percentage

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            depth = scope.awg_get_am_depth()
        """
        try:
            response = self.instrument.query(":SOURce:MOD:AM:DEPTh?")
            depth = float(response.strip())
            print(f"AWG AM depth: {depth}%")
            return depth
        except pyvisa.VisaIOError as e:
            print(f"Failed to query AWG AM depth: {e}")
            raise

    def awg_set_am_frequency(self, frequency: float) -> None:
        """
        Set the AM modulation frequency.

        Reference: pdf_chapters/3.25.12_SOURce_MOD_AM_INTernal_FREQuency.pdf

        Args:
            frequency: Modulation frequency in Hz (2 mHz to 1 MHz)

        Default: 100 Hz

        Raises:
            ValueError: If frequency is out of range
            pyvisa.VisaIOError: If communication fails

        Example:
            scope.awg_set_am_frequency(1000)  # 1 kHz modulation
        """
        if not 0.002 <= frequency <= 1e6:
            raise ValueError(f"AM frequency must be 2 mHz to 1 MHz, got {frequency}")

        try:
            self.instrument.write(f":SOURce:MOD:AM:INTernal:FREQuency {frequency}")
            print(f"AWG AM frequency set to {frequency} Hz")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set AWG AM frequency: {e}")
            raise

    def awg_get_am_frequency(self) -> float:
        """
        Query the AM modulation frequency.

        Reference: pdf_chapters/3.25.12_SOURce_MOD_AM_INTernal_FREQuency.pdf

        Returns:
            Modulation frequency in Hz

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            freq = scope.awg_get_am_frequency()
        """
        try:
            response = self.instrument.query(":SOURce:MOD:AM:INTernal:FREQuency?")
            frequency = float(response.strip())
            print(f"AWG AM frequency: {frequency} Hz")
            return frequency
        except pyvisa.VisaIOError as e:
            print(f"Failed to query AWG AM frequency: {e}")
            raise

    def awg_set_am_function(self, function: str) -> None:
        """
        Set the AM modulation waveform type.

        Reference: pdf_chapters/3.25.13_SOURce_MOD_AM_INTernal_FUNCtion.pdf

        Args:
            function: Modulation waveform - 'SINusoid', 'SQUare', 'TRIangle',
                     'UPRamp', 'DNRamp', or 'NOISe'

        Default: 'SINusoid'

        Raises:
            ValueError: If function is invalid
            pyvisa.VisaIOError: If communication fails

        Example:
            scope.awg_set_am_function('SQUare')
        """
        valid_functions = ['SINusoid', 'SQUare', 'TRIangle', 'UPRamp', 'DNRamp', 'NOISe']
        if function not in valid_functions:
            raise ValueError(f"AM function must be one of {valid_functions}, got '{function}'")

        try:
            self.instrument.write(f":SOURce:MOD:AM:INTernal:FUNCtion {function}")
            print(f"AWG AM function set to {function}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set AWG AM function: {e}")
            raise

    def awg_get_am_function(self) -> str:
        """
        Query the AM modulation waveform type.

        Reference: pdf_chapters/3.25.13_SOURce_MOD_AM_INTernal_FUNCtion.pdf

        Returns:
            Modulation waveform - 'SIN', 'SQU', 'TRI', 'UPR', 'DNR', or 'NOIS'

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            function = scope.awg_get_am_function()
        """
        try:
            response = self.instrument.query(":SOURce:MOD:AM:INTernal:FUNCtion?")
            function = response.strip()
            print(f"AWG AM function: {function}")
            return function
        except pyvisa.VisaIOError as e:
            print(f"Failed to query AWG AM function: {e}")
            raise

    # --- FM Modulation ---

    def awg_set_fm_deviation(self, deviation: float) -> None:
        """
        Set the FM (Frequency Modulation) frequency deviation.

        Reference: pdf_chapters/3.25.14_SOURce_MOD_FM_DEViation.pdf

        Args:
            deviation: Frequency deviation in Hz (2 mHz to carrier frequency)
                      Peak variation in frequency from carrier

        Default: 1 kHz

        Raises:
            ValueError: If deviation is negative
            pyvisa.VisaIOError: If communication fails

        Example:
            scope.awg_set_fm_deviation(5000)  # ±5 kHz deviation
        """
        if deviation < 0.002:
            raise ValueError(f"FM deviation must be ≥ 2 mHz, got {deviation}")

        try:
            self.instrument.write(f":SOURce:MOD:FM:DEViation {deviation}")
            print(f"AWG FM deviation set to {deviation} Hz")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set AWG FM deviation: {e}")
            raise

    def awg_get_fm_deviation(self) -> float:
        """
        Query the FM frequency deviation.

        Reference: pdf_chapters/3.25.14_SOURce_MOD_FM_DEViation.pdf

        Returns:
            Frequency deviation in Hz

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            deviation = scope.awg_get_fm_deviation()
        """
        try:
            response = self.instrument.query(":SOURce:MOD:FM:DEViation?")
            deviation = float(response.strip())
            print(f"AWG FM deviation: {deviation} Hz")
            return deviation
        except pyvisa.VisaIOError as e:
            print(f"Failed to query AWG FM deviation: {e}")
            raise

    def awg_set_fm_frequency(self, frequency: float) -> None:
        """
        Set the FM modulation frequency.

        Reference: pdf_chapters/3.25.15_SOURce_MOD_FM_INTernal_FREQuency.pdf

        Args:
            frequency: Modulation frequency in Hz (2 mHz to 1 MHz)

        Default: 100 Hz

        Raises:
            ValueError: If frequency is out of range
            pyvisa.VisaIOError: If communication fails

        Example:
            scope.awg_set_fm_frequency(500)  # 500 Hz modulation
        """
        if not 0.002 <= frequency <= 1e6:
            raise ValueError(f"FM frequency must be 2 mHz to 1 MHz, got {frequency}")

        try:
            self.instrument.write(f":SOURce:MOD:FM:INTernal:FREQuency {frequency}")
            print(f"AWG FM frequency set to {frequency} Hz")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set AWG FM frequency: {e}")
            raise

    def awg_get_fm_frequency(self) -> float:
        """
        Query the FM modulation frequency.

        Reference: pdf_chapters/3.25.15_SOURce_MOD_FM_INTernal_FREQuency.pdf

        Returns:
            Modulation frequency in Hz

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            freq = scope.awg_get_fm_frequency()
        """
        try:
            response = self.instrument.query(":SOURce:MOD:FM:INTernal:FREQuency?")
            frequency = float(response.strip())
            print(f"AWG FM frequency: {frequency} Hz")
            return frequency
        except pyvisa.VisaIOError as e:
            print(f"Failed to query AWG FM frequency: {e}")
            raise

    def awg_set_fm_function(self, function: str) -> None:
        """
        Set the FM modulation waveform type.

        Reference: pdf_chapters/3.25.16_SOURce_MOD_FM_INTernal_FUNCtion.pdf

        Args:
            function: Modulation waveform - 'SINusoid', 'SQUare', 'TRIangle',
                     'UPRamp', 'DNRamp', or 'NOISe'

        Default: 'SINusoid'

        Raises:
            ValueError: If function is invalid
            pyvisa.VisaIOError: If communication fails

        Example:
            scope.awg_set_fm_function('TRIangle')
        """
        valid_functions = ['SINusoid', 'SQUare', 'TRIangle', 'UPRamp', 'DNRamp', 'NOISe']
        if function not in valid_functions:
            raise ValueError(f"FM function must be one of {valid_functions}, got '{function}'")

        try:
            self.instrument.write(f":SOURce:MOD:FM:INTernal:FUNCtion {function}")
            print(f"AWG FM function set to {function}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set AWG FM function: {e}")
            raise

    def awg_get_fm_function(self) -> str:
        """
        Query the FM modulation waveform type.

        Reference: pdf_chapters/3.25.16_SOURce_MOD_FM_INTernal_FUNCtion.pdf

        Returns:
            Modulation waveform - 'SIN', 'SQU', 'TRI', 'UPR', 'DNR', or 'NOIS'

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            function = scope.awg_get_fm_function()
        """
        try:
            response = self.instrument.query(":SOURce:MOD:FM:INTernal:FUNCtion?")
            function = response.strip()
            print(f"AWG FM function: {function}")
            return function
        except pyvisa.VisaIOError as e:
            print(f"Failed to query AWG FM function: {e}")
            raise

    # --- PM Modulation ---

    def awg_set_pm_deviation(self, deviation: float) -> None:
        """
        Set the PM (Phase Modulation) phase deviation.

        Reference: pdf_chapters/3.25.17_SOURce_MOD_PM_DEViation.pdf

        Args:
            deviation: Phase deviation in degrees (0° to 360°)
                      Peak variation in phase from carrier

        Default: 90°

        Raises:
            ValueError: If deviation is out of range
            pyvisa.VisaIOError: If communication fails

        Example:
            scope.awg_set_pm_deviation(180)  # ±180° deviation
        """
        if not 0 <= deviation <= 360:
            raise ValueError(f"PM deviation must be 0-360°, got {deviation}")

        try:
            self.instrument.write(f":SOURce:MOD:PM:DEViation {deviation}")
            print(f"AWG PM deviation set to {deviation}°")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set AWG PM deviation: {e}")
            raise

    def awg_get_pm_deviation(self) -> float:
        """
        Query the PM phase deviation.

        Reference: pdf_chapters/3.25.17_SOURce_MOD_PM_DEViation.pdf

        Returns:
            Phase deviation in degrees

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            deviation = scope.awg_get_pm_deviation()
        """
        try:
            response = self.instrument.query(":SOURce:MOD:PM:DEViation?")
            deviation = float(response.strip())
            print(f"AWG PM deviation: {deviation}°")
            return deviation
        except pyvisa.VisaIOError as e:
            print(f"Failed to query AWG PM deviation: {e}")
            raise

    def awg_set_pm_frequency(self, frequency: float) -> None:
        """
        Set the PM modulation frequency.

        Reference: pdf_chapters/3.25.18_SOURce_MOD_PM_INTernal_FREQuency.pdf

        Args:
            frequency: Modulation frequency in Hz (2 mHz to 1 MHz)

        Default: 100 Hz

        Raises:
            ValueError: If frequency is out of range
            pyvisa.VisaIOError: If communication fails

        Example:
            scope.awg_set_pm_frequency(250)  # 250 Hz modulation
        """
        if not 0.002 <= frequency <= 1e6:
            raise ValueError(f"PM frequency must be 2 mHz to 1 MHz, got {frequency}")

        try:
            self.instrument.write(f":SOURce:MOD:PM:INTernal:FREQuency {frequency}")
            print(f"AWG PM frequency set to {frequency} Hz")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set AWG PM frequency: {e}")
            raise

    def awg_get_pm_frequency(self) -> float:
        """
        Query the PM modulation frequency.

        Reference: pdf_chapters/3.25.18_SOURce_MOD_PM_INTernal_FREQuency.pdf

        Returns:
            Modulation frequency in Hz

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            freq = scope.awg_get_pm_frequency()
        """
        try:
            response = self.instrument.query(":SOURce:MOD:PM:INTernal:FREQuency?")
            frequency = float(response.strip())
            print(f"AWG PM frequency: {frequency} Hz")
            return frequency
        except pyvisa.VisaIOError as e:
            print(f"Failed to query AWG PM frequency: {e}")
            raise

    def awg_set_pm_function(self, function: str) -> None:
        """
        Set the PM modulation waveform type.

        Reference: pdf_chapters/3.25.19_SOURce_MOD_PM_INTernal_FUNCtion.pdf

        Args:
            function: Modulation waveform - 'SINusoid', 'SQUare', 'TRIangle',
                     'UPRamp', 'DNRamp', or 'NOISe'

        Default: 'SINusoid'

        Raises:
            ValueError: If function is invalid
            pyvisa.VisaIOError: If communication fails

        Example:
            scope.awg_set_pm_function('SQUare')
        """
        valid_functions = ['SINusoid', 'SQUare', 'TRIangle', 'UPRamp', 'DNRamp', 'NOISe']
        if function not in valid_functions:
            raise ValueError(f"PM function must be one of {valid_functions}, got '{function}'")

        try:
            self.instrument.write(f":SOURce:MOD:PM:INTernal:FUNCtion {function}")
            print(f"AWG PM function set to {function}")
        except pyvisa.VisaIOError as e:
            print(f"Failed to set AWG PM function: {e}")
            raise

    def awg_get_pm_function(self) -> str:
        """
        Query the PM modulation waveform type.

        Reference: pdf_chapters/3.25.19_SOURce_MOD_PM_INTernal_FUNCtion.pdf

        Returns:
            Modulation waveform - 'SIN', 'SQU', 'TRI', 'UPR', 'DNR', or 'NOIS'

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            function = scope.awg_get_pm_function()
        """
        try:
            response = self.instrument.query(":SOURce:MOD:PM:INTernal:FUNCtion?")
            function = response.strip()
            print(f"AWG PM function: {function}")
            return function
        except pyvisa.VisaIOError as e:
            print(f"Failed to query AWG PM function: {e}")
            raise

    # --- High-Level AWG Helper Method ---

    def awg_configure_simple(self, function: str, frequency: float,
                            amplitude: float, offset: float = 0.0,
                            enable: bool = True) -> None:
        """
        High-level method to quickly configure and enable the AWG.

        This is a convenience method that sets up basic AWG parameters in one call.

        Args:
            function: Waveform type - 'SINusoid', 'SQUare', 'RAMP', 'DC', 'NOISe'
            frequency: Output frequency in Hz
            amplitude: Output amplitude in volts (Vpp)
            offset: DC offset in volts (default: 0.0)
            enable: Enable output after configuration (default: True)

        Raises:
            pyvisa.VisaIOError: If communication fails

        Example:
            # Configure 1 kHz sine wave, 2 Vpp, no offset
            scope.awg_configure_simple('SINusoid', 1000, 2.0)

            # Configure 10 kHz square wave, 5 Vpp, +1V offset
            scope.awg_configure_simple('SQUare', 10000, 5.0, offset=1.0)
        """
        try:
            print(f"Configuring AWG: {function}, {frequency} Hz, {amplitude} Vpp, {offset} V offset")

            # Disable output first for safety
            self.awg_set_output_enable(False)

            # Configure waveform parameters
            self.awg_set_function(function)
            self.awg_set_frequency(frequency)
            self.awg_set_amplitude(amplitude)
            self.awg_set_offset(offset)

            # Enable output if requested
            if enable:
                self.awg_set_output_enable(True)

            print(f"AWG configured successfully")
        except Exception as e:
            print(f"Failed to configure AWG: {e}")
            raise
