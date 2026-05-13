# NI TestStand Setup

This guide walks you through driving the toolkit from **NI TestStand** on a TAMU managed Windows machine (or any Windows machine without admin rights). By the end you will have:

- A real Python 3.12 install that TestStand can load
- A virtual environment with the toolkit installed inside it
- A working TestStand Python adapter configuration
- A smoke-test sequence that proves the wiring end-to-end
- Example step modules that drive real instruments from TestStand

If you are only using the REPL or the Python API directly, you do not need any of this. See [Installation](install.md).

---

## How much of this is already done for you?

If you ran the all-in-one TAMU setup (see [Troubleshooting > First-time setup](troubleshooting.md#first-time-setup-on-tamu-managed-windows-machines)):

```powershell
irm "https://raw.githubusercontent.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit/main/setup-tamu.ps1" | iex
```

then the script has already done these steps for you:

| Step | Done by `setup-tamu.ps1`? |
|---|---|
| Install git + GitHub Desktop + GitHub CLI | Yes |
| Install Python 3.12 (user scope, no admin) | Yes |
| Add Python and Scripts dirs to user PATH | Yes (winget package handles this) |
| `pip install` toolkit from GitHub (global) | Yes |
| Install Claude Code | Yes |
| **Create a TestStand-compatible venv** | **No - run `setup-teststand.ps1` (see [section 3](#3-create-a-venv-on-a-mapped-drive))** |
| **Configure TestStand Python adapter** | **No - do this below** |
| Install NI-VISA / NI-DCPower system drivers | No - needs admin, install separately |

So if you already ran the setup script, skip ahead to [Create the venv](#3-create-a-venv-on-a-mapped-drive) and use `setup-teststand.ps1` to finish the job. The first two sections only matter if you are setting up Python manually.

---

## 1. Why Microsoft Store Python Does Not Work

The Microsoft Store versions of Python (3.12, 3.13, etc.) use **app execution aliases** - stub launchers that redirect to the real installation in `C:\Program Files\WindowsApps\...`, which is a protected directory. TestStand's Python adapter needs to load `python3XX.dll` directly, and that DLL is not accessible when Python is installed from the Store.

You can verify this yourself by running:

```python
import ctypes.util
print(ctypes.util.find_library('python312'))  # prints None for Store installs
```

TestStand hits the same wall - it cannot find or load the DLL, and will show:

> Unable to load specified version of python. Make sure python of proper bitness is installed and added to PATH environment variable.

The fix is to install a **real** Python (not the Store stub). You have two options.

---

## 2. Install a Real Python 3.12 (No Admin Required)

You only need to do this once. Pick **one** of the two options below.

### Option A: Use `setup-tamu.ps1` (recommended)

The setup script installs Python 3.12 via winget into your user profile:

```text
%LOCALAPPDATA%\Programs\Python\Python312\python.exe
%LOCALAPPDATA%\Programs\Python\Python312\python312.dll
```

That directory is added to your **user PATH** automatically, so TestStand can find the DLL on launch. No further PATH edits needed.

### Option B: Use the Python Install Manager (`py install`)

The Python install manager (`py` command, pre-installed on TAMU lab machines as a Windows app alias) can also install a real Python without admin rights. Open a terminal and run:

```cmd
py install 3.12
```

This installs Python 3.12 to:

```text
%LOCALAPPDATA%\Python\pythoncore-3.12-64\python.exe
%LOCALAPPDATA%\Python\pythoncore-3.12-64\python312.dll
```

Note: this is a **different directory** than Option A. Unlike Option A, `py install` does **not** add the directory to PATH automatically, so TestStand will not find the DLL unless you add it yourself:

```powershell
$currentPath = [System.Environment]::GetEnvironmentVariable('PATH', 'User')
$newDir = "$env:LOCALAPPDATA\Python\pythoncore-3.12-64"
[System.Environment]::SetEnvironmentVariable('PATH', $newDir + ';' + $currentPath, 'User')
```

**Restart TestStand after editing PATH** - TestStand reads PATH only at launch.

### Verify Python is on PATH

After either option, open a **new** terminal and run:

```powershell
python --version
python -c "import ctypes.util; print(ctypes.util.find_library('python312'))"
```

The first should print `Python 3.12.x`. The second should print a path (not `None`). If both work, TestStand will find the DLL.

---

## 3. Create a Venv on a Mapped Drive

### Why a venv (and not just the global Python)?

Even though `setup-tamu.ps1` already installs the toolkit globally, the TestStand adapter expects you to point it at a **virtual environment** so that:

- Your environment survives roaming-profile resets on TAMU lab machines
- Per-project package versions do not collide with other classes
- The TestStand Python adapter has a stable, known location to load packages from

### Why a mapped drive (not a raw UNC path)?

On TAMU lab machines, `H:\` is a **junction to your network home directory** (a `\\coe-fs.engr.tamu.edu\Ugrads\<NetID>\...` UNC share). You should always type the `H:\` path - tools like cmd.exe refuse to use raw UNC paths as a working directory ("UNC paths are not supported"), but they handle the `H:\` junction fine.

- **DO NOT** type: `\\coe-fs.engr.tamu.edu\Ugrads\<NetID>\Documents\eset-453\.venv`
- **USE** instead: `H:\Documents\eset-453\.venv`

> Replace `H:\Documents\eset-453\` with your own mapped drive letter and project path throughout this guide.

!!! note "Heads-up: Python's 'redirects, links or junctions' warning is harmless here"
    When you create the venv, Python 3.12 will print:

    > Actual environment location may have moved due to redirects, links or junctions.
    > Requested location: "H:\\Documents\\eset-453\\.venv\\Scripts\\python.exe"
    > Actual location:    "\\\\coe-fs.engr.tamu.edu\\Ugrads\\<NetID>\\Documents\\eset-453\\.venv\\Scripts\\python.exe"

    This is **expected** because `H:\` resolves to that UNC share. It is informational only - the venv works correctly, `Activate.ps1` works, and TestStand can use the `H:\...\.venv` path without issue. See [issue #104](https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit/issues/104).

### Option 1: Use `setup-teststand.ps1` (recommended)

After `setup-tamu.ps1` has installed Python 3.12, run the helper script from the toolkit repo:

```powershell
.\setup-teststand.ps1
```

Or, if you have not cloned the repo:

```powershell
irm "https://raw.githubusercontent.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit/main/setup-teststand.ps1" | iex
```

What it does:

- Picks `H:\Documents\scpi-workspace\` as the project root (or falls back to `%USERPROFILE%` if `H:\` is not mapped, with a warning)
- Finds a real Python 3.12 from `setup-tamu.ps1` **or** `py install 3.12`
- Creates `<project-root>\.venv` (or skips if one is already there)
- Installs `scpi-instrument-toolkit` into the venv
- **Validates** end-to-end: confirms `python312.dll` is loadable (the thing TestStand needs), confirms `lab_instruments` imports cleanly
- Prints the exact TestStand adapter values to copy-paste

Useful flags:

| Flag | Purpose |
|---|---|
| `-ProjectName eset-453` | Use `H:\Documents\eset-453\` instead of `scpi-workspace`. |
| `-Drive G` | Use a different drive letter (defaults to `H`). |
| `-Recreate` | Wipe and rebuild the venv from scratch. |
| `-NoPause` | Skip the "Press Enter to close" prompt. Useful when chaining scripts. |

Skip ahead to [Configure the TestStand Python Adapter](#4-configure-the-teststand-python-adapter) if the script ran clean.

### Option 2: Manual setup (if the script does not fit your workflow)

#### Create the venv

If you used Option A (`setup-tamu.ps1`):

```cmd
"%LOCALAPPDATA%\Programs\Python\Python312\python.exe" -m venv H:\Documents\eset-453\.venv
```

If you used Option B (`py install 3.12`):

```cmd
"%LOCALAPPDATA%\Python\pythoncore-3.12-64\python.exe" -m venv H:\Documents\eset-453\.venv
```

#### Install the toolkit into the venv

The toolkit is **not on PyPI** - it installs from the GitHub repo:

```cmd
H:\Documents\eset-453\.venv\Scripts\pip.exe install "git+https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git"
```

!!! warning "`pip install scpi-instrument-toolkit` will fail"
    You will see `ERROR: Could not find a version that satisfies the requirement scpi-instrument-toolkit` if you drop the `git+https://...` URL. The package is not published on PyPI - always use the URL form. See [issue #106](https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit/issues/106).

If your lab has its own `requirements.txt`, install that instead:

```cmd
H:\Documents\eset-453\.venv\Scripts\pip.exe install -r H:\Documents\eset-453\requirements.txt
```

> **Note:** Both commands write to the TAMU network drive, which is slow. The venv creation
> takes 30-60 seconds and the pip install can take several minutes depending on network
> conditions. This is normal - do not cancel. Wait for the prompt to return before continuing.

#### Verify the venv

Run this in PowerShell - it confirms the three things TestStand actually depends on (real interpreter, loadable DLL, importable toolkit) in one shot:

<!-- doc-test: skip reason="PowerShell snippet with embedded Python heredoc, not pure Python" -->
```powershell
& "H:\Documents\eset-453\.venv\Scripts\python.exe" -c @"
import sys, ctypes.util
print('python:', sys.version.split()[0])
print('exe:', sys.executable)
dll = ctypes.util.find_library('python312')
print('python312.dll:', dll if dll else '<not found>')
assert dll, 'python312.dll not on PATH - TestStand will refuse to load this interpreter.'
from lab_instruments import find_all
print('lab_instruments: OK')
"@
```

You should see four lines printed and no traceback. If `python312.dll: <not found>` or the assertion fires, TestStand will not be able to load this interpreter even though the venv works on the command line.

**This means the base Python dir (the one that holds `python312.dll`) is not on your user PATH.** The venv's `Scripts\` directory does not contain `python312.dll` - only the base install does, so PATH must point to the base install for TestStand to find it. Fix it by either:

- Re-run `setup-teststand.ps1` - it now adds the base Python dir to user PATH automatically, then open a **new** terminal and re-run the verification.
- Or add it yourself in PowerShell (cmd-style `%LOCALAPPDATA%` does **not** expand in PowerShell - use `$env:LOCALAPPDATA`):

```powershell
$dir = "$env:LOCALAPPDATA\Programs\Python\Python312"  # or \Python\pythoncore-3.12-64 for `py install`
$cur = [Environment]::GetEnvironmentVariable("Path", "User")
if (($cur -split ";") -notcontains $dir) {
    [Environment]::SetEnvironmentVariable("Path", "$cur;$dir", "User")
}
```

Close and reopen PowerShell after either fix - PATH changes do not affect already-open shells. Then restart TestStand for the same reason.

---

## 4. Configure the TestStand Python Adapter

Open TestStand, then go to **Configure > Adapters > Python > Configure**.

### Main tab

| Field | Value |
|---|---|
| Interpreter to use | Global |
| Virtual environment (optional) | `H:\Documents\eset-453\.venv` |
| Executable Path | *(greyed out on managed machines - leave blank)* |
| Version | `3.12` |

### Advanced tab — **check this box, students miss it**

- [x] **Display Console for Interpreter Sessions**

Without this, every `print()` inside a Python step disappears silently — the step still runs and reports its Status, but you cannot see any of the diagnostic output the function produced. NI's own Python example bundled with TestStand lists this as a prerequisite. Issue #118 was a student concluding the smoke test was broken because this box was unchecked and they assumed Status:Done with no console meant nothing ran. (The COM property behind this checkbox is `PythonAdapter.DisplayConsoleForInterpreterSessions` — verified against TestStand 2025 Q3 64-bit.)

### When else you need `pywin32`

The toolkit itself does **not** need `pywin32` inside the venv to run any of the smoke-test steps in [section 5](#5-smoke-test-prove-the-wiring-works) or the instrument calls in [section 6](#6-calling-real-instruments-from-teststand). You only need to `pip install pywin32` into the venv if a Python step accepts TestStand's `SequenceContext`, `Engine`, or another `IDispatch` COM object as a parameter (which gives your Python code access to the running TestStand engine itself). None of our examples do this — but if you write one that does, the adapter will fail with `-17500: Unable to pass parameter as COM object. Make sure you have installed pywin32`. The fix is `H:\Documents\<your-project>\.venv\Scripts\pip.exe install pywin32` and a restart of the TestStand interpreter session.

### Notes

- The **Version** dropdown is editable - click it and type `3.12` directly if it does not appear in the list.
- The **Executable Path** field is locked on TAMU managed machines. This is only used for step-into debugging anyway, not for normal test execution.
- TestStand embeds the Python DLL at runtime via PATH - it does **not** invoke `python.exe` directly to run code modules. That is why steps 1 and 2 above matter even when a venv is provided.
- The venv path must use a mapped drive letter (`H:\...`), not a UNC path. See above.

---

## 5. Smoke Test - Prove the Wiring Works

Before you write a single real test step, save the file below to your project folder. It uses no instruments, just a fake reading.

**`teststand_hello.py`**:

```python
"""Simple NI TestStand Python adapter smoke test."""


def check_connection():
    """Action step. Takes no arguments. Returns None."""
    print("Python adapter is working correctly.")


def get_voltage():
    """Numeric Limit Test step. Takes no arguments. Returns 5.0."""
    voltage = 5.0
    print(f"Measured voltage: {voltage} V")
    return voltage


def add(a, b):
    """Numeric Limit Test step. Takes two numeric arguments from TestStand. Returns a + b."""
    result = a + b
    print(f"add({a}, {b}) = {result}")
    return result


if __name__ == "__main__":
    # Verify the file works outside TestStand
    check_connection()
    print(get_voltage())
    print(add(3, 4))
```

In TestStand, **File > New > Sequence File**, then insert three steps in the **Main** group. The exact UI for each:

### Step 1 — Action calling `check_connection`

1. Right-click **Main** → **Insert Step** → **Action**.
2. With the new step selected, in the **Step Settings** pane (bottom of the window):
   - **Module Path**: browse to `teststand_hello.py`
   - **Function Name**: `check_connection`
3. **Arguments** tab: empty (the function takes no parameters).
4. Save the sequence, click **Execute > Run MainSequence**. Look at the **Steps** pane — the Action row's **Status** column should read **Done** and the **Executions** pane (top-left) should show a green checkmark next to MainSequence. That is the success signal.

!!! note "Why isn't `Python adapter is working correctly.` in the Output pane?"
    TestStand's **Output** pane is a structured message log (note the `MESSAGE` column header), not a Python stdout console. The Python adapter captures `print()` output silently and does not surface it there by default. Don't worry about it — **Status: Done** means the function ran. To make `print()` output visible, check the **Display Console for Interpreter Sessions** box under [Configure > Adapters > Python > Configure > Advanced](#advanced-tab-check-this-box-students-miss-it).

### Step 2 — Numeric Limit Test calling `get_voltage`

1. Right-click → **Insert Step** → **Tests** → **Numeric Limit Test**.
2. **Step Settings** → **Module** tab:
   - **Module Path**: `teststand_hello.py`
   - **Function Name**: **pick `get_voltage` from the dropdown** (don't type it). Selecting from the dropdown is what makes TestStand introspect the function signature and auto-add the Return Value row.
3. **Arguments** tab: confirm a single row appears at the top — `Return Value`, **Value/Expression** = `Step.Result.Numeric`. **If this row is missing, your Measurement will read `0` and the limit check will always fail** ([fix below](#measurement-00-when-the-python-function-returns-a-non-zero-value)). Leave the row alone — `Step.Result.Numeric` is the correct binding.
4. **Limits** tab:
   - **Comparison Type**: `GELE (>= <=)`
   - **Low**: `4.5`
   - **High**: `5.5`
5. Run. Status should be **Passed**, Measurement should be **5.0**. If you see Measurement `0.0` instead, the Return Value row is missing — re-pick the function from the dropdown to force re-introspection.

### Step 3 — Numeric Limit Test calling `add` (with parameters)

1. Insert another **Numeric Limit Test** step.
2. **Module** tab:
   - **Module Path**: `teststand_hello.py`
   - **Function Name**: **pick `add` from the dropdown** (don't type it).
3. **Arguments** tab: TestStand introspects the function signature and shows **three rows**:

   | # | Name | Value/Expression | What to do |
   |---|---|---|---|
   | 0 | `Return Value` | `Step.Result.Numeric` | Leave alone (this is how the function's return value reaches Measurement). |
   | 1 | `a` | *(empty)* | **Fill in:** `3` |
   | 2 | `b` | *(empty)* | **Fill in:** `4` |

   **You must fill in `a` and `b`** — leaving them empty triggers run-time error `-17347: The expression cannot be empty`. Literal numbers (`3`, `4.5`, `True`) are valid expressions; TestStand variables also work (e.g. `Locals.SomeNumber`).
4. **Limits** tab:
   - **Comparison Type**: `EQ (==)`
   - **Limit**: `7`
5. Run. Status **Passed**, Measurement **7**.

!!! tip "All Python Numeric Limit Test steps share the same shape"
    Verified against NI's bundled Python example on TestStand 2025 Q3: every Python adapter Numeric Limit Test step has a `Return Value` row in its Arguments tab with `Step.Result.Numeric` as the expression. That's the channel the function's return value uses to reach Measurement. If you skip the dropdown and type the function name by hand, the row may not get added — pick from the dropdown and the Arguments table populates automatically.

If all three pass, the Python adapter, venv, and DLL load are all wired correctly. Move on.

---

## 6. Calling Real Instruments from TestStand

Once the smoke test passes, you can call the toolkit drivers from TestStand. The example below mirrors `lab4/scripts/teststand_instruments.py` in the eset-453 reference repo - it uses `find_all()` to auto-discover instruments on the VISA bus (the same call `scpi-repl` makes).

**`teststand_instruments.py`**:

```python
"""
TestStand Python module - uses lab_instruments directly.

Instruments are auto-discovered via find_all() the same way scpi-repl does it.
Each function below is a TestStand step (Action or Numeric Limit Test).
"""

import sys as _sys

# Insert the venv site-packages first on sys.path so TestStand can resolve
# `lab_instruments` even when its embedded Python falls back to the global
# interpreter's site-packages.
_VENV = r'H:\Documents\eset-453\.venv\Lib\site-packages'
if _VENV not in _sys.path:
    _sys.path.insert(0, _VENV)

from lab_instruments import find_all

# Populated by setup() - do not call find_all() at module load so TestStand
# controls when discovery runs (instruments must be powered on before setup).
instruments = {}


def setup(**kwargs):
    """
    Setup step - call this as the first step in your TestStand sequence.
    Scans the VISA bus and connects to all recognized instruments.
    All other functions in this module depend on this running first.
    """
    global instruments
    instruments = find_all()
    print("Instruments found:", list(instruments.keys()))


def measure_dc_voltage(**kwargs):
    """Numeric Limit Test - returns DMM DC voltage reading in volts."""
    return instruments["dmm"].measure_dc_voltage()


def measure_dc_current(**kwargs):
    """Numeric Limit Test - returns DMM DC current reading in amps."""
    return instruments["dmm"].measure_dc_current()


def measure_resistance(**kwargs):
    """Numeric Limit Test - returns DMM 2-wire resistance in ohms."""
    return instruments["dmm"].measure_resistance_2wire()


def set_psu_5v(**kwargs):
    """Action - sets PSU channel 1 to 5 V, 0.5 A limit, output on."""
    instruments["psu"].set_output_channel("positive_6_volts_channel", 5.0, 0.5)
    instruments["psu"].enable_output(True)


def psu_off(**kwargs):
    """Action - disables all PSU channels. Use as a cleanup step."""
    instruments["psu"].disable_all_channels()
```

### Why the `sys.path` insert at the top?

TestStand's Python adapter loads the embedded interpreter via PATH and `python312.dll`. Depending on adapter version and machine state, it does **not** always honor the venv's `site-packages` automatically - some setups end up importing from the global interpreter's site-packages instead. Inserting the venv's `site-packages` at index 0 of `sys.path` guarantees the toolkit version installed in your venv wins. Update the `_VENV` path string to match your venv location.

### Typical TestStand sequence

| # | Step Type | Function | Notes |
|---|---|---|---|
| 1 | Action | `setup` | Discovers PSU + DMM + AWG + Scope on the bus. Runs once at sequence start. |
| 2 | Action | `set_psu_5v` | Apply VIN. |
| 3 | Numeric Limit Test | `measure_dc_voltage` | Limits 4.5 V .. 5.5 V. |
| 4 | Numeric Limit Test | `measure_dc_current` | Limits 0 mA .. 100 mA. |
| 5 | Action | `psu_off` | Cleanup. |

You can write one of these per lab and reuse `setup` / `psu_off` as common bookends.

---

## 7. NI-VISA / NI-DCPower (System Drivers)

The toolkit talks to instruments through NI-VISA. NI-VISA install requires **admin rights**, so `setup-tamu.ps1` deliberately does not attempt it. On a TAMU managed machine, NI-VISA is usually pre-installed by lab IT. If it is missing, ask your TA - they can install it.

- **NI-VISA**: https://www.ni.com/en/support/downloads/drivers/download.ni-visa.html
- **NI-DCPower** (only for PXIe-4139 SMU labs): https://www.ni.com/en/support/downloads/drivers/download.ni-dcpower.html

You can confirm NI-VISA is installed by opening **NI MAX** and seeing your instruments listed under **Devices and Interfaces**.

---

## 8. Supported Python Versions by TestStand Release

| TestStand Release | Max Python Supported |
|---|---|
| 2025 Q3 | 3.13 |
| 2025 Q2 | 3.12 |
| 2025 Q1 | 3.12 |
| 2024 Q4 | 3.12 |
| 2023 Q4 | 3.11 |

To check your TestStand version: **Help > About TestStand**

We standardize on **3.12** in this guide because it is the latest version supported by every TestStand release from 2024 Q4 onwards.

---

## 9. Rebuilding the Venv

If you need to start over (corrupted install, wrong Python version baked in, etc.), the script handles this with the `-Recreate` flag:

```powershell
.\setup-teststand.ps1 -Recreate
```

Or do it manually:

```cmd
rem Delete old venv
rmdir /s /q H:\Documents\eset-453\.venv

rem Recreate with Python 3.12 (use the path from your install Option above)
"%LOCALAPPDATA%\Programs\Python\Python312\python.exe" -m venv H:\Documents\eset-453\.venv

rem Reinstall the toolkit (note: not on PyPI - install from GitHub)
H:\Documents\eset-453\.venv\Scripts\pip.exe install "git+https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git"
```

---

## Troubleshooting

### "Unable to load specified version of python"

TestStand cannot find `python312.dll`. Verify in a fresh terminal:

```powershell
where python
python -c "import ctypes.util; print(ctypes.util.find_library('python312'))"
```

If `where python` returns a path inside `C:\Program Files\WindowsApps\...`, you have the Microsoft Store stub - install a real Python via one of the [two options above](#2-install-a-real-python-312-no-admin-required).

If both commands succeed but TestStand still cannot load, **restart TestStand** - it caches PATH at launch.

### `Run-Time Error -17347: The expression cannot be empty`

You left a parameter slot blank in the **Arguments** tab of a TestStand Python step. TestStand introspects the function signature, creates a row for every parameter, and refuses to call the function until every row's **Value/Expression** column is filled in.

Open the step's settings → **Arguments** tab → fill every row. Literal values (`3`, `4.5`, `True`, `"hello"`) and TestStand expressions (`Locals.MyVar`, `Parameters.Voltage`) are both valid.

### Measurement = `0.0` when the Python function returns a non-zero value

For a **Numeric Limit Test** step using the Python adapter, the function's return value should populate `Step.Result.Numeric`, which is what the Limits comparison reads. If Measurement shows `0.0` even though your Python `print` shows the right value, walk through this list:

1. **Confirm the Arguments tab has a `Return Value` row.** Open the step's settings, **Arguments** tab. The first row must be `Name = Return Value`, `Value/Expression = Step.Result.Numeric`. If the row is missing, TestStand never introspected the function — open the **Module** tab, **re-pick the function from the Function Name dropdown** (don't type it). The Return Value row will populate. Verified against NI's bundled Python example on TestStand 2025 Q3.
2. **The function returns the value, not just prints it.** `print(voltage)` alone is not enough — the function body needs `return voltage`.
3. **The function signature matches what TestStand calls.** TestStand passes Arguments-tab values by name; `def get_voltage()` and `def get_voltage(**kwargs)` both work, but a function with required positional args you didn't fill in fails earlier with [-17347](#run-time-error-17347-the-expression-cannot-be-empty).
3. **The step type is Test - Numeric Limit Test, not Action.** Action steps don't have a measurement.
4. **The Numeric Measurement expression on the Limits tab is at its default.** The Python adapter wires the return value into `Step.Result.Numeric` for you; if someone edited that expression to read from somewhere else, restore the default.

### `ModuleNotFoundError: No module named 'lab_instruments'`

TestStand is running Python but not seeing your venv packages. Either:

1. Confirm the **Virtual environment** field in the TestStand Python adapter config points at `H:\Documents\eset-453\.venv` (not a UNC path).
2. Add the explicit `sys.path.insert(0, ...)` block from the [`teststand_instruments.py` example above](#6-calling-real-instruments-from-teststand) to the top of your module.
3. Verify the package is actually in the venv: `H:\Documents\eset-453\.venv\Scripts\pip.exe show scpi-instrument-toolkit`

### `find_all()` returns an empty dict

NI-VISA cannot see any instruments. Open **NI MAX** and confirm your devices appear under **Devices and Interfaces**. If MAX is empty too, the issue is upstream of the toolkit - check USB/GPIB cables, instrument power, and that NI-VISA is installed.

### `"\\server\share\..." is not supported`

You created the venv on a UNC path. Delete it and recreate on a mapped drive letter ([section 3](#3-create-a-venv-on-a-mapped-drive)).

### `ERROR: Could not find a version that satisfies the requirement scpi-instrument-toolkit`

You typed `pip install scpi-instrument-toolkit` (or any variant ending in just the bare name). The package is **not on PyPI**; pip is searching the index, finding nothing, and giving up. Install from the GitHub repo instead:

```cmd
H:\Documents\eset-453\.venv\Scripts\pip.exe install "git+https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git"
```

If pip then complains that `git` is missing, install git via `setup-tamu.ps1` first.

---

## Tips & Gotchas

Things that trip students up most often when wiring TestStand to this toolkit.

- **Use a real Python, not the Microsoft Store stub.** Store Python lives in `WindowsApps`, which TestStand cannot load `python3XX.dll` from. Install via `setup-tamu.ps1` (winget) or `py install 3.12` -- see [section 2](#2-install-a-real-python-312-no-admin-required).
- **Put the venv on `H:\`, never on a UNC path.** Type `H:\Documents\eset-453\.venv`, not `\\coe-fs.engr.tamu.edu\Ugrads\<NetID>\...`. TestStand and `cmd.exe` both refuse raw UNC working directories. See [section 3](#3-create-a-venv-on-a-mapped-drive).
- **Base Python directory must be on PATH, not just the venv `Scripts\`.** TestStand needs to load `python312.dll`, which lives in the **base install** (not in the venv's `Scripts\` folder). `setup-teststand.ps1` adds it for you. If you set things up manually, do it yourself and restart TestStand.
- **Restart TestStand after editing PATH.** TestStand reads PATH only at launch. Editing PATH in the middle of a TestStand session has no effect.
- **The function has to `return` the value -- not just `print` it.** For a Numeric Limit Test, the Python return value goes into `Step.Result.Numeric`. `print(voltage)` alone leaves Measurement at `0.0`.
- **Fill in every Arguments row.** A blank parameter cell raises `Run-Time Error -17347: The expression cannot be empty`. Use literal values, `Locals.X`, or `Parameters.Y`.
- **`pip install scpi-instrument-toolkit` does not work.** The package is not on PyPI. Always install with the `git+https://...` URL.
- **Verify the venv before wiring TestStand.** Run the `python312.dll` + `from lab_instruments import find_all` smoke test from [section 3](#verify-the-venv). If that fails on the command line, TestStand will fail the same way -- save yourself the dialog-box hunting.

---

## Related: LabVIEW Python Node

If you are also calling the toolkit from a LabVIEW VI, the **same venv** can be used. Point the LabVIEW Python Node at the same `H:\...\.venv` -- there is a worked walkthrough (including a student case study) on the [LabVIEW Bridge](labview.md) page.
