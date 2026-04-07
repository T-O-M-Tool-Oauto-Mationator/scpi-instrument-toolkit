"""Tests for cross-source variable arithmetic.

Verifies that variables from any source (plain assignment, instrument read,
calc) can be used in arithmetic expressions with all supported operators.
"""

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


def make_mock_repl():
    from mock_instruments import get_mock_devices

    return make_repl(get_mock_devices(verbose=False))


@pytest.fixture
def repl():
    return make_repl()


@pytest.fixture
def mock_repl():
    return make_mock_repl()


# ---------------------------------------------------------------------------
# Basic arithmetic with plain variables
# ---------------------------------------------------------------------------


class TestBasicArithmetic:
    def test_addition(self, repl):
        repl.onecmd("x = 12")
        repl.onecmd("y = 3")
        repl.onecmd("z = x + y")
        assert float(repl.ctx.script_vars["z"]) == 15.0

    def test_subtraction(self, repl):
        repl.onecmd("a = 10")
        repl.onecmd("b = 4")
        repl.onecmd("c = a - b")
        assert float(repl.ctx.script_vars["c"]) == 6.0

    def test_multiplication(self, repl):
        repl.onecmd("p = 7")
        repl.onecmd("q = 6")
        repl.onecmd("r = p * q")
        assert float(repl.ctx.script_vars["r"]) == 42.0

    def test_division(self, repl):
        repl.onecmd("a = 100")
        repl.onecmd("b = 4")
        repl.onecmd("c = a / b")
        assert float(repl.ctx.script_vars["c"]) == 25.0

    def test_floor_division(self, repl):
        repl.onecmd("a = 7")
        repl.onecmd("b = 2")
        repl.onecmd("c = a // b")
        assert float(repl.ctx.script_vars["c"]) == 3.0

    def test_modulo(self, repl):
        repl.onecmd("a = 17")
        repl.onecmd("b = 5")
        repl.onecmd("c = a % b")
        assert float(repl.ctx.script_vars["c"]) == 2.0

    def test_power(self, repl):
        repl.onecmd("a = 2")
        repl.onecmd("b = 10")
        repl.onecmd("c = a ** b")
        assert float(repl.ctx.script_vars["c"]) == 1024.0

    def test_caret_as_power(self, repl):
        repl.onecmd("a = 3")
        repl.onecmd("c = a ^ 2")
        assert float(repl.ctx.script_vars["c"]) == 9.0

    def test_parentheses(self, repl):
        repl.onecmd("a = 2")
        repl.onecmd("b = 3")
        repl.onecmd("c = 4")
        repl.onecmd("d = (a + b) * c")
        assert float(repl.ctx.script_vars["d"]) == 20.0

    def test_nested_parentheses(self, repl):
        repl.onecmd("x = 1")
        repl.onecmd("y = 2")
        repl.onecmd("z = 3")
        repl.onecmd("r = ((x + y) * z) ** 2")
        assert float(repl.ctx.script_vars["r"]) == 81.0

    def test_unary_negative(self, repl):
        repl.onecmd("a = 5")
        repl.onecmd("b = -a")
        assert float(repl.ctx.script_vars["b"]) == -5.0

    def test_builtin_functions(self, repl):
        repl.onecmd("a = -7.5")
        repl.onecmd("b = abs(a)")
        assert float(repl.ctx.script_vars["b"]) == 7.5

        repl.onecmd("c = round(3.14159, 2)")
        assert float(repl.ctx.script_vars["c"]) == 3.14

        repl.onecmd("d = max(10, 20)")
        assert float(repl.ctx.script_vars["d"]) == 20.0

        repl.onecmd("e = min(10, 20)")
        assert float(repl.ctx.script_vars["e"]) == 10.0


# ---------------------------------------------------------------------------
# Chained arithmetic (result of one used in the next)
# ---------------------------------------------------------------------------


class TestChainedArithmetic:
    def test_chain_five_steps(self, repl):
        repl.onecmd("p = 2")
        repl.onecmd("q = 3")
        repl.onecmd("r = p * q")       # 6
        repl.onecmd("s = r + 1")       # 7
        repl.onecmd("t = s * 2")       # 14
        assert float(repl.ctx.script_vars["r"]) == 6.0
        assert float(repl.ctx.script_vars["s"]) == 7.0
        assert float(repl.ctx.script_vars["t"]) == 14.0


# ---------------------------------------------------------------------------
# Cross-source: instrument read + plain var in arithmetic
# ---------------------------------------------------------------------------


class TestCrossSourceArithmetic:
    def test_instrument_read_plus_constant(self, mock_repl):
        mock_repl.onecmd("psu chan 1 on")
        mock_repl.onecmd("v = psu meas v unit=V")
        mock_repl.onecmd("offset = 1.0")
        mock_repl.onecmd("adjusted = v + offset")
        v = float(mock_repl.ctx.script_vars["v"])
        adjusted = float(mock_repl.ctx.script_vars["adjusted"])
        assert abs(adjusted - (v + 1.0)) < 1e-9

    def test_two_instrument_reads_arithmetic(self, mock_repl):
        mock_repl.onecmd("psu chan 1 on")
        mock_repl.onecmd("voltage = psu meas v unit=V")
        mock_repl.onecmd("current = psu meas i unit=A")
        mock_repl.onecmd("power = voltage * current")
        v = float(mock_repl.ctx.script_vars["voltage"])
        i = float(mock_repl.ctx.script_vars["current"])
        p = float(mock_repl.ctx.script_vars["power"])
        assert abs(p - v * i) < 1e-9

    def test_dmm_read_in_expression(self, mock_repl):
        mock_repl.onecmd("dmm config vdc")
        mock_repl.onecmd("reading = dmm meas unit=V")
        mock_repl.onecmd("target = 5.0")
        mock_repl.onecmd("error = reading - target")
        reading = float(mock_repl.ctx.script_vars["reading"])
        error = float(mock_repl.ctx.script_vars["error"])
        assert abs(error - (reading - 5.0)) < 1e-9

    def test_mixed_instrument_and_plain(self, mock_repl):
        mock_repl.onecmd("base = 100")
        mock_repl.onecmd("reading = dmm meas unit=V")
        mock_repl.onecmd("result = base + reading")
        base = float(mock_repl.ctx.script_vars["base"])
        reading = float(mock_repl.ctx.script_vars["reading"])
        result = float(mock_repl.ctx.script_vars["result"])
        assert abs(result - (base + reading)) < 1e-9


# ---------------------------------------------------------------------------
# Measurements are recorded correctly
# ---------------------------------------------------------------------------


class TestMeasurementRecording:
    def test_instrument_read_records_measurement(self, mock_repl):
        mock_repl.onecmd("psu chan 1 on")
        mock_repl.onecmd("my_voltage = psu meas v unit=V")
        entry = mock_repl.ctx.measurements.get_by_label("my_voltage")
        assert entry is not None
        assert entry["unit"] == "V"
        assert isinstance(entry["value"], float)
        assert "time" in entry

    def test_plain_assignment_not_in_measurements(self, repl):
        repl.onecmd("x = 42")
        entry = repl.ctx.measurements.get_by_label("x")
        assert entry is None

    def test_arithmetic_result_not_in_measurements(self, repl):
        repl.onecmd("a = 10")
        repl.onecmd("b = 20")
        repl.onecmd("c = a + b")
        entry = repl.ctx.measurements.get_by_label("c")
        assert entry is None


# ---------------------------------------------------------------------------
# safe_eval operator coverage
# ---------------------------------------------------------------------------


class TestSafeEvalOperators:
    def test_floor_div(self, repl):
        repl.onecmd("x = 10 // 3")
        assert float(repl.ctx.script_vars["x"]) == 3.0

    def test_power_double_star(self, repl):
        repl.onecmd("x = 2 ** 8")
        assert float(repl.ctx.script_vars["x"]) == 256.0

    def test_caret_power(self, repl):
        repl.onecmd("x = 2 ^ 8")
        assert float(repl.ctx.script_vars["x"]) == 256.0

    def test_modulo(self, repl):
        repl.onecmd("x = 10 % 3")
        assert float(repl.ctx.script_vars["x"]) == 1.0

    def test_complex_expression(self, repl):
        repl.onecmd("x = (10 + 5) * 2 / 3")
        assert abs(float(repl.ctx.script_vars["x"]) - 10.0) < 1e-9

    def test_int_and_float_functions(self, repl):
        repl.onecmd("x = int(3.7)")
        assert repl.ctx.script_vars["x"] == "3"

        repl.onecmd("y = float(42)")
        assert float(repl.ctx.script_vars["y"]) == 42.0
