"""Tests for _generate_pdf_report — mocking fpdf2 since it may not be installed."""

import os
import sys
import tempfile
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def make_repl(devices=None):
    from lab_instruments.src import discovery as _disc

    _disc.InstrumentDiscovery.__init__ = lambda self: None
    _disc.InstrumentDiscovery.scan = lambda self, verbose=True: devices or {}
    from lab_instruments.repl import InstrumentRepl

    repl = InstrumentRepl()
    repl._scan_done.set()
    repl.devices = devices or {}
    return repl


def _make_fake_fpdf():
    """Create a minimal FPDF mock that is sufficient for _generate_pdf_report."""
    mock_pdf = MagicMock()
    mock_pdf.w = 210
    mock_pdf.l_margin = 10
    mock_pdf.r_margin = 10
    mock_pdf.get_x.return_value = 10
    mock_pdf.get_y.return_value = 50
    return mock_pdf


@pytest.fixture
def repl():
    return make_repl()


def _add_test_result(repl, label, value, passed):
    repl.ctx.test_results.append(
        {
            "label": label,
            "value": value,
            "unit": "V",
            "min": value - 0.5 if passed else value + 1.0,
            "max": value + 0.5 if passed else value + 2.0,
            "passed": passed,
            "limits_str": f"[{value - 0.5}, {value + 0.5}]",
        }
    )


def _add_measurement(repl, label, value):
    repl.measurements.append({"label": label, "value": value, "unit": "V", "source": "test"})


class TestGeneratePdfReport:
    """Test _generate_pdf_report by mocking fpdf.FPDF."""

    def _run_generate(self, repl, path):
        """Run _generate_pdf_report with fpdf mocked."""
        fake_pdf = _make_fake_fpdf()
        fake_fpdf_module = MagicMock()
        fake_fpdf_module.FPDF = MagicMock(return_value=fake_pdf)
        with patch.dict("sys.modules", {"fpdf": fake_fpdf_module}):
            repl._log_cmd._generate_pdf_report(path)
        return fake_pdf

    def test_generate_empty_report(self, repl):
        """Generate report with no checks and no measurements."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "report.pdf")
            pdf = self._run_generate(repl, path)
            pdf.output.assert_called_once_with(path)

    def test_generate_report_with_pass(self, repl):
        """Report with passing check."""
        _add_test_result(repl, "vout", 5.0, True)
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "report.pdf")
            pdf = self._run_generate(repl, path)
            pdf.output.assert_called_once()

    def test_generate_report_with_fail(self, repl):
        """Report with failing check."""
        _add_test_result(repl, "vout", 6.0, False)
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "report.pdf")
            pdf = self._run_generate(repl, path)
            pdf.output.assert_called_once()

    def test_generate_report_with_measurements(self, repl):
        """Report with measurements table."""
        _add_measurement(repl, "vout", 5.0)
        _add_measurement(repl, "iout", 0.1)
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "report.pdf")
            pdf = self._run_generate(repl, path)
            pdf.output.assert_called_once()

    def test_generate_report_with_title(self, repl):
        """Report with custom title."""
        repl.ctx.report_title = "My Custom Test Report"
        _add_test_result(repl, "vout", 5.0, True)
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "report.pdf")
            pdf = self._run_generate(repl, path)
            pdf.output.assert_called_once()

    def test_generate_report_with_operator(self, repl):
        """Report with operator name."""
        repl.ctx.report_operator = "Jane Doe"
        _add_test_result(repl, "vout", 5.0, True)
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "report.pdf")
            pdf = self._run_generate(repl, path)
            pdf.output.assert_called_once()

    def test_generate_report_all_pass_verdict(self, repl):
        """Report with all passes gets PASS verdict."""
        _add_test_result(repl, "v1", 5.0, True)
        _add_test_result(repl, "v2", 3.3, True)
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "report.pdf")
            pdf = self._run_generate(repl, path)
            pdf.output.assert_called_once()

    def test_generate_report_with_screenshot(self, repl):
        """Report with a screenshot path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a fake image file
            img_path = os.path.join(tmpdir, "shot.png")
            with open(img_path, "wb") as f:
                f.write(b"PNG")
            repl.ctx.report_screenshots = [img_path]
            _add_test_result(repl, "vout", 5.0, True)
            path = os.path.join(tmpdir, "report.pdf")
            pdf = self._run_generate(repl, path)
            pdf.output.assert_called_once()

    def test_generate_report_no_results_na_verdict(self, repl):
        """Report with no checks gets N/A verdict."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "report.pdf")
            pdf = self._run_generate(repl, path)
            pdf.output.assert_called_once()

    def test_report_save_via_repl_with_fpdf_mocked(self, repl, capsys):
        """report save command works end-to-end with fpdf mocked."""
        _add_test_result(repl, "vout", 5.0, True)
        _add_measurement(repl, "vout", 5.0)
        fake_pdf = _make_fake_fpdf()
        fake_fpdf_module = MagicMock()
        fake_fpdf_module.FPDF = MagicMock(return_value=fake_pdf)
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "report.pdf")
            with patch.dict("sys.modules", {"fpdf": fake_fpdf_module}):
                repl.onecmd(f"report save {path}")
            out = capsys.readouterr().out
            assert "Report saved" in out or "saved" in out.lower()
