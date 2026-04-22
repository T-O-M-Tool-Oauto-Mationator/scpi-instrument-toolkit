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
        assert repl.ctx.script_vars["result"] == 1

    def test_if_false_branch_skipped(self, repl):
        repl.onecmd("x = 3")
        repl.onecmd("result = 0")
        repl.onecmd("if x > 5")
        repl.onecmd("result = 1")
        repl.onecmd("end")
        assert repl.ctx.script_vars["result"] == 0

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
        assert repl.ctx.script_vars["result"] == 0


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
        assert repl.ctx.script_vars["result"] == 1

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


# ---------------------------------------------------------------------------
# Regression tests for issue #87: assignment grammar for multi-channel PSU
# (v = psu meas <ch> v unit=V) and EV2300 reads (code = ev2300 read_word ...).
# ---------------------------------------------------------------------------


class _StateTrackingMultiChanPSU:
    """Multi-channel PSU mock that tracks which channel was measured.

    Values are deterministic per channel but reflect the last setpoint so
    a sweep of `psu set 2 V; psu meas 2 v` reads back what was written.
    Per-channel read and write counts are incremented on every call so this
    is not a constant-returning stub (state tracking per project rules).
    """

    CHANNEL_FROM_NUMBER = {1: "P6V", 2: "P25V", 3: "N25V"}

    def __init__(self):
        self.v_reads = {1: 0, 2: 0, 3: 0}
        self.i_reads = {1: 0, 2: 0, 3: 0}
        self.setpoints_v = {1: 6.0, 2: 25.0, 3: -25.0}
        self.setpoints_i = {1: 0.10, 2: 0.25, 3: -0.25}
        self.output_enabled = False
        self.selected_channel = None
        self.last_channel = None

    def _ch_num(self, channel):
        inv = {v: k for k, v in self.CHANNEL_FROM_NUMBER.items()}
        return inv.get(channel, channel if isinstance(channel, int) else 1)

    def measure_voltage(self, channel):
        n = self._ch_num(channel)
        self.v_reads[n] += 1
        self.last_channel = n
        return self.setpoints_v[n]

    def measure_current(self, channel):
        n = self._ch_num(channel)
        self.i_reads[n] += 1
        self.last_channel = n
        return self.setpoints_i[n]

    def set_output_channel(self, channel, voltage, current=None):
        n = self._ch_num(channel)
        self.setpoints_v[n] = float(voltage)
        if current is not None:
            self.setpoints_i[n] = float(current)
        self.last_channel = n

    def select_channel(self, channel):
        self.selected_channel = self._ch_num(channel)

    def enable_output(self, state):
        self.output_enabled = bool(state)

    def safe_all(self):
        self.output_enabled = False


class _StateTrackingEV2300:
    """EV2300 mock that tracks each read call; returns distinct values."""

    def __init__(self):
        self.word_reads = []
        self.byte_reads = []
        self.block_reads = []

    def read_word(self, addr, reg):
        self.word_reads.append((addr, reg))
        return {"ok": True, "value": 0x1234}

    def read_byte(self, addr, reg):
        self.byte_reads.append((addr, reg))
        return {"ok": True, "value": 0x5A}

    def read_block(self, addr, reg):
        self.block_reads.append((addr, reg))
        return {"ok": True, "block": [0xDE, 0xAD, 0xBE, 0xEF]}

    def safe_all(self):
        pass


@pytest.fixture
def repl_multi_psu(make_repl):
    return make_repl({"psu1": _StateTrackingMultiChanPSU()})


@pytest.fixture
def repl_ev2300(make_repl):
    return make_repl({"ev2300": _StateTrackingEV2300()})


class TestAssignPsuMeasWithChannel:
    """Issue #87: `v = psu meas <ch> v unit=V` must forward the channel."""

    def test_assign_psu_meas_with_channel_multi(self, repl_multi_psu):
        repl_multi_psu.onecmd("v = psu meas 2 v unit=V")
        assert repl_multi_psu.ctx.command_had_error is False
        assert float(repl_multi_psu.ctx.script_vars["v"]) == 25.0
        entry = repl_multi_psu.ctx.measurements.get_by_label("v")
        assert entry is not None
        assert entry["unit"] == "V"
        assert float(entry["value"]) == 25.0
        dev = repl_multi_psu.ctx.registry.get_device("psu1")
        assert dev.v_reads[2] == 1
        assert dev.last_channel == 2

    def test_assign_psu_meas_with_channel_current(self, repl_multi_psu):
        repl_multi_psu.onecmd("i = psu meas 3 i unit=A")
        assert repl_multi_psu.ctx.command_had_error is False
        assert float(repl_multi_psu.ctx.script_vars["i"]) == -0.25
        entry = repl_multi_psu.ctx.measurements.get_by_label("i")
        assert entry is not None
        assert entry["unit"] == "A"
        dev = repl_multi_psu.ctx.registry.get_device("psu1")
        assert dev.i_reads[3] == 1
        assert dev.last_channel == 3


class TestAssignEV2300Read:
    """Issue #87: `code = ev2300 read_word ...` must capture the value."""

    def test_assign_ev2300_read_word(self, repl_ev2300):
        repl_ev2300.onecmd("code = ev2300 read_word 0x08 0x0C")
        assert repl_ev2300.ctx.command_had_error is False
        assert repl_ev2300.ctx.script_vars["code"] == 0x1234
        entry = repl_ev2300.ctx.measurements.get_by_label("code")
        assert entry is not None
        assert entry["value"] == 0x1234
        dev = repl_ev2300.ctx.registry.get_device("ev2300")
        assert dev.word_reads == [(0x08, 0x0C)]

    def test_assign_ev2300_read_byte(self, repl_ev2300):
        repl_ev2300.onecmd("b = ev2300 read_byte 0x08 0x00")
        assert repl_ev2300.ctx.command_had_error is False
        assert repl_ev2300.ctx.script_vars["b"] == 0x5A
        dev = repl_ev2300.ctx.registry.get_device("ev2300")
        assert dev.byte_reads == [(0x08, 0x00)]

    def test_assign_ev2300_read_block(self, repl_ev2300):
        repl_ev2300.onecmd("blk = ev2300 read_block 0x08 0x20")
        assert repl_ev2300.ctx.command_had_error is False
        assert repl_ev2300.ctx.script_vars["blk"] == "DE AD BE EF"
        dev = repl_ev2300.ctx.registry.get_device("ev2300")
        assert dev.block_reads == [(0x08, 0x20)]


# ---------------------------------------------------------------------------
# End-to-end regression for issue #87: replay the student's sweep script
# (linspace + for + psu set + ev2300 read_word + psu meas <ch> + log save).
# If any of the four underlying bugs regress, this test fails rather than
# returning silently with "No measurements recorded."
# ---------------------------------------------------------------------------


class TestIssue87SweepEndToEnd:
    """Regression test for https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit/issues/87.

    Runs the user's reported script through the full script engine (linspace
    expansion, for-loop, command dispatch) and asserts that measurements are
    recorded for every iteration and that `log save` produces a CSV with all
    rows. Silently passing (empty log, no error) was the original symptom.
    """

    def test_student_sweep_records_all_measurements(self, make_repl, tmp_path, monkeypatch):
        from lab_instruments.repl.commands import variables as variables_mod

        psu = _StateTrackingMultiChanPSU()
        ev = _StateTrackingEV2300()
        repl = make_repl({"psu1": psu, "ev2300": ev})

        monkeypatch.setattr(variables_mod.time, "sleep", lambda _secs: None)
        # In script mode `log save <relative>` resolves under the scripts
        # dir (see logging_cmd.py: `base = ctx.get_scripts_dir() if ctx.in_script`).
        monkeypatch.setenv("SCPI_SCRIPTS_DIR", str(tmp_path))
        monkeypatch.setenv("SCPI_DATA_DIR", str(tmp_path))

        # The mock's safe_all() (fired by make_repl's scan) leaves output=False.
        # The student's real session had the channel enabled before running the
        # sweep, so prime it here — otherwise the `psu chan 2 off` assertion
        # below would pass tautologically.
        psu.output_enabled = True

        csv_name = "ADC_digital_code.csv"
        script_lines = [
            "val = linspace 18 21.5 3",
            "for v val",
            '    print "Setting {v}V..."',
            "    psu set 2 {v}",
            "    sleep 0.3",
            "    code = ev2300 read_word 0x08 0x0C",
            "    readback = psu meas 2 v unit=V",
            "end",
            "psu chan 2 off",
            'print "=== Sweep complete ==="',
            "log print",
            f"log save {csv_name}",
        ]

        repl._run_script_lines(script_lines)

        # The sweep must not silently fail: no command-level errors.
        assert repl.ctx.command_had_error is False

        # Three iterations -> three code reads + three readback measurements.
        entries = repl.ctx.measurements.entries
        code_entries = [e for e in entries if e["label"] == "code"]
        readback_entries = [e for e in entries if e["label"] == "readback"]
        assert len(code_entries) == 3, f"expected 3 ev2300 reads, got {len(code_entries)}: {entries}"
        assert len(readback_entries) == 3, f"expected 3 psu readbacks, got {len(readback_entries)}: {entries}"

        # PSU channel 2 must have been written and read back three times each,
        # and the final readback must match the final setpoint (21.5 V).
        assert psu.v_reads[2] == 3
        assert psu.setpoints_v[2] == pytest.approx(21.5)
        assert readback_entries[-1]["value"] == pytest.approx(21.5)
        assert readback_entries[-1]["unit"] == "V"

        # EV2300 read_word must have been called with the documented args.
        assert ev.word_reads == [(0x08, 0x0C), (0x08, 0x0C), (0x08, 0x0C)]
        assert all(e["value"] == 0x1234 for e in code_entries)

        # `psu chan 2 off` must have disabled the output.
        assert psu.output_enabled is False

        # `log save` must have written a CSV with header + 6 data rows (order
        # preserved: code, readback, code, readback, code, readback).
        csv_path = tmp_path / csv_name
        assert csv_path.exists(), f"log save did not write {csv_path}"
        lines = csv_path.read_text(encoding="utf-8").splitlines()
        assert lines[0] == "label,value,unit,source"
        data_rows = lines[1:]
        assert len(data_rows) == 6
        labels_in_order = [row.split(",")[0] for row in data_rows]
        assert labels_in_order == [
            "code",
            "readback",
            "code",
            "readback",
            "code",
            "readback",
        ]

    def test_student_sweep_without_fix_would_fail(self, make_repl, monkeypatch):
        """Tight assertion on the specific symptom from the bug report.

        Before the fix, `psu meas 2 v unit=V` raised a TypeError from
        `HP_E3631A.measure_voltage()` and `ev2300 read_word ...` fell
        through to a literal string assignment. This test fails loudly if
        either regression returns, independent of the broader log-save path.
        """
        from lab_instruments.repl.commands import variables as variables_mod

        psu = _StateTrackingMultiChanPSU()
        ev = _StateTrackingEV2300()
        repl = make_repl({"psu1": psu, "ev2300": ev})
        monkeypatch.setattr(variables_mod.time, "sleep", lambda _secs: None)

        repl._run_script_lines(
            [
                "code = ev2300 read_word 0x08 0x0C",
                "readback = psu meas 2 v unit=V",
            ]
        )

        assert repl.ctx.command_had_error is False
        # `code` must be the integer 0x1234, not the literal string
        # "ev2300 read_word 0x08 0x0C" that the pre-fix fallthrough produced.
        assert repl.ctx.script_vars["code"] == 0x1234
        assert not isinstance(repl.ctx.script_vars["code"], str)
        # `readback` must hold the float from measure_voltage(channel), not
        # error out with "missing 1 required positional argument: 'channel'".
        assert repl.ctx.script_vars["readback"] == pytest.approx(25.0)
        assert psu.last_channel == 2
