# SCPI Instrument Toolkit — Python API

Python drivers for controlling lab instruments — oscilloscopes, power supplies, multimeters, function generators, and more — over VISA (USB, GPIB, Serial, LAN).

---

## Install

```bash
pip install git+https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git
```

!!! note "Requires NI-VISA"
    Install [NI-VISA](https://www.ni.com/en/support/downloads/drivers/download.ni-visa.html) for USB and GPIB communication. The toolkit uses PyVISA with the `pyvisa-py` backend, but NI-VISA provides the best hardware compatibility.

---

## Quickstart

```python
from lab_instruments import HP_E3631A, HP_34401A

# Connect
psu = HP_E3631A("GPIB0::5::INSTR")
dmm = HP_34401A("GPIB0::22::INSTR")
psu.connect()
dmm.connect()

try:
    # Set 3.3 V on the +6 V channel
    psu.set_output_channel(HP_E3631A.Channel.POSITIVE_6V, 3.3, current_limit=0.1)
    psu.enable_output(True)

    # Measure with the DMM
    dmm.configure_dc_voltage()
    voltage = dmm.read()
    print(f"Measured: {voltage} V")
finally:
    psu.enable_output(False)
    psu.disconnect()
    dmm.disconnect()
```

---

## Supported Instruments

| Type | Models |
|------|--------|
| **Power Supplies** | [HP E3631A](instruments/psu/hp-e3631a.md), [Keysight EDU36311A](instruments/psu/keysight-edu36311a.md), [Matrix MPS-6010H](instruments/psu/matrix-mps6010h.md) |
| **Multimeters** | [HP 34401A](instruments/dmm/hp-34401a.md), [Keysight EDU34450A](instruments/dmm/keysight-edu34450a.md), [OWON XDM1041](instruments/dmm/owon-xdm1041.md) |
| **Function Generators** | [Keysight EDU33212A](instruments/awg/keysight-edu33212a.md), [BK Precision 4063](instruments/awg/bk-4063.md), [JDS6600](instruments/awg/jds6600.md) |
| **Oscilloscopes** | [Rigol DHO804](instruments/scope/rigol-dho804.md), [Tektronix MSO2024](instruments/scope/tektronix-mso2024.md), [Keysight DSOX1204G](instruments/scope/keysight-dsox1204g.md) |
| **Specialized** | [NI PXIe-4139 (SMU)](instruments/specialized/ni-pxie-4139.md), [TI EV2300 (I2C)](instruments/specialized/ti-ev2300.md) |

---

## What's in the Docs

| Page | What It Covers |
|------|---------------|
| [Getting Started](getting-started.md) | Prerequisites, VISA addresses, connection patterns, auto-discovery |
| [DeviceManager](instruments/device-manager.md) | Base class for all drivers — raw SCPI access |
| [Discovery](instruments/discovery.md) | Auto-detect connected instruments |
| [Examples](examples.md) | Full Python scripts for common lab workflows |
