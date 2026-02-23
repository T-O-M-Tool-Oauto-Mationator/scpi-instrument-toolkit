"""Tests for data output dir, script dir, and path-based script run."""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def make_repl():
    from lab_instruments.src import discovery as _disc

    _disc.InstrumentDiscovery.__init__ = lambda self: None
    _disc.InstrumentDiscovery.scan = lambda self, verbose=True: {}
    from lab_instruments.repl import InstrumentRepl

    repl = InstrumentRepl()
    repl._scan_done.set()
    repl.devices = {}
    return repl


@pytest.fixture
def repl():
    return make_repl()


class TestDataDir:
    def test_show_no_args(self, repl, capsys):
        repl.onecmd("data")
        assert capsys.readouterr().out  # prints something

    def test_set_cwd(self, repl):
        repl.onecmd("data .")
        assert repl._data_dir_override == os.path.abspath(".")

    def test_set_tmp(self, repl, tmp_path):
        repl.onecmd(f"data {tmp_path.as_posix()}")
        assert repl._data_dir_override == str(tmp_path)

    def test_reset(self, repl, tmp_path):
        repl.onecmd(f"data {tmp_path.as_posix()}")
        repl.onecmd("data reset")
        assert repl._data_dir_override is None

    def test_get_data_dir_uses_override(self, repl, tmp_path):
        repl._data_dir_override = str(tmp_path)
        assert repl._get_data_dir() == str(tmp_path)


class TestScriptDir:
    def test_show_no_args(self, repl, capsys):
        repl.onecmd("script dir")
        assert capsys.readouterr().out

    def test_set_tmp(self, repl, tmp_path):
        repl.onecmd(f"script dir {tmp_path.as_posix()}")
        assert repl._scripts_dir_override == str(tmp_path)

    def test_reset(self, repl, tmp_path):
        repl.onecmd(f"script dir {tmp_path.as_posix()}")
        repl.onecmd("script dir reset")
        assert repl._scripts_dir_override is None


class TestScriptRunByPath:
    def test_run_by_path(self, repl, tmp_path):
        script = tmp_path / "hello.scpi"
        script.write_text("print hello\n")
        repl.onecmd(f"script run {script}")  # no exception = pass

    def test_run_missing_path_errors(self, repl, capsys):
        repl.onecmd("script run ./nonexistent_xyz.scpi")
        out = capsys.readouterr().out
        assert any(w in out.lower() for w in ["cannot", "error", "not found"])
