"""Tests for pythonic instrument read assignment (issue #43).

Covers:
  - value = dmm read (interactive TUI)
  - value = dmm read in .scpi scripts
  - {value} resolves in print, calc, set, and instrument commands
  - log save CSV captures measurements assigned via new syntax
  - meas_store still works but prints deprecation warning
  - m["label"] still works in calc but prints deprecation warning
  - Unit auto-detection for all modes
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lab_instruments.mock_instruments import (
    MockHP_34401A,
    MockMPS6010H,
    MockXDM1041,
)


def make_repl(devices):
    """Create an InstrumentRepl with mock devices pre-loaded."""
    from lab_instruments.src import discovery as _disc

    _disc.InstrumentDiscovery.__init__ = lambda self: None
    _disc.InstrumentDiscovery.scan = lambda self, verbose=True: devices
    from lab_instruments.repl import InstrumentRepl

    repl = InstrumentRepl()
    repl._scan_thread.join(timeout=5.0)
    repl._scan_done.wait(timeout=5.0)
    repl.devices = devices
    return repl


@pytest.fixture
def repl_dmm():
    devices = {"dmm": MockHP_34401A()}
    return make_repl(devices)


@pytest.fixture
def repl_dmm_psu():
    devices = {"dmm": MockHP_34401A(), "psu": MockMPS6010H()}
    return make_repl(devices)


@pytest.fixture
def repl_owon():
    devices = {"dmm": MockXDM1041()}
    return make_repl(devices)


# -----------------------------------------------------------------------
# Interactive TUI: value = dmm read
# -----------------------------------------------------------------------


class TestInstrumentReadAssignment:
    """Test 'value = <instrument> read' in TUI prompt."""

    def test_dmm_read_assigns_variable(self, repl_dmm):
        repl_dmm.onecmd("dmm config vdc")
        repl_dmm.onecmd("output_v = dmm read")
        assert "output_v" in repl_dmm.ctx.script_vars
        val = float(repl_dmm.ctx.script_vars["output_v"])
        assert 4.0 < val < 6.0

    def test_dmm_read_stores_in_measurement_log(self, repl_dmm):
        repl_dmm.onecmd("dmm config vdc")
        repl_dmm.onecmd("output_v = dmm read")
        assert len(repl_dmm.ctx.measurements) == 1
        entry = repl_dmm.ctx.measurements.get_by_label("output_v")
        assert entry is not None
        assert entry["source"] == "dmm.read"

    def test_dmm_read_unit_autodetect_vdc(self, repl_dmm):
        repl_dmm.onecmd("dmm config vdc")
        repl_dmm.onecmd("v = dmm read")
        entry = repl_dmm.ctx.measurements.get_by_label("v")
        assert entry["unit"] == "V"

    def test_dmm_read_unit_autodetect_idc(self, repl_dmm):
        repl_dmm.onecmd("dmm config idc")
        repl_dmm.onecmd("i = dmm read")
        entry = repl_dmm.ctx.measurements.get_by_label("i")
        assert entry["unit"] == "A"

    def test_dmm_read_unit_autodetect_res(self, repl_dmm):
        repl_dmm.onecmd("dmm config res")
        repl_dmm.onecmd("r = dmm read")
        entry = repl_dmm.ctx.measurements.get_by_label("r")
        assert entry["unit"] == "ohms"

    def test_dmm_read_unit_autodetect_freq(self, repl_dmm):
        repl_dmm.onecmd("dmm config freq")
        repl_dmm.onecmd("f = dmm read")
        entry = repl_dmm.ctx.measurements.get_by_label("f")
        assert entry["unit"] == "Hz"

    def test_dmm_read_unit_autodetect_vac(self, repl_dmm):
        repl_dmm.onecmd("dmm config vac")
        repl_dmm.onecmd("vac = dmm read")
        entry = repl_dmm.ctx.measurements.get_by_label("vac")
        assert entry["unit"] == "V"

    def test_dmm_read_unit_autodetect_iac(self, repl_dmm):
        repl_dmm.onecmd("dmm config iac")
        repl_dmm.onecmd("iac = dmm read")
        entry = repl_dmm.ctx.measurements.get_by_label("iac")
        assert entry["unit"] == "A"

    def test_dmm_read_unit_override(self, repl_dmm):
        repl_dmm.onecmd("dmm config res")
        repl_dmm.onecmd("r = dmm read unit=kohms")
        entry = repl_dmm.ctx.measurements.get_by_label("r")
        assert entry["unit"] == "kohms"

    def test_psu_read_voltage(self, repl_dmm_psu):
        repl_dmm_psu.onecmd("psu meas v")
        repl_dmm_psu.onecmd("supply = psu read")
        assert "supply" in repl_dmm_psu.ctx.script_vars
        entry = repl_dmm_psu.ctx.measurements.get_by_label("supply")
        assert entry is not None
        assert entry["unit"] == "V"
        assert entry["source"] == "psu.read"

    def test_psu_read_current(self, repl_dmm_psu):
        repl_dmm_psu.onecmd("psu meas i")
        repl_dmm_psu.onecmd("supply_i = psu read")
        entry = repl_dmm_psu.ctx.measurements.get_by_label("supply_i")
        assert entry is not None
        assert entry["unit"] == "A"

    def test_owon_read(self, repl_owon):
        repl_owon.onecmd("dmm config vdc")
        repl_owon.onecmd("v = dmm read")
        assert "v" in repl_owon.ctx.script_vars
        entry = repl_owon.ctx.measurements.get_by_label("v")
        assert entry is not None
        assert entry["unit"] == "V"


# -----------------------------------------------------------------------
# Variable resolution: {value} works everywhere
# -----------------------------------------------------------------------


class TestVariableResolution:
    """Test that {value} resolves in print, calc, set, and instrument commands."""

    def test_print_resolves_variable(self, repl_dmm, capsys):
        repl_dmm.onecmd("dmm config vdc")
        repl_dmm.onecmd("output_v = dmm read")
        val = repl_dmm.ctx.script_vars["output_v"]
        repl_dmm.onecmd('print "Measured: {output_v}"')
        captured = capsys.readouterr()
        assert val in captured.out

    def test_calc_resolves_variable(self, repl_dmm):
        repl_dmm.onecmd("dmm config vdc")
        repl_dmm.onecmd("output_v = dmm read")
        repl_dmm.onecmd("calc err {output_v} - 5.0 unit=V")
        entry = repl_dmm.ctx.measurements.get_by_label("err")
        assert entry is not None
        assert entry["unit"] == "V"

    def test_set_resolves_variable(self, repl_dmm):
        repl_dmm.onecmd("dmm config vdc")
        repl_dmm.onecmd("output_v = dmm read")
        repl_dmm.onecmd("doubled = {output_v} * 2")
        assert "doubled" in repl_dmm.ctx.script_vars


# -----------------------------------------------------------------------
# log save captures new-syntax measurements
# -----------------------------------------------------------------------


class TestLogSave:
    """Test that log save CSV captures measurements assigned via new syntax."""

    def test_log_save_csv(self, repl_dmm, tmp_path, monkeypatch):
        repl_dmm.onecmd("dmm config vdc")
        repl_dmm.onecmd("output_v = dmm read")
        # Set data dir to tmp_path so relative paths resolve correctly
        repl_dmm.ctx._data_dir_override = str(tmp_path)
        repl_dmm.onecmd("log save test_output.csv csv")
        csv_path = str(tmp_path / "test_output.csv")
        assert os.path.isfile(csv_path)
        with open(csv_path) as f:
            content = f.read()
        assert "output_v" in content
        assert "dmm.read" in content


# -----------------------------------------------------------------------
# Deprecation warnings
# -----------------------------------------------------------------------


class TestDeprecationWarnings:
    """Test that deprecated syntax still works but prints warnings."""

    def test_meas_store_still_works(self, repl_dmm, capsys):
        repl_dmm.onecmd("dmm config vdc")
        repl_dmm.onecmd("dmm meas_store test_v unit=V")
        assert len(repl_dmm.ctx.measurements) == 1
        captured = capsys.readouterr()
        assert "deprecated" in captured.out.lower()

    def test_m_bracket_in_calc_warns(self, repl_dmm, capsys):
        repl_dmm.onecmd("dmm config vdc")
        repl_dmm.onecmd("dmm meas_store test_v unit=V")
        repl_dmm.onecmd('calc power m["test_v"] * 0.1 unit=W')
        captured = capsys.readouterr()
        assert "deprecated" in captured.out.lower()

    def test_psu_meas_store_still_works(self, repl_dmm_psu, capsys):
        repl_dmm_psu.onecmd("psu meas_store v test_psu unit=V")
        assert repl_dmm_psu.ctx.measurements.get_by_label("test_psu") is not None
        captured = capsys.readouterr()
        assert "deprecated" in captured.out.lower()


# -----------------------------------------------------------------------
# Script (.scpi) support
# -----------------------------------------------------------------------


class TestScriptSupport:
    """Test that value = dmm read works inside .scpi scripts."""

    def test_instrument_read_in_script(self, repl_dmm):
        script_lines = [
            "dmm config vdc",
            "output_v = dmm read",
            'print "Got {output_v}"',
        ]
        repl_dmm.ctx.scripts["test_read"] = script_lines
        repl_dmm.onecmd("script run test_read")
        assert "output_v" in repl_dmm.ctx.script_vars
        assert repl_dmm.ctx.measurements.get_by_label("output_v") is not None

    def test_instrument_read_unit_in_script(self, repl_dmm):
        script_lines = [
            "dmm config res",
            "r = dmm read unit=kohms",
        ]
        repl_dmm.ctx.scripts["test_unit"] = script_lines
        repl_dmm.onecmd("script run test_unit")
        entry = repl_dmm.ctx.measurements.get_by_label("r")
        assert entry is not None
        assert entry["unit"] == "kohms"


# -----------------------------------------------------------------------
# Edge cases
# -----------------------------------------------------------------------


class TestEdgeCases:
    """Edge cases for instrument read assignment."""

    def test_nonexistent_instrument_type(self, repl_dmm):
        """Assignment to unknown instrument falls through to normal assignment."""
        repl_dmm.onecmd("x = foobar read")
        # Not an instrument read — should be treated as normal assignment
        assert "x" in repl_dmm.ctx.script_vars
        assert repl_dmm.ctx.script_vars["x"] == "foobar read"

    def test_no_device_connected_for_type(self, repl_dmm):
        """Trying to read a PSU when none is connected gives an error."""
        repl_dmm.onecmd("v = psu read")
        assert repl_dmm.ctx.command_had_error

    def test_plain_assignment_still_works(self, repl_dmm):
        """Normal var = expr assignment still works."""
        repl_dmm.onecmd("voltage = 5.0")
        assert repl_dmm.ctx.script_vars["voltage"] == "5.0"

    def test_arithmetic_assignment_still_works(self, repl_dmm):
        """Normal var = arithmetic assignment still works."""
        repl_dmm.onecmd("x = 3.0")
        repl_dmm.onecmd("y = x * 2")
        assert repl_dmm.ctx.script_vars["y"] == "6.0"
