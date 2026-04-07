# SCPI Instrument Toolkit

A tool for controlling lab instruments (oscilloscopes, power supplies, multimeters, and function generators) from your computer.

---

## 🎓 TAMU Students — Managed / Lab Machines

> **On a TAMU lab or personal managed machine with no admin rights?**
> Run the one-liner below in PowerShell — it installs everything for you (GitHub Desktop, git, Python, and this toolkit) with **zero admin required**.

```powershell
irm "https://raw.githubusercontent.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit/main/setup-tamu.ps1" | iex
```

Already cloned the repo? Just run:

```powershell
.\setup-tamu.ps1
```

**What it installs:** GitHub Desktop (includes git) · Git for Windows (Git Bash) · GitHub CLI (gh) · Python 3.12 · scpi-instrument-toolkit · Claude Code

To uninstall everything the setup script installed:

```powershell
irm "https://raw.githubusercontent.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit/main/uninstall-tamu.ps1" | iex
```

> **NI-VISA** (needed for real hardware) requires admin rights and must be installed separately by IT or via the [NI download page](https://www.ni.com/en/support/downloads/drivers/download.ni-visa.html). Use `--mock` mode until then.

### Set up a project workspace (venv)

For lab scripts and data analysis, create an isolated Python environment per project so package installs do not affect each other.

```powershell
# Create a project folder and enter it
mkdir my-lab-project
cd my-lab-project

# Create a virtual environment
python -m venv .venv

# Activate it
.\.venv\Scripts\Activate.ps1
```

> **Managed machines:** if activation fails with a script-execution error, run this once in PowerShell:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```
> Or use the batch form instead: `.\.venv\Scripts\activate.bat`

With the venv active, install the toolkit into it:

```powershell
pip install "git+https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git"
```

To deactivate when you are done: `deactivate`

**VS Code:** open the project folder (`code .`), then pick `.venv` as the interpreter (Ctrl+Shift+P -> "Python: Select Interpreter").

> **Don't want to use the REPL?** You can import the drivers directly in your own Python scripts -- see [Using the Python Drivers Directly](#using-the-python-drivers-directly).

### Documentation

| Docs | What they cover |
|------|----------------|
| [REPL Command Reference](docs/index.md) | Interactive REPL commands, scripting, logging |
| [Python API Reference](docs-library/index.md) | Using the drivers as a Python library in your own scripts |

To open them from the REPL: `docs repl` or `docs python`.

See [docs/troubleshooting.md](docs/troubleshooting.md) if you run into issues.

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

> **BQ76920 battery monitor IC:** for Python drivers and register-level documentation, see [CesMag/BQ76920_Bridge](https://github.com/CesMag/BQ76920_Bridge).

---

## Installation

You need **Python 3.8 or newer** installed on your computer. You can check by opening a terminal and running:

```
python --version
```

If you don't have Python, download it from [python.org](https://www.python.org/downloads/).

### Install channels

There are two channels: **stable** (recommended) and **nightly** (latest development build).

#### Stable

The latest reviewed, tested release:

```
pip install "git+https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git"
```

#### Nightly

Built automatically from the latest `main` branch every night at midnight CST. Use this to get the newest features before a stable release. Not recommended for production lab use.

```
pip install "git+https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git@nightly"
```

To update to the latest nightly:

```
pip install --upgrade "git+https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git@nightly"
```

That's it. Both channels install everything including the `scpi-repl` command.

> **Note:** You also need [NI-VISA](https://www.ni.com/en/support/downloads/drivers/download.ni-visa.html) installed for the tool to detect instruments over USB or GPIB.

---

## Using the REPL

The REPL (Read-Eval-Print Loop) is an interactive terminal where you type commands to control your instruments.

### Start it

```
scpi-repl
```

It will automatically scan for connected instruments and show you what it found.

> **On managed machines (school/work computers):** if `scpi-repl` is not recognized, pip may have installed it to a directory that isn't on your PATH. Use this instead — `python` is always available:
> ```
> python -m lab_instruments
> ```
> All flags work the same way: `python -m lab_instruments --mock`, etc.

### Try it without any instruments

If you just want to explore the tool without connecting anything:

```
scpi-repl --mock
```

This uses fake instruments so you can test commands safely.

---

## Using the Python Drivers Directly

If you are writing a Python script for data collection, pandas analysis, or a lab report and do not need the interactive REPL, you can import the instrument drivers directly.

> **Full Python API docs:** Run `docs python` in the REPL, or open [docs-library/index.md](docs-library/index.md) for the complete API reference with method tables and examples for every driver.

### Find your instrument's VISA address

Connect the instrument and run this in Python:

```python
import pyvisa
rm = pyvisa.ResourceManager()
print(rm.list_resources())
# Example output: ('GPIB0::5::INSTR', 'GPIB0::22::INSTR', 'USB0::...')
```

### Minimal example

```python
from lab_instruments.src.hp_e3631a import HP_E3631A
from lab_instruments.src.hp_34401a import HP_34401A

psu = HP_E3631A("GPIB0::5::INSTR")   # replace with your address
dmm = HP_34401A("GPIB0::22::INSTR")  # replace with your address

psu.connect()
dmm.connect()
try:
    # Set +6V channel to 3.3V, 0.1A limit and enable output
    psu.set_output_channel("positive_6_volts_channel", 3.3, current_limit=0.1)
    psu.enable_output(True)

    # Configure DMM for DC voltage and take a reading
    dmm.configure_dc_voltage()
    reading = dmm.read()
    print(f"Measured: {reading} V")
finally:
    psu.disconnect()
    dmm.disconnect()
```

Always call `disconnect()` in a `finally` block so the instrument is released even if the script crashes.

### Available drivers

| Instrument | Class | Import path |
|---|---|---|
| HP E3631A PSU | `HP_E3631A` | `lab_instruments.src.hp_e3631a` |
| HP 34401A DMM | `HP_34401A` | `lab_instruments.src.hp_34401a` |
| Tektronix MSO2024 | `Tektronix_MSO2024` | `lab_instruments.src.tektronix_mso2024` |
| Rigol DHO804 | `Rigol_DHO804` | `lab_instruments.src.rigol_dho804` |
| BK Precision 4063 | `BK_4063` | `lab_instruments.src.bk_4063` |
| Keysight EDU33212A | `Keysight_EDU33212A` | `lab_instruments.src.keysight_edu33212a` |
| OWON XDM1041 | `Owon_XDM1041` | `lab_instruments.src.owon_xdm1041` |
| Matrix MPS6010H | `MATRIX_MPS6010H` | `lab_instruments.src.matrix_mps6010h` |
| JDS6600 | `JDS6600_Generator` | `lab_instruments.src.jds6600_generator` |
| NI PXIe-4139 | `NI_PXIe_4139` | `lab_instruments.src.ni_pxie_4139` |

---

## Basic Commands

Once the REPL is running, here are the most useful commands:

| Command | What it does |
|---|---|
| `help` | Show all available commands |
| `docs` | Open the full command reference in your browser |
| `list` | Show connected instruments |
| `scan` | Re-scan for instruments |
| `psu chan 1 on` | Turn on the power supply |
| `psu set 5.0 0.5` | Set PSU to 5V, 0.5A limit |
| `psu meas v` | Measure output voltage |
| `dmm meas vdc` | Measure DC voltage |
| `dmm read` | Take a reading |
| `awg wave 1 sine freq=1000 amp=2.0` | Output a 1kHz sine wave |
| `scope meas 1 FREQUENCY` | Measure frequency on channel 1 |
| `scope autoset` | Auto-configure the scope |
| `state safe` | Put all instruments in a safe state |
| `exit` | Quit |

Type `help <command>` for more detail on any command. For example: `help psu`

### Full documentation

Run `docs` inside the REPL to open a complete command reference in your browser. It covers every command and subcommand with parameter descriptions and examples — including what `label`, `unit=`, and `scale=` do in measurement commands.

---

## Saving and Running Scripts

You can save sequences of commands as scripts so you don't have to type them every time.

```
script new my_setup
```

This opens a text editor. Type your commands (one per line), save, and close. Then run it with:

```
script run my_setup
```

Scripts are saved as individual `.scpi` files in your user scripts directory (usually `Documents/scpi-instrument-toolkit/scripts`).

---

## Updating

**Stable:**

```
pip install --upgrade "git+https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git"
```

**Nightly:**

```
pip install --upgrade "git+https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git@nightly"
```

---

## Troubleshooting

### `scpi-repl` is not recognized

Pip installs `scpi-repl` to the Python `Scripts` folder, which may not be on your PATH.

**Self-healing fix (standard Windows)**

Run the module form once:

```powershell
python -m lab_instruments
```

The toolkit automatically adds the Scripts folder to your user PATH via the Windows registry and prints a message telling you to open a new terminal. After that, `scpi-repl` will work in every new PowerShell window.

**Managed machines (TAMU VOAL and similar)**

On machines where group policy blocks registry edits, the automatic fix above will not work. Use one of these instead:

- **Permanent workaround** — always launch with:
  ```powershell
  python -m lab_instruments
  ```
  All flags work the same way: `python -m lab_instruments --mock`, etc.

- **Session-only PATH fix** — paste this into PowerShell to enable `scpi-repl` for the current session only:
  ```powershell
  $pyPath = python -c "import sys, os; print(os.path.join(sys.prefix, 'Scripts'))"
  $env:Path += ";$pyPath"
  scpi-repl
  ```
  You'll need to run these two lines again each time you open a new terminal.

### `git` is not recognized on managed machines

On many managed lab/work machines, you can install GitHub Desktop but still not have `git` on your PATH.

Use the repo helper script (no admin required):

```powershell
.\setup-git.ps1
```

What it does:

- Finds GitHub Desktop's bundled `git.exe` dynamically (works across app version updates)
- Adds only the `...\git\cmd` folder to your **user** PATH
- Avoids duplicate PATH entries

Then open a **new terminal** and verify:

```powershell
git --version
```

Quick one-liner option:

```powershell
$g=(Get-ChildItem "$env:LOCALAPPDATA\GitHubDesktop\app-*\resources\app\git\cmd\git.exe" -EA 0|Sort-Object LastWriteTime -Desc|Select-Object -First 1); if(-not $g){$g=(Get-ChildItem "$env:LOCALAPPDATA\GitHubDesktop" -Filter git.exe -Recurse -EA 0|?{$_.DirectoryName -like "*\git\cmd"}|Sort-Object LastWriteTime -Desc|Select-Object -First 1)}; if(-not $g){Write-Host "GitHub Desktop Git not found" -FG Red}else{$p=$g.DirectoryName;$u=[Environment]::GetEnvironmentVariable('Path','User'); if(($u -split ';'|%{$_.TrimEnd('\\').ToLowerInvariant()}) -notcontains $p.TrimEnd('\\').ToLowerInvariant()){[Environment]::SetEnvironmentVariable('Path',($(if([string]::IsNullOrWhiteSpace($u)){$p}else{"$u;$p"})),'User')}; Write-Host "Done. Open a new terminal and run: git --version" -FG Green}
```
