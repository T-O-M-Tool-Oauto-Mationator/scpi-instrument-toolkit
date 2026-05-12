# NI TestStand Setup

This page is for students and engineers who want to drive the toolkit from **NI TestStand** on a TAMU lab machine (or any Windows machine without admin rights).

If you are only using the REPL or the Python API directly, you do not need any of this. See [Installation](install.md).

---

## Environment

- **Machine**: TAMU managed machine (no admin rights)
- **TestStand version**: 2025 Q1 (25.0.0) - 64-bit
- **Python version**: 3.12 (64-bit)
- **Project path**: your mapped drive + project folder (for example `H:\Documents\eset-453\`)
- **Mapped drive**: `H:\` points to your TAMU network home directory

> Replace `H:\Documents\eset-453\` with your own mapped drive letter and project path throughout this guide.

---

## Why Microsoft Store Python Does Not Work

The Microsoft Store versions of Python (3.12, 3.13, etc.) use **app execution aliases** - stub launchers that redirect to the real installation in `C:\Program Files\WindowsApps\...`, which is a protected directory. TestStand's Python adapter needs to load `python3XX.dll` directly, and that DLL is not accessible when Python is installed from the Store.

You can verify this yourself by running:

```python
import ctypes.util
print(ctypes.util.find_library('python3.12'))  # prints None for Store installs
```

TestStand hits the same wall - it cannot find or load the DLL, and will show:

> Unable to load specified version of python. Make sure python of proper bitness is installed and added to PATH environment variable.

---

## Python Installation (No Admin Required)

The **Python install manager** (`py` command, pre-installed on TAMU lab machines as a Windows app alias) can install a real Python to your user profile without admin rights.

Open a terminal and run:

```
py install 3.12
```

This installs Python 3.12 to:

```
C:\Users\<YourNetID>\AppData\Local\Python\pythoncore-3.12-64\
```

The Python DLL (`python312.dll`) lives in that directory.

### Add the DLL Directory to Your User PATH

TestStand needs `python312.dll` on the PATH to load the interpreter. Run this in PowerShell (no admin needed - modifies user PATH only):

```powershell
$currentPath = [System.Environment]::GetEnvironmentVariable('PATH', 'User')
$newDir = "C:\Users\$env:USERNAME\AppData\Local\Python\pythoncore-3.12-64"
[System.Environment]::SetEnvironmentVariable('PATH', $newDir + ';' + $currentPath, 'User')
```

**Restart TestStand after this** - it reads the PATH only at launch.

---

## Virtual Environment

### Why You Must Use a Mapped Drive Letter (Not a UNC Path)

Python and TestStand both have known issues with UNC paths (`\\server\share\...`) as working directories. Windows will refuse with "UNC paths are not supported" when Python tries to operate from one.

- DO NOT use: `\\coe-fs.engr.tamu.edu\Ugrads\<NetID>\Documents\eset-453\.venv`
- USE instead: `H:\Documents\eset-453\.venv`

Your TAMU home directory is already mapped to a drive letter (`H:` by default). Use that.

### Create the Venv

```cmd
C:\Users\<YourNetID>\AppData\Local\Python\pythoncore-3.12-64\python.exe -m venv H:\Documents\eset-453\.venv
```

### Install the Toolkit

```cmd
H:\Documents\eset-453\.venv\Scripts\pip.exe install scpi-instrument-toolkit
```

If your lab has its own `requirements.txt`, install that instead:

```cmd
H:\Documents\eset-453\.venv\Scripts\pip.exe install -r H:\Documents\eset-453\requirements.txt
```

> **Note:** Both commands write to the TAMU network drive, which is slow. The venv creation
> takes 30-60 seconds and the pip install can take several minutes depending on network
> conditions. This is normal - do not cancel. Wait for the prompt to return before continuing.

---

## TestStand Python Adapter Configuration

Open TestStand, then go to **Configure > Adapters > Python > Configure**

| Field | Value |
|---|---|
| Interpreter to use | Global |
| Virtual environment (optional) | `H:\Documents\eset-453\.venv` |
| Executable Path | *(greyed out on managed machines - leave blank)* |
| Version | `3.12` |

### Notes

- The **Version** dropdown is editable - click it and type `3.12` directly if it does not appear in the list.
- The **Executable Path** field is locked on TAMU managed machines. This is only used for step-into debugging anyway, not for normal test execution.
- TestStand embeds the Python DLL at runtime via PATH - it does **not** invoke `python.exe` directly to run code modules.
- The venv path must use a mapped drive letter (`H:\...`), not a UNC path. See above.

---

## Supported Python Versions by TestStand Release

| TestStand Release | Max Python Supported |
|---|---|
| 2025 Q3 | 3.13 |
| 2025 Q2 | 3.12 |
| 2025 Q1 | 3.12 |
| 2024 Q4 | 3.12 |
| 2023 Q4 | 3.11 |

To check your TestStand version: **Help > About TestStand**

---

## Rebuilding the Venv

If you need to start over:

```cmd
rem Delete old venv
rmdir /s /q H:\Documents\eset-453\.venv

rem Recreate with Python 3.12
C:\Users\<YourNetID>\AppData\Local\Python\pythoncore-3.12-64\python.exe -m venv H:\Documents\eset-453\.venv

rem Reinstall the toolkit
H:\Documents\eset-453\.venv\Scripts\pip.exe install scpi-instrument-toolkit
```
