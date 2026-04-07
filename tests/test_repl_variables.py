"""Tests for the Pythonic print/variable syntax in REPL scripts.

Covers:
  - {var} f-string interpolation in print
  - var = expr Python-style assignment
  - Deprecation warning on 'set var expr'
  - substitute_vars unit tests
  - Regression: existing $var, ${var}, set, print behavior unchanged
"""

from lab_instruments.repl.syntax import substitute_vars

# ---------------------------------------------------------------------------
# Unit tests: substitute_vars
# ---------------------------------------------------------------------------


class TestSubstituteVars:
    def test_fstring_style(self):
        assert substitute_vars("v={voltage}", {"voltage": "5.0"}) == "v=5.0"

    def test_fstring_in_sentence(self):
        assert (
            substitute_vars("Setting {voltage}V to {label}", {"voltage": "5.0", "label": "vtest"})
            == "Setting 5.0V to vtest"
        )

    def test_dollar_style_no_longer_resolves(self):
        assert substitute_vars("v=$voltage", {"voltage": "3.3"}) == "v=$voltage"

    def test_only_brace_style(self):
        result = substitute_vars("{a} and {b}", {"a": "1", "b": "2"})
        assert result == "1 and 2"

    def test_unresolved_fstring_left_as_is(self):
        assert substitute_vars("{unknown}", {}) == "{unknown}"

    def test_unresolved_dollar_left_as_is(self):
        assert substitute_vars("$unknown", {}) == "$unknown"

    def test_measurement_store_via_fstring(self):
        """Measurement labels are reachable via {label} syntax."""
        from lab_instruments.repl.measurement_store import MeasurementStore

        store = MeasurementStore()
        store.record("vout", 4.95, "V", "dmm")
        result = substitute_vars("measured {vout}V", {}, measurements=store)
        assert result == "measured 4.95V"

    def test_last_keyword(self):
        from lab_instruments.repl.measurement_store import MeasurementStore

        store = MeasurementStore()
        store.record("x", 7.0, "", "test")
        assert substitute_vars("{last}", {}, measurements=store) == "7.0"


# ---------------------------------------------------------------------------
# REPL integration: print command
# ---------------------------------------------------------------------------


class TestPrintCommand:
    def test_print_plain_text(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("print hello world")
        out = capsys.readouterr().out
        assert "hello world" in out

    def test_print_quoted_fstring(self, make_repl, capsys):
        repl = make_repl({})
        repl.ctx.script_vars["v"] = "3.3"
        repl.onecmd('print "Voltage is {v}V"')
        out = capsys.readouterr().out
        assert "Voltage is 3.3V" in out

    def test_print_unquoted_fstring(self, make_repl, capsys):
        repl = make_repl({})
        repl.ctx.script_vars["label"] = "vtest"
        repl.onecmd("print label={label}")
        out = capsys.readouterr().out
        assert "label=vtest" in out

    def test_print_no_color_codes(self, make_repl, capsys):
        """print must output plain text — no ANSI escape sequences."""
        repl = make_repl({})
        capsys.readouterr()  # flush REPL init messages
        repl.onecmd("print hello")
        out = capsys.readouterr().out
        assert "\033[" not in out

    def test_print_empty(self, make_repl, capsys):
        repl = make_repl({})
        capsys.readouterr()  # flush REPL init messages
        repl.onecmd("print")
        out = capsys.readouterr().out
        assert out == "\n"

    def test_print_single_quoted_fstring(self, make_repl, capsys):
        repl = make_repl({})
        repl.ctx.script_vars["x"] = "42"
        repl.onecmd("print 'x={x}'")
        out = capsys.readouterr().out
        assert "x=42" in out

    def test_print_unresolved_fstring_left_as_is(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd('print "{unknown}"')
        out = capsys.readouterr().out
        assert "{unknown}" in out


# ---------------------------------------------------------------------------
# REPL integration: Python-style assignment (var = expr)
# ---------------------------------------------------------------------------


class TestAssignmentSyntax:
    def test_assign_simple_value(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("voltage = 5.0")
        assert repl.ctx.script_vars["voltage"] == "5.0"

    def test_assign_integer(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("count = 3")
        assert repl.ctx.script_vars["count"] == "3"

    def test_assign_string_value(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("label = mytest")
        assert repl.ctx.script_vars["label"] == "mytest"

    def test_assign_expression(self, make_repl, capsys):
        repl = make_repl({})
        repl.ctx.script_vars["voltage"] = "5.0"
        repl.onecmd("doubled = voltage * 2")
        assert repl.ctx.script_vars["doubled"] == "10.0"

    def test_assign_prints_success(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("x = 7")
        out = capsys.readouterr().out
        assert "x" in out
        assert "7" in out

    def test_assign_no_deprecation_warning(self, make_repl, capsys):
        """var = expr must NOT emit a deprecation warning."""
        repl = make_repl({})
        repl.onecmd("v = 1.0")
        out = capsys.readouterr().out
        assert "deprecated" not in out.lower()

    def test_assigned_var_accessible_in_print(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("myval = 9.9")
        capsys.readouterr()
        repl.onecmd('print "result={myval}"')
        out = capsys.readouterr().out
        assert "result=9.9" in out


# ---------------------------------------------------------------------------
# REPL integration: set deprecation
# ---------------------------------------------------------------------------


class TestSetBehavior:
    def test_set_assignment_prints_error(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("set x 42")
        out = capsys.readouterr().out
        assert "var = expr" in out.lower() or "unknown" in out.lower()
        assert "x" not in repl.ctx.script_vars

    def test_set_minus_e_works(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("set -e")
        capsys.readouterr()
        assert repl.ctx.exit_on_error is True

    def test_set_plus_e_works(self, make_repl, capsys):
        repl = make_repl({})
        repl.ctx.exit_on_error = True
        repl.onecmd("set +e")
        capsys.readouterr()
        assert repl.ctx.exit_on_error is False


# ---------------------------------------------------------------------------
# Regression tests — existing behavior must not break
# ---------------------------------------------------------------------------


class TestRegressions:
    def test_print_hello_world(self, make_repl, capsys):
        """test_do_print_via_shell regression."""
        repl = make_repl({})
        repl.onecmd("print hello world")
        out = capsys.readouterr().out
        assert "hello world" in out

    def test_print_brace_var(self, make_repl, capsys):
        """{var} substitution in print works."""
        repl = make_repl({})
        repl.ctx.script_vars["msg"] = "hello"
        repl.onecmd("print {msg}")
        out = capsys.readouterr().out
        assert "hello" in out

    def test_dollar_syntax_not_resolved(self, make_repl, capsys):
        """$var is no longer resolved — left as literal."""
        repl = make_repl({})
        repl.ctx.script_vars["v"] = "1"
        repl.onecmd("print $v")
        out = capsys.readouterr().out
        assert "$v" in out

    def test_set_x_42_prints_error(self, make_repl, capsys):
        """set for assignment is removed — prints error message."""
        repl = make_repl({})
        repl.onecmd("set x 42")
        out = capsys.readouterr().out
        assert "var = expr" in out.lower() or "unknown" in out.lower()
        assert "x" not in repl.ctx.script_vars

    def test_set_arithmetic_prints_error(self, make_repl, capsys):
        """set for assignment is removed — prints error message."""
        repl = make_repl({})
        repl.onecmd("set doubled 2 * 5")
        out = capsys.readouterr().out
        assert "var = expr" in out.lower() or "unknown" in out.lower()
        assert "doubled" not in repl.ctx.script_vars

    def test_semicolon_splitting(self, make_repl, capsys):
        """Semicolons still split commands."""
        repl = make_repl({})
        repl.onecmd("print hello ; print world")
        out = capsys.readouterr().out
        assert "hello" in out
        assert "world" in out

    def test_print_hi_plain(self, make_repl, capsys):
        """Simple print hi works."""
        repl = make_repl({})
        repl.onecmd("print hi")
        out = capsys.readouterr().out
        assert "hi" in out


# ---------------------------------------------------------------------------
# unset command
# ---------------------------------------------------------------------------


class TestUnsetCommand:
    def test_unset_removes_variable(self, make_repl, capsys):
        repl = make_repl({})
        repl.ctx.script_vars["voltage"] = "5.0"
        repl.onecmd("unset voltage")
        assert "voltage" not in repl.ctx.script_vars

    def test_unset_nonexistent_warns(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("unset nothere")
        out = capsys.readouterr().out
        assert "not defined" in out or "nothere" in out

    def test_unset_no_args_warns(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("unset")
        out = capsys.readouterr().out
        assert "Usage" in out or "usage" in out.lower() or out != ""

    def test_unset_stops_substitution(self, make_repl, capsys):
        repl = make_repl({})
        repl.ctx.script_vars["x"] = "42"
        repl.onecmd("unset x")
        capsys.readouterr()
        repl.onecmd('print "{x}"')
        out = capsys.readouterr().out
        assert "42" not in out
        assert "{x}" in out


# ---------------------------------------------------------------------------
# calc assignment: result = calc <expr> [unit=X]
# ---------------------------------------------------------------------------


class TestCalcAssignment:
    def test_calc_assign_simple_expression(self, make_repl, capsys):
        """result = calc 2 * 3 should store '6' in script_vars."""
        repl = make_repl({})
        repl.onecmd("result = calc 2 * 3")
        assert repl.ctx.script_vars["result"] == "6"

    def test_calc_assign_with_variables(self, make_repl, capsys):
        """result = calc {a} * {b} should substitute and compute."""
        repl = make_repl({})
        repl.ctx.script_vars["a"] = "5"
        repl.ctx.script_vars["b"] = "3"
        repl.onecmd("result = calc {a} * {b}")
        assert repl.ctx.script_vars["result"] == "15"

    def test_calc_assign_with_unit(self, make_repl, capsys):
        """result = calc 5 * 2 unit=W should store value and record unit."""
        repl = make_repl({})
        repl.onecmd("result = calc 5 * 2 unit=W")
        assert repl.ctx.script_vars["result"] == "10"
        entry = repl.ctx.measurements.get_by_label("result")
        assert entry is not None
        assert entry["value"] == 10
        assert entry["unit"] == "W"

    def test_calc_assign_records_to_measurements(self, make_repl, capsys):
        """Calc assignment should record in measurement store with source='calc'."""
        repl = make_repl({})
        repl.onecmd("power = calc 3.3 * 0.5 unit=W")
        entry = repl.ctx.measurements.get_by_label("power")
        assert entry is not None
        assert entry["source"] == "calc"
        assert abs(entry["value"] - 1.65) < 1e-9

    def test_calc_assign_var_usable_in_subsequent_commands(self, make_repl, capsys):
        """Variable set by calc assignment should be usable via {var}."""
        repl = make_repl({})
        repl.onecmd("x = calc 7 + 3")
        capsys.readouterr()
        repl.onecmd('print "x={x}"')
        out = capsys.readouterr().out
        assert "x=10" in out

    def test_calc_assign_prints_output(self, make_repl, capsys):
        """Calc assignment should print the result."""
        repl = make_repl({})
        repl.onecmd("power = calc 10 * 2 unit=W")
        out = capsys.readouterr().out
        assert "power" in out
        assert "20" in out

    def test_calc_assign_invalid_expr_shows_error(self, make_repl, capsys):
        """Invalid expression should print error and not set variable."""
        repl = make_repl({})
        repl.onecmd("bad = calc foo bar baz")
        out = capsys.readouterr().out
        assert "bad" not in repl.ctx.script_vars
        assert "calc failed" in out.lower() or "error" in out.lower()

    def test_calc_assign_empty_expr_shows_warning(self, make_repl, capsys):
        """Empty calc expression should warn."""
        repl = make_repl({})
        repl.onecmd("x = calc")
        out = capsys.readouterr().out
        assert "x" not in repl.ctx.script_vars
        assert "expects" in out.lower() or "expression" in out.lower()

    def test_standalone_calc_unchanged(self, make_repl, capsys):
        """Standalone calc (not assignment) should still work as before."""
        repl = make_repl({})
        # Record an initial measurement so do_calc doesn't bail out
        repl.ctx.measurements.record("seed", 1.0, "", "test")
        repl.onecmd("calc power = 5 * 2 unit=W")
        entry = repl.ctx.measurements.get_by_label("power")
        assert entry is not None
        assert entry["value"] == 10
        # Standalone calc should NOT set script_vars
        assert "power" not in repl.ctx.script_vars

    def test_calc_assign_no_unit(self, make_repl, capsys):
        """Calc assignment without unit= should still work."""
        repl = make_repl({})
        repl.onecmd("val = calc 100 / 4")
        assert repl.ctx.script_vars["val"] == "25.0"
        entry = repl.ctx.measurements.get_by_label("val")
        assert entry is not None
        assert entry["unit"] == ""


# ---------------------------------------------------------------------------
# pyeval command
# ---------------------------------------------------------------------------


class TestPyeval:
    def test_pyeval_basic_expression(self, make_repl, capsys):
        """pyeval should evaluate a simple arithmetic expression."""
        repl = make_repl({})
        repl.onecmd("pyeval 2 ** 10")
        out = capsys.readouterr().out
        assert "1024" in out

    def test_pyeval_accesses_script_vars(self, make_repl, capsys):
        """pyeval should have access to REPL script variables as names."""
        repl = make_repl({})
        repl.onecmd("voltage = 3.3")
        repl.onecmd("current = 0.5")
        capsys.readouterr()
        repl.onecmd("pyeval voltage * current")
        out = capsys.readouterr().out
        assert "1.65" in out

    def test_pyeval_stores_result_in_underscore(self, make_repl, capsys):
        """pyeval result should be stored in the _ variable."""
        repl = make_repl({})
        repl.onecmd("pyeval 42 + 8")
        assert repl.ctx.script_vars["_"] == "50"

    def test_pyeval_with_measurements(self, make_repl, capsys):
        """pyeval should access measurements via the m dict."""
        repl = make_repl({})
        repl.ctx.measurements.record("vout", 4.95, "V", "dmm")
        capsys.readouterr()
        repl.onecmd("pyeval m['vout']")
        out = capsys.readouterr().out
        assert "4.95" in out

    def test_pyeval_with_fstring(self, make_repl, capsys):
        """pyeval should support f-strings."""
        repl = make_repl({})
        repl.onecmd("x = 3.14159")
        capsys.readouterr()
        repl.onecmd("pyeval f'pi is approximately {float(vars[\"x\"]):.2f}'")
        out = capsys.readouterr().out
        assert "pi is approximately 3.14" in out

    def test_pyeval_with_list_comprehension(self, make_repl, capsys):
        """pyeval should support list comprehensions."""
        repl = make_repl({})
        capsys.readouterr()
        repl.onecmd("pyeval [x**2 for x in range(5)]")
        out = capsys.readouterr().out
        assert "[0, 1, 4, 9, 16]" in out

    def test_pyeval_error_handling(self, make_repl, capsys):
        """pyeval should print an error for invalid expressions."""
        repl = make_repl({})
        capsys.readouterr()
        repl.onecmd("pyeval 1/0")
        out = capsys.readouterr().out
        assert "pyeval" in out.lower() or "error" in out.lower() or "division" in out.lower()

    def test_pyeval_vars_dict_access(self, make_repl, capsys):
        """pyeval should be able to access vars dict."""
        repl = make_repl({})
        repl.onecmd("a = 10")
        repl.onecmd("b = 20")
        capsys.readouterr()
        repl.onecmd("pyeval sorted(vars.keys())")
        out = capsys.readouterr().out
        assert "a" in out
        assert "b" in out

    def test_pyeval_empty_shows_usage(self, make_repl, capsys):
        """pyeval with no args should show usage."""
        repl = make_repl({})
        capsys.readouterr()
        repl.onecmd("pyeval")
        out = capsys.readouterr().out
        assert "pyeval" in out.lower() or "expression" in out.lower()


# ---------------------------------------------------------------------------
# Increment/decrement and compound assignment
# ---------------------------------------------------------------------------


class TestCompoundAssignment:
    def test_increment_existing(self, make_repl, capsys):
        """x++ should increment an existing variable by 1."""
        repl = make_repl({})
        repl.onecmd("x = 5")
        repl.onecmd("x++")
        assert float(repl.ctx.script_vars["x"]) == 6.0

    def test_increment_nonexistent(self, make_repl, capsys):
        """x++ when x doesn't exist should start from 0 and become 1."""
        repl = make_repl({})
        repl.onecmd("x++")
        assert float(repl.ctx.script_vars["x"]) == 1.0

    def test_decrement_existing(self, make_repl, capsys):
        """x-- should decrement an existing variable by 1."""
        repl = make_repl({})
        repl.onecmd("x = 10")
        repl.onecmd("x--")
        assert float(repl.ctx.script_vars["x"]) == 9.0

    def test_decrement_nonexistent(self, make_repl, capsys):
        """x-- when x doesn't exist should start from 0 and become -1."""
        repl = make_repl({})
        repl.onecmd("x--")
        assert float(repl.ctx.script_vars["x"]) == -1.0

    def test_plus_equal(self, make_repl, capsys):
        """x += 5 should add 5 to x."""
        repl = make_repl({})
        repl.onecmd("x = 10")
        repl.onecmd("x += 5")
        assert float(repl.ctx.script_vars["x"]) == 15.0

    def test_minus_equal(self, make_repl, capsys):
        """x -= 2 should subtract 2 from x."""
        repl = make_repl({})
        repl.onecmd("x = 10")
        repl.onecmd("x -= 2")
        assert float(repl.ctx.script_vars["x"]) == 8.0

    def test_multiply_equal(self, make_repl, capsys):
        """x *= 3 should multiply x by 3."""
        repl = make_repl({})
        repl.onecmd("x = 4")
        repl.onecmd("x *= 3")
        assert float(repl.ctx.script_vars["x"]) == 12.0

    def test_divide_equal(self, make_repl, capsys):
        """x /= 4 should divide x by 4."""
        repl = make_repl({})
        repl.onecmd("x = 20")
        repl.onecmd("x /= 4")
        assert float(repl.ctx.script_vars["x"]) == 5.0

    def test_floor_divide_equal(self, make_repl, capsys):
        """x //= 2 should floor divide x by 2."""
        repl = make_repl({})
        repl.onecmd("x = 7")
        repl.onecmd("x //= 2")
        assert float(repl.ctx.script_vars["x"]) == 3.0

    def test_power_equal(self, make_repl, capsys):
        """x **= 3 should raise x to the power 3."""
        repl = make_repl({})
        repl.onecmd("x = 2")
        repl.onecmd("x **= 3")
        assert float(repl.ctx.script_vars["x"]) == 8.0

    def test_modulo_equal(self, make_repl, capsys):
        """x %= 2 should compute x modulo 2."""
        repl = make_repl({})
        repl.onecmd("x = 7")
        repl.onecmd("x %= 2")
        assert float(repl.ctx.script_vars["x"]) == 1.0

    def test_compound_with_variable_rhs(self, make_repl, capsys):
        """x += y should add the value of y to x."""
        repl = make_repl({})
        repl.onecmd("x = 10")
        repl.onecmd("y = 5")
        repl.onecmd("x += {y}")
        assert float(repl.ctx.script_vars["x"]) == 15.0

    def test_multiple_increments(self, make_repl, capsys):
        """Multiple x++ calls should accumulate."""
        repl = make_repl({})
        repl.onecmd("x = 0")
        repl.onecmd("x++")
        repl.onecmd("x++")
        repl.onecmd("x++")
        assert float(repl.ctx.script_vars["x"]) == 3.0

    def test_compound_from_zero(self, make_repl, capsys):
        """Compound assignment on non-existent var should start from 0."""
        repl = make_repl({})
        repl.onecmd("x += 5")
        assert float(repl.ctx.script_vars["x"]) == 5.0
