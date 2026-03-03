"""
Driver for the Keysight EDU33212A Trueform Arbitrary Waveform Generator.
Instrument Type: Dual-Channel Arbitrary Waveform Generator (AWG)

Based on Keysight EDU33210 Series User's Guide, Edition 4, July 2025.
Part Number: EDU33212-90002

IDN response: Keysight Technologies,EDU33212A,<serial>,<firmware>
Interface: USB-B (USB-TMC) or LAN
"""

from .device_manager import DeviceManager


class Keysight_EDU33212A(DeviceManager):
    """
    Driver for Keysight EDU33212A Dual-Channel Trueform Arbitrary Waveform Generator.

    Channels are addressed via SOURce1/SOURce2 SCPI prefix.
    Output enable/disable uses OUTPut1/OUTPut2 (no SOURce prefix).
    Both channels default to OFF at power-on.
    """

    CHANNEL_MAP = {1: "SOURce1", 2: "SOURce2"}

    VALID_WAVEFORMS = {"SIN", "SQU", "RAMP", "PULS", "NOIS", "PRBS", "DC", "ARB"}

    VALID_MOD_FUNCS = {"SIN", "SQU", "TRI", "UPRAMP", "DNRAMP", "NOIS", "PRBS", "ARB"}

    def __init__(self, resource_name):
        """Initialize the Keysight EDU33212A AWG."""
        super().__init__(resource_name)

    def __enter__(self):
        """Context manager entry: clear status and disable all outputs."""
        self.clear_status()
        self.disable_all_channels()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Context manager exit: disable all outputs for safety."""
        self.disable_all_channels()

    # ==========================================
    # INTERNAL HELPERS
    # ==========================================

    def _validate_channel(self, channel):
        if channel not in self.CHANNEL_MAP:
            raise ValueError(
                f"Invalid channel {channel}. Must be one of: {list(self.CHANNEL_MAP.keys())}"
            )

    def _src(self, channel):
        """Return the SOURce prefix for the given channel number."""
        return self.CHANNEL_MAP[channel]

    # ==========================================
    # OUTPUT CONTROL
    # ==========================================

    def enable_output(self, channel, enabled: bool = True):
        """Enable or disable the output for the specified channel.

        Args:
            channel (int): Channel number (1 or 2).
            enabled (bool): True to enable, False to disable.
        """
        self._validate_channel(channel)
        state = "ON" if enabled else "OFF"
        self.send_command(f"OUTPut{channel} {state}")

    def disable_all_channels(self):
        """Zeroes SINE memory (0V amp/offset), switches to DC 0V, then disables output."""
        for channel in self.CHANNEL_MAP:
            # Zero stored SINE parameters so they are safe if the user switches back
            self.set_function(channel, 'SIN')
            self.set_amplitude(channel, 0.0)
            self.set_offset(channel, 0.0)
            # Then switch to DC at 0V and disable
            self.set_dc_output(channel, 0.0)
            self.enable_output(channel, False)

    def set_output_load(self, channel, load):
        """Set the output load impedance.

        Args:
            channel (int): Channel number (1 or 2).
            load (int|float|str): Load in Ohms (1-10000) or 'INF' for high-Z.
        """
        self._validate_channel(channel)
        if isinstance(load, str) and load.upper() in ("INF", "INFINITY", "INFinity"):
            load_str = "INFinity"
        else:
            load_str = str(load)
        self.send_command(f"OUTPut{channel}:LOAD {load_str}")

    def set_output_polarity(self, channel, normal: bool = True):
        """Set output polarity.

        Args:
            channel (int): Channel number (1 or 2).
            normal (bool): True for normal, False for inverted.
        """
        self._validate_channel(channel)
        polarity = "NORMal" if normal else "INVerted"
        self.send_command(f"OUTPut{channel}:POLarity {polarity}")

    def set_sync_output(self, enabled: bool = True):
        """Enable or disable the Sync output signal."""
        state = "ON" if enabled else "OFF"
        self.send_command(f"OUTPut:SYNC {state}")

    def get_amplitude(self, channel):
        """Query the current amplitude (Vpp) for the specified channel."""
        self._validate_channel(channel)
        return float(self.query(f"{self._src(channel)}:VOLTage?"))

    def get_offset(self, channel):
        """Query the current DC offset for the specified channel."""
        self._validate_channel(channel)
        return float(self.query(f"{self._src(channel)}:VOLTage:OFFSet?"))

    def get_frequency(self, channel):
        """Query the current frequency (Hz) for the specified channel."""
        self._validate_channel(channel)
        return float(self.query(f"{self._src(channel)}:FREQuency?"))

    def get_output_state(self, channel):
        """Query whether the output is enabled for the specified channel."""
        self._validate_channel(channel)
        resp = self.query(f"OUTPut{channel}?").strip()
        return resp in ("1", "ON")

    # ==========================================
    # WAVEFORM CONFIGURATION
    # ==========================================

    def set_function(self, channel, func):
        """Set the output waveform function.

        Args:
            channel (int): Channel number (1 or 2).
            func (str): One of SIN, SQU, RAMP, PULS, NOIS, PRBS, DC, ARB.
        """
        self._validate_channel(channel)
        f = func.upper()
        if f not in self.VALID_WAVEFORMS:
            raise ValueError(f"Invalid function '{func}'. Must be one of: {self.VALID_WAVEFORMS}")
        self.send_command(f"{self._src(channel)}:FUNCtion {f}")

    def set_frequency(self, channel, frequency):
        """Set the output frequency.

        Args:
            channel (int): Channel number (1 or 2).
            frequency (float): Frequency in Hz (1 µHz to max for sine/square/ramp).
        """
        self._validate_channel(channel)
        self.send_command(f"{self._src(channel)}:FREQuency {frequency}")

    def set_amplitude(self, channel, amplitude):
        """Set the output amplitude in Vpp (default units).

        Args:
            channel (int): Channel number (1 or 2).
            amplitude (float): Amplitude in Vpp.
        """
        self._validate_channel(channel)
        self.send_command(f"{self._src(channel)}:VOLTage {amplitude}")

    def set_offset(self, channel, offset):
        """Set the DC offset voltage.

        Args:
            channel (int): Channel number (1 or 2).
            offset (float): Offset in Volts.
        """
        self._validate_channel(channel)
        self.send_command(f"{self._src(channel)}:VOLTage:OFFSet {offset}")

    def set_high_low(self, channel, high, low):
        """Set output using high and low voltage levels.

        Args:
            channel (int): Channel number (1 or 2).
            high (float): High voltage level in Volts.
            low (float): Low voltage level in Volts.
        """
        self._validate_channel(channel)
        self.send_command(f"{self._src(channel)}:VOLTage:HIGH {high}")
        self.send_command(f"{self._src(channel)}:VOLTage:LOW {low}")

    def set_voltage_unit(self, channel, unit):
        """Set the voltage unit for amplitude display.

        Args:
            channel (int): Channel number (1 or 2).
            unit (str): VPP, VRMS, or DBM.
        """
        self._validate_channel(channel)
        u = unit.upper()
        if u not in ("VPP", "VRMS", "DBM"):
            raise ValueError(f"Invalid voltage unit '{unit}'. Must be VPP, VRMS, or DBM.")
        self.send_command(f"{self._src(channel)}:VOLTage:UNIT {u}")

    # ==========================================
    # WAVEFORM SHAPE PARAMETERS
    # ==========================================

    def set_square_duty(self, channel, duty_cycle):
        """Set the duty cycle for a square wave.

        Args:
            channel (int): Channel number (1 or 2).
            duty_cycle (float): Duty cycle as a percentage (0.01 to 99.99).
        """
        self._validate_channel(channel)
        self.send_command(f"{self._src(channel)}:FUNCtion:SQUare:DCYCle {duty_cycle}")

    def set_ramp_symmetry(self, channel, symmetry):
        """Set the symmetry of a ramp waveform.

        Args:
            channel (int): Channel number (1 or 2).
            symmetry (float): Symmetry percentage (0 to 100). 100% = sawtooth up,
                              0% = sawtooth down, 50% = triangle.
        """
        self._validate_channel(channel)
        self.send_command(f"{self._src(channel)}:FUNCtion:RAMP:SYMMetry {symmetry}")

    # ==========================================
    # PULSE WAVEFORM PARAMETERS
    # ==========================================

    def set_pulse_period(self, channel, period):
        """Set the pulse period.

        Args:
            channel (int): Channel number (1 or 2).
            period (float): Period in seconds.
        """
        self._validate_channel(channel)
        self.send_command(f"{self._src(channel)}:FUNCtion:PULSe:PERiod {period}")

    def set_pulse_width(self, channel, width):
        """Set the pulse width.

        Args:
            channel (int): Channel number (1 or 2).
            width (float): Pulse width in seconds (minimum 16 ns).
        """
        self._validate_channel(channel)
        self.send_command(f"{self._src(channel)}:FUNCtion:PULSe:WIDTh {width}")

    def set_pulse_duty(self, channel, duty_cycle):
        """Set the pulse duty cycle.

        Args:
            channel (int): Channel number (1 or 2).
            duty_cycle (float): Duty cycle as a percentage (0.01 to 99.99).
        """
        self._validate_channel(channel)
        self.send_command(f"{self._src(channel)}:FUNCtion:PULSe:DCYCle {duty_cycle}")

    def set_pulse_edge(self, channel, leading=None, trailing=None):
        """Set the pulse edge transition times (10%-90%).

        Args:
            channel (int): Channel number (1 or 2).
            leading (float|None): Leading edge time in seconds (8.4 ns to 1 µs).
            trailing (float|None): Trailing edge time in seconds (8.4 ns to 1 µs).
        """
        self._validate_channel(channel)
        src = self._src(channel)
        if leading is not None:
            self.send_command(f"{src}:FUNCtion:PULSe:TRANsition:LEADing {leading}")
        if trailing is not None:
            self.send_command(f"{src}:FUNCtion:PULSe:TRANsition:TRAiling {trailing}")

    # ==========================================
    # CONVENIENCE METHOD (matches BK_4063 API)
    # ==========================================

    def set_waveform(
        self,
        channel,
        wave_type,
        frequency=None,
        amplitude=None,
        offset=None,
        duty=None,
        symmetry=None,
    ):
        """Set waveform type and parameters for the specified channel.

        Args:
            channel (int): Channel number (1 or 2).
            wave_type (str): Waveform type (SIN, SQU, RAMP, PULS, NOIS, PRBS, DC, ARB).
            frequency (float|None): Frequency in Hz.
            amplitude (float|None): Amplitude in Vpp.
            offset (float|None): DC offset in Volts.
            duty (float|None): Duty cycle in % (SQU and PULS only).
            symmetry (float|None): Symmetry in % (RAMP only).
        """
        self._validate_channel(channel)
        w = wave_type.upper()
        if w not in self.VALID_WAVEFORMS:
            raise ValueError(f"Invalid waveform '{wave_type}'. Must be one of: {self.VALID_WAVEFORMS}")

        self.set_function(channel, w)

        if frequency is not None and w not in ("NOIS", "DC"):
            self.set_frequency(channel, frequency)
        if amplitude is not None and w not in ("NOIS", "DC"):
            self.set_amplitude(channel, amplitude)
        if offset is not None:
            self.set_offset(channel, offset)
        if duty is not None and w == "SQU":
            self.set_square_duty(channel, duty)
        if duty is not None and w == "PULS":
            self.set_pulse_duty(channel, duty)
        if symmetry is not None and w == "RAMP":
            self.set_ramp_symmetry(channel, symmetry)

    def set_dc_output(self, channel, voltage):
        """Configure channel for DC output at a specified voltage.

        Args:
            channel (int): Channel number (1 or 2).
            voltage (float): DC voltage in Volts.
        """
        self.set_function(channel, "DC")
        self.set_offset(channel, voltage)

    # ==========================================
    # MODULATION
    # ==========================================

    def set_am(
        self,
        channel,
        state: bool,
        depth=100.0,
        mod_freq=10.0,
        mod_func="SIN",
        source="INTernal",
        dssc=False,
    ):
        """Configure Amplitude Modulation (AM).

        Args:
            channel (int): Channel number (1 or 2).
            state (bool): Enable or disable AM.
            depth (float): Modulation depth in % (0-120). Default 100%.
            mod_freq (float): Modulating frequency in Hz. Default 10 Hz.
            mod_func (str): Modulating waveform shape. Default SIN.
            source (str): INTernal, CH1, or CH2. Default INTernal.
            dssc (bool): Enable double-sideband suppressed carrier. Default False.
        """
        self._validate_channel(channel)
        src = self._src(channel)
        st = "ON" if state else "OFF"
        self.send_command(f"{src}:AM:STATe {st}")
        if state:
            self.send_command(f"{src}:AM:DEPTh {depth}")
            self.send_command(f"{src}:AM:INTernal:FUNCtion {mod_func.upper()}")
            self.send_command(f"{src}:AM:INTernal:FREQuency {mod_freq}")
            self.send_command(f"{src}:AM:SOURce {source}")
            dssc_st = "ON" if dssc else "OFF"
            self.send_command(f"{src}:AM:DSSC {dssc_st}")

    def set_fm(
        self,
        channel,
        state: bool,
        deviation=100.0,
        mod_freq=10.0,
        mod_func="SIN",
        source="INTernal",
    ):
        """Configure Frequency Modulation (FM).

        Args:
            channel (int): Channel number (1 or 2).
            state (bool): Enable or disable FM.
            deviation (float): Frequency deviation in Hz. Default 100 Hz.
            mod_freq (float): Modulating frequency in Hz. Default 10 Hz.
            mod_func (str): Modulating waveform shape. Default SIN.
            source (str): INTernal, CH1, or CH2. Default INTernal.
        """
        self._validate_channel(channel)
        src = self._src(channel)
        st = "ON" if state else "OFF"
        self.send_command(f"{src}:FM:STATe {st}")
        if state:
            self.send_command(f"{src}:FM:DEViation {deviation}")
            self.send_command(f"{src}:FM:INTernal:FUNCtion {mod_func.upper()}")
            self.send_command(f"{src}:FM:INTernal:FREQuency {mod_freq}")
            self.send_command(f"{src}:FM:SOURce {source}")

    def set_pm(
        self,
        channel,
        state: bool,
        deviation=180.0,
        mod_freq=10.0,
        mod_func="SIN",
        source="INTernal",
    ):
        """Configure Phase Modulation (PM).

        Args:
            channel (int): Channel number (1 or 2).
            state (bool): Enable or disable PM.
            deviation (float): Phase deviation in degrees (0-360). Default 180°.
            mod_freq (float): Modulating frequency in Hz. Default 10 Hz.
            mod_func (str): Modulating waveform shape. Default SIN.
            source (str): INTernal, CH1, or CH2. Default INTernal.
        """
        self._validate_channel(channel)
        src = self._src(channel)
        st = "ON" if state else "OFF"
        self.send_command(f"{src}:PM:STATe {st}")
        if state:
            self.send_command(f"{src}:PM:DEViation {deviation}")
            self.send_command(f"{src}:PM:INTernal:FUNCtion {mod_func.upper()}")
            self.send_command(f"{src}:PM:INTernal:FREQuency {mod_freq}")
            self.send_command(f"{src}:PM:SOURce {source}")

    def set_fsk(
        self,
        channel,
        state: bool,
        hop_freq=100.0,
        rate=10.0,
        source="INTernal",
    ):
        """Configure Frequency-Shift Keying (FSK) Modulation.

        Args:
            channel (int): Channel number (1 or 2).
            state (bool): Enable or disable FSK.
            hop_freq (float): Hop (alternate) frequency in Hz. Default 100 Hz.
            rate (float): FSK rate in Hz (internal only). Default 10 Hz.
            source (str): INTernal or EXTernal. Default INTernal.
        """
        self._validate_channel(channel)
        src = self._src(channel)
        st = "ON" if state else "OFF"
        self.send_command(f"{src}:FSKey:STATe {st}")
        if state:
            self.send_command(f"{src}:FSKey:FREQuency {hop_freq}")
            self.send_command(f"{src}:FSKey:SOURce {source}")
            if source.upper() == "INTERNAL":
                self.send_command(f"{src}:FSKey:INTernal:RATE {rate}")

    def set_pwm(
        self,
        channel,
        state: bool,
        deviation=None,
        mod_freq=10.0,
        mod_func="SIN",
        source="INTernal",
    ):
        """Configure Pulse Width Modulation (PWM). Carrier must be PULS.

        Args:
            channel (int): Channel number (1 or 2).
            state (bool): Enable or disable PWM.
            deviation (float|None): Width deviation in seconds. Default None (instrument default).
            mod_freq (float): Modulating frequency in Hz. Default 10 Hz.
            mod_func (str): Modulating waveform shape. Default SIN.
            source (str): INTernal, CH1, or CH2. Default INTernal.
        """
        self._validate_channel(channel)
        src = self._src(channel)
        st = "ON" if state else "OFF"
        self.send_command(f"{src}:PWM:STATe {st}")
        if state:
            if deviation is not None:
                self.send_command(f"{src}:PWM:DEViation {deviation}")
            self.send_command(f"{src}:PWM:INTernal:FUNCtion {mod_func.upper()}")
            self.send_command(f"{src}:PWM:INTernal:FREQuency {mod_freq}")
            self.send_command(f"{src}:PWM:SOURce {source}")

    # ==========================================
    # SWEEP
    # ==========================================

    def set_sweep(
        self,
        channel,
        state: bool,
        start=100.0,
        stop=1000.0,
        time=1.0,
        spacing="LINear",
        hold_time=0.0,
        return_time=0.0,
    ):
        """Configure frequency sweep.

        Args:
            channel (int): Channel number (1 or 2).
            state (bool): Enable or disable sweep.
            start (float): Start frequency in Hz. Default 100 Hz.
            stop (float): Stop frequency in Hz. Default 1 kHz.
            time (float): Sweep time in seconds. Default 1 s.
            spacing (str): LINear or LOGarithmic. Default LINear.
            hold_time (float): Hold time in seconds. Default 0.
            return_time (float): Return time in seconds. Default 0.
        """
        self._validate_channel(channel)
        src = self._src(channel)
        st = "ON" if state else "OFF"
        self.send_command(f"{src}:SWEep:STATe {st}")
        if state:
            self.send_command(f"{src}:FREQuency:STARt {start}")
            self.send_command(f"{src}:FREQuency:STOP {stop}")
            self.send_command(f"{src}:SWEep:TIME {time}")
            self.send_command(f"{src}:SWEep:SPACing {spacing}")
            self.send_command(f"{src}:SWEep:HTIMe {hold_time}")
            self.send_command(f"{src}:SWEep:RTIMe {return_time}")

    # ==========================================
    # BURST
    # ==========================================

    def set_burst(
        self,
        channel,
        state: bool,
        mode="TRIGgered",
        n_cycles=1,
        period=0.01,
        phase=0.0,
    ):
        """Configure burst mode.

        Args:
            channel (int): Channel number (1 or 2).
            state (bool): Enable or disable burst.
            mode (str): TRIGgered or GATed. Default TRIGgered.
            n_cycles (int): Number of cycles per burst (1 to 100,000,000). Default 1.
            period (float): Burst period in seconds (triggered internal only). Default 10 ms.
            phase (float): Start phase in degrees (-360 to +360). Default 0.
        """
        self._validate_channel(channel)
        src = self._src(channel)
        st = "ON" if state else "OFF"
        self.send_command(f"{src}:BURSt:STATe {st}")
        if state:
            self.send_command(f"{src}:BURSt:MODE {mode}")
            self.send_command(f"{src}:BURSt:NCYCles {n_cycles}")
            self.send_command(f"{src}:BURSt:INTernal:PERiod {period}")
            self.send_command(f"{src}:BURSt:PHASe {phase}")

    # ==========================================
    # TRIGGER
    # ==========================================

    def set_trigger_source(self, channel, source="IMMediate"):
        """Set the trigger source for sweep or burst.

        Args:
            channel (int): Channel number (1 or 2).
            source (str): IMMediate, EXTernal, TIMer, or BUS. Default IMMediate.
        """
        self._validate_channel(channel)
        self.send_command(f"TRIGger{channel}:SOURce {source}")

    def send_trigger(self):
        """Send a software (bus) trigger."""
        self.send_command("TRIG")

    # ==========================================
    # SYSTEM & UTILITY
    # ==========================================

    def get_error(self):
        """Read the most recent error from the error queue."""
        return self.query("SYSTem:ERRor?")

    def save_state(self, location):
        """Save instrument state to non-volatile memory.

        Args:
            location (int): Memory location 0-4.
        """
        if location not in range(5):
            raise ValueError("State location must be 0-4.")
        self.send_command(f"*SAV {location}")

    def recall_state(self, location):
        """Recall instrument state from non-volatile memory.

        Args:
            location (int): Memory location 0-4.
        """
        if location not in range(5):
            raise ValueError("State location must be 0-4.")
        self.send_command(f"*RCL {location}")
