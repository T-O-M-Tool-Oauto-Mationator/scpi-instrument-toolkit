# Installation — short version

> One-page install guide. For the full reference (platform-specific notes, every vendor driver, troubleshooting), see [`docs/install.md`](docs/install.md).

## 1. Install the toolkit

The toolkit is not on PyPI. Install from GitHub:

```bash
pip install "git+https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git"
```

Requires **Python 3.10 or later** and `git` on PATH.

**TAMU managed laptops:** admin is restricted, so a normal `pip install` fails. Use the bundled installer instead:

```powershell
irm "https://raw.githubusercontent.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit/main/setup-tamu.ps1" -OutFile setup-tamu.ps1
notepad setup-tamu.ps1     # skim before running anything from the internet
powershell -ExecutionPolicy Bypass -File .\setup-tamu.ps1
```

It installs to `%APPDATA%\Python` (your user profile), so no admin is needed.

## 2. Verify

```bash
scpi-repl --mock
```

You should see the REPL banner and `eset>` prompt. `--mock` simulates 14 devices, so this works without any real hardware. See `help` once you're in.

## 3. Vendor drivers (only if you have real hardware)

Skip this whole section if you're only going to use `--mock` mode.

| Driver | When you need it | Install |
|---|---|---|
| **NI-VISA runtime** | Any USB-TMC, GPIB, or VXI-11 / HiSLIP instrument (Keysight DMMs/PSUs, Rigol scopes, Tektronix scopes, BK function generators, etc.) | [ni.com/en/support/downloads/drivers/download.ni-visa.html](https://www.ni.com/en/support/downloads/drivers/download.ni-visa.html) — admin required, ~5–10 min, restart terminal afterwards |
| **NI-DCPower** | NI PXIe-4139 SMU only | [ni.com → DCPower](https://www.ni.com/en/support/downloads/drivers.html) + `pip install nidcpower` |
| **EV2300 / STM32 bridge** | BQ76920 battery-monitor labs | Enumerates as USB-HID — no separate vendor driver; `pip install "scpi-instrument-toolkit[hid] @ git+https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git"` adds the Python `hidapi` binding |

Optional vendor utilities (Keysight Connection Expert, NI MAX, TI BQStudio) are useful for troubleshooting but **never required** by the toolkit itself.

## 4. Upgrading

```bash
pip install --upgrade "git+https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git"
```

To pull the latest nightly instead of the most recent stable tag:

```bash
pip install --upgrade --force-reinstall "git+https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git@dev/nightly"
```

## 5. If something breaks

- Toolkit-side issues: see the [Troubleshooting](https://t-o-m-tool-oauto-mationator.github.io/scpi-instrument-toolkit/troubleshooting/) page.
- Driver-side issues (NI MAX doesn't see your instrument, EV2300 fails to enumerate, etc.): close any other program that might be holding the resource (only one app can own a VISA handle at a time), then `force_scan` from the REPL.
