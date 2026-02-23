"""
Mock instrument classes for testing the REPL without physical hardware.

Usage:
    python repl.py --mock
"""

import random


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
    def enable_output(self, state):
        pass

    def disable_all_channels(self):
        pass

    def set_voltage(self, v):
        pass

    def set_current_limit(self, i):
        pass

    def set_output_channel(self, ch, v, i=None):
        pass

    def measure_voltage(self, ch=None):
        return round(random.uniform(4.985, 5.015), 6)

    def measure_current(self, ch=None):
        return round(random.uniform(0.0990, 0.1010), 6)

    def get_voltage_setpoint(self):
        return 5.0

    def get_current_limit(self):
        return 0.1

    def get_output_state(self):
        return True

    def save_state(self, n):
        pass

    def recall_state(self, n):
        pass

    def set_tracking(self, on):
        pass


class MockAWG(MockBase):
    def enable_output(self, ch_or_state=None, state=None, ch1=None, ch2=None):
        pass

    def disable_all_channels(self):
        pass

    def set_waveform(self, ch, wave, **kwargs):
        pass

    def set_frequency(self, ch, freq):
        pass

    def set_amplitude(self, ch, amp):
        pass

    def set_offset(self, ch, offset):
        pass

    def set_duty_cycle(self, ch, duty):
        pass

    def set_phase(self, ch, phase):
        pass

    def set_sync_output(self, on):
        pass


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
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAC0lEQVQI12NgAAIABQAB"
            "Nl7BcQAAAABJRU5ErkJggg=="
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


class MockMSO2024(MockScope):
    """Mock Tektronix MSO2024 oscilloscope."""
    pass


class MockMPS6010H(MockPSU):
    """Mock Matrix MPS-6010H power supply with remote mode."""

    def set_remote_mode(self, on):
        pass


class MockHP_E3631A(MockPSU):
    """Mock HP E3631A triple-output power supply."""
    pass


class MockJDS6600(MockAWG):
    """Mock JDS6600 DDS function generator."""
    pass


class MockEDU33212A(MockAWG):
    """Mock Keysight EDU33212A function generator."""
    pass


class MockHP_34401A(MockDMM):
    """Mock HP 34401A digital multimeter."""
    pass


class MockXDM1041(MockDMM):
    """Mock OWON XDM1041 digital multimeter."""
    pass


def get_mock_devices(verbose=True):
    from lab_instruments import ColorPrinter
    if verbose:
        ColorPrinter.warning("Mock mode — no real instruments connected")
        ColorPrinter.info("Injecting: psu1 (MockHP_E3631A), psu2 (MockMPS6010H), awg1 (MockEDU33212A), awg2 (MockJDS6600), dmm1 (MockHP_34401A), dmm2 (MockXDM1041), scope1 (MockDHO804), scope2 (MockMSO2024)")
    return {
        "psu1": MockHP_E3631A(),
        "psu2": MockMPS6010H(),
        "awg1": MockEDU33212A(),
        "awg2": MockJDS6600(),
        "dmm1": MockHP_34401A(),
        "dmm2": MockXDM1041(),
        "scope1": MockDHO804(),
        "scope2": MockMSO2024(),
    }
