"""Tests for scripting REPL commands: script, record, examples, python, limits."""

import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lab_instruments.mock_instruments import MockHP_E3631A


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


@pytest.fixture
def repl():
    return make_repl({"psu1": MockHP_E3631A()})


# ---------------------------------------------------------------------------
# script command
# ---------------------------------------------------------------------------


class TestScriptCommand:
    def test_script_no_args_shows_help(self, repl, capsys):
        repl.onecmd("script")
        out = capsys.readouterr().out
        assert out != ""

    def test_script_help_flag(self, repl, capsys):
        repl.onecmd("script --help")
        out = capsys.readouterr().out
        assert out != ""

    def test_script_list_empty(self, repl, capsys):
        repl.ctx.scripts = {}
        repl.onecmd("script list")
        out = capsys.readouterr().out
        assert "No scripts" in out

    def test_script_list_with_scripts(self, repl, capsys):
        repl.ctx.scripts = {"test_s": ["psu set 5.0"]}
        repl.onecmd("script list")
        out = capsys.readouterr().out
        assert "test_s" in out

    def test_script_show(self, repl, capsys):
        repl.ctx.scripts = {"my_script": ["psu set 5.0", "psu on"]}
        repl.onecmd("script show my_script")
        out = capsys.readouterr().out
        assert "psu set 5.0" in out

    def test_script_show_not_found(self, repl, capsys):
        repl.ctx.scripts = {}
        repl.onecmd("script show nonexistent")
        out = capsys.readouterr().out
        assert "not found" in out.lower()

    def test_script_run(self, repl, capsys):
        repl.ctx.scripts = {"test_run": ["psu set 5.0"]}
        repl.onecmd("script run test_run")

    def test_script_run_not_found(self, repl, capsys):
        repl.ctx.scripts = {}
        repl.onecmd("script run nonexistent")
        out = capsys.readouterr().out
        assert "not found" in out.lower()

    def test_script_debug_not_found(self, repl, capsys):
        repl.ctx.scripts = {}
        repl.onecmd("script debug nonexistent")
        out = capsys.readouterr().out
        assert "not found" in out.lower()

    def test_script_rm(self, repl, capsys):
        repl.ctx.scripts = {"to_delete": ["psu on"]}
        repl.onecmd("script rm to_delete")
        assert "to_delete" not in repl.ctx.scripts
        out = capsys.readouterr().out
        assert "deleted" in out.lower()

    def test_script_rm_not_found(self, repl, capsys):
        repl.ctx.scripts = {}
        repl.onecmd("script rm nonexistent")
        out = capsys.readouterr().out
        assert "not found" in out.lower()

    def test_script_import(self, repl, capsys):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".scpi", delete=False, encoding="utf-8") as f:
            f.write("psu set 5.0\npsu on\n")
            fname = f.name
        try:
            repl.onecmd(f"script import imported_s {fname}")
            assert "imported_s" in repl.ctx.scripts
            out = capsys.readouterr().out
            assert "Imported" in out
        finally:
            os.unlink(fname)

    def test_script_import_bad_path(self, repl, capsys):
        repl.onecmd("script import myname /nonexistent/path/file.scpi")
        out = capsys.readouterr().out
        assert "Failed" in out or "Error" in out.lower()

    def test_script_load(self, repl, capsys):
        repl.onecmd("script load")
        out = capsys.readouterr().out
        assert "Loaded" in out

    def test_script_save(self, repl, capsys):
        repl.ctx.scripts = {}
        repl.onecmd("script save")
        out = capsys.readouterr().out
        assert "Saved" in out

    def test_script_dir_no_args(self, repl, capsys):
        repl.onecmd("script dir")
        out = capsys.readouterr().out
        assert "Scripts dir" in out or "scripts" in out.lower()

    def test_script_dir_reset(self, repl, capsys):
        repl.onecmd("script dir reset")
        out = capsys.readouterr().out
        assert "reset" in out.lower()

    def test_script_dir_set_path(self, repl, capsys):
        with tempfile.TemporaryDirectory() as tmpdir:
            repl.onecmd(f"script dir {tmpdir}")
            out = capsys.readouterr().out
            assert "set" in out.lower() or tmpdir in out

    def test_script_unknown_subcmd(self, repl, capsys):
        repl.onecmd("script xyz")
        out = capsys.readouterr().out
        assert "Unknown" in out or "xyz" in out


# ---------------------------------------------------------------------------
# record command
# ---------------------------------------------------------------------------


class TestRecord:
    def test_record_no_args_when_not_recording(self, repl, capsys):
        repl.ctx.record_script = None
        repl.onecmd("record")
        out = capsys.readouterr().out
        assert "Not recording" in out

    def test_record_no_args_when_recording(self, repl, capsys):
        repl.ctx.record_script = "live_script"
        repl.ctx.scripts["live_script"] = []
        repl.onecmd("record")
        out = capsys.readouterr().out
        assert "live_script" in out
        repl.ctx.record_script = None

    def test_record_start(self, repl, capsys):
        repl.onecmd("record start my_recording")
        assert repl.ctx.record_script == "my_recording"
        out = capsys.readouterr().out
        assert "Recording" in out
        repl.ctx.record_script = None

    def test_record_stop(self, repl, capsys):
        repl.ctx.record_script = "my_recording"
        repl.ctx.scripts["my_recording"] = ["psu on"]
        repl.onecmd("record stop")
        assert repl.ctx.record_script is None
        out = capsys.readouterr().out
        assert "Stopped" in out

    def test_record_stop_when_not_recording(self, repl, capsys):
        repl.ctx.record_script = None
        repl.onecmd("record stop")
        out = capsys.readouterr().out
        assert "Not recording" in out

    def test_record_status_recording(self, repl, capsys):
        repl.ctx.record_script = "live"
        repl.ctx.scripts["live"] = ["psu on", "psu set 5.0"]
        repl.onecmd("record status")
        out = capsys.readouterr().out
        assert "live" in out
        repl.ctx.record_script = None

    def test_record_status_not_recording(self, repl, capsys):
        repl.ctx.record_script = None
        repl.onecmd("record status")
        out = capsys.readouterr().out
        assert "Not recording" in out


# ---------------------------------------------------------------------------
# examples command
# ---------------------------------------------------------------------------


class TestExamples:
    def test_examples_list(self, repl, capsys):
        repl.onecmd("examples")
        # Either shows examples or warns none available
        out = capsys.readouterr().out
        assert out != ""

    def test_examples_load_all(self, repl, capsys):
        repl.onecmd("examples load all")
        capsys.readouterr()
        # Should either load or say not found — just no crash

    def test_examples_load_nonexistent(self, repl, capsys):
        repl.onecmd("examples load nonexistent_example_xyz")
        out = capsys.readouterr().out
        assert out != ""


# ---------------------------------------------------------------------------
# python command
# ---------------------------------------------------------------------------


class TestPythonCommand:
    def test_python_no_args(self, repl, capsys):
        repl.onecmd("python")
        out = capsys.readouterr().out
        assert out != ""

    def test_python_file_not_found(self, repl, capsys):
        repl.onecmd("python /nonexistent/path/script.py")
        out = capsys.readouterr().out
        assert "not found" in out.lower() or "File not found" in out

    def test_python_execute_script(self, repl, capsys):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("x = 1 + 1\n")
            fname = f.name
        try:
            repl.onecmd(f"python {fname}")
            out = capsys.readouterr().out
            assert "executed" in out.lower() or "Executing" in out
        finally:
            os.unlink(fname)

    def test_python_failing_script(self, repl, capsys):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("raise ValueError('test error')\n")
            fname = f.name
        try:
            repl.onecmd(f"python {fname}")
            out = capsys.readouterr().out
            assert "failed" in out.lower() or "test error" in out
        finally:
            os.unlink(fname)


# ---------------------------------------------------------------------------
# upper_limit / lower_limit commands
# ---------------------------------------------------------------------------


class TestLimits:
    def test_upper_limit_no_args(self, repl, capsys):
        repl.onecmd("upper_limit")
        out = capsys.readouterr().out
        assert out != ""

    def test_upper_limit_psu_voltage(self, repl, capsys):
        repl.onecmd("upper_limit psu1 voltage 5.0")
        out = capsys.readouterr().out
        assert "Limit" in out or "limit" in out.lower()

    def test_upper_limit_psu_current(self, repl, capsys):
        repl.onecmd("upper_limit psu1 current 0.5")
        out = capsys.readouterr().out
        assert out != ""

    def test_lower_limit_no_args(self, repl, capsys):
        repl.onecmd("lower_limit")
        out = capsys.readouterr().out
        assert out != ""

    def test_lower_limit_psu_voltage(self, repl, capsys):
        repl.onecmd("lower_limit psu1 voltage 0.0")
        out = capsys.readouterr().out
        assert out != ""
