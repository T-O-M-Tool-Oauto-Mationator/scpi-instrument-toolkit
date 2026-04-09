"""
Mock instrument classes for testing the REPL without physical hardware.

Usage:
    python repl.py --mock
"""

import random

from lab_instruments.src.hp_e3631a import HP_E3631A as _HP_E3631A


class MockBase:
    def disconnect(self):
        pass

    def reset(self):
        pass

    def query(self, cmd, **kwargs):
        return f"MOCK INSTRUMENTS INC.,{type(self).__name__},SN000001,v1.0"

    def send_command(self, cmd):
        pass


class MockPSU(MockBase):
    def __init__(self):
        self._voltage = 5.0
        self._current = 0.1
        self._output = False

    def enable_output(self, state):
        self._output = bool(state)

    def disable_all_channels(self):
        self._output = False

    def set_voltage(self, v):
        self._voltage = float(v)

    def set_current_limit(self, i):
        self._current = float(i)

    def set_output_channel(self, ch, voltage, current_limit=None):
        self._voltage = float(voltage)
        if current_limit is not None:
            self._current = float(current_limit)

    def measure_voltage(self, ch=None):
        return round(random.uniform(4.985, 5.015), 6)

    def measure_current(self, ch=None):
        return round(random.uniform(0.0990, 0.1010), 6)

    def get_voltage_setpoint(self):
        return self._voltage

    def get_current_limit(self):
        return self._current

    def get_output_state(self):
        return self._output

    def save_state(self, n):
        pass

    def recall_state(self, n):
        pass

    def set_tracking(self, on):
        pass


class MockAWG(MockBase):
    def __init__(self):
        self._ch_amplitude = {1: 5.0, 2: 5.0}
        self._ch_offset = {1: 0.0, 2: 0.0}
        self._ch_frequency = {1: 10000.0, 2: 10000.0}
        self._ch_output = {1: False, 2: False}

    def enable_output(self, ch_or_state=None, state=None, ch1=None, ch2=None):
        if ch1 is not None:
            self._ch_output[1] = bool(ch1)
        if ch2 is not None:
            self._ch_output[2] = bool(ch2)
        if ch_or_state is not None and state is not None:
            self._ch_output[int(ch_or_state)] = bool(state)

    def disable_all_channels(self):
        self._ch_output[1] = False
        self._ch_output[2] = False

    def set_waveform(self, ch, wave, **kwargs):
        pass

    def set_frequency(self, ch, freq):
        self._ch_frequency[int(ch)] = float(freq)

    def set_amplitude(self, ch, amp):
        self._ch_amplitude[int(ch)] = float(amp)

    def set_offset(self, ch, offset):
        self._ch_offset[int(ch)] = float(offset)

    def set_duty_cycle(self, ch, duty):
        pass

    def set_phase(self, ch, phase):
        pass

    def set_sync_output(self, on):
        pass

    def get_amplitude(self, ch):
        return self._ch_amplitude.get(int(ch))

    def get_offset(self, ch):
        return self._ch_offset.get(int(ch))

    def get_frequency(self, ch):
        return self._ch_frequency.get(int(ch))

    def get_output_state(self, ch):
        return self._ch_output.get(int(ch), False)


class MockDMM(MockBase):
    def read(self):
        return round(random.uniform(4.9980, 5.0020), 6)

    def fetch(self):
        return round(random.uniform(4.9980, 5.0020), 6)

    def beep(self):
        pass

    def set_display(self, on):
        pass

    def display_text(self, text):
        pass

    def display_text_scroll(self, *args, **kwargs):
        pass

    def display_text_rolling(self, *args, **kwargs):
        pass

    def clear_display(self):
        pass

    def clear_display_text(self):
        pass

    def configure_dc_voltage(self, range_val="DEF", resolution="DEF", nplc=None):
        pass

    def configure_ac_voltage(self, range_val="DEF", resolution="DEF"):
        pass

    def configure_dc_current(self, range_val="DEF", resolution="DEF", nplc=None):
        pass

    def configure_ac_current(self, range_val="DEF", resolution="DEF"):
        pass

    def configure_resistance_2wire(self, range_val="DEF", resolution="DEF", nplc=None):
        pass

    def configure_resistance_4wire(self, range_val="DEF", resolution="DEF", nplc=None):
        pass

    def configure_frequency(self, range_val="DEF", resolution="DEF"):
        pass

    def configure_period(self, range_val="DEF", resolution="DEF"):
        pass

    def configure_continuity(self):
        pass

    def configure_diode(self):
        pass

    def measure_dc_voltage(self, range_val="DEF", resolution="DEF"):
        return self.read()

    def measure_ac_voltage(self, range_val="DEF", resolution="DEF"):
        return self.read()

    def measure_dc_current(self, range_val="DEF", resolution="DEF"):
        return round(random.uniform(0.0998, 0.1002), 6)

    def measure_ac_current(self, range_val="DEF", resolution="DEF"):
        return round(random.uniform(0.0998, 0.1002), 6)

    def measure_resistance_2wire(self, range_val="DEF", resolution="DEF"):
        return round(random.uniform(99.5, 100.5), 3)

    def measure_resistance_4wire(self, range_val="DEF", resolution="DEF"):
        return round(random.uniform(99.5, 100.5), 3)

    def measure_frequency(self, range_val="DEF", resolution="DEF"):
        return round(random.uniform(999.8, 1000.2), 3)

    def measure_period(self, range_val="DEF", resolution="DEF"):
        return round(1 / 1000.0, 9)

    def measure_continuity(self):
        return round(random.uniform(0.4, 0.6), 3)

    def measure_diode(self):
        return round(random.uniform(0.60, 0.70), 3)

    def set_mode(self, mode):
        pass


class MockScope(MockBase):
    num_channels = 4

    def autoset(self):
        pass

    def run(self):
        pass

    def stop(self):
        pass

    def single(self):
        pass

    def set_trigger_sweep(self, sweep):
        pass

    def get_trigger_status(self):
        return "TD"

    def wait_for_stop(self, timeout=10.0):
        return True

    def enable_channel(self, ch):
        pass

    def disable_channel(self, ch):
        pass

    def enable_all_channels(self):
        pass

    def disable_all_channels(self):
        pass

    def set_coupling(self, ch, coupling):
        pass

    def set_probe_attenuation(self, ch, atten):
        pass

    def set_horizontal_scale(self, scale):
        pass

    def set_horizontal_position(self, pos):
        pass

    def move_horizontal(self, delta):
        pass

    def set_vertical_scale(self, ch, scale, pos=0.0):
        pass

    def set_vertical_position(self, ch, pos):
        pass

    def move_vertical(self, ch, delta):
        pass

    def configure_trigger(self, ch, level, slope, mode):
        pass

    def measure_bnf(self, ch, mtype):
        values = {
            "FREQUENCY": round(random.uniform(999.5, 1000.5), 3),
            "PK2PK": round(random.uniform(1.98, 2.02), 4),
            "RMS": round(random.uniform(0.695, 0.715), 4),
            "MEAN": round(random.uniform(-0.005, 0.005), 6),
            "PERIOD": round(1 / 1000.0, 9),
            "AMPLITUDE": round(random.uniform(1.98, 2.02), 4),
            "MINIMUM": round(random.uniform(-1.01, -0.99), 4),
            "MAXIMUM": round(random.uniform(0.99, 1.01), 4),
        }
        return values.get(mtype.upper(), round(random.uniform(0.0, 1.0), 4))

    def configure_measurement(self, channel, measurement_type):
        pass

    # Measurement shorthands (match Tektronix driver API)
    def measure_frequency(self, ch):
        return self.measure_bnf(ch, "FREQUENCY")

    def measure_peak_to_peak(self, ch):
        return self.measure_bnf(ch, "PK2PK")

    def measure_rms(self, ch):
        return self.measure_bnf(ch, "RMS")

    def measure_mean(self, ch):
        return self.measure_bnf(ch, "MEAN")

    def measure_max(self, ch):
        return self.measure_bnf(ch, "MAXIMUM")

    def measure_min(self, ch):
        return self.measure_bnf(ch, "MINIMUM")

    def measure_period(self, ch):
        return self.measure_bnf(ch, "PERIOD")

    def get_waveform_data(self, ch):
        return [random.randint(0, 255) for _ in range(1000)]

    def get_waveform_scaled(self, ch):
        n = 1000
        dt = 1e-6
        time_vals = [i * dt for i in range(n)]
        import math

        volt_vals = [math.sin(2 * math.pi * 1000 * t) for t in time_vals]
        return time_vals, volt_vals

    def measure_delay(self, ch1, ch2, edge1="RISE", edge2="RISE", direction="FORWARDS"):
        return round(random.uniform(-1e-6, 1e-6), 9)

    def save_waveform_csv(self, ch, fname, **kwargs):
        pass

    def save_waveforms_csv(self, channels, fname, **kwargs):
        pass

    def awg_set_output_enable(self, on):
        pass

    def awg_configure_simple(self, func, freq, amp, offset, enable=True):
        pass

    def awg_set_function(self, func):
        pass

    def awg_set_frequency(self, freq):
        pass

    def awg_set_amplitude(self, amp):
        pass

    def awg_set_offset(self, offset):
        pass

    def awg_set_phase(self, phase):
        pass

    def awg_set_square_duty(self, duty):
        pass

    def awg_set_ramp_symmetry(self, sym):
        pass

    def awg_set_modulation_enable(self, on):
        pass

    def awg_set_modulation_type(self, mtype):
        pass

    def set_counter_enable(self, on):
        pass

    def get_counter_current(self):
        return round(random.uniform(999.5, 1000.5), 3)

    def set_counter_source(self, ch):
        pass

    def set_counter_mode(self, mode):
        pass

    def set_dvm_enable(self, on):
        pass

    def get_dvm_current(self):
        return round(random.uniform(4.997, 5.003), 4)

    def set_dvm_source(self, ch):
        pass


class MockDHO804(MockScope):
    """Mock Rigol DHO804 oscilloscope with model-specific features."""

    def get_screenshot(self):
        """Return dummy PNG bytes (a minimal valid PNG)."""
        # Minimal 1x1 white PNG
        import base64

        return base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAC0lEQVQI12NgAAIABQABNl7BcQAAAABJRU5ErkJggg=="
        )

    def set_channel_label(self, channel, label, show=True):
        pass

    def invert_channel(self, channel, enable):
        pass

    def set_bandwidth_limit(self, channel, limit):
        pass

    def force_trigger(self):
        pass

    # Display methods
    def clear_display(self):
        pass

    def set_waveform_brightness(self, brightness):
        pass

    def set_grid_type(self, grid):
        pass

    def set_grid_brightness(self, brightness):
        pass

    def set_persistence(self, time):
        pass

    def set_display_type(self, display_type):
        pass

    # Acquire methods
    def set_acquisition_type(self, acq_type):
        pass

    def set_average_count(self, count):
        pass

    def set_memory_depth(self, depth):
        pass

    def get_memory_depth(self):
        return "AUTO"

    def get_sample_rate(self):
        return 1e9

    # Cursor methods
    def set_cursor_mode(self, mode):
        pass

    def set_manual_cursor_type(self, cursor_type):
        pass

    def set_manual_cursor_source(self, source):
        pass

    def set_manual_cursor_positions(self, ax=None, ay=None, bx=None, by=None):
        pass

    def get_manual_cursor_values(self):
        return {"AX": 0.0, "AY": 0.0, "BX": 1.0, "BY": 1.0, "DX": 1.0, "DY": 1.0}

    # Math methods
    def enable_math_channel(self, math_ch, enable=True):
        pass

    def configure_math_operation(self, math_ch, operation, source1, source2=None):
        pass

    def configure_math_function(self, math_ch, function, source):
        pass

    def configure_fft(self, math_ch, source, window="RECT"):
        pass

    def configure_digital_filter(self, math_ch, filter_type, source, upper=None, lower=None):
        pass

    def set_math_scale(self, math_ch, scale, offset=None):
        pass

    # Record methods
    def set_recording_enable(self, enable):
        pass

    def get_recording_enable(self):
        return False

    def set_recording_frames(self, frames):
        pass

    def get_recording_frames(self):
        return 100

    def start_recording(self):
        pass

    def stop_recording(self):
        pass

    def get_recording_status(self):
        return "STOP"

    def start_playback(self):
        pass

    def stop_playback(self):
        pass

    def get_playback_status(self):
        return "STOP"

    # Mask methods
    def set_mask_enable(self, enable):
        pass

    def get_mask_enable(self):
        return False

    def set_mask_source(self, channel):
        pass

    def get_mask_source(self):
        return 1

    def set_mask_tolerance_x(self, tolerance):
        pass

    def set_mask_tolerance_y(self, tolerance):
        pass

    def create_mask(self):
        pass

    def start_mask_test(self):
        pass

    def stop_mask_test(self):
        pass

    def get_mask_test_status(self):
        return "STOP"

    def reset_mask_statistics(self):
        pass

    def get_mask_failed_count(self):
        return 0

    def get_mask_passed_count(self):
        return random.randint(90, 100)

    def get_mask_total_count(self):
        return 100

    def get_mask_statistics(self):
        passed = random.randint(90, 100)
        total = 100
        return {"passed": passed, "failed": total - passed, "total": total}


class MockDSOX1204G(MockScope):
    """Mock Keysight DSOX1204G oscilloscope."""

    def digitize(self, channel=None):
        pass

    def measure_counter(self, channel=None):
        return round(random.uniform(999.5, 1000.5), 3)

    def measure_rise_time(self, ch):
        return round(random.uniform(0.9e-6, 1.1e-6), 9)

    def measure_fall_time(self, ch):
        return round(random.uniform(0.9e-6, 1.1e-6), 9)

    def measure_duty_cycle(self, ch):
        return round(random.uniform(49.5, 50.5), 2)

    def measure_pos_width(self, ch):
        return round(random.uniform(0.49e-3, 0.51e-3), 6)

    def measure_neg_width(self, ch):
        return round(random.uniform(0.49e-3, 0.51e-3), 6)

    def measure_overshoot(self, ch):
        return round(random.uniform(3.0, 7.0), 2)

    def measure_preshoot(self, ch):
        return round(random.uniform(1.0, 3.0), 2)

    def get_screenshot(self):
        """Return dummy PNG bytes."""
        import base64

        return base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAC0lEQVQI12NgAAIABQABNl7BcQAAAABJRU5ErkJggg=="
        )

    def set_channel_label(self, channel, label, show=True):
        pass

    def invert_channel(self, channel, enable):
        pass

    def set_bandwidth_limit(self, channel, limit):
        pass

    def force_trigger(self):
        pass

    def clear_display(self):
        pass

    def set_waveform_brightness(self, brightness):
        pass

    def set_persistence(self, time):
        pass

    def set_display_type(self, display_type):
        pass

    def set_acquisition_type(self, acq_type):
        pass

    def set_average_count(self, count):
        pass

    def get_sample_rate(self):
        return 1e9

    def enable_math_channel(self, math_ch, enable=True):
        pass

    def configure_math_operation(self, math_ch, operation, source1, source2=None):
        pass

    def configure_math_function(self, math_ch, function, source):
        pass

    def configure_fft(self, math_ch, source, window="RECT"):
        pass

    def set_math_scale(self, math_ch, scale, offset=None):
        pass

    def set_mask_enable(self, enable):
        pass

    def get_mask_enable(self):
        return False

    def set_mask_source(self, channel):
        pass

    def get_mask_source(self):
        return 1

    def set_mask_tolerance_x(self, tolerance):
        pass

    def set_mask_tolerance_y(self, tolerance):
        pass

    def create_mask(self):
        pass

    def start_mask_test(self):
        pass

    def stop_mask_test(self):
        pass

    def get_mask_test_status(self):
        return "STOP"

    def reset_mask_statistics(self):
        pass

    def get_mask_failed_count(self):
        return 0

    def get_mask_passed_count(self):
        return random.randint(90, 100)

    def get_mask_total_count(self):
        return 100

    def get_mask_statistics(self):
        passed = random.randint(90, 100)
        total = 100
        return {"passed": passed, "failed": total - passed, "total": total}

    def clear_measurements(self):
        pass

    def awg_set_output_enable(self, on):
        pass

    def awg_configure_simple(self, func, freq, amp, offset, enable=True):
        pass

    def awg_set_function(self, func):
        pass

    def awg_set_frequency(self, freq):
        pass

    def awg_set_amplitude(self, amp):
        pass

    def awg_set_offset(self, offset):
        pass

    def awg_set_square_duty(self, duty):
        pass

    def awg_set_ramp_symmetry(self, sym):
        pass

    def set_dvm_enable(self, on):
        pass

    def get_dvm_current(self):
        return round(random.uniform(4.997, 5.003), 4)

    def set_dvm_source(self, ch):
        pass

    def set_cursor_mode(self, mode):
        pass

    def set_cursor_source(self, channel):
        pass

    def set_manual_cursor_positions(self, x1=None, y1=None, x2=None, y2=None):
        pass

    def get_manual_cursor_values(self):
        return {"x1": 0.0, "y1": 0.0, "x2": 1.0, "y2": 1.0, "dx": 1.0, "dy": 1.0}

    def set_timebase_mode(self, mode):
        pass

    def get_timebase_mode(self):
        return "MAIN"

    def set_timebase_reference(self, ref):
        pass

    def get_timebase_reference(self):
        return "LEFT"

    def set_trigger_holdoff(self, holdoff):
        pass

    def get_trigger_holdoff(self):
        return 100e-9

    def set_trigger_noise_reject(self, enable):
        pass

    def set_trigger_hf_reject(self, enable):
        pass

    def set_trigger_coupling(self, coupling):
        pass

    def set_measurement_statistics(self, enable):
        pass

    def reset_measurement_statistics(self):
        pass

    def get_measurement_results(self):
        return ""

    def awg_set_pulse_width(self, width):
        pass

    def set_acquisition_mode(self, mode):
        pass

    def set_segment_count(self, count):
        pass

    def get_segment_count(self):
        return 100

    def set_segment_index(self, index):
        pass

    def get_segment_index(self):
        return 1

    def save_setup(self, slot):
        pass

    def recall_setup(self, slot):
        pass

    def self_test(self):
        return 0

    def set_system_lock(self, enable):
        pass

    def set_system_message(self, message):
        pass

    def set_display_vectors(self, enable):
        pass

    def set_display_annotation(self, text):
        pass

    def clear_display_annotation(self):
        pass

    def set_channel_units(self, channel, units):
        pass

    def get_channel_units(self, channel):
        return "VOLT"


class MockMSO2024(MockScope):
    """Mock Tektronix MSO2024 oscilloscope."""

    pass


class MockMPS6010H(MockPSU):
    """Mock Matrix MPS-6010H power supply with remote mode."""

    MAX_VOLTAGE = 60.0
    MAX_CURRENT = 10.0

    def set_remote_mode(self, on):
        pass


class MockNI_PXIe_4139(MockPSU):
    """Mock NI PXIe-4139 Source Measure Unit."""

    def __init__(self):
        super().__init__()
        self._output_mode = "voltage"
        self._current_level = 0.0
        self._voltage_limit = 5.0
        self._source_delay = 0.0
        self._samples_to_average = 1
        self._in_compliance = False

    def measure_vi(self) -> dict:
        if self._output_mode == "current":
            v = round(random.uniform(self._voltage_limit * 0.997, self._voltage_limit * 1.003), 6)
            i = round(random.uniform(self._current_level * 0.990, self._current_level * 1.010), 6)
        else:
            v = round(random.uniform(self._voltage * 0.997, self._voltage * 1.003), 6)
            i = round(random.uniform(self._current * 0.990, self._current * 1.010), 6)
        return {"voltage": v, "current": i, "in_compliance": self._in_compliance}

    def measure_voltage(self, ch=None):
        return self.measure_vi()["voltage"]

    def measure_current(self, ch=None):
        return self.measure_vi()["current"]

    def query_in_compliance(self) -> bool:
        return self._in_compliance

    def _set_mock_compliance(self, state: bool) -> None:
        self._in_compliance = bool(state)

    def set_source_delay(self, seconds: float) -> None:
        if not 0 <= seconds <= 167.0:
            raise ValueError("source_delay must be between 0 and 167.0 seconds")
        self._source_delay = float(seconds)

    def get_source_delay(self) -> float:
        return self._source_delay

    def set_voltage_mode(self, voltage: float, current_limit: float = None) -> None:
        self._voltage = float(voltage)
        if current_limit is not None:
            self._current = float(current_limit)
        self._output_mode = "voltage"

    def set_current_mode(self, current: float, voltage_limit: float = None) -> None:
        self._current_level = float(current)
        if voltage_limit is not None:
            self._voltage_limit = float(voltage_limit)
        self._output_mode = "current"

    def get_output_mode(self) -> str:
        return self._output_mode

    def get_voltage_setpoint(self):
        if self._output_mode == "current":
            return self._voltage_limit
        return self._voltage

    def get_current_limit(self):
        if self._output_mode == "current":
            return self._current_level
        return self._current

    def set_samples_to_average(self, n: int) -> None:
        n = int(n)
        if n < 1:
            raise ValueError("samples_to_average must be >= 1")
        self._samples_to_average = n

    def get_samples_to_average(self) -> int:
        return self._samples_to_average

    def read_temperature(self) -> float:
        return round(random.uniform(22.0, 28.0), 1)


class MockMultiChannelPSU(MockPSU):
    """Base for multi-channel PSUs: adds select_channel + per-channel output state."""

    def __init__(self):
        super().__init__()
        if hasattr(self.__class__, "CHANNEL_FROM_NUMBER"):
            self._ch_outputs: dict = {ch: False for ch in self.__class__.CHANNEL_FROM_NUMBER.values()}
        else:
            self._ch_outputs = {k: False for k in self.CHANNEL_MAP}
        self._selected_ch = None

    def select_channel(self, ch: str) -> None:
        self._selected_ch = ch

    def enable_output(self, state) -> None:
        ch = self._selected_ch
        if ch and ch in self._ch_outputs:
            self._ch_outputs[ch] = bool(state)
        else:
            for k in self._ch_outputs:
                self._ch_outputs[k] = bool(state)

    def get_output_state(self, ch=None) -> bool:
        key = ch if ch is not None else self._selected_ch
        if key and key in self._ch_outputs:
            return self._ch_outputs[key]
        return any(self._ch_outputs.values())

    def disable_all_channels(self) -> None:
        for k in self._ch_outputs:
            self._ch_outputs[k] = False


class MockHP_E3631A(MockMultiChannelPSU):
    """Mock HP E3631A triple-output power supply."""

    Channel = _HP_E3631A.Channel
    CHANNEL_FROM_NUMBER = _HP_E3631A.CHANNEL_FROM_NUMBER
    CHANNEL_LIMITS = {
        _HP_E3631A.Channel.POSITIVE_6V: (6.0, 5.0),
        _HP_E3631A.Channel.POSITIVE_25V: (25.0, 1.0),
        _HP_E3631A.Channel.NEGATIVE_25V: (25.0, 1.0),
    }


class MockEDU36311A(MockMultiChannelPSU):
    """Mock Keysight EDU36311A triple-output power supply."""

    CHANNEL_MAP = {
        "p6v_channel": "P6V",
        "p30v_channel": "P30V",
        "n30v_channel": "N30V",
    }
    CHANNEL_LIMITS = {
        "p6v_channel": (6.0, 5.0),
        "p30v_channel": (30.0, 1.0),
        "n30v_channel": (30.0, 1.0),
    }


class MockJDS6600(MockAWG):
    """Mock JDS6600 DDS function generator."""

    VALID_WAVEFORMS = [
        "SINE",
        "SQUARE",
        "PULSE",
        "TRIANGLE",
        "PARTIAL_SINE",
        "CMOS",
        "DC",
        "HALF_WAVE",
        "FULL_WAVE",
        "POS_LADDER",
        "NEG_LADDER",
        "NOISE",
        "EXP_RISE",
        "EXP_DECAY",
        "MULTITONE",
        "SINC",
        "LORENZ",
    ]


class MockEDU33212A(MockAWG):
    """Mock Keysight EDU33212A function generator."""

    VALID_WAVEFORMS = ["SIN", "SQU", "RAMP", "PULS", "NOIS", "PRBS", "DC", "ARB"]


class MockBK_4063(MockAWG):
    """Mock B&K Precision 4063 function generator."""

    VALID_WAVEFORMS = ["SINE", "SQUARE", "RAMP", "PULSE", "NOISE", "DC", "ARB"]


class MockHP_34401A(MockDMM):
    """Mock HP 34401A digital multimeter."""

    pass


class MockEDU34450A(MockDMM):
    """Mock Keysight EDU34450A digital multimeter."""

    def configure_capacitance(self, range_val="DEF"):
        pass

    def configure_temperature(self):
        pass

    def measure_capacitance(self, range_val="DEF"):
        return round(random.uniform(99e-9, 101e-9), 12)

    def measure_temperature(self):
        return round(random.uniform(22.0, 26.0), 1)


class MockXDM1041(MockDMM):
    """Mock OWON XDM1041 digital multimeter."""

    pass


class MockEV2300(MockBase):
    """Mock TI EV2300 USB-to-I2C adapter."""

    def __init__(self):
        self.resource_name = "mock-ev2300"
        self._is_open = False

    def connect(self):
        self._is_open = True

    def disconnect(self):
        self._is_open = False

    @property
    def is_open(self):
        return self._is_open

    def read_word(self, i2c_addr: int, register: int) -> dict:
        return {"ok": True, "cmd": 0x41, "value": random.randint(0, 0xFFFF), "crc_ok": True, "error": False}

    def write_word(self, i2c_addr: int, register: int, value: int) -> dict:
        return {"ok": True, "cmd": 0x44, "crc_ok": True, "error": False}

    def read_byte(self, i2c_addr: int, register: int) -> dict:
        return {"ok": True, "cmd": 0x43, "value": random.randint(0, 0xFF), "crc_ok": True, "error": False}

    def write_byte(self, i2c_addr: int, register: int, value: int) -> dict:
        return {"ok": True, "cmd": 0x47, "crc_ok": True, "error": False}

    def read_block(self, i2c_addr: int, register: int) -> dict:
        block = bytes(random.randint(0, 0xFF) for _ in range(4))
        return {"ok": True, "cmd": 0x42, "block": block, "crc_ok": True, "error": False}

    def write_block(self, i2c_addr: int, register: int, data: bytes) -> dict:
        return {"ok": True, "cmd": 0x45, "crc_ok": True, "error": False}

    def send_byte(self, i2c_addr: int, command: int) -> dict:
        return {"ok": True, "cmd": 0x46, "crc_ok": True, "error": False}

    def get_device_info(self) -> dict:
        return {
            "ok": True,
            "vid": "0x0451",
            "pid": "0x0036",
            "serial": "MOCK001",
            "product": "EV2300A",
            "manufacturer": "Texas Inst",
            "version": "0x0200",
        }

    def i2c_power(self, enabled: int = 1) -> dict:
        return {"ok": True, "status": 0, "enabled": int(enabled)}

    def open_device(self, adapter: str = "auto") -> dict:
        self.connect()
        return {"ok": True, "status": 0}

    def close_device(self) -> int:
        self.disconnect()
        return 0

    def read_smbus_word(self, i2c_addr: int, register_addr: int, pec: int = 0) -> dict:
        r = self.read_word(i2c_addr, register_addr)
        return {"ok": True, "status": 0, "value": r["value"]}

    def write_smbus_byte(self, i2c_addr: int, register_addr: int, value: int, pec: int = 0) -> dict:
        return {"ok": True, "status": 0, "register": register_addr, "value": value & 0xFF}

    def clear_status(self):
        pass

    def query(self, cmd, **kwargs):
        return "Texas Instruments,EV2300A,MOCK001,mock"

    def probe_command(self, cmd, i2c_addr=0x08, register=0x00, data=b"", write_submit=False):
        return {"ok": True, "cmd": cmd | 0x40, "probe_cmd": cmd, "error": False}


def get_mock_devices(verbose=True):
    from lab_instruments import ColorPrinter

    if verbose:
        ColorPrinter.warning("Mock mode — no real instruments connected")
        ColorPrinter.info(
            "Injecting: psu1 (MockHP_E3631A), psu2 (MockMPS6010H), psu3 (MockEDU36311A), "
            "smu (MockNI_PXIe_4139), "
            "awg1 (MockEDU33212A), awg2 (MockJDS6600), awg3 (MockBK_4063), "
            "dmm1 (MockHP_34401A), dmm2 (MockXDM1041), dmm3 (MockEDU34450A), "
            "scope1 (MockDHO804), scope2 (MockMSO2024), scope3 (MockDSOX1204G), "
            "ev2300 (MockEV2300)"
        )
    return {
        "psu1": MockHP_E3631A(),
        "psu2": MockMPS6010H(),
        "psu3": MockEDU36311A(),
        "smu": MockNI_PXIe_4139(),
        "awg1": MockEDU33212A(),
        "awg2": MockJDS6600(),
        "awg3": MockBK_4063(),
        "dmm1": MockHP_34401A(),
        "dmm2": MockXDM1041(),
        "dmm3": MockEDU34450A(),
        "scope1": MockDHO804(),
        "scope2": MockMSO2024(),
        "scope3": MockDSOX1204G(),
        "ev2300": MockEV2300(),
    }
