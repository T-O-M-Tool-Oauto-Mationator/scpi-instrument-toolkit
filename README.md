# SCPI Instrument Toolkit

Control oscilloscopes, power supplies, multimeters, and function generators from your computer.

**Docs:** https://t-o-m-tool-oauto-mationator.github.io/scpi-instrument-toolkit/

---

## What can I do with this toolkit?

- **Drive a full bench from one prompt** -- PSUs, DMMs, scopes, AWGs, SMUs, and the TI EV2300 USB-to-I2C adapter, all from one REPL.
- **Run measurement scripts** -- `for`/`while`/`if`, variables, asserts, parameter overrides, and a step debugger. ([Scripting](https://t-o-m-tool-oauto-mationator.github.io/scpi-instrument-toolkit/scripting.html))
- **Practice without hardware** -- 14 simulated instruments via `--mock`. ([Mock Mode](https://t-o-m-tool-oauto-mationator.github.io/scpi-instrument-toolkit/mock_mode.html))
- **Log to CSV and analyze in pandas** -- assign-style measurement syntax, `calc` for derived values, `log save` to CSV.
- **15+ bundled examples** -- PSU+DMM sweeps, scope captures, full lab-report workflows. ([Examples](https://t-o-m-tool-oauto-mationator.github.io/scpi-instrument-toolkit/examples.html))

**Learning path:** Start in [Mock Mode](https://t-o-m-tool-oauto-mationator.github.io/scpi-instrument-toolkit/mock_mode.html), skim the [Examples](https://t-o-m-tool-oauto-mationator.github.io/scpi-instrument-toolkit/examples.html), then read [Scripting](https://t-o-m-tool-oauto-mationator.github.io/scpi-instrument-toolkit/scripting.html) when you want to write your own tests. See the [Architecture overview](https://t-o-m-tool-oauto-mationator.github.io/scpi-instrument-toolkit/architecture.html) for the 5-layer system diagram.

---

## TAMU Students — Start Here

Run this one line in **PowerShell** (no admin required):

```powershell
irm "https://raw.githubusercontent.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit/main/setup-tamu.ps1" | iex
```

That's it. It installs Python, git, and the toolkit automatically. Then jump to [Start the REPL](#start-the-repl).

**Using NI TestStand?** After the line above, also run `setup-teststand.ps1` to create a TestStand-compatible venv on your `H:` drive and have the script validate it for you. See the [NI TestStand Setup guide](https://t-o-m-tool-oauto-mationator.github.io/scpi-instrument-toolkit/teststand.html) for details.

---

## Everyone Else — Install

You need Python 3.10+ (use 3.12 if you plan to drive the toolkit from NI TestStand). Then:

```
pip install "git+https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git"
```

> You also need [NI-VISA](https://www.ni.com/en/support/downloads/drivers/download.ni-visa.html) to talk to real instruments. Skip it and use `--mock` to try everything without hardware.

---

## Start the REPL

```
scpi-repl
```

> If `scpi-repl` isn't recognized, use: `python -m lab_instruments`

### Try it without instruments

```
scpi-repl --mock
```

Fake instruments — safe to experiment with everything.

---

## Updating

```
pip install --upgrade "git+https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git"
```

---

## Nightly / Dev Builds

Want the latest in-progress features? Install from the `dev/nightly` branch:

```
pip install "git+https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git@dev/nightly"
```

To update an existing nightly install, add `--upgrade --force-reinstall` (forces pip to re-pull even if the version string hasn't changed):

```
pip install --upgrade --force-reinstall "git+https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git@dev/nightly"
```

> Nightly builds track active development — expect rough edges. For stable use, stick with the default install above.

---

## Supported Instruments

| Instrument | Type |
|---|---|
| Tektronix MSO2024 | Oscilloscope |
| Rigol DHO804 | Oscilloscope |
| HP E3631A | Power Supply |
| HP 34401A | Multimeter |
| BK Precision 4063 | Function Generator |
| Keysight EDU33212A | Function Generator |
| OWON XDM1041 | Multimeter |
| Matrix MPS6010H | Power Supply |
| JDS6600 | Function Generator |
| NI PXIe-4139 | SMU |