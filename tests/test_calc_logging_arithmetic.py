"""Extensive tests for calc command, logging system, and arithmetic operations together."""

import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def make_repl(devices=None):
    from lab_instruments.src import discovery as _disc

    _disc.InstrumentDiscovery.__init__ = lambda self: None
    _disc.InstrumentDiscovery.scan = lambda self, verbose=True: devices or {}
    from lab_instruments.repl import InstrumentRepl

    repl = InstrumentRepl()
    repl._scan_thread.join(timeout=5.0)
    repl._scan_done.wait(timeout=5.0)
    repl.devices = devices or {}
    return repl


def _store(repl, label, value, unit="V", source="test"):
    """Directly inject a measurement entry via the MeasurementStore."""
    repl.ctx.measurements.record(label, value, unit, source)


@pytest.fixture
def repl():
    return make_repl()


# ---------------------------------------------------------------------------
# TestCalcChainedOperations
# ---------------------------------------------------------------------------


class TestCalcChainedOperations:
    def test_chain_abc_values(self, repl):
        repl.onecmd("calc a = 5 * 2")
        repl.onecmd("calc b = a + 3")
        repl.onecmd("calc c = a * b")
        assert repl.ctx.script_vars["a"] == 10
        assert repl.ctx.script_vars["b"] == 13
        assert repl.ctx.script_vars["c"] == 130

    def test_chain_intermediate_measurement_stored(self, repl):
        repl.onecmd("calc a = 5 * 2")
        repl.onecmd("calc b = a + 3")
        assert repl.ctx.measurements.get_by_label("a")["value"] == 10
        assert repl.ctx.measurements.get_by_label("b")["value"] == 13

    def test_chain_with_unit_each_step(self, repl, capsys):
        repl.onecmd("calc v = 3.3 unit=V")
        repl.onecmd("calc i = 0.1 unit=A")
        repl.onecmd("calc p = v * i unit=W")
        capsys.readouterr()
        assert abs(repl.ctx.script_vars["p"] - 0.33) < 1e-10
        assert repl.ctx.measurements.get_by_label("p")["unit"] == "W"

    def test_chain_units_preserved_per_step(self, repl):
        repl.onecmd("calc v = 5.0 unit=V")
        repl.onecmd("calc i = 2.0 unit=A")
        assert repl.ctx.measurements.get_by_label("v")["unit"] == "V"
        assert repl.ctx.measurements.get_by_label("i")["unit"] == "A"

    def test_last_references_most_recent_calc(self, repl):
        repl.onecmd("calc x = 7")
        repl.onecmd("calc y = last + 1")
        assert repl.ctx.script_vars["y"] == 8

    def test_last_updated_after_each_calc(self, repl):
        repl.onecmd("calc x = 10")
        repl.onecmd("calc y = last * 2")
        repl.onecmd("calc z = last + 5")
        # after y=20, last=20, so z = 20 + 5 = 25
        assert repl.ctx.script_vars["z"] == 25

    def test_long_expression_chain(self, repl):
        repl.onecmd("calc a = 2")
        repl.onecmd("calc b = 3")
        repl.onecmd("calc c = 4")
        repl.onecmd("calc d = 5")
        repl.onecmd("calc e = 2")
        repl.onecmd("calc result = (a + b) * (c - d) / e")
        # (2+3) * (4-5) / 2 = 5 * -1 / 2 = -2.5
        assert repl.ctx.script_vars["result"] == pytest.approx(-2.5)

    def test_chain_five_steps(self, repl):
        repl.onecmd("calc s1 = 1")
        repl.onecmd("calc s2 = s1 + 1")
        repl.onecmd("calc s3 = s2 + 1")
        repl.onecmd("calc s4 = s3 + 1")
        repl.onecmd("calc s5 = s4 + 1")
        assert repl.ctx.script_vars["s5"] == 5

    def test_chain_overwrite_label(self, repl):
        repl.onecmd("calc x = 10")
        repl.onecmd("calc x = x + 1")
        # get_by_label returns the last entry with that label
        entry = repl.ctx.measurements.get_by_label("x")
        assert entry["value"] == 11

    def test_chain_result_in_script_vars(self, repl):
        repl.onecmd("calc alpha = 100")
        repl.onecmd("calc beta = alpha / 4")
        assert "alpha" in repl.ctx.script_vars
        assert "beta" in repl.ctx.script_vars
        assert repl.ctx.script_vars["beta"] == 25.0


# ---------------------------------------------------------------------------
# TestCalcWithAllOperators
# ---------------------------------------------------------------------------


class TestCalcWithAllOperators:
    def test_addition(self, repl):
        repl.onecmd("calc r = 3 + 4")
        assert repl.ctx.script_vars["r"] == 7

    def test_subtraction(self, repl):
        repl.onecmd("calc r = 10 - 6")
        assert repl.ctx.script_vars["r"] == 4

    def test_multiplication(self, repl):
        repl.onecmd("calc r = 6 * 7")
        assert repl.ctx.script_vars["r"] == 42

    def test_division(self, repl):
        repl.onecmd("calc r = 9 / 4")
        assert repl.ctx.script_vars["r"] == pytest.approx(2.25)

    def test_floor_division(self, repl):
        repl.onecmd("calc r = 9 // 4")
        assert repl.ctx.script_vars["r"] == 2

    def test_modulo(self, repl):
        repl.onecmd("calc r = 10 % 3")
        assert repl.ctx.script_vars["r"] == 1

    def test_exponentiation(self, repl):
        repl.onecmd("calc r = 2 ** 8")
        assert repl.ctx.script_vars["r"] == 256

    def test_sqrt(self, repl):
        repl.onecmd("calc r = sqrt(144)")
        assert repl.ctx.script_vars["r"] == pytest.approx(12.0)

    def test_sin_pi_over_2(self, repl):
        repl.onecmd("calc r = sin(pi / 2)")
        assert repl.ctx.script_vars["r"] == pytest.approx(1.0)

    def test_cos_zero(self, repl):
        repl.onecmd("calc r = cos(0)")
        assert repl.ctx.script_vars["r"] == pytest.approx(1.0)

    def test_log10(self, repl):
        repl.onecmd("calc r = log10(1000)")
        assert repl.ctx.script_vars["r"] == pytest.approx(3.0)

    def test_bitwise_and(self, repl):
        repl.onecmd("calc r = 0xFF & 0x0F")
        assert repl.ctx.script_vars["r"] == 0x0F

    def test_bitwise_or(self, repl):
        repl.onecmd("calc r = 0xF0 | 0x0F")
        assert repl.ctx.script_vars["r"] == 0xFF

    def test_comparison_greater_than_true(self, repl):
        repl.onecmd("calc a = 10")
        repl.onecmd("calc b = 5")
        repl.onecmd("calc flag = a > b")
        assert repl.ctx.script_vars["flag"] is True

    def test_comparison_less_than_false(self, repl):
        repl.onecmd("calc a = 3")
        repl.onecmd("calc b = 7")
        repl.onecmd("calc flag = a > b")
        assert repl.ctx.script_vars["flag"] is False

    def test_negative_unary(self, repl):
        repl.onecmd("calc r = -5 + 10")
        assert repl.ctx.script_vars["r"] == 5

    def test_abs_function(self, repl):
        repl.onecmd("calc r = abs(-42)")
        assert repl.ctx.script_vars["r"] == 42

    def test_round_function(self, repl):
        repl.onecmd("calc r = round(3.7)")
        assert repl.ctx.script_vars["r"] == 4

    def test_exp_function(self, repl):
        repl.onecmd("calc r = exp(0)")
        assert repl.ctx.script_vars["r"] == pytest.approx(1.0)

    def test_degrees_radians(self, repl):
        repl.onecmd("calc r = degrees(pi)")
        assert repl.ctx.script_vars["r"] == pytest.approx(180.0)


# ---------------------------------------------------------------------------
# TestCalcWithUnits
# ---------------------------------------------------------------------------


class TestCalcWithUnits:
    def test_unit_V(self, repl):
        repl.onecmd("calc vout = 3.3 unit=V")
        assert repl.ctx.measurements.get_by_label("vout")["unit"] == "V"

    def test_unit_A(self, repl):
        repl.onecmd("calc iout = 0.5 unit=A")
        assert repl.ctx.measurements.get_by_label("iout")["unit"] == "A"

    def test_unit_W(self, repl):
        repl.onecmd("calc power = 1.65 unit=W")
        assert repl.ctx.measurements.get_by_label("power")["unit"] == "W"

    def test_unit_ohm(self, repl):
        repl.onecmd("calc rload = 10 unit=ohm")
        assert repl.ctx.measurements.get_by_label("rload")["unit"] == "ohm"

    def test_unit_dB(self, repl):
        repl.onecmd("calc gain = 20 unit=dB")
        assert repl.ctx.measurements.get_by_label("gain")["unit"] == "dB"

    def test_unit_Hz(self, repl):
        repl.onecmd("calc freq = 1000 unit=Hz")
        assert repl.ctx.measurements.get_by_label("freq")["unit"] == "Hz"

    def test_unit_pF(self, repl):
        repl.onecmd("calc cap = 100 unit=pF")
        assert repl.ctx.measurements.get_by_label("cap")["unit"] == "pF"

    def test_unit_uF(self, repl):
        repl.onecmd("calc cap = 10 unit=uF")
        assert repl.ctx.measurements.get_by_label("cap")["unit"] == "uF"

    def test_unit_mA(self, repl):
        repl.onecmd("calc i = 50 unit=mA")
        assert repl.ctx.measurements.get_by_label("i")["unit"] == "mA"

    def test_unit_uA(self, repl):
        repl.onecmd("calc i = 500 unit=uA")
        assert repl.ctx.measurements.get_by_label("i")["unit"] == "uA"

    def test_unit_degrees_C(self, repl):
        repl.onecmd("calc temp = 25 unit=degreesC")
        assert repl.ctx.measurements.get_by_label("temp")["unit"] == "degreesC"

    def test_no_unit_stored_as_empty(self, repl):
        repl.onecmd("calc x = 42")
        assert repl.ctx.measurements.get_by_label("x")["unit"] == ""

    def test_multiple_units_same_session(self, repl):
        repl.onecmd("calc v = 5.0 unit=V")
        repl.onecmd("calc i = 0.2 unit=A")
        repl.onecmd("calc p = v * i unit=W")
        assert repl.ctx.measurements.get_by_label("v")["unit"] == "V"
        assert repl.ctx.measurements.get_by_label("i")["unit"] == "A"
        assert repl.ctx.measurements.get_by_label("p")["unit"] == "W"

    def test_unit_stored_in_script_vars_not_included(self, repl):
        repl.onecmd("calc vout = 3.3 unit=V")
        # script_vars holds the numeric result, not the unit
        assert isinstance(repl.ctx.script_vars["vout"], (int, float))

    def test_unit_value_correct_with_unit_flag(self, repl):
        repl.onecmd("calc gain_db = 20 * log10(10) unit=dB")
        assert repl.ctx.script_vars["gain_db"] == pytest.approx(20.0)


# ---------------------------------------------------------------------------
# TestLogSystem
# ---------------------------------------------------------------------------


class TestLogSystem:
    def test_log_print_no_data(self, repl, capsys):
        repl.onecmd("log print")
        out = capsys.readouterr().out
        assert "No measurements" in out

    def test_log_print_after_single_calc(self, repl, capsys):
        repl.onecmd("calc vout = 5.0 unit=V")
        capsys.readouterr()
        repl.onecmd("log print")
        out = capsys.readouterr().out
        assert "vout" in out

    def test_log_print_after_multiple_calcs(self, repl, capsys):
        repl.onecmd("calc a = 1 unit=V")
        repl.onecmd("calc b = 2 unit=A")
        repl.onecmd("calc c = 3 unit=W")
        capsys.readouterr()
        repl.onecmd("log print")
        out = capsys.readouterr().out
        assert "a" in out
        assert "b" in out
        assert "c" in out

    def test_log_clear_empties_measurements(self, repl):
        repl.onecmd("calc x = 10")
        repl.onecmd("calc y = 20")
        assert len(repl.ctx.measurements) == 2
        repl.onecmd("log clear")
        assert len(repl.ctx.measurements) == 0

    def test_log_clear_output_message(self, repl, capsys):
        repl.onecmd("calc x = 1")
        capsys.readouterr()
        repl.onecmd("log clear")
        out = capsys.readouterr().out
        assert "clear" in out.lower()

    def test_log_entries_maintain_insertion_order(self, repl):
        repl.onecmd("calc first = 1")
        repl.onecmd("calc second = 2")
        repl.onecmd("calc third = 3")
        labels = [e["label"] for e in repl.ctx.measurements.entries]
        assert labels == ["first", "second", "third"]

    def test_get_by_label_correct_entry(self, repl):
        repl.onecmd("calc alpha = 100 unit=V")
        repl.onecmd("calc beta = 200 unit=A")
        entry = repl.ctx.measurements.get_by_label("alpha")
        assert entry is not None
        assert entry["value"] == 100
        assert entry["unit"] == "V"

    def test_get_last_returns_most_recent(self, repl):
        repl.onecmd("calc x = 1")
        repl.onecmd("calc y = 2")
        repl.onecmd("calc z = 3")
        last = repl.ctx.measurements.get_last()
        assert last["label"] == "z"
        assert last["value"] == 3

    def test_log_print_shows_source_calc(self, repl, capsys):
        repl.onecmd("calc myval = 42 unit=V")
        capsys.readouterr()
        repl.onecmd("log print")
        out = capsys.readouterr().out
        assert "calc" in out

    def test_log_clear_then_new_calcs(self, repl):
        repl.onecmd("calc x = 5")
        repl.onecmd("log clear")
        repl.onecmd("calc y = 10")
        assert len(repl.ctx.measurements) == 1
        assert repl.ctx.measurements.get_by_label("y")["value"] == 10

    def test_log_clear_does_not_affect_script_vars(self, repl):
        repl.onecmd("calc x = 99")
        repl.onecmd("log clear")
        # script_vars retains the value even after log clear
        assert repl.ctx.script_vars.get("x") == 99


# ---------------------------------------------------------------------------
# TestCalcWithMeasurementRefs
# ---------------------------------------------------------------------------


class TestCalcWithMeasurementRefs:
    def test_calc_uses_script_var(self, repl):
        repl.ctx.script_vars["base"] = 7
        repl.onecmd("calc doubled = base * 2")
        assert repl.ctx.script_vars["doubled"] == 14

    def test_calc_uses_curly_brace_measurement_ref(self, repl):
        _store(repl, "vout", 5.0, "V")
        repl.onecmd("calc scaled = {vout} * 2 unit=V")
        assert repl.ctx.script_vars["scaled"] == pytest.approx(10.0)

    def test_last_after_variable_assignment_via_calc(self, repl):
        repl.onecmd("calc x = 42")
        # 'last' should resolve to x's value
        repl.onecmd("calc y = last")
        assert repl.ctx.script_vars["y"] == 42

    def test_last_not_affected_by_script_var_set_directly(self, repl):
        repl.ctx.script_vars["z"] = 999
        # No calc has been run, so last should be 0 (no measurement)
        repl.onecmd("calc r = last")
        assert repl.ctx.script_vars["r"] == 0

    def test_multiple_labels_referenceable(self, repl):
        repl.onecmd("calc v1 = 3.0")
        repl.onecmd("calc v2 = 4.0")
        repl.onecmd("calc hyp = sqrt(v1 ** 2 + v2 ** 2)")
        assert repl.ctx.script_vars["hyp"] == pytest.approx(5.0)

    def test_overwrite_label_updates_measurement(self, repl):
        repl.onecmd("calc val = 10 unit=V")
        repl.onecmd("calc val = 20 unit=V")
        entry = repl.ctx.measurements.get_by_label("val")
        assert entry["value"] == 20

    def test_overwrite_label_updates_script_vars(self, repl):
        repl.onecmd("calc val = 10")
        repl.onecmd("calc val = 20")
        assert repl.ctx.script_vars["val"] == 20

    def test_calc_references_injected_measurement(self, repl):
        _store(repl, "vsense", 2.5, "V")
        repl.onecmd("calc error_pct = (vsense - 2.5) / 2.5 * 100 unit=%")
        assert repl.ctx.script_vars["error_pct"] == pytest.approx(0.0)

    def test_calc_bad_ref_still_runs_but_outputs_error(self, repl, capsys):
        repl.onecmd("calc r = {nonexistent_label_xyz} + 1")
        out = capsys.readouterr().out
        # Should produce an error, not silently succeed with wrong value
        assert out != ""

    def test_last_keyword_chained_three_times(self, repl):
        repl.onecmd("calc a = 5")
        repl.onecmd("calc b = last + 5")  # b = 10
        repl.onecmd("calc c = last + 5")  # c = 15
        assert repl.ctx.script_vars["c"] == 15


# ---------------------------------------------------------------------------
# TestArithmeticPrecision
# ---------------------------------------------------------------------------


class TestArithmeticPrecision:
    def test_float_point_01_plus_02(self, repl):
        repl.onecmd("calc r = 0.1 + 0.2")
        # Python float arithmetic: 0.1 + 0.2 = 0.30000000000000004
        assert repl.ctx.script_vars["r"] == pytest.approx(0.3, rel=1e-9)

    def test_very_small_numbers(self, repl):
        repl.onecmd("calc r = 1e-15 * 1e-15")
        assert repl.ctx.script_vars["r"] == pytest.approx(1e-30, rel=1e-9)

    def test_very_large_numbers(self, repl):
        repl.onecmd("calc r = 1e15 + 1")
        assert repl.ctx.script_vars["r"] == pytest.approx(1e15 + 1, rel=1e-12)

    def test_integer_large_value(self, repl):
        # Python handles big integers natively
        repl.onecmd("calc r = 2 ** 62")
        assert repl.ctx.script_vars["r"] == 2**62

    def test_division_precision(self, repl):
        repl.onecmd("calc r = 1 / 3 * 3")
        assert repl.ctx.script_vars["r"] == pytest.approx(1.0, rel=1e-10)

    def test_division_by_zero_gives_nan(self, repl, capsys):
        repl.onecmd("calc r = 1 / 0")
        capsys.readouterr()
        val = repl.ctx.script_vars.get("r")
        # safe_eval returns float('nan') on ZeroDivisionError
        assert val is not None and math.isnan(float(val))

    def test_sqrt_of_two_precision(self, repl):
        repl.onecmd("calc r = sqrt(2)")
        assert repl.ctx.script_vars["r"] == pytest.approx(math.sqrt(2), rel=1e-12)

    def test_sin_of_pi(self, repl):
        repl.onecmd("calc r = sin(pi)")
        # sin(pi) is not exactly 0 due to floating point
        assert abs(repl.ctx.script_vars["r"]) < 1e-15

    def test_negative_exponent(self, repl):
        repl.onecmd("calc r = 10 ** -3")
        assert repl.ctx.script_vars["r"] == pytest.approx(0.001, rel=1e-12)

    def test_floor_ceil_precision(self, repl):
        repl.onecmd("calc lo = floor(2.9)")
        repl.onecmd("calc hi = ceil(2.1)")
        assert repl.ctx.script_vars["lo"] == 2
        assert repl.ctx.script_vars["hi"] == 3

    def test_pi_constant(self, repl):
        repl.onecmd("calc r = pi")
        assert repl.ctx.script_vars["r"] == pytest.approx(math.pi, rel=1e-12)

    def test_e_constant(self, repl):
        repl.onecmd("calc r = e")
        assert repl.ctx.script_vars["r"] == pytest.approx(math.e, rel=1e-12)

    def test_hypot(self, repl):
        repl.onecmd("calc r = hypot(3, 4)")
        assert repl.ctx.script_vars["r"] == pytest.approx(5.0)

    def test_log_natural(self, repl):
        repl.onecmd("calc r = log(e)")
        assert repl.ctx.script_vars["r"] == pytest.approx(1.0)

    def test_log2(self, repl):
        repl.onecmd("calc r = log2(1024)")
        assert repl.ctx.script_vars["r"] == pytest.approx(10.0)
