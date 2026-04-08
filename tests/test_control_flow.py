"""Tests for scripting control flow features:
while, if/elif/else, break, continue, assert, increment/compound ops, pyeval,
and Python variable injection via do_python.
"""

import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lab_instruments.repl.syntax import safe_eval_bool


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_repl(devices=None):
    """Build an InstrumentRepl with no instruments (or supplied devices)."""
    from lab_instruments.src import discovery as _disc

    _disc.InstrumentDiscovery.__init__ = lambda self: None
    _disc.InstrumentDiscovery.scan = lambda self, verbose=True: devices or {}
    from lab_instruments.repl import InstrumentRepl

    repl = InstrumentRepl()
    repl._scan_thread.join(timeout=5.0)
    repl._scan_done.wait(timeout=5.0)
    repl.devices = devices or {}
    return repl


@pytest.fixture
def repl():
    return _make_repl()


# ---------------------------------------------------------------------------
# Unit tests: safe_eval_bool
# ---------------------------------------------------------------------------


class TestSafeEvalBool:
    def test_simple_less_than_true(self):
        assert safe_eval_bool("x < 5", {"x": 3.0}) is True

    def test_simple_less_than_false(self):
        assert safe_eval_bool("x < 5", {"x": 7.0}) is False

    def test_greater_than(self):
        assert safe_eval_bool("y > 10", {"y": 15.0}) is True

    def test_equal(self):
        assert safe_eval_bool("x == 3", {"x": 3.0}) is True

    def test_not_equal(self):
        assert safe_eval_bool("x != 0", {"x": 1.0}) is True

    def test_less_equal(self):
        assert safe_eval_bool("x <= 3", {"x": 3.0}) is True

    def test_greater_equal(self):
        assert safe_eval_bool("x >= 3", {"x": 3.0}) is True

    def test_and_both_true(self):
        assert safe_eval_bool("x > 0 and y > 0", {"x": 1.0, "y": 2.0}) is True

    def test_and_one_false(self):
        assert safe_eval_bool("x > 0 and y > 0", {"x": 1.0, "y": -1.0}) is False

    def test_or_one_true(self):
        assert safe_eval_bool("x > 0 or y > 0", {"x": -1.0, "y": 1.0}) is True

    def test_or_both_false(self):
        assert safe_eval_bool("x > 0 or y > 0", {"x": -1.0, "y": -2.0}) is False

    def test_not_true(self):
        assert safe_eval_bool("not x > 5", {"x": 3.0}) is True

    def test_not_false(self):
        assert safe_eval_bool("not x > 5", {"x": 7.0}) is False

    def test_ampersand_alias(self):
        assert safe_eval_bool("x > 0 && y > 0", {"x": 1.0, "y": 1.0}) is True

    def test_pipe_alias(self):
        assert safe_eval_bool("x > 0 || y > 0", {"x": -1.0, "y": 1.0}) is True

    def test_string_equality(self):
        assert safe_eval_bool('s == "ok"', {"s": "ok"}) is True

    def test_string_inequality(self):
        assert safe_eval_bool('s != "fail"', {"s": "ok"}) is True

    def test_numeric_literal_only(self):
        assert safe_eval_bool("1 < 2", {}) is True

    def test_zero_is_falsy(self):
        assert safe_eval_bool("x", {"x": 0}) is False

    def test_nonzero_is_truthy(self):
        assert safe_eval_bool("x", {"x": 5}) is True

    def test_chained_comparison(self):
        assert safe_eval_bool("0 < x < 10", {"x": 5.0}) is True

    def test_chained_comparison_fails(self):
        assert safe_eval_bool("0 < x < 3", {"x": 5.0}) is False

    def test_unknown_name_raises(self):
        with pytest.raises(ValueError, match="Unknown name"):
            safe_eval_bool("undefined_var > 0", {})


# ---------------------------------------------------------------------------
# While loop tests
# ---------------------------------------------------------------------------


class TestWhileLoop:
    def test_basic_while_increments(self, repl):
        repl._run_script_lines(["x = 0", "while x < 3", "x++", "end"])
        assert float(repl.ctx.script_vars["x"]) == pytest.approx(3.0)

    def test_while_never_executes_when_false(self, repl):
        repl._run_script_lines(["x = 5", "while x < 3", "x++", "end"])
        assert float(repl.ctx.script_vars["x"]) == pytest.approx(5.0)

    def test_while_accumulates_value(self, repl):
        repl._run_script_lines(["total = 0", "i = 0", "while i < 5", "total += 1", "i++", "end"])
        assert float(repl.ctx.script_vars["total"]) == pytest.approx(5.0)
        assert float(repl.ctx.script_vars["i"]) == pytest.approx(5.0)

    def test_while_break_stops_early(self, repl):
        repl._run_script_lines([
            "x = 0",
            "while x < 100",
            "x++",
            "if x == 5",
            "break",
            "end",
            "end",
        ])
        assert float(repl.ctx.script_vars["x"]) == pytest.approx(5.0)

    def test_while_continue_skips_body(self, repl):
        # count should be 9, not 10 (the x==5 iteration is skipped)
        repl._run_script_lines([
            "x = 0",
            "count = 0",
            "while x < 10",
            "x++",
            "if x == 5",
            "continue",
            "end",
            "count += 1",
            "end",
        ])
        assert float(repl.ctx.script_vars["x"]) == pytest.approx(10.0)
        assert float(repl.ctx.script_vars["count"]) == pytest.approx(9.0)

    def test_nested_while_loops(self, repl):
        repl._run_script_lines([
            "total = 0",
            "i = 0",
            "while i < 3",
            "j = 0",
            "while j < 3",
            "total += 1",
            "j++",
            "end",
            "i++",
            "end",
        ])
        assert float(repl.ctx.script_vars["total"]) == pytest.approx(9.0)

    def test_while_decrement(self, repl):
        repl._run_script_lines(["x = 5", "while x > 0", "x--", "end"])
        assert float(repl.ctx.script_vars["x"]) == pytest.approx(0.0)

    def test_while_compound_step(self, repl):
        repl._run_script_lines(["x = 0", "while x < 10", "x += 3", "end"])
        # 0 → 3 → 6 → 9 → 12 (stops when x >= 10)
        assert float(repl.ctx.script_vars["x"]) == pytest.approx(12.0)


# ---------------------------------------------------------------------------
# If/elif/else tests
# ---------------------------------------------------------------------------


class TestIfElse:
    def test_if_true_branch_taken(self, repl):
        repl._run_script_lines(["x = 5", "if x > 3", "y = 1", "end"])
        assert repl.ctx.script_vars.get("y") is not None
        assert float(repl.ctx.script_vars["y"]) == pytest.approx(1.0)

    def test_if_false_branch_not_taken(self, repl):
        repl._run_script_lines(["x = 1", "if x > 3", "y = 99", "end"])
        assert "y" not in repl.ctx.script_vars

    def test_if_else_true(self, repl):
        repl._run_script_lines(["x = 5", "if x > 3", "y = 1", "else", "y = 0", "end"])
        assert float(repl.ctx.script_vars["y"]) == pytest.approx(1.0)

    def test_if_else_false(self, repl):
        repl._run_script_lines(["x = 1", "if x > 3", "y = 1", "else", "y = 0", "end"])
        assert float(repl.ctx.script_vars["y"]) == pytest.approx(0.0)

    def test_elif_first_matches(self, repl):
        repl._run_script_lines([
            "x = 1",
            "if x == 1",
            "result = 10",
            "elif x == 2",
            "result = 20",
            "else",
            "result = 30",
            "end",
        ])
        assert float(repl.ctx.script_vars["result"]) == pytest.approx(10.0)

    def test_elif_second_matches(self, repl):
        repl._run_script_lines([
            "x = 2",
            "if x == 1",
            "result = 10",
            "elif x == 2",
            "result = 20",
            "else",
            "result = 30",
            "end",
        ])
        assert float(repl.ctx.script_vars["result"]) == pytest.approx(20.0)

    def test_elif_else_taken(self, repl):
        repl._run_script_lines([
            "x = 3",
            "if x == 1",
            "result = 10",
            "elif x == 2",
            "result = 20",
            "else",
            "result = 30",
            "end",
        ])
        assert float(repl.ctx.script_vars["result"]) == pytest.approx(30.0)

    def test_nested_if(self, repl):
        repl._run_script_lines([
            "x = 5",
            "y = 3",
            "if x > 3",
            "if y > 2",
            "z = 99",
            "end",
            "end",
        ])
        assert float(repl.ctx.script_vars["z"]) == pytest.approx(99.0)

    def test_nested_if_inner_false(self, repl):
        repl._run_script_lines([
            "x = 5",
            "y = 1",
            "if x > 3",
            "if y > 2",
            "z = 99",
            "end",
            "end",
        ])
        assert "z" not in repl.ctx.script_vars

    def test_if_with_string_comparison(self, repl):
        repl._run_script_lines([
            'mode = "fast"',
            'if mode == "fast"',
            "speed = 100",
            "else",
            "speed = 10",
            "end",
        ])
        assert float(repl.ctx.script_vars["speed"]) == pytest.approx(100.0)

    def test_if_inside_while(self, repl):
        repl._run_script_lines([
            "x = 0",
            "hits = 0",
            "while x < 10",
            "x++",
            "if x == 3",
            "hits += 1",
            "end",
            "end",
        ])
        assert float(repl.ctx.script_vars["hits"]) == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# Assert tests
# ---------------------------------------------------------------------------


class TestAssert:
    def test_assert_passes(self, repl, capsys):
        repl.onecmd("assert 1 == 1")
        out = capsys.readouterr().out
        assert "PASS" in out

    def test_assert_passes_with_vars(self, repl, capsys):
        repl.ctx.script_vars["v"] = "5.0"
        repl.onecmd("assert v == 5")
        out = capsys.readouterr().out
        assert "PASS" in out

    def test_assert_passes_with_message(self, repl, capsys):
        repl.onecmd('assert 1 == 1 "voltage check"')
        out = capsys.readouterr().out
        assert "PASS" in out
        assert "voltage check" in out

    def test_assert_fail_raises(self, repl):
        from lab_instruments.repl.script_engine.runner import _AssertFailure

        with pytest.raises(_AssertFailure):
            repl.onecmd("assert 1 == 2")

    def test_assert_fail_with_message(self, repl, capsys):
        from lab_instruments.repl.script_engine.runner import _AssertFailure

        with pytest.raises(_AssertFailure):
            repl.onecmd('assert 0 == 1 "should fail"')
        out = capsys.readouterr().out
        assert "should fail" in out

    def test_assert_stops_script_on_failure(self, repl):
        """After assert fails, subsequent runtime commands don't execute."""
        # Use a runtime command (counter++) as a sentinel — it only runs if assert passes
        repl.ctx.script_vars["counter"] = "0"
        repl._run_script_lines(["assert counter == 99", "counter++"])
        # counter++ is a runtime cmd; assert failed → it never ran → counter stays 0
        assert float(repl.ctx.script_vars["counter"]) == pytest.approx(0.0)

    def test_assert_script_continues_on_pass(self, repl):
        """After assert passes, subsequent runtime commands execute."""
        repl.ctx.script_vars["x"] = "5"
        repl.ctx.script_vars["counter"] = "0"
        repl._run_script_lines(["assert x == 5", "counter++"])
        assert float(repl.ctx.script_vars["counter"]) == pytest.approx(1.0)

    def test_assert_no_arg_prints_usage(self, repl, capsys):
        repl.onecmd("assert")
        out = capsys.readouterr().out
        assert "Usage" in out or "assert" in out.lower()

    def test_assert_invalid_expression_sets_error(self, repl, capsys):
        repl.onecmd("assert undefined_var > 0")
        out = capsys.readouterr().out
        assert "assert" in out.lower() or "error" in out.lower() or "could not" in out.lower()
        assert repl.ctx.command_had_error


# ---------------------------------------------------------------------------
# Increment / compound assignment tests
# ---------------------------------------------------------------------------


class TestIncrement:
    def test_postfix_increment(self, repl):
        repl.onecmd("x = 5")
        repl.onecmd("x++")
        assert float(repl.ctx.script_vars["x"]) == pytest.approx(6.0)

    def test_postfix_decrement(self, repl):
        repl.onecmd("x = 5")
        repl.onecmd("x--")
        assert float(repl.ctx.script_vars["x"]) == pytest.approx(4.0)

    def test_prefix_increment(self, repl):
        repl.onecmd("x = 10")
        repl.onecmd("++x")
        assert float(repl.ctx.script_vars["x"]) == pytest.approx(11.0)

    def test_prefix_decrement(self, repl):
        repl.onecmd("x = 10")
        repl.onecmd("--x")
        assert float(repl.ctx.script_vars["x"]) == pytest.approx(9.0)

    def test_increment_from_zero(self, repl):
        repl.onecmd("n = 0")
        repl.onecmd("n++")
        assert float(repl.ctx.script_vars["n"]) == pytest.approx(1.0)

    def test_add_assign(self, repl):
        repl.onecmd("x = 10")
        repl.onecmd("x += 3")
        assert float(repl.ctx.script_vars["x"]) == pytest.approx(13.0)

    def test_sub_assign(self, repl):
        repl.onecmd("x = 10")
        repl.onecmd("x -= 4")
        assert float(repl.ctx.script_vars["x"]) == pytest.approx(6.0)

    def test_mul_assign(self, repl):
        repl.onecmd("x = 3")
        repl.onecmd("x *= 4")
        assert float(repl.ctx.script_vars["x"]) == pytest.approx(12.0)

    def test_div_assign(self, repl):
        repl.onecmd("x = 10")
        repl.onecmd("x /= 2")
        assert float(repl.ctx.script_vars["x"]) == pytest.approx(5.0)

    def test_compound_assign_expression(self, repl):
        repl.onecmd("x = 10")
        repl.onecmd("y = 3")
        repl.onecmd("x += y")
        assert float(repl.ctx.script_vars["x"]) == pytest.approx(13.0)

    def test_multiple_increments(self, repl):
        repl.onecmd("n = 0")
        for _ in range(5):
            repl.onecmd("n++")
        assert float(repl.ctx.script_vars["n"]) == pytest.approx(5.0)

    def test_increment_in_script(self, repl):
        repl._run_script_lines(["n = 0", "n++", "n++", "n++"])
        assert float(repl.ctx.script_vars["n"]) == pytest.approx(3.0)


# ---------------------------------------------------------------------------
# pyeval tests
# ---------------------------------------------------------------------------


class TestPyeval:
    def test_basic_arithmetic(self, repl):
        repl.onecmd("result = pyeval 5.0 * 2.5")
        assert float(repl.ctx.script_vars["result"]) == pytest.approx(12.5)

    def test_addition(self, repl):
        repl.onecmd("result = pyeval 3 + 4")
        assert float(repl.ctx.script_vars["result"]) == pytest.approx(7.0)

    def test_math_sqrt(self, repl):
        repl.onecmd("result = pyeval sqrt(4.0)")
        assert float(repl.ctx.script_vars["result"]) == pytest.approx(2.0)

    def test_math_pi(self, repl):
        import math

        repl.onecmd("result = pyeval pi")
        assert float(repl.ctx.script_vars["result"]) == pytest.approx(math.pi)

    def test_uses_script_vars(self, repl):
        repl.ctx.script_vars["a"] = "3"
        repl.ctx.script_vars["b"] = "4"
        repl.onecmd("c = pyeval a * b")
        assert float(repl.ctx.script_vars["c"]) == pytest.approx(12.0)

    def test_uses_vars_dict(self, repl):
        repl.ctx.script_vars["voltage"] = "5.0"
        repl.onecmd("v2 = pyeval vars['voltage']")
        # vars dict gives string values
        assert repl.ctx.script_vars["v2"] == "5.0"

    def test_pyeval_in_script(self, repl):
        repl._run_script_lines([
            "base = 10",
            "exp = 2",
            "result = pyeval base ** exp",
        ])
        assert float(repl.ctx.script_vars["result"]) == pytest.approx(100.0)

    def test_pyeval_complex_expression(self, repl):
        repl.onecmd("result = pyeval round(3.14159, 2)")
        assert float(repl.ctx.script_vars["result"]) == pytest.approx(3.14)

    def test_pyeval_integer_result(self, repl):
        repl.onecmd("result = pyeval 7 // 2")
        assert int(float(repl.ctx.script_vars["result"])) == 3

    def test_pyeval_bad_expression_sets_error(self, repl, capsys):
        repl.onecmd("result = pyeval 1/0")
        out = capsys.readouterr().out
        assert "pyeval" in out.lower() or "error" in out.lower() or "failed" in out.lower()
        assert repl.ctx.command_had_error


# ---------------------------------------------------------------------------
# Python variable injection tests
# ---------------------------------------------------------------------------


class TestPythonVarInjection:
    def _run_python_script(self, repl, code: str) -> str:
        """Write *code* to a temp file, exec via repl, return captured stdout."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            fname = f.name
        try:
            import io
            from contextlib import redirect_stdout

            buf = io.StringIO()
            with redirect_stdout(buf):
                repl.onecmd(f"python {fname}")
            return buf.getvalue()
        finally:
            os.unlink(fname)

    def test_float_var_injected(self, repl, capsys):
        repl.ctx.script_vars["voltage"] = "5.0"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("assert isinstance(voltage, float), f'got {type(voltage)}'\n")
            f.write("assert voltage == 5.0\n")
            fname = f.name
        try:
            repl.onecmd(f"python {fname}")
            out = capsys.readouterr().out
            assert "failed" not in out.lower()
        finally:
            os.unlink(fname)

    def test_int_var_injected(self, repl, capsys):
        repl.ctx.script_vars["steps"] = "10"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("assert isinstance(steps, int), f'got {type(steps)}'\n")
            f.write("assert steps == 10\n")
            fname = f.name
        try:
            repl.onecmd(f"python {fname}")
            out = capsys.readouterr().out
            assert "failed" not in out.lower()
        finally:
            os.unlink(fname)

    def test_string_var_injected(self, repl, capsys):
        repl.ctx.script_vars["label"] = "vtest"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("assert isinstance(label, str), f'got {type(label)}'\n")
            f.write("assert label == 'vtest'\n")
            fname = f.name
        try:
            repl.onecmd(f"python {fname}")
            out = capsys.readouterr().out
            assert "failed" not in out.lower()
        finally:
            os.unlink(fname)

    def test_vars_dict_available(self, repl, capsys):
        repl.ctx.script_vars["x"] = "42"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("assert 'x' in vars, 'vars dict missing x'\n")
            f.write("assert vars['x'] == '42'\n")
            fname = f.name
        try:
            repl.onecmd(f"python {fname}")
            out = capsys.readouterr().out
            assert "failed" not in out.lower()
        finally:
            os.unlink(fname)

    def test_multiple_vars_injected(self, repl, capsys):
        repl.ctx.script_vars["v"] = "3.3"
        repl.ctx.script_vars["i"] = "0.5"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("power = v * i\n")
            f.write("assert abs(power - 1.65) < 1e-9\n")
            fname = f.name
        try:
            repl.onecmd(f"python {fname}")
            out = capsys.readouterr().out
            assert "failed" not in out.lower()
        finally:
            os.unlink(fname)

    def test_no_vars_does_not_crash(self, repl, capsys):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("result = 2 + 2\n")
            f.write("assert result == 4\n")
            fname = f.name
        try:
            repl.onecmd(f"python {fname}")
            out = capsys.readouterr().out
            assert "failed" not in out.lower()
        finally:
            os.unlink(fname)


# ---------------------------------------------------------------------------
# Break / continue at top level (outside loops — should be gracefully ignored)
# ---------------------------------------------------------------------------


class TestBreakContinueTopLevel:
    def test_break_outside_loop_ignored_in_script(self, repl, capsys):
        """break at the top level emits a warning and continues."""
        repl._run_script_lines(["x = 1", "break", "x = 99"])
        out = capsys.readouterr().out
        # Script should warn about break outside loop
        assert "break" in out.lower() or "outside" in out.lower() or "loop" in out.lower()

    def test_continue_outside_loop_ignored_in_script(self, repl, capsys):
        """continue at the top level emits a warning and continues."""
        repl._run_script_lines(["x = 1", "continue", "x = 99"])
        out = capsys.readouterr().out
        assert "continue" in out.lower() or "outside" in out.lower() or "loop" in out.lower()
