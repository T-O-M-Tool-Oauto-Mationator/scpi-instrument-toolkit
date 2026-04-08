"""Unit tests for safe_eval — the sandboxed expression evaluator in syntax.py."""

import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lab_instruments.repl.syntax import safe_eval


# ---------------------------------------------------------------------------
# Arithmetic operators
# ---------------------------------------------------------------------------


class TestArithmetic:
    def test_addition(self):
        assert safe_eval("1 + 2", {}) == 3

    def test_subtraction(self):
        assert safe_eval("10 - 4", {}) == 6

    def test_multiplication(self):
        assert safe_eval("3 * 7", {}) == 21

    def test_division(self):
        assert safe_eval("10 / 4", {}) == 2.5

    def test_floor_division(self):
        assert safe_eval("7 // 2", {}) == 3

    def test_modulo(self):
        assert safe_eval("10 % 3", {}) == 1

    def test_power(self):
        assert safe_eval("2 ** 8", {}) == 256

    def test_caret_as_power(self):
        # ^ is rewritten to **
        assert safe_eval("2 ^ 10", {}) == 1024

    def test_unary_neg(self):
        assert safe_eval("-5", {}) == -5

    def test_unary_pos(self):
        assert safe_eval("+3", {}) == 3

    def test_parentheses(self):
        assert safe_eval("(2 + 3) * 4", {}) == 20


# ---------------------------------------------------------------------------
# Comparisons
# ---------------------------------------------------------------------------


class TestComparisons:
    def test_less_than_true(self):
        assert safe_eval("3 < 5", {}) is True

    def test_less_than_false(self):
        assert safe_eval("5 < 3", {}) is False

    def test_less_equal(self):
        assert safe_eval("5 <= 5", {}) is True

    def test_greater_than(self):
        assert safe_eval("7 > 3", {}) is True

    def test_greater_equal(self):
        assert safe_eval("7 >= 8", {}) is False

    def test_equal_true(self):
        assert safe_eval("4 == 4", {}) is True

    def test_equal_false(self):
        assert safe_eval("4 == 5", {}) is False

    def test_not_equal_true(self):
        assert safe_eval("4 != 5", {}) is True

    def test_not_equal_false(self):
        assert safe_eval("4 != 4", {}) is False

    def test_chained(self):
        assert safe_eval("1 < 2 < 3", {}) is True

    def test_chained_false(self):
        assert safe_eval("1 < 2 < 1", {}) is False

    def test_with_var(self):
        assert safe_eval("x > 0", {"x": 5.0}) is True


# ---------------------------------------------------------------------------
# Boolean operators
# ---------------------------------------------------------------------------


class TestBooleanOps:
    def test_and_true(self):
        assert safe_eval("True and True", {}) is True

    def test_and_false(self):
        assert safe_eval("True and False", {}) is False

    def test_or_true(self):
        assert safe_eval("False or True", {}) is True

    def test_or_false(self):
        assert safe_eval("False or False", {}) is False

    def test_not_true(self):
        assert safe_eval("not False", {}) is True

    def test_not_false(self):
        assert safe_eval("not True", {}) is False

    def test_pipe_pipe_alias(self):
        # || should be treated as or
        result = safe_eval("False || True", {})
        assert result is True

    def test_ampersand_ampersand_alias(self):
        # && should be treated as and
        result = safe_eval("True && False", {})
        assert result is False

    def test_combined(self):
        assert safe_eval("(True and False) or True", {}) is True


# ---------------------------------------------------------------------------
# Bitwise operators
# ---------------------------------------------------------------------------


class TestBitwiseOps:
    def test_bitwise_or(self):
        assert safe_eval("0b1010 | 0b0101", {}) == 0b1111

    def test_bitwise_and(self):
        assert safe_eval("0b1111 & 0b1010", {}) == 0b1010

    def test_caret_is_power_not_xor(self):
        # In safe_eval, ^ is rewritten to ** (exponentiation), not XOR
        assert safe_eval("2 ^ 3", {}) == 8

    def test_left_shift(self):
        assert safe_eval("1 << 4", {}) == 16

    def test_right_shift(self):
        assert safe_eval("16 >> 2", {}) == 4

    def test_bitwise_invert(self):
        assert safe_eval("~0", {}) == -1


# ---------------------------------------------------------------------------
# Ternary
# ---------------------------------------------------------------------------


class TestTernary:
    def test_true_branch(self):
        assert safe_eval("10 if True else 20", {}) == 10

    def test_false_branch(self):
        assert safe_eval("10 if False else 20", {}) == 20

    def test_with_comparison(self):
        assert safe_eval("100 if x > 3 else 0", {"x": 5.0}) == 100

    def test_with_comparison_false(self):
        assert safe_eval("100 if x > 3 else 0", {"x": 1.0}) == 0

    def test_nested_expressions(self):
        assert safe_eval("x * 2 if x > 5 else x * 3", {"x": 7.0}) == 14.0


# ---------------------------------------------------------------------------
# Math functions
# ---------------------------------------------------------------------------


class TestMathFunctions:
    def test_sqrt(self):
        assert safe_eval("sqrt(16)", {}) == 4.0

    def test_log(self):
        assert abs(safe_eval("log(e)", {}) - 1.0) < 1e-9

    def test_log2(self):
        assert safe_eval("log2(8)", {}) == 3.0

    def test_log10(self):
        assert safe_eval("log10(1000)", {}) == 3.0

    def test_exp(self):
        assert safe_eval("exp(0)", {}) == 1.0

    def test_floor(self):
        assert safe_eval("floor(3.9)", {}) == 3

    def test_ceil(self):
        assert safe_eval("ceil(3.1)", {}) == 4

    def test_sin_zero(self):
        assert safe_eval("sin(0)", {}) == 0.0

    def test_cos_zero(self):
        assert safe_eval("cos(0)", {}) == 1.0

    def test_sin_pi_half(self):
        assert abs(safe_eval("sin(pi / 2)", {}) - 1.0) < 1e-9

    def test_cos_pi(self):
        assert abs(safe_eval("cos(pi)", {}) - (-1.0)) < 1e-9


# ---------------------------------------------------------------------------
# Type-cast functions
# ---------------------------------------------------------------------------


class TestTypeCasts:
    def test_int(self):
        assert safe_eval("int(3.7)", {}) == 3

    def test_float(self):
        assert safe_eval("float(42)", {}) == 42.0

    def test_str(self):
        assert safe_eval("str(99)", {}) == "99"

    def test_hex(self):
        assert safe_eval("hex(255)", {}) == "0xff"

    def test_bin(self):
        assert safe_eval("bin(10)", {}) == "0b1010"

    def test_oct(self):
        assert safe_eval("oct(8)", {}) == "0o10"

    def test_bool_true(self):
        assert safe_eval("bool(1)", {}) is True

    def test_bool_false(self):
        assert safe_eval("bool(0)", {}) is False


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


class TestConstants:
    def test_pi(self):
        assert abs(safe_eval("pi", {}) - math.pi) < 1e-12

    def test_e(self):
        assert abs(safe_eval("e", {}) - math.e) < 1e-12

    def test_inf(self):
        assert safe_eval("inf", {}) == math.inf

    def test_nan(self):
        assert math.isnan(safe_eval("nan", {}))


# ---------------------------------------------------------------------------
# NaN / Inf check functions
# ---------------------------------------------------------------------------


class TestNanInfChecks:
    def test_is_nan_true(self):
        assert safe_eval("is_nan(nan)", {}) is True

    def test_is_nan_false(self):
        assert safe_eval("is_nan(1.0)", {}) is False

    def test_is_inf_true(self):
        assert safe_eval("is_inf(inf)", {}) is True

    def test_is_inf_false(self):
        assert safe_eval("is_inf(0.0)", {}) is False

    def test_is_finite_true(self):
        assert safe_eval("is_finite(3.14)", {}) is True

    def test_is_finite_false(self):
        assert safe_eval("is_finite(inf)", {}) is False


# ---------------------------------------------------------------------------
# Division by zero → nan (no exception)
# ---------------------------------------------------------------------------


class TestDivisionByZero:
    def test_div_zero_returns_nan(self):
        result = safe_eval("3 / 0", {})
        assert math.isnan(result)

    def test_floor_div_zero_returns_nan(self):
        result = safe_eval("3 // 0", {})
        assert math.isnan(result)

    def test_modulo_zero_returns_nan(self):
        result = safe_eval("5 % 0", {})
        assert math.isnan(result)


# ---------------------------------------------------------------------------
# String comparison with unknown names treated as string literals
# ---------------------------------------------------------------------------


class TestStringComparison:
    def test_status_equals_string_literal(self):
        # unknown name "passed" is treated as the string "passed"
        result = safe_eval("status == passed", {"status": "passed"})
        assert result is True

    def test_status_not_equals(self):
        result = safe_eval("status == failed", {"status": "passed"})
        assert result is False

    def test_unknown_name_returns_itself(self):
        result = safe_eval("myvar", {})
        assert result == "myvar"


# ---------------------------------------------------------------------------
# Variable lookup
# ---------------------------------------------------------------------------


class TestVarLookup:
    def test_int_var(self):
        assert safe_eval("x + 1", {"x": 4}) == 5

    def test_float_var(self):
        assert abs(safe_eval("v * 2", {"v": 2.5}) - 5.0) < 1e-9

    def test_multiple_vars(self):
        assert safe_eval("a + b", {"a": 3, "b": 4}) == 7

    def test_var_in_comparison(self):
        assert safe_eval("v > 4.9", {"v": 5.0}) is True
