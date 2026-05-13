# Chapter 1: Architecture Overview

## The 5-Layer Stack

The toolkit is built in five layers, from hardware at the bottom to user interfaces at the top:

    Layer 4: Frontends (CLI REPL, Python API, LabVIEW bridge)
    Layer 3: REPL layer (ReplContext, ScriptEngine, CommandHandlers)
    Layer 2: Driver classes (HP_E3631A, Rigol_DHO804, etc.)
    Layer 1: Transport libraries (pyvisa, ctypes, nidcpower)
    Layer 0: Hardware & OS interfaces (NI-VISA, HID, NI-DCPower)

Each layer only talks to the one directly below it. Users interact with Layer 4, and commands flow down through the stack to hardware.

## How a Command Flows

When a user types `psu set 1 5.0`, here is exactly what happens:

### 1. Shell receives input

`InstrumentRepl.do_psu("set 1 5.0")` is called by Python's `cmd.Cmd` framework.

File: `lab_instruments/repl/shell.py`, the `do_psu` method.

### 2. Device resolution

The shell resolves "psu" to a specific device name (e.g., "psu1"):

    dev_name = self.ctx.registry.resolve_type("psu")
    dev = self.ctx.registry.get_device(dev_name)

File: `lab_instruments/repl/device_registry.py`

### 3. Command handler dispatch

The shell delegates to the PSU command handler:

    self._psu_cmd.execute("set 1 5.0", dev, dev_name)

File: `lab_instruments/repl/commands/psu.py`

### 4. Argument parsing

The command handler parses "set 1 5.0" into command="set", channel=1, voltage=5.0. It resolves the channel number to the driver's channel enum.

### 5. Driver method call

The handler calls the driver method:

    dev.set_voltage(channel_enum, 5.0)

File: `lab_instruments/src/hp_e3631a.py`

### 6. SCPI command generation

The driver formats the SCPI command:

    self.send_command("APPL P6V,5.0,MAX")

### 7. PyVISA transport

DeviceManager.send_command() sends the string to the instrument:

    self.instrument.write("APPL P6V,5.0,MAX")

File: `lab_instruments/src/device_manager.py`

### 8. Hardware response

The instrument receives the SCPI string over USB/GPIB and sets its output to 5.0 V.

## Key Components

### ReplContext (`lab_instruments/repl/context.py`)

Shared state for the entire REPL session:

- `script_vars` -- variable storage (dict[str, Any])
- `measurements` -- MeasurementStore for logged data
- `registry` -- DeviceRegistry managing connected instruments
- `scripts` -- loaded script definitions
- Error flags, mode tracking, script state

### DeviceRegistry (`lab_instruments/repl/device_registry.py`)

Manages the mapping between friendly names ("psu1", "dmm1") and driver instances. Handles:

- Registering discovered devices
- Resolving type-based names ("psu" -> "psu1")
- The "active" instrument selection (`use psu1`)

### DeviceManager (`lab_instruments/src/device_manager.py`)

Base class for all SCPI instrument drivers. Provides:

- `connect()` / `disconnect()` -- VISA session management
- `send_command(cmd)` -- write a SCPI command
- `query(cmd)` -- write and read response
- `get_identity()` -- `*IDN?` query
- `clear_status()` -- `*CLS` command
- `reset()` -- `*RST` command

### InstrumentDiscovery (`lab_instruments/src/discovery.py`)

Auto-detects instruments by:

1. Scanning all VISA resources
2. Querying `*IDN?` on each
3. Matching the model string against MODEL_MAP
4. Instantiating the correct driver class
5. Assigning a friendly name ("psu1", "dmm1", etc.)

### ScriptEngine (`lab_instruments/repl/script_engine/`)

Handles script execution:

- `expander.py` -- expands for/repeat loops and variable substitutions at compile time
- `runner.py` -- executes expanded lines, handles while/if at runtime
- `variables.py` -- variable resolution utilities

## Three Instrument Families

Not all instruments use VISA. The toolkit supports three transport mechanisms:

| Family | Transport | Library | Examples |
|--------|-----------|---------|----------|
| SCPI via VISA | USB/GPIB/Serial | pyvisa | PSU, DMM, AWG, Scope |
| USB HID | HID reports | ctypes | TI EV2300 |
| NI-DCPower | PXIe bus | nidcpower | NI PXIe-4139 |

Each family has its own base class or direct implementation, but all present the same interface to the REPL layer.

## Where Mocks Fit

Mock instruments (`lab_instruments/mock_instruments.py`) replace Layer 2 drivers. They implement the same methods but store state internally instead of talking to hardware. The REPL, command handlers, and script engine cannot tell the difference -- this is how `--mock` mode works.
