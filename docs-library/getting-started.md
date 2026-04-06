# Getting Started

This guide covers how to use the `lab_instruments` Python package to control lab instruments programmatically.

---

## Prerequisites

1. **Python 3.10+**
2. **NI-VISA** — Download from [ni.com](https://www.ni.com/en/support/downloads/drivers/download.ni-visa.html). Required for USB and GPIB communication.
3. **PyVISA** — Installed automatically with the package.

---

## Installation

```bash
pip install git+https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git
```

For optional dependencies:

```bash
# NI PXIe-4139 SMU support
pip install nidcpower

# TI EV2300 USB-to-I2C support (Windows: automatic, Linux/macOS: pip install hidapi)
```

---

## Finding Your VISA Address

Every instrument needs a VISA resource string to connect. Common formats:

| Interface | Format | Example |
|-----------|--------|---------|
| USB | `USB0::VENDOR::PRODUCT::SERIAL::INSTR` | `USB0::0x2A8D::0x1301::MY12345678::INSTR` |
| GPIB | `GPIB0::ADDRESS::INSTR` | `GPIB0::22::INSTR` |
| Serial | `ASRL{N}::INSTR` | `ASRL3::INSTR` |
| LAN | `TCPIP0::IP::INSTR` | `TCPIP0::192.168.1.100::INSTR` |

To list connected instruments:

```python
import pyvisa
rm = pyvisa.ResourceManager()
print(rm.list_resources())
# ('USB0::0x2A8D::0x1301::MY12345678::INSTR', 'GPIB0::22::INSTR', ...)
```

Or use the toolkit's auto-discovery:

```python
from lab_instruments import find_all

instruments = find_all()
for name, inst in instruments.items():
    print(f"{name}: {type(inst).__name__} at {inst.resource_name}")
```

---

## Basic Pattern

All drivers follow the same lifecycle: **instantiate, connect, use, disconnect**.

```python
from lab_instruments import HP_34401A

dmm = HP_34401A("GPIB0::22::INSTR")
dmm.connect()

try:
    dmm.configure_dc_voltage()
    voltage = dmm.read()
    print(f"Measured: {voltage} V")
finally:
    dmm.disconnect()
```

---

## Context Managers

All drivers support `with` statements for automatic cleanup:

```python
from lab_instruments import HP_E3631A

psu = HP_E3631A("GPIB0::5::INSTR")
psu.connect()

with psu:
    psu.set_output_channel("positive_6_volts_channel", 3.3, current_limit=0.1)
    psu.enable_output(True)
    # ... do work ...
# Output is automatically disabled when exiting the `with` block
```

!!! note
    Context managers handle **safe shutdown** (disabling outputs, zeroing setpoints). You still need to call `connect()` before entering the `with` block and `disconnect()` after.

---

## Imports

You can import directly from the top-level package:

```python
from lab_instruments import HP_E3631A, HP_34401A, Rigol_DHO804
```

Or from the specific module:

```python
from lab_instruments.src.hp_e3631a import HP_E3631A
```

Both forms are equivalent. The top-level import is recommended.

---

## Auto-Discovery

The `InstrumentDiscovery` class scans all connected VISA resources and returns typed driver instances:

```python
from lab_instruments import InstrumentDiscovery

discovery = InstrumentDiscovery()
instruments = discovery.scan()

for name, inst in instruments.items():
    print(f"{name}: {type(inst).__name__}")
# psu1: HP_E3631A
# dmm1: HP_34401A
# scope1: Rigol_DHO804
```

Or use the shorthand:

```python
from lab_instruments import find_all

instruments = find_all()
```

See [Discovery](instruments/discovery.md) for details.

---

## Error Handling

Drivers raise standard Python exceptions:

```python
import pyvisa
from lab_instruments import HP_34401A

dmm = HP_34401A("GPIB0::22::INSTR")

try:
    dmm.connect()
except pyvisa.VisaIOError as e:
    print(f"Connection failed: {e}")

# After connecting, check the instrument error queue:
error = dmm.get_error()
print(error)  # '+0,"No error"'
```

| Exception | When |
|-----------|------|
| `pyvisa.VisaIOError` | Connection failure, timeout, communication error |
| `ConnectionError` | Method called before `connect()` |
| `ValueError` | Invalid parameter (wrong channel, out-of-range value) |

---

## Base Class: DeviceManager

All VISA-based drivers inherit from `DeviceManager`, which provides raw SCPI access. If your instrument isn't supported, you can use `DeviceManager` directly:

```python
from lab_instruments import DeviceManager

inst = DeviceManager("GPIB0::10::INSTR")
inst.connect()

# Send raw SCPI commands
inst.send_command("*RST")
response = inst.query("*IDN?")
print(response)

inst.disconnect()
```

See [DeviceManager](instruments/device-manager.md) for the full reference.
