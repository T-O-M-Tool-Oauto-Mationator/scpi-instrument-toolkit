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

```
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

## NI-VISA not found

The toolkit needs [NI-VISA](https://www.ni.com/en/support/downloads/drivers/download.ni-visa.html) to communicate with instruments over USB or GPIB. If you see an error about VISA not being found, download and install NI-VISA from the link above, then restart your terminal and try again.

If you just want to explore the tool without any hardware, use mock mode — no VISA required:

```powershell
python -m lab_instruments --mock
```

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
