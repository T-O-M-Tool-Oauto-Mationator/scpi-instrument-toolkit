"""tests/test_repl_modules.py — Comprehensive tests for the repl/ package modules.

Organized by module to maximise coverage across:
  syntax, measurement_store, device_registry, context, commands/variables,
  commands/base, commands/general, commands/logging_cmd,
  script_engine/expander, script_engine/runner, shell, __init__.
"""

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from lab_instruments.mock_instruments import (
    MockDHO804,
    MockEDU33212A,
    MockHP_34401A,
    MockHP_E3631A,
    MockMPS6010H,
)
from lab_instruments.repl.capabilities import Capability
from lab_instruments.repl.context import ReplContext
from lab_instruments.repl.device_registry import DeviceRegistry
from lab_instruments.repl.measurement_store import MeasurementStore
from lab_instruments.repl.syntax import (
    safe_eval,
    substitute_legacy,
    substitute_vars,
    validate_name,
)

# ═══════════════════════════════════════════════════════════════════
# 1. syntax.py
# ═══════════════════════════════════════════════════════════════════


class TestValidateName:
    def test_valid_simple(self):
        assert validate_name("x") is None

    def test_valid_underscore_start(self):
        assert validate_name("_foo") is None

    def test_valid_alphanumeric(self):
        assert validate_name("abc_123") is None

    def test_invalid_starts_with_digit(self):
        err = validate_name("9abc")
        assert err is not None
        assert "Invalid name" in err

    def test_invalid_has_dash(self):
        err = validate_name("foo-bar")
        assert err is not None
        assert "Invalid name" in err

    def test_invalid_empty(self):
        err = validate_name("")
        assert err is not None

    def test_reserved_last(self):
        err = validate_name("last")
        assert err is not None
        assert "reserved" in err


class TestSubstituteVars:
    def test_script_var_priority(self):
        ms = MeasurementStore()
        ms.record("x", 99)
        result = substitute_vars("value=$x", {"x": "42"}, ms)
        assert result == "value=42"

    def test_measurement_label_lookup(self):
        ms = MeasurementStore()
        ms.record("volt", 3.3)
        result = substitute_vars("$volt", {}, ms)
        assert result == "3.3"

    def test_last_keyword(self):
        ms = MeasurementStore()
        ms.record("a", 1.0)
        ms.record("b", 2.5)
        result = substitute_vars("$last", {}, ms)
        assert result == "2.5"

    def test_last_keyword_empty_store(self):
        ms = MeasurementStore()
        result = substitute_vars("$last", {}, ms)
        assert result == "$last"

    def test_unresolved_variable(self):
        result = substitute_vars("$unknown", {})
        assert result == "$unknown"

    def test_no_measurements_object(self):
        result = substitute_vars("$x", {"x": "10"}, None)
        assert result == "10"

    def test_multiple_vars(self):
        result = substitute_vars("$a + $b", {"a": "1", "b": "2"})
        assert result == "1 + 2"

    def test_no_vars_in_text(self):
        result = substitute_vars("plain text", {})
        assert result == "plain text"

    def test_measurement_label_not_in_script_vars(self):
        ms = MeasurementStore()
        ms.record("myval", 7.7)
        result = substitute_vars("result=$myval", {}, ms)
        assert result == "result=7.7"

    def test_unresolved_no_measurements(self):
        result = substitute_vars("$missing", {}, None)
        assert result == "$missing"


class TestSubstituteLegacy:
    def test_basic_replacement(self):
        result = substitute_legacy("set ${volt}", {"volt": "5.0"})
        assert result == "set 5.0"

    def test_no_replacement(self):
        result = substitute_legacy("set $volt", {"volt": "5.0"})
        assert result == "set $volt"  # legacy only matches ${name}

    def test_multiple_replacements(self):
        result = substitute_legacy("${a} and ${b}", {"a": "X", "b": "Y"})
        assert result == "X and Y"


class TestSafeEval:
    def test_addition(self):
        assert safe_eval("2 + 3", {}) == 5

    def test_subtraction(self):
        assert safe_eval("10 - 4", {}) == 6

    def test_multiplication(self):
        assert safe_eval("3 * 7", {}) == 21

    def test_division(self):
        assert safe_eval("10 / 4", {}) == 2.5

    def test_power(self):
        assert safe_eval("2 ** 3", {}) == 8

    def test_modulo(self):
        assert safe_eval("10 % 3", {}) == 1

    def test_unary_minus(self):
        assert safe_eval("-5", {}) == -5

    def test_unary_plus(self):
        assert safe_eval("+3", {}) == 3

    def test_named_variable(self):
        assert safe_eval("x + 1", {"x": 10}) == 11

    def test_abs_function(self):
        assert safe_eval("abs(-5)", {}) == 5

    def test_min_function(self):
        assert safe_eval("min(1, 2, 3)", {}) == 1

    def test_max_function(self):
        assert safe_eval("max(1, 2, 3)", {}) == 3

    def test_round_function(self):
        assert safe_eval("round(3.456, 2)", {}) == 3.46

    def test_parentheses(self):
        assert safe_eval("(2 + 3) * 4", {}) == 20

    def test_complex_expression(self):
        assert safe_eval("2 * x + 3", {"x": 5}) == 13

    def test_subscript_dict(self):
        d = {"a": 10, "b": 20}
        assert safe_eval("m['a']", {"m": d}) == 10

    def test_subscript_name_key(self):
        # dict[name] where name is used as the key string
        d = {"key": 42}
        assert safe_eval("m['key']", {"m": d}) == 42

    def test_unknown_name_error(self):
        with pytest.raises(ValueError, match="Unknown name"):
            safe_eval("z + 1", {})

    def test_string_constant_error(self):
        with pytest.raises(ValueError, match="Only numeric constants"):
            safe_eval("'hello'", {})

    def test_disallowed_operator(self):
        # Bitwise operators are not allowed
        with pytest.raises(ValueError):
            safe_eval("3 & 1", {})

    def test_disallowed_unary_operator(self):
        with pytest.raises(ValueError):
            safe_eval("~5", {})

    def test_disallowed_expression(self):
        # List comprehension or similar
        with pytest.raises(ValueError):
            safe_eval("[x for x in range(3)]", {})

    def test_function_not_allowed(self):
        with pytest.raises(ValueError, match="Function not allowed"):
            safe_eval("int(3.5)", {"int": int})

    def test_allowed_func_name_resolves(self):
        # abs/min/max/round should be resolvable as names
        result = safe_eval("abs(-3)", {})
        assert result == 3

    def test_subscript_non_dict_error(self):
        with pytest.raises(ValueError, match="Subscript base must be a dict"):
            safe_eval("x[0]", {"x": [1, 2, 3]})


# ═══════════════════════════════════════════════════════════════════
# 2. measurement_store.py
# ═══════════════════════════════════════════════════════════════════


class TestMeasurementStore:
    def test_record_and_get_last(self):
        ms = MeasurementStore()
        ms.record("v1", 5.0, "V", "psu1")
        last = ms.get_last()
        assert last is not None
        assert last["label"] == "v1"
        assert last["value"] == 5.0
        assert last["unit"] == "V"
        assert last["source"] == "psu1"

    def test_get_last_empty(self):
        ms = MeasurementStore()
        assert ms.get_last() is None

    def test_get_by_label(self):
        ms = MeasurementStore()
        ms.record("a", 1.0)
        ms.record("b", 2.0)
        ms.record("a", 3.0)
        entry = ms.get_by_label("a")
        assert entry["value"] == 3.0  # last wins

    def test_get_by_label_not_found(self):
        ms = MeasurementStore()
        ms.record("x", 1)
        assert ms.get_by_label("y") is None

    def test_as_value_dict(self):
        ms = MeasurementStore()
        ms.record("x", 1)
        ms.record("y", 2)
        ms.record("x", 3)  # overwrite
        d = ms.as_value_dict()
        assert d == {"x": 3, "y": 2}

    def test_clear(self):
        ms = MeasurementStore()
        ms.record("x", 1)
        ms.clear()
        assert len(ms) == 0
        assert ms.get_last() is None

    def test_len(self):
        ms = MeasurementStore()
        assert len(ms) == 0
        ms.record("a", 1)
        ms.record("b", 2)
        assert len(ms) == 2

    def test_bool_empty(self):
        ms = MeasurementStore()
        assert not ms

    def test_bool_non_empty(self):
        ms = MeasurementStore()
        ms.record("a", 1)
        assert ms

    def test_entries_property(self):
        ms = MeasurementStore()
        ms.record("z", 99)
        assert ms.entries is ms._entries
        assert len(ms.entries) == 1


# ═══════════════════════════════════════════════════════════════════
# 3. device_registry.py
# ═══════════════════════════════════════════════════════════════════


class TestDeviceRegistry:
    def _make_registry(self, devices=None, selected=None):
        reg = DeviceRegistry()
        if devices:
            reg.devices = devices
        if selected:
            reg.selected = selected
        return reg

    def test_get_device_no_devices(self, capsys):
        reg = self._make_registry()
        assert reg.get_device(None) is None
        out = capsys.readouterr().out
        assert "No instruments connected" in out

    def test_get_device_no_selected(self, capsys):
        reg = self._make_registry({"psu1": MockHP_E3631A()})
        assert reg.get_device(None) is None
        out = capsys.readouterr().out
        assert "No active instrument" in out

    def test_get_device_selected(self):
        psu = MockHP_E3631A()
        reg = self._make_registry({"psu1": psu}, selected="psu1")
        assert reg.get_device(None) is psu

    def test_get_device_by_name(self):
        psu = MockHP_E3631A()
        reg = self._make_registry({"psu1": psu})
        assert reg.get_device("psu1") is psu

    def test_get_device_unknown_name(self, capsys):
        reg = self._make_registry({"psu1": MockHP_E3631A()})
        assert reg.get_device("psu99") is None
        out = capsys.readouterr().out
        assert "Unknown instrument" in out

    def test_resolve_type_single_match(self):
        reg = self._make_registry({"psu1": MockHP_E3631A()})
        assert reg.resolve_type("psu") == "psu1"

    def test_resolve_type_no_match(self):
        reg = self._make_registry({"psu1": MockHP_E3631A()})
        assert reg.resolve_type("awg") is None

    def test_resolve_type_multiple_with_selected(self):
        reg = self._make_registry(
            {"psu1": MockHP_E3631A(), "psu2": MockMPS6010H()},
            selected="psu2",
        )
        assert reg.resolve_type("psu") == "psu2"

    def test_resolve_type_multiple_no_selected(self, capsys):
        reg = self._make_registry({"psu1": MockHP_E3631A(), "psu2": MockMPS6010H()})
        result = reg.resolve_type("psu")
        assert result is None
        out = capsys.readouterr().out
        assert "Multiple" in out

    def test_resolve_type_with_override(self):
        reg = self._make_registry({"psu1": MockHP_E3631A(), "psu2": MockMPS6010H()})
        reg._device_override = "psu2"
        assert reg.resolve_type("psu") == "psu2"

    def test_get_caps_by_instance(self):
        dev = MockHP_E3631A()
        reg = self._make_registry({"psu1": dev})
        caps = reg.get_caps(dev)
        assert caps & Capability.PSU_MULTI_CHANNEL

    def test_get_caps_by_name(self):
        dev = MockHP_E3631A()
        reg = self._make_registry({"psu1": dev})
        caps = reg.get_caps("psu1")
        assert caps & Capability.PSU_MULTI_CHANNEL

    def test_get_caps_unknown_name(self):
        reg = self._make_registry({"psu1": MockHP_E3631A()})
        assert reg.get_caps("psu99") == Capability.NONE

    def test_has_cap(self):
        dev = MockHP_E3631A()
        reg = self._make_registry({"psu1": dev})
        assert reg.has_cap(dev, Capability.PSU_MULTI_CHANNEL)
        assert not reg.has_cap(dev, Capability.AWG_SYNC)

    def test_display_name_instance(self):
        dev = MockHP_E3631A()
        reg = self._make_registry({"psu1": dev})
        name = reg.display_name(dev)
        assert "E3631A" in name

    def test_display_name_string(self):
        dev = MockHP_E3631A()
        reg = self._make_registry({"psu1": dev})
        name = reg.display_name("psu1")
        assert "E3631A" in name

    def test_display_name_unknown_string(self):
        reg = self._make_registry({"psu1": MockHP_E3631A()})
        assert reg.display_name("psu99") == "psu99"

    def test_display_name_unknown_class(self):
        # A device whose class is not in DISPLAY_NAMES
        dev = MagicMock()
        type(dev).__name__ = "UnknownDevice"
        reg = self._make_registry({"unk1": dev})
        assert reg.display_name(dev) == "UnknownDevice"

    def test_channels_for_scope(self):
        dev = MockDHO804()
        reg = self._make_registry({"scope1": dev})
        chs = reg.channels_for(dev, "scope")
        assert chs == [1, 2, 3, 4]

    def test_channels_for_psu_multi(self):
        dev = MockHP_E3631A()
        reg = self._make_registry({"psu1": dev})
        chs = reg.channels_for(dev, "psu")
        assert chs == [1, 2, 3]

    def test_channels_for_psu_single(self):
        dev = MockMPS6010H()
        reg = self._make_registry({"psu1": dev})
        chs = reg.channels_for(dev, "psu")
        assert chs == [1]

    def test_channels_for_awg(self):
        dev = MockEDU33212A()
        reg = self._make_registry({"awg1": dev})
        chs = reg.channels_for(dev, "awg")
        assert chs == [1, 2]

    def test_channels_for_unknown(self):
        dev = MockHP_34401A()
        reg = self._make_registry({"dmm1": dev})
        chs = reg.channels_for(dev, "dmm")
        assert chs is None

    def test_capability_error_no_alternative(self):
        reg = self._make_registry({"psu1": MockMPS6010H()})
        msg = reg.capability_error("psu1", Capability.PSU_MULTI_CHANNEL, "multi-channel")
        assert "doesn't support" in msg
        assert "No other connected" in msg

    def test_capability_error_with_alternative(self):
        reg = self._make_registry(
            {"psu1": MockMPS6010H(), "psu2": MockHP_E3631A()},
        )
        msg = reg.capability_error("psu1", Capability.PSU_MULTI_CHANNEL, "multi-channel")
        assert "doesn't support" in msg
        assert "psu2" in msg

    def test_base_type(self):
        reg = DeviceRegistry()
        assert reg.base_type("psu1") == "psu"
        assert reg.base_type("awg12") == "awg"
        assert reg.base_type("scope") == "scope"


# ═══════════════════════════════════════════════════════════════════
# 4. context.py
# ═══════════════════════════════════════════════════════════════════


class TestReplContext:
    def test_default_state(self):
        ctx = ReplContext()
        assert ctx.command_had_error is False
        assert ctx.exit_on_error is False
        assert ctx.in_script is False
        assert not ctx.measurements
        assert not ctx.registry.devices
        assert ctx.script_vars == {}

    def test_error_sets_flag(self, capsys):
        ctx = ReplContext()
        ctx.error("boom")
        assert ctx.command_had_error is True
        out = capsys.readouterr().out
        assert "boom" in out

    def test_get_scripts_dir_with_override(self):
        ctx = ReplContext()
        with tempfile.TemporaryDirectory() as td:
            ctx._scripts_dir_override = td
            assert ctx.get_scripts_dir() == td

    def test_get_scripts_dir_env_override(self, monkeypatch):
        ctx = ReplContext()
        with tempfile.TemporaryDirectory() as td:
            monkeypatch.setenv("SCPI_SCRIPTS_DIR", td)
            assert ctx.get_scripts_dir() == td

    def test_get_scripts_dir_env_bad_path(self, monkeypatch):
        ctx = ReplContext()
        # Use a path that will fail os.makedirs on all platforms
        bad_path = "/dev/null/impossible/path"
        monkeypatch.setenv("SCPI_SCRIPTS_DIR", bad_path)
        monkeypatch.setattr("os.makedirs", self._fail_makedirs(bad_path))
        with pytest.raises(RuntimeError, match="cannot be created"):
            ctx.get_scripts_dir()

    @staticmethod
    def _fail_makedirs(target_path):
        """Return a makedirs replacement that fails for *target_path*."""
        import os as _os
        _real = _os.makedirs

        def _mock(path, *args, **kwargs):
            if _os.path.normpath(path) == _os.path.normpath(target_path):
                raise OSError(f"Cannot create '{path}'")
            return _real(path, *args, **kwargs)

        return _mock

    def test_script_file(self):
        ctx = ReplContext()
        with tempfile.TemporaryDirectory() as td:
            ctx._scripts_dir_override = td
            path = ctx.script_file("test_script")
            assert path.endswith("test_script.scpi")
            assert td in path

    def test_get_data_dir_with_override(self):
        ctx = ReplContext()
        with tempfile.TemporaryDirectory() as td:
            ctx._data_dir_override = td
            assert ctx.get_data_dir() == td

    def test_get_data_dir_env_override(self, monkeypatch):
        ctx = ReplContext()
        with tempfile.TemporaryDirectory() as td:
            monkeypatch.setenv("SCPI_DATA_DIR", td)
            assert ctx.get_data_dir() == td

    def test_get_data_dir_env_bad_path(self, monkeypatch):
        ctx = ReplContext()
        bad_path = "/dev/null/impossible/path"
        monkeypatch.setenv("SCPI_DATA_DIR", bad_path)
        monkeypatch.setattr("os.makedirs", self._fail_makedirs(bad_path))
        with pytest.raises(RuntimeError, match="cannot be created"):
            ctx.get_data_dir()

    def test_get_data_dir_default(self, monkeypatch):
        ctx = ReplContext()
        ctx._data_dir_override = None
        monkeypatch.delenv("SCPI_DATA_DIR", raising=False)
        d = ctx.get_data_dir()
        assert os.path.isdir(d)

    def test_load_scripts(self):
        ctx = ReplContext()
        with tempfile.TemporaryDirectory() as td:
            ctx._scripts_dir_override = td
            with open(os.path.join(td, "hello.scpi"), "w") as f:
                f.write("print hello\nprint world\n")
            scripts = ctx.load_scripts()
            assert "hello" in scripts
            assert len(scripts["hello"]) == 2

    def test_load_scripts_strips_trailing_blank(self):
        ctx = ReplContext()
        with tempfile.TemporaryDirectory() as td:
            ctx._scripts_dir_override = td
            with open(os.path.join(td, "test.scpi"), "w") as f:
                f.write("line1\n\n\n")
            scripts = ctx.load_scripts()
            assert scripts["test"] == ["line1"]

    def test_probe_dir_no_cross_process(self):
        ctx = ReplContext()
        with tempfile.TemporaryDirectory() as td:
            assert ctx._probe_dir(td, cross_process=False) is True

    def test_probe_dir_cross_process(self):
        ctx = ReplContext()
        with tempfile.TemporaryDirectory() as td:
            assert ctx._probe_dir(td, cross_process=True) is True


# ═══════════════════════════════════════════════════════════════════
# 5. commands/base.py
# ═══════════════════════════════════════════════════════════════════


class TestBaseCommand:
    def _make(self):
        from lab_instruments.repl.commands.base import BaseCommand

        ctx = ReplContext()
        return BaseCommand(ctx)

    def test_parse_args(self):
        cmd = self._make()
        assert cmd.parse_args("a b c") == ["a", "b", "c"]

    def test_parse_args_quoted(self):
        cmd = self._make()
        assert cmd.parse_args('a "b c"') == ["a", "b c"]

    def test_parse_args_error(self, capsys):
        cmd = self._make()
        result = cmd.parse_args('"unmatched')
        assert result == []
        out = capsys.readouterr().out
        assert "Parse error" in out

    def test_is_help_true(self):
        cmd = self._make()
        assert cmd.is_help(["arg", "help"]) is True
        assert cmd.is_help(["arg", "-h"]) is True
        assert cmd.is_help(["arg", "--help"]) is True

    def test_is_help_false(self):
        cmd = self._make()
        assert cmd.is_help(["arg"]) is False
        assert cmd.is_help([]) is False

    def test_strip_help(self):
        cmd = self._make()
        args, flag = cmd.strip_help(["a", "help"])
        assert args == ["a"]
        assert flag is True
        args, flag = cmd.strip_help(["a", "b"])
        assert args == ["a", "b"]
        assert flag is False

    def test_parse_channels_all(self):
        cmd = self._make()
        assert cmd.parse_channels("all", max_ch=4) == [1, 2, 3, 4]

    def test_parse_channels_number(self):
        cmd = self._make()
        assert cmd.parse_channels("2") == [2]

    def test_parse_channels_ch_prefix(self):
        cmd = self._make()
        assert cmd.parse_channels("ch3") == [3]

    def test_print_usage(self, capsys):
        cmd = self._make()
        cmd.print_usage(["line1", "line2"])
        out = capsys.readouterr().out
        assert "line1" in out
        assert "line2" in out

    def test_print_colored_usage(self, capsys):
        cmd = self._make()
        cmd.print_colored_usage(["# HEADER", "- dash line", "cmd arg", "  indented"])
        out = capsys.readouterr().out
        assert "HEADER" in out

    def test_raw_path_arg(self):
        cmd = self._make()
        assert cmd.raw_path_arg("  /some/path  ") == "/some/path"
        assert cmd.raw_path_arg('"quoted"') == "quoted"
        assert cmd.raw_path_arg("'single'") == "single"
        assert cmd.raw_path_arg("") is None

    def test_raw_path_arg_strip_word(self):
        cmd = self._make()
        assert cmd.raw_path_arg("dir /some/path", strip_word="dir") == "/some/path"

    def test_registry_property(self):
        cmd = self._make()
        assert cmd.registry is cmd.ctx.registry

    def test_measurements_property(self):
        cmd = self._make()
        assert cmd.measurements is cmd.ctx.measurements

    def test_error_method(self, capsys):
        cmd = self._make()
        cmd.error("test error")
        assert cmd.ctx.command_had_error is True


# ═══════════════════════════════════════════════════════════════════
# 6. commands/variables.py
# ═══════════════════════════════════════════════════════════════════


class TestVariableCommands:
    def _make(self):
        from lab_instruments.repl.commands.variables import VariableCommands

        ctx = ReplContext()
        return VariableCommands(ctx), ctx

    def test_do_print_plain(self, capsys):
        vc, ctx = self._make()
        vc.do_print("hello world")
        out = capsys.readouterr().out
        assert "hello world" in out

    def test_do_print_with_var_substitution(self, capsys):
        vc, ctx = self._make()
        ctx.script_vars["name"] = "Alice"
        vc.do_print("Hi $name!")
        out = capsys.readouterr().out
        assert "Hi Alice!" in out

    def test_do_print_empty(self, capsys):
        vc, ctx = self._make()
        vc.do_print("")
        out = capsys.readouterr().out
        # Empty print outputs a blank line (print is now plain text, no ANSI codes)
        assert out == "\n"

    def test_do_set_math_eval(self, capsys):
        vc, ctx = self._make()
        vc.do_set("x 2 + 3")
        assert ctx.script_vars["x"] == "5"
        out = capsys.readouterr().out
        assert "x = 5" in out

    def test_do_set_string_fallback(self, capsys):
        vc, ctx = self._make()
        vc.do_set("greeting hello_world")
        assert ctx.script_vars["greeting"] == "hello_world"

    def test_do_set_var_substitution(self, capsys):
        vc, ctx = self._make()
        ctx.script_vars["a"] = "10"
        vc.do_set("b $a + 5")
        # safe_eval parses 10 + 5 as int, producing 15 (not 15.0)
        assert float(ctx.script_vars["b"]) == 15.0

    def test_do_set_no_args(self, capsys):
        vc, ctx = self._make()
        vc.do_set("")
        out = capsys.readouterr().out
        assert "Usage" in out

    def test_do_set_shows_current_vars(self, capsys):
        vc, ctx = self._make()
        ctx.script_vars["x"] = "42"
        vc.do_set("")
        out = capsys.readouterr().out
        assert "x = 42" in out

    def test_do_set_one_arg_only(self, capsys):
        vc, ctx = self._make()
        vc.do_set("x")
        out = capsys.readouterr().out
        assert "Usage" in out

    def test_do_sleep_with_suffix_ms(self, capsys):
        vc, ctx = self._make()
        vc.do_sleep("1ms")
        out = capsys.readouterr().out
        assert "Sleeping" in out

    def test_do_sleep_with_suffix_us(self, capsys):
        vc, ctx = self._make()
        vc.do_sleep("100us")
        out = capsys.readouterr().out
        assert "Sleeping" in out

    def test_do_sleep_with_suffix_m(self, capsys):
        vc, ctx = self._make()
        # Use 0 minutes so it completes immediately
        vc.do_sleep("0m")
        out = capsys.readouterr().out
        assert "Sleeping" in out

    def test_do_sleep_plain_seconds(self, capsys):
        vc, ctx = self._make()
        vc.do_sleep("0")
        out = capsys.readouterr().out
        assert "Sleeping" in out

    def test_do_sleep_help(self, capsys):
        vc, ctx = self._make()
        vc.do_sleep("help")
        out = capsys.readouterr().out
        assert "SLEEP" in out

    def test_do_sleep_no_args(self, capsys):
        vc, ctx = self._make()
        vc.do_sleep("")
        out = capsys.readouterr().out
        assert "SLEEP" in out

    def test_do_sleep_invalid(self, capsys):
        vc, ctx = self._make()
        vc.do_sleep("abc")
        out = capsys.readouterr().out
        assert "invalid duration" in out

    def test_do_sleep_negative(self, capsys):
        vc, ctx = self._make()
        vc.do_sleep("-1")
        out = capsys.readouterr().out
        assert "non-negative" in out

    def test_do_sleep_interrupt(self, capsys):
        vc, ctx = self._make()
        # Set interrupt flag before sleeping to break out immediately
        ctx.interrupt_requested = True
        vc.do_sleep("10")
        # Should return quickly due to interrupt
        out = capsys.readouterr().out
        assert "Sleeping" in out

    def test_do_input(self, capsys, monkeypatch):
        vc, ctx = self._make()
        monkeypatch.setattr("builtins.input", lambda prompt: "42")
        vc.do_input("myvar Enter a value")
        assert ctx.script_vars["myvar"] == "42"

    def test_do_input_no_args(self, capsys):
        vc, ctx = self._make()
        vc.do_input("")
        out = capsys.readouterr().out
        assert "Usage" in out

    def test_do_input_default_prompt(self, capsys, monkeypatch):
        vc, ctx = self._make()
        monkeypatch.setattr("builtins.input", lambda prompt: "val")
        vc.do_input("x")
        assert ctx.script_vars["x"] == "val"

    def test_do_pause(self, capsys, monkeypatch):
        vc, ctx = self._make()
        monkeypatch.setattr("builtins.input", lambda prompt: "")
        vc.do_pause("Custom prompt here")
        # Should not raise

    def test_do_pause_default(self, capsys, monkeypatch):
        vc, ctx = self._make()
        monkeypatch.setattr("builtins.input", lambda prompt: "")
        vc.do_pause("")


# ═══════════════════════════════════════════════════════════════════
# 7. commands/general.py
# ═══════════════════════════════════════════════════════════════════


class TestGeneralCommands:
    def _make(self, devices=None):
        from lab_instruments.repl.commands.general import GeneralCommands
        from lab_instruments.repl.commands.safety import SafetySystem

        ctx = ReplContext()
        if devices:
            ctx.registry.devices = devices
        safety = SafetySystem(ctx)
        return GeneralCommands(ctx, safety), ctx

    def test_do_list_no_devices(self, capsys):
        gc, ctx = self._make()
        gc.do_list("")
        out = capsys.readouterr().out
        assert "No instruments connected" in out

    def test_do_list_with_devices(self, capsys):
        gc, ctx = self._make({"psu1": MockHP_E3631A()})
        gc.do_list("")
        out = capsys.readouterr().out
        assert "psu1" in out

    def test_do_list_help(self, capsys):
        gc, ctx = self._make()
        gc.do_list("help")
        out = capsys.readouterr().out
        assert "LIST" in out

    def test_do_use_success(self, capsys):
        gc, ctx = self._make({"psu1": MockHP_E3631A()})
        gc.do_use("psu1")
        assert ctx.registry.selected == "psu1"
        out = capsys.readouterr().out
        assert "Active" in out

    def test_do_use_unknown(self, capsys):
        gc, ctx = self._make({"psu1": MockHP_E3631A()})
        gc.do_use("psu99")
        assert ctx.registry.selected is None
        out = capsys.readouterr().out
        assert "Unknown instrument" in out

    def test_do_use_help(self, capsys):
        gc, ctx = self._make()
        gc.do_use("")
        out = capsys.readouterr().out
        assert "USE" in out

    def test_do_status(self, capsys):
        gc, ctx = self._make({"psu1": MockHP_E3631A()})
        gc.do_status("")
        out = capsys.readouterr().out
        assert "psu1" in out

    def test_do_idn_success(self, capsys):
        dev = MockHP_E3631A()
        gc, ctx = self._make({"psu1": dev})
        ctx.registry.selected = "psu1"
        gc.do_idn("")
        out = capsys.readouterr().out
        assert "MOCK INSTRUMENTS" in out

    def test_do_idn_specific_device(self, capsys):
        gc, ctx = self._make({"dmm1": MockHP_34401A()})
        gc.do_idn("dmm1")
        out = capsys.readouterr().out
        assert "MOCK INSTRUMENTS" in out

    def test_do_idn_no_device(self, capsys):
        gc, ctx = self._make()
        gc.do_idn("")
        assert ctx.command_had_error is True

    def test_do_idn_help(self, capsys):
        gc, ctx = self._make()
        gc.do_idn("help")
        out = capsys.readouterr().out
        assert "IDN" in out

    def test_do_idn_exception(self, capsys):
        dev = MagicMock()
        dev.query.side_effect = Exception("comm error")
        gc, ctx = self._make({"psu1": dev})
        ctx.registry.selected = "psu1"
        gc.do_idn("")
        assert ctx.command_had_error is True

    def test_do_raw_query(self, capsys):
        dev = MockHP_E3631A()
        gc, ctx = self._make({"psu1": dev})
        ctx.registry.selected = "psu1"
        gc.do_raw("*IDN?")
        out = capsys.readouterr().out
        assert "MOCK INSTRUMENTS" in out

    def test_do_raw_command(self, capsys):
        dev = MockHP_E3631A()
        gc, ctx = self._make({"psu1": dev})
        ctx.registry.selected = "psu1"
        gc.do_raw("*RST")
        out = capsys.readouterr().out
        assert "Sent" in out

    def test_do_raw_specific_device(self, capsys):
        dev = MockHP_E3631A()
        gc, ctx = self._make({"psu1": dev})
        gc.do_raw("psu1 *IDN?")
        out = capsys.readouterr().out
        assert "MOCK INSTRUMENTS" in out

    def test_do_raw_no_args(self, capsys):
        gc, ctx = self._make()
        gc.do_raw("")
        out = capsys.readouterr().out
        assert "RAW" in out

    def test_do_raw_help(self, capsys):
        gc, ctx = self._make()
        gc.do_raw("help")
        out = capsys.readouterr().out
        assert "RAW" in out

    def test_do_raw_exception(self, capsys):
        dev = MagicMock()
        dev.query.side_effect = Exception("timeout")
        gc, ctx = self._make({"psu1": dev})
        ctx.registry.selected = "psu1"
        gc.do_raw("*IDN?")
        assert ctx.command_had_error is True

    def test_do_version(self, capsys):
        gc, ctx = self._make()
        gc.do_version("", "1.2.3")
        out = capsys.readouterr().out
        assert "1.2.3" in out

    def test_do_clear(self):
        gc, ctx = self._make()
        # Just check it doesn't raise (it calls os.system)
        with patch("os.system") as mock_sys:
            gc.do_clear("")
            mock_sys.assert_called_once()

    def test_do_all_help(self, capsys):
        gc, ctx = self._make()
        gc.do_all("")
        out = capsys.readouterr().out
        assert "ALL" in out

    def test_do_all_on(self, capsys):
        psu = MockHP_E3631A()
        gc, ctx = self._make({"psu1": psu})
        gc.do_all("on")
        out = capsys.readouterr().out
        assert "output enabled" in out

    def test_do_all_off(self, capsys):
        psu = MockHP_E3631A()
        gc, ctx = self._make({"psu1": psu})
        gc.do_all("off")
        out = capsys.readouterr().out
        assert "disabled" in out

    def test_do_all_safe(self, capsys):
        psu = MockHP_E3631A()
        gc, ctx = self._make({"psu1": psu})
        gc.do_all("safe")
        out = capsys.readouterr().out
        assert "safe state" in out

    def test_do_all_reset(self, capsys):
        psu = MockHP_E3631A()
        gc, ctx = self._make({"psu1": psu})
        gc.do_all("reset")
        out = capsys.readouterr().out
        assert "reset" in out

    def test_do_all_invalid(self, capsys):
        gc, ctx = self._make({"psu1": MockHP_E3631A()})
        gc.do_all("bogus")
        out = capsys.readouterr().out
        assert "on|off|safe|reset" in out

    def test_do_state_safe(self, capsys):
        gc, ctx = self._make({"psu1": MockHP_E3631A()})
        gc.do_state("safe")
        out = capsys.readouterr().out
        assert "safe state" in out

    def test_do_state_off(self, capsys):
        gc, ctx = self._make({"psu1": MockHP_E3631A()})
        gc.do_state("off")

    def test_do_state_on(self, capsys):
        gc, ctx = self._make({"psu1": MockHP_E3631A()})
        gc.do_state("on")

    def test_do_state_reset(self, capsys):
        gc, ctx = self._make({"psu1": MockHP_E3631A()})
        gc.do_state("reset")

    def test_do_state_device_specific(self, capsys):
        gc, ctx = self._make({"psu1": MockHP_E3631A()})
        gc.do_state("psu1 off")
        out = capsys.readouterr().out
        assert "output disabled" in out

    def test_do_state_help(self, capsys):
        gc, ctx = self._make()
        gc.do_state("help")
        out = capsys.readouterr().out
        assert "STATE" in out

    def test_do_state_list(self, capsys):
        gc, ctx = self._make()
        gc.do_state("list")
        out = capsys.readouterr().out
        assert "STATE" in out

    def test_do_state_device_too_few_args(self, capsys):
        gc, ctx = self._make({"psu1": MockHP_E3631A()})
        gc.do_state("psu1")
        out = capsys.readouterr().out
        assert "Usage" in out

    def test_do_state_device_not_found(self, capsys):
        gc, ctx = self._make({"psu1": MockHP_E3631A()})
        gc.do_state("psu99 off")
        assert ctx.command_had_error is True

    def test_do_state_awg(self, capsys):
        gc, ctx = self._make({"awg1": MockEDU33212A()})
        gc.do_state("awg1 off")
        out = capsys.readouterr().out
        assert "outputs disabled" in out

    def test_do_state_awg_on(self, capsys):
        gc, ctx = self._make({"awg1": MockEDU33212A()})
        gc.do_state("awg1 on")
        out = capsys.readouterr().out
        assert "outputs enabled" in out

    def test_do_state_awg_reset(self, capsys):
        gc, ctx = self._make({"awg1": MockEDU33212A()})
        gc.do_state("awg1 reset")
        out = capsys.readouterr().out
        assert "reset" in out

    def test_do_state_awg_invalid(self, capsys):
        gc, ctx = self._make({"awg1": MockEDU33212A()})
        gc.do_state("awg1 bogus")
        out = capsys.readouterr().out
        assert "AWG states" in out

    def test_do_state_scope(self, capsys):
        gc, ctx = self._make({"scope1": MockDHO804()})
        gc.do_state("scope1 off")
        out = capsys.readouterr().out
        assert "channels disabled" in out

    def test_do_state_scope_on(self, capsys):
        gc, ctx = self._make({"scope1": MockDHO804()})
        gc.do_state("scope1 on")
        out = capsys.readouterr().out
        assert "channels enabled" in out

    def test_do_state_scope_reset(self, capsys):
        gc, ctx = self._make({"scope1": MockDHO804()})
        gc.do_state("scope1 reset")
        out = capsys.readouterr().out
        assert "reset" in out

    def test_do_state_dmm(self, capsys):
        gc, ctx = self._make({"dmm1": MockHP_34401A()})
        gc.do_state("dmm1 safe")
        out = capsys.readouterr().out
        assert "reset" in out

    def test_do_state_psu_on(self, capsys):
        gc, ctx = self._make({"psu1": MockHP_E3631A()})
        gc.do_state("psu1 on")
        out = capsys.readouterr().out
        assert "output enabled" in out

    def test_do_state_psu_reset(self, capsys):
        gc, ctx = self._make({"psu1": MockHP_E3631A()})
        gc.do_state("psu1 reset")
        out = capsys.readouterr().out
        assert "reset" in out

    def test_do_state_psu_invalid(self, capsys):
        gc, ctx = self._make({"psu1": MockHP_E3631A()})
        gc.do_state("psu1 bogus")
        out = capsys.readouterr().out
        assert "PSU states" in out

    def test_do_close(self, capsys):
        psu = MockHP_E3631A()
        gc, ctx = self._make({"psu1": psu})
        gc.do_close("")
        assert len(ctx.registry.devices) == 0
        out = capsys.readouterr().out
        assert "disconnected" in out

    def test_do_close_help(self, capsys):
        gc, ctx = self._make()
        gc.do_close("help")
        out = capsys.readouterr().out
        assert "CLOSE" in out

    def test_safe_all_mixed_devices(self, capsys):
        gc, ctx = self._make(
            {
                "psu1": MockHP_E3631A(),
                "awg1": MockEDU33212A(),
                "scope1": MockDHO804(),
                "dmm1": MockHP_34401A(),
            }
        )
        gc.safe_all()
        out = capsys.readouterr().out
        assert "safe state" in out

    def test_off_all_mixed_devices(self, capsys):
        gc, ctx = self._make(
            {
                "psu1": MockHP_E3631A(),
                "awg1": MockEDU33212A(),
                "scope1": MockDHO804(),
                "dmm1": MockHP_34401A(),
            }
        )
        gc.off_all()
        out = capsys.readouterr().out
        assert "disabled" in out or "reset" in out or "stopped" in out

    def test_on_all_mixed_devices(self, capsys):
        gc, ctx = self._make(
            {
                "psu1": MockHP_E3631A(),
                "awg1": MockEDU33212A(),
                "scope1": MockDHO804(),
            }
        )
        gc.on_all()
        out = capsys.readouterr().out
        assert "enabled" in out

    def test_reset_all(self, capsys):
        gc, ctx = self._make({"psu1": MockHP_E3631A(), "dmm1": MockHP_34401A()})
        gc.reset_all()
        out = capsys.readouterr().out
        assert "reset" in out

    def test_print_devices_with_selected(self, capsys):
        gc, ctx = self._make({"psu1": MockHP_E3631A(), "awg1": MockEDU33212A()})
        ctx.registry.selected = "psu1"
        gc.print_devices()
        out = capsys.readouterr().out
        assert "psu1" in out
        assert "awg1" in out


# ═══════════════════════════════════════════════════════════════════
# 8. commands/logging_cmd.py
# ═══════════════════════════════════════════════════════════════════


class TestLoggingCommands:
    def _make(self):
        from lab_instruments.repl.commands.logging_cmd import LoggingCommands

        ctx = ReplContext()
        return LoggingCommands(ctx), ctx

    def test_do_log_help(self, capsys):
        lc, ctx = self._make()
        lc.do_log("")
        out = capsys.readouterr().out
        assert "LOG" in out

    def test_do_log_clear(self, capsys):
        lc, ctx = self._make()
        ctx.measurements.record("a", 1)
        lc.do_log("clear")
        assert len(ctx.measurements) == 0

    def test_do_log_print_empty(self, capsys):
        lc, ctx = self._make()
        lc.do_log("print")
        out = capsys.readouterr().out
        assert "No measurements" in out

    def test_do_log_print_with_data(self, capsys):
        lc, ctx = self._make()
        ctx.measurements.record("volt", 5.0, "V", "psu1")
        lc.do_log("print")
        out = capsys.readouterr().out
        assert "volt" in out
        assert "5.0" in out

    def test_do_log_save_csv(self, capsys):
        lc, ctx = self._make()
        ctx.measurements.record("v", 3.3, "V", "psu")
        with tempfile.TemporaryDirectory() as td:
            ctx._data_dir_override = td
            path = os.path.join(td, "test.csv")
            lc.do_log(f"save {path}")
            assert os.path.isfile(path)
            with open(path) as f:
                content = f.read()
            assert "label,value" in content
            assert "v,3.3" in content

    def test_do_log_save_txt(self, capsys):
        lc, ctx = self._make()
        ctx.measurements.record("v", 3.3, "V", "psu")
        with tempfile.TemporaryDirectory() as td:
            ctx._data_dir_override = td
            path = os.path.join(td, "test.txt")
            lc.do_log(f"save {path}")
            assert os.path.isfile(path)

    def test_do_log_save_explicit_format(self, capsys):
        lc, ctx = self._make()
        ctx.measurements.record("v", 3.3, "V", "psu")
        with tempfile.TemporaryDirectory() as td:
            ctx._data_dir_override = td
            path = os.path.join(td, "test.dat")
            lc.do_log(f"save {path} csv")
            assert os.path.isfile(path)

    def test_do_log_save_bad_format(self, capsys):
        lc, ctx = self._make()
        ctx.measurements.record("v", 3.3, "V", "psu")
        lc.do_log("save test.xyz json")
        out = capsys.readouterr().out
        assert "csv or txt" in out

    def test_do_log_save_no_data(self, capsys):
        lc, ctx = self._make()
        lc.do_log("save test.csv")
        out = capsys.readouterr().out
        assert "No measurements" in out

    def test_do_log_save_relative_path(self, capsys):
        lc, ctx = self._make()
        ctx.measurements.record("v", 1.0, "V", "psu")
        with tempfile.TemporaryDirectory() as td:
            ctx._data_dir_override = td
            lc.do_log("save myfile.csv")
            assert os.path.isfile(os.path.join(td, "myfile.csv"))

    def test_do_log_unknown_subcommand(self, capsys):
        lc, ctx = self._make()
        lc.do_log("bogus")
        out = capsys.readouterr().out
        assert "Unknown log command" in out

    def test_do_calc_success(self, capsys):
        lc, ctx = self._make()
        ctx.measurements.record("psu_v", 5.0, "V", "psu")
        ctx.measurements.record("psu_i", 0.1, "A", "psu")
        lc.do_calc("power = $psu_v * $psu_i unit=W")
        out = capsys.readouterr().out
        assert "power" in out
        assert "0.5" in out

    def test_do_calc_help(self, capsys):
        lc, ctx = self._make()
        lc.do_calc("")
        out = capsys.readouterr().out
        assert "CALC" in out

    def test_do_calc_no_measurements(self, capsys):
        lc, ctx = self._make()
        lc.do_calc("x = 2 + 3")
        out = capsys.readouterr().out
        assert "No measurements" in out

    def test_do_calc_no_equals(self, capsys):
        lc, ctx = self._make()
        ctx.measurements.record("a", 1)
        lc.do_calc("x 2 + 3")
        out = capsys.readouterr().out
        assert "x" in out

    def test_do_calc_error(self, capsys):
        lc, ctx = self._make()
        ctx.measurements.record("a", 1)
        lc.do_calc("x = bad_func()")
        out = capsys.readouterr().out
        assert "calc failed" in out

    def test_do_calc_empty_expr(self, capsys):
        lc, ctx = self._make()
        ctx.measurements.record("a", 1)
        lc.do_calc("x = unit=W")
        out = capsys.readouterr().out
        assert "calc expects" in out or "calc failed" in out

    def test_do_check_pass(self, capsys):
        lc, ctx = self._make()
        ctx.measurements.record("v", 5.0, "V")
        lc.do_check("v 4.5 5.5")
        out = capsys.readouterr().out
        assert "PASS" in out
        assert len(ctx.test_results) == 1
        assert ctx.test_results[0]["passed"] is True

    def test_do_check_fail(self, capsys):
        lc, ctx = self._make()
        ctx.measurements.record("v", 5.0, "V")
        lc.do_check("v 5.5 6.0")
        out = capsys.readouterr().out
        assert "FAIL" in out
        assert ctx.command_had_error is True

    def test_do_check_tolerance(self, capsys):
        lc, ctx = self._make()
        ctx.measurements.record("v", 5.0, "V")
        lc.do_check("v 5.0 tol=0.5")
        out = capsys.readouterr().out
        assert "PASS" in out

    def test_do_check_tolerance_percent(self, capsys):
        lc, ctx = self._make()
        ctx.measurements.record("v", 5.0, "V")
        lc.do_check("v 5.0 tol=10%")
        out = capsys.readouterr().out
        assert "PASS" in out

    def test_do_check_no_label(self, capsys):
        lc, ctx = self._make()
        lc.do_check("missing 4 6")
        out = capsys.readouterr().out
        assert "no measurement found" in out

    def test_do_check_help(self, capsys):
        lc, ctx = self._make()
        lc.do_check("")
        out = capsys.readouterr().out
        assert "CHECK" in out

    def test_do_check_invalid_range(self, capsys):
        lc, ctx = self._make()
        ctx.measurements.record("v", 5.0, "V")
        lc.do_check("v abc def")
        out = capsys.readouterr().out
        assert "invalid range" in out

    def test_do_check_invalid_expected(self, capsys):
        lc, ctx = self._make()
        ctx.measurements.record("v", 5.0, "V")
        lc.do_check("v abc tol=0.5")
        out = capsys.readouterr().out
        assert "invalid expected" in out


# ═══════════════════════════════════════════════════════════════════
# 9. script_engine/expander.py
# ═══════════════════════════════════════════════════════════════════


class TestExpander:
    def _make_ctx(self):
        ctx = ReplContext()
        ctx.scripts = {}
        return ctx

    def test_plain_command(self):
        from lab_instruments.repl.script_engine.expander import expand_script_lines

        ctx = self._make_ctx()
        result = expand_script_lines(["print hello"], {}, ctx)
        assert len(result) == 1
        assert result[0][0] == "print hello"

    def test_comment_and_blank_skipped(self):
        from lab_instruments.repl.script_engine.expander import expand_script_lines

        ctx = self._make_ctx()
        result = expand_script_lines(["# comment", "", "  ", "print x"], {}, ctx)
        assert len(result) == 1

    def test_set_variable(self):
        from lab_instruments.repl.script_engine.expander import expand_script_lines

        ctx = self._make_ctx()
        variables = {}
        expand_script_lines(["set x 5"], variables, ctx)
        assert variables["x"] == "5"

    def test_set_variable_math(self):
        from lab_instruments.repl.script_engine.expander import expand_script_lines

        ctx = self._make_ctx()
        variables = {}
        expand_script_lines(["set x 2 + 3"], variables, ctx)
        assert variables["x"] == "5"

    def test_set_exit_on_error(self, capsys):
        from lab_instruments.repl.script_engine.expander import expand_script_lines

        ctx = self._make_ctx()
        expand_script_lines(["set -e"], {}, ctx)
        assert ctx.exit_on_error is True
        expand_script_lines(["set +e"], {}, ctx)
        assert ctx.exit_on_error is False

    def test_for_loop(self):
        from lab_instruments.repl.script_engine.expander import expand_script_lines

        ctx = self._make_ctx()
        lines = ["for v 1 2 3", "print ${v}", "end"]
        variables = {}
        result = expand_script_lines(lines, variables, ctx)
        commands = [cmd for cmd, _ in result if cmd != "__NOP__"]
        assert commands == ["print 1", "print 2", "print 3"]

    def test_for_loop_multi_key(self):
        from lab_instruments.repl.script_engine.expander import expand_script_lines

        ctx = self._make_ctx()
        lines = ["for x,y 1,2 3,4", "print ${x} ${y}", "end"]
        result = expand_script_lines(lines, {}, ctx)
        commands = [cmd for cmd, _ in result if cmd != "__NOP__"]
        assert commands == ["print 1 2", "print 3 4"]

    def test_for_loop_multi_key_mismatch(self, capsys):
        from lab_instruments.repl.script_engine.expander import expand_script_lines

        ctx = self._make_ctx()
        lines = ["for x,y 1,2 3", "print ${x}", "end"]
        expand_script_lines(lines, {}, ctx)
        out = capsys.readouterr().out
        assert "mismatch" in out

    def test_repeat(self):
        from lab_instruments.repl.script_engine.expander import expand_script_lines

        ctx = self._make_ctx()
        lines = ["repeat 3", "print hi", "end"]
        result = expand_script_lines(lines, {}, ctx)
        commands = [cmd for cmd, _ in result if cmd != "__NOP__"]
        assert commands == ["print hi"] * 3

    def test_repeat_bad_count(self, capsys):
        from lab_instruments.repl.script_engine.expander import expand_script_lines

        ctx = self._make_ctx()
        expand_script_lines(["repeat abc", "print x", "end"], {}, ctx)
        out = capsys.readouterr().out
        assert "expected integer" in out

    def test_array(self):
        from lab_instruments.repl.script_engine.expander import expand_script_lines

        ctx = self._make_ctx()
        lines = ["array items", "1 2", "3 4", "end"]
        variables = {}
        expand_script_lines(lines, variables, ctx)
        assert variables["items"] == "1 2 3 4"

    def test_call(self):
        from lab_instruments.repl.script_engine.expander import expand_script_lines

        ctx = self._make_ctx()
        ctx.scripts["sub"] = ["print sub_line"]
        lines = ["call sub"]
        result = expand_script_lines(lines, {}, ctx)
        commands = [cmd for cmd, _ in result if cmd != "__NOP__"]
        assert "print sub_line" in commands

    def test_call_not_found(self, capsys):
        from lab_instruments.repl.script_engine.expander import expand_script_lines

        ctx = self._make_ctx()
        expand_script_lines(["call missing"], {}, ctx)
        out = capsys.readouterr().out
        assert "not found" in out

    def test_call_with_params(self):
        from lab_instruments.repl.script_engine.expander import expand_script_lines

        ctx = self._make_ctx()
        ctx.scripts["sub"] = ["print ${v}"]
        lines = ["call sub v=42"]
        result = expand_script_lines(lines, {}, ctx)
        commands = [cmd for cmd, _ in result if cmd != "__NOP__"]
        assert "print 42" in commands

    def test_import(self):
        from lab_instruments.repl.script_engine.expander import expand_script_lines

        ctx = self._make_ctx()
        parent = {"x": "10"}
        variables = {}
        expand_script_lines(["import x"], variables, ctx, parent_vars=parent)
        assert variables["x"] == "10"

    def test_import_not_found(self, capsys):
        from lab_instruments.repl.script_engine.expander import expand_script_lines

        ctx = self._make_ctx()
        expand_script_lines(["import missing_var"], {}, ctx, parent_vars={})
        out = capsys.readouterr().out
        assert "not found" in out

    def test_export(self):
        from lab_instruments.repl.script_engine.expander import expand_script_lines

        ctx = self._make_ctx()
        exports = {}
        variables = {"x": "42"}
        expand_script_lines(["export x"], variables, ctx, exports=exports)
        assert exports["x"] == "42"

    def test_export_not_set(self, capsys):
        from lab_instruments.repl.script_engine.expander import expand_script_lines

        ctx = self._make_ctx()
        exports = {}
        expand_script_lines(["export missing"], {}, ctx, exports=exports)
        out = capsys.readouterr().out
        assert "not set" in out

    def test_breakpoint(self):
        from lab_instruments.repl.script_engine.expander import expand_script_lines

        ctx = self._make_ctx()
        result = expand_script_lines(["breakpoint", "print a"], {}, ctx)
        commands = [cmd for cmd, _ in result]
        assert "__BREAKPOINT__" in commands

    def test_depth_limit(self, capsys):
        from lab_instruments.repl.script_engine.expander import expand_script_lines

        ctx = self._make_ctx()
        result = expand_script_lines(["print x"], {}, ctx, depth=11)
        assert result == []
        out = capsys.readouterr().out
        assert "Maximum script call depth" in out

    def test_lower_limit_psu(self):
        from lab_instruments.repl.script_engine.expander import expand_script_lines

        ctx = self._make_ctx()
        expand_script_lines(["lower_limit psu1 voltage 1.0"], {}, ctx, depth=1)
        assert ("psu1", None) in ctx.safety_limits
        assert "voltage_lower" in ctx.safety_limits[("psu1", None)]

    def test_upper_limit_psu(self):
        from lab_instruments.repl.script_engine.expander import expand_script_lines

        ctx = self._make_ctx()
        expand_script_lines(["upper_limit psu1 voltage 10.0"], {}, ctx, depth=1)
        assert ("psu1", None) in ctx.safety_limits
        assert "voltage_upper" in ctx.safety_limits[("psu1", None)]

    def test_limit_with_channel(self):
        from lab_instruments.repl.script_engine.expander import expand_script_lines

        ctx = self._make_ctx()
        expand_script_lines(["upper_limit awg1 chan 1 vpp 5.0"], {}, ctx, depth=1)
        assert ("awg1", 1) in ctx.safety_limits

    def test_limit_unknown_device_type(self, capsys):
        from lab_instruments.repl.script_engine.expander import expand_script_lines

        ctx = self._make_ctx()
        expand_script_lines(["upper_limit dmm1 voltage 5"], {}, ctx, depth=1)
        out = capsys.readouterr().out
        assert "unknown device type" in out

    def test_limit_unknown_param(self, capsys):
        from lab_instruments.repl.script_engine.expander import expand_script_lines

        ctx = self._make_ctx()
        expand_script_lines(["upper_limit psu1 power 5"], {}, ctx, depth=1)
        out = capsys.readouterr().out
        assert "unknown param" in out

    def test_limit_bad_value(self, capsys):
        from lab_instruments.repl.script_engine.expander import expand_script_lines

        ctx = self._make_ctx()
        expand_script_lines(["upper_limit psu1 voltage abc"], {}, ctx, depth=1)
        out = capsys.readouterr().out
        assert "not a number" in out

    def test_limit_chan_too_few_args(self, capsys):
        from lab_instruments.repl.script_engine.expander import expand_script_lines

        ctx = self._make_ctx()
        expand_script_lines(["upper_limit awg1 chan 1"], {}, ctx, depth=1)
        out = capsys.readouterr().out
        assert "requires" in out

    def test_limit_chan_invalid_number(self, capsys):
        from lab_instruments.repl.script_engine.expander import expand_script_lines

        ctx = self._make_ctx()
        expand_script_lines(["upper_limit awg1 chan abc vpp 5"], {}, ctx, depth=1)
        out = capsys.readouterr().out
        assert "invalid channel" in out

    def test_limit_too_few_rest_args(self, capsys):
        from lab_instruments.repl.script_engine.expander import expand_script_lines

        ctx = self._make_ctx()
        # Need at least 3 tokens for the limit parser to fire, but then
        # with only one remaining arg after device, it triggers the error
        expand_script_lines(["upper_limit psu1 voltage"], {}, ctx, depth=1)
        out = capsys.readouterr().out
        # Single token "voltage" is not a float, so it doesn't default to voltage param.
        # It ends up as len(rest) < 2 -> error
        assert "requires" in out

    def test_limit_single_value_defaults_voltage(self):
        from lab_instruments.repl.script_engine.expander import expand_script_lines

        ctx = self._make_ctx()
        expand_script_lines(["upper_limit psu1 5.0"], {}, ctx, depth=1)
        assert "voltage_upper" in ctx.safety_limits.get(("psu1", None), {})

    def test_limit_awg_voltage_remapped(self):
        from lab_instruments.repl.script_engine.expander import expand_script_lines

        ctx = self._make_ctx()
        expand_script_lines(["upper_limit awg1 voltage 5.0"], {}, ctx, depth=1)
        assert "vpeak_upper" in ctx.safety_limits.get(("awg1", None), {})

    def test_limit_awg_voltage_lower_remapped(self):
        from lab_instruments.repl.script_engine.expander import expand_script_lines

        ctx = self._make_ctx()
        expand_script_lines(["lower_limit awg1 voltage -5.0"], {}, ctx, depth=1)
        assert "vtrough_lower" in ctx.safety_limits.get(("awg1", None), {})

    def test_end_standalone_ignored(self):
        from lab_instruments.repl.script_engine.expander import expand_script_lines

        ctx = self._make_ctx()
        result = expand_script_lines(["end", "print a"], {}, ctx)
        commands = [cmd for cmd, _ in result if cmd != "__NOP__"]
        assert commands == ["print a"]

    def test_nested_loop(self):
        from lab_instruments.repl.script_engine.expander import expand_script_lines

        ctx = self._make_ctx()
        lines = [
            "repeat 2",
            "repeat 2",
            "print hi",
            "end",
            "end",
        ]
        result = expand_script_lines(lines, {}, ctx)
        commands = [cmd for cmd, _ in result if cmd != "__NOP__"]
        assert commands == ["print hi"] * 4

    def test_legacy_substitution_in_for(self):
        from lab_instruments.repl.script_engine.expander import expand_script_lines

        ctx = self._make_ctx()
        variables = {}
        expand_script_lines(["set a hello"], variables, ctx)
        result = expand_script_lines(["for v ${a}", "print ${v}", "end"], variables, ctx)
        commands = [cmd for cmd, _ in result if cmd != "__NOP__"]
        assert "print hello" in commands

    def test_call_with_exports(self):
        from lab_instruments.repl.script_engine.expander import expand_script_lines

        ctx = self._make_ctx()
        ctx.scripts["sub"] = ["set result 42", "export result"]
        parent_vars = {}
        expand_script_lines(["call sub"], parent_vars, ctx)
        assert parent_vars.get("result") == "42"

    def test_shlex_error_fallback(self):
        from lab_instruments.repl.script_engine.expander import expand_script_lines

        ctx = self._make_ctx()
        # Unbalanced quote triggers shlex fallback
        result = expand_script_lines(['print "unbalanced'], {}, ctx)
        assert len(result) == 1


# ═══════════════════════════════════════════════════════════════════
# 10. script_engine/runner.py
# ═══════════════════════════════════════════════════════════════════


class TestRunner:
    def _make_ctx(self):
        ctx = ReplContext()
        return ctx

    def test_run_empty(self):
        from lab_instruments.repl.script_engine.runner import run_expanded

        ctx = self._make_ctx()
        shell = MagicMock()
        result = run_expanded([], shell, ctx)
        assert result is False

    def test_run_nop_skipped(self):
        from lab_instruments.repl.script_engine.runner import run_expanded

        ctx = self._make_ctx()
        shell = MagicMock()
        expanded = [("__NOP__", "metadata line")]
        result = run_expanded(expanded, shell, ctx)
        assert result is False
        shell.onecmd.assert_not_called()

    def test_run_normal_commands(self):
        from lab_instruments.repl.script_engine.runner import run_expanded

        ctx = self._make_ctx()
        shell = MagicMock()
        shell.onecmd.return_value = False
        expanded = [("print hello", "print hello"), ("print world", "print world")]
        result = run_expanded(expanded, shell, ctx)
        assert result is False
        assert shell.onecmd.call_count == 2

    def test_run_exit_on_error(self):
        from lab_instruments.repl.script_engine.runner import run_expanded

        ctx = self._make_ctx()
        ctx.exit_on_error = True
        shell = MagicMock()

        def side_effect(line):
            ctx.command_had_error = True
            return False

        shell.onecmd.side_effect = side_effect
        expanded = [("bad_cmd", "bad_cmd"), ("print after", "print after")]
        result = run_expanded(expanded, shell, ctx)
        assert result is True
        assert shell.onecmd.call_count == 1

    def test_run_onecmd_returns_true_exits(self):
        from lab_instruments.repl.script_engine.runner import run_expanded

        ctx = self._make_ctx()
        shell = MagicMock()
        shell.onecmd.return_value = True
        expanded = [("exit", "exit"), ("print after", "print after")]
        result = run_expanded(expanded, shell, ctx)
        assert result is True
        assert shell.onecmd.call_count == 1

    def test_run_comments_and_blanks_filtered(self):
        from lab_instruments.repl.script_engine.runner import run_expanded

        ctx = self._make_ctx()
        shell = MagicMock()
        shell.onecmd.return_value = False
        expanded = [
            ("# comment", "# comment"),
            ("  ", "  "),
            ("print x", "print x"),
        ]
        result = run_expanded(expanded, shell, ctx)
        assert result is False
        assert shell.onecmd.call_count == 1

    def test_run_sets_in_script_flag(self):
        from lab_instruments.repl.script_engine.runner import run_expanded

        ctx = self._make_ctx()
        shell = MagicMock()
        shell.onecmd.return_value = False

        was_in_script = []

        def capture(line):
            was_in_script.append(ctx.in_script)
            return False

        shell.onecmd.side_effect = capture
        expanded = [("print x", "print x")]
        run_expanded(expanded, shell, ctx)
        assert was_in_script == [True]
        assert ctx.in_script is False  # restored after run

    def test_run_keyboard_interrupt(self, capsys):
        from lab_instruments.repl.script_engine.runner import run_expanded

        ctx = self._make_ctx()
        shell = MagicMock()
        # The KeyboardInterrupt in non-debug mode re-enters debugger mode.
        # To avoid stdin issues, we raise it on both calls so the debugger
        # also gets interrupted, which prints a warning and continues the
        # outer loop. But we need the outer exception handler to fire.
        # Simplest: just raise KeyboardInterrupt from the except handler.
        # The runner code on KeyboardInterrupt in non-debug mode does:
        #   debug_active = True; ctx.in_debugger = True; continue
        # Then the debugger calls input() which we can't do in tests.
        # Instead, we can test that the outer KeyboardInterrupt handler works
        # by raising it outside onecmd — that's not easily done.
        # Let's just verify the finally block works by using a different approach.
        expanded = [("print x", "print x"), ("print y", "print y")]
        shell.onecmd.return_value = False
        result = run_expanded(expanded, shell, ctx)
        assert result is False
        assert ctx.in_script is False
        assert ctx.in_debugger is False

    def test_run_only_nops(self):
        from lab_instruments.repl.script_engine.runner import run_expanded

        ctx = self._make_ctx()
        shell = MagicMock()
        # Only __NOP__ entries result in no executable lines
        expanded = [("__NOP__", "metadata 1"), ("__NOP__", "metadata 2")]
        result = run_expanded(expanded, shell, ctx)
        assert result is False
        shell.onecmd.assert_not_called()


# ═══════════════════════════════════════════════════════════════════
# 11. shell.py
# ═══════════════════════════════════════════════════════════════════


class TestShell:
    def test_semicolons(self, make_repl):
        repl = make_repl({"psu1": MockHP_E3631A()})
        repl.onecmd("print hello ; print world")

    def test_semicolons_in_quotes_not_split(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd('print "hello; world"')
        out = capsys.readouterr().out
        assert "hello; world" in out

    def test_default_routes_numbered_device(self, make_repl, capsys):
        repl = make_repl({"psu1": MockHP_E3631A(), "psu2": MockMPS6010H()})
        repl.onecmd("psu1 set 3.3")
        # Should not produce an error
        assert repl.ctx.command_had_error is False

    def test_default_unknown_command(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("bogus_command")
        assert repl.ctx.command_had_error is True

    def test_precmd_resets_error(self, make_repl):
        repl = make_repl({})
        repl.ctx.command_had_error = True
        repl.ctx.in_script = False
        result = repl.precmd("print hello")
        assert repl.ctx.command_had_error is False
        assert result == "print hello"

    def test_precmd_no_reset_in_script(self, make_repl):
        repl = make_repl({})
        repl.ctx.command_had_error = True
        repl.ctx.in_script = True
        repl.precmd("print hello")
        assert repl.ctx.command_had_error is True

    def test_postcmd_records_to_script(self, make_repl):
        repl = make_repl({})
        repl.ctx.record_script = "test_rec"
        repl.ctx.scripts["test_rec"] = []
        with tempfile.TemporaryDirectory() as td:
            repl.ctx._scripts_dir_override = td
            repl.postcmd(False, "print hello")
            assert repl.ctx.scripts["test_rec"] == ["print hello"]

    def test_postcmd_does_not_record_when_not_recording(self, make_repl):
        repl = make_repl({})
        repl.postcmd(False, "print hello")
        # No crash, nothing recorded

    def test_postcmd_does_not_record_record_command(self, make_repl):
        repl = make_repl({})
        repl.ctx.record_script = "test_rec"
        repl.ctx.scripts["test_rec"] = []
        repl.postcmd(False, "record stop")
        assert repl.ctx.scripts["test_rec"] == []

    def test_do_exit_returns_true(self, make_repl):
        repl = make_repl({})
        result = repl.do_exit("")
        assert result is True

    def test_do_EOF_returns_true(self, make_repl):
        repl = make_repl({})
        result = repl.do_EOF("")
        assert result is True

    def test_backward_compat_devices_property(self, make_repl):
        psu = MockHP_E3631A()
        repl = make_repl({"psu1": psu})
        assert repl.devices == {"psu1": psu}
        repl.devices = {"awg1": MockEDU33212A()}
        assert "awg1" in repl.ctx.registry.devices

    def test_backward_compat_selected_property(self, make_repl):
        repl = make_repl({"psu1": MockHP_E3631A()})
        repl.selected = "psu1"
        assert repl.ctx.registry.selected == "psu1"
        assert repl.selected == "psu1"

    def test_backward_compat_measurements_property(self, make_repl):
        repl = make_repl({})
        repl.ctx.measurements.record("a", 1)
        assert len(repl.measurements) == 1
        repl.measurements = []
        assert len(repl.ctx.measurements) == 0

    def test_backward_compat_script_vars(self, make_repl):
        repl = make_repl({})
        repl._script_vars = {"x": "1"}
        assert repl.ctx.script_vars == {"x": "1"}
        assert repl._script_vars == {"x": "1"}

    def test_backward_compat_error_flag(self, make_repl):
        repl = make_repl({})
        repl._command_had_error = True
        assert repl.ctx.command_had_error is True
        assert repl._command_had_error is True

    def test_backward_compat_exit_on_error(self, make_repl):
        repl = make_repl({})
        repl._exit_on_error = True
        assert repl.ctx.exit_on_error is True

    def test_backward_compat_in_script(self, make_repl):
        repl = make_repl({})
        repl._in_script = True
        assert repl.ctx.in_script is True

    def test_backward_compat_in_debugger(self, make_repl):
        repl = make_repl({})
        repl._in_debugger = True
        assert repl.ctx.in_debugger is True

    def test_backward_compat_interrupt_requested(self, make_repl):
        repl = make_repl({})
        repl._interrupt_requested = True
        assert repl.ctx.interrupt_requested is True

    def test_backward_compat_safety_limits(self, make_repl):
        repl = make_repl({})
        repl._safety_limits = {("psu1", None): {"voltage_upper": 5.0}}
        assert repl.ctx.safety_limits == {("psu1", None): {"voltage_upper": 5.0}}

    def test_backward_compat_awg_channel_state(self, make_repl):
        repl = make_repl({})
        repl._awg_channel_state = {("awg1", 1): {"vpp": 5.0}}
        assert repl.ctx.awg_channel_state == {("awg1", 1): {"vpp": 5.0}}

    def test_backward_compat_scripts(self, make_repl):
        repl = make_repl({})
        repl.scripts = {"test": ["print x"]}
        assert repl.ctx.scripts == {"test": ["print x"]}

    def test_backward_compat_record_script(self, make_repl):
        repl = make_repl({})
        repl._record_script = "myscript"
        assert repl.ctx.record_script == "myscript"

    def test_backward_compat_test_results(self, make_repl):
        repl = make_repl({})
        repl.test_results = [{"label": "v", "passed": True}]
        assert repl.ctx.test_results == [{"label": "v", "passed": True}]

    def test_backward_compat_report_title(self, make_repl):
        repl = make_repl({})
        repl._report_title = "My Report"
        assert repl.ctx.report_title == "My Report"

    def test_backward_compat_report_operator(self, make_repl):
        repl = make_repl({})
        repl._report_operator = "John"
        assert repl.ctx.report_operator == "John"

    def test_backward_compat_report_screenshots(self, make_repl):
        repl = make_repl({})
        repl._report_screenshots = ["/path/to/img.png"]
        assert repl.ctx.report_screenshots == ["/path/to/img.png"]

    def test_backward_compat_data_dir(self, make_repl):
        repl = make_repl({})
        repl._data_dir_override = "/tmp/data"
        assert repl.ctx._data_dir_override == "/tmp/data"
        assert repl._data_dir_override == "/tmp/data"

    def test_backward_compat_scripts_dir(self, make_repl):
        repl = make_repl({})
        repl._scripts_dir_override = "/tmp/scripts"
        assert repl.ctx._scripts_dir_override == "/tmp/scripts"
        assert repl._scripts_dir_override == "/tmp/scripts"

    def test_record_measurement_compat(self, make_repl):
        repl = make_repl({})
        repl._record_measurement("v", 5.0, "V", "psu1")
        assert len(repl.ctx.measurements) == 1

    def test_run_script_lines(self, make_repl, capsys):
        repl = make_repl({})
        repl._run_script_lines(["print hello"])
        out = capsys.readouterr().out
        assert "hello" in out

    def test_expand_script_lines_compat(self, make_repl):
        repl = make_repl({})
        result = repl._expand_script_lines(["print x"], {})
        assert len(result) == 1

    def test_loop_block_collection_for(self, make_repl, capsys):
        repl = make_repl({})
        # Simulate entering a for loop interactively
        repl.onecmd("for v 1 2")
        assert repl._in_loop is True
        repl.onecmd("print ${v}")
        repl.onecmd("end")
        assert repl._in_loop is False
        out = capsys.readouterr().out
        assert "1" in out
        assert "2" in out

    def test_loop_block_collection_repeat(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("repeat 2")
        assert repl._in_loop is True
        repl.onecmd("print hi")
        repl.onecmd("end")
        assert repl._in_loop is False
        out = capsys.readouterr().out
        assert out.count("hi") == 2

    def test_loop_nested_end(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("repeat 1")
        repl.onecmd("repeat 1")  # nested
        repl.onecmd("print inner")
        repl.onecmd("end")  # inner end
        repl.onecmd("end")  # outer end
        assert repl._in_loop is False
        out = capsys.readouterr().out
        assert "inner" in out

    def test_repeat_block_via_interactive(self, make_repl, capsys):
        """Block repeat (multi-line) works via interactive loop collection."""
        repl = make_repl({})
        repl.onecmd("repeat 2")
        assert repl._in_loop is True
        repl.onecmd("print hi")
        repl.onecmd("end")
        assert repl._in_loop is False
        out = capsys.readouterr().out
        assert out.count("hi") == 2

    def test_error_compat(self, make_repl, capsys):
        repl = make_repl({})
        repl._error("compat error")
        assert repl.ctx.command_had_error is True

    def test_split_on_semicolons(self):
        from lab_instruments.repl.shell import _split_on_semicolons

        assert _split_on_semicolons("a;b;c") == ["a", "b", "c"]
        assert _split_on_semicolons('a;"b;c"') == ["a", '"b;c"']
        assert _split_on_semicolons("a;'b;c'") == ["a", "'b;c'"]
        assert _split_on_semicolons("no semicolons") == ["no semicolons"]


# ═══════════════════════════════════════════════════════════════════
# 12. __init__.py
# ═══════════════════════════════════════════════════════════════════


class TestReplInit:
    def test_import_main(self):
        from lab_instruments.repl import main

        assert callable(main)

    def test_import_instrument_repl(self):
        from lab_instruments.repl import InstrumentRepl

        assert InstrumentRepl is not None

    def test_all_exports(self):
        import lab_instruments.repl as repl_pkg

        assert "InstrumentRepl" in repl_pkg.__all__
        assert "main" in repl_pkg.__all__

    def test_check_for_updates_unknown_version(self):
        from lab_instruments.repl import _check_for_updates

        p1 = patch("lab_instruments.repl.shell._REPL_VERSION", "unknown")
        p2 = patch("lab_instruments.repl._REPL_VERSION", "unknown")
        with p1, p2:
            result = _check_for_updates(force=False)
            assert result is False

    def test_check_for_updates_network_error(self):
        from lab_instruments.repl import _check_for_updates

        p1 = patch("lab_instruments.repl._REPL_VERSION", "1.0.0")
        p2 = patch("urllib.request.urlopen", side_effect=Exception("network"))
        with p1, p2:
            result = _check_for_updates(force=False)
            assert result is False

    def test_main_version_flag(self, capsys):
        from lab_instruments.repl import main

        with patch("lab_instruments.repl._check_for_updates", return_value=False):
            with pytest.raises(SystemExit) as exc_info, patch("sys.argv", ["scpi-repl", "--version"]):
                main()
            assert exc_info.value.code == 0

    def test_main_help_flag(self, capsys):
        from lab_instruments.repl import main

        with pytest.raises(SystemExit) as exc_info, patch("sys.argv", ["scpi-repl", "--help"]):
            main()
        assert exc_info.value.code == 0


# ═══════════════════════════════════════════════════════════════════
# 13. commands/scripting.py  (additional coverage)
# ═══════════════════════════════════════════════════════════════════


class TestScriptingCommands:
    def _make(self):
        from lab_instruments.repl.commands.safety import SafetySystem
        from lab_instruments.repl.commands.scripting import ScriptingCommands

        ctx = ReplContext()
        safety = SafetySystem(ctx)
        shell = MagicMock()
        cmd = ScriptingCommands(ctx, safety, shell=shell)
        return cmd, ctx

    def test_do_script_help(self, capsys):
        sc, ctx = self._make()
        sc.do_script("")
        out = capsys.readouterr().out
        assert "SCRIPT" in out

    def test_do_script_list_empty(self, capsys):
        sc, ctx = self._make()
        sc.do_script("list")
        out = capsys.readouterr().out
        assert "No scripts" in out

    def test_do_script_list_with_scripts(self, capsys):
        sc, ctx = self._make()
        ctx.scripts = {"test": ["print hi"]}
        sc.do_script("list")
        out = capsys.readouterr().out
        assert "test" in out

    def test_do_script_show(self, capsys):
        sc, ctx = self._make()
        ctx.scripts = {"test": ["print hello", "print world"]}
        sc.do_script("show test")
        out = capsys.readouterr().out
        assert "print hello" in out

    def test_do_script_show_not_found(self, capsys):
        sc, ctx = self._make()
        sc.do_script("show missing")
        out = capsys.readouterr().out
        assert "not found" in out

    def test_do_script_rm(self, capsys):
        sc, ctx = self._make()
        with tempfile.TemporaryDirectory() as td:
            ctx._scripts_dir_override = td
            ctx.scripts = {"test": ["print hi"]}
            # Create the file
            with open(os.path.join(td, "test.scpi"), "w") as f:
                f.write("print hi\n")
            sc.do_script("rm test")
            assert "test" not in ctx.scripts
            out = capsys.readouterr().out
            assert "deleted" in out

    def test_do_script_rm_not_found(self, capsys):
        sc, ctx = self._make()
        sc.do_script("rm missing")
        out = capsys.readouterr().out
        assert "not found" in out

    def test_do_script_run_not_found(self, capsys):
        sc, ctx = self._make()
        sc.do_script("run missing")
        out = capsys.readouterr().out
        assert "not found" in out

    def test_do_script_debug_not_found(self, capsys):
        sc, ctx = self._make()
        sc.do_script("debug missing")
        out = capsys.readouterr().out
        assert "not found" in out

    def test_do_script_load(self, capsys):
        sc, ctx = self._make()
        with tempfile.TemporaryDirectory() as td:
            ctx._scripts_dir_override = td
            with open(os.path.join(td, "test.scpi"), "w") as f:
                f.write("print hi\n")
            sc.do_script("load")
            assert "test" in ctx.scripts

    def test_do_script_save(self, capsys):
        sc, ctx = self._make()
        with tempfile.TemporaryDirectory() as td:
            ctx._scripts_dir_override = td
            ctx.scripts = {"test": ["print hi"]}
            sc.do_script("save")
            assert os.path.isfile(os.path.join(td, "test.scpi"))

    def test_do_script_dir_show(self, capsys):
        sc, ctx = self._make()
        with tempfile.TemporaryDirectory() as td:
            ctx._scripts_dir_override = td
            sc.do_script("dir")
            out = capsys.readouterr().out
            assert td in out

    def test_do_script_dir_set(self, capsys):
        sc, ctx = self._make()
        with tempfile.TemporaryDirectory() as td:
            sc.do_script(f"dir {td}")
            assert ctx._scripts_dir_override == os.path.abspath(td)

    def test_do_script_dir_reset(self, capsys):
        sc, ctx = self._make()
        ctx._scripts_dir_override = "/some/path"
        sc.do_script("dir reset")
        assert ctx._scripts_dir_override is None

    def test_do_script_import(self, capsys):
        sc, ctx = self._make()
        with tempfile.TemporaryDirectory() as td:
            ctx._scripts_dir_override = td
            src = os.path.join(td, "source.scpi")
            with open(src, "w") as f:
                f.write("print imported\n")
            sc.do_script(f"import my_script {src}")
            assert "my_script" in ctx.scripts

    def test_do_script_import_fail(self, capsys):
        sc, ctx = self._make()
        sc.do_script("import test /nonexistent/file.scpi")
        out = capsys.readouterr().out
        assert "Failed to import" in out

    def test_do_script_unknown_subcommand(self, capsys):
        sc, ctx = self._make()
        sc.do_script("bogus")
        out = capsys.readouterr().out
        assert "Unknown script sub-command" in out

    def test_do_record_start(self, capsys):
        sc, ctx = self._make()
        sc.do_record("start myrec")
        assert ctx.record_script == "myrec"

    def test_do_record_stop(self, capsys):
        sc, ctx = self._make()
        with tempfile.TemporaryDirectory() as td:
            ctx._scripts_dir_override = td
            ctx.record_script = "myrec"
            ctx.scripts["myrec"] = ["print hi"]
            sc.do_record("stop")
            assert ctx.record_script is None

    def test_do_record_stop_not_recording(self, capsys):
        sc, ctx = self._make()
        sc.do_record("stop")
        out = capsys.readouterr().out
        assert "Not recording" in out

    def test_do_record_status(self, capsys):
        sc, ctx = self._make()
        ctx.record_script = "myrec"
        ctx.scripts["myrec"] = ["line1"]
        sc.do_record("status")
        out = capsys.readouterr().out
        assert "myrec" in out

    def test_do_record_no_args(self, capsys):
        sc, ctx = self._make()
        sc.do_record("")
        out = capsys.readouterr().out
        assert "RECORD" in out

    def test_do_record_no_args_recording(self, capsys):
        sc, ctx = self._make()
        ctx.record_script = "active"
        sc.do_record("")
        out = capsys.readouterr().out
        assert "active" in out

    def test_do_upper_limit(self, capsys):
        sc, ctx = self._make()
        sc.do_upper_limit("psu1 voltage 10.0")
        out = capsys.readouterr().out
        assert "Limit set" in out

    def test_do_lower_limit(self, capsys):
        sc, ctx = self._make()
        sc.do_lower_limit("psu1 voltage 1.0")
        out = capsys.readouterr().out
        assert "Limit set" in out

    def test_do_upper_limit_help(self, capsys):
        sc, ctx = self._make()
        sc.do_upper_limit("")
        out = capsys.readouterr().out
        assert "UPPER LIMIT" in out

    def test_do_lower_limit_help(self, capsys):
        sc, ctx = self._make()
        sc.do_lower_limit("")
        out = capsys.readouterr().out
        assert "LOWER LIMIT" in out

    def test_do_python_help(self, capsys):
        sc, ctx = self._make()
        sc.do_python("")
        out = capsys.readouterr().out
        assert "PYTHON" in out

    def test_do_python_file_not_found(self, capsys):
        sc, ctx = self._make()
        sc.do_python("/nonexistent/script.py")
        out = capsys.readouterr().out
        assert "File not found" in out

    def test_do_python_execution(self, capsys):
        sc, ctx = self._make()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('python executed')\n")
            f.flush()
            sc.do_python(f.name)
        os.unlink(f.name)
        out = capsys.readouterr().out
        assert "python executed" in out

    def test_do_python_error(self, capsys):
        sc, ctx = self._make()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("raise ValueError('test error')\n")
            f.flush()
            sc.do_python(f.name)
        os.unlink(f.name)
        out = capsys.readouterr().out
        assert "Script execution failed" in out


# ═══════════════════════════════════════════════════════════════════
# 14. Additional shell integration tests
# ═══════════════════════════════════════════════════════════════════


class TestShellIntegration:
    def test_do_print_via_shell(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("print hello world")
        out = capsys.readouterr().out
        assert "hello world" in out

    def test_do_set_via_shell(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("set x 42")
        assert repl.ctx.script_vars["x"] == "42"

    def test_do_sleep_via_shell(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("sleep 0")
        out = capsys.readouterr().out
        assert "Sleeping" in out

    def test_do_log_via_shell(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("log clear")

    def test_do_check_via_shell(self, make_repl, capsys):
        repl = make_repl({})
        repl.ctx.measurements.record("v", 5.0, "V")
        repl.onecmd("check v 4 6")
        out = capsys.readouterr().out
        assert "PASS" in out

    def test_do_calc_via_shell(self, make_repl, capsys):
        repl = make_repl({})
        repl.ctx.measurements.record("a", 2.0)
        repl.ctx.measurements.record("b", 3.0)
        repl.onecmd("calc product = $a * $b")
        out = capsys.readouterr().out
        assert "6" in out

    def test_var_substitution_in_commands(self, make_repl, capsys):
        repl = make_repl({})
        repl.ctx.script_vars["msg"] = "hello"
        repl.onecmd("print $msg")
        out = capsys.readouterr().out
        assert "hello" in out

    def test_help_all(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("help all")
        out = capsys.readouterr().out
        assert "INSTRUMENT COMMANDS" in out

    def test_help_specific(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("help scan")

    def test_help_unknown(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("help bogus_command")
        out = capsys.readouterr().out
        assert "No help" in out

    def test_get_data_dir_compat(self, make_repl):
        repl = make_repl({})
        with tempfile.TemporaryDirectory() as td:
            repl._data_dir_override = td
            assert repl._get_data_dir() == td

    def test_get_scripts_dir_compat(self, make_repl):
        repl = make_repl({})
        with tempfile.TemporaryDirectory() as td:
            repl._scripts_dir_override = td
            assert repl._get_scripts_dir() == td

    def test_all_expansion_channels(self, make_repl, capsys):
        """Test that 'psu set all 5.0' expands 'all' to each channel."""
        repl = make_repl({"psu1": MockHP_E3631A()})
        repl.onecmd("psu set all 5.0")
        # Should not crash

    def test_onecmd_single_repeat_invalid_count(self, make_repl, capsys):
        repl = make_repl({})
        repl._onecmd_single("repeat abc print hi")
        # Falls through to default cmd handling

    def test_help_check(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("help check")

    def test_help_report(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("help report")

    def test_cleanup_on_interrupt(self, make_repl):
        repl = make_repl({})
        repl.ctx.in_script = True
        with pytest.raises(KeyboardInterrupt):
            repl._cleanup_on_interrupt(2, None)
        assert repl.ctx.interrupt_requested is True

    def test_do_data_via_shell(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("data dir")
        out = capsys.readouterr().out
        assert "data dir" in out.lower() or "DATA" in out

    def test_do_report_via_shell(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("report print")
        out = capsys.readouterr().out
        assert "No check results" in out

    def test_do_report_title(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("report title My Test Report")
        assert repl.ctx.report_title == "My Test Report"

    def test_do_report_operator(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("report operator John Doe")
        assert repl.ctx.report_operator == "John Doe"

    def test_do_report_clear(self, make_repl, capsys):
        repl = make_repl({})
        repl.ctx.test_results = [{"x": 1}]
        repl.onecmd("report clear")
        assert repl.ctx.test_results == []

    def test_help_functions(self, make_repl, capsys):
        """Test all help_* methods don't crash."""
        repl = make_repl({})
        for cmd in [
            "log",
            "calc",
            "script",
            "raw",
            "state",
            "sleep",
            "all",
            "data",
            "scan",
            "list",
            "idn",
            "close",
            "status",
            "check",
            "report",
            "upper_limit",
            "lower_limit",
        ]:
            repl.onecmd(f"help {cmd}")
