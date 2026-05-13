[CmdletBinding()]
param(
    [string]$ProjectName = "scpi-workspace",
    [string]$Drive = "H:",
    [switch]$Recreate,
    [switch]$NoPause
)

# setup-teststand.ps1
# Creates a TestStand-compatible Python venv on the user's network home drive
# (default H:) so it survives roaming-profile resets on TAMU managed machines,
# installs the toolkit into it, and validates that it actually works end-to-end.
#
# Run AFTER setup-tamu.ps1 (which installs Python 3.12 globally). Idempotent -
# rerun any time. Pass -Recreate to wipe and rebuild the venv.

function Wait-IfNeeded {
    if (-not $NoPause) {
        try { [void](Read-Host "Press Enter to close") } catch {}
    }
}

function Write-Step { param($n, $msg)
    Write-Host ""
    Write-Host "[$n] $msg" -ForegroundColor Cyan
    Write-Host ("-" * 60)
}

function Fail { param($msg)
    Write-Host ""
    Write-Host "ERROR: $msg" -ForegroundColor Red
    Wait-IfNeeded
    exit 1
}

Write-Host ("=" * 60)
Write-Host "  SCPI Toolkit - NI TestStand venv setup"
Write-Host "  No admin rights required"
Write-Host ("=" * 60)

# ---------------------------------------------------------------------------
# Step 1: Pick a project root that survives roaming-profile resets
# ---------------------------------------------------------------------------
Write-Step 1 "Choosing project root..."

$projectRoot = $null
$driveLetter = $Drive.TrimEnd(":").TrimEnd("\")
$drivePath   = "${driveLetter}:\"

if (Test-Path $drivePath) {
    $projectRoot = Join-Path $drivePath "Documents\$ProjectName"
    Write-Host "Mapped drive ${driveLetter}: detected." -ForegroundColor Green
    Write-Host "Project root: $projectRoot" -ForegroundColor Cyan

    # Detect that H: is a junction/redirect to a UNC share (TAMU lab default).
    # The venv still works, but tell the student up front so the warning Python
    # emits during venv creation is not alarming.
    try {
        $resolved = (Resolve-Path $drivePath -ErrorAction Stop).ProviderPath
        if ($resolved -like "\\*") {
            Write-Host ""
            Write-Host "NOTE: ${driveLetter}:\ on this machine is a junction to a UNC share:" -ForegroundColor Yellow
            Write-Host "      $resolved" -ForegroundColor Yellow
            Write-Host "Python may print a 'redirects, links or junctions' warning when it" -ForegroundColor Yellow
            Write-Host "creates the venv. This is informational - the venv WILL work." -ForegroundColor Yellow
        }
    } catch {
        # Ignore - if Resolve-Path fails we'll let venv creation surface a real error
    }
} else {
    $fallback = Join-Path $env:USERPROFILE "Documents\$ProjectName"
    Write-Host "Mapped drive ${driveLetter}: was not found." -ForegroundColor Yellow
    Write-Host "Falling back to local profile: $fallback" -ForegroundColor Yellow
    Write-Host "WARNING: On TAMU managed machines the local profile may reset on" -ForegroundColor Yellow
    Write-Host "         logout. If you have an H: drive but it is not connected," -ForegroundColor Yellow
    Write-Host "         cancel now (Ctrl+C), reconnect it, and rerun this script." -ForegroundColor Yellow
    $projectRoot = $fallback
}

New-Item -ItemType Directory -Force -Path $projectRoot | Out-Null
$venvPath = Join-Path $projectRoot ".venv"

# ---------------------------------------------------------------------------
# Step 2: Find a real Python 3.12 (not the Microsoft Store stub)
# ---------------------------------------------------------------------------
Write-Step 2 "Locating Python 3.12..."

$candidates = @(
    (Join-Path $env:LOCALAPPDATA "Programs\Python\Python312\python.exe"),   # winget / setup-tamu.ps1
    (Join-Path $env:LOCALAPPDATA "Python\pythoncore-3.12-64\python.exe")    # py install 3.12
)

$pythonExe = $null
foreach ($cand in $candidates) {
    if (Test-Path $cand) {
        # Make sure this is not the Store stub by checking it actually runs.
        $ver = & $cand --version 2>&1
        if ($LASTEXITCODE -eq 0 -and $ver -match "^Python 3\.12") {
            $pythonExe = $cand
            Write-Host "Found: $pythonExe  ($ver)" -ForegroundColor Green
            break
        }
    }
}

if (-not $pythonExe) {
    Fail @"
Could not find a real Python 3.12 install in a TestStand-compatible location.
Run setup-tamu.ps1 first, or install manually with:
    py install 3.12
Expected locations checked:
    %LOCALAPPDATA%\Programs\Python\Python312\python.exe
    %LOCALAPPDATA%\Python\pythoncore-3.12-64\python.exe
"@
}

# ---------------------------------------------------------------------------
# Step 3: Create the venv (recreate if asked, skip if usable)
# ---------------------------------------------------------------------------
Write-Step 3 "Creating venv at $venvPath..."

$venvPython = Join-Path $venvPath "Scripts\python.exe"

if (Test-Path $venvPath) {
    if ($Recreate) {
        Write-Host "Removing existing venv (-Recreate specified)..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force $venvPath
    } elseif (Test-Path $venvPython) {
        Write-Host "Venv already exists and looks usable. Skipping creation." -ForegroundColor Yellow
        Write-Host "(Pass -Recreate to wipe and rebuild.)" -ForegroundColor Yellow
    } else {
        Write-Host "Existing venv directory looks broken (no python.exe). Recreating..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force $venvPath
    }
}

if (-not (Test-Path $venvPython)) {
    & $pythonExe -m venv $venvPath
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path $venvPython)) {
        Fail "venv creation failed. See output above."
    }
    Write-Host "Venv created." -ForegroundColor Green
}

# ---------------------------------------------------------------------------
# Step 4: Install the toolkit into the venv
# ---------------------------------------------------------------------------
Write-Step 4 "Installing scpi-instrument-toolkit into the venv..."
Write-Host "(This can take several minutes on the TAMU network drive - be patient.)" -ForegroundColor Yellow
Write-Host "(The package is not on PyPI - we install directly from the GitHub repo.)" -ForegroundColor DarkGray

$pkgUrl = "git+https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git"
# Use `python -m pip` to upgrade pip: on Windows, invoking pip.exe to upgrade
# itself fails ("To modify pip, please run...") because pip cannot overwrite
# its own running .exe. Also avoid `2>&1` on native commands - in PowerShell
# 5.1 it wraps pip's stderr lines as NativeCommandError, burying the real
# error in a wall of red and confusing users.
& $venvPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    Fail "pip self-upgrade failed. See output above."
}
& $venvPython -m pip install $pkgUrl
if ($LASTEXITCODE -ne 0) {
    Fail @"
pip install failed. See output above. The toolkit is NOT on PyPI - it installs
from GitHub via:
    pip install "$pkgUrl"
Most common cause: git is not on PATH. Run setup-tamu.ps1 (which installs git)
or install git manually, then rerun this script.
"@
}

# ---------------------------------------------------------------------------
# Step 4.5: Ensure the base Python dir is on user PATH
# ---------------------------------------------------------------------------
# TestStand loads python312.dll by searching PATH (the same lookup
# ctypes.util.find_library('python312') performs). The base Python dir
# - NOT the venv's Scripts dir - is what holds python312.dll. If a
# previous setup-tamu.ps1 run did not persist this dir to user PATH (or
# the user has not started a fresh shell since), validation below would
# fail even though the venv itself works. Fix it proactively.
Write-Step "4.5" "Ensuring base Python dir is on user PATH..."

$pythonDir = Split-Path $pythonExe -Parent
$userPath  = [Environment]::GetEnvironmentVariable("Path", "User")
$onUserPath = $false
if ($userPath) {
    $onUserPath = (
        ($userPath -split ";") |
        ForEach-Object { $_.TrimEnd("\").ToLowerInvariant() }
    ) -contains $pythonDir.TrimEnd("\").ToLowerInvariant()
}

if ($onUserPath) {
    Write-Host "Already on user PATH: $pythonDir" -ForegroundColor Yellow
} else {
    Write-Host "Adding to user PATH: $pythonDir" -ForegroundColor Green
    if ([string]::IsNullOrWhiteSpace($userPath)) {
        [Environment]::SetEnvironmentVariable("Path", $pythonDir, "User")
    } else {
        [Environment]::SetEnvironmentVariable("Path", "$userPath;$pythonDir", "User")
    }
    Write-Host "NOTE: Restart TestStand (and any open terminals) after this script" -ForegroundColor Yellow
    Write-Host "      finishes so they pick up the new user PATH." -ForegroundColor Yellow
}

# Always refresh the current session so validation in step 5 sees the dir.
if (";$($env:Path);" -notlike "*;$pythonDir;*") {
    $env:Path = "$env:Path;$pythonDir"
}

# ---------------------------------------------------------------------------
# Step 5: Validate the venv works end-to-end
# ---------------------------------------------------------------------------
Write-Step 5 "Validating the venv..."

$validate = @"
import sys, ctypes.util
print('python:', sys.version.split()[0])
print('exe:', sys.executable)
dll = ctypes.util.find_library('python312')
print('python312.dll:', dll if dll else '<not found>')
assert dll, 'python312.dll not on PATH - TestStand will refuse to load this interpreter.'
from lab_instruments import find_all  # toolkit import smoke test
print('lab_instruments: OK')
"@

$tmpScript = New-TemporaryFile
$validate | Set-Content -Path $tmpScript -Encoding UTF8
try {
    & $venvPython $tmpScript
    if ($LASTEXITCODE -ne 0) {
        Fail "Venv validation failed. See output above."
    }
} finally {
    Remove-Item $tmpScript -Force -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "Venv validated. python.exe runs, python312.dll is on PATH, and the" -ForegroundColor Green
Write-Host "toolkit imports cleanly." -ForegroundColor Green

# ---------------------------------------------------------------------------
# Done - print TestStand adapter values to copy-paste
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host ("=" * 60)
Write-Host "  Done - paste these values into TestStand" -ForegroundColor Green
Write-Host ("=" * 60)
Write-Host ""
Write-Host "Configure > Adapters > Python > Configure"
Write-Host ""
Write-Host ("  Interpreter to use            : Global")
Write-Host ("  Virtual environment (optional): {0}" -f $venvPath)
Write-Host ("  Executable Path               : (leave blank - greyed out on managed machines)")
Write-Host ("  Version                       : 3.12")
Write-Host ""
Write-Host "Then restart TestStand so it re-reads PATH."
Write-Host ""
Write-Host "Full guide: https://t-o-m-tool-oauto-mationator.github.io/scpi-instrument-toolkit/teststand.html"
Write-Host ""

Wait-IfNeeded
