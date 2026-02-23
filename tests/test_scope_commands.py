"""Automated tests for scope REPL commands using mock instruments."""
import pytest
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lab_instruments.mock_instruments import MockDHO804, MockMSO2024


def make_repl(devices):
    """Create an InstrumentRepl with mock devices pre-loaded."""
    from lab_instruments.src import discovery as _disc
    _disc.InstrumentDiscovery.__init__ = lambda self: None
    _disc.InstrumentDiscovery.scan = lambda self, verbose=True: devices
    from lab_instruments.repl import InstrumentRepl
    repl = InstrumentRepl()
    repl._scan_done.set()
    repl.devices = devices
    return repl


@pytest.fixture
def repl():
    devices = {"scope1": MockDHO804()}
    return make_repl(devices)


# --- Acquisition control ---

class TestScopeAcquisition:
    def test_autoset(self, repl):
        repl.onecmd("scope autoset")

    def test_run(self, repl):
        repl.onecmd("scope run")

    def test_stop(self, repl):
        repl.onecmd("scope stop")

    def test_single(self, repl):
        repl.onecmd("scope single")


# --- Channel control ---

class TestScopeChannel:
    def test_chan_on(self, repl):
        repl.onecmd("scope chan 1 on")

    def test_chan_off(self, repl):
        repl.onecmd("scope chan 1 off")

    def test_chan_all(self, repl):
        repl.onecmd("scope chan all on")

    def test_coupling(self, repl):
        repl.onecmd("scope coupling 1 DC")

    def test_coupling_all(self, repl):
        repl.onecmd("scope coupling all AC")

    def test_probe(self, repl):
        repl.onecmd("scope probe 1 10")

    def test_label(self, repl):
        repl.onecmd("scope label 1 VCC")

    def test_invert_on(self, repl):
        repl.onecmd("scope invert 1 on")

    def test_invert_off(self, repl):
        repl.onecmd("scope invert 1 off")

    def test_bwlimit(self, repl):
        repl.onecmd("scope bwlimit 1 20M")

    def test_bwlimit_off(self, repl):
        repl.onecmd("scope bwlimit 1 OFF")


# --- Horizontal ---

class TestScopeHorizontal:
    def test_hscale(self, repl):
        repl.onecmd("scope hscale 0.001")

    def test_hpos(self, repl):
        repl.onecmd("scope hpos 50")


# --- Vertical ---

class TestScopeVertical:
    def test_vscale(self, repl):
        repl.onecmd("scope vscale 1 0.5")

    def test_vscale_with_pos(self, repl):
        repl.onecmd("scope vscale 1 0.5 -2")

    def test_vpos(self, repl):
        repl.onecmd("scope vpos 1 0")

    def test_vmove(self, repl):
        repl.onecmd("scope vmove 1 -1")


# --- Trigger ---

class TestScopeTrigger:
    def test_trigger(self, repl):
        repl.onecmd("scope trigger 1 0.0")

    def test_trigger_with_slope(self, repl):
        repl.onecmd("scope trigger 1 1.5 FALL")

    def test_force(self, repl):
        repl.onecmd("scope force")


# --- Measurements ---

class TestScopeMeasurements:
    def test_meas(self, repl):
        repl.onecmd("scope meas 1 FREQUENCY")

    def test_meas_pk2pk(self, repl):
        repl.onecmd("scope meas 1 PK2PK")

    def test_meas_all(self, repl):
        repl.onecmd("scope meas all RMS")

    def test_meas_store(self, repl):
        repl.onecmd("scope meas_store 1 FREQUENCY test_freq unit=Hz")
        assert len(repl.measurements) == 1
        assert repl.measurements[0]["label"] == "test_freq"

    def test_meas_delay(self, repl):
        repl.onecmd("scope meas_delay 1 2")

    def test_meas_delay_store(self, repl):
        repl.onecmd("scope meas_delay_store 1 2 prop_delay unit=s")
        assert len(repl.measurements) == 1


# --- Waveform save ---

class TestScopeSave:
    def test_save(self, repl):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test.csv")
            repl.onecmd(f"scope save 1 {path}")


# --- Screenshot ---

class TestScopeScreenshot:
    def test_screenshot_default(self, repl):
        """Screenshot with auto-generated filename should create a file."""
        repl.onecmd("scope screenshot")

    def test_screenshot_custom_name(self, repl):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test_capture.png")
            # Quote path to handle backslashes on Windows
            repl.onecmd(f'scope screenshot "{path}"')
            assert os.path.exists(path)


# --- Display ---

class TestScopeDisplay:
    def test_display_help(self, repl):
        repl.onecmd("scope display")

    def test_display_clear(self, repl):
        repl.onecmd("scope display clear")

    def test_display_brightness(self, repl):
        repl.onecmd("scope display brightness 50")

    def test_display_grid(self, repl):
        repl.onecmd("scope display grid HALF")

    def test_display_gridbright(self, repl):
        repl.onecmd("scope display gridbright 30")

    def test_display_persist(self, repl):
        repl.onecmd("scope display persist INF")

    def test_display_type(self, repl):
        repl.onecmd("scope display type VECTORS")


# --- Acquire ---

class TestScopeAcquire:
    def test_acquire_help(self, repl):
        repl.onecmd("scope acquire")

    def test_acquire_type(self, repl):
        repl.onecmd("scope acquire type AVERAGE")

    def test_acquire_averages(self, repl):
        repl.onecmd("scope acquire averages 64")

    def test_acquire_depth(self, repl):
        repl.onecmd("scope acquire depth 1M")

    def test_acquire_rate(self, repl):
        repl.onecmd("scope acquire rate")


# --- Cursor ---

class TestScopeCursor:
    def test_cursor_help(self, repl):
        repl.onecmd("scope cursor")

    def test_cursor_off(self, repl):
        repl.onecmd("scope cursor off")

    def test_cursor_manual(self, repl):
        repl.onecmd("scope cursor manual X CH1")

    def test_cursor_set(self, repl):
        repl.onecmd("scope cursor set 0.001 0.0 0.002 0.0")

    def test_cursor_read(self, repl):
        repl.onecmd("scope cursor read")


# --- Math ---

class TestScopeMath:
    def test_math_help(self, repl):
        repl.onecmd("scope math")

    def test_math_on(self, repl):
        repl.onecmd("scope math on 1")

    def test_math_off(self, repl):
        repl.onecmd("scope math off 1")

    def test_math_op(self, repl):
        repl.onecmd("scope math op 1 SUB CH1 CH2")

    def test_math_func(self, repl):
        repl.onecmd("scope math func 1 ABS CH1")

    def test_math_fft(self, repl):
        repl.onecmd("scope math fft 1 CH1 window=HANN")

    def test_math_filter(self, repl):
        repl.onecmd("scope math filter 1 LPAS CH1 upper=1000")

    def test_math_scale(self, repl):
        repl.onecmd("scope math scale 1 0.5")


# --- Record ---

class TestScopeRecord:
    def test_record_help(self, repl):
        repl.onecmd("scope record")

    def test_record_on(self, repl):
        repl.onecmd("scope record on")

    def test_record_off(self, repl):
        repl.onecmd("scope record off")

    def test_record_frames(self, repl):
        repl.onecmd("scope record frames 500")

    def test_record_start(self, repl):
        repl.onecmd("scope record start")

    def test_record_stop(self, repl):
        repl.onecmd("scope record stop")

    def test_record_status(self, repl):
        repl.onecmd("scope record status")

    def test_record_play(self, repl):
        repl.onecmd("scope record play")


# --- Mask ---

class TestScopeMask:
    def test_mask_help(self, repl):
        repl.onecmd("scope mask")

    def test_mask_on(self, repl):
        repl.onecmd("scope mask on")

    def test_mask_off(self, repl):
        repl.onecmd("scope mask off")

    def test_mask_source(self, repl):
        repl.onecmd("scope mask source 1")

    def test_mask_tolerance(self, repl):
        repl.onecmd("scope mask tolerance 0.1 0.2")

    def test_mask_create(self, repl):
        repl.onecmd("scope mask create")

    def test_mask_start(self, repl):
        repl.onecmd("scope mask start")

    def test_mask_stop(self, repl):
        repl.onecmd("scope mask stop")

    def test_mask_stats(self, repl):
        repl.onecmd("scope mask stats")

    def test_mask_reset(self, repl):
        repl.onecmd("scope mask reset")


# --- Built-in tools ---

class TestScopeTools:
    def test_awg_help(self, repl):
        repl.onecmd("scope awg")

    def test_counter_help(self, repl):
        repl.onecmd("scope counter")

    def test_dvm_help(self, repl):
        repl.onecmd("scope dvm")

    def test_counter_on(self, repl):
        repl.onecmd("scope counter on")

    def test_counter_read(self, repl):
        repl.onecmd("scope counter read")

    def test_dvm_on(self, repl):
        repl.onecmd("scope dvm on")

    def test_dvm_read(self, repl):
        repl.onecmd("scope dvm read")


# --- Reset ---

class TestScopeReset:
    def test_reset(self, repl):
        repl.onecmd("scope reset")


# --- Help ---

class TestScopeHelp:
    def test_help_no_args(self, repl):
        """Calling scope with no args should print help without error."""
        repl.onecmd("scope")

    def test_unknown_cmd(self, repl):
        """Unknown subcommand should print a warning, not crash."""
        repl.onecmd("scope nonexistent_command")
