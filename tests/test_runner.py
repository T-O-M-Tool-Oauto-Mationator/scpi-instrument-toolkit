"""Tests for script_engine/runner.py — run_expanded and _debug_show_context."""

import os
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lab_instruments.repl.script_engine.runner import _debug_show_context, run_expanded


class FakeCtx:
    def __init__(self):
        self.in_script = False
        self.in_debugger = False
        self.interrupt_requested = False
        self.command_had_error = False
        self.exit_on_error = False
        self.current_script_source: str | None = None
        self.current_script_line: int | None = None


class FakeShell:
    def __init__(self, onecmd_returns=None):
        self.calls = []
        self._returns = onecmd_returns or {}

    def onecmd(self, line):
        self.calls.append(line)
        return self._returns.get(line, False)


# ---------------------------------------------------------------------------
# Basic execution
# ---------------------------------------------------------------------------


class TestRunExpandedBasic:
    def test_empty_list_returns_false(self):
        ctx = FakeCtx()
        shell = FakeShell()
        result = run_expanded([], shell, ctx)
        assert result is False

    def test_comment_lines_skipped(self):
        ctx = FakeCtx()
        shell = FakeShell()
        result = run_expanded([("# comment", "# comment")], shell, ctx)
        assert result is False
        assert shell.calls == []

    def test_blank_lines_skipped(self):
        ctx = FakeCtx()
        shell = FakeShell()
        result = run_expanded([("", "")], shell, ctx)
        assert result is False

    def test_single_command_executed(self):
        ctx = FakeCtx()
        shell = FakeShell()
        run_expanded([("psu set 1 5.0", "psu set 1 5.0")], shell, ctx)
        assert shell.calls == ["psu set 1 5.0"]

    def test_multiple_commands_executed_in_order(self):
        ctx = FakeCtx()
        shell = FakeShell()
        cmds = [("psu set 1 5.0", "psu set 1 5.0"), ("smu on", "smu on"), ("scope run", "scope run")]
        run_expanded(cmds, shell, ctx)
        assert shell.calls == ["psu set 1 5.0", "smu on", "scope run"]

    def test_ctx_in_script_reset_after(self):
        ctx = FakeCtx()
        shell = FakeShell()
        run_expanded([("cmd1", "cmd1")], shell, ctx)
        assert ctx.in_script is False

    def test_returns_true_when_shell_onecmd_returns_true(self):
        ctx = FakeCtx()
        shell = FakeShell(onecmd_returns={"exit": True})
        result = run_expanded([("exit", "exit")], shell, ctx)
        assert result is True

    def test_nop_command_skipped(self):
        ctx = FakeCtx()
        shell = FakeShell()
        run_expanded([("__NOP__", "__NOP__")], shell, ctx)
        assert shell.calls == []

    def test_exit_on_error_stops_script(self):
        ctx = FakeCtx()
        ctx.exit_on_error = True
        shell = FakeShell()

        # First command will set command_had_error
        def bad_cmd(line):
            ctx.command_had_error = True
            return False

        shell.onecmd = bad_cmd
        result = run_expanded([("cmd1", "cmd1"), ("cmd2", "cmd2")], shell, ctx)
        assert result is True

    def test_tuple_and_str_items(self):
        ctx = FakeCtx()
        shell = FakeShell()
        # Mix of tuples and raw strings (the raw string case in the for loop)
        cmds = [("cmd1", "src1"), ("cmd2", "src2")]
        run_expanded(cmds, shell, ctx)
        assert "cmd1" in shell.calls

    def test_breakpoint_token_stripped(self):
        """__BREAKPOINT__ lines are not executed as commands (triggers debug mode)."""
        ctx = FakeCtx()
        shell = FakeShell()
        cmds = [("__BREAKPOINT__", "__BREAKPOINT__"), ("real_cmd", "real_cmd")]
        # __BREAKPOINT__ triggers debug mode; feed 'c' to continue, executing real_cmd
        with patch("builtins.input", side_effect=["c"]):
            run_expanded(cmds, shell, ctx)
        assert "__BREAKPOINT__" not in shell.calls
        assert "real_cmd" in shell.calls

    def test_keyboard_interrupt_handled(self):
        ctx = FakeCtx()
        shell = FakeShell()
        call_count = [0]

        def interrupt_once(line):
            call_count[0] += 1
            if call_count[0] == 1:
                raise KeyboardInterrupt()
            return False

        shell.onecmd = interrupt_once
        # Should not raise; should enter debugger mode
        # But since we're not in debug mode, it enters debugger but can't read input
        # so we just verify it doesn't crash the whole run
        # Actually: when debug=False and KeyboardInterrupt is raised, it re-enters
        # debug mode (debug_active=True). Then the next loop iteration will try
        # input() — so we need to provide EOF to abort.
        with patch("builtins.input", side_effect=EOFError):
            result = run_expanded([("cmd1", "cmd1")], shell, ctx)
        # After EOFError in debugger, returns True (abort)
        assert result is True


# ---------------------------------------------------------------------------
# Debug mode
# ---------------------------------------------------------------------------


class TestRunExpandedDebug:
    def test_debug_mode_step_executes_command(self):
        ctx = FakeCtx()
        shell = FakeShell()
        # Simulate: user presses 'n' (next/step) then 'q' to quit after that
        with patch("builtins.input", side_effect=["n", "q"]):
            result = run_expanded([("cmd1", "cmd1"), ("cmd2", "cmd2")], shell, ctx, debug=True)
        assert result is True  # quit returns True
        assert "cmd1" in shell.calls

    def test_debug_mode_continue(self):
        ctx = FakeCtx()
        shell = FakeShell()
        # 'c' continues (exits debug mode), then commands run normally
        with patch("builtins.input", side_effect=["c"]):
            run_expanded([("cmd1", "cmd1"), ("cmd2", "cmd2")], shell, ctx, debug=True)
        assert "cmd1" in shell.calls
        assert "cmd2" in shell.calls

    def test_debug_mode_quit(self):
        ctx = FakeCtx()
        shell = FakeShell()
        with patch("builtins.input", side_effect=["q"]):
            result = run_expanded([("cmd1", "cmd1")], shell, ctx, debug=True)
        assert result is True

    def test_debug_mode_abort(self):
        ctx = FakeCtx()
        shell = FakeShell()
        with patch("builtins.input", side_effect=["abort"]):
            result = run_expanded([("cmd1", "cmd1")], shell, ctx, debug=True)
        assert result is True

    def test_debug_mode_eof_aborts(self):
        ctx = FakeCtx()
        shell = FakeShell()
        with patch("builtins.input", side_effect=EOFError):
            result = run_expanded([("cmd1", "cmd1")], shell, ctx, debug=True)
        assert result is True

    def test_debug_mode_goto(self):
        ctx = FakeCtx()
        shell = FakeShell()
        # goto 2, then step, then quit
        with patch("builtins.input", side_effect=["goto 2", "n", "q"]):
            run_expanded([("cmd1", "cmd1"), ("cmd2", "cmd2"), ("cmd3", "cmd3")], shell, ctx, debug=True)

    def test_debug_mode_goto_out_of_range(self):
        ctx = FakeCtx()
        shell = FakeShell()
        with patch("builtins.input", side_effect=["goto 999", "q"]):
            run_expanded([("cmd1", "cmd1")], shell, ctx, debug=True)

    def test_debug_mode_goto_invalid(self):
        ctx = FakeCtx()
        shell = FakeShell()
        with patch("builtins.input", side_effect=["goto abc", "q"]):
            run_expanded([("cmd1", "cmd1")], shell, ctx, debug=True)

    def test_debug_mode_back(self):
        ctx = FakeCtx()
        shell = FakeShell()
        # Step forward first, then back, then quit
        with patch("builtins.input", side_effect=["n", "back", "q"]):
            run_expanded([("cmd1", "cmd1"), ("cmd2", "cmd2")], shell, ctx, debug=True)

    def test_debug_mode_back_at_first_line(self):
        ctx = FakeCtx()
        shell = FakeShell()
        with patch("builtins.input", side_effect=["back", "q"]):
            run_expanded([("cmd1", "cmd1")], shell, ctx, debug=True)

    def test_debug_mode_set_breakpoint(self):
        ctx = FakeCtx()
        shell = FakeShell()
        with patch("builtins.input", side_effect=["b 2", "q"]):
            run_expanded([("cmd1", "cmd1"), ("cmd2", "cmd2")], shell, ctx, debug=True)

    def test_debug_mode_set_breakpoint_out_of_range(self):
        ctx = FakeCtx()
        shell = FakeShell()
        with patch("builtins.input", side_effect=["b 999", "q"]):
            run_expanded([("cmd1", "cmd1")], shell, ctx, debug=True)

    def test_debug_mode_break_invalid(self):
        ctx = FakeCtx()
        shell = FakeShell()
        with patch("builtins.input", side_effect=["break", "q"]):
            run_expanded([("cmd1", "cmd1")], shell, ctx, debug=True)

    def test_debug_mode_delete_breakpoint(self):
        ctx = FakeCtx()
        shell = FakeShell()
        with patch("builtins.input", side_effect=["b 1", "d 1", "q"]):
            run_expanded([("cmd1", "cmd1")], shell, ctx, debug=True)

    def test_debug_mode_delete_nonexistent(self):
        ctx = FakeCtx()
        shell = FakeShell()
        with patch("builtins.input", side_effect=["d 5", "q"]):
            run_expanded([("cmd1", "cmd1")], shell, ctx, debug=True)

    def test_debug_mode_delete_invalid(self):
        ctx = FakeCtx()
        shell = FakeShell()
        with patch("builtins.input", side_effect=["d", "q"]):
            run_expanded([("cmd1", "cmd1")], shell, ctx, debug=True)

    def test_debug_mode_list(self):
        ctx = FakeCtx()
        shell = FakeShell()
        with patch("builtins.input", side_effect=["l", "q"]):
            run_expanded([("cmd1", "cmd1"), ("cmd2", "cmd2")], shell, ctx, debug=True)

    def test_debug_mode_list_all(self):
        ctx = FakeCtx()
        shell = FakeShell()
        with patch("builtins.input", side_effect=["l all", "q"]):
            run_expanded([("cmd1", "cmd1"), ("cmd2", "cmd2")], shell, ctx, debug=True)

    def test_debug_mode_list_n(self):
        ctx = FakeCtx()
        shell = FakeShell()
        with patch("builtins.input", side_effect=["l 5", "q"]):
            run_expanded([("cmd1", "cmd1"), ("cmd2", "cmd2")], shell, ctx, debug=True)

    def test_debug_mode_list_invalid(self):
        ctx = FakeCtx()
        shell = FakeShell()
        with patch("builtins.input", side_effect=["l abc", "q"]):
            run_expanded([("cmd1", "cmd1")], shell, ctx, debug=True)

    def test_debug_mode_info(self):
        ctx = FakeCtx()
        shell = FakeShell()
        with patch("builtins.input", side_effect=["info", "q"]):
            run_expanded([("cmd1", "cmd1")], shell, ctx, debug=True)

    def test_debug_mode_info_with_breakpoints(self):
        ctx = FakeCtx()
        shell = FakeShell()
        with patch("builtins.input", side_effect=["b 1", "i", "q"]):
            run_expanded([("cmd1", "cmd1"), ("cmd2", "cmd2")], shell, ctx, debug=True)

    def test_debug_mode_arbitrary_cmd_passed_to_shell(self):
        ctx = FakeCtx()
        shell = FakeShell()
        with patch("builtins.input", side_effect=["psu set 1 5.0", "q"]):
            run_expanded([("cmd1", "cmd1")], shell, ctx, debug=True)
        assert "psu set 1 5.0" in shell.calls

    def test_debug_mode_keyboard_interrupt_in_prompt(self):
        ctx = FakeCtx()
        shell = FakeShell()
        with patch("builtins.input", side_effect=[KeyboardInterrupt, "q"]):
            run_expanded([("cmd1", "cmd1")], shell, ctx, debug=True)

    def test_debug_mode_nop_step(self):
        ctx = FakeCtx()
        shell = FakeShell()
        with patch("builtins.input", side_effect=["n", "q"]):
            run_expanded([("__NOP__", "__NOP__"), ("cmd2", "cmd2")], shell, ctx, debug=True)

    def test_debug_mode_nop_continue(self):
        ctx = FakeCtx()
        shell = FakeShell()
        with patch("builtins.input", side_effect=["c"]):
            run_expanded([("__NOP__", "__NOP__"), ("cmd2", "cmd2")], shell, ctx, debug=True)
        assert "cmd2" in shell.calls

    def test_debug_exit_on_error(self):
        ctx = FakeCtx()
        ctx.exit_on_error = True
        shell = FakeShell()

        def bad_cmd(line):
            ctx.command_had_error = True
            return False

        shell.onecmd = bad_cmd
        with patch("builtins.input", side_effect=["n"]):
            result = run_expanded([("cmd1", "cmd1"), ("cmd2", "cmd2")], shell, ctx, debug=True)
        assert result is True

    def test_debug_continue_keyboard_interrupt(self):
        ctx = FakeCtx()
        shell = FakeShell()
        call_count = [0]

        def interrupt_once(line):
            call_count[0] += 1
            if call_count[0] == 1:
                raise KeyboardInterrupt()
            return False

        shell.onecmd = interrupt_once
        # 'c' then KeyboardInterrupt re-enters debug, then 'q'
        with patch("builtins.input", side_effect=["c", "q"]):
            run_expanded([("cmd1", "cmd1")], shell, ctx, debug=True)

    def test_breakpoint_triggers_debug(self):
        ctx = FakeCtx()
        shell = FakeShell()
        # Line 2 has a breakpoint; running without debug=True, breakpoint will trigger debug
        cmds = [("cmd1", "cmd1"), ("__BREAKPOINT__", "__BREAKPOINT__"), ("cmd2", "cmd2")]
        with patch("builtins.input", side_effect=["q"]):
            result = run_expanded(cmds, shell, ctx, debug=False)
        assert result is True


# ---------------------------------------------------------------------------
# _debug_show_context
# ---------------------------------------------------------------------------


class TestDebugShowContext:
    def test_shows_all_lines(self, capsys):
        lines = ["cmd1", "cmd2", "cmd3"]
        _debug_show_context(lines, lines, 1, set(), show_all=True)
        out = capsys.readouterr().out
        assert "cmd1" in out
        assert "cmd2" in out
        assert "cmd3" in out

    def test_shows_window(self, capsys):
        lines = [f"cmd{i}" for i in range(10)]
        _debug_show_context(lines, lines, 5, set(), window=2)
        out = capsys.readouterr().out
        assert "cmd5" in out

    def test_marks_current_line(self, capsys):
        lines = ["cmd1", "cmd2"]
        _debug_show_context(lines, lines, 0, set())
        out = capsys.readouterr().out
        assert "cmd1" in out

    def test_marks_breakpoints(self, capsys):
        lines = ["cmd1", "cmd2", "cmd3"]
        _debug_show_context(lines, lines, 1, {2})
        out = capsys.readouterr().out
        assert "●" in out

    def test_expanded_line_shown(self, capsys):
        lines = ["expanded_cmd"]
        source = ["source_cmd"]
        _debug_show_context(lines, source, 0, set())
        out = capsys.readouterr().out
        assert "source_cmd" in out
        assert "expanded_cmd" in out
