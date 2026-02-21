# SCPI Instrument Toolkit

Python REPL for controlling lab instruments — oscilloscopes, power supplies, multimeters, and function generators — over VISA (USB, GPIB, Serial).

---

## Quick Start

### 1. Install

```bash
pip install git+https://github.com/bsikar/scpi-instrument-toolkit.git
```

> **Requires** [NI-VISA](https://www.ni.com/en/support/downloads/drivers/download.ni-visa.html) for USB and GPIB instruments.

### 2. Launch

```bash
scpi-repl           # auto-discovers connected instruments
scpi-repl --mock    # simulate instruments (no hardware needed)
```

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

`meas_store` saves a reading to the log with a **label** (name you choose). `calc` retrieves it by that label. `log print` shows the table. `log save` exports it.

```
psu meas_store v output unit=V     # save voltage — label is "output"
dmm meas_store vdc dmm_v unit=V   # save DMM reading — label is "dmm_v"
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
| [General Commands](general.md) | scan, list, use, idn, raw, state, sleep, reload |
| [PSU](psu.md) | Power supply control and measurement |
| [AWG](awg.md) | Function generator — waveforms, frequency, amplitude |
| [DMM](dmm.md) | Multimeter — measurement modes, logging |
| [Scope](scope.md) | Oscilloscope — channels, triggers, measurements, waveform capture |
| [Scripting](scripting.md) | Scripts, variables, loops, directives — full reference |
| [Examples](examples.md) | Bundled example workflows with explanations |
| [Log & Calc](logging.md) | Measurement log, CSV export, derived calculations |
| [Instruments](instruments.md) | Supported models and connection setup |
