# SCPI Instrument Toolkit

Python drivers and an interactive REPL for test and measurement instruments used in the ESET 453 course. Connect to oscilloscopes, power supplies, multimeters, and function generators over USB, GPIB, and Serial using a single consistent interface.

## Supported Instruments

| Instrument | Type | Interface |
|---|---|---|
| Tektronix MSO2024 | Oscilloscope | USB |
| Rigol DHO804 | Oscilloscope | USB |
| HP E3631A | Triple-output DC Power Supply | GPIB |
| HP 34401A | 6.5-digit Digital Multimeter | GPIB |
| BK Precision 4063 | Function/AWG Generator | USB |
| Keysight EDU33212A | Function Generator | USB |
| Keysight EDU36311A | Power Supply | USB |
| OWON XDM1041 | Digital Multimeter | USB |
| Matrix MPS6010H | Power Supply | USB |
| JDS6600 | Function Generator | Serial |

## Quick Start

**Windows (PowerShell):**
```powershell
.\setup.ps1
python repl.py
```

**Linux/Mac:**
```bash
python setup.py
python repl.py
```

## Install as a Package

If you want to use the drivers in your own scripts without cloning this repo:

```bash
# Latest stable:
pip install git+https://github.com/bsikar/scpi-instrument-toolkit.git@main

# Pin to a specific version (check releases for the latest tag):
pip install git+https://github.com/bsikar/scpi-instrument-toolkit.git@v0.1.1
```

Then in your code:
```python
from lab_instruments import InstrumentDiscovery, HP_E3631A, Tektronix_MSO2024
```

## Interactive REPL

The REPL lets you discover connected instruments and send commands interactively. It also saves and replays command sequences (useful for automating repetitive lab steps).

**Using it from this repo (simplest):**
```bash
python repl.py
```

**Using it from your own personal lab repo (recommended):**

Add this toolkit as a git submodule in your personal repo, then use the provided wrapper so `.repl_scripts.json` is saved in your repo root and the submodule stays clean.

```bash
# 1. In your personal repo, add this toolkit as a submodule
git submodule add https://github.com/bsikar/scpi-instrument-toolkit.git
git submodule update --init

# 2. Copy the wrapper to your personal repo root and rename it
cp scpi-instrument-toolkit/repl_wrapper.py repl.py

# 3. Run from your personal repo root — that's it
python repl.py
```

The wrapper (`repl_wrapper.py`) adds the submodule to `sys.path` at runtime so no pip install or path configuration is needed. Your `.repl_scripts.json` is saved in your personal repo root, not inside the submodule.

Common commands:
```
scan                          # find all connected VISA instruments
list                          # show discovered instruments
use scope                     # select the oscilloscope
use psu                       # select the power supply
state safe                    # put all instruments in a safe state
psu set p6v 5.0 0.2           # set PSU channel to 5V, 200mA limit
psu output on                 # enable PSU output
awg wave 1 sine freq=1000 amp=1.0 offset=0
scope autoset
dmm meas vdc 10 0.001
```

## Using the Drivers in Your Own Scripts

```python
from lab_instruments import InstrumentDiscovery, HP_E3631A, HP_34401A

# Find all connected instruments
discovery = InstrumentDiscovery()
instruments = discovery.find_all()

# Connect to a specific instrument by model
psu_resource = next(i['resource'] for i in instruments if 'E3631A' in i['model'])
psu = HP_E3631A(psu_resource)
psu.set_voltage('p6v', 3.3)
psu.set_current('p6v', 0.1)
psu.output_on()

# Clean up
psu.close()
```

## Prerequisites

- Python 3.8+
- [NI-VISA](https://www.ni.com/en-us/support/downloads/drivers/download.ni-visa.html) (required for USB-TMC and GPIB)
- GPIB adapter if using GPIB instruments

## Project Structure

```
scpi-instrument-toolkit/
├── lab_instruments/        # Installable Python package
│   ├── __init__.py         # Exports all drivers
│   ├── pyproject.toml
│   └── src/                # Individual instrument drivers
├── tests/                  # Unit tests for each driver
├── repl.py                 # Interactive REPL
├── repl_wrapper.py         # Copy this to your personal repo root, rename to repl.py
├── setup.py                # Linux/Mac environment setup
├── setup.ps1               # Windows environment setup
└── requirements.txt        # Python dependencies
```

## Running Tests

```bash
# Activate your venv first, then:
python -m pytest tests/
```

## Troubleshooting

**No devices found:**
- Install NI-VISA and restart
- Check USB cables and device power
- Close NI MAX or LabVIEW if open
- Check Device Manager for "USB Test and Measurement Device"

**GPIB errors:**
- Verify GPIB cable connections
- Check the device address (typically 1-30)
- Confirm the GPIB adapter appears in NI MAX

**Reset environment:**
```powershell
Remove-Item -Recurse -Force .venv
.\setup.ps1
```

## Contributing

Found a bug or want to add support for another instrument? Open an issue or submit a pull request. New drivers should follow the `DeviceManager` base class pattern in `lab_instruments/src/device_manager.py`.

## License

MIT
