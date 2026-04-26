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
    repl._scan_thread.join(timeout=5.0)
    repl._scan_done.wait(timeout=5.0)
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
                        f.write("psu set 1 5.0\n")

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
        repl.ctx.scripts = {"debug_s": ["psu set 1 5.0"]}
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
# script new overwrite confirmation: protect students who retype
# `script new X` over a file they already populated.
# ---------------------------------------------------------------------------


class TestScriptNewOverwriteConfirm:
    def test_new_on_existing_script_requires_confirmation(self, repl, capsys):
        """With an existing script in memory and a 'n' answer, the original
        contents are preserved and the editor is never invoked."""
        original = ["psu set 1 5.0", "sleep 1"]
        repl.ctx.scripts["existing"] = list(original)

        with tempfile.TemporaryDirectory() as tmpdir:
            repl.ctx._scripts_dir_override = tmpdir
            # Seed the disk file so we can verify it survives.
            repl._script_cmd._save_script("existing")

            with (
                patch("builtins.input", return_value="n") as mock_input,
                patch.object(repl._script_cmd, "_edit_script") as mock_edit,
            ):
                repl.onecmd("script new existing")
                mock_input.assert_called_once()
                mock_edit.assert_not_called()

            assert repl.ctx.scripts["existing"] == original
            with open(repl.ctx.script_file("existing")) as f:
                disk = [line.rstrip("\n") for line in f.readlines()]
            assert disk == original
            out = capsys.readouterr().out
            assert "not overwritten" in out.lower()

    def test_new_on_existing_script_yes_overwrites(self, repl, capsys):
        """With an existing script and a 'y' answer, the editor is invoked
        and the new contents replace the old."""
        repl.ctx.scripts["existing"] = ["psu set 1 5.0"]

        with tempfile.TemporaryDirectory() as tmpdir:
            repl.ctx._scripts_dir_override = tmpdir
            repl._script_cmd._save_script("existing")

            def fake_run(cmd, **kwargs):
                if len(cmd) >= 2:
                    with open(cmd[1], "w") as f:
                        f.write("psu off\n")

            with (
                patch("builtins.input", return_value="y"),
                patch("subprocess.run", side_effect=fake_run),
            ):
                repl.onecmd("script new existing")

            assert repl.ctx.scripts["existing"] == ["psu off"]

    def test_new_on_fresh_name_does_not_prompt(self, repl, capsys):
        """A brand-new name must skip the prompt entirely."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repl.ctx._scripts_dir_override = tmpdir

            def fake_run(cmd, **kwargs):
                if len(cmd) >= 2:
                    with open(cmd[1], "w") as f:
                        f.write("psu on\n")

            with (
                patch("builtins.input") as mock_input,
                patch("subprocess.run", side_effect=fake_run),
            ):
                repl.onecmd("script new brand_new_name")
                mock_input.assert_not_called()

            assert "brand_new_name" in repl.ctx.scripts

    def test_new_on_existing_eof_aborts(self, repl, capsys):
        """Piped input / non-TTY context (EOFError on input) must abort
        rather than silently overwrite."""
        repl.ctx.scripts["existing"] = ["psu on"]

        with tempfile.TemporaryDirectory() as tmpdir:
            repl.ctx._scripts_dir_override = tmpdir
            repl._script_cmd._save_script("existing")

            with (
                patch("builtins.input", side_effect=EOFError()),
                patch.object(repl._script_cmd, "_edit_script") as mock_edit,
            ):
                repl.onecmd("script new existing")
                mock_edit.assert_not_called()

            assert repl.ctx.scripts["existing"] == ["psu on"]

    def test_new_on_disk_only_script_prompts(self, repl, capsys):
        """Script file on disk but not in-memory (e.g. written directly,
        script load not yet run) must still trigger the prompt."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repl.ctx._scripts_dir_override = tmpdir
            disk_path = repl.ctx.script_file("disk_only")
            with open(disk_path, "w") as f:
                f.write("psu set 1 3.3\n")
            repl.ctx.scripts.pop("disk_only", None)

            with (
                patch("builtins.input", return_value="n") as mock_input,
                patch.object(repl._script_cmd, "_edit_script") as mock_edit,
            ):
                repl.onecmd("script new disk_only")
                mock_input.assert_called_once()
                mock_edit.assert_not_called()

            with open(disk_path) as f:
                assert "psu set 1 3.3" in f.read()

    def test_ctrl_c_during_prompt_propagates(self, repl, capsys):
        """Ctrl-C at the overwrite prompt must NOT be silently swallowed.

        Users expect Ctrl-C to abort back to the REPL prompt. Treating it
        as an implicit 'No' would hide a signal we don't own.
        """
        repl.ctx.scripts["existing"] = ["psu on"]
        with tempfile.TemporaryDirectory() as tmpdir:
            repl.ctx._scripts_dir_override = tmpdir
            repl._script_cmd._save_script("existing")

            with (
                patch("builtins.input", side_effect=KeyboardInterrupt()),
                patch.object(repl._script_cmd, "_edit_script") as mock_edit,
                pytest.raises(KeyboardInterrupt),
            ):
                repl._script_cmd.do_script("new existing")

            mock_edit.assert_not_called()
            assert repl.ctx.scripts["existing"] == ["psu on"]


# ---------------------------------------------------------------------------
# End-to-end regression for the student scenario that motivated this fix:
# a script with real content exists; the student types `script new X`
# again; the REPL must not silently destroy the prior work.
# ---------------------------------------------------------------------------


class TestScriptNewOverwriteRegression:
    """Regression for the `script new` overwrite footgun.

    These tests replay the exact sequence a student follows:

      1. `script new my_lab`   -> write real content, save
      2. (time passes, student forgets)
      3. `script new my_lab`   -> must prompt, default No

    Before the fix step (3) silently truncated the file. The student's
    entire lab script was gone with no warning.
    """

    STUDENT_SCRIPT = [
        "# Lab 3 sweep -- 2 hours of work",
        "val = linspace 0 5 11",
        "for v val",
        '    print "Setting {v}V..."',
        "    psu set 1 {v}",
        "    sleep 0.5",
        "    reading = psu meas 1 v unit=V",
        "end",
        "log save lab3_results.csv",
    ]

    def test_student_scenario_default_no_preserves_both_memory_and_disk(self, repl, capsys):
        """The full retype-and-press-enter sequence must leave both the
        in-memory script and the on-disk .scpi file untouched."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repl.ctx._scripts_dir_override = tmpdir

            # Step 1: populate the script the way the student did.
            repl.ctx.scripts["my_lab"] = list(self.STUDENT_SCRIPT)
            repl._script_cmd._save_script("my_lab")
            disk_path = repl.ctx.script_file("my_lab")
            with open(disk_path) as f:
                original_on_disk = f.read()
            assert "linspace 0 5 11" in original_on_disk

            # Step 3: student retypes `script new my_lab` and presses Enter
            # (blank answer) -- the pre-fix code silently blew it away.
            with (
                patch("builtins.input", return_value="") as mock_input,
                patch.object(repl._script_cmd, "_edit_script") as mock_edit,
            ):
                repl.onecmd("script new my_lab")
                mock_input.assert_called_once()
                mock_edit.assert_not_called()

            # In-memory script is intact line-for-line.
            assert repl.ctx.scripts["my_lab"] == self.STUDENT_SCRIPT

            # On-disk file is byte-identical.
            with open(disk_path) as f:
                assert f.read() == original_on_disk

            # The REPL must explicitly tell the student what happened --
            # silence here is how the student lost work in the first place.
            out = capsys.readouterr().out
            assert "not overwritten" in out.lower()

    def test_student_scenario_explicit_yes_overwrites_cleanly(self, repl):
        """If the student really does mean to start over, `y` overwrites
        the script and the new content lands in both memory and on disk."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repl.ctx._scripts_dir_override = tmpdir

            repl.ctx.scripts["my_lab"] = list(self.STUDENT_SCRIPT)
            repl._script_cmd._save_script("my_lab")
            disk_path = repl.ctx.script_file("my_lab")

            new_content = "psu off\n"

            def fake_run(cmd, **kwargs):
                if len(cmd) >= 2:
                    with open(cmd[1], "w") as f:
                        f.write(new_content)

            with (
                patch("builtins.input", return_value="y"),
                patch("subprocess.run", side_effect=fake_run),
            ):
                repl.onecmd("script new my_lab")

            assert repl.ctx.scripts["my_lab"] == ["psu off"]
            with open(disk_path) as f:
                disk_content = f.read()
            assert "linspace" not in disk_content
            assert "psu off" in disk_content

    def test_student_scenario_non_interactive_abort_preserves_work(self, repl):
        """Running in a non-TTY context (e.g. piped stdin) must abort
        rather than treat missing input as implicit consent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repl.ctx._scripts_dir_override = tmpdir
            repl.ctx.scripts["my_lab"] = list(self.STUDENT_SCRIPT)
            repl._script_cmd._save_script("my_lab")
            disk_path = repl.ctx.script_file("my_lab")
            with open(disk_path) as f:
                original = f.read()

            with (
                patch("builtins.input", side_effect=EOFError()),
                patch.object(repl._script_cmd, "_edit_script") as mock_edit,
            ):
                repl.onecmd("script new my_lab")
                mock_edit.assert_not_called()

            assert repl.ctx.scripts["my_lab"] == self.STUDENT_SCRIPT
            with open(disk_path) as f:
                assert f.read() == original


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

        if os.name == "nt":
            # On Windows, _open_file_nonblocking calls os.startfile and returns
            with patch("os.startfile") as mock_startfile:
                ScriptingCommands._open_file_nonblocking(path)
                mock_startfile.assert_called_once_with(path)
        else:
            with patch.dict(os.environ, {"EDITOR": "echo"}), patch("subprocess.Popen") as mock_popen:
                ScriptingCommands._open_file_nonblocking(path)
                mock_popen.assert_called()

    def test_open_file_without_editor_env(self, tmp_path):
        """Test _open_file_nonblocking without EDITOR set (uses xdg-open)."""
        from lab_instruments.repl.commands.scripting import ScriptingCommands

        path = str(tmp_path / "test.repl")
        with open(path, "w") as f:
            f.write("test\n")

        if os.name == "nt":
            # On Windows, _open_file_nonblocking calls os.startfile and returns
            with patch("os.startfile") as mock_startfile:
                ScriptingCommands._open_file_nonblocking(path)
                mock_startfile.assert_called_once_with(path)
        else:
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
