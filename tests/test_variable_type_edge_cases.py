"""Comprehensive edge-case tests for native-type variable storage.

After issue #76, script_vars stores native types (int, float, bool, str, list)
instead of converting everything to strings.  These tests verify correct
behavior across all code paths that interact with variable types.
"""

import pytest

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def repl(make_repl):
    return make_repl({})


# ---------------------------------------------------------------------------
# Type preservation on assignment
# ---------------------------------------------------------------------------


class TestTypePreservation:
    """Variables must retain their native Python type after assignment."""

    def test_int_stays_int(self, repl):
        repl.onecmd("x = 5")
        assert repl.ctx.script_vars["x"] == 5
        assert isinstance(repl.ctx.script_vars["x"], int)

    def test_float_stays_float(self, repl):
        repl.onecmd("x = 3.14")
        assert repl.ctx.script_vars["x"] == pytest.approx(3.14)
        assert isinstance(repl.ctx.script_vars["x"], float)

    def test_negative_int(self, repl):
        repl.onecmd("x = -42")
        assert repl.ctx.script_vars["x"] == -42

    def test_negative_float(self, repl):
        repl.onecmd("x = -0.001")
        assert repl.ctx.script_vars["x"] == pytest.approx(-0.001)

    def test_zero_int(self, repl):
        repl.onecmd("x = 0")
        assert repl.ctx.script_vars["x"] == 0
        assert isinstance(repl.ctx.script_vars["x"], int)

    def test_zero_float(self, repl):
        repl.onecmd("x = 0.0")
        assert repl.ctx.script_vars["x"] == 0.0
        assert isinstance(repl.ctx.script_vars["x"], float)

    def test_bool_true(self, repl):
        repl.onecmd("x = True")
        assert repl.ctx.script_vars["x"] is True

    def test_bool_false(self, repl):
        repl.onecmd("x = False")
        assert repl.ctx.script_vars["x"] is False

    def test_string_stays_string(self, repl):
        repl.onecmd('x = "hello"')
        assert repl.ctx.script_vars["x"] == "hello"
        assert isinstance(repl.ctx.script_vars["x"], str)

    def test_plain_word_stays_string(self, repl):
        """Unquoted non-numeric token is stored as raw string."""
        repl.onecmd("x = mytest")
        assert repl.ctx.script_vars["x"] == "mytest"
        assert isinstance(repl.ctx.script_vars["x"], str)

    def test_list_preserved(self, repl):
        repl.onecmd("x = [1, 2, 3]")
        assert repl.ctx.script_vars["x"] == [1, 2, 3]

    def test_tuple_preserved(self, repl):
        repl.onecmd("x = (10, 20)")
        assert repl.ctx.script_vars["x"] == (10, 20)

    def test_scientific_notation(self, repl):
        repl.onecmd("x = 1e-6")
        assert repl.ctx.script_vars["x"] == pytest.approx(1e-6)

    def test_hex_literal(self, repl):
        repl.onecmd("x = 0xFF")
        assert repl.ctx.script_vars["x"] == 255


# ---------------------------------------------------------------------------
# Type reassignment (changing types)
# ---------------------------------------------------------------------------


class TestTypeReassignment:
    """Variables can change type on reassignment."""

    def test_int_to_float(self, repl):
        repl.onecmd("x = 5")
        assert isinstance(repl.ctx.script_vars["x"], int)
        repl.onecmd("x = 3.14")
        assert isinstance(repl.ctx.script_vars["x"], float)

    def test_float_to_string(self, repl):
        repl.onecmd("x = 3.14")
        repl.onecmd('x = "hello"')
        assert repl.ctx.script_vars["x"] == "hello"

    def test_string_to_int(self, repl):
        repl.onecmd('x = "hello"')
        repl.onecmd("x = 42")
        assert repl.ctx.script_vars["x"] == 42

    def test_bool_to_int(self, repl):
        repl.onecmd("x = True")
        repl.onecmd("x = 5")
        assert repl.ctx.script_vars["x"] == 5

    def test_int_to_bool(self, repl):
        repl.onecmd("x = 5")
        repl.onecmd("x = bool(0)")
        assert repl.ctx.script_vars["x"] is False


# ---------------------------------------------------------------------------
# Mixed-type arithmetic
# ---------------------------------------------------------------------------


class TestMixedTypeArithmetic:
    """Arithmetic with mixed types should produce correct results."""

    def test_int_plus_float(self, repl):
        repl.onecmd("a = 5")
        repl.onecmd("b = 2.5")
        repl.onecmd("c = a + b")
        assert repl.ctx.script_vars["c"] == pytest.approx(7.5)
        assert isinstance(repl.ctx.script_vars["c"], float)

    def test_int_times_int(self, repl):
        repl.onecmd("a = 6")
        repl.onecmd("b = 7")
        repl.onecmd("c = a * b")
        assert repl.ctx.script_vars["c"] == 42
        assert isinstance(repl.ctx.script_vars["c"], int)

    def test_int_div_int_produces_float(self, repl):
        repl.onecmd("a = 10")
        repl.onecmd("b = 3")
        repl.onecmd("c = a / b")
        assert repl.ctx.script_vars["c"] == pytest.approx(10.0 / 3.0)
        assert isinstance(repl.ctx.script_vars["c"], float)

    def test_floor_div_stays_int(self, repl):
        repl.onecmd("c = 10 // 3")
        assert repl.ctx.script_vars["c"] == 3
        assert isinstance(repl.ctx.script_vars["c"], int)

    def test_modulo(self, repl):
        repl.onecmd("c = 10 % 3")
        assert repl.ctx.script_vars["c"] == 1

    def test_power(self, repl):
        repl.onecmd("c = 2 ** 10")
        assert repl.ctx.script_vars["c"] == 1024

    def test_bool_in_arithmetic(self, repl):
        """True is 1, False is 0 in arithmetic."""
        repl.onecmd("x = True")
        repl.onecmd("y = x + 5")
        assert repl.ctx.script_vars["y"] == 6

    def test_string_number_in_expression(self, repl):
        """A string that looks numeric should be usable in expressions via variable ref."""
        repl.ctx.script_vars["s"] = "3.5"
        repl.onecmd("y = s + 1")
        # s is in num_vars as float(3.5), so s + 1 = 4.5
        assert repl.ctx.script_vars["y"] == pytest.approx(4.5)

    def test_non_numeric_string_in_expr_falls_through(self, repl):
        """If a var is a non-numeric string, expression with it falls through to raw."""
        repl.ctx.script_vars["label"] = "hello"
        repl.onecmd("y = 5 + 3")
        # label is silently excluded from num_vars, arithmetic still works
        assert repl.ctx.script_vars["y"] == 8


# ---------------------------------------------------------------------------
# Compound assignment with mixed types
# ---------------------------------------------------------------------------


class TestCompoundAssignmentTypes:
    """Compound operators (+=, -=, etc.) with mixed initial types."""

    def test_int_plus_eq_int(self, repl):
        repl.onecmd("x = 10")
        repl.onecmd("x += 5")
        assert repl.ctx.script_vars["x"] == pytest.approx(15.0)

    def test_int_plus_eq_float(self, repl):
        repl.onecmd("x = 10")
        repl.onecmd("x += 0.5")
        assert repl.ctx.script_vars["x"] == pytest.approx(10.5)

    def test_float_minus_eq(self, repl):
        repl.onecmd("x = 3.14")
        repl.onecmd("x -= 0.14")
        assert repl.ctx.script_vars["x"] == pytest.approx(3.0)

    def test_string_number_compound(self, repl):
        """If x is a string that looks numeric, compound should still work."""
        repl.ctx.script_vars["x"] = "10"
        repl.onecmd("x += 5")
        assert float(repl.ctx.script_vars["x"]) == pytest.approx(15.0)

    def test_compound_on_undefined_var(self, repl):
        """Undefined var defaults to 0 for compound assignment."""
        repl.onecmd("newvar += 3")
        assert float(repl.ctx.script_vars["newvar"]) == pytest.approx(3.0)

    def test_multiply_eq(self, repl):
        repl.onecmd("x = 4")
        repl.onecmd("x *= 3")
        assert repl.ctx.script_vars["x"] == pytest.approx(12.0)

    def test_divide_eq(self, repl):
        repl.onecmd("x = 20")
        repl.onecmd("x /= 4")
        assert repl.ctx.script_vars["x"] == pytest.approx(5.0)


# ---------------------------------------------------------------------------
# Increment / decrement edge cases
# ---------------------------------------------------------------------------


class TestIncrementDecrementEdgeCases:
    """Edge cases for ++ and -- operators."""

    def test_increment_float(self, repl):
        repl.onecmd("x = 2.5")
        repl.onecmd("x++")
        assert repl.ctx.script_vars["x"] == pytest.approx(3.5)

    def test_decrement_float(self, repl):
        repl.onecmd("x = 2.5")
        repl.onecmd("x--")
        assert repl.ctx.script_vars["x"] == pytest.approx(1.5)

    def test_increment_bool_true(self, repl):
        """True is 1.0, so True++ = 2.0."""
        repl.onecmd("x = True")
        repl.onecmd("x++")
        assert repl.ctx.script_vars["x"] == pytest.approx(2.0)

    def test_increment_bool_false(self, repl):
        """False is 0.0, so False++ = 1.0."""
        repl.onecmd("x = False")
        repl.onecmd("x++")
        assert repl.ctx.script_vars["x"] == pytest.approx(1.0)

    def test_increment_string_number(self, repl):
        """String '5' should be convertible and increment to 6.0."""
        repl.ctx.script_vars["x"] = "5"
        repl.onecmd("x++")
        assert repl.ctx.script_vars["x"] == pytest.approx(6.0)

    def test_increment_non_numeric_string_raises(self, repl, capsys):
        """Non-numeric string surfaces TypeError and leaves x unchanged."""
        repl.ctx.script_vars["x"] = "hello"
        repl.onecmd("x++")
        out = capsys.readouterr().out
        assert "TypeError" in out
        assert repl.ctx.script_vars["x"] == "hello"

    def test_increment_undefined(self, repl):
        """Undefined var starts at 0, increments to 1.0."""
        repl.onecmd("brand_new_var++")
        assert repl.ctx.script_vars["brand_new_var"] == pytest.approx(1.0)

    def test_decrement_to_negative(self, repl):
        repl.onecmd("x = 0")
        repl.onecmd("x--")
        assert repl.ctx.script_vars["x"] == pytest.approx(-1.0)

    def test_multiple_increments(self, repl):
        repl.onecmd("x = 0")
        for _ in range(10):
            repl.onecmd("x++")
        assert repl.ctx.script_vars["x"] == pytest.approx(10.0)


# ---------------------------------------------------------------------------
# Variable substitution with native types
# ---------------------------------------------------------------------------


class TestSubstitutionWithNativeTypes:
    """Ensure {var} substitution works when vars are native types."""

    def test_int_in_print(self, repl, capsys):
        repl.onecmd("x = 42")
        repl.onecmd('print "value is {x}"')
        out = capsys.readouterr().out
        assert "value is 42" in out

    def test_float_in_print(self, repl, capsys):
        repl.onecmd("x = 3.14")
        repl.onecmd('print "pi is {x}"')
        out = capsys.readouterr().out
        assert "pi is 3.14" in out

    def test_bool_in_print(self, repl, capsys):
        repl.onecmd("x = True")
        repl.onecmd('print "flag is {x}"')
        out = capsys.readouterr().out
        assert "flag is True" in out

    def test_list_in_print(self, repl, capsys):
        repl.onecmd("x = [1, 2, 3]")
        repl.onecmd('print "items: {x}"')
        out = capsys.readouterr().out
        assert "[1, 2, 3]" in out

    def test_substitution_in_expression(self, repl):
        """Using {var} in an expression inlines the string representation."""
        repl.onecmd("a = 5")
        repl.onecmd("b = {a} * 2")
        assert repl.ctx.script_vars["b"] == 10


# ---------------------------------------------------------------------------
# Calc with native types
# ---------------------------------------------------------------------------


class TestCalcWithNativeTypes:
    """Calc command should handle native types correctly."""

    def test_calc_with_int_vars(self, repl):
        repl.onecmd("a = 10")
        repl.onecmd("b = 3")
        repl.onecmd("result = calc a + b")
        assert repl.ctx.script_vars["result"] == 13

    def test_calc_with_float_vars(self, repl):
        repl.onecmd("a = 3.14")
        repl.onecmd("b = 2.0")
        repl.onecmd("result = calc a * b")
        assert repl.ctx.script_vars["result"] == pytest.approx(6.28)

    def test_calc_with_mixed_vars(self, repl):
        repl.onecmd("a = 5")
        repl.onecmd("b = 2.5")
        repl.onecmd("result = calc a + b")
        assert repl.ctx.script_vars["result"] == pytest.approx(7.5)

    def test_calc_with_unit(self, repl):
        repl.onecmd("v = 5.0")
        repl.onecmd("i = 2.0")
        repl.onecmd("power = calc v * i unit=W")
        assert repl.ctx.script_vars["power"] == pytest.approx(10.0)
        entry = repl.ctx.measurements.get_by_label("power")
        assert entry is not None
        assert entry["unit"] == "W"


# ---------------------------------------------------------------------------
# Comparisons and conditions with native types
# ---------------------------------------------------------------------------


class TestConditionsWithNativeTypes:
    """If/while/assert/check should work with native-type variables."""

    def test_if_with_int(self, repl):
        repl.onecmd("x = 10")
        repl.onecmd("result = 0")
        repl.onecmd("if x > 5")
        repl.onecmd("result = 1")
        repl.onecmd("end")
        assert repl.ctx.script_vars["result"] == 1

    def test_if_with_float(self, repl):
        repl.onecmd("x = 3.14")
        repl.onecmd("result = 0")
        repl.onecmd("if x > 3.0")
        repl.onecmd("result = 1")
        repl.onecmd("end")
        assert repl.ctx.script_vars["result"] == 1

    def test_if_with_bool(self, repl):
        repl.onecmd("flag = True")
        repl.onecmd("result = 0")
        repl.onecmd("if flag")
        repl.onecmd("result = 1")
        repl.onecmd("end")
        assert repl.ctx.script_vars["result"] == 1

    def test_comparison_int_vs_float(self, repl):
        """5 == 5.0 should be True."""
        repl.onecmd("a = 5")
        repl.onecmd("b = 5.0")
        repl.onecmd("result = a == b")
        assert repl.ctx.script_vars["result"] is True

    def test_assert_with_native_int(self, repl, capsys):
        repl.onecmd("x = 10")
        repl.onecmd('assert x > 5 "x must be > 5"')
        # If assert fails it would set command_had_error
        assert not repl.ctx.command_had_error

    def test_while_with_native_counter(self, repl):
        repl.onecmd("i = 0")
        repl.onecmd("total = 0")
        repl.onecmd("while i < 3")
        repl.onecmd("i++")
        repl.onecmd("total += 1")
        repl.onecmd("end")
        assert repl.ctx.script_vars["total"] == pytest.approx(3.0)


# ---------------------------------------------------------------------------
# Unset and re-assign
# ---------------------------------------------------------------------------


class TestUnsetAndReassign:
    """Unset a variable and reassign with a different type."""

    def test_unset_int_reassign_string(self, repl):
        repl.onecmd("x = 42")
        repl.onecmd("unset x")
        assert "x" not in repl.ctx.script_vars
        repl.onecmd('x = "hello"')
        assert repl.ctx.script_vars["x"] == "hello"

    def test_unset_stops_substitution(self, repl, capsys):
        repl.onecmd("x = 42")
        repl.onecmd("unset x")
        repl.onecmd('print "{x}"')
        out = capsys.readouterr().out
        assert "{x}" in out


# ---------------------------------------------------------------------------
# Edge cases with special float values
# ---------------------------------------------------------------------------


class TestSpecialFloatValues:
    """Edge cases with inf, nan, and very small/large numbers."""

    def test_infinity(self, repl):
        repl.onecmd("x = float('inf')")
        assert repl.ctx.script_vars["x"] == float("inf")

    def test_negative_infinity(self, repl):
        repl.onecmd("x = float('-inf')")
        assert repl.ctx.script_vars["x"] == float("-inf")

    def test_very_small_float(self, repl):
        repl.onecmd("x = 1e-15")
        assert repl.ctx.script_vars["x"] == pytest.approx(1e-15)

    def test_very_large_float(self, repl):
        repl.onecmd("x = 1e15")
        assert repl.ctx.script_vars["x"] == pytest.approx(1e15)

    def test_division_by_large_number(self, repl):
        repl.onecmd("x = 1 / 1000000")
        assert repl.ctx.script_vars["x"] == pytest.approx(1e-6)


# ---------------------------------------------------------------------------
# Pyeval with native types
# ---------------------------------------------------------------------------


class TestPyevalWithNativeTypes:
    """pyeval should see native types, not strings."""

    def test_pyeval_accesses_int_var(self, repl, capsys):
        repl.onecmd("x = 42")
        repl.onecmd("pyeval x + 8")
        out = capsys.readouterr().out
        assert "50" in out

    def test_pyeval_accesses_float_var(self, repl, capsys):
        repl.onecmd("x = 3.14")
        repl.onecmd("pyeval round(x, 1)")
        out = capsys.readouterr().out
        assert "3.1" in out

    def test_pyeval_result_stored_native(self, repl):
        repl.onecmd("pyeval 10 ** 2")
        assert repl.ctx.script_vars["_"] == 100


# ---------------------------------------------------------------------------
# String vs number confusion
# ---------------------------------------------------------------------------


class TestStringNumberConfusion:
    """Cases where a value could be interpreted as either string or number."""

    def test_quoted_number_is_string(self, repl):
        """A quoted number should stay as string."""
        repl.onecmd('x = "42"')
        assert repl.ctx.script_vars["x"] == "42"
        assert isinstance(repl.ctx.script_vars["x"], str)

    def test_unquoted_number_is_numeric(self, repl):
        repl.onecmd("x = 42")
        assert isinstance(repl.ctx.script_vars["x"], int)

    def test_string_number_still_works_in_calc(self, repl):
        """Even if a var is a string '5', calc should still use it."""
        repl.ctx.script_vars["x"] = "5"
        repl.onecmd("y = x * 2")
        # x is converted to float(5) for the expression
        assert repl.ctx.script_vars["y"] == pytest.approx(10.0)

    def test_mixed_string_and_native_in_expression(self, repl):
        """Mix of string-stored and native-stored vars in one expression."""
        repl.ctx.script_vars["a"] = "3"  # legacy string
        repl.onecmd("b = 7")  # native int
        repl.onecmd("c = a + b")
        assert repl.ctx.script_vars["c"] == pytest.approx(10.0)

    def test_hex_string_not_auto_parsed(self, repl):
        """An unquoted hex-looking word that isn't a valid literal stays as string."""
        repl.onecmd("x = 0xGG")
        # Not a valid hex literal, safe_eval fails, falls through to raw string
        assert repl.ctx.script_vars["x"] == "0xGG"

    def test_assign_empty_string(self, repl):
        repl.onecmd('x = ""')
        assert repl.ctx.script_vars["x"] == ""
        assert isinstance(repl.ctx.script_vars["x"], str)


# ---------------------------------------------------------------------------
# For loop variable types
# ---------------------------------------------------------------------------


class TestForLoopVariableTypes:
    """For loop iteration variables should be usable in expressions."""

    def test_for_loop_var_in_print(self, repl, capsys):
        repl.onecmd("for v 1.0 2.0 3.0")
        repl.onecmd('print "v={v}"')
        repl.onecmd("end")
        out = capsys.readouterr().out
        assert "v=1.0" in out
        assert "v=2.0" in out
        assert "v=3.0" in out

    def test_for_loop_var_in_compound_assignment(self, repl):
        """For loop variable should be usable via {v} substitution in compound assignment."""
        repl.onecmd("total = 0")
        repl.onecmd("for v 1 2 3")
        repl.onecmd("total += {v}")
        repl.onecmd("end")
        # {v} is substituted by the expander, so total = 0+1+2+3 = 6
        assert float(repl.ctx.script_vars["total"]) == pytest.approx(6.0)
