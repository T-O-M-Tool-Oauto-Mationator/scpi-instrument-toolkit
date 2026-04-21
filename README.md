# SCPI Instrument Toolkit

Control oscilloscopes, power supplies, multimeters, and function generators from your computer.

**Docs:** https://t-o-m-tool-oauto-mationator.github.io/scpi-instrument-toolkit/

---

## TAMU Students — Start Here

Run this one line in **PowerShell** (no admin required):

```powershell
irm "https://raw.githubusercontent.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit/main/setup-tamu.ps1" | iex
```

That's it. It installs Python, git, and the toolkit automatically. Then jump to [Start the REPL](#start-the-repl).

---

## Everyone Else — Install

You need Python 3.8+. Then:

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