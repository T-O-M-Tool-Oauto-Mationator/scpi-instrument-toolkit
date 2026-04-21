"""Tests for REPL operator type handling, string/float coercion, and edge cases.

Covers:
  - safe_eval() return types (int vs float vs string vs bool)
  - Compound assignment type coercion through the REPL
  - The non-numeric string variable crash bug in compound assignment
  - Increment/decrement type behavior
  - Regular assignment type coercion
  - Comparison and boolean operator types
  - Edge cases: NaN, Inf, scientific notation, division by zero
  - The ^ -> ** rewrite in safe_eval
  - Result type preservation (int-string vs float-string)
"""

import math

import pytest

from lab_instruments.repl.syntax import safe_eval

# ---------------------------------------------------------------------------
# TestSafeEvalTypes -- direct tests of safe_eval()
# ---------------------------------------------------------------------------


class TestSafeEvalTypes:
    """Direct tests of safe_eval return types."""

    def test_add_two_ints_returns_int(self):
        result = safe_eval("2 + 3", {})
        assert result == 5
        assert isinstance(result, int)

    def test_add_int_and_float_returns_float(self):
        result = safe_eval("2 + 3.0", {})
        assert result == 5.0
        assert isinstance(result, float)

    def test_add_two_floats_returns_float(self):
        result = safe_eval("2.0 + 3.0", {})
        assert result == 5.0
        assert isinstance(result, float)

    def test_subtract_ints_returns_int(self):
        result = safe_eval("10 - 3", {})
        assert result == 7
        assert isinstance(result, int)

    def test_subtract_int_float_returns_float(self):
        result = safe_eval("10 - 3.0", {})
        assert result == 7.0
        assert isinstance(result, float)

    def test_multiply_ints_returns_int(self):
        result = safe_eval("4 * 5", {})
        assert result == 20
        assert isinstance(result, int)

    def test_multiply_int_float_returns_float(self):
        result = safe_eval("4 * 5.0", {})
        assert result == 20.0
        assert isinstance(result, float)

    def test_true_division_always_returns_float(self):
        result = safe_eval("6 / 2", {})
        assert result == 3.0
        assert isinstance(result, float)

    def test_true_division_float_operands(self):
        result = safe_eval("7.0 / 2.0", {})
        assert result == 3.5
        assert isinstance(result, float)

    def test_floor_division_ints_returns_int(self):
        result = safe_eval("7 // 2", {})
        assert result == 3
        assert isinstance(result, int)

    def test_floor_division_with_float_returns_float(self):
        result = safe_eval("7.0 // 2", {})
        assert result == 3.0
        assert isinstance(result, float)

    def test_power_ints_returns_int(self):
        result = safe_eval("2 ** 3", {})
        assert result == 8
        assert isinstance(result, int)

    def test_power_float_base_returns_float(self):
        result = safe_eval("2.0 ** 3", {})
        assert result == 8.0
        assert isinstance(result, float)

    def test_modulo_ints_returns_int(self):
        result = safe_eval("7 % 3", {})
        assert result == 1
        assert isinstance(result, int)

    def test_modulo_with_float_returns_float(self):
        result = safe_eval("7.0 % 3", {})
        assert result == 1.0
        assert isinstance(result, float)

    def test_variable_from_names_dict(self):
        result = safe_eval("x + 1", {"x": 5.0})
        assert result == 6.0
        assert isinstance(result, float)

    def test_variable_int_from_names_dict(self):
        result = safe_eval("x + 1", {"x": 5})
        assert result == 6
        assert isinstance(result, int)

    def test_string_literal_returns_string(self):
        result = safe_eval('"hello"', {})
        assert result == "hello"
        assert isinstance(result, str)

    def test_string_concatenation(self):
        result = safe_eval('"hello" + " world"', {})
        assert result == "hello world"

    def test_string_plus_int_raises_type_error(self):
        with pytest.raises(TypeError):
            safe_eval('"hello" + 1', {})

    def test_division_by_zero_raises(self):
        with pytest.raises(ZeroDivisionError):
            safe_eval("1 / 0", {})

    def test_floor_division_by_zero_raises(self):
        with pytest.raises(ZeroDivisionError):
            safe_eval("1 // 0", {})

    def test_modulo_by_zero_raises(self):
        with pytest.raises(ZeroDivisionError):
            safe_eval("1 % 0", {})

    def test_unknown_name_raises_nameerror(self):
        """Unknown identifiers raise NameError in strict (default) mode."""
        with pytest.raises(NameError, match="'hello' is not defined"):
            safe_eval("hello", {})
        # Legacy lenient mode still returns the identifier string.
        assert safe_eval("hello", {}, strict=False) == "hello"

    def test_int_conversion(self):
        result = safe_eval("int(3.7)", {})
        assert result == 3
        assert isinstance(result, int)

    def test_float_conversion(self):
        result = safe_eval("float(3)", {})
        assert result == 3.0
        assert isinstance(result, float)

    def test_str_conversion(self):
        result = safe_eval("str(42)", {})
        assert result == "42"
        assert isinstance(result, str)

    def test_caret_rewrite_to_power(self):
        """^ is rewritten to ** so 2^3 means 2**3 = 8, not bitwise XOR."""
        result = safe_eval("2 ^ 3", {})
        # After rewrite, "2 ^ 3" becomes "2 ** 3" = 8
        # (bitwise XOR of 2 and 3 would be 1)
        assert result == 8

    def test_caret_matches_double_star(self):
        assert safe_eval("2 ^ 3", {}) == safe_eval("2 ** 3", {})

    def test_bitwise_or(self):
        result = safe_eval("0b1010 | 0b0101", {})
        assert result == 15

    def test_bitwise_and(self):
        result = safe_eval("0b1010 & 0b1111", {})
        assert result == 10

    def test_left_shift(self):
        result = safe_eval("1 << 4", {})
        assert result == 16

    def test_right_shift(self):
        result = safe_eval("16 >> 2", {})
        assert result == 4

    def test_bitwise_invert_converts_float_to_int(self):
        """Bitwise invert calls int() on the operand first."""
        result = safe_eval("~0", {})
        assert result == -1
        assert isinstance(result, int)

    def test_bitwise_or_converts_floats_to_int(self):
        """BitOr does int(a) | int(b), so floats get truncated."""
        result = safe_eval("3.9 | 1.1", {})
        # int(3.9) | int(1.1) = 3 | 1 = 3
        assert result == 3

    def test_unary_plus(self):
        result = safe_eval("+5", {})
        assert result == 5

    def test_unary_minus(self):
        result = safe_eval("-5", {})
        assert result == -5
        assert isinstance(result, int)

    def test_unary_minus_float(self):
        result = safe_eval("-5.0", {})
        assert result == -5.0
        assert isinstance(result, float)

    def test_nested_parentheses(self):
        result = safe_eval("(2 + 3) * (4 - 1)", {})
        assert result == 15

    def test_multiple_variables(self):
        result = safe_eval("x + y * z", {"x": 1, "y": 2, "z": 3})
        assert result == 7


# ---------------------------------------------------------------------------
# TestCompoundAssignmentTypeCoercion -- REPL-level compound ops
# ---------------------------------------------------------------------------


class TestCompoundAssignmentTypeCoercion:
    """REPL-level tests for compound assignment type coercion."""

    def test_int_plus_int(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("x = 10")
        repl.onecmd("x += 5")
        assert float(repl.ctx.script_vars["x"]) == pytest.approx(15.0)

    def test_int_plus_float(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("x = 10")
        repl.onecmd("x += 2.5")
        assert float(repl.ctx.script_vars["x"]) == pytest.approx(12.5)

    def test_float_plus_int(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("x = 10.5")
        repl.onecmd("x += 2")
        assert float(repl.ctx.script_vars["x"]) == pytest.approx(12.5)

    def test_minus_equal_float(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("x = 10")
        repl.onecmd("x -= 3.5")
        assert float(repl.ctx.script_vars["x"]) == pytest.approx(6.5)

    def test_multiply_equal_fractional(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("x = 10")
        repl.onecmd("x *= 0.5")
        assert float(repl.ctx.script_vars["x"]) == pytest.approx(5.0)

    def test_divide_equal(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("x = 10")
        repl.onecmd("x /= 3")
        assert float(repl.ctx.script_vars["x"]) == pytest.approx(10.0 / 3.0)

    def test_floor_divide_equal(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("x = 10")
        repl.onecmd("x //= 3")
        assert float(repl.ctx.script_vars["x"]) == pytest.approx(3.0)

    def test_power_equal(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("x = 2")
        repl.onecmd("x **= 10")
        assert float(repl.ctx.script_vars["x"]) == pytest.approx(1024.0)

    def test_modulo_equal(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("x = 10")
        repl.onecmd("x %= 3")
        assert float(repl.ctx.script_vars["x"]) == pytest.approx(1.0)

    def test_compound_on_undefined_defaults_to_zero(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("x += 7")
        assert float(repl.ctx.script_vars["x"]) == pytest.approx(7.0)

    def test_compound_with_negative_rhs(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("x = 10")
        repl.onecmd("x += -3")
        assert float(repl.ctx.script_vars["x"]) == pytest.approx(7.0)

    def test_compound_with_expression_rhs(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("x = 10")
        repl.onecmd("x += 2 * 3")
        assert float(repl.ctx.script_vars["x"]) == pytest.approx(16.0)

    def test_compound_with_variable_rhs(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("x = 10")
        repl.onecmd("y = 5")
        repl.onecmd("x += {y}")
        assert float(repl.ctx.script_vars["x"]) == pytest.approx(15.0)

    def test_multiple_sequential_compounds(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("x = 0")
        repl.onecmd("x += 1")
        repl.onecmd("x += 1")
        repl.onecmd("x += 1")
        assert float(repl.ctx.script_vars["x"]) == pytest.approx(3.0)

    def test_stored_value_is_native_type(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("x = 10")
        repl.onecmd("x += 5")
        assert repl.ctx.script_vars["x"] == 15

    def test_compound_prints_result(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("x = 10")
        capsys.readouterr()
        repl.onecmd("x += 5")
        out = capsys.readouterr().out
        assert "x" in out
        assert "15" in out

    def test_compound_chain_multiply_then_add(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("x = 2")
        repl.onecmd("x *= 5")
        repl.onecmd("x += 3")
        assert float(repl.ctx.script_vars["x"]) == pytest.approx(13.0)


# ---------------------------------------------------------------------------
# TestCompoundAssignmentWithNonNumericVars -- the float(v) crash bug
# ---------------------------------------------------------------------------


class TestCompoundAssignmentWithNonNumericVars:
    """Tests for the bug where non-numeric string variables crash compound assignment.

    The compound assignment handler uses:
        {k: float(v) for k, v in self.ctx.script_vars.items() if k != varname}
    This crashes with ValueError when ANY non-numeric string variable exists
    (e.g. label = "mytest"), because float("mytest") raises ValueError.

    The compound assignment handler now uses the same pattern as _assign_var:
    iterating with try/except to skip non-numeric values.
    """

    def test_compound_with_nonnumeric_var_present(self, make_repl, capsys):
        """x += 3 should succeed even when a non-numeric var (label) exists."""
        repl = make_repl({})
        repl.onecmd("label = mytest")
        repl.onecmd("x = 5")
        repl.onecmd("x += 3")
        assert float(repl.ctx.script_vars["x"]) == pytest.approx(8.0)

    def test_increment_with_nonnumeric_var_present(self, make_repl, capsys):
        """counter++ should succeed when non-numeric vars exist."""
        repl = make_repl({})
        repl.onecmd("name = hello")
        repl.onecmd("counter = 0")
        repl.onecmd("counter++")
        assert float(repl.ctx.script_vars["counter"]) == pytest.approx(1.0)

    def test_compound_with_multiple_nonnumeric_vars(self, make_repl, capsys):
        """Compound assignment with several non-numeric vars in scope."""
        repl = make_repl({})
        repl.onecmd("label = test_run")
        repl.onecmd("status = passed")
        repl.onecmd("note = experiment_one")
        repl.onecmd("x = 10")
        repl.onecmd("x += 5")
        assert float(repl.ctx.script_vars["x"]) == pytest.approx(15.0)

    def test_compound_on_nonnumeric_var_itself_errors_gracefully(self, make_repl, capsys):
        """Compound += on a non-numeric var should produce an error, not crash."""
        repl = make_repl({})
        repl.onecmd("label = mytest")
        capsys.readouterr()
        repl.onecmd("label += 3")
        out = capsys.readouterr().out
        # Should print an error message, not crash the REPL
        # The var may or may not change, but the REPL should survive
        assert "error" in out.lower() or "failed" in out.lower() or "label" in repl.ctx.script_vars

    def test_compound_preserves_value_on_failure(self, make_repl, capsys):
        """If compound assignment fails due to type error, var retains its previous value."""
        repl = make_repl({})
        repl.onecmd("x = 5")
        repl.onecmd("x += invalid_not_a_number")
        # x should still be 5 (not clobbered) because the error is caught
        assert repl.ctx.script_vars["x"] == 5

    def test_compound_succeeds_when_nonnumeric_vars_exist(self, make_repl, capsys):
        """Compound assignment works correctly with non-numeric vars in scope."""
        repl = make_repl({})
        repl.onecmd("label = mytest")
        repl.onecmd("x = 5")
        repl.onecmd("x += 3")
        assert float(repl.ctx.script_vars["x"]) == pytest.approx(8.0)


# ---------------------------------------------------------------------------
# TestIncrementDecrementTypes
# ---------------------------------------------------------------------------


class TestIncrementDecrementTypes:
    """Type behavior of x++ and x-- operators."""

    def test_increment_int_stores_native_float(self, make_repl, capsys):
        """x = 5; x++ stores the result as a native float (float(5) + 1)."""
        repl = make_repl({})
        repl.onecmd("x = 5")
        repl.onecmd("x++")
        assert repl.ctx.script_vars["x"] == pytest.approx(6.0)
        assert isinstance(repl.ctx.script_vars["x"], float)

    def test_increment_float(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("x = 5.5")
        repl.onecmd("x++")
        assert float(repl.ctx.script_vars["x"]) == pytest.approx(6.5)

    def test_increment_undefined_becomes_one(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("x++")
        assert float(repl.ctx.script_vars["x"]) == pytest.approx(1.0)

    def test_decrement_undefined_becomes_negative_one(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("x--")
        assert float(repl.ctx.script_vars["x"]) == pytest.approx(-1.0)

    def test_increment_nonnumeric_string_raises_typeerror(self, make_repl, capsys):
        """x = hello; x++ surfaces TypeError and leaves x unchanged."""
        repl = make_repl({})
        repl.ctx.script_vars["x"] = "hello"
        repl.onecmd("x++")
        out = capsys.readouterr().out
        assert "TypeError" in out
        assert repl.ctx.script_vars["x"] == "hello"

    def test_decrement_nonnumeric_string_raises_typeerror(self, make_repl, capsys):
        """x = hello; x-- surfaces TypeError and leaves x unchanged."""
        repl = make_repl({})
        repl.ctx.script_vars["x"] = "hello"
        repl.onecmd("x--")
        out = capsys.readouterr().out
        assert "TypeError" in out
        assert repl.ctx.script_vars["x"] == "hello"

    def test_multiple_increments_accumulate(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("x = 0")
        for _ in range(5):
            repl.onecmd("x++")
        assert float(repl.ctx.script_vars["x"]) == pytest.approx(5.0)

    def test_increment_result_stored_as_native_float(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("x = 10")
        repl.onecmd("x++")
        assert isinstance(repl.ctx.script_vars["x"], float)

    def test_increment_zero(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("x = 0")
        repl.onecmd("x++")
        assert float(repl.ctx.script_vars["x"]) == pytest.approx(1.0)

    def test_increment_negative(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("x = -1")
        repl.onecmd("x++")
        assert float(repl.ctx.script_vars["x"]) == pytest.approx(0.0)

    def test_increment_large_number(self, make_repl, capsys):
        repl = make_repl({})
        repl.ctx.script_vars["x"] = "1e10"
        repl.onecmd("x++")
        assert float(repl.ctx.script_vars["x"]) == pytest.approx(10000000001.0)

    def test_decrement_prints_result(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("x = 10")
        capsys.readouterr()
        repl.onecmd("x--")
        out = capsys.readouterr().out
        assert "x" in out
        assert "9" in out


# ---------------------------------------------------------------------------
# TestInlineCommentStripping
# ---------------------------------------------------------------------------


class TestInlineCommentStripping:
    """Inline # comments must be stripped from ++, --, and compound assignments."""

    def test_increment_with_inline_comment(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("x = 5")
        repl.onecmd("x++                # bump")
        assert repl.ctx.script_vars["x"] == pytest.approx(6.0)

    def test_decrement_with_inline_comment(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("x = 5")
        repl.onecmd("x--                # drop")
        assert repl.ctx.script_vars["x"] == pytest.approx(4.0)

    def test_compound_add_with_inline_comment(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("x = 10")
        repl.onecmd("x += 1             # count = 11")
        assert repl.ctx.script_vars["x"] == pytest.approx(11.0)

    def test_compound_sub_with_inline_comment(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("x = 10")
        repl.onecmd("x -= 3             # count = 7")
        assert repl.ctx.script_vars["x"] == pytest.approx(7.0)

    def test_compound_mul_with_inline_comment(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("x = 5")
        repl.onecmd("x *= 2             # double it")
        assert repl.ctx.script_vars["x"] == pytest.approx(10.0)

    def test_assignment_with_hash_in_string_preserved(self, make_repl, capsys):
        """Hash inside quotes must NOT be treated as a comment."""
        repl = make_repl({})
        repl.onecmd('name = "test # value"')
        assert repl.ctx.script_vars["name"] == "test # value"


# ---------------------------------------------------------------------------
# TestAssignmentTypeCoercion
# ---------------------------------------------------------------------------


class TestAssignmentTypeCoercion:
    """Type coercion behavior of regular var = expr assignment."""

    def test_assign_int_literal(self, make_repl, capsys):
        """x = 5 stores 5 -- safe_eval returns int for int literal."""
        repl = make_repl({})
        repl.onecmd("x = 5")
        assert repl.ctx.script_vars["x"] == 5

    def test_assign_float_literal(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("x = 5.0")
        assert repl.ctx.script_vars["x"] == 5.0

    def test_assign_string_falls_through(self, make_repl, capsys):
        """x = hello stores 'hello' because safe_eval returns 'hello' (unknown name)."""
        repl = make_repl({})
        repl.onecmd("x = hello")
        assert repl.ctx.script_vars["x"] == "hello"

    def test_assign_int_expression(self, make_repl, capsys):
        """x = 3 + 2 stores 5 (int result from safe_eval)."""
        repl = make_repl({})
        repl.onecmd("x = 3 + 2")
        assert repl.ctx.script_vars["x"] == 5

    def test_assign_mixed_expression(self, make_repl, capsys):
        """x = 3.0 + 2 stores 5.0 (float result from int+float)."""
        repl = make_repl({})
        repl.onecmd("x = 3.0 + 2")
        assert repl.ctx.script_vars["x"] == 5.0

    def test_assign_true_division_stores_float(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("x = 10 / 3")
        val = float(repl.ctx.script_vars["x"])
        assert val == pytest.approx(10.0 / 3.0)

    def test_assign_floor_division_stores_int(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("x = 10 // 3")
        assert repl.ctx.script_vars["x"] == 3

    def test_assign_with_variable_ref(self, make_repl, capsys):
        """a = 5; b = {a} + 1.

        Since vars are stored as strings, and the assignment handler builds
        num_vars with float(v), {a} resolves to the string '5', which then
        is in the expression as '5 + 1', evaluating to 6 via safe_eval.
        But the variable 'a' is passed in num_vars as float(5) = 5.0,
        so if the expression uses the name directly (not {a}), it would be 6.0.
        With {a} substitution, '5' is inlined, safe_eval sees '5 + 1' = 6 (int).
        """
        repl = make_repl({})
        repl.onecmd("a = 5")
        repl.onecmd("b = {a} + 1")
        # {a} is substituted to "5", so safe_eval sees "5 + 1" = 6 (int)
        assert repl.ctx.script_vars["b"] == 6

    def test_assign_int_cast(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("x = int(3.7)")
        assert repl.ctx.script_vars["x"] == 3

    def test_assign_float_cast(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("x = float(5)")
        assert repl.ctx.script_vars["x"] == 5.0

    def test_assign_with_nonnumeric_var_in_scope(self, make_repl, capsys):
        """label = test; x = 5 + 3 should still work.

        The assignment handler uses contextlib.suppress to skip non-numeric
        vars, so 'label' is excluded from num_vars without crashing.
        """
        repl = make_repl({})
        repl.onecmd("label = test")
        repl.onecmd("x = 5 + 3")
        assert repl.ctx.script_vars["x"] == 8

    def test_assign_stored_as_native_type(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("x = 42")
        assert isinstance(repl.ctx.script_vars["x"], int)

    def test_assign_negative_number(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("x = -7")
        assert repl.ctx.script_vars["x"] == -7

    def test_assign_negative_float(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("x = -3.5")
        assert repl.ctx.script_vars["x"] == -3.5


# ---------------------------------------------------------------------------
# TestComparisonOperatorTypes
# ---------------------------------------------------------------------------


class TestComparisonOperatorTypes:
    """Test comparison operator return types in safe_eval."""

    def test_equal_ints(self):
        assert safe_eval("5 == 5", {}) is True

    def test_equal_int_float_cross_type(self):
        assert safe_eval("5 == 5.0", {}) is True

    def test_not_equal(self):
        assert safe_eval("5 != 6", {}) is True

    def test_less_than(self):
        assert safe_eval("5 < 6", {}) is True

    def test_less_than_equal(self):
        assert safe_eval("5 <= 5", {}) is True

    def test_greater_than_float(self):
        assert safe_eval("5.0 > 4.9", {}) is True

    def test_greater_than_equal(self):
        assert safe_eval("5.0 >= 5.0", {}) is True

    def test_chained_comparison_true(self):
        assert safe_eval("1 < 2 < 3", {}) is True

    def test_chained_comparison_false(self):
        assert safe_eval("3 < 2 < 1", {}) is False

    def test_string_equality_unknown_names(self):
        """Two unknown names compared -- lenient mode treats them as strings."""
        assert safe_eval("hello == hello", {}, strict=False) is True

    def test_string_inequality_unknown_names(self):
        assert safe_eval("hello == world", {}, strict=False) is False

    def test_variable_comparison_float(self):
        assert safe_eval("x == 5", {"x": 5.0}) is True

    def test_variable_comparison_int(self):
        assert safe_eval("x == 5", {"x": 5}) is True

    def test_comparison_returns_bool_type(self):
        result = safe_eval("1 < 2", {})
        assert isinstance(result, bool)


# ---------------------------------------------------------------------------
# TestBooleanOperatorTypes
# ---------------------------------------------------------------------------


class TestBooleanOperatorTypes:
    """Test boolean operator return types in safe_eval."""

    def test_and_truthy_returns_last(self):
        result = safe_eval("1 and 2", {})
        assert result == 2

    def test_and_falsy_short_circuits(self):
        result = safe_eval("0 and 2", {})
        assert result == 0

    def test_or_falsy_first_returns_second(self):
        result = safe_eval("0 or 2", {})
        assert result == 2

    def test_or_truthy_first_returns_first(self):
        result = safe_eval("1 or 2", {})
        assert result == 1

    def test_not_zero_is_true(self):
        result = safe_eval("not 0", {})
        assert result is True

    def test_not_one_is_false(self):
        result = safe_eval("not 1", {})
        assert result is False

    def test_c_style_or(self):
        """|| is rewritten to 'or'."""
        result = safe_eval("1 || 0", {})
        assert result == 1

    def test_c_style_and(self):
        """&& is rewritten to 'and'."""
        result = safe_eval("1 && 0", {})
        assert result == 0

    def test_c_style_or_both_falsy(self):
        result = safe_eval("0 || 0", {})
        assert result == 0

    def test_c_style_and_both_truthy(self):
        result = safe_eval("1 && 2", {})
        assert result == 2

    def test_not_returns_bool(self):
        assert isinstance(safe_eval("not 0", {}), bool)


# ---------------------------------------------------------------------------
# TestEdgeCaseTypes
# ---------------------------------------------------------------------------


class TestEdgeCaseTypes:
    """Edge cases: scientific notation, NaN, Inf, precision, etc."""

    def test_scientific_notation_assignment(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("x = 1e-3")
        val = float(repl.ctx.script_vars["x"])
        assert val == pytest.approx(0.001)

    def test_large_number_precision(self, make_repl, capsys):
        repl = make_repl({})
        repl.ctx.script_vars["x"] = "1e15"
        repl.onecmd("x += 1")
        val = float(repl.ctx.script_vars["x"])
        assert val == pytest.approx(1e15 + 1)

    def test_nan_constant_in_safe_eval(self):
        result = safe_eval("nan", {})
        assert math.isnan(result)

    def test_nan_plus_one(self):
        result = safe_eval("nan + 1", {})
        assert math.isnan(result)

    def test_inf_constant_in_safe_eval(self):
        result = safe_eval("inf", {})
        assert math.isinf(result)

    def test_inf_plus_one(self):
        result = safe_eval("inf + 1", {})
        assert math.isinf(result)
        assert result > 0

    def test_inf_minus_inf_is_nan(self):
        result = safe_eval("inf - inf", {})
        assert math.isnan(result)

    def test_negative_float_compound(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("x = -3.5")
        repl.onecmd("x += 1")
        assert float(repl.ctx.script_vars["x"]) == pytest.approx(-2.5)

    def test_very_small_float_compound(self, make_repl, capsys):
        repl = make_repl({})
        repl.ctx.script_vars["x"] = "0.0000001"
        repl.onecmd("x *= 2")
        assert float(repl.ctx.script_vars["x"]) == pytest.approx(0.0000002)

    def test_division_by_zero_safe_eval_raises(self):
        with pytest.raises(ZeroDivisionError):
            safe_eval("1 / 0", {})

    def test_floor_division_by_zero_safe_eval_raises(self):
        with pytest.raises(ZeroDivisionError):
            safe_eval("1 // 0", {})

    def test_modulo_by_zero_safe_eval_raises(self):
        with pytest.raises(ZeroDivisionError):
            safe_eval("1 % 0", {})

    def test_zero_division_compound_assignment(self, make_repl, capsys):
        """x = 5; x /= 0 reports ZeroDivisionError and leaves x unchanged."""
        repl = make_repl({})
        repl.onecmd("x = 5")
        capsys.readouterr()
        repl.onecmd("x /= 0")
        out = capsys.readouterr().out
        assert "ZeroDivisionError" in out
        assert repl.ctx.script_vars["x"] == 5

    def test_negative_exponent(self):
        result = safe_eval("2 ** -1", {})
        assert result == pytest.approx(0.5)
        assert isinstance(result, float)

    def test_zero_power_zero(self):
        result = safe_eval("0 ** 0", {})
        assert result == 1

    def test_large_integer(self):
        result = safe_eval("2 ** 64", {})
        assert result == 2**64
        assert isinstance(result, int)


# ---------------------------------------------------------------------------
# TestCaretRewrite
# ---------------------------------------------------------------------------


class TestCaretRewrite:
    """The ^ operator is rewritten to ** in safe_eval."""

    def test_caret_is_power_not_xor(self):
        """2 ^ 3 gives 8 (power) not 1 (XOR)."""
        result = safe_eval("2 ^ 3", {})
        assert result == 8

    def test_caret_same_as_double_star(self):
        assert safe_eval("2 ^ 3", {}) == safe_eval("2 ** 3", {})

    def test_caret_with_floats(self):
        result = safe_eval("2.0 ^ 3", {})
        assert result == pytest.approx(8.0)
        assert isinstance(result, float)

    def test_caret_equals_not_matched_as_compound(self, make_repl, capsys):
        """x ^= 3 is NOT in the compound assignment regex, so it won't be
        handled as compound assignment. It would fall through to regular
        assignment or be unrecognized."""
        repl = make_repl({})
        repl.onecmd("x = 2")
        capsys.readouterr()
        # ^= is not in the compound regex: (\+|-|\*\*|\*|//|/|%)=
        # So this will not be matched as compound assignment
        repl.onecmd("x ^= 3")
        # The REPL should not crash -- it may treat "x ^= 3" as something else
        # or produce an error. Check that x still exists.
        assert "x" in repl.ctx.script_vars

    def test_caret_in_expression(self):
        """Caret works inside larger expressions."""
        result = safe_eval("1 + 2 ^ 3", {})
        # 2^3 -> 2**3 = 8, so 1 + 8 = 9
        assert result == 9

    def test_double_caret_becomes_double_power(self):
        """Edge case: 2 ^^ 3 becomes 2 **** 3 which is a syntax error.
        The ^ -> ** rewrite is a simple string replace."""
        with pytest.raises(SyntaxError):
            safe_eval("2 ^^ 3", {})


# ---------------------------------------------------------------------------
# TestResultTypePreservation
# ---------------------------------------------------------------------------


class TestResultTypePreservation:
    """Verify int vs float type is correctly preserved in safe_eval results."""

    def test_int_add_returns_int(self):
        result = safe_eval("2 + 3", {})
        assert result == 5
        assert isinstance(result, int), f"Expected int, got {type(result).__name__}"

    def test_float_add_returns_float(self):
        result = safe_eval("2.0 + 3", {})
        assert result == 5.0
        assert isinstance(result, float), f"Expected float, got {type(result).__name__}"

    def test_true_division_always_float(self):
        result = safe_eval("6 / 2", {})
        assert result == 3.0
        assert isinstance(result, float), f"Expected float, got {type(result).__name__}"

    def test_floor_division_ints_returns_int(self):
        result = safe_eval("6 // 2", {})
        assert result == 3
        assert isinstance(result, int), f"Expected int, got {type(result).__name__}"

    def test_power_ints_returns_int(self):
        result = safe_eval("2 ** 3", {})
        assert result == 8
        assert isinstance(result, int), f"Expected int, got {type(result).__name__}"

    def test_power_float_base_returns_float(self):
        result = safe_eval("2.0 ** 3", {})
        assert result == 8.0
        assert isinstance(result, float), f"Expected float, got {type(result).__name__}"

    def test_modulo_ints_returns_int(self):
        result = safe_eval("7 % 3", {})
        assert result == 1
        assert isinstance(result, int), f"Expected int, got {type(result).__name__}"

    def test_modulo_float_returns_float(self):
        result = safe_eval("7.0 % 3", {})
        assert result == 1.0
        assert isinstance(result, float), f"Expected float, got {type(result).__name__}"

    def test_subtraction_ints_returns_int(self):
        result = safe_eval("10 - 3", {})
        assert result == 7
        assert isinstance(result, int)

    def test_multiplication_ints_returns_int(self):
        result = safe_eval("4 * 3", {})
        assert result == 12
        assert isinstance(result, int)

    def test_str_representation_int(self):
        """str(safe_eval('2 + 3', {})) should be '5', not '5.0'."""
        result = safe_eval("2 + 3", {})
        assert str(result) == "5"

    def test_str_representation_float(self):
        """str(safe_eval('2.0 + 3', {})) should be '5.0'."""
        result = safe_eval("2.0 + 3", {})
        assert str(result) == "5.0"

    def test_str_representation_division(self):
        """str(safe_eval('6 / 2', {})) should be '3.0' (float division)."""
        result = safe_eval("6 / 2", {})
        assert str(result) == "3.0"

    def test_str_representation_floor_div(self):
        """str(safe_eval('6 // 2', {})) should be '3' (int)."""
        result = safe_eval("6 // 2", {})
        assert str(result) == "3"
