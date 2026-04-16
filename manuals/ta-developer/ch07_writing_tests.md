# Chapter 7: Writing Tests

## Test Framework

The project uses pytest. All tests live in the `tests/` directory.

## Key Fixtures (tests/conftest.py)

### mock_visa_rm

Patches `pyvisa.ResourceManager` so no real VISA connection is needed:

    @pytest.fixture
    def mock_visa_rm(ensure_pyvisa_mocked):
        mock_instrument = MagicMock()
        mock_rm = MagicMock()
        mock_rm.open_resource.return_value = mock_instrument
        with patch("pyvisa.ResourceManager", return_value=mock_rm):
            yield mock_rm, mock_instrument

### Driver fixture pattern

Each driver has a fixture that returns (driver, mock_instrument):

    @pytest.fixture
    def hp_e3631a(mock_visa_rm):
        mock_rm, mock_instrument = mock_visa_rm
        from lab_instruments.src.hp_e3631a import HP_E3631A
        psu = HP_E3631A("GPIB::5::INSTR")
        psu.instrument = mock_instrument
        mock_instrument.reset_mock()
        return psu, mock_instrument

### make_repl

Creates a REPL instance wired to a given devices dict:

    @pytest.fixture
    def make_repl(monkeypatch):
        created = []
        def _make(devices):
            monkeypatch.setattr(_disc.InstrumentDiscovery, "scan",
                                lambda self, verbose=True: devices)
            repl = InstrumentRepl(register_lifecycle=False)
            repl._scan_thread.join(timeout=5.0)
            repl.devices = devices
            created.append(repl)
            return repl
        yield _make
        for repl in created:
            repl.close()

Usage:

    def test_something(self, make_repl):
        repl = make_repl({})              # no devices
        repl = make_repl({"psu1": mock})  # with mock PSU

## The State-Tracking Mock Pattern

Mocks must track state, not return constants:

**Wrong (constant mock):**

    mock_psu = MagicMock()
    mock_psu.measure_voltage.return_value = 5.0    # always returns 5.0!

**Right (state-tracking mock):**

    class MockPSU:
        def __init__(self):
            self._voltage = 0.0
            self._output = False

        def set_voltage(self, ch, v):
            self._voltage = float(v)

        def measure_voltage(self, ch=None):
            return self._voltage + random.uniform(-0.01, 0.01)

        def get_voltage_setpoint(self):
            return self._voltage

## One-Test-Per-Method Convention

Each test should verify one specific behavior:

    class TestSetVoltage:
        def test_sends_correct_scpi_command(self, hp_e3631a):
            psu, mi = hp_e3631a
            psu.set_voltage(HP_E3631A.Channel.POSITIVE_6V, 5.0)
            mi.write.assert_called()

        def test_updates_cache(self, hp_e3631a):
            psu, mi = hp_e3631a
            psu.set_voltage(HP_E3631A.Channel.POSITIVE_6V, 5.0)
            assert psu._voltage == 5.0

        def test_out_of_range_raises(self, hp_e3631a):
            psu, mi = hp_e3631a
            with pytest.raises(ValueError):
                psu.set_voltage(HP_E3631A.Channel.POSITIVE_6V, 100.0)

        def test_invalid_channel_raises(self, hp_e3631a):
            psu, mi = hp_e3631a
            with pytest.raises(ValueError):
                psu.set_voltage(99, 5.0)

## Monkeypatch for time.sleep

Always skip sleep in tests:

    def test_something(self, monkeypatch):
        import lab_instruments.src.my_driver as mod
        monkeypatch.setattr(mod.time, "sleep", lambda _: None)

This makes tests fast. Never use `from time import sleep` in driver code (see Driver Contract, Rule 2).

## Testing REPL Commands

Use capsys to capture output:

    def test_psu_set_success(self, make_repl, capsys):
        devices = {"psu1": MockHP_E3631A()}
        repl = make_repl(devices)
        repl.onecmd("scan")
        repl.onecmd("psu1 set 1 5.0")
        out = capsys.readouterr().out
        assert "5.0" in out
        assert "SUCCESS" in out

## Testing Variables and Calc

    def test_calc_stores_result(self, make_repl):
        repl = make_repl({})
        repl.onecmd("x = 5")
        repl.onecmd("y = 3")
        repl.onecmd("result = calc x + y")
        assert repl.ctx.script_vars["result"] == 8

## Coverage Targets

Target: 80%+ line coverage. Check with:

    pytest tests/ -v --cov=lab_instruments --cov-report=term-missing

The `--cov-report=term-missing` flag shows exactly which lines are not covered.

## Running Specific Tests

    pytest tests/test_hp_e3631a.py -v          # one file
    pytest tests/ -k "test_set_voltage"         # by name pattern
    pytest tests/ -x --tb=short                 # stop on first failure

## The @driver-test-writer Subagent

Use this Claude Code subagent to auto-generate tests for new driver methods:

    @driver-test-writer

It follows the project's state-tracking mock convention and generates one-test-per-method with proper fixtures.

## Test Organization

    tests/
    ├── conftest.py                          # shared fixtures
    ├── test_hp_e3631a.py                    # HP E3631A driver tests
    ├── test_rigol_dho804.py                 # Rigol DHO804 driver tests
    ├── test_tektronix_mso2024.py            # Tektronix MSO2024 tests
    ├── test_repl_variables.py               # variable/assignment tests
    ├── test_repl_comprehensive.py           # arithmetic, types, logging
    ├── test_variable_type_edge_cases.py     # type system edge cases
    ├── test_calc_logging_arithmetic.py      # calc + log integration
    ├── test_instrument_measurement_workflows.py  # multi-instrument
    └── ...
