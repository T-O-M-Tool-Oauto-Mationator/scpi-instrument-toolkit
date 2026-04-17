"""Pythonic error-handling tests for the REPL.

Covers the refactor that makes REPL expressions raise Python-style errors
(NameError, TypeError, ZeroDivisionError, ValueError, IndexError, KeyError)
and route them through ``ctx.report_error``. Key invariants:

* Failed expressions do NOT create or mutate variables.
* REPL stays usable after any caught error.
* ``print "{undef}"`` stays lenient (placeholder rule).
* ``set -e`` aborts on first error; ``set +e`` continues.
"""

import contextlib
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lab_instruments.repl.shell import InstrumentRepl


def _make_bare_repl(monkeypatch):
    """Build a REPL with no devices -- minimal scaffolding for error tests."""
    from lab_instruments.src import discovery as _disc

    monkeypatch.setattr(_disc.InstrumentDiscovery, "__init__", lambda self: None)
    monkeypatch.setattr(_disc.InstrumentDiscovery, "scan", lambda self, verbose=True: {})
    repl = InstrumentRepl(register_lifecycle=False)
    repl._scan_thread.join(timeout=5.0)
    return repl


@pytest.fixture
def repl(monkeypatch):
    r = _make_bare_repl(monkeypatch)
    yield r
    with contextlib.suppress(Exception):
        r.close()


# ---------------------------------------------------------------------------
# calc -- TypeError on mixed str/number operands
# ---------------------------------------------------------------------------


class TestCalcTypeError:
    def test_calc_str_plus_int_raises_typeerror(self, repl, capsys):
        repl.onecmd('foo = "hello"')
        capsys.readouterr()
        repl.onecmd("calc x = foo + 1")
        out = capsys.readouterr().out
        assert "TypeError" in out
        # The original foo stays untouched, x was never created.
        assert "x" not in repl.ctx.script_vars
        assert repl.ctx.command_had_error is True

    def test_calc_does_not_mutate_on_typeerror(self, repl, capsys):
        repl.onecmd('foo = "hello"')
        repl.onecmd("x = 42")
        capsys.readouterr()
        repl.onecmd("calc x = foo + 1")
        # Pre-existing x is preserved, not clobbered.
        assert repl.ctx.script_vars["x"] == 42


# ---------------------------------------------------------------------------
# calc -- NameError on unknown identifiers
# ---------------------------------------------------------------------------


class TestCalcNameError:
    def test_calc_undefined_identifier_raises_nameerror(self, repl, capsys):
        repl.onecmd("calc y = undefined_var + 1")
        out = capsys.readouterr().out
        assert "NameError" in out
        assert "undefined_var" in out
        assert "y" not in repl.ctx.script_vars

    def test_calc_undefined_function_raises_nameerror(self, repl, capsys):
        repl.onecmd("calc y = nosuchfn(3)")
        out = capsys.readouterr().out
        assert "NameError" in out
        assert "nosuchfn" in out


# ---------------------------------------------------------------------------
# ZeroDivisionError -- calc, assert, check, if-condition
# ---------------------------------------------------------------------------


class TestZeroDivisionPropagation:
    def test_calc_zero_division_raises(self, repl, capsys):
        repl.onecmd("calc z = 1 / 0")
        out = capsys.readouterr().out
        assert "ZeroDivisionError" in out
        assert "z" not in repl.ctx.script_vars

    def test_assert_zero_division_reports_and_aborts_interactive(self, repl, capsys):
        # Interactive assert that divides by zero prints the Python error class.
        # The interactive onecmd boundary catches the _AssertFailure and surfaces
        # it as a script-aborted message -- we just assert the ZeroDivisionError
        # text shows up.
        with contextlib.suppress(Exception):
            repl.onecmd("assert 1 / 0 > 0")
        out = capsys.readouterr().out
        assert "ZeroDivisionError" in out

    def test_check_zero_division_reports_and_continues(self, repl, capsys):
        repl.onecmd("check 1 / 0 > 0")
        out = capsys.readouterr().out
        assert "ZeroDivisionError" in out
        # REPL still usable afterwards:
        repl.onecmd("x = 7")
        assert repl.ctx.script_vars["x"] == 7

    def test_if_condition_zero_division_reports(self, repl, capsys):
        repl.onecmd("if 1 / 0 > 0")
        repl.onecmd("x = 1")
        repl.onecmd("end")
        out = capsys.readouterr().out
        assert "ZeroDivisionError" in out
        # Branch body not executed:
        assert "x" not in repl.ctx.script_vars


# ---------------------------------------------------------------------------
# set -e abort-on-error vs set +e continue
# ---------------------------------------------------------------------------


class TestSetDashE:
    def _run_script(self, repl, lines):
        """Execute a list of REPL lines via the script engine."""
        from lab_instruments.repl.script_engine.runner import run_expanded

        expanded = [(line, line) for line in lines]
        run_expanded(expanded, repl, repl.ctx, debug=False, source="<test>")

    def test_dash_e_aborts_after_first_error(self, repl, capsys):
        self._run_script(
            repl,
            [
                "set -e",
                "calc a = 1",
                "calc b = 1 / 0",
                "calc c = 2",
            ],
        )
        # a computed, b failed, c never ran because set -e.
        assert "a" in repl.ctx.script_vars
        assert "b" not in repl.ctx.script_vars
        assert "c" not in repl.ctx.script_vars

    def test_plus_e_continues_past_error(self, repl, capsys):
        self._run_script(
            repl,
            [
                "set +e",
                "calc a = 1",
                "calc b = 1 / 0",
                "calc c = 2",
            ],
        )
        assert "a" in repl.ctx.script_vars
        assert "b" not in repl.ctx.script_vars
        assert "c" in repl.ctx.script_vars


# ---------------------------------------------------------------------------
# print keeps placeholder for undefined vars -- the two-context rule
# ---------------------------------------------------------------------------


class TestPrintLenience:
    def test_print_undefined_leaves_placeholder(self, repl, capsys):
        repl.onecmd('print "hello {undef_var}"')
        out = capsys.readouterr().out
        assert "{undef_var}" in out
        # And does NOT raise or set error flag.
        assert repl.ctx.command_had_error is False


# ---------------------------------------------------------------------------
# Compound assignment with wrong type
# ---------------------------------------------------------------------------


class TestCompoundAssignTypeError:
    def test_plus_equal_on_string_raises_typeerror(self, repl, capsys):
        repl.onecmd('foo = "hello"')
        capsys.readouterr()
        repl.onecmd("foo += 1")
        out = capsys.readouterr().out
        assert "TypeError" in out
        # foo is unchanged:
        assert repl.ctx.script_vars["foo"] == "hello"


# ---------------------------------------------------------------------------
# Subscript errors -- IndexError / KeyError
# ---------------------------------------------------------------------------


class TestSubscriptErrors:
    def test_list_index_out_of_range_raises(self, repl, capsys):
        repl.onecmd("xs = [1, 2, 3]")
        capsys.readouterr()
        repl.onecmd("calc v = xs[10]")
        out = capsys.readouterr().out
        assert "IndexError" in out
        assert "v" not in repl.ctx.script_vars


# ---------------------------------------------------------------------------
# Error location format -- "at line N in <source>"
# ---------------------------------------------------------------------------


class TestErrorLocationFormat:
    def test_script_error_includes_line_and_source(self, repl, capsys, tmp_path):
        from lab_instruments.repl.script_engine.runner import run_expanded

        # Five-line script, error on line 3 (1-indexed in the formatted
        # message). Expanded list is [(cmd, src)] pairs; we stamp source
        # via the runner's source= argument.
        src_name = str(tmp_path / "script.repl")
        lines = [
            "calc a = 1",
            "calc b = 2",
            "calc c = nosuch + 1",
            "calc d = 3",
            "calc e = 4",
        ]
        expanded = [(line, line) for line in lines]
        run_expanded(expanded, repl, repl.ctx, debug=False, source=src_name)
        out = capsys.readouterr().out
        assert "NameError" in out
        assert "at line 3" in out
        assert src_name in out


# ---------------------------------------------------------------------------
# REPL survives every error class and stays usable
# ---------------------------------------------------------------------------


class TestReplDoesNotCrash:
    def test_repl_still_usable_after_nameerror(self, repl, capsys):
        repl.onecmd("calc bad = oops + 1")
        capsys.readouterr()
        repl.onecmd("good = 42")
        assert repl.ctx.script_vars["good"] == 42

    def test_repl_still_usable_after_typeerror(self, repl, capsys):
        repl.onecmd('s = "x"')
        repl.onecmd("calc bad = s + 1")
        capsys.readouterr()
        repl.onecmd("good = 7")
        assert repl.ctx.script_vars["good"] == 7

    def test_repl_still_usable_after_zerodiv(self, repl, capsys):
        repl.onecmd("calc bad = 1 / 0")
        capsys.readouterr()
        repl.onecmd("good = 9")
        assert repl.ctx.script_vars["good"] == 9
