"""Tests for logging commands: log, calc, check, report, data."""

import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def make_repl(devices=None):
    from lab_instruments.src import discovery as _disc

    _disc.InstrumentDiscovery.__init__ = lambda self: None
    _disc.InstrumentDiscovery.scan = lambda self, verbose=True: devices or {}
    from lab_instruments.repl import InstrumentRepl

    repl = InstrumentRepl()
    repl._scan_thread.join(timeout=5.0)
    repl._scan_done.wait(timeout=5.0)
    repl.devices = devices or {}
    return repl


def _store(repl, label, value, unit="V", source="test"):
    """Directly inject a measurement entry."""
    repl.measurements.append({"label": label, "value": value, "unit": unit, "source": source})


@pytest.fixture
def repl():
    return make_repl()


# ---------------------------------------------------------------------------
# data command
# ---------------------------------------------------------------------------


class TestData:
    def test_data_no_args_shows_current(self, repl, capsys):
        repl.onecmd("data")
        out = capsys.readouterr().out
        assert out != ""

    def test_data_help_flag(self, repl, capsys):
        repl.onecmd("data --help")
        out = capsys.readouterr().out
        assert out != ""

    def test_data_dir_no_args(self, repl, capsys):
        repl.onecmd("data dir")
        out = capsys.readouterr().out
        assert out != ""

    def test_data_dir_set_path(self, repl, capsys):
        with tempfile.TemporaryDirectory() as tmpdir:
            repl.onecmd(f"data dir {tmpdir}")
            out = capsys.readouterr().out
            assert "set" in out.lower() or tmpdir in out

    def test_data_dir_reset(self, repl, capsys):
        repl.onecmd("data dir reset")
        out = capsys.readouterr().out
        assert "reset" in out.lower()

    def test_data_dir_no_path_error(self, repl, capsys):
        """data with no usable path."""
        repl.onecmd("data dir")
        out = capsys.readouterr().out
        assert out != ""


# ---------------------------------------------------------------------------
# log command
# ---------------------------------------------------------------------------


class TestLog:
    def test_log_no_args(self, repl, capsys):
        repl.onecmd("log")
        out = capsys.readouterr().out
        assert out != ""

    def test_log_help(self, repl, capsys):
        repl.onecmd("log --help")
        out = capsys.readouterr().out
        assert out != ""

    def test_log_print_empty(self, repl, capsys):
        repl.onecmd("log print")
        out = capsys.readouterr().out
        assert "No measurements" in out

    def test_log_print_with_entries(self, repl, capsys):
        _store(repl, "vout", 5.0, "V")
        repl.onecmd("log print")
        out = capsys.readouterr().out
        assert "vout" in out

    def test_log_clear(self, repl, capsys):
        _store(repl, "vout", 5.0)
        repl.onecmd("log clear")
        assert len(repl.measurements) == 0
        out = capsys.readouterr().out
        assert "Clear" in out or "clear" in out.lower()

    def test_log_save_csv(self, repl, capsys):
        _store(repl, "vout", 5.0, "V", "test")
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "out.csv")
            repl.onecmd(f"log save {path}")
            out = capsys.readouterr().out
            assert os.path.exists(path)
            assert "Saved" in out

    def test_log_save_txt(self, repl, capsys):
        _store(repl, "vout", 5.0, "V", "test")
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "out.txt")
            repl.onecmd(f"log save {path}")
            capsys.readouterr()
            assert os.path.exists(path)

    def test_log_save_no_measurements(self, repl, capsys):
        repl.onecmd("log save /tmp/nodata.csv")
        out = capsys.readouterr().out
        assert "No measurements" in out

    def test_log_save_invalid_format(self, repl, capsys):
        _store(repl, "v", 1.0)
        repl.onecmd("log save /tmp/out.xyz")
        out = capsys.readouterr().out
        assert "format" in out.lower() or "csv" in out.lower()

    def test_log_save_explicit_format(self, repl, capsys):
        _store(repl, "vout", 5.0, "V")
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "out.dat")
            repl.onecmd(f"log save {path} csv")
            assert os.path.exists(path)

    def test_log_unknown_cmd(self, repl, capsys):
        repl.onecmd("log xyz")
        out = capsys.readouterr().out
        assert out != ""


# ---------------------------------------------------------------------------
# calc command
# ---------------------------------------------------------------------------


class TestCalc:
    def test_calc_help(self, repl, capsys):
        repl.onecmd("calc")
        out = capsys.readouterr().out
        assert out != ""

    def test_calc_simple_expression(self, repl, capsys):
        _store(repl, "vout", 5.0, "V")
        repl.onecmd("calc result = 2 + 3")
        out = capsys.readouterr().out
        assert "result" in out

    def test_calc_using_stored_measurement(self, repl, capsys):
        _store(repl, "vout", 5.0, "V")
        repl.onecmd("calc doubled = $vout * 2 unit=V")
        out = capsys.readouterr().out
        assert "doubled" in out

    def test_calc_no_measurements(self, repl, capsys):
        repl.onecmd("calc result = 2 + 3")
        out = capsys.readouterr().out
        assert "No measurements" in out

    def test_calc_no_expression(self, repl, capsys):
        _store(repl, "v", 1.0)
        repl.onecmd("calc label")
        out = capsys.readouterr().out
        assert out != ""

    def test_calc_stores_result(self, repl):
        _store(repl, "vout", 5.0, "V")
        initial_count = len(repl.measurements)
        repl.onecmd("calc result = 2 + 3")
        assert len(repl.measurements) == initial_count + 1

    def test_calc_bad_expression(self, repl, capsys):
        _store(repl, "v", 1.0)
        repl.onecmd("calc result = $undefined_var_xyz * 2")
        out = capsys.readouterr().out
        assert out != ""


# ---------------------------------------------------------------------------
# report command
# ---------------------------------------------------------------------------


class TestReport:
    def _make_check_result(self, repl, label, value, min_val, max_val, passed):
        repl.ctx.test_results.append(
            {
                "label": label,
                "value": value,
                "unit": "V",
                "min": min_val,
                "max": max_val,
                "passed": passed,
                "limits_str": f"[{min_val}, {max_val}]",
            }
        )

    def test_report_no_args(self, repl, capsys):
        repl.onecmd("report")
        out = capsys.readouterr().out
        assert out != ""

    def test_report_print_empty(self, repl, capsys):
        repl.onecmd("report print")
        out = capsys.readouterr().out
        assert "No check" in out

    def test_report_print_with_results(self, repl, capsys):
        self._make_check_result(repl, "vout", 5.0, 4.9, 5.1, True)
        repl.onecmd("report print")
        out = capsys.readouterr().out
        assert "vout" in out
        assert "PASS" in out

    def test_report_print_fail(self, repl, capsys):
        self._make_check_result(repl, "vout", 6.0, 4.9, 5.1, False)
        repl.onecmd("report print")
        out = capsys.readouterr().out
        assert "FAIL" in out

    def test_report_clear(self, repl, capsys):
        self._make_check_result(repl, "vout", 5.0, 4.9, 5.1, True)
        repl.onecmd("report clear")
        assert len(repl.ctx.test_results) == 0
        out = capsys.readouterr().out
        assert "Clear" in out or "clear" in out.lower()

    def test_report_title(self, repl, capsys):
        repl.onecmd("report title My Test Report")
        out = capsys.readouterr().out
        assert "My Test Report" in out

    def test_report_title_no_text(self, repl, capsys):
        repl.onecmd("report title")
        out = capsys.readouterr().out
        assert out != ""

    def test_report_operator(self, repl, capsys):
        repl.onecmd("report operator John Doe")
        out = capsys.readouterr().out
        assert "John Doe" in out

    def test_report_operator_no_name(self, repl, capsys):
        repl.onecmd("report operator")
        out = capsys.readouterr().out
        assert out != ""

    def test_report_save_missing_path(self, repl, capsys):
        repl.onecmd("report save")
        out = capsys.readouterr().out
        assert out != ""

    def test_report_unknown_subcmd(self, repl, capsys):
        repl.onecmd("report xyz")
        out = capsys.readouterr().out
        assert "Unknown" in out or "xyz" in out

    def test_report_save_no_fpdf(self, repl, capsys):
        """report save should print error if fpdf2 missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "report.pdf")
            repl.onecmd(f"report save {path}")
            capsys.readouterr()
            # Either succeeds (fpdf2 installed) or prints error — just no crash
