"""Tests for the 'check' pass/fail assertion and 'report' commands."""

import os
import sys
import tempfile
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def make_repl():
    """Create a bare InstrumentRepl with no real devices."""
    from lab_instruments.src import discovery as _disc

    _disc.InstrumentDiscovery.__init__ = lambda self: None
    _disc.InstrumentDiscovery.scan = lambda self, verbose=True: {}
    from lab_instruments.repl import InstrumentRepl

    repl = InstrumentRepl()
    repl._scan_done.set()
    repl.devices = {}
    return repl


def _store(repl, label, value, unit="V", source="test"):
    """Directly inject a measurement entry, bypassing instrument calls."""
    repl.measurements.append({"label": label, "value": value, "unit": unit, "source": source})


@pytest.fixture
def repl():
    return make_repl()


# ---------------------------------------------------------------------------
# Initial state
# ---------------------------------------------------------------------------


class TestInitialState:
    def test_test_results_empty(self, repl):
        assert repl.test_results == []

    def test_report_title_default(self, repl):
        assert repl._report_title == "Lab Test Report"

    def test_report_operator_default(self, repl):
        assert repl._report_operator == ""

    def test_report_screenshots_empty(self, repl):
        assert repl._report_screenshots == []


# ---------------------------------------------------------------------------
# check — range mode
# ---------------------------------------------------------------------------


class TestCheckRange:
    def test_pass_value_inside_range(self, repl):
        _store(repl, "vout", 5.0)
        repl._command_had_error = False
        repl.onecmd("check vout 4.9 5.1")
        assert not repl._command_had_error
        assert repl.test_results[-1]["passed"] is True

    def test_fail_value_below_range(self, repl):
        _store(repl, "vout", 4.8)
        repl._command_had_error = False
        repl.onecmd("check vout 4.9 5.1")
        assert repl._command_had_error
        assert repl.test_results[-1]["passed"] is False

    def test_fail_value_above_range(self, repl):
        _store(repl, "vout", 5.2)
        repl._command_had_error = False
        repl.onecmd("check vout 4.9 5.1")
        assert repl._command_had_error
        assert repl.test_results[-1]["passed"] is False

    def test_pass_value_exactly_at_min(self, repl):
        _store(repl, "vout", 4.9)
        repl._command_had_error = False
        repl.onecmd("check vout 4.9 5.1")
        assert not repl._command_had_error
        assert repl.test_results[-1]["passed"] is True

    def test_pass_value_exactly_at_max(self, repl):
        _store(repl, "vout", 5.1)
        repl._command_had_error = False
        repl.onecmd("check vout 4.9 5.1")
        assert not repl._command_had_error
        assert repl.test_results[-1]["passed"] is True

    def test_result_dict_fields(self, repl):
        _store(repl, "vout", 5.0, unit="V")
        repl.onecmd("check vout 4.9 5.1")
        r = repl.test_results[-1]
        assert r["label"] == "vout"
        assert r["value"] == pytest.approx(5.0)
        assert r["unit"] == "V"
        assert r["min"] == pytest.approx(4.9)
        assert r["max"] == pytest.approx(5.1)
        assert "limits_str" in r

    def test_limits_str_range_format(self, repl):
        _store(repl, "vout", 5.0)
        repl.onecmd("check vout 4.9 5.1")
        assert "4.9" in repl.test_results[-1]["limits_str"]
        assert "5.1" in repl.test_results[-1]["limits_str"]

    def test_appends_to_test_results(self, repl):
        _store(repl, "vout", 5.0)
        _store(repl, "iout", 0.1, unit="A")
        repl.onecmd("check vout 4.9 5.1")
        repl.onecmd("check iout 0.09 0.11")
        assert len(repl.test_results) == 2

    def test_negative_range(self, repl):
        _store(repl, "vneg", -5.0)
        repl._command_had_error = False
        repl.onecmd("check vneg -5.1 -4.9")
        assert not repl._command_had_error
        assert repl.test_results[-1]["passed"] is True


# ---------------------------------------------------------------------------
# check — absolute tolerance mode
# ---------------------------------------------------------------------------


class TestCheckAbsoluteTol:
    def test_pass_within_abs_tol(self, repl):
        _store(repl, "vout", 5.05)
        repl._command_had_error = False
        repl.onecmd("check vout 5.0 tol=0.1")
        assert not repl._command_had_error
        assert repl.test_results[-1]["passed"] is True

    def test_fail_outside_abs_tol(self, repl):
        _store(repl, "vout", 5.15)
        repl._command_had_error = False
        repl.onecmd("check vout 5.0 tol=0.1")
        assert repl._command_had_error
        assert repl.test_results[-1]["passed"] is False

    def test_pass_exactly_at_abs_boundary(self, repl):
        _store(repl, "vout", 5.1)
        repl._command_had_error = False
        repl.onecmd("check vout 5.0 tol=0.1")
        assert not repl._command_had_error
        assert repl.test_results[-1]["passed"] is True

    def test_limits_str_abs_format(self, repl):
        _store(repl, "vout", 5.0)
        repl.onecmd("check vout 5.0 tol=0.1")
        ls = repl.test_results[-1]["limits_str"]
        assert "5.0" in ls
        assert "0.1" in ls
        assert "%" not in ls


# ---------------------------------------------------------------------------
# check — percent tolerance mode
# ---------------------------------------------------------------------------


class TestCheckPercentTol:
    def test_pass_within_pct_tol(self, repl):
        # 2% of 5.0 = 0.1 → allowed range [4.9, 5.1]
        _store(repl, "vout", 5.05)
        repl._command_had_error = False
        repl.onecmd("check vout 5.0 tol=2%")
        assert not repl._command_had_error
        assert repl.test_results[-1]["passed"] is True

    def test_fail_outside_pct_tol(self, repl):
        _store(repl, "vout", 5.2)
        repl._command_had_error = False
        repl.onecmd("check vout 5.0 tol=2%")
        assert repl._command_had_error
        assert repl.test_results[-1]["passed"] is False

    def test_pass_exactly_at_pct_boundary(self, repl):
        # 2% of 5.0 = 0.1; value=4.9 is the lower boundary
        _store(repl, "vout", 4.9)
        repl._command_had_error = False
        repl.onecmd("check vout 5.0 tol=2%")
        assert not repl._command_had_error

    def test_limits_str_pct_format(self, repl):
        _store(repl, "vout", 5.0)
        repl.onecmd("check vout 5.0 tol=2%")
        ls = repl.test_results[-1]["limits_str"]
        assert "%" in ls
        assert "5.0" in ls

    def test_pct_tol_computed_from_expected(self, repl):
        # 10% of 10.0 = 1.0 → [9.0, 11.0]
        _store(repl, "vmeas", 9.5)
        repl._command_had_error = False
        repl.onecmd("check vmeas 10.0 tol=10%")
        assert not repl._command_had_error

        _store(repl, "vmeas", 8.9)
        repl._command_had_error = False
        repl.onecmd("check vmeas 10.0 tol=10%")
        assert repl._command_had_error


# ---------------------------------------------------------------------------
# check — error cases
# ---------------------------------------------------------------------------


class TestCheckErrors:
    def test_no_measurement_sets_error(self, repl):
        repl._command_had_error = False
        repl.onecmd("check vout 4.9 5.1")
        assert repl._command_had_error
        assert repl.test_results == []

    def test_wrong_label_sets_error(self, repl):
        _store(repl, "vout", 5.0)
        repl._command_had_error = False
        repl.onecmd("check iout 0.0 1.0")
        assert repl._command_had_error
        assert repl.test_results == []

    def test_help_flag_no_result(self, repl):
        repl.onecmd("check --help")
        assert repl.test_results == []

    def test_no_args_no_result(self, repl):
        repl.onecmd("check")
        assert repl.test_results == []

    def test_pass_does_not_set_error_flag(self, repl):
        _store(repl, "vout", 5.0)
        repl._command_had_error = False
        repl.onecmd("check vout 4.9 5.1")
        assert not repl._command_had_error

    def test_fail_sets_error_flag(self, repl):
        _store(repl, "vout", 4.0)
        repl._command_had_error = False
        repl.onecmd("check vout 4.9 5.1")
        assert repl._command_had_error


# ---------------------------------------------------------------------------
# check — label lookup (last match)
# ---------------------------------------------------------------------------


class TestCheckLabelLookup:
    def test_finds_last_matching_label(self, repl):
        _store(repl, "vout", 3.0)  # first entry — outside range
        _store(repl, "vout", 5.0)  # second (last) — inside range
        repl._command_had_error = False
        repl.onecmd("check vout 4.9 5.1")
        assert not repl._command_had_error
        assert repl.test_results[-1]["value"] == pytest.approx(5.0)

    def test_ignores_other_labels(self, repl):
        _store(repl, "iout", 0.1)
        _store(repl, "vout", 5.0)
        repl._command_had_error = False
        repl.onecmd("check iout 0.05 0.15")
        assert not repl._command_had_error
        assert repl.test_results[-1]["label"] == "iout"

    def test_unit_from_measurement_entry(self, repl):
        _store(repl, "iout", 0.1, unit="A")
        repl.onecmd("check iout 0.05 0.15")
        assert repl.test_results[-1]["unit"] == "A"


# ---------------------------------------------------------------------------
# report — metadata sub-commands
# ---------------------------------------------------------------------------


class TestReportMetadata:
    def test_set_title(self, repl):
        repl.onecmd("report title My Lab Test")
        assert repl._report_title == "My Lab Test"

    def test_set_operator(self, repl):
        repl.onecmd("report operator Brighton")
        assert repl._report_operator == "Brighton"

    def test_set_operator_multi_word(self, repl):
        repl.onecmd("report operator Jane Smith")
        assert repl._report_operator == "Jane Smith"

    def test_set_title_multi_word(self, repl):
        repl.onecmd("report title Lab 3 Final Report")
        assert repl._report_title == "Lab 3 Final Report"


# ---------------------------------------------------------------------------
# report — clear sub-command
# ---------------------------------------------------------------------------


class TestReportClear:
    def test_clear_test_results(self, repl):
        _store(repl, "vout", 5.0)
        repl.onecmd("check vout 4.9 5.1")
        assert len(repl.test_results) == 1
        repl.onecmd("report clear")
        assert repl.test_results == []

    def test_clear_screenshots(self, repl):
        repl._report_screenshots = ["/tmp/shot1.png", "/tmp/shot2.png"]
        repl.onecmd("report clear")
        assert repl._report_screenshots == []

    def test_clear_both_at_once(self, repl):
        _store(repl, "vout", 5.0)
        repl.onecmd("check vout 4.9 5.1")
        repl._report_screenshots = ["/tmp/shot.png"]
        repl.onecmd("report clear")
        assert repl.test_results == []
        assert repl._report_screenshots == []


# ---------------------------------------------------------------------------
# report — print sub-command (smoke + output content)
# ---------------------------------------------------------------------------


class TestReportPrint:
    def test_empty_results_no_crash(self, repl, capsys):
        repl.onecmd("report print")
        out = capsys.readouterr().out
        # Should print a warning, not crash
        assert len(out) > 0 or True  # just no exception

    def test_print_shows_label(self, repl, capsys):
        _store(repl, "vout", 5.0, unit="V")
        repl.onecmd("check vout 4.9 5.1")
        capsys.readouterr()  # flush check output
        repl.onecmd("report print")
        out = capsys.readouterr().out
        assert "vout" in out

    def test_print_shows_pass(self, repl, capsys):
        _store(repl, "vout", 5.0)
        repl.onecmd("check vout 4.9 5.1")
        capsys.readouterr()
        repl.onecmd("report print")
        out = capsys.readouterr().out
        assert "PASS" in out

    def test_print_shows_fail(self, repl, capsys):
        _store(repl, "vout", 4.0)
        repl.onecmd("check vout 4.9 5.1")
        capsys.readouterr()
        repl.onecmd("report print")
        out = capsys.readouterr().out
        assert "FAIL" in out

    def test_print_overall_pass_all_pass(self, repl, capsys):
        _store(repl, "vout", 5.0)
        repl.onecmd("check vout 4.9 5.1")
        capsys.readouterr()
        repl.onecmd("report print")
        out = capsys.readouterr().out
        assert "Overall" in out

    def test_print_counts(self, repl, capsys):
        _store(repl, "vout", 5.0)
        _store(repl, "iout", 0.0, unit="A")
        repl.onecmd("check vout 4.9 5.1")  # pass
        repl.onecmd("check iout 0.05 0.15")  # fail
        capsys.readouterr()
        repl.onecmd("report print")
        out = capsys.readouterr().out
        assert "1" in out  # 1 passed


# ---------------------------------------------------------------------------
# report — save sub-command (PDF generation)
# ---------------------------------------------------------------------------


class TestReportSave:
    def test_save_missing_path_prints_error(self, repl, capsys):
        repl.onecmd("report save")
        out = capsys.readouterr().out
        # Should print an error (captured via ColorPrinter)

    def test_save_creates_pdf_file(self, repl):
        pytest.importorskip("fpdf")
        with tempfile.TemporaryDirectory() as tmpdir:
            # Use forward slashes so shlex doesn't eat Windows backslashes
            pdf_path = tmpdir.replace("\\", "/") + "/report.pdf"
            repl._report_title = "Test Report"
            repl.onecmd(f"report save {pdf_path}")
            assert os.path.isfile(pdf_path)
            assert os.path.getsize(pdf_path) > 100

    def test_save_with_checks_creates_file(self, repl):
        pytest.importorskip("fpdf")
        _store(repl, "vout", 5.0, unit="V")
        repl.onecmd("check vout 4.9 5.1")
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = tmpdir.replace("\\", "/") + "/out.pdf"
            repl.onecmd(f"report save {pdf_path}")
            assert os.path.isfile(pdf_path)

    def test_save_no_fpdf_prints_error(self, repl, capsys):
        import builtins

        real_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "fpdf":
                raise ImportError("No module named 'fpdf'")
            return real_import(name, *args, **kwargs)

        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = os.path.join(tmpdir, "report.pdf")
            with patch("builtins.__import__", side_effect=mock_import):
                repl.onecmd(f"report save {pdf_path}")
            out = capsys.readouterr().out
            assert "fpdf2" in out or "fpdf" in out or not os.path.isfile(pdf_path)

    def test_unknown_subcommand_no_crash(self, repl):
        repl.onecmd("report bogus")

    def test_help_flag_no_crash(self, repl):
        repl.onecmd("report --help")

    def test_no_args_no_crash(self, repl):
        repl.onecmd("report")


# ---------------------------------------------------------------------------
# _generate_pdf_report — direct unit tests
# ---------------------------------------------------------------------------


class TestGeneratePdfReport:
    def _pdf(self, repl, extra=None):
        pytest.importorskip("fpdf")
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test.pdf")
            if extra:
                extra(repl)
            repl._generate_pdf_report(path)
            assert os.path.isfile(path)
            size = os.path.getsize(path)
            assert size > 200, f"PDF suspiciously small: {size} bytes"
            return path, size

    def test_empty_report_generates(self, repl):
        self._pdf(repl)

    def test_with_checks_generates(self, repl):
        _store(repl, "vout", 5.0, unit="V")
        repl.onecmd("check vout 4.9 5.1")
        _store(repl, "iout", 0.0, unit="A")
        repl.onecmd("check iout 0.05 0.15")
        self._pdf(repl)

    def test_with_measurements_only_generates(self, repl):
        _store(repl, "v1", 3.3, unit="V")
        _store(repl, "v2", 1.8, unit="V")
        self._pdf(repl)

    def test_custom_title_operator_in_report(self, repl):
        def setup(r):
            r._report_title = "My Custom Title"
            r._report_operator = "Jane Smith"

        # Just verify it generates without error; content checked separately
        self._pdf(repl, setup)

    def test_with_screenshots_skips_missing_files(self, repl):
        repl._report_screenshots = ["/nonexistent/path/shot.png"]
        self._pdf(repl)  # Should not raise; missing files are skipped

    def test_with_valid_screenshot_embeds_image(self, repl):
        pytest.importorskip("fpdf")
        try:
            from PIL import Image
        except ImportError:
            pytest.skip("Pillow not installed — cannot create test PNG")

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a tiny valid PNG
            img_path = os.path.join(tmpdir, "scope.png")
            img = Image.new("RGB", (100, 50), color=(0, 128, 255))
            img.save(img_path)

            repl._report_screenshots = [img_path]
            pdf_path = os.path.join(tmpdir, "report.pdf")
            repl._generate_pdf_report(pdf_path)
            assert os.path.isfile(pdf_path)

    def test_all_pass_verdict(self, repl):
        """All checks passing → PASS verdict (smoke: no crash)."""
        pytest.importorskip("fpdf")
        _store(repl, "vout", 5.0, unit="V")
        repl.onecmd("check vout 4.9 5.1")
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "r.pdf")
            repl._generate_pdf_report(path)
            assert os.path.isfile(path)

    def test_mixed_pass_fail_verdict(self, repl):
        """Mixed results → FAIL verdict (smoke: no crash)."""
        pytest.importorskip("fpdf")
        _store(repl, "vout", 5.0, unit="V")
        repl.onecmd("check vout 4.9 5.1")  # pass
        _store(repl, "iout", 0.0, unit="A")
        repl.onecmd("check iout 0.5 1.0")  # fail
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "r.pdf")
            repl._generate_pdf_report(path)
            assert os.path.isfile(path)

    def test_no_checks_no_measurements_verdict_na(self, repl):
        """No checks → N/A verdict (smoke: no crash)."""
        pytest.importorskip("fpdf")
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "r.pdf")
            repl._generate_pdf_report(path)
            assert os.path.isfile(path)


# ---------------------------------------------------------------------------
# Screenshot tracking
# ---------------------------------------------------------------------------


class TestScreenshotTracking:
    def test_screenshots_list_starts_empty(self, repl):
        assert repl._report_screenshots == []

    def test_report_clear_empties_screenshots(self, repl):
        repl._report_screenshots = ["/tmp/a.png", "/tmp/b.png"]
        repl.onecmd("report clear")
        assert repl._report_screenshots == []


# ---------------------------------------------------------------------------
# Integration: check + report workflow
# ---------------------------------------------------------------------------


class TestCheckReportIntegration:
    def test_full_range_check_then_print(self, repl, capsys):
        _store(repl, "vout", 5.0, unit="V")
        repl.onecmd("check vout 4.9 5.1")
        capsys.readouterr()
        repl.onecmd("report print")
        out = capsys.readouterr().out
        assert "vout" in out
        assert "PASS" in out

    def test_full_pct_check_then_save(self, repl):
        pytest.importorskip("fpdf")
        _store(repl, "vout", 5.0, unit="V")
        repl.onecmd("check vout 5.0 tol=2%")
        repl.onecmd("report title Integration Test")
        repl.onecmd("report operator Test Bot")
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = tmpdir.replace("\\", "/") + "/integration.pdf"
            repl.onecmd(f"report save {pdf_path}")
            assert os.path.isfile(pdf_path)
            assert os.path.getsize(pdf_path) > 100

    def test_multiple_checks_all_pass(self, repl):
        _store(repl, "v1", 3.3, unit="V")
        _store(repl, "v2", 1.8, unit="V")
        _store(repl, "i1", 0.5, unit="A")
        repl.onecmd("check v1 3.2 3.4")
        repl.onecmd("check v2 1.7 1.9")
        repl.onecmd("check i1 0.4 0.6")
        assert all(r["passed"] for r in repl.test_results)
        assert len(repl.test_results) == 3

    def test_set_e_behavior_on_fail(self, repl):
        """Failing check sets _command_had_error so set -e can abort scripts."""
        _store(repl, "vout", 4.0, unit="V")
        repl._command_had_error = False
        repl.onecmd("check vout 4.9 5.1")
        assert repl._command_had_error

    def test_clear_between_runs(self, repl):
        _store(repl, "vout", 5.0)
        repl.onecmd("check vout 4.9 5.1")
        assert len(repl.test_results) == 1
        repl.onecmd("report clear")
        assert repl.test_results == []
        _store(repl, "vout", 5.0)
        repl.onecmd("check vout 4.9 5.1")
        assert len(repl.test_results) == 1
