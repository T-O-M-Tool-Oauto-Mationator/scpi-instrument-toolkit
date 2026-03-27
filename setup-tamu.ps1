param(
    [switch]$NoPause
)

function Wait-IfNeeded {
    if (-not $NoPause) {
        try {
            [void](Read-Host "Press Enter to close")
        } catch {
            # Ignore pause failures in non-interactive hosts.
        }
    }
}

function Write-Step { param($n, $msg)
    Write-Host ""
    Write-Host "[$n] $msg" -ForegroundColor Cyan
    Write-Host ("-" * 60)
}

Write-Host ("=" * 60)
Write-Host "  SCPI Toolkit - TAMU Managed Machine Setup"
Write-Host "  No admin rights required"
Write-Host ("=" * 60)

# ---------------------------------------------------------------------------
# Step 1: Install GitHub Desktop (includes bundled git) via winget
# ---------------------------------------------------------------------------
Write-Step 1 "Installing GitHub Desktop (includes git)..."

if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Host "winget is not available on this machine." -ForegroundColor Red
    Write-Host "Install 'App Installer' from the Microsoft Store, then re-run this script." -ForegroundColor Yellow
    Wait-IfNeeded
    exit 1
}

$ghInstalled = winget list --id GitHub.GitHubDesktop --accept-source-agreements 2>$null |
    Select-String "GitHub.GitHubDesktop"

if ($ghInstalled) {
    Write-Host "GitHub Desktop is already installed. Skipping." -ForegroundColor Yellow
} else {
    Write-Host "Installing GitHub Desktop (user scope, no admin)..."
    winget install GitHub.GitHubDesktop `
        --scope user `
        --accept-package-agreements `
        --accept-source-agreements `
        --silent
    if ($LASTEXITCODE -ne 0) {
        Write-Host "GitHub Desktop installation failed. Check winget output above." -ForegroundColor Red
        Wait-IfNeeded
        exit 1
    }
    Write-Host "GitHub Desktop installed." -ForegroundColor Green
}

# ---------------------------------------------------------------------------
# Step 2: Install Git for Windows (Git Bash) via winget
# ---------------------------------------------------------------------------
Write-Step 2 "Installing Git for Windows (Git Bash)..."

$gitForWindowsInstalled = winget list --id Git.Git --accept-source-agreements 2>$null |
    Select-String "Git.Git"

if ($gitForWindowsInstalled) {
    Write-Host "Git for Windows is already installed. Skipping." -ForegroundColor Yellow
} else {
    Write-Host "Installing Git for Windows (user scope, no admin)..."
    winget install Git.Git `
        --scope user `
        --accept-package-agreements `
        --accept-source-agreements `
        --silent
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Git for Windows installation failed. git from GitHub Desktop will be used instead." -ForegroundColor Yellow
    } else {
        Write-Host "Git for Windows (Git Bash) installed." -ForegroundColor Green
    }
}

# ---------------------------------------------------------------------------
# Step 3: Add GitHub Desktop's bundled git to user PATH (fallback)
# ---------------------------------------------------------------------------
Write-Step 3 "Adding GitHub Desktop's bundled git to user PATH (fallback)..."

$desktopRoot = Join-Path $env:LOCALAPPDATA "GitHubDesktop"
$gitExe = $null

if (Test-Path $desktopRoot) {
    $gitExe = Get-ChildItem -Path "$desktopRoot\app-*\resources\app\git\cmd\git.exe" `
                  -ErrorAction SilentlyContinue |
              Sort-Object LastWriteTime -Descending |
              Select-Object -First 1

    if (-not $gitExe) {
        $gitExe = Get-ChildItem -Path $desktopRoot -Filter git.exe -Recurse `
                      -ErrorAction SilentlyContinue |
                  Where-Object { $_.DirectoryName -like "*\git\cmd" } |
                  Sort-Object LastWriteTime -Descending |
                  Select-Object -First 1
    }
}

if (-not $gitExe) {
    Write-Host "git.exe not found inside GitHub Desktop." -ForegroundColor Yellow
    Write-Host "Open GitHub Desktop once to finish its setup, then re-run this script." -ForegroundColor Yellow
} else {
    $gitCmdPath = $gitExe.DirectoryName          # …\git\cmd
    $gitRootPath = Split-Path $gitCmdPath -Parent # …\git  (contains git-bash.exe)
    $userPath   = [Environment]::GetEnvironmentVariable("Path", "User")
    $parts = @()
    if ($userPath) {
        $parts = $userPath -split ";" | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" }
    }

    foreach ($addPath in @($gitCmdPath, $gitRootPath)) {
        $alreadyPresent = $false
        foreach ($p in $parts) {
            if ($p.TrimEnd('\').ToLowerInvariant() -eq $addPath.TrimEnd('\').ToLowerInvariant()) {
                $alreadyPresent = $true; break
            }
        }
        if ($alreadyPresent) {
            Write-Host "Already on user PATH: $addPath" -ForegroundColor Yellow
        } else {
            $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
            $newPath = if ([string]::IsNullOrWhiteSpace($currentPath)) { $addPath } else { "$currentPath;$addPath" }
            [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
            $parts += $addPath
            Write-Host "Added to user PATH: $addPath" -ForegroundColor Green
        }
    }

    $gitVersion = & "$($gitExe.FullName)" --version 2>$null
    if ($gitVersion) { Write-Host "Detected: $gitVersion" -ForegroundColor Cyan }

    $gitBashExe = Join-Path $gitRootPath "git-bash.exe"
    if (Test-Path $gitBashExe) {
        Write-Host "Git Bash available at: $gitBashExe" -ForegroundColor Cyan
        Write-Host "(Now on PATH — open a new terminal and type: git-bash)" -ForegroundColor Cyan
    }
}

# ---------------------------------------------------------------------------
# Step 3: Install Python via winget
# ---------------------------------------------------------------------------
Write-Step 4 "Checking / installing Python..."

$pythonOk = $false
try {
    $v = & python --version 2>$null
    if ($LASTEXITCODE -eq 0 -and $v) { $pythonOk = $true; Write-Host "Python already available: $v" -ForegroundColor Yellow }
} catch {}

if (-not $pythonOk) {
    Write-Host "Installing Python 3.12 (user scope, no admin)..."
    winget install Python.Python.3.12 `
        --scope user `
        --accept-package-agreements `
        --accept-source-agreements `
        --silent
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Python installation failed. Check winget output above." -ForegroundColor Red
        Wait-IfNeeded
        exit 1
    }
    Write-Host "Python installed." -ForegroundColor Green
}

# ---------------------------------------------------------------------------
# Step 4: Refresh PATH in current session
# ---------------------------------------------------------------------------
Write-Step 5 "Refreshing PATH in current session..."

$machinePath = [Environment]::GetEnvironmentVariable("Path", "Machine")
$userPath2   = [Environment]::GetEnvironmentVariable("Path", "User")
$env:Path    = "$machinePath;$userPath2"
Write-Host "PATH refreshed." -ForegroundColor Green

# ---------------------------------------------------------------------------
# Step 5: pip install scpi-instrument-toolkit
# ---------------------------------------------------------------------------
Write-Step 6 "Installing scpi-instrument-toolkit..."

$pipCmd = $null
if (Get-Command pip -ErrorAction SilentlyContinue)         { $pipCmd = "pip" }
elseif (Get-Command pip3 -ErrorAction SilentlyContinue)    { $pipCmd = "pip3" }
elseif (Get-Command python -ErrorAction SilentlyContinue)  { $pipCmd = "python -m pip" }

if (-not $pipCmd) {
    Write-Host "pip not found. Open a NEW terminal and run:" -ForegroundColor Yellow
    Write-Host "  pip install git+https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git" -ForegroundColor White
} else {
    $installArgs = @(
        "install",
        "git+https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git"
    )
    if ($pipCmd -eq "python -m pip") {
        & python -m pip @installArgs
    } else {
        & $pipCmd @installArgs
    }

    if ($LASTEXITCODE -eq 0) {
        Write-Host "scpi-instrument-toolkit installed." -ForegroundColor Green
    } else {
        Write-Host "pip install failed. Try running in a new terminal:" -ForegroundColor Red
        Write-Host "  pip install git+https://github.com/T-O-M-Tool-Oauto-Mationator/scpi-instrument-toolkit.git" -ForegroundColor White
    }
}

# ---------------------------------------------------------------------------
# Step 7: Explicitly install nidcpower (Python bindings, no admin needed)
# ---------------------------------------------------------------------------
Write-Step 7 "Installing nidcpower Python bindings..."

if (-not $pipCmd) {
    Write-Host "pip not found — open a NEW terminal and run:" -ForegroundColor Yellow
    Write-Host "  pip install nidcpower" -ForegroundColor White
} else {
    if ($pipCmd -eq "python -m pip") {
        & python -m pip install "nidcpower>=1.5.0"
    } else {
        & $pipCmd install "nidcpower>=1.5.0"
    }

    if ($LASTEXITCODE -eq 0) {
        Write-Host "nidcpower installed." -ForegroundColor Green
    } else {
        Write-Host "nidcpower install failed. Try in a new terminal:" -ForegroundColor Red
        Write-Host "  pip install nidcpower" -ForegroundColor White
    }
}

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host ("=" * 60)
Write-Host "  Setup complete!" -ForegroundColor Green
Write-Host ("=" * 60)
Write-Host ""
Write-Host "Open a NEW terminal and verify:" -ForegroundColor Cyan
Write-Host "  git --version"
Write-Host "  python --version"
Write-Host "  scpi-repl --mock"
Write-Host ""
Write-Host "NOTE: For real instruments you also need NI-VISA and NI-DCPower system drivers (require admin)." -ForegroundColor Yellow
Write-Host "      NI-VISA:    https://www.ni.com/en/support/downloads/drivers/download.ni-visa.html" -ForegroundColor Yellow
Write-Host "      NI-DCPower: https://www.ni.com/en/support/downloads/drivers/download.ni-dcpower.html" -ForegroundColor Yellow
Write-Host ""

Wait-IfNeeded
