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
import re

import pytest

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
        # Word boundary: prevent "at line 3456" from matching "at line 3".
        assert re.search(r"\bat line 3\b", out)
        assert src_name in out

    def test_script_error_includes_offending_line_text(self, repl, capsys, tmp_path):
        """Issue #82: error output must show the offending source line text.

        Lab scripts run 20-100+ lines. A line number alone forces students to
        cross-reference the file; printing the offending command inline
        eliminates the trip back to the editor.
        """
        from lab_instruments.repl.script_engine.runner import run_expanded

        src_name = str(tmp_path / "measure.scpi")
        lines = [
            "calc a = 1",
            "calc b = 2",
            "calc c = nosuch + 1",
            "calc d = 3",
        ]
        expanded = [(line, line) for line in lines]
        run_expanded(expanded, repl, repl.ctx, debug=False, source=src_name)
        out = capsys.readouterr().out
        assert "NameError" in out
        # The offending command text must appear verbatim so the user can
        # see exactly which line failed without opening the file.
        assert "calc c = nosuch + 1" in out
        # And it must follow the location pointer (line+source come first,
        # then the offending text on the next continuation line).
        loc_idx = out.find("at line 3")
        text_idx = out.find("calc c = nosuch + 1", loc_idx)
        assert loc_idx != -1 and text_idx != -1 and text_idx > loc_idx

    def test_line_text_cleared_between_commands(self, repl, capsys, tmp_path):
        """A successful command must not leave stale line text on ctx.

        Otherwise a later REPL error (typed after the script finished) would
        wrongly print the last script line as its source.
        """
        from lab_instruments.repl.script_engine.runner import run_expanded

        expanded = [("calc a = 1", "calc a = 1")]
        run_expanded(expanded, repl, repl.ctx, debug=False, source="x.scpi")
        assert repl.ctx.current_script_line_text is None
        assert repl.ctx.current_script_line is None
        assert repl.ctx.current_script_source is None


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
