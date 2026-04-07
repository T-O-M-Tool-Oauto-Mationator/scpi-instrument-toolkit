# SCPI Instrument Toolkit

Python REPL for controlling lab instruments — oscilloscopes, power supplies, multimeters, and function generators — over VISA (USB, GPIB, Serial).

---

## Quick Start

### 1. Install

```bash
pip install git+https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git
```

> **Requires** [NI-VISA](https://www.ni.com/en/support/downloads/drivers/download.ni-visa.html) for USB and GPIB instruments.

### 2. Launch

```bash
scpi-repl           # auto-discovers connected instruments
scpi-repl --mock    # simulate instruments (no hardware needed)
```

!!! tip "scpi-repl not recognized?"
    Run `python -m lab_instruments` once. On standard Windows the toolkit will automatically add the Scripts folder to your PATH — open a new terminal and `scpi-repl` will work.

    On **managed machines (TAMU VOAL and similar)** where registry edits are blocked, use the module form as your permanent launch method:
    ```powershell
    python -m lab_instruments
    python -m lab_instruments --mock
    ```
    See [Troubleshooting](troubleshooting.md) for a session-only PATH fix and other tips.

!!! warning "One connection at a time"
    Instrument connections are exclusive. Only one program can hold the connection to a device at a time.

    - You cannot run the REPL and a Python script against the same instrument simultaneously.
    - You cannot have the REPL or a Python script connected while BQStudio (or any other vendor software) is open and using that instrument.

    Close one program before opening the other. If you get a "resource busy" or "cannot open" error, check that no other terminal, script, or vendor tool is already connected.

### 3. Find your instruments

```
list          # show all connected instruments and their names
scan          # re-scan if you plugged something in after launch
```

Instruments are assigned names automatically based on type: `psu1`, `psu2`, `dmm1`, `scope1`, `awg1`, etc.

### 4. Control an instrument

```
use psu1          # set psu1 as the active power supply
psu chan 1 on     # enable output
psu set 5.0 0.5   # set 5 V, 0.5 A current limit
psu meas v        # measure output voltage
```

### 5. Log results and export

The assignment syntax (`label = instrument meas ...`) saves a reading to the log with a **label** (name you choose). `calc` retrieves it by that label. `log print` shows the table. `log save` exports it.

```
output = psu meas v unit=V         # save voltage — label is "output"
dmm config vdc                     # set DMM to DC voltage mode
dmm_v = dmm meas unit=V            # save DMM reading — label is "dmm_v"
calc error m["dmm_v"] - m["output"] unit=V   # reference labels in math
log print                           # show the full results table
log save results.csv                # export to CSV
```

See [Log & Calc](logging.md) for the full explanation of labels, `calc`, and export.

---

## Addressing multiple instruments

When you have more than one instrument of the same type, they are numbered:

```
list
# → psu1: HP E3631A
# → psu2: Matrix MPS-6010H
# → scope1: Rigol DHO804
```

You can address them directly by prefixing any command:

```
psu1 set 5.0      # set psu1 without changing the active selection
psu2 set 12.0     # set psu2 at the same time
```

Or switch the active instrument with `use`:

```
use psu2
psu set 12.0      # now acts on psu2
```

---

## Getting help

```
help              # list all commands
help psu          # inline help for a specific command
docs              # open this documentation in your browser
examples          # list bundled example scripts
```

---

## What's in the docs

| Page | What it covers |
|------|---------------|
| [Python API](python.md) | Control instruments from Python — autodiscovery, enums, direct instantiation |
| [General Commands](general.md) | scan, force_scan, list, use, idn, raw, state, sleep, reload |
| [PSU](psu.md) | Power supply control and measurement |
| [AWG](awg.md) | Function generator — waveforms, frequency, amplitude |
| [DMM](dmm.md) | Multimeter — measurement modes, logging |
| [Scope](scope.md) | Oscilloscope — channels, triggers, measurements, waveform capture |
| [SMU](smu.md) | Source measure unit — voltage/current sourcing and measurement |
| [EV2300](ev2300.md) | USB-to-I2C adapter — SMBus register read/write, scan, probe |
| [Scripting](scripting.md) | Scripts, variables, loops, directives — full reference |
| [Examples](examples.md) | Bundled example workflows with explanations |
| [Log & Calc](logging.md) | Measurement log, CSV export, derived calculations |
| [Plotting](plotting.md) | Static plots, live plots, interactive charts, data selection, detail view |
| [Instruments](instruments.md) | Supported models and connection setup |
| [LabVIEW Bridge](labview.md) | Calling instrument drivers from LabVIEW Python Nodes |
| [Troubleshooting](troubleshooting.md) | PATH issues, NI-VISA errors, managed machine workarounds |
