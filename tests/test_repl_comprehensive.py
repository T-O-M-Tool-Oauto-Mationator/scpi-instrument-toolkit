"""tests/test_repl_comprehensive.py -- Comprehensive REPL tests.

Covers arithmetic, data type conversion, logging, printing, plotting,
and error handling using the make_repl fixture from conftest.py.
"""

import math

import pytest

from lab_instruments.repl.syntax import safe_eval

# ===================================================================
# 1. Arithmetic & Math Functions
# ===================================================================


class TestArithmeticOperators:
    """Test all arithmetic operators via REPL assignment and safe_eval."""

    def test_addition(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("x = 3 + 4")
        assert repl.ctx.script_vars["x"] == 7

    def test_subtraction(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("x = 10 - 3")
        assert repl.ctx.script_vars["x"] == 7

    def test_multiplication(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("x = 6 * 7")
        assert repl.ctx.script_vars["x"] == 42

    def test_division(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("x = 15 / 4")
        assert repl.ctx.script_vars["x"] == 3.75

    def test_floor_division(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("x = 15 // 4")
        assert repl.ctx.script_vars["x"] == 3

    def test_modulo(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("x = 17 % 5")
        assert repl.ctx.script_vars["x"] == 2

    def test_power(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("x = 2 ** 10")
        assert repl.ctx.script_vars["x"] == 1024

    def test_operator_precedence(self, make_repl, capsys):
        """2 + 3 * 4 should be 14, not 20."""
        repl = make_repl({})
        repl.onecmd("x = 2 + 3 * 4")
        assert repl.ctx.script_vars["x"] == 14

    def test_parenthesized_precedence(self, make_repl, capsys):
        """(2 + 3) * 4 should be 20."""
        repl = make_repl({})
        repl.onecmd("x = (2 + 3) * 4")
        assert repl.ctx.script_vars["x"] == 20

    def test_chained_operations(self, make_repl, capsys):
        """Test multi-step expression: (a + b) * (c - d) / e."""
        repl = make_repl({})
        repl.onecmd("a = 10")
        repl.onecmd("b = 5")
        repl.onecmd("c = 8")
        repl.onecmd("d = 3")
        repl.onecmd("e_val = 5")
        capsys.readouterr()
        repl.onecmd("result = ({a} + {b}) * ({c} - {d}) / {e_val}")
        # (10 + 5) * (8 - 3) / 5 = 15 * 5 / 5 = 15
        assert float(repl.ctx.script_vars["result"]) == 15.0

    def test_negative_numbers(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("x = -5 + 3")
        assert repl.ctx.script_vars["x"] == -2

    def test_unary_minus(self):
        result = safe_eval("-42", {})
        assert result == -42


class TestMathFunctions:
    """Test math functions available in the safe evaluator."""

    def test_sqrt(self):
        result = safe_eval("sqrt(144)", {})
        assert result == 12.0

    def test_sin(self):
        result = safe_eval("sin(0)", {})
        assert result == 0.0

    def test_cos(self):
        result = safe_eval("cos(0)", {})
        assert result == 1.0

    def test_tan(self):
        result = safe_eval("tan(0)", {})
        assert result == 0.0

    def test_log_natural(self):
        result = safe_eval("log(e)", {})
        assert abs(result - 1.0) < 1e-10

    def test_log10(self):
        result = safe_eval("log10(1000)", {})
        assert abs(result - 3.0) < 1e-10

    def test_exp(self):
        result = safe_eval("exp(0)", {})
        assert result == 1.0

    def test_ceil(self):
        result = safe_eval("ceil(3.2)", {})
        assert result == 4

    def test_floor(self):
        result = safe_eval("floor(3.8)", {})
        assert result == 3

    def test_abs_positive(self):
        result = safe_eval("abs(-7)", {})
        assert result == 7

    def test_abs_negative(self):
        result = safe_eval("abs(5)", {})
        assert result == 5

    def test_round_no_digits(self):
        result = safe_eval("round(3.7)", {})
        assert result == 4

    def test_round_with_digits(self):
        result = safe_eval("round(3.14159, 2)", {})
        assert result == 3.14

    def test_pow_func(self):
        result = safe_eval("pow(2, 8)", {})
        assert result == 256

    def test_min_func(self):
        result = safe_eval("min(3, 1, 4, 1, 5)", {})
        assert result == 1

    def test_max_func(self):
        result = safe_eval("max(3, 1, 4, 1, 5)", {})
        assert result == 5

    def test_sum_func(self):
        result = safe_eval("sum([1, 2, 3, 4, 5])", {})
        assert result == 15


class TestMathConstants:
    """Test math constants accessible in the evaluator."""

    def test_pi(self):
        result = safe_eval("pi", {})
        assert abs(result - math.pi) < 1e-10

    def test_e(self):
        result = safe_eval("e", {})
        assert abs(result - math.e) < 1e-10

    def test_pi_in_expression(self):
        """Area of unit circle: pi * 1**2."""
        result = safe_eval("pi * 1 ** 2", {})
        assert abs(result - math.pi) < 1e-10


class TestNestedFunctionCalls:
    """Test nested math function calls."""

    def test_round_sqrt(self):
        result = safe_eval("round(sqrt(2), 4)", {})
        assert result == 1.4142

    def test_abs_floor(self):
        result = safe_eval("abs(floor(-3.7))", {})
        assert result == 4

    def test_ceil_of_division(self):
        result = safe_eval("ceil(7 / 3)", {})
        assert result == 3

    def test_sqrt_of_sum(self):
        """sqrt(3^2 + 4^2) = 5."""
        result = safe_eval("sqrt(3**2 + 4**2)", {})
        assert result == 5.0

    def test_log10_of_exp(self):
        result = safe_eval("round(log10(exp(1)), 4)", {})
        expected = round(math.log10(math.e), 4)
        assert result == expected


# ===================================================================
# 2. Data Type Conversion
# ===================================================================


class TestTypeConversionInt:
    """Test int() conversions."""

    def test_int_from_float_literal(self):
        result = safe_eval("int(3.9)", {})
        assert result == 3

    def test_int_from_string(self):
        result = safe_eval('int("42")', {})
        assert result == 42

    def test_int_from_negative(self):
        result = safe_eval("int(-2.7)", {})
        assert result == -2


class TestTypeConversionFloat:
    """Test float() conversions."""

    def test_float_from_int(self):
        result = safe_eval("float(5)", {})
        assert result == 5.0
        assert isinstance(result, float)

    def test_float_from_string(self):
        result = safe_eval('float("3.14")', {})
        assert result == 3.14


class TestTypeConversionStr:
    """Test str() conversions."""

    def test_str_from_int(self):
        result = safe_eval("str(42)", {})
        assert result == "42"

    def test_str_from_float(self):
        result = safe_eval("str(3.14)", {})
        assert result == "3.14"


class TestTypeConversionBool:
    """Test bool() conversions and edge cases."""

    def test_bool_of_zero(self):
        result = safe_eval("bool(0)", {})
        assert result is False

    def test_bool_of_one(self):
        result = safe_eval("bool(1)", {})
        assert result is True

    def test_bool_of_empty_string(self):
        result = safe_eval('bool("")', {})
        assert result is False

    def test_bool_of_nonempty_string(self):
        result = safe_eval('bool("hello")', {})
        assert result is True

    def test_bool_of_empty_list(self):
        result = safe_eval("bool([])", {})
        assert result is False

    def test_bool_of_nonempty_list(self):
        result = safe_eval("bool([1])", {})
        assert result is True


class TestTypeConversionHexBinOct:
    """Test hex(), bin(), oct() conversions."""

    def test_hex(self):
        result = safe_eval("hex(255)", {})
        assert result == "0xff"

    def test_bin(self):
        result = safe_eval("bin(10)", {})
        assert result == "0b1010"

    def test_oct(self):
        result = safe_eval("oct(8)", {})
        assert result == "0o10"


class TestTypeConversionOrdChr:
    """Test ord() and chr() conversions."""

    def test_ord(self):
        result = safe_eval('ord("A")', {})
        assert result == 65

    def test_chr(self):
        result = safe_eval("chr(65)", {})
        assert result == "A"

    def test_chr_ord_roundtrip(self):
        result = safe_eval('chr(ord("Z"))', {})
        assert result == "Z"


class TestTypeConversionChains:
    """Test chained type conversions."""

    def test_int_of_float_string(self):
        """int(float('3.7')) should truncate to 3."""
        result = safe_eval('int(float("3.7"))', {})
        assert result == 3

    def test_float_of_int_roundtrip(self):
        """float(int(3.7)) should be 3.0."""
        result = safe_eval("float(int(3.7))", {})
        assert result == 3.0
        assert isinstance(result, float)

    def test_str_of_int_of_float(self):
        result = safe_eval("str(int(9.9))", {})
        assert result == "9"


class TestTypeConversionErrors:
    """Test that invalid type conversions raise appropriately."""

    def test_int_of_nonumeric_string(self):
        with pytest.raises(ValueError):
            safe_eval('int("hello")', {})

    def test_float_of_nonnumeric_string(self):
        with pytest.raises(ValueError):
            safe_eval('float("abc")', {})


# ===================================================================
# 3. Logging Commands
# ===================================================================


class TestLogCommand:
    """Test the log command: print, clear, and recording."""

    def test_log_print_no_measurements(self, make_repl, capsys):
        """log print with no data should warn."""
        repl = make_repl({})
        capsys.readouterr()
        repl.onecmd("log print")
        out = capsys.readouterr().out
        assert "no measurements" in out.lower()

    def test_log_print_with_data(self, make_repl, capsys):
        """log print after recording should display entries."""
        repl = make_repl({})
        repl.ctx.measurements.record("vout", 3.3, "V", "psu1")
        capsys.readouterr()
        repl.onecmd("log print")
        out = capsys.readouterr().out
        assert "vout" in out
        assert "3.3" in out

    def test_log_clear(self, make_repl, capsys):
        """log clear should remove all measurements."""
        repl = make_repl({})
        repl.ctx.measurements.record("vout", 3.3, "V", "psu1")
        repl.ctx.measurements.record("iout", 0.5, "A", "psu1")
        assert len(repl.ctx.measurements) == 2
        repl.onecmd("log clear")
        assert len(repl.ctx.measurements) == 0

    def test_log_clear_then_print(self, make_repl, capsys):
        """After clearing, log print should warn no data."""
        repl = make_repl({})
        repl.ctx.measurements.record("vout", 3.3, "V", "psu1")
        repl.onecmd("log clear")
        capsys.readouterr()
        repl.onecmd("log print")
        out = capsys.readouterr().out
        assert "no measurements" in out.lower()

    def test_log_help(self, make_repl, capsys):
        """log with no args should show help."""
        repl = make_repl({})
        capsys.readouterr()
        repl.onecmd("log")
        out = capsys.readouterr().out
        assert "log print" in out.lower() or "log" in out.lower()

    def test_log_unknown_subcommand(self, make_repl, capsys):
        """log foo should warn about unknown subcommand."""
        repl = make_repl({})
        capsys.readouterr()
        repl.onecmd("log foo")
        out = capsys.readouterr().out
        assert "unknown" in out.lower() or "log print" in out.lower()

    def test_log_multiple_entries(self, make_repl, capsys):
        """Log should preserve multiple entries."""
        repl = make_repl({})
        repl.ctx.measurements.record("v1", 1.0, "V", "psu1")
        repl.ctx.measurements.record("v2", 2.0, "V", "psu1")
        repl.ctx.measurements.record("v3", 3.0, "V", "psu1")
        capsys.readouterr()
        repl.onecmd("log print")
        out = capsys.readouterr().out
        assert "v1" in out
        assert "v2" in out
        assert "v3" in out


class TestCalcCommand:
    """Test the calc command for derived measurements."""

    def test_calc_simple(self, make_repl, capsys):
        """calc power = 5 * 2 unit=W should compute and store."""
        repl = make_repl({})
        repl.onecmd("calc power = 5 * 2 unit=W")
        entry = repl.ctx.measurements.get_by_label("power")
        assert entry is not None
        assert entry["value"] == 10
        assert entry["unit"] == "W"

    def test_calc_with_unit(self, make_repl, capsys):
        """calc with unit= suffix should preserve the unit."""
        repl = make_repl({})
        repl.onecmd("calc resistance = 5 / 0.01 unit=ohms")
        entry = repl.ctx.measurements.get_by_label("resistance")
        assert entry is not None
        assert entry["value"] == 500.0
        assert entry["unit"] == "ohms"

    def test_calc_no_unit(self, make_repl, capsys):
        """calc without unit= should work with empty unit."""
        repl = make_repl({})
        repl.onecmd("calc ratio = 10 / 3")
        entry = repl.ctx.measurements.get_by_label("ratio")
        assert entry is not None
        assert entry["unit"] == ""

    def test_calc_stores_in_script_vars(self, make_repl, capsys):
        """calc should also store the result in script_vars."""
        repl = make_repl({})
        repl.onecmd("calc total = 100 + 200")
        assert repl.ctx.script_vars.get("total") == 300

    def test_calc_with_last_keyword(self, make_repl, capsys):
        """calc using 'last' should reference the most recent measurement."""
        repl = make_repl({})
        repl.ctx.measurements.record("reading", 4.5, "V", "dmm")
        capsys.readouterr()
        repl.onecmd("calc doubled = last * 2 unit=V")
        entry = repl.ctx.measurements.get_by_label("doubled")
        assert entry is not None
        assert entry["value"] == 9.0

    def test_calc_with_measurement_variables(self, make_repl, capsys):
        """calc should be able to reference previously recorded measurements."""
        repl = make_repl({})
        repl.ctx.measurements.record("voltage", 5.0, "V", "psu")
        repl.ctx.measurements.record("current", 0.1, "A", "psu")
        # Store them in script_vars too for the evaluator
        repl.ctx.script_vars["voltage"] = "5.0"
        repl.ctx.script_vars["current"] = "0.1"
        capsys.readouterr()
        repl.onecmd("calc power = {voltage} * {current} unit=W")
        entry = repl.ctx.measurements.get_by_label("power")
        assert entry is not None
        assert abs(entry["value"] - 0.5) < 1e-9

    def test_calc_invalid_expression(self, make_repl, capsys):
        """calc with invalid expression should report error."""
        repl = make_repl({})
        capsys.readouterr()
        repl.onecmd("calc bad = xyz_unknown_func()")
        out = capsys.readouterr().out
        assert "error" in out.lower() or "failed" in out.lower()


class TestLogNativeTypes:
    """Test that measurement store preserves native types."""

    def test_record_float(self, make_repl, capsys):
        repl = make_repl({})
        repl.ctx.measurements.record("temp", 25.5, "C", "sensor")
        entry = repl.ctx.measurements.get_by_label("temp")
        assert isinstance(entry["value"], float)
        assert entry["value"] == 25.5

    def test_record_int(self, make_repl, capsys):
        repl = make_repl({})
        repl.ctx.measurements.record("count", 42, "", "counter")
        entry = repl.ctx.measurements.get_by_label("count")
        assert isinstance(entry["value"], int)
        assert entry["value"] == 42

    def test_get_last(self, make_repl, capsys):
        repl = make_repl({})
        repl.ctx.measurements.record("a", 1.0, "V", "src")
        repl.ctx.measurements.record("b", 2.0, "V", "src")
        last = repl.ctx.measurements.get_last()
        assert last["label"] == "b"
        assert last["value"] == 2.0


# ===================================================================
# 4. Print Command
# ===================================================================


class TestPrintCommand:
    """Test print command variations."""

    def test_print_plain_text(self, make_repl, capsys):
        repl = make_repl({})
        capsys.readouterr()
        repl.onecmd("print hello world")
        out = capsys.readouterr().out
        assert "hello world" in out

    def test_print_quoted_text(self, make_repl, capsys):
        repl = make_repl({})
        capsys.readouterr()
        repl.onecmd('print "hello world"')
        out = capsys.readouterr().out
        assert "hello world" in out

    def test_print_single_quoted_text(self, make_repl, capsys):
        repl = make_repl({})
        capsys.readouterr()
        repl.onecmd("print 'hello world'")
        out = capsys.readouterr().out
        assert "hello world" in out

    def test_print_var_substitution(self, make_repl, capsys):
        repl = make_repl({})
        repl.ctx.script_vars["voltage"] = "3.3"
        capsys.readouterr()
        repl.onecmd('print "Voltage is {voltage}V"')
        out = capsys.readouterr().out
        assert "Voltage is 3.3V" in out

    def test_print_int_var(self, make_repl, capsys):
        repl = make_repl({})
        repl.ctx.script_vars["count"] = "42"
        capsys.readouterr()
        repl.onecmd('print "count={count}"')
        out = capsys.readouterr().out
        assert "count=42" in out

    def test_print_float_var(self, make_repl, capsys):
        repl = make_repl({})
        repl.ctx.script_vars["pi_val"] = "3.14159"
        capsys.readouterr()
        repl.onecmd('print "pi={pi_val}"')
        out = capsys.readouterr().out
        assert "pi=3.14159" in out

    def test_print_bool_var(self, make_repl, capsys):
        repl = make_repl({})
        repl.ctx.script_vars["flag"] = "True"
        capsys.readouterr()
        repl.onecmd('print "flag={flag}"')
        out = capsys.readouterr().out
        assert "flag=True" in out

    def test_print_list_var(self, make_repl, capsys):
        repl = make_repl({})
        repl.ctx.script_vars["data"] = "[1, 2, 3]"
        capsys.readouterr()
        repl.onecmd('print "data={data}"')
        out = capsys.readouterr().out
        assert "data=[1, 2, 3]" in out

    def test_print_unquoted_with_var(self, make_repl, capsys):
        repl = make_repl({})
        repl.ctx.script_vars["x"] = "99"
        capsys.readouterr()
        repl.onecmd("print x={x}")
        out = capsys.readouterr().out
        assert "x=99" in out

    def test_print_undefined_var_left_as_placeholder(self, make_repl, capsys):
        repl = make_repl({})
        capsys.readouterr()
        repl.onecmd('print "{undefined_var}"')
        out = capsys.readouterr().out
        assert "{undefined_var}" in out

    def test_print_multiple_vars(self, make_repl, capsys):
        repl = make_repl({})
        repl.ctx.script_vars["a"] = "10"
        repl.ctx.script_vars["b"] = "20"
        repl.ctx.script_vars["c"] = "30"
        capsys.readouterr()
        repl.onecmd('print "{a} + {b} = {c}"')
        out = capsys.readouterr().out
        assert "10 + 20 = 30" in out

    def test_print_empty(self, make_repl, capsys):
        repl = make_repl({})
        capsys.readouterr()
        repl.onecmd("print")
        out = capsys.readouterr().out
        assert out == "\n"

    def test_print_no_ansi_codes(self, make_repl, capsys):
        """print must output plain text with no ANSI escape sequences."""
        repl = make_repl({})
        capsys.readouterr()
        repl.onecmd("print test output")
        out = capsys.readouterr().out
        assert "\033[" not in out


# ===================================================================
# 5. Plotting Commands
# ===================================================================


class TestPlotCommand:
    """Test plot command behavior."""

    def test_plot_no_data_warns(self, make_repl, capsys):
        """plot with no measurements should warn."""
        repl = make_repl({})
        capsys.readouterr()
        repl.onecmd("plot")
        out = capsys.readouterr().out
        assert "no measurements" in out.lower() or "nothing to plot" in out.lower()

    def test_plot_help(self, make_repl, capsys):
        """plot --help should display usage info."""
        repl = make_repl({})
        capsys.readouterr()
        repl.onecmd("plot --help")
        out = capsys.readouterr().out
        assert "plot" in out.lower()

    def test_plot_with_data_does_not_crash(self, make_repl, capsys):
        """plot with measurements should not raise (requires matplotlib)."""
        pytest.importorskip("matplotlib")
        repl = make_repl({})
        repl.ctx.measurements.record("v1", 1.0, "V", "test")
        repl.ctx.measurements.record("v2", 2.0, "V", "test")
        repl.ctx.measurements.record("v3", 3.0, "V", "test")
        capsys.readouterr()
        # Should not raise; output may include __PLOT__ marker
        repl.onecmd("plot")
        out = capsys.readouterr().out
        assert "error" not in out.lower() or "__PLOT__" in out

    def test_plot_no_matching_pattern(self, make_repl, capsys):
        """plot with a non-matching pattern should warn."""
        repl = make_repl({})
        repl.ctx.measurements.record("v1", 1.0, "V", "test")
        capsys.readouterr()
        repl.onecmd("plot zzz_nonexistent*")
        out = capsys.readouterr().out
        assert "no measurements match" in out.lower()

    def test_plot_module_importable(self):
        """The plot command module should be importable."""
        from lab_instruments.repl.commands.plot import PlotCommand

        assert PlotCommand is not None


# ===================================================================
# 6. Error Handling
# ===================================================================


class TestDivisionByZero:
    """Division by zero in safe_eval raises ZeroDivisionError (Python-style)."""

    def test_division_by_zero_raises(self):
        with pytest.raises(ZeroDivisionError):
            safe_eval("1 / 0", {})

    def test_floor_division_by_zero_raises(self):
        with pytest.raises(ZeroDivisionError):
            safe_eval("1 // 0", {})

    def test_modulo_by_zero_raises(self):
        with pytest.raises(ZeroDivisionError):
            safe_eval("1 % 0", {})


class TestUndefinedVariables:
    """Test behavior with undefined variable references."""

    def test_undefined_var_in_assignment(self, make_repl, capsys):
        """Assignment referencing an undefined var should store the raw string."""
        repl = make_repl({})
        repl.onecmd("x = some_undefined_thing")
        # Should store the string literal since it cannot be evaluated numerically
        assert "x" in repl.ctx.script_vars

    def test_undefined_var_in_print_stays_as_placeholder(self, make_repl, capsys):
        repl = make_repl({})
        capsys.readouterr()
        repl.onecmd('print "{nope}"')
        out = capsys.readouterr().out
        assert "{nope}" in out


class TestInvalidFunctionName:
    """Test calling a function that is not in the allowlist."""

    def test_disallowed_function_raises(self):
        # __import__ is a NameError in strict mode (not in allowed_funcs).
        with pytest.raises(NameError):
            safe_eval("__import__('os')", {})

    def test_unknown_function_name_raises_nameerror(self):
        """Unknown function names raise NameError in strict mode."""
        with pytest.raises(NameError, match="foobar"):
            safe_eval("foobar(1, 2)", {})


class TestSyntaxErrors:
    """Test that malformed expressions raise appropriately."""

    def test_incomplete_expression(self):
        with pytest.raises(SyntaxError):
            safe_eval("3 +", {})

    def test_unclosed_paren(self):
        with pytest.raises(SyntaxError):
            safe_eval("(3 + 4", {})

    def test_empty_expression(self):
        with pytest.raises(SyntaxError):
            safe_eval("", {})


class TestTypeErrors:
    """Test type mismatches in expressions."""

    def test_string_plus_int_in_names(self):
        """Adding a string name to an int via safe_eval."""
        # 'hello' is treated as a string, 5 as int; 'hello' + 5 is TypeError
        with pytest.raises(TypeError):
            safe_eval("x + 5", {"x": "hello"})

    def test_attribute_access_not_allowed(self):
        """Attribute access should raise ValueError."""
        with pytest.raises(ValueError, match="Attribute access not allowed"):
            safe_eval("x.upper()", {"x": "hello"})


class TestReplErrorHandling:
    """Test error handling at the REPL level."""

    def test_unknown_command(self, make_repl, capsys):
        """Unknown command should print an error."""
        repl = make_repl({})
        capsys.readouterr()
        repl.onecmd("xyzzy_not_a_command")
        out = capsys.readouterr().out
        assert "unknown" in out.lower() or "error" in out.lower()

    def test_calc_empty_expression_warns(self, make_repl, capsys):
        """calc with no expression should warn."""
        repl = make_repl({})
        capsys.readouterr()
        repl.onecmd("calc")
        out = capsys.readouterr().out
        # Should show help or usage
        assert "calc" in out.lower()

    def test_calc_invalid_expression_error(self, make_repl, capsys):
        """calc with bad expression should not crash."""
        repl = make_repl({})
        capsys.readouterr()
        repl.onecmd("calc bad = !@#$%")
        out = capsys.readouterr().out
        assert "error" in out.lower() or "failed" in out.lower()

    def test_assignment_with_bad_expression_stores_raw(self, make_repl, capsys):
        """If expression evaluation fails, raw value is stored."""
        repl = make_repl({})
        repl.onecmd("x = some random text")
        # The REPL falls back to storing raw string
        assert "x" in repl.ctx.script_vars

    def test_division_by_zero_in_repl(self, make_repl, capsys):
        """Division by zero in assignment surfaces ZeroDivisionError and
        leaves the target variable unset (failed expressions do not create
        destination vars)."""
        repl = make_repl({})
        capsys.readouterr()
        repl.onecmd("x = 1 / 0")
        out = capsys.readouterr().out
        assert "ZeroDivisionError" in out
        assert "x" not in repl.ctx.script_vars
