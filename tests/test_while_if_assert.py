"""Tests for while, if/elif/else, and assert support in the SCPI script engine."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def make_repl(devices=None):
    from lab_instruments.src import discovery as _disc

    _disc.InstrumentDiscovery.__init__ = lambda self: None
    _disc.InstrumentDiscovery.scan = lambda self, verbose=True: devices or {}
    from lab_instruments.repl import InstrumentRepl

    repl = InstrumentRepl(auto_scan=True)
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
# While loop tests
# ---------------------------------------------------------------------------


class TestWhileLoop:
    def test_basic_count_to_10(self, repl):
        """While loop counting x from 0 to 10."""
        repl.onecmd("x = 0")
        repl.onecmd("while x < 10")
        repl.onecmd("x++")
        repl.onecmd("end")
        assert float(repl.ctx.script_vars["x"]) == 10.0

    def test_count_to_5(self, repl):
        """While loop counting to 5."""
        repl.onecmd("count = 0")
        repl.onecmd("while count < 5")
        repl.onecmd("count++")
        repl.onecmd("end")
        assert float(repl.ctx.script_vars["count"]) == 5.0

    def test_condition_false_initially(self, repl):
        """While loop with false condition should not execute body."""
        repl.onecmd("x = 100")
        repl.onecmd("while x < 0")
        repl.onecmd("x = 999")
        repl.onecmd("end")
        assert float(repl.ctx.script_vars["x"]) == 100.0

    def test_compound_assignment(self, repl):
        """While loop with compound assignment (x += 1)."""
        repl.onecmd("x = 0")
        repl.onecmd("while x < 5")
        repl.onecmd("x += 2")
        repl.onecmd("end")
        assert float(repl.ctx.script_vars["x"]) == 6.0

    def test_with_instrument_reads(self, mock_repl):
        """While loop reading from a DMM instrument."""
        # Do 3 iterations of reading from dmm
        mock_repl.onecmd("count = 0")
        mock_repl.onecmd("while count < 3")
        mock_repl.onecmd("reading = dmm meas unit=V")
        mock_repl.onecmd("count++")
        mock_repl.onecmd("end")
        assert float(mock_repl.ctx.script_vars["count"]) == 3.0
        assert "reading" in mock_repl.ctx.script_vars

    def test_break(self, repl):
        """While loop with break statement."""
        repl.onecmd("x = 0")
        repl.onecmd("while x < 100")
        repl.onecmd("x++")
        repl.onecmd("if x == 5")
        repl.onecmd("break")
        repl.onecmd("end")
        repl.onecmd("end")
        assert float(repl.ctx.script_vars["x"]) == 5.0

    def test_continue(self, repl):
        """While loop with continue statement — sum only even numbers."""
        repl.onecmd("x = 0")
        repl.onecmd("total = 0")
        repl.onecmd("while x < 6")
        repl.onecmd("x++")
        # Skip odd numbers using modulo check
        repl.onecmd("remainder = x % 2")
        repl.onecmd("if remainder != 0")
        repl.onecmd("continue")
        repl.onecmd("end")
        repl.onecmd("total += x")
        repl.onecmd("end")
        # Even numbers 2 + 4 + 6 = 12
        assert float(repl.ctx.script_vars["total"]) == 12.0

    def test_max_iteration_safety(self, repl, capsys):
        """While loop hitting max iteration limit should warn and stop."""
        # Set a small max for testing
        original = repl._WHILE_MAX_ITERATIONS
        try:
            repl.__class__._WHILE_MAX_ITERATIONS = 50
            repl.onecmd("x = 0")
            repl.onecmd("while True")
            repl.onecmd("x++")
            repl.onecmd("end")
            assert float(repl.ctx.script_vars["x"]) == 50.0
        finally:
            repl.__class__._WHILE_MAX_ITERATIONS = original

    def test_interrupt_stops_loop(self, repl):
        """While loop checks interrupt_requested each iteration."""
        repl.onecmd("x = 0")
        # We'll set interrupt_requested after a few iterations by using
        # a counter and checking it in the condition
        repl.ctx.interrupt_requested = False
        repl.onecmd("x = 0")

        # Override to set interrupt after 3 iterations
        original_eval = repl._eval_condition

        call_count = [0]

        def counting_eval(cond):
            call_count[0] += 1
            if call_count[0] > 3:
                repl.ctx.interrupt_requested = True
            return original_eval(cond)

        repl._eval_condition = counting_eval
        repl.onecmd("while x < 1000")
        repl.onecmd("x++")
        repl.onecmd("end")
        # Should have stopped after ~3 iterations due to interrupt
        assert float(repl.ctx.script_vars["x"]) <= 4.0

    def test_while_with_decrement(self, repl):
        """While loop with decrement."""
        repl.onecmd("x = 10")
        repl.onecmd("while x > 0")
        repl.onecmd("x--")
        repl.onecmd("end")
        assert float(repl.ctx.script_vars["x"]) == 0.0


# ---------------------------------------------------------------------------
# If/Elif/Else tests
# ---------------------------------------------------------------------------


class TestIfElifElse:
    def test_if_true(self, repl):
        """If condition is true, execute body."""
        repl.onecmd("x = 10")
        repl.onecmd("if x > 5")
        repl.onecmd("result = 1")
        repl.onecmd("end")
        assert repl.ctx.script_vars["result"] == "1"

    def test_if_false(self, repl):
        """If condition is false, skip body."""
        repl.onecmd("x = 3")
        repl.onecmd("result = 0")
        repl.onecmd("if x > 5")
        repl.onecmd("result = 1")
        repl.onecmd("end")
        assert repl.ctx.script_vars["result"] == "0"

    def test_if_else_true_branch(self, repl):
        """If/else where if branch is taken."""
        repl.onecmd("x = 10")
        repl.onecmd("if x > 5")
        repl.onecmd("result = 1")
        repl.onecmd("else")
        repl.onecmd("result = 2")
        repl.onecmd("end")
        assert repl.ctx.script_vars["result"] == "1"

    def test_if_else_false_branch(self, repl):
        """If/else where else branch is taken."""
        repl.onecmd("x = 3")
        repl.onecmd("if x > 5")
        repl.onecmd("result = 1")
        repl.onecmd("else")
        repl.onecmd("result = 2")
        repl.onecmd("end")
        assert repl.ctx.script_vars["result"] == "2"

    def test_if_elif_else_first_branch(self, repl):
        """If/elif/else where first branch matches."""
        repl.onecmd("v = 6.0")
        repl.onecmd("if v > 5.0")
        repl.onecmd('result = "high"')
        repl.onecmd("elif v < 4.9")
        repl.onecmd('result = "low"')
        repl.onecmd("else")
        repl.onecmd('result = "ok"')
        repl.onecmd("end")
        assert repl.ctx.script_vars["result"] == "high"

    def test_if_elif_else_second_branch(self, repl):
        """If/elif/else where elif branch matches."""
        repl.onecmd("v = 4.0")
        repl.onecmd("if v > 5.0")
        repl.onecmd('result = "high"')
        repl.onecmd("elif v < 4.9")
        repl.onecmd('result = "low"')
        repl.onecmd("else")
        repl.onecmd('result = "ok"')
        repl.onecmd("end")
        assert repl.ctx.script_vars["result"] == "low"

    def test_if_elif_else_else_branch(self, repl):
        """If/elif/else where else branch is taken."""
        repl.onecmd("v = 4.95")
        repl.onecmd("if v > 5.0")
        repl.onecmd('result = "high"')
        repl.onecmd("elif v < 4.9")
        repl.onecmd('result = "low"')
        repl.onecmd("else")
        repl.onecmd('result = "ok"')
        repl.onecmd("end")
        assert repl.ctx.script_vars["result"] == "ok"

    def test_multiple_elif(self, repl):
        """If with multiple elif branches."""
        repl.onecmd("x = 3")
        repl.onecmd("if x == 1")
        repl.onecmd("result = 1")
        repl.onecmd("elif x == 2")
        repl.onecmd("result = 2")
        repl.onecmd("elif x == 3")
        repl.onecmd("result = 3")
        repl.onecmd("else")
        repl.onecmd("result = 0")
        repl.onecmd("end")
        assert repl.ctx.script_vars["result"] == "3"

    def test_if_with_instrument_values(self, mock_repl):
        """If block with values from instrument reads."""
        mock_repl.onecmd("v = psu meas v unit=V")
        # MockPSU returns ~5.0V, so v > 4.0 should be true
        mock_repl.onecmd("if v > 4.0")
        mock_repl.onecmd("result = 1")
        mock_repl.onecmd("else")
        mock_repl.onecmd("result = 0")
        mock_repl.onecmd("end")
        assert mock_repl.ctx.script_vars["result"] == "1"

    def test_nested_if_inside_while(self, repl):
        """Nested if inside a while loop."""
        repl.onecmd("x = 0")
        repl.onecmd("evens = 0")
        repl.onecmd("odds = 0")
        repl.onecmd("while x < 6")
        repl.onecmd("x++")
        repl.onecmd("remainder = x % 2")
        repl.onecmd("if remainder == 0")
        repl.onecmd("evens++")
        repl.onecmd("else")
        repl.onecmd("odds++")
        repl.onecmd("end")
        repl.onecmd("end")
        assert float(repl.ctx.script_vars["evens"]) == 3.0  # 2, 4, 6
        assert float(repl.ctx.script_vars["odds"]) == 3.0  # 1, 3, 5

    def test_if_no_match_no_else(self, repl):
        """If with no matching branch and no else -- should not change anything."""
        repl.onecmd("result = 0")
        repl.onecmd("x = 1")
        repl.onecmd("if x > 10")
        repl.onecmd("result = 1")
        repl.onecmd("elif x > 20")
        repl.onecmd("result = 2")
        repl.onecmd("end")
        assert repl.ctx.script_vars["result"] == "0"


# ---------------------------------------------------------------------------
# Assert tests
# ---------------------------------------------------------------------------


class TestAssert:
    def test_assert_pass(self, repl, capsys):
        """Assert with true condition prints PASS."""
        repl.onecmd("x = 5")
        repl.onecmd("assert x > 3")
        captured = capsys.readouterr()
        assert "PASS" in captured.out

    def test_assert_fail(self, repl, capsys):
        """Assert with false condition prints FAIL."""
        repl.onecmd("x = 2")
        repl.onecmd("assert x > 3")
        captured = capsys.readouterr()
        assert "FAIL" in captured.out

    def test_assert_sets_error_flag_on_fail(self, repl):
        """Assert fail sets command_had_error."""
        repl.onecmd("x = 2")
        repl.ctx.command_had_error = False
        repl.onecmd("assert x > 3")
        assert repl.ctx.command_had_error is True

    def test_assert_no_error_on_pass(self, repl):
        """Assert pass does not set error flag."""
        repl.onecmd("x = 10")
        repl.ctx.command_had_error = False
        repl.onecmd("assert x > 3")
        assert repl.ctx.command_had_error is False

    def test_assert_with_custom_message(self, repl, capsys):
        """Assert with custom message includes message in output."""
        repl.onecmd("v = 4.5")
        repl.onecmd('assert v > 4.9 "Voltage below minimum"')
        captured = capsys.readouterr()
        assert "FAIL" in captured.out
        assert "Voltage below minimum" in captured.out

    def test_assert_pass_with_custom_message(self, repl, capsys):
        """Assert pass with custom message."""
        repl.onecmd("v = 5.05")
        repl.onecmd('assert v > 4.9 "Voltage above minimum"')
        captured = capsys.readouterr()
        assert "PASS" in captured.out
        assert "Voltage above minimum" in captured.out

    def test_assert_does_not_record_test_result(self, repl):
        """Assert (hard stop) does NOT record in test_results — use check for that."""
        repl.ctx.test_results = []
        repl.onecmd("x = 10")
        repl.onecmd('assert x > 5 "x is big enough"')
        assert len(repl.ctx.test_results) == 0

    def test_assert_fail_sets_error_and_aborts(self, repl, capsys):
        """Assert fail in interactive mode prints aborted message."""
        repl.ctx.test_results = []
        repl.onecmd("x = 2")
        repl.onecmd('assert x > 5 "x is big enough"')
        assert len(repl.ctx.test_results) == 0
        assert repl.ctx.command_had_error is True
        out = capsys.readouterr().out
        assert "FAIL" in out
        assert "aborted" in out.lower()

    def test_assert_with_instrument_values(self, mock_repl, capsys):
        """Assert using variable from instrument read."""
        mock_repl.onecmd("v = psu meas v unit=V")
        # MockPSU returns ~5.0V, so v > 4.0 should pass
        mock_repl.onecmd('assert v > 4.0 "PSU voltage above minimum"')
        captured = capsys.readouterr()
        assert "PASS" in captured.out

    def test_assert_equality(self, repl, capsys):
        """Assert with equality check."""
        repl.onecmd("x = 5")
        repl.onecmd("assert x == 5")
        captured = capsys.readouterr()
        assert "PASS" in captured.out

    def test_assert_compound_condition(self, repl, capsys):
        """Assert with compound condition (and)."""
        repl.onecmd("x = 5")
        repl.onecmd("y = 10")
        repl.onecmd("assert x > 3 and y < 20")
        captured = capsys.readouterr()
        assert "PASS" in captured.out

    def test_assert_invalid_expression(self, repl, capsys):
        """Assert with invalid expression shows error."""
        repl.onecmd("assert @@@ invalid")
        captured = capsys.readouterr()
        assert "error" in captured.out.lower() or "FAIL" in captured.out


# ---------------------------------------------------------------------------
# Script execution tests (via _run_script_lines)
# ---------------------------------------------------------------------------


class TestScriptExecution:
    def test_while_in_script(self, repl):
        """While loop executed via script runner."""
        lines = [
            "x = 0",
            "while x < 5",
            "x++",
            "end",
        ]
        repl._run_script_lines(lines)
        assert float(repl.ctx.script_vars["x"]) == 5.0

    def test_if_in_script(self, repl):
        """If/else executed via script runner."""
        lines = [
            "x = 10",
            "if x > 5",
            "result = 1",
            "else",
            "result = 2",
            "end",
        ]
        repl._run_script_lines(lines)
        assert repl.ctx.script_vars["result"] == "1"

    def test_assert_in_script(self, repl, capsys):
        """Assert executed via script runner (hard stop, no test_results)."""
        repl.ctx.test_results = []
        lines = [
            "x = 10",
            'assert x > 5 "x check"',
        ]
        repl._run_script_lines(lines)
        assert len(repl.ctx.test_results) == 0
        assert "PASS" in capsys.readouterr().out

    def test_while_with_if_in_script(self, repl):
        """Combined while and if in a script."""
        lines = [
            "x = 0",
            "total = 0",
            "while x < 10",
            "x++",
            "remainder = x % 2",
            "if remainder == 0",
            "total += x",
            "end",
            "end",
        ]
        repl._run_script_lines(lines)
        # Even numbers 2+4+6+8+10 = 30
        assert float(repl.ctx.script_vars["total"]) == 30.0

    def test_while_break_in_script(self, repl):
        """While with break in a script."""
        lines = [
            "x = 0",
            "while x < 100",
            "x++",
            "if x == 7",
            "break",
            "end",
            "end",
        ]
        repl._run_script_lines(lines)
        assert float(repl.ctx.script_vars["x"]) == 7.0

    def test_if_elif_else_in_script(self, repl):
        """Full if/elif/else in script."""
        lines = [
            "x = 50",
            "if x > 100",
            'grade = "A"',
            "elif x > 40",
            'grade = "B"',
            "else",
            'grade = "C"',
            "end",
        ]
        repl._run_script_lines(lines)
        assert repl.ctx.script_vars["grade"] == "B"

    def test_assert_stops_at_first_failure_in_script(self, repl, capsys):
        """Assert stops script at first failure — later lines never run."""
        lines = [
            "v = 5.0",
            'assert v > 4.9 "Voltage above min"',
            'assert v > 10.0 "This should fail"',
            'assert v < 5.1 "Never reached"',
        ]
        repl._run_script_lines(lines)
        assert repl.ctx.command_had_error is True
        out = capsys.readouterr().out
        assert "Voltage above min" in out
        assert "This should fail" in out
        assert "Never reached" not in out
