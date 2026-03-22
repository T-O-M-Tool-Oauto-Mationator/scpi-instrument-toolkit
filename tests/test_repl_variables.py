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

    def test_dollar_style_still_works(self):
        assert substitute_vars("v=$voltage", {"voltage": "3.3"}) == "v=3.3"

    def test_both_styles_in_one_string(self):
        result = substitute_vars("{a} and $b", {"a": "1", "b": "2"})
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
        assert substitute_vars("$last", {}, measurements=store) == "7.0"


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


class TestSetDeprecation:
    def test_set_emits_deprecation_warning(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("set x 42")
        out = capsys.readouterr().out
        assert "deprecated" in out.lower()

    def test_set_still_assigns_variable(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("set x 42")
        assert repl.ctx.script_vars["x"] == "42"

    def test_set_minus_e_not_deprecated(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("set -e")
        out = capsys.readouterr().out
        assert "deprecated" not in out.lower()
        assert repl.ctx.exit_on_error is True

    def test_set_plus_e_not_deprecated(self, make_repl, capsys):
        repl = make_repl({})
        repl.ctx.exit_on_error = True
        repl.onecmd("set +e")
        out = capsys.readouterr().out
        assert "deprecated" not in out.lower()
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

    def test_print_dollar_var(self, make_repl, capsys):
        """$var substitution in print still works."""
        repl = make_repl({})
        repl.ctx.script_vars["msg"] = "hello"
        repl.onecmd("print $msg")
        out = capsys.readouterr().out
        assert "hello" in out

    def test_print_legacy_braces(self, make_repl, capsys):
        """${var} legacy syntax still works in print."""
        repl = make_repl({})
        repl.ctx.script_vars["v"] = "1"
        repl.onecmd("print ${v}")
        out = capsys.readouterr().out
        assert "1" in out

    def test_set_x_42_assigns(self, make_repl, capsys):
        """test_do_set_via_shell regression — set still assigns despite deprecation."""
        repl = make_repl({})
        repl.onecmd("set x 42")
        assert repl.ctx.script_vars["x"] == "42"

    def test_set_arithmetic(self, make_repl, capsys):
        """set with arithmetic expression still works."""
        repl = make_repl({})
        repl.onecmd("set doubled 2 * 5")
        assert float(repl.ctx.script_vars["doubled"]) == 10.0

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
