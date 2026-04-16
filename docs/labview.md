# LabVIEW Bridge

Call the toolkit's Python instrument drivers from LabVIEW using the built-in **Python Node** (LabVIEW 2018+).

---

## Prerequisites

| Requirement | Notes |
|---|---|
| **LabVIEW 2018+** | Python Node was introduced in LabVIEW 2018 |
| **Python 3.10+** | Must match LabVIEW bitness (64-bit LabVIEW needs 64-bit Python) |
| **scpi-instrument-toolkit** | `pip install git+https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git` |
| **NI-VISA** | For USB/GPIB/LAN instruments |

!!! warning "Python must be on your PATH"
    When installing Python, check the box **"Add Python to PATH"**. LabVIEW uses the system PATH to find the Python interpreter. If Python is not on PATH, the Python Node will fail silently.

!!! warning "Bitness must match"
    64-bit LabVIEW requires 64-bit Python. 32-bit LabVIEW requires 32-bit Python. A mismatch will cause the Python Node to fail with no useful error message.

---

## Step 1: Find the Bridge Module Path

There are two ways to get the path, depending on how you installed the toolkit.

### Option A: pip install (installed from PyPI or git)

Open a terminal and run:

```bash
python -c "from lab_instruments.src import labview_bridge; print(labview_bridge.__file__)"
```

Copy the full path. Example:

```
C:\Users\you\AppData\Local\Programs\Python\Python312\Lib\site-packages\lab_instruments\src\labview_bridge.py
```

### Option B: git clone (repo on disk)

Use the top-level shim at the repository root instead:

```
C:\path\to\scpi-instrument-toolkit\labview_bridge.py
```

This file re-exports every function from the real bridge and is the recommended target for git-clone setups.

!!! note "Either path works"
    Both files expose identical function names. The only difference is the path you paste into the Python Node's module path terminal.

---

## Step 2: Understand the Python Node Pattern

LabVIEW's Python integration uses a **"railroad track" pattern** with three palette items found under **Connectivity > Python** in the Functions palette:

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Open Python  │────>│ Python Node  │────>│ Python Node  │────>│ Close Python │
│   Session    │     │ (open_psu)   │     │ (set_voltage) │     │   Session    │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
     session refnum passes through ALL nodes like a railroad track
```

### The Three Palette Items

1. **Open Python Session** — Creates a Python interpreter session
    - Input: Python version number (use **3** for Python 3.x)
    - Output: A **session refnum** (reference wire) — thread this through all your Python Nodes

2. **Python Node** — Calls one Python function
    - Has built-in terminals for: **session refnum**, **module path** (Path type), and **function name** (String)
    - **Resize the node** (drag the bottom edge down) to add input terminals for the function's parameters
    - Parameters are **positional** — the order you wire them must match the Python function signature
    - Has **one output terminal** on the right — right-click it to set the expected return type
    - Has **error in/out** terminals along the bottom

3. **Close Python Session** — Shuts down the Python interpreter
    - Always close the session when your VI is done

!!! tip "Session persistence is critical"
    The bridge stores instrument connections in a Python module-level cache. All Python Nodes that share the same session refnum share the same cache. This means `open_psu()` in one node and `psu_set_voltage()` in the next node can find each other's data — **as long as they share the same session wire**.

---

## Step 3: Tutorial — Set PSU to 5V and Read DMM

This tutorial uses instruments from the ESET-453 lab bench:

- **HP E3631A** PSU on `GPIB0::1::INSTR`
- **HP 34401A** DMM on `GPIB0::22::INSTR`

### 3.1 Create a New VI

Open LabVIEW and create a new blank VI (**File > New VI**). Switch to the **Block Diagram** window (Ctrl+E).

### 3.2 Place Open Python Session

1. Right-click the block diagram to open the **Functions palette**
2. Navigate to **Connectivity > Python**
3. Place **Open Python Session** on the left side of your diagram
4. Right-click the **version** input terminal and select **Create > Constant**
5. Set the constant value to **3** (for Python 3.x)

### 3.3 Place the First Python Node — Open the PSU

1. From the same **Connectivity > Python** palette, place a **Python Node** to the right of Open Python Session
2. Wire the **session refnum** output from Open Python Session into the Python Node's session input (top-left terminal)
3. Wire the **module path** terminal:
    - Right-click it and select **Create > Constant**
    - This creates a **Path** constant — paste your module path from Step 1
4. Wire the **function name** terminal:
    - Right-click it and select **Create > Constant**
    - Type: `open_psu`
5. **Add function parameters** — drag the bottom edge of the Python Node down to expose **2 additional input terminals**
6. Wire the first parameter:
    - Right-click the terminal and select **Create > Constant**
    - This creates a String constant — type: `GPIB0::1::INSTR`
7. Wire the second parameter:
    - Right-click > Create > Constant
    - Type: `HP_E3631A`
8. **Set the output type** — right-click the output terminal on the right side, select the return type as **String**
    - This output will contain the instrument ID (e.g. `"psu_1"`)

### 3.4 Place Python Node — Set Voltage to 5V on Channel 2

1. Place another **Python Node** to the right
2. Wire the **session refnum** through from the previous node
3. Wire the same **module path** (you can branch the wire or create another constant)
4. Set **function name** to: `psu_set_voltage`
5. Drag the bottom edge down to expose **3 input terminals**
6. Wire the inputs in order:
    - **instrument_id** (String) — wire from the output of the `open_psu` node
    - **channel** (I32) — create a Numeric Constant, set to `2` (the +25V channel)
    - **voltage** (Double) — create a Numeric Constant, set to `5.0`
7. Set output type to **String** (returns `"OK"`)

### 3.5 Place Python Node — Enable PSU Output

1. Place another Python Node
2. Wire session refnum and module path
3. Set function name to: `psu_enable_output`
4. Expand to **2 input terminals**:
    - **instrument_id** (String) — wire from the `open_psu` output
    - **enabled** (Boolean) — create a Boolean Constant, set to **True**
5. Set output type to String

### 3.6 Place Python Node — Open the DMM

1. Place another Python Node
2. Wire session refnum and module path
3. Set function name to: `open_dmm`
4. Expand to **2 input terminals**:
    - `GPIB0::22::INSTR` (String constant)
    - `HP_34401A` (String constant)
5. Set output type to **String** (returns DMM instrument ID like `"dmm_2"`)

### 3.7 Place Python Node — Measure DC Voltage

1. Place another Python Node
2. Wire session refnum and module path
3. Set function name to: `dmm_measure_dc_voltage`
4. Expand to **1 input terminal**:
    - **instrument_id** (String) — wire from the `open_dmm` output
5. Set output type to **Double** (returns the measured voltage)
6. Right-click the output terminal and select **Create > Indicator** — this puts a numeric indicator on the front panel to display the reading

### 3.8 Clean Up — Close Instruments and Session

1. Place a Python Node for `close_instrument` with the PSU's instrument_id
2. Place another Python Node for `close_instrument` with the DMM's instrument_id
3. Place **Close Python Session** (from the Connectivity > Python palette) at the end
4. Wire the session refnum through to Close Python Session

### 3.9 Wire Error Clusters

Every Python Node has **error in** (bottom-left) and **error out** (bottom-right) terminals. Wire them in series through all your nodes:

```
Open Session → Node 1 → Node 2 → ... → Close Session
  error out ──> error in ──> error in ──> error in
```

This ensures that if any node fails (e.g. instrument not found), subsequent nodes are skipped and you get the error message.

### 3.10 Run the VI

1. Switch to the **Front Panel** (Ctrl+E)
2. Click **Run** (the arrow button) or press Ctrl+R
3. The numeric indicator should show the voltage reading from your DMM

### Complete Block Diagram Layout

```
┌─────────┐   ┌───────────┐   ┌──────────────┐   ┌──────────────┐   ┌───────────┐   ┌──────────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
│  Open   │──>│ open_psu  │──>│psu_set_voltage│──>│psu_enable_   │──>│ open_dmm  │──>│dmm_measure_  │──>│ close   │──>│ close   │──>│ Close   │
│ Python  │   │           │   │              │   │  output      │   │           │   │ dc_voltage   │   │ PSU     │   │ DMM     │   │ Python  │
│ Session │   │GPIB0::1   │   │ id, 2, 5.0  │   │ id, True     │   │GPIB0::22  │   │     id       │   │         │   │         │   │ Session │
│  v=3    │   │HP_E3631A  │   │   -> "OK"    │   │  -> "OK"     │   │HP_34401A  │   │  -> 5.003    │   │ -> "OK" │   │ -> "OK" │   │         │
└─────────┘   └───────────┘   └──────────────┘   └──────────────┘   └───────────┘   └──────────────┘   └─────────┘   └─────────┘   └─────────┘
session refnum ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════>
error cluster  ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────>
```

---

## Step 4: Tutorial — EV2300 I2C Register Read

This example opens the EV2300 and reads the SYS_STAT register (0x00) from a BQ76920 at I2C address 0x08.

### Block Diagram

1. **Open Python Session** (version = 3)
2. **Python Node** — `open_ev2300`
    - 1 input: `""` (empty string = auto-detect)
    - Output type: String (returns `"ev2300_1"`)
3. **Python Node** — `ev2300_read_byte`
    - 3 inputs: instrument_id (String), `8` (I32 = I2C address 0x08), `0` (I32 = register 0x00)
    - Output type: **I32** (returns the register value, e.g. `0`)
    - Create an Indicator on the output to display the value
4. **Python Node** — `close_instrument`
5. **Close Python Session**

---

## Data Type Mapping

| Python Type | LabVIEW Type | Example |
|---|---|---|
| `str` | String | Instrument IDs, JSON results, `"OK"` |
| `int` | I32 | Channel numbers, register addresses, byte values |
| `float` | Double | Voltages, currents, measurements |
| `bool` | Boolean | Enable/disable flags |

Complex data (instrument lists, device info) is returned as **JSON strings**. Parse them in LabVIEW using the Flatten/Unflatten from JSON functions or a string parser.

---

## Function Reference

### Discovery

| Function | Signature | Returns |
|---|---|---|
| `discover_instruments` | `() -> str` | JSON: `{"psu": "HP_E3631A", ...}` |
| `list_available_drivers` | `() -> str` | JSON list of driver name strings |
| `list_open_instruments` | `() -> str` | JSON: `{"psu_1": "HP_E3631A", ...}` |
| `list_visa_resources` | `() -> str` | JSON list of VISA resource strings |

### Connection

| Function | Signature | Returns |
|---|---|---|
| `open_instrument` | `(visa_address: str, driver_name: str) -> str` | instrument ID |
| `open_psu` | `(visa_address: str, driver_name: str) -> str` | instrument ID (validates PSU) |
| `open_dmm` | `(visa_address: str, driver_name: str) -> str` | instrument ID (validates DMM) |
| `open_awg` | `(visa_address: str, driver_name: str) -> str` | instrument ID (validates AWG) |
| `open_scope` | `(visa_address: str, driver_name: str) -> str` | instrument ID (validates Scope) |
| `open_smu` | `(visa_address: str, driver_name: str) -> str` | instrument ID (validates SMU) |
| `open_ev2300` | `(resource_name: str) -> str` | instrument ID (pass `""` to auto-detect) |
| `close_instrument` | `(instrument_id: str) -> str` | `"OK"` |
| `close_all` | `() -> str` | `"OK"` |

### Power Supply (PSU)

| Function | Signature | Returns |
|---|---|---|
| `psu_set_voltage` | `(id: str, channel: int, voltage: float) -> str` | `"OK"` |
| `psu_set_current_limit` | `(id: str, channel: int, current: float) -> str` | `"OK"` |
| `psu_set_output_channel` | `(id: str, channel: int, voltage: float, current_limit: float) -> str` | `"OK"` |
| `psu_enable_output` | `(id: str, enabled: bool) -> str` | `"OK"` |
| `psu_measure_voltage` | `(id: str, channel: int) -> float` | Measured volts |
| `psu_measure_current` | `(id: str, channel: int) -> float` | Measured amps |
| `psu_disable_all` | `(id: str) -> str` | `"OK"` |

### Digital Multimeter (DMM)

| Function | Signature | Returns |
|---|---|---|
| `dmm_measure_dc_voltage` | `(id: str) -> float` | Volts DC |
| `dmm_measure_ac_voltage` | `(id: str) -> float` | Volts AC |
| `dmm_measure_dc_current` | `(id: str) -> float` | Amps DC |
| `dmm_measure_resistance_2w` | `(id: str) -> float` | Ohms (2-wire) |
| `dmm_measure_resistance_4w` | `(id: str) -> float` | Ohms (4-wire) |
| `dmm_measure_frequency` | `(id: str) -> float` | Hz |
| `dmm_measure_diode` | `(id: str) -> float` | Volts (forward) |

### Function Generator (AWG)

| Function | Signature | Returns |
|---|---|---|
| `awg_set_waveform` | `(id: str, channel: int, wave_type: str, frequency: float, amplitude: float, offset: float) -> str` | `"OK"` |
| `awg_set_frequency` | `(id: str, channel: int, frequency: float) -> str` | `"OK"` |
| `awg_set_amplitude` | `(id: str, channel: int, amplitude: float) -> str` | `"OK"` |
| `awg_set_dc_output` | `(id: str, channel: int, voltage: float) -> str` | `"OK"` |
| `awg_enable_output` | `(id: str, channel: int, enabled: bool) -> str` | `"OK"` |
| `awg_disable_all` | `(id: str) -> str` | `"OK"` |

### Oscilloscope

| Function | Signature | Returns |
|---|---|---|
| `scope_run` | `(id: str) -> str` | `"OK"` |
| `scope_stop` | `(id: str) -> str` | `"OK"` |
| `scope_single` | `(id: str) -> str` | `"OK"` |
| `scope_set_vertical_scale` | `(id: str, channel: int, volts_per_div: float) -> str` | `"OK"` |
| `scope_set_timebase` | `(id: str, time_per_div: float) -> str` | `"OK"` |
| `scope_measure_vpp` | `(id: str, channel: int) -> float` | Volts peak-to-peak |
| `scope_measure_frequency` | `(id: str, channel: int) -> float` | Hz |
| `scope_measure_vrms` | `(id: str, channel: int) -> float` | Volts RMS |

### EV2300 (I2C Bridge)

| Function | Signature | Returns |
|---|---|---|
| `ev2300_read_byte` | `(id: str, i2c_addr: int, register: int) -> int` | Byte value (0-255) |
| `ev2300_write_byte` | `(id: str, i2c_addr: int, register: int, value: int) -> str` | `"OK"` |
| `ev2300_read_word` | `(id: str, i2c_addr: int, register: int) -> int` | 16-bit value |
| `ev2300_write_word` | `(id: str, i2c_addr: int, register: int, value: int) -> str` | `"OK"` |
| `ev2300_read_block` | `(id: str, i2c_addr: int, register: int) -> str` | JSON list of ints |
| `ev2300_write_block` | `(id: str, i2c_addr: int, register: int, data_json: str) -> str` | `"OK"` |
| `ev2300_get_device_info` | `(id: str) -> str` | JSON device info |

### SMU (Source Measure Unit)

| Function | Signature | Returns |
|---|---|---|
| `smu_set_voltage_mode` | `(id: str, voltage: float, current_limit: float) -> str` | `"OK"` |
| `smu_set_current_mode` | `(id: str, current: float, voltage_limit: float) -> str` | `"OK"` |
| `smu_enable_output` | `(id: str, enabled: bool) -> str` | `"OK"` |
| `smu_measure_voltage` | `(id: str) -> float` | Volts |
| `smu_measure_current` | `(id: str) -> float` | Amps |

### Generic / Utility

| Function | Signature | Returns |
|---|---|---|
| `send_scpi` | `(id: str, command: str) -> str` | `"OK"` |
| `query_scpi` | `(id: str, command: str) -> str` | Response string |
| `reset_instrument` | `(id: str) -> str` | `"OK"` |
| `get_instrument_type` | `(id: str) -> str` | `"psu"`, `"dmm"`, `"awg"`, `"scope"`, `"smu"`, `"ev2300"` |
| `get_version` | `() -> str` | Package version string |

---

## PSU Channel Mapping

The bridge normalizes channel numbers (1, 2, 3) across all PSU drivers:

| Channel | HP E3631A | EDU36311A | MPS-6010H | PXIe-4139 |
|---|---|---|---|---|
| 1 | +6V (P6V) | +6V (P6V) | *(single channel)* | *(single channel)* |
| 2 | +25V (P25V) | +30V (P30V) | --- | --- |
| 3 | -25V (N25V) | -30V (N30V) | --- | --- |

Single-channel PSUs (MPS-6010H, PXIe-4139) ignore the channel argument.

---

## Supported Drivers

| Driver Name | Instrument | Type |
|---|---|---|
| `HP_E3631A` | HP E3631A Triple Output PSU | PSU |
| `EDU36311A` | Keysight EDU36311A Triple Output PSU | PSU |
| `MPS6010H` | MATRIX MPS-6010H-1C (60V/10A) | PSU |
| `HP_34401A` | HP/Agilent 34401A DMM | DMM |
| `EDU34450A` | Keysight EDU34450A DMM | DMM |
| `XDM1041` | Owon XDM1041 DMM | DMM |
| `EDU33212A` | Keysight EDU33212A AWG | AWG |
| `BK_4063` | BK Precision 4063 AWG | AWG |
| `JDS6600` | JDS6600/Seesii DDS Generator | AWG |
| `MSO2024` | Tektronix MSO2024 Oscilloscope | Scope |
| `DHO804` | Rigol DHO804 Oscilloscope | Scope |
| `DSOX1204G` | Keysight DSOX1204G Oscilloscope | Scope |
| `PXIe_4139` | NI PXIe-4139 SMU | SMU |
| `EV2300` | TI EV2300 USB-to-I2C Adapter | EV2300 |

---

## Error Handling

Python exceptions automatically become LabVIEW error clusters when you wire the error terminals. Common errors:

| Python Exception | Meaning |
|---|---|
| `KeyError` | Invalid instrument ID (not open or already closed) |
| `TypeError` | Wrong instrument type (e.g. calling `psu_set_voltage` on a DMM) |
| `ValueError` | Invalid parameter (bad channel number, out-of-range voltage) |
| `RuntimeError` | EV2300 I2C communication failure |
| `ConnectionError` | Instrument not connected |

Wire the **error in/out** clusters through all your Python Nodes in series. If any node throws an exception, subsequent nodes are skipped and the error propagates to the end of your chain.

---

## Troubleshooting

**ImportError: attempted relative import with no known parent package**

This error means LabVIEW loaded `labview_bridge.py` as a standalone script instead of as part of the `lab_instruments` package, causing all `from .xyz import` statements to fail.

Fix: make sure the version of the toolkit installed is **1.0.5 or later** (the file was patched to handle standalone loads). Upgrade with:

```powershell
pip install --upgrade git+https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git
```

If you are using a git clone and cannot upgrade, switch the Python Node's module path to the top-level shim at the repository root (`labview_bridge.py`) instead of the buried path in `lab_instruments/src/`.

---

**Python Node shows "Python not found" or fails silently**

- Verify Python is on your system PATH: open a terminal and type `python --version`
- Verify bitness matches: 64-bit LabVIEW needs 64-bit Python
- Try setting the version input on Open Python Session to `3` (not `3.10` or `3.12`)

**Instrument not found / KeyError on second node**

- Make sure all Python Nodes share the **same session refnum wire** from Open Python Session
- If each node opens its own session, the module cache is separate and `psu_set_voltage` can't find the instrument opened by `open_psu`

**"No module named lab_instruments"**

- The toolkit is not installed in the Python that LabVIEW is using
- Run `pip install git+https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git` in the same Python installation

**Raw SCPI escape hatch**

If the bridge doesn't have a wrapper for your specific command, use `send_scpi()` / `query_scpi()` to send any SCPI command directly to the instrument.
