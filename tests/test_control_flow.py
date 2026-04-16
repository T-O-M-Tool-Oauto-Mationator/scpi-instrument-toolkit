"""Integration tests for if/elif/else, while, assert, and augmented assignment
in the SCPI script engine (via shell.onecmd and _run_script_lines)."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture
def repl(make_repl):
    return make_repl({})


@pytest.fixture
def mock_repl(make_repl):
    from mock_instruments import get_mock_devices

    return make_repl(get_mock_devices(verbose=False))


# ---------------------------------------------------------------------------
# if/elif/else — interactive (onecmd)
# ---------------------------------------------------------------------------


class TestIfInteractive:
    def test_if_true_branch_taken(self, repl):
        repl.onecmd("x = 10")
        repl.onecmd("if x > 5")
        repl.onecmd("result = 1")
        repl.onecmd("end")
        assert repl.ctx.script_vars["result"] == "1"

    def test_if_false_branch_skipped(self, repl):
        repl.onecmd("x = 3")
        repl.onecmd("result = 0")
        repl.onecmd("if x > 5")
        repl.onecmd("result = 1")
        repl.onecmd("end")
        assert repl.ctx.script_vars["result"] == "0"

    def test_elif_branch(self, repl):
        repl.onecmd("v = 4.5")
        repl.onecmd("if v > 5.1")
        repl.onecmd('reading = "high"')
        repl.onecmd("elif v < 4.9")
        repl.onecmd('reading = "low"')
        repl.onecmd("else")
        repl.onecmd('reading = "ok"')
        repl.onecmd("end")
        assert repl.ctx.script_vars["reading"] == "low"

    def test_else_fallback(self, repl):
        repl.onecmd("v = 5.0")
        repl.onecmd("if v > 5.1")
        repl.onecmd('reading = "high"')
        repl.onecmd("elif v < 4.9")
        repl.onecmd('reading = "low"')
        repl.onecmd("else")
        repl.onecmd('reading = "ok"')
        repl.onecmd("end")
        assert repl.ctx.script_vars["reading"] == "ok"

    def test_no_match_no_else(self, repl):
        repl.onecmd("result = 0")
        repl.onecmd("x = 1")
        repl.onecmd("if x > 10")
        repl.onecmd("result = 1")
        repl.onecmd("end")
        assert repl.ctx.script_vars["result"] == "0"


# ---------------------------------------------------------------------------
# while — interactive (onecmd)
# ---------------------------------------------------------------------------


class TestWhileInteractive:
    def test_basic_count(self, repl):
        repl.onecmd("count = 0")
        repl.onecmd("while count < 5")
        repl.onecmd("count++")
        repl.onecmd("end")
        assert float(repl.ctx.script_vars["count"]) == 5.0

    def test_false_initial_condition(self, repl):
        repl.onecmd("x = 100")
        repl.onecmd("while x < 0")
        repl.onecmd("x = 999")
        repl.onecmd("end")
        assert float(repl.ctx.script_vars["x"]) == 100.0

    def test_augmented_assign_in_loop(self, repl):
        repl.onecmd("total = 0")
        repl.onecmd("i = 1")
        repl.onecmd("while i <= 5")
        repl.onecmd("total += i")
        repl.onecmd("i++")
        repl.onecmd("end")
        assert float(repl.ctx.script_vars["total"]) == 15.0


# ---------------------------------------------------------------------------
# assert — interactive (onecmd)
# ---------------------------------------------------------------------------


class TestAssertInteractive:
    def test_assert_pass(self, repl, capsys):
        repl.onecmd("x = 10")
        repl.onecmd("assert x > 5")
        assert repl.ctx.command_had_error is False
        assert "PASS" in capsys.readouterr().out

    def test_assert_fail_stops(self, repl, capsys):
        """Assert fail in interactive mode prints FAIL + aborted message."""
        repl.onecmd("x = 2")
        repl.ctx.command_had_error = False
        repl.onecmd("assert x > 5")
        assert repl.ctx.command_had_error is True
        out = capsys.readouterr().out
        assert "FAIL" in out
        assert "aborted" in out.lower()

    def test_assert_with_message(self, repl, capsys):
        repl.onecmd("v = 4.0")
        repl.onecmd('assert v > 4.9 "Voltage too low"')
        out = capsys.readouterr().out
        assert "FAIL" in out
        assert "Voltage too low" in out


# ---------------------------------------------------------------------------
# check (condition form) — interactive (onecmd)
# ---------------------------------------------------------------------------


class TestCheckConditionInteractive:
    def test_check_pass(self, repl, capsys):
        repl.onecmd("x = 10")
        repl.onecmd("check x > 5")
        assert repl.ctx.command_had_error is False
        assert "PASS" in capsys.readouterr().out

    def test_check_fail_continues(self, repl, capsys):
        """Check fail records result but does NOT stop execution."""
        repl.onecmd("x = 2")
        repl.ctx.command_had_error = False
        repl.onecmd("check x > 5")
        assert repl.ctx.command_had_error is True
        out = capsys.readouterr().out
        assert "FAIL" in out
        # Should NOT say "aborted"
        assert "aborted" not in out.lower()

    def test_check_records_in_test_results(self, repl):
        repl.ctx.test_results = []
        repl.onecmd("v = 5.0")
        repl.onecmd('check v > 4.9 "above min"')
        repl.onecmd('check v < 5.1 "below max"')
        assert len(repl.ctx.test_results) == 2
        assert repl.ctx.test_results[0]["passed"] is True
        assert repl.ctx.test_results[1]["passed"] is True

    def test_check_with_message(self, repl, capsys):
        repl.onecmd("v = 4.0")
        repl.onecmd('check v > 4.9 "Voltage too low"')
        out = capsys.readouterr().out
        assert "FAIL" in out
        assert "Voltage too low" in out


# ---------------------------------------------------------------------------
# if/while/assert via script runner (_run_script_lines)
# ---------------------------------------------------------------------------


class TestScriptControlFlow:
    def test_if_in_script(self, repl):
        repl._run_script_lines(
            [
                "x = 10",
                "if x > 5",
                "result = 1",
                "else",
                "result = 2",
                "end",
            ]
        )
        assert repl.ctx.script_vars["result"] == "1"

    def test_while_in_script(self, repl):
        repl._run_script_lines(
            [
                "x = 0",
                "while x < 5",
                "x++",
                "end",
            ]
        )
        assert float(repl.ctx.script_vars["x"]) == 5.0

    def test_assert_pass_in_script(self, repl, capsys):
        repl._run_script_lines(
            [
                "x = 10",
                'assert x > 5 "x check"',
            ]
        )
        assert "PASS" in capsys.readouterr().out

    def test_assert_fail_stops_script(self, repl):
        """Assert fail ALWAYS stops the script (no set -e needed)."""
        repl._run_script_lines(
            [
                "x = 2",
                'assert x > 5 "x check"',
                "result = done",
            ]
        )
        # Assert fail stops the script — result should NOT be set
        assert "result" not in repl.ctx.script_vars
        assert repl.ctx.command_had_error is True

    def test_nested_if_inside_while(self, repl):
        repl._run_script_lines(
            [
                "x = 0",
                "evens = 0",
                "odds = 0",
                "while x < 6",
                "x++",
                "remainder = x % 2",
                "if remainder == 0",
                "evens++",
                "else",
                "odds++",
                "end",
                "end",
            ]
        )
        assert float(repl.ctx.script_vars["evens"]) == 3.0
        assert float(repl.ctx.script_vars["odds"]) == 3.0

    def test_while_with_augmented_assign_in_script(self, repl):
        repl._run_script_lines(
            [
                "count = 0",
                "total = 0",
                "while count < 5",
                "count += 1",
                "total += count",
                "end",
            ]
        )
        assert float(repl.ctx.script_vars["count"]) == 5.0
        assert float(repl.ctx.script_vars["total"]) == 15.0

    def test_if_elif_else_in_script(self, repl):
        repl._run_script_lines(
            [
                "x = 50",
                "if x > 100",
                'grade = "A"',
                "elif x > 40",
                'grade = "B"',
                "else",
                'grade = "C"',
                "end",
            ]
        )
        assert repl.ctx.script_vars["grade"] == "B"

    def test_while_break_in_script(self, repl):
        repl._run_script_lines(
            [
                "x = 0",
                "while x < 100",
                "x++",
                "if x == 7",
                "break",
                "end",
                "end",
            ]
        )
        assert float(repl.ctx.script_vars["x"]) == 7.0

    def test_assert_stops_at_first_failure(self, repl, capsys):
        """Assert stops the script at the first failure — later lines don't run."""
        repl._run_script_lines(
            [
                "v = 5.0",
                'assert v > 4.9 "above min"',
                'assert v > 10.0 "this fails"',
                'assert v < 5.1 "never reached"',
                "result = done",
            ]
        )
        assert "result" not in repl.ctx.script_vars
        out = capsys.readouterr().out
        assert "above min" in out
        assert "this fails" in out
        # "never reached" should not appear
        assert "never reached" not in out

    def test_multiple_checks_in_script(self, repl):
        """Check records all results and continues past failures."""
        repl.ctx.test_results = []
        repl._run_script_lines(
            [
                "v = 5.0",
                'check v > 4.9 "above min"',
                'check v < 5.1 "below max"',
                'check v > 10.0 "this fails"',
            ]
        )
        assert len(repl.ctx.test_results) == 3
        assert repl.ctx.test_results[0]["passed"] is True
        assert repl.ctx.test_results[1]["passed"] is True
        assert repl.ctx.test_results[2]["passed"] is False

    def test_check_continues_after_failure(self, repl):
        """Check does NOT stop execution — subsequent checks still run."""
        repl.ctx.test_results = []
        repl._run_script_lines(
            [
                "v = 1.0",
                'check v > 10 "this fails"',
                'check v > 0 "this passes"',
            ]
        )
        # Both checks ran — script was NOT aborted
        assert len(repl.ctx.test_results) == 2
        assert repl.ctx.test_results[0]["passed"] is False
        assert repl.ctx.test_results[1]["passed"] is True


# ---------------------------------------------------------------------------
# calc with bare variable names (regression: fix for do_calc)
# ---------------------------------------------------------------------------


class TestCalcWithBareNames:
    def test_calc_uses_script_vars(self, repl):
        repl.onecmd("psu_v = 5.0")
        repl.onecmd("psu_i = 0.5")
        repl.onecmd("calc power psu_v * psu_i unit=W")
        # Result should be stored in both script_vars and measurements
        assert "power" in repl.ctx.script_vars
        assert float(repl.ctx.script_vars["power"]) == 2.5

    def test_calc_stores_in_measurements(self, repl):
        repl.onecmd("v = 3.0")
        repl.onecmd("i = 2.0")
        repl.onecmd("calc p v * i unit=W")
        entry = repl.ctx.measurements.get_by_label("p")
        assert entry is not None
        assert float(entry["value"]) == 6.0
        assert entry["unit"] == "W"

    def test_calc_result_usable_in_next_calc(self, repl):
        repl.onecmd("v_in = 10.0")
        repl.onecmd("v_out = 5.0")
        repl.onecmd("calc gain v_out / v_in")
        repl.onecmd("calc gain_db 20 * log10(gain) unit=dB")
        assert "gain_db" in repl.ctx.script_vars
        import math

        expected = 20 * math.log10(0.5)
        assert abs(float(repl.ctx.script_vars["gain_db"]) - expected) < 1e-9


# ---------------------------------------------------------------------------
# unit= in plain assignment
# ---------------------------------------------------------------------------


class TestUnitInAssignment:
    def test_assignment_with_unit_records_measurement(self, repl):
        repl.onecmd("error = 5.0 - 4.95 unit=V")
        entry = repl.ctx.measurements.get_by_label("error")
        assert entry is not None
        assert abs(float(entry["value"]) - 0.05) < 1e-9
        assert entry["unit"] == "V"

    def test_assignment_with_unit_still_stores_in_script_vars(self, repl):
        repl.onecmd("result = 3.14 unit=rad")
        assert "result" in repl.ctx.script_vars
        assert abs(float(repl.ctx.script_vars["result"]) - 3.14) < 1e-9

    def test_assignment_with_unit_expr_uses_vars(self, repl):
        repl.onecmd("a = 10.0")
        repl.onecmd("b = 3.0")
        repl.onecmd("diff = a - b unit=V")
        entry = repl.ctx.measurements.get_by_label("diff")
        assert entry is not None
        assert float(entry["value"]) == 7.0


# ---------------------------------------------------------------------------
# Mock instrument integration: if/while with real reads
# ---------------------------------------------------------------------------


class TestMockInstrumentControlFlow:
    def test_if_with_psu_read(self, mock_repl):
        """If block using PSU measurement (mock returns ~5.0V)."""
        mock_repl.onecmd("v = psu meas v unit=V")
        mock_repl.onecmd("if v > 4.0")
        mock_repl.onecmd('verdict = "in_range"')
        mock_repl.onecmd("else")
        mock_repl.onecmd('verdict = "out_of_range"')
        mock_repl.onecmd("end")
        assert mock_repl.ctx.script_vars["verdict"] == "in_range"

    def test_while_with_psu_samples(self, mock_repl):
        """While loop reading PSU measurements into a total."""
        mock_repl.onecmd("count = 0")
        mock_repl.onecmd("total = 0.0")
        mock_repl.onecmd("while count < 3")
        mock_repl.onecmd("count += 1")
        mock_repl.onecmd("sample = psu meas v unit=V")
        mock_repl.onecmd("total = total + sample")
        mock_repl.onecmd("end")
        assert float(mock_repl.ctx.script_vars["count"]) == 3.0
        total = float(mock_repl.ctx.script_vars["total"])
        assert total > 0.0

    def test_assert_with_psu_read_passes(self, mock_repl, capsys):
        """Assert using mock PSU reading (returns ~5.0V, should pass > 4.0)."""
        mock_repl.onecmd("v = psu meas v unit=V")
        mock_repl.onecmd('assert v > 4.0 "PSU voltage in range"')
        out = capsys.readouterr().out
        assert "PASS" in out
