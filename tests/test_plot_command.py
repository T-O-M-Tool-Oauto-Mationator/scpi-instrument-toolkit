"""Tests for the plot command."""

import os
import sys
from unittest.mock import MagicMock, patch

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
# No measurements
# ---------------------------------------------------------------------------


class TestPlotNoMeasurements:
    def test_plot_no_measurements_warns(self, repl, capsys):
        repl.onecmd("plot")
        out = capsys.readouterr().out
        assert "nothing to plot" in out.lower() or "no measurements" in out.lower()


# ---------------------------------------------------------------------------
# Pattern filtering
# ---------------------------------------------------------------------------


class TestPlotFiltering:
    @patch("matplotlib.pyplot.close")
    @patch("matplotlib.pyplot.tight_layout")
    @patch("matplotlib.pyplot.subplots")
    def test_plot_all_measurements(self, mock_subplots, mock_tight, mock_close, repl, capsys):
        mock_ax = MagicMock()
        mock_subplots.return_value = (MagicMock(), mock_ax)

        _store(repl, "vout_1", 3.3, "V")
        _store(repl, "vout_2", 5.0, "V")

        repl.onecmd("plot")
        capsys.readouterr()

        mock_close.assert_called_once()
        # Both measurements should be plotted
        call_args = mock_ax.plot.call_args
        assert len(call_args[0][1]) == 2  # two values

    @patch("matplotlib.pyplot.close")
    @patch("matplotlib.pyplot.tight_layout")
    @patch("matplotlib.pyplot.subplots")
    def test_plot_with_pattern(self, mock_subplots, mock_tight, mock_close, repl, capsys):
        mock_ax = MagicMock()
        mock_subplots.return_value = (MagicMock(), mock_ax)

        _store(repl, "linereg_1", 3.3, "V")
        _store(repl, "loadreg_1", 1.2, "V")
        _store(repl, "linereg_2", 3.31, "V")

        repl.onecmd("plot linereg_*")
        capsys.readouterr()

        mock_close.assert_called_once()
        call_args = mock_ax.plot.call_args
        assert len(call_args[0][1]) == 2  # only linereg entries

    @patch("matplotlib.pyplot.close")
    @patch("matplotlib.pyplot.tight_layout")
    @patch("matplotlib.pyplot.subplots")
    def test_plot_multiple_patterns(self, mock_subplots, mock_tight, mock_close, repl, capsys):
        mock_ax = MagicMock()
        mock_subplots.return_value = (MagicMock(), mock_ax)

        _store(repl, "linereg_1", 3.3, "V")
        _store(repl, "loadreg_1", 1.2, "V")
        _store(repl, "ilim_1", 0.5, "V")

        repl.onecmd("plot linereg_* ilim_*")
        capsys.readouterr()

        mock_close.assert_called_once()
        call_args = mock_ax.plot.call_args
        assert len(call_args[0][1]) == 2  # linereg + ilim

    def test_plot_no_match_warns(self, repl, capsys):
        _store(repl, "vout_1", 3.3, "V")
        repl.onecmd("plot nonexistent_*")
        out = capsys.readouterr().out
        assert "no measurements match" in out.lower()


# ---------------------------------------------------------------------------
# Title option
# ---------------------------------------------------------------------------


class TestPlotTitle:
    @patch("matplotlib.pyplot.close")
    @patch("matplotlib.pyplot.tight_layout")
    @patch("matplotlib.pyplot.subplots")
    def test_plot_custom_title(self, mock_subplots, mock_tight, mock_close, repl, capsys):
        mock_ax = MagicMock()
        mock_subplots.return_value = (MagicMock(), mock_ax)

        _store(repl, "vout_1", 3.3, "V")
        repl.onecmd('plot --title "My Custom Title"')

        mock_ax.set_title.assert_called_once_with("My Custom Title")


# ---------------------------------------------------------------------------
# Multiple units
# ---------------------------------------------------------------------------


class TestPlotMultipleUnits:
    @patch("matplotlib.pyplot.close")
    @patch("matplotlib.pyplot.tight_layout")
    @patch("matplotlib.pyplot.subplots")
    def test_plot_groups_by_unit(self, mock_subplots, mock_tight, mock_close, repl, capsys):
        mock_ax1 = MagicMock()
        mock_ax2 = MagicMock()
        mock_subplots.return_value = (MagicMock(), [mock_ax1, mock_ax2])

        _store(repl, "voltage_1", 3.3, "V")
        _store(repl, "current_1", 0.1, "A")

        repl.onecmd("plot")

        # Both axes should have been used
        mock_ax1.plot.assert_called_once()
        mock_ax2.plot.assert_called_once()


# ---------------------------------------------------------------------------
# Help
# ---------------------------------------------------------------------------


class TestPlotHelp:
    def test_plot_help(self, repl, capsys):
        repl.onecmd("plot --help")
        out = capsys.readouterr().out
        assert "plot" in out.lower()
