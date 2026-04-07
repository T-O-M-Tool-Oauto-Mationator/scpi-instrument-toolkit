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
        repl.onecmd("r = p * q")  # 6
        repl.onecmd("s = r + 1")  # 7
        repl.onecmd("t = s * 2")  # 14
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


# ---------------------------------------------------------------------------
# String functions: str(), hex(), bin(), oct(), ord(), chr()
# ---------------------------------------------------------------------------


class TestStringFunctions:
    def test_str_of_number(self, repl):
        repl.onecmd("x = str(42)")
        assert repl.ctx.script_vars["x"] == "42"

    def test_str_of_float(self, repl):
        repl.onecmd("x = str(3.14)")
        assert repl.ctx.script_vars["x"] == "3.14"

    def test_hex_conversion(self, repl):
        repl.onecmd("x = hex(255)")
        assert repl.ctx.script_vars["x"] == "0xff"

    def test_hex_of_zero(self, repl):
        repl.onecmd("x = hex(0)")
        assert repl.ctx.script_vars["x"] == "0x0"

    def test_bin_conversion(self, repl):
        repl.onecmd("x = bin(10)")
        assert repl.ctx.script_vars["x"] == "0b1010"

    def test_oct_conversion(self, repl):
        repl.onecmd("x = oct(8)")
        assert repl.ctx.script_vars["x"] == "0o10"

    def test_ord_conversion(self, repl):
        repl.onecmd("x = ord('A')")
        assert repl.ctx.script_vars["x"] == "65"

    def test_chr_conversion(self, repl):
        repl.onecmd("x = chr(65)")
        assert repl.ctx.script_vars["x"] == "A"

    def test_bool_true(self, repl):
        repl.onecmd("x = bool(1)")
        assert repl.ctx.script_vars["x"] == "True"

    def test_bool_false(self, repl):
        repl.onecmd("x = bool(0)")
        assert repl.ctx.script_vars["x"] == "False"


# ---------------------------------------------------------------------------
# Math functions: sqrt, sin, cos, log, etc, pi, e
# ---------------------------------------------------------------------------


class TestMathFunctions:
    def test_sqrt(self, repl):
        repl.onecmd("x = sqrt(16)")
        assert float(repl.ctx.script_vars["x"]) == 4.0

    def test_sqrt_non_perfect(self, repl):
        repl.onecmd("x = sqrt(2)")
        assert abs(float(repl.ctx.script_vars["x"]) - 1.41421356) < 1e-6

    def test_sin_zero(self, repl):
        repl.onecmd("x = sin(0)")
        assert float(repl.ctx.script_vars["x"]) == 0.0

    def test_cos_zero(self, repl):
        repl.onecmd("x = cos(0)")
        assert float(repl.ctx.script_vars["x"]) == 1.0

    def test_sin_pi_half(self, repl):
        repl.onecmd("x = sin(pi / 2)")
        assert abs(float(repl.ctx.script_vars["x"]) - 1.0) < 1e-9

    def test_cos_pi(self, repl):
        repl.onecmd("x = cos(pi)")
        assert abs(float(repl.ctx.script_vars["x"]) - (-1.0)) < 1e-9

    def test_tan(self, repl):
        repl.onecmd("x = tan(0)")
        assert float(repl.ctx.script_vars["x"]) == 0.0

    def test_asin(self, repl):
        repl.onecmd("x = asin(1)")
        import math

        assert abs(float(repl.ctx.script_vars["x"]) - math.pi / 2) < 1e-9

    def test_acos(self, repl):
        repl.onecmd("x = acos(1)")
        assert float(repl.ctx.script_vars["x"]) == 0.0

    def test_atan(self, repl):
        repl.onecmd("x = atan(0)")
        assert float(repl.ctx.script_vars["x"]) == 0.0

    def test_atan2(self, repl):
        repl.onecmd("x = atan2(1, 1)")
        import math

        assert abs(float(repl.ctx.script_vars["x"]) - math.pi / 4) < 1e-9

    def test_log_natural(self, repl):
        repl.onecmd("x = log(e)")
        assert abs(float(repl.ctx.script_vars["x"]) - 1.0) < 1e-9

    def test_log2(self, repl):
        repl.onecmd("x = log2(8)")
        assert float(repl.ctx.script_vars["x"]) == 3.0

    def test_log10(self, repl):
        repl.onecmd("x = log10(1000)")
        assert float(repl.ctx.script_vars["x"]) == 3.0

    def test_exp(self, repl):
        repl.onecmd("x = exp(0)")
        assert float(repl.ctx.script_vars["x"]) == 1.0

    def test_ceil(self, repl):
        repl.onecmd("x = ceil(3.2)")
        assert float(repl.ctx.script_vars["x"]) == 4.0

    def test_floor(self, repl):
        repl.onecmd("x = floor(3.9)")
        assert float(repl.ctx.script_vars["x"]) == 3.0

    def test_hypot(self, repl):
        repl.onecmd("x = hypot(3, 4)")
        assert float(repl.ctx.script_vars["x"]) == 5.0

    def test_degrees(self, repl):
        repl.onecmd("x = degrees(pi)")
        assert abs(float(repl.ctx.script_vars["x"]) - 180.0) < 1e-9

    def test_radians(self, repl):
        import math

        repl.onecmd("x = radians(180)")
        assert abs(float(repl.ctx.script_vars["x"]) - math.pi) < 1e-9

    def test_pi_constant(self, repl):
        import math

        repl.onecmd("x = pi")
        assert abs(float(repl.ctx.script_vars["x"]) - math.pi) < 1e-9

    def test_e_constant(self, repl):
        import math

        repl.onecmd("x = e")
        assert abs(float(repl.ctx.script_vars["x"]) - math.e) < 1e-9

    def test_combined_math(self, repl):
        """sqrt(sin(x)**2 + cos(x)**2) should be 1.0 for any x."""
        repl.onecmd("x = sqrt(sin(1) ** 2 + cos(1) ** 2)")
        assert abs(float(repl.ctx.script_vars["x"]) - 1.0) < 1e-9


# ---------------------------------------------------------------------------
# Comparisons: ==, !=, <, <=, >, >=
# ---------------------------------------------------------------------------


class TestComparisons:
    def test_equal_true(self, repl):
        repl.onecmd("x = 5 == 5")
        assert repl.ctx.script_vars["x"] == "True"

    def test_equal_false(self, repl):
        repl.onecmd("x = 5 == 6")
        assert repl.ctx.script_vars["x"] == "False"

    def test_not_equal_true(self, repl):
        repl.onecmd("x = 5 != 6")
        assert repl.ctx.script_vars["x"] == "True"

    def test_not_equal_false(self, repl):
        repl.onecmd("x = 5 != 5")
        assert repl.ctx.script_vars["x"] == "False"

    def test_less_than_true(self, repl):
        repl.onecmd("x = 3 < 5")
        assert repl.ctx.script_vars["x"] == "True"

    def test_less_than_false(self, repl):
        repl.onecmd("x = 5 < 3")
        assert repl.ctx.script_vars["x"] == "False"

    def test_less_equal_true(self, repl):
        repl.onecmd("x = 5 <= 5")
        assert repl.ctx.script_vars["x"] == "True"

    def test_greater_than_true(self, repl):
        repl.onecmd("x = 7 > 3")
        assert repl.ctx.script_vars["x"] == "True"

    def test_greater_equal_true(self, repl):
        repl.onecmd("x = 7 >= 7")
        assert repl.ctx.script_vars["x"] == "True"

    def test_chained_comparison(self, repl):
        repl.onecmd("x = 1 < 2 < 3")
        assert repl.ctx.script_vars["x"] == "True"

    def test_comparison_with_vars(self, repl):
        repl.onecmd("a = 10")
        repl.onecmd("b = 20")
        repl.onecmd("x = a < b")
        assert repl.ctx.script_vars["x"] == "True"


# ---------------------------------------------------------------------------
# Boolean operators: and, or, not
# ---------------------------------------------------------------------------


class TestBooleanOps:
    def test_and_true(self, repl):
        repl.onecmd("x = True and True")
        assert repl.ctx.script_vars["x"] == "True"

    def test_and_false(self, repl):
        repl.onecmd("x = True and False")
        assert repl.ctx.script_vars["x"] == "False"

    def test_or_true(self, repl):
        repl.onecmd("x = False or True")
        assert repl.ctx.script_vars["x"] == "True"

    def test_or_false(self, repl):
        repl.onecmd("x = False or False")
        assert repl.ctx.script_vars["x"] == "False"

    def test_not_true(self, repl):
        repl.onecmd("x = not False")
        assert repl.ctx.script_vars["x"] == "True"

    def test_not_false(self, repl):
        repl.onecmd("x = not True")
        assert repl.ctx.script_vars["x"] == "False"

    def test_combined_boolean(self, repl):
        repl.onecmd("x = (True and False) or True")
        assert repl.ctx.script_vars["x"] == "True"

    def test_boolean_with_comparisons(self, repl):
        repl.onecmd("a = 5")
        repl.onecmd("b = 10")
        repl.onecmd("x = a < b and b > 0")
        assert repl.ctx.script_vars["x"] == "True"


# ---------------------------------------------------------------------------
# Ternary: a if cond else b
# ---------------------------------------------------------------------------


class TestTernary:
    def test_ternary_true_branch(self, repl):
        repl.onecmd("x = 10 if True else 20")
        assert float(repl.ctx.script_vars["x"]) == 10.0

    def test_ternary_false_branch(self, repl):
        repl.onecmd("x = 10 if False else 20")
        assert float(repl.ctx.script_vars["x"]) == 20.0

    def test_ternary_with_comparison(self, repl):
        repl.onecmd("a = 5")
        repl.onecmd("x = 100 if a > 3 else 0")
        assert float(repl.ctx.script_vars["x"]) == 100.0

    def test_ternary_with_comparison_false(self, repl):
        repl.onecmd("a = 1")
        repl.onecmd("x = 100 if a > 3 else 0")
        assert float(repl.ctx.script_vars["x"]) == 0.0

    def test_ternary_with_expressions(self, repl):
        repl.onecmd("a = 7")
        repl.onecmd("x = a * 2 if a > 5 else a * 3")
        assert float(repl.ctx.script_vars["x"]) == 14.0


# ---------------------------------------------------------------------------
# Containers: [list], (tuple), len(), sum()
# ---------------------------------------------------------------------------


class TestContainers:
    def test_list_literal(self, repl):
        repl.onecmd("x = [1, 2, 3]")
        assert repl.ctx.script_vars["x"] == "[1, 2, 3]"

    def test_tuple_literal(self, repl):
        repl.onecmd("x = (1, 2)")
        assert repl.ctx.script_vars["x"] == "(1, 2)"

    def test_len_of_list(self, repl):
        repl.onecmd("x = len([10, 20, 30, 40])")
        assert repl.ctx.script_vars["x"] == "4"

    def test_sum_of_list(self, repl):
        repl.onecmd("x = sum([1, 2, 3, 4, 5])")
        assert repl.ctx.script_vars["x"] == "15"

    def test_min_of_list(self, repl):
        repl.onecmd("x = min([5, 3, 8, 1])")
        assert repl.ctx.script_vars["x"] == "1"

    def test_max_of_list(self, repl):
        repl.onecmd("x = max([5, 3, 8, 1])")
        assert repl.ctx.script_vars["x"] == "8"

    def test_subscript_list(self, repl):
        repl.onecmd("x = [10, 20, 30][1]")
        assert repl.ctx.script_vars["x"] == "20"

    def test_keyword_arg_round(self, repl):
        repl.onecmd("x = round(3.14159, ndigits=2)")
        assert float(repl.ctx.script_vars["x"]) == 3.14


# ---------------------------------------------------------------------------
# Bitwise operators: ~, |, &, <<, >>
# ---------------------------------------------------------------------------


class TestBitwiseOps:
    def test_bitwise_or(self, repl):
        repl.onecmd("x = 0b1010 | 0b0101")
        assert int(float(repl.ctx.script_vars["x"])) == 0b1111

    def test_bitwise_and(self, repl):
        repl.onecmd("x = 0b1111 & 0b1010")
        assert int(float(repl.ctx.script_vars["x"])) == 0b1010

    def test_left_shift(self, repl):
        repl.onecmd("x = 1 << 4")
        assert int(float(repl.ctx.script_vars["x"])) == 16

    def test_right_shift(self, repl):
        repl.onecmd("x = 16 >> 2")
        assert int(float(repl.ctx.script_vars["x"])) == 4

    def test_bitwise_invert(self, repl):
        repl.onecmd("x = ~0")
        assert int(float(repl.ctx.script_vars["x"])) == -1
