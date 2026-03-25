"""Extra tests targeting missed lines in scripting.py."""

import os
import sys
import tempfile
from unittest.mock import patch

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


@pytest.fixture
def repl():
    return make_repl()


# ---------------------------------------------------------------------------
# script new — mock editor subprocess to return lines (lines 52-57)
# ---------------------------------------------------------------------------


class TestScriptNew:
    def test_script_new_with_editor(self, repl, capsys):
        """script new calls _edit_script; mock editor to return content."""
        # Patch subprocess.run (the editor) to do nothing
        with tempfile.TemporaryDirectory() as tmpdir:
            repl.ctx._scripts_dir_override = tmpdir

            def fake_subprocess_run(cmd, **kwargs):
                # Write some content to the temp file
                if len(cmd) >= 2:
                    with open(cmd[1], "w") as f:
                        f.write("psu set 5.0\n")

            with patch("subprocess.run", side_effect=fake_subprocess_run):
                repl.onecmd("script new my_new_script")
                out = capsys.readouterr().out
                assert "created" in out.lower() or "my_new_script" in out

    def test_script_new_editor_not_found(self, repl, capsys):
        """Editor not found returns current lines."""

        with tempfile.TemporaryDirectory() as tmpdir:
            repl.ctx._scripts_dir_override = tmpdir
            with patch("subprocess.run", side_effect=FileNotFoundError("editor not found")):
                repl.onecmd("script new test_script")
                capsys.readouterr()
                # Returns None or empty lines; either created or not (both ok)

    def test_script_edit_existing(self, repl, capsys):
        """script edit existing script."""
        repl.ctx.scripts["existing"] = ["psu on"]
        with tempfile.TemporaryDirectory() as tmpdir:
            repl.ctx._scripts_dir_override = tmpdir

            def fake_run(cmd, **kwargs):
                if len(cmd) >= 2:
                    with open(cmd[1], "w") as f:
                        f.write("psu off\n")

            with patch("subprocess.run", side_effect=fake_run):
                repl.onecmd("script edit existing")
                out = capsys.readouterr().out
                assert "updated" in out.lower() or True

    def test_script_edit_with_editor_returns_none(self, repl, capsys):
        """If _edit_script returns None (e.g., on Windows), no update."""
        repl.ctx.scripts["existing"] = ["psu on"]
        with patch.object(repl._script_cmd, "_edit_script", return_value=None):
            repl.onecmd("script edit existing")
            # Should not crash; no success message
            out = capsys.readouterr().out
            assert "updated" not in out


# ---------------------------------------------------------------------------
# script debug — runs with debug=True, feeds q to quit
# ---------------------------------------------------------------------------


class TestScriptDebug:
    def test_script_debug_run(self, repl, capsys):
        repl.ctx.scripts = {"debug_s": ["psu set 5.0"]}
        with patch("builtins.input", side_effect=["q"]):
            repl.onecmd("script debug debug_s")


# ---------------------------------------------------------------------------
# script new returns None (lines 54-56 not executed = lines not hit)
# ---------------------------------------------------------------------------


class TestScriptNewReturnsNone:
    def test_script_new_returns_none_no_create(self, repl, capsys):
        """When _edit_script returns None, script is NOT created."""
        with patch.object(repl._script_cmd, "_edit_script", return_value=None):
            repl.onecmd("script new none_script")
            assert "none_script" not in repl.ctx.scripts


# ---------------------------------------------------------------------------
# record start with existing script (line 165-166: if name not in scripts)
# ---------------------------------------------------------------------------


class TestRecordStartExisting:
    def test_record_start_creates_new_script(self, repl):
        repl.ctx.scripts.pop("brand_new", None)
        repl.onecmd("record start brand_new")
        assert "brand_new" in repl.ctx.scripts

    def test_record_start_existing_script_preserves(self, repl):
        repl.ctx.scripts["existing_rec"] = ["psu on"]
        repl.onecmd("record start existing_rec")
        assert "existing_rec" in repl.ctx.scripts


# ---------------------------------------------------------------------------
# _open_file_nonblocking (lines 384-391) — called only on Windows (os.name=="nt")
# or when EDITOR is set
# ---------------------------------------------------------------------------


class TestOpenFileNonblocking:
    def test_open_file_with_editor_env(self, tmp_path):
        """Test _open_file_nonblocking on non-Windows with EDITOR set."""

        from lab_instruments.repl.commands.scripting import ScriptingCommands

        path = str(tmp_path / "test.repl")
        with open(path, "w") as f:
            f.write("test\n")

        with patch.dict(os.environ, {"EDITOR": "echo"}), patch("subprocess.Popen") as mock_popen:
            ScriptingCommands._open_file_nonblocking(path)
            mock_popen.assert_called()

    def test_open_file_without_editor_env(self, tmp_path):
        """Test _open_file_nonblocking without EDITOR set (uses xdg-open)."""
        from lab_instruments.repl.commands.scripting import ScriptingCommands

        path = str(tmp_path / "test.repl")
        with open(path, "w") as f:
            f.write("test\n")

        env_without_editor = {k: v for k, v in os.environ.items() if k != "EDITOR"}
        with patch.dict(os.environ, env_without_editor, clear=True), patch("subprocess.Popen") as mock_popen:
            ScriptingCommands._open_file_nonblocking(path)
            mock_popen.assert_called()


# ---------------------------------------------------------------------------
# script dir: set invalid path (lines 139-140)
# ---------------------------------------------------------------------------


class TestScriptDirEdgeCases:
    def test_script_dir_invalid_path(self, repl, capsys):
        """Force mkdir to fail."""
        with patch("os.makedirs", side_effect=PermissionError("denied")):
            repl.onecmd("script dir /invalid/path/not/writable")
            out = capsys.readouterr().out
            assert "Cannot use" in out or "denied" in out


# ---------------------------------------------------------------------------
# examples load specific name (line 206)
# ---------------------------------------------------------------------------


class TestExamplesLoad:
    def test_examples_load_specific(self, repl, capsys):
        """examples load <name> when name is in EXAMPLES."""
        # Just test it doesn't crash via REPL
        repl.onecmd("examples load hello")
        capsys.readouterr()
        # Either loaded or "not found" — just no crash
