# Chapter 3: Adding a New Instrument Driver

This chapter walks through adding support for a new instrument from scratch.

## Step-by-Step Checklist

1. Create the driver file in `lab_instruments/src/`
2. Implement the SCPI driver contract
3. Register the instrument in `discovery.py`
4. Create a mock in `mock_instruments.py`
5. Add REPL command support in `commands/`
6. Write tests
7. Add documentation
8. Open a PR

## Step 1: Create the Driver File

Create `lab_instruments/src/my_new_instrument.py`:

    from lab_instruments.src.device_manager import DeviceManager


    class MyNewInstrument(DeviceManager):
        """Driver for the My New Instrument model XYZ."""

        # Channel mapping (if multi-channel)
        CHANNEL_FROM_NUMBER = {
            1: "CH1",
            2: "CH2",
        }

        # Allowed values for enum-type parameters
        MODES_ALLOWLIST = frozenset({"MODE1", "MODE2", "MODE3"})

        def __init__(self, resource_name: str):
            super().__init__(resource_name)
            self._voltage = 0.0
            self._output = False
            self._mode = "MODE1"

        def __enter__(self):
            self.disable_all_channels()
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            self.disable_all_channels()

        def connect(self):
            super().connect()
            self.clear_status()

        # --- Setters (always validate, always update cache) ---

        def set_voltage(self, channel: int, voltage: float):
            if not 0 <= voltage <= 30.0:
                raise ValueError(f"Voltage {voltage} out of range [0, 30.0]")
            ch_str = self.CHANNEL_FROM_NUMBER.get(channel)
            if ch_str is None:
                raise ValueError(f"Invalid channel: {channel}")
            self.send_command(f"VOLT {voltage}")
            self._voltage = voltage   # update cache atomically

        def set_mode(self, mode: str):
            mode = mode.upper()
            if mode not in self.MODES_ALLOWLIST:
                raise ValueError(f"Invalid mode '{mode}'. Allowed: {self.MODES_ALLOWLIST}")
            self.send_command(f"MODE {mode}")
            self._mode = mode

        # --- Getters (never hardcode, always return self._attr) ---

        def get_voltage_setpoint(self) -> float:
            return self._voltage       # return cached value

        def get_mode(self) -> str:
            return self._mode

        # --- Measurements (always use query, not write) ---

        def measure_voltage(self) -> float:
            response = self.query("MEAS:VOLT?")
            return float(response)

        def measure_current(self) -> float:
            response = self.query("MEAS:CURR?")
            return float(response)

        # --- Output control ---

        def enable_output(self, enabled: bool = True):
            self.send_command(f"OUTP {'ON' if enabled else 'OFF'}")
            self._output = enabled

        def disable_all_channels(self):
            self.send_command("OUTP OFF")
            self._output = False

        # --- Error handling (required by contract) ---

        def get_error(self) -> str:
            return self.query("SYST:ERR?")

## Step 2: Register in Discovery

Edit `lab_instruments/src/discovery.py`:

    # In MODEL_MAP, add:
    "XYZ123": MyNewInstrument,

    # In NAME_MAP, add:
    "XYZ123": "mytype",    # e.g., "psu", "dmm", "scope", etc.

The discovery system queries `*IDN?` on each VISA resource and matches the model substring against MODEL_MAP.

## Step 3: Create a Mock

In `lab_instruments/mock_instruments.py`, add a mock class:

    class MockMyNewInstrument(MockBase):
        def __init__(self):
            super().__init__()
            self._voltage = 0.0
            self._output = False
            self._mode = "MODE1"

        def set_voltage(self, channel, voltage):
            self._voltage = float(voltage)

        def get_voltage_setpoint(self):
            return self._voltage

        def measure_voltage(self, ch=None):
            return round(self._voltage + random.uniform(-0.02, 0.02), 6)

        def measure_current(self, ch=None):
            return round(random.uniform(0.001, 0.5), 6)

        def enable_output(self, state=True):
            self._output = bool(state)

        def disable_all_channels(self):
            self._output = False

        def set_mode(self, mode):
            self._mode = mode

        def get_mode(self):
            return self._mode

        def get_error(self):
            return "0,No error"

Key rules for mocks:
- Track state (do not return constants)
- Add realistic jitter to measurements (random.uniform)
- Return exact values for setpoint getters
- Implement all methods the driver has

Add the mock to `get_mock_devices()`:

    def get_mock_devices(verbose=True):
        devices = {
            ...
            "mytype1": MockMyNewInstrument(),
        }

## Step 4: Add REPL Commands

If your instrument fits an existing type (PSU, DMM, scope, AWG), the existing command handler may work. If it is a new type, create `lab_instruments/repl/commands/mytype.py`:

    from .base import BaseCommand

    class MyTypeCommand(BaseCommand):
        def execute(self, arg, dev, dev_name):
            args = self.parse_args(arg)
            if not args:
                self.print_colored_usage([...])
                return
            cmd = args[0].lower()
            rest = args[1:]

            if cmd == "set":
                self._handle_set(rest, dev, dev_name)
            elif cmd == "meas":
                self._handle_meas(rest, dev, dev_name)
            else:
                self.error(f"Unknown mytype command: {cmd}")

        def _handle_set(self, args, dev, dev_name):
            ...

        def _handle_meas(self, args, dev, dev_name):
            ...

Register in shell.py:

    # In __init__:
    self._mytype_cmd = MyTypeCommand(self.ctx)

    # Add do_mytype method:
    def do_mytype(self, arg):
        # ... resolve device, delegate to handler

## Step 5: Write Tests

See Chapter 7 for the full testing guide. At minimum:

    # tests/test_my_new_instrument.py
    class TestSetVoltage:
        def test_set_voltage_sends_correct_command(self, fixture):
            dev, mock_instr = fixture
            dev.set_voltage(1, 5.0)
            mock_instr.write.assert_called_with("VOLT 5.0")

        def test_set_voltage_out_of_range_raises(self, fixture):
            dev, mock_instr = fixture
            with pytest.raises(ValueError):
                dev.set_voltage(1, 100.0)

## Step 6: Add Documentation

1. Create `docs/mytype.md` with command reference
2. Add to `mkdocs.yml` nav section
3. Add to `docs/instruments.md` supported models table
4. Run `mkdocs build` to verify
5. Deploy with `mkdocs gh-deploy --force`

## Step 7: Open a PR

    git checkout -b feature/add-mytype-driver
    git add lab_instruments/ tests/ docs/ mkdocs.yml
    git commit -m "Add MyNewInstrument driver with tests and docs"
    git push -u origin feature/add-mytype-driver
    gh pr create --base dev/nightly

Run `@scpi-contract-reviewer` before opening the PR to catch contract violations.
