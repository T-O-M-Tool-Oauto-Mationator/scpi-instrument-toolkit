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


def get_mock_devices(verbose=True):
    from lab_instruments import ColorPrinter
    if verbose:
        ColorPrinter.warning("Mock mode — no real instruments connected")
        ColorPrinter.info("Injecting: psu (MockPSU), awg (MockAWG), dmm (MockDMM), scope (MockScope)")
    return {
        "psu": MockPSU(),
        "awg": MockAWG(),
        "dmm": MockDMM(),
        "scope": MockScope(),
    }
