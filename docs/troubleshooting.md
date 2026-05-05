# Troubleshooting

## `scpi-repl` is not recognized

Pip installs `scpi-repl` to the Python `Scripts` folder, which may not be on your PATH. There are three scenarios:

---

### Standard Windows — self-healing fix

Run the module form once:

```powershell
python -m lab_instruments
```

The toolkit automatically adds the Scripts folder to your user PATH via the Windows registry (no admin required) and prints:

```text
[scpi] Added Python Scripts to your PATH (C:\...\Scripts).
[scpi] Open a new terminal and 'scpi-repl' will work.
```

Open a **new** PowerShell window and `scpi-repl` will work from then on.

---

### Managed machines (TAMU VOAL and similar)

On machines where group policy blocks user registry edits, the automatic fix above fails silently. Use one of these instead:

!!! tip "Permanent workaround — always launch with the module form"
    ```powershell
    python -m lab_instruments
    python -m lab_instruments --mock
    ```
    All flags work the same way. This is the recommended method on any machine where you cannot permanently modify PATH.

!!! note "Session-only PATH fix — enables `scpi-repl` for this terminal window"
    ```powershell
    $pyPath = python -c "import sys, os; print(os.path.join(sys.prefix, 'Scripts'))"
    $env:Path += ";$pyPath"
    scpi-repl
    ```
    You'll need to run these two lines again each time you open a new terminal.

---

## Serial port permission denied (Linux)

On Linux, serial ports (`/dev/ttyUSB*`, `/dev/ttyACM*`) are owned by a system group. Your user must be in that group or you will get a `Permission denied` error when connecting to serial instruments (Matrix MPS, JDS6600, etc.).

### Arch Linux — group is `uucp`

```bash
sudo usermod -aG uucp $USER
```

### Debian / Ubuntu / Raspberry Pi OS — group is `dialout`

```bash
sudo usermod -aG dialout $USER
```

After running the command, **log out and log back in** (or reboot) for the group membership to take effect. Verify with:

```bash
groups   # should include uucp or dialout
```

!!! tip "Check which group owns the port"
    ```bash
    ls -l /dev/ttyUSB0
    # crw-rw---- 1 root uucp 188, 0 ...
    ```
    The fourth field (after owner) is the owning group.

---

## NI PXIe-4139 not detected

The PXIe chassis must be powered on **before** the host PC boots. PXIe devices are enumerated during BIOS/POST — if the chassis powers on after the PC, the instrument will not appear in `scan` or `list`. Power cycle the PC with the chassis already on to fix this.

This is standard PXIe bus behavior: the host enumerates PCIe devices at startup and does not hot-scan later. It is a common gotcha for students and new users who expect plug-and-play behavior.

---

## NI-VISA not found

The toolkit needs [NI-VISA](https://www.ni.com/en/support/downloads/drivers/download.ni-visa.html) to communicate with instruments over USB or GPIB. If you see an error about VISA not being found, download and install NI-VISA from the link above, then restart your terminal and try again.

If you just want to explore the tool without any hardware, use mock mode — no VISA required:

```powershell
python -m lab_instruments --mock
```

---

## "Resource busy" / instrument already in use

Instrument connections are exclusive. Only one program can hold a connection to a device at a time. Common causes:

- **REPL + Python script open at the same time** targeting the same instrument
- **REPL or Python script open while BQStudio is connected** to the EV2300 (or any other TI/vendor tool that holds the USB connection)
- **A previous script that crashed** without calling `disconnect()`, leaving the VISA session open

**Fix:** close the other program first, then retry. If a crashed script left a session open, restart your terminal -- the VISA session is tied to the Python process and will be released when the process exits.

!!! tip "Using the EV2300 with BQStudio"
    The EV2300A USB-to-I2C adapter can only be claimed by one application at a time. If you need to use BQStudio for firmware flashing or register browsing, close the REPL or stop your script first. When you are done in BQStudio, close it before re-running your script or REPL.

---

## First-time setup on TAMU / managed Windows machines

If you are starting from scratch on a managed machine, use the all-in-one setup script — it installs GitHub Desktop (including git), Python, and the toolkit in one step with no admin rights.

!!! warning "Review the script before running"
    Always inspect a script before piping it to `iex`. Download and read `setup-tamu.ps1` from the repository first, then run it locally.

```powershell
# Preferred: clone the repo and run from disk
.\setup-tamu.ps1
```

Or if you just want a one-liner and have reviewed the script source:

```powershell
irm "https://raw.githubusercontent.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit/main/setup-tamu.ps1" | iex
```

Or if you have already cloned the repo:

```powershell
.\setup-tamu.ps1
```

---

## DOCX/PPTX preview in the GUI says "LibreOffice is required"

The GUI's Office document viewer shells out to LibreOffice's `soffice --headless --convert-to pdf` to render `.docx` and `.pptx` files. Every other feature works without it.

`setup-tamu.ps1` installs LibreOffice via `msiexec /a` (administrative extract — no admin rights required) into `%LOCALAPPDATA%\Programs\LibreOffice` as its Step 9. Re-run the setup script to retry, or install manually:

```powershell
$url = "https://download.documentfoundation.org/libreoffice/stable/26.2.2/win/x86_64/LibreOffice_26.2.2_Win_x86-64.msi"
$msi = "$env:TEMP\LibreOffice.msi"
$dir = "$env:LOCALAPPDATA\Programs\LibreOffice"
Invoke-WebRequest -Uri $url -OutFile $msi -UseBasicParsing
msiexec.exe /a "$msi" /qn TARGETDIR="$dir"
```

After extraction, `soffice.exe` lands at `$dir\program\soffice.exe`. The GUI looks for it there automatically; the setup script also appends the directory to your user `PATH` so `soffice --headless --convert-to pdf` works from any new shell.

---

## `git` is not recognized on managed Windows machines

If you only need to fix git (Python and the toolkit are already installed), use the smaller helper script (no admin needed):

```powershell
.\setup-git.ps1
```

What the script does:

- Locates GitHub Desktop's bundled `git.exe` dynamically (supports changing `app-x.y.z` folders)
- Adds only the `...\git\cmd` directory to your **user** PATH
- Skips duplicate PATH entries safely

After running it, open a **new** terminal and verify:

```powershell
git --version
```

If you cannot run scripts, use this one-liner in PowerShell:

```powershell
$g=(Get-ChildItem "$env:LOCALAPPDATA\GitHubDesktop\app-*\resources\app\git\cmd\git.exe" -EA 0|Sort-Object LastWriteTime -Desc|Select-Object -First 1); if(-not $g){$g=(Get-ChildItem "$env:LOCALAPPDATA\GitHubDesktop" -Filter git.exe -Recurse -EA 0|?{$_.DirectoryName -like "*\git\cmd"}|Sort-Object LastWriteTime -Desc|Select-Object -First 1)}; if(-not $g){Write-Host "GitHub Desktop Git not found" -FG Red}else{$p=$g.DirectoryName;$u=[Environment]::GetEnvironmentVariable('Path','User'); if(($u -split ';'|%{$_.TrimEnd('\\').ToLowerInvariant()}) -notcontains $p.TrimEnd('\\').ToLowerInvariant()){[Environment]::SetEnvironmentVariable('Path',($(if([string]::IsNullOrWhiteSpace($u)){$p}else{"$u;$p"})),'User')}; Write-Host "Done. Open a new terminal and run: git --version" -FG Green}
```

---

## LabVIEW: "attempted relative import with no known parent package"

This error appears in LabVIEW's Python Node error cluster when the function name is `open_ev2300` (or any other bridge function) and the full class is `ImportError`.

**Cause:** LabVIEW loads the `.py` file by its absolute path as a standalone script. That strips the package context (`__package__ = None`), so every `from .xyz import` statement inside `lab_instruments/src/labview_bridge.py` fails immediately.

**Fix:** Upgrade to version 1.0.5 or later, which patches the file to handle standalone loads:

```powershell
pip install --upgrade git+https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git
```

If you cannot upgrade (e.g. a managed machine with no internet access), use the top-level shim instead. Change the Python Node's module path from:

```text
...\site-packages\lab_instruments\src\labview_bridge.py
```

to the `labview_bridge.py` at the repository root:

```text
C:\path\to\scpi-instrument-toolkit\labview_bridge.py
```

The shim sets up the correct import context before delegating to the real bridge. All function names remain the same.

See [LabVIEW Bridge - Troubleshooting](labview.md#troubleshooting) for more details.

---

## EV2300 communication errors

### "Device error (0x46)" or I2C read/write failures

The EV2300 USB-to-I2C bridge can get into a bad state. Run `ev2300 fix` in the REPL for step-by-step recovery, or follow these steps:

1. Make sure the BQ EVM board is powered (e.g. PSU set to 18V)
2. Press the **BOOT** button on the BQ EVM board
3. `disconnect ev2300`
4. `scan`
5. Retry your command

If it still doesn't work, unplug the EV2300 USB cable, plug it back in, then `disconnect ev2300`, `scan`, and retry.

### EV2300 detected but cannot connect

Another program (e.g. **BQ Studio**) likely has the EV2300 HID handle open. Close it and run `scan` again. Only one program can use the EV2300 at a time.

See [EV2300 Troubleshooting](ev2300.md#troubleshooting) for more details.

### BQ76920 CC_CFG stays 0x00 after BOOT (open-source bridge firmware only)

If you are using the open-source [BQ76920_Bridge](https://github.com/T-O-M-Tool-Oauto-Mationator/BQ76920_Bridge) firmware (the STM32F405 replacement for the TI EV2300/EV2400) and `ev2300 read_byte 0x08 0x0B` returns `0x00` instead of `0x19` after pressing BOOT on the EVM, the bridge's automatic re-init is not firing. The fix until firmware is patched: write the init values from the host:

```bash
ev2300 write_byte 0x08 0x00 0xFF   # clear SYS_STAT fault latches (write-1-to-clear, SLUSBK2I Table 8-3)
ev2300 write_byte 0x08 0x0B 0x19   # CC_CFG = 0x19 (SLUSBK2I sec 8.5 Register Maps requires this)
ev2300 write_byte 0x08 0x04 0x10   # SYS_CTRL1 ADC_EN (bit 4, SLUSBK2I Table 8-7)
ev2300 write_byte 0x08 0x05 0x40   # SYS_CTRL2 CC_EN (bit 6, SLUSBK2I Table 8-8)
ev2300 write_byte 0x08 0x00 0xFF   # clear any UV/OV that latched on first ADC frame
```

Verify CC_CFG = 0x19 with `ev2300 read_byte 0x08 0x0B` before doing measurements. The genuine TI EV2300/EV2400 with bqStudio handles this automatically and is unaffected.

### After `scan`, BQ goes silent (PSU was disabled)

The REPL applies a "safe state" to every discovered instrument on startup. For the HP E3631A this means `OUTPUT:STATE OFF` plus zeroing all channel setpoints. If the BQ EVM was running on that PSU before you launched the REPL, the BQ now has no rail and falls into SHIP mode within seconds. Subsequent `ev2300 read_*` commands will return `Device error (0x46)`.

Recovery, in order, after `scan`:

```bash
psu set 2 18.0 0.5            # reconfigure P25V to 18 V / 0.5 A
psu chan 2 on                  # re-enable output
ev2300 wait_for_bq 30          # press BOOT on the EVM during this 30 s window
ev2300 read_byte 0x08 0x0B     # confirm BQ is up; expect 0x19 once init runs
```

A future REPL flag may let you skip the PSU safe-state when an EV2300 is also present; until then, the four lines above are the canonical recovery.
