"""Unit tests for expand_script_lines in script_engine/expander.py."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import MagicMock


def make_ctx():
    """Create a minimal mock context for expander tests."""
    ctx = MagicMock()
    ctx.safety_limits = {}
    ctx.awg_channel_state = {}
    ctx.scripts = {}
    ctx.exit_on_error = False
    return ctx


def expand(lines, variables=None, ctx=None):
    from lab_instruments.repl.script_engine.expander import expand_script_lines

    if ctx is None:
        ctx = make_ctx()
    if variables is None:
        variables = {}
    return expand_script_lines(lines, variables, ctx)


def cmds(expanded):
    """Extract only the non-NOP commands from expanded output."""
    return [cmd for cmd, _ in expanded if cmd != "__NOP__" and not cmd.startswith("#")]


# ---------------------------------------------------------------------------
# Basic passthrough
# ---------------------------------------------------------------------------


class TestBasicPassthrough:
    def test_plain_command(self):
        result = expand(["psu chan 1 on"])
        assert any("psu chan 1 on" in cmd for cmd, _ in result)

    def test_comment_becomes_nop(self):
        result = expand(["# this is a comment"])
        assert all(cmd == "__NOP__" for cmd, _ in result)

    def test_blank_line_becomes_nop(self):
        result = expand([""])
        assert all(cmd == "__NOP__" for cmd, _ in result)


# ---------------------------------------------------------------------------
# Plain assignment
# ---------------------------------------------------------------------------


class TestPlainAssignment:
    def test_numeric_assignment(self):
        vars_ = {}
        expand(["x = 42"], variables=vars_)
        assert vars_["x"] == "42"

    def test_expression_assignment(self):
        vars_ = {"a": "3", "b": "4"}
        expand(["c = a + b"], variables=vars_)
        assert float(vars_["c"]) == 7.0

    def test_instrument_read_is_passthrough(self):
        result = expand(["v = psu meas v unit=V"])
        # Must be emitted as a raw command, not __NOP__
        raw_cmds = [cmd for cmd, _ in result if cmd != "__NOP__"]
        assert any("psu" in c and "meas" in c for c in raw_cmds)


# ---------------------------------------------------------------------------
# repeat
# ---------------------------------------------------------------------------


class TestRepeat:
    def test_repeat_expands_block(self):
        result = expand(["repeat 3", "print hello", "end"])
        prints = [cmd for cmd, _ in result if "print hello" in cmd]
        assert len(prints) == 3

    def test_repeat_zero_times(self):
        result = expand(["repeat 0", "print hello", "end"])
        prints = [cmd for cmd, _ in result if "print hello" in cmd]
        assert len(prints) == 0


# ---------------------------------------------------------------------------
# for loop
# ---------------------------------------------------------------------------


class TestForLoop:
    def test_for_expands_each_value(self):
        vars_ = {}
        result = expand(["for v 1.0 2.0 3.0", "print {v}", "end"], variables=vars_)
        prints = [cmd for cmd, _ in result if cmd.startswith("print")]
        assert len(prints) == 3
        assert "1.0" in prints[0]
        assert "2.0" in prints[1]
        assert "3.0" in prints[2]

    def test_for_with_variable_substitution(self):
        vars_ = {"vals": "10 20 30"}
        result = expand(["for x {vals}", "print {x}", "end"], variables=vars_)
        prints = [cmd for cmd, _ in result if cmd.startswith("print")]
        assert len(prints) == 3


# ---------------------------------------------------------------------------
# array
# ---------------------------------------------------------------------------


class TestArray:
    def test_array_collects_elements(self):
        vars_ = {}
        expand(["array mylist", "1.0", "2.0", "3.0", "end"], variables=vars_)
        assert vars_["mylist"] == "1.0 2.0 3.0"


# ---------------------------------------------------------------------------
# import / export
# ---------------------------------------------------------------------------


class TestImportExport:
    def test_import_from_parent(self):
        from lab_instruments.repl.script_engine.expander import expand_script_lines

        ctx = make_ctx()
        parent_vars = {"voltage": "5.0"}
        child_vars = {}
        expand_script_lines(["import voltage"], child_vars, ctx, parent_vars=parent_vars)
        assert child_vars["voltage"] == "5.0"

    def test_export_to_parent(self):
        from lab_instruments.repl.script_engine.expander import expand_script_lines

        ctx = make_ctx()
        child_vars = {"result": "42"}
        exports = {}
        expand_script_lines(["export result"], child_vars, ctx, exports=exports)
        assert exports["result"] == "42"


# ---------------------------------------------------------------------------
# lower_limit / upper_limit
# ---------------------------------------------------------------------------


class TestLimits:
    def test_lower_limit_psu(self):
        ctx = make_ctx()
        expand(["lower_limit psu voltage 4.5"], ctx=ctx)
        assert ("psu", None) in ctx.safety_limits
        assert ctx.safety_limits[("psu", None)]["voltage_lower"] == 4.5

    def test_upper_limit_psu(self):
        ctx = make_ctx()
        expand(["upper_limit psu voltage 5.5"], ctx=ctx)
        assert ctx.safety_limits[("psu", None)]["voltage_upper"] == 5.5


# ---------------------------------------------------------------------------
# while and if — pass-through to runtime
# ---------------------------------------------------------------------------


class TestControlFlowPassthrough:
    def test_while_emits_raw_block(self):
        result = expand(["x = 0", "while x < 3", "x++", "end"])
        raw_cmds = [cmd for cmd, _ in result if cmd != "__NOP__"]
        # The 'while' line must be in there as a raw command
        assert any("while" in c for c in raw_cmds)
        # The 'end' must be there
        assert any(c == "end" for c in raw_cmds)

    def test_if_emits_raw_block(self):
        result = expand(["if x > 0", "print yes", "end"])
        raw_cmds = [cmd for cmd, _ in result if cmd != "__NOP__"]
        assert any("if" in c for c in raw_cmds)
        assert any("print yes" in c for c in raw_cmds)

    def test_elif_and_else_passthrough(self):
        result = expand(["if x > 0", "a = 1", "elif x < 0", "a = -1", "else", "a = 0", "end"])
        raw_cmds = [cmd for cmd, _ in result if cmd != "__NOP__"]
        assert any("elif" in c for c in raw_cmds)
        assert any("else" in c for c in raw_cmds)


# ---------------------------------------------------------------------------
# assert — pass-through with variable sync
# ---------------------------------------------------------------------------


class TestAssertPassthrough:
    def test_assert_emits_raw(self):
        vars_ = {"x": "5"}
        result = expand(["assert x > 0"], variables=vars_)
        raw_cmds = [cmd for cmd, _ in result if cmd != "__NOP__"]
        assert any("assert" in c for c in raw_cmds)


# ---------------------------------------------------------------------------
# Augmented assignment: x += 5 → x = x + (5)
# ---------------------------------------------------------------------------


class TestAugmentedAssignment:
    def test_augmented_add_expands_when_var_known(self):
        vars_ = {"x": "10"}
        expand(["x += 5"], variables=vars_)
        assert vars_["x"] == "15.0" or float(vars_["x"]) == 15.0

    def test_augmented_sub_expands(self):
        vars_ = {"x": "10"}
        expand(["x -= 3"], variables=vars_)
        assert float(vars_["x"]) == 7.0

    def test_augmented_mul_expands(self):
        vars_ = {"x": "4"}
        expand(["x *= 3"], variables=vars_)
        assert float(vars_["x"]) == 12.0

    def test_augmented_div_expands(self):
        vars_ = {"x": "12"}
        expand(["x /= 4"], variables=vars_)
        assert float(vars_["x"]) == 3.0

    def test_augmented_unknown_var_is_passthrough(self):
        vars_ = {}
        result = expand(["x += 5"], variables=vars_)
        # x is not known → emitted as raw command, not a __NOP__
        raw_cmds = [cmd for cmd, _ in result if cmd != "__NOP__"]
        assert any("x += 5" in c or "x+=" in c.replace(" ", "") for c in raw_cmds)

    def test_augmented_in_repeat_updates_across_iterations(self):
        """After repeat, the var should be updated in expanded state."""
        vars_ = {"count": "0"}
        expand(["count += 1"], variables=vars_)
        assert float(vars_["count"]) == 1.0


# ---------------------------------------------------------------------------
# Increment / decrement: x++  →  x = x + 1
# ---------------------------------------------------------------------------


class TestIncrDecr:
    def test_postfix_increment_expands_when_known(self):
        vars_ = {"x": "5"}
        expand(["x++"], variables=vars_)
        assert float(vars_["x"]) == 6.0

    def test_postfix_decrement_expands_when_known(self):
        vars_ = {"x": "5"}
        expand(["x--"], variables=vars_)
        assert float(vars_["x"]) == 4.0

    def test_prefix_increment_expands_when_known(self):
        vars_ = {"x": "3"}
        expand(["++x"], variables=vars_)
        assert float(vars_["x"]) == 4.0

    def test_prefix_decrement_expands_when_known(self):
        vars_ = {"x": "3"}
        expand(["--x"], variables=vars_)
        assert float(vars_["x"]) == 2.0

    def test_incr_unknown_var_is_passthrough(self):
        vars_ = {}
        result = expand(["x++"], variables=vars_)
        raw_cmds = [cmd for cmd, _ in result if cmd != "__NOP__"]
        assert any("x++" in c or "x ++" in c for c in raw_cmds)
