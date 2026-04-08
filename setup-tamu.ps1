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
    Write-Host "Installing GitHub Desktop..."
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
    Write-Host "Installing Git for Windows..."
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

# Add Git for Windows to user PATH (winget --scope user installs to %LOCALAPPDATA%\Programs\Git)
$gitWinRoot = Join-Path $env:LOCALAPPDATA "Programs\Git"
$gitWinCmd  = Join-Path $gitWinRoot "cmd"
if (Test-Path (Join-Path $gitWinCmd "git.exe")) {
    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    $parts = @()
    if ($userPath) { $parts = $userPath -split ";" | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" } }

    # Include usr\bin so bash.exe is on PATH directly (required by Claude Code)
    $gitUsrBin = Join-Path $gitWinRoot "usr\bin"
    foreach ($addPath in @($gitWinCmd, $gitWinRoot, $gitUsrBin)) {
        $already = $parts | Where-Object { $_.TrimEnd('\').ToLowerInvariant() -eq $addPath.TrimEnd('\').ToLowerInvariant() }
        if ($already) {
            Write-Host "Already on PATH: $addPath" -ForegroundColor Yellow
        } else {
            $cur = [Environment]::GetEnvironmentVariable("Path", "User")
            if ([string]::IsNullOrWhiteSpace($cur)) {
                [Environment]::SetEnvironmentVariable("Path", $addPath, "User")
            } else {
                [Environment]::SetEnvironmentVariable("Path", "$cur;$addPath", "User")
            }
            $env:Path = "$env:Path;$addPath"
            $parts += $addPath
            Write-Host "Added to user PATH: $addPath" -ForegroundColor Green
        }
    }

    $gitBash = Join-Path $gitWinRoot "git-bash.exe"
    if (Test-Path $gitBash) {
        Write-Host "Git Bash available — open a new terminal and type: git-bash" -ForegroundColor Cyan
    }

    # Set CLAUDE_CODE_GIT_BASH_PATH — try usr\bin\bash.exe first, then bin\bash.exe
    $bashExe = Join-Path $gitWinRoot "usr\bin\bash.exe"
    if (-not (Test-Path $bashExe)) {
        $bashExe = Join-Path $gitWinRoot "bin\bash.exe"
    }
    if (Test-Path $bashExe) {
        [Environment]::SetEnvironmentVariable("CLAUDE_CODE_GIT_BASH_PATH", $bashExe, "User")
        $env:CLAUDE_CODE_GIT_BASH_PATH = $bashExe
        Write-Host "Set CLAUDE_CODE_GIT_BASH_PATH=$bashExe" -ForegroundColor Green
    } else {
        Write-Host "bash.exe not found under $gitWinRoot — Claude Code may not work" -ForegroundColor Yellow
    }
} else {
    Write-Host "Git for Windows not found at $gitWinRoot — will fall back to GitHub Desktop git." -ForegroundColor Yellow
}

# ---------------------------------------------------------------------------
# Step 3: Install GitHub CLI (gh) via winget
# ---------------------------------------------------------------------------
Write-Step 3 "Installing GitHub CLI (gh)..."

$ghInstallDir = Join-Path $env:LOCALAPPDATA "Programs\gh"
$ghExe        = Join-Path $ghInstallDir "gh.exe"

if (Test-Path $ghExe) {
    Write-Host "GitHub CLI already installed at $ghExe. Skipping." -ForegroundColor Yellow
} else {
    # gh winget package is machine-scope only — download portable zip instead
    Write-Host "Downloading GitHub CLI portable zip..."
    try {
        $ghRelease  = Invoke-RestMethod "https://api.github.com/repos/cli/cli/releases/latest"
        $ghAsset    = $ghRelease.assets | Where-Object { $_.name -like "*windows_amd64.zip" } | Select-Object -First 1
        $ghZip      = Join-Path $env:TEMP "gh_windows_amd64.zip"
        Invoke-WebRequest -Uri $ghAsset.browser_download_url -OutFile $ghZip -UseBasicParsing
        New-Item -ItemType Directory -Force -Path $ghInstallDir | Out-Null
        Expand-Archive -Path $ghZip -DestinationPath $ghInstallDir -Force
        # The zip extracts into a versioned subfolder — move gh.exe up
        $extracted = Get-ChildItem -Path $ghInstallDir -Filter "gh.exe" -Recurse | Select-Object -First 1
        if ($extracted -and $extracted.FullName -ne $ghExe) {
            Copy-Item $extracted.FullName $ghExe -Force
        }
        Remove-Item $ghZip -Force -ErrorAction SilentlyContinue
        Write-Host "GitHub CLI installed." -ForegroundColor Green
    } catch {
        Write-Host "GitHub CLI install failed: $_" -ForegroundColor Yellow
    }
}

# Add gh to user PATH
if (Test-Path $ghExe) {
    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    $parts = @()
    if ($userPath) { $parts = $userPath -split ";" | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" } }
    $already = $parts | Where-Object { $_.TrimEnd("\").ToLowerInvariant() -eq $ghInstallDir.TrimEnd("\").ToLowerInvariant() }
    if (-not $already) {
        if ([string]::IsNullOrWhiteSpace($userPath)) {
            [Environment]::SetEnvironmentVariable("Path", $ghInstallDir, "User")
        } else {
            [Environment]::SetEnvironmentVariable("Path", "$userPath;$ghInstallDir", "User")
        }
        $env:Path = "$env:Path;$ghInstallDir"
        Write-Host "Added gh to user PATH: $ghInstallDir" -ForegroundColor Green
    } else {
        Write-Host "gh already on PATH." -ForegroundColor Yellow
    }
}

# ---------------------------------------------------------------------------
# Step 4: Add GitHub Desktop's bundled git to user PATH (fallback)
# ---------------------------------------------------------------------------
Write-Step 4 "Adding GitHub Desktop's bundled git to user PATH (fallback)..."

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
            if ([string]::IsNullOrWhiteSpace($currentPath)) {
                [Environment]::SetEnvironmentVariable("Path", $addPath, "User")
            } else {
                [Environment]::SetEnvironmentVariable("Path", "$currentPath;$addPath", "User")
            }
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
# Step 5: Install Python via winget
# ---------------------------------------------------------------------------
Write-Step 5 "Checking / installing Python..."

$pythonOk = $false
$pythonVersion = $null
try {
    $v = & python --version 2>$null
    if ($LASTEXITCODE -eq 0 -and $v) {
        $pythonOk = $true
        $pythonVersion = $v
        Write-Host "Python already available: $v" -ForegroundColor Yellow
    }
} catch {}

if (-not $pythonOk) {
    try {
        $v = & py -3 --version 2>$null
        if ($LASTEXITCODE -eq 0 -and $v) {
            $pythonOk = $true
            $pythonVersion = $v
            Write-Host "Python launcher already available: $v" -ForegroundColor Yellow
        }
    } catch {}
}

if (-not $pythonOk) {
    Write-Host "Installing Python 3.12..."
    winget install Python.Python.3.12 `
        --scope user `
        --accept-package-agreements `
        --accept-source-agreements `
        --silent

    $pythonWingetExit = $LASTEXITCODE
    if ($pythonWingetExit -ne 0) {
        Write-Host "winget Python install failed (exit code: $pythonWingetExit)." -ForegroundColor Yellow
        Write-Host "Falling back to python.org per-user installer..." -ForegroundColor Yellow

        $pyInstallerVersion = "3.12.10"
        $pyInstallerUrl = "https://www.python.org/ftp/python/$pyInstallerVersion/python-$pyInstallerVersion-amd64.exe"
        $pyInstallerPath = Join-Path $env:TEMP "python-$pyInstallerVersion-amd64.exe"

        try {
            Invoke-WebRequest -Uri $pyInstallerUrl -OutFile $pyInstallerPath -UseBasicParsing
            $pyInstallArgs = @(
                "/quiet",
                "InstallAllUsers=0",
                "PrependPath=1",
                "Include_launcher=1",
                "SimpleInstall=1",
                "Shortcuts=0"
            )
            $pyProc = Start-Process -FilePath $pyInstallerPath -ArgumentList $pyInstallArgs -Wait -NoNewWindow -PassThru
            if ($pyProc.ExitCode -ne 0) {
                Write-Host "python.org installer failed with exit code $($pyProc.ExitCode)." -ForegroundColor Yellow
            }
        } catch {
            Write-Host "python.org installer fallback failed: $_" -ForegroundColor Yellow
        } finally {
            Remove-Item $pyInstallerPath -Force -ErrorAction SilentlyContinue
        }
    }

    # Refresh current session PATH before re-checking Python.
    $machinePath = [Environment]::GetEnvironmentVariable("Path", "Machine")
    $userPath2   = [Environment]::GetEnvironmentVariable("Path", "User")
    $env:Path    = "$machinePath;$userPath2"

    try {
        $v = & python --version 2>$null
        if ($LASTEXITCODE -eq 0 -and $v) {
            $pythonOk = $true
            $pythonVersion = $v
        }
    } catch {}

    if (-not $pythonOk) {
        try {
            $v = & py -3 --version 2>$null
            if ($LASTEXITCODE -eq 0 -and $v) {
                $pythonOk = $true
                $pythonVersion = $v
            }
        } catch {}
    }

    if (-not $pythonOk) {
        Write-Host "Python installation failed after all attempts." -ForegroundColor Red
        Write-Host "If this is a managed machine policy block, install Python 3.12 manually for Current User from python.org and rerun." -ForegroundColor Yellow
        Wait-IfNeeded
        exit 1
    }
}

Write-Host "Python ready: $pythonVersion" -ForegroundColor Green

# ---------------------------------------------------------------------------
# Step 6: Refresh PATH in current session
# ---------------------------------------------------------------------------
Write-Step 6 "Refreshing PATH in current session..."

$machinePath = [Environment]::GetEnvironmentVariable("Path", "Machine")
$userPath2   = [Environment]::GetEnvironmentVariable("Path", "User")
$env:Path    = "$machinePath;$userPath2"
Write-Host "PATH refreshed." -ForegroundColor Green

# ---------------------------------------------------------------------------
# Step 7: Install LibreOffice for headless document conversion (no-admin)
# ---------------------------------------------------------------------------
Write-Step 7 "Installing LibreOffice (headless support, no admin)..."

$loUserDir = Join-Path $env:LOCALAPPDATA "Programs\LibreOffice"
$sofficePath = $null

function Find-SofficePath {
    param([string[]]$SearchCandidates)

    $cmd = Get-Command soffice -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($cmd -and $cmd.Source -and (Test-Path $cmd.Source)) {
        return $cmd.Source
    }

    foreach ($path in $SearchCandidates) {
        if ($path -and (Test-Path $path)) {
            return $path
        }
    }

    return $null
}

$candidates = @(
    (Join-Path $loUserDir "program\soffice.exe")
)
if ($env:ProgramFiles) {
    $candidates += (Join-Path $env:ProgramFiles "LibreOffice\program\soffice.exe")
}
$programFilesX86 = [Environment]::GetEnvironmentVariable("ProgramFiles(x86)")
if ($programFilesX86) {
    $candidates += (Join-Path $programFilesX86 "LibreOffice\program\soffice.exe")
}

$sofficePath = Find-SofficePath -SearchCandidates $candidates

if ($sofficePath) {
    Write-Host "LibreOffice already installed at: $sofficePath" -ForegroundColor Yellow
} else {
    # Try winget user-scope first (works on some managed images).
    Write-Host "Attempting winget install (user scope)..."
    winget install TheDocumentFoundation.LibreOffice `
        --scope user `
        --accept-package-agreements `
        --accept-source-agreements `
        --silent

    $sofficePath = Find-SofficePath -SearchCandidates $candidates

    # Fallback: direct MSI install into user profile without elevation.
    if (-not $sofficePath) {
        Write-Host "Winget install failed or requires admin. Falling back to MSI user install..." -ForegroundColor Yellow

        $loVersion = "25.2.2"
        $msiUrl = "https://download.documentfoundation.org/libreoffice/stable/$loVersion/win/x86_64/LibreOffice_${loVersion}_Win_x86-64.msi"
        $msiPath = Join-Path $env:TEMP "LibreOffice_install.msi"

        try {
            Write-Host "Downloading LibreOffice MSI (~350 MB)..."
            Invoke-WebRequest -Uri $msiUrl -OutFile $msiPath -UseBasicParsing

            Write-Host "Running MSI user-level install (no admin)..."
            $msiArgs = @(
                "/i", $msiPath,
                "/quiet",
                "/norestart",
                "INSTALLDIR=$loUserDir",
                'ALLUSERS=""',
                "CREATEDESKTOPLINK=0",
                "REGISTERVFW=0"
            )

            $msiProc = Start-Process msiexec.exe -ArgumentList $msiArgs -Wait -NoNewWindow -PassThru
            if ($msiProc.ExitCode -ne 0) {
                Write-Host "MSI install exited with code $($msiProc.ExitCode)." -ForegroundColor Yellow
            }
        } catch {
            Write-Host "MSI download/install failed: $_" -ForegroundColor Red
        } finally {
            Remove-Item $msiPath -Force -ErrorAction SilentlyContinue
        }

        $sofficePath = Find-SofficePath -SearchCandidates $candidates
        if ($sofficePath) {
            Write-Host "LibreOffice installed via MSI." -ForegroundColor Green
        } else {
            Write-Host "LibreOffice install unavailable without admin on this machine." -ForegroundColor Yellow
            Write-Host "Expected location: $loUserDir\program\soffice.exe" -ForegroundColor Yellow
            Write-Host "Download manually: https://www.libreoffice.org/download/download-libreoffice/" -ForegroundColor Yellow
        }
    }
}

# Ensure LibreOffice program directory is on user PATH for `soffice --headless`.
if ($sofficePath) {
    $sofficeDir = Split-Path $sofficePath -Parent
    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    $parts = @()
    if ($userPath) {
        $parts = $userPath -split ";" | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" }
    }
    $already = $parts | Where-Object { $_.TrimEnd("\\").ToLowerInvariant() -eq $sofficeDir.TrimEnd("\\").ToLowerInvariant() }

    if (-not $already) {
        $newPath = if ([string]::IsNullOrWhiteSpace($userPath)) { $sofficeDir } else { "$userPath;$sofficeDir" }
        [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
        $env:Path = "$env:Path;$sofficeDir"
        Write-Host "Added LibreOffice to user PATH: $sofficeDir" -ForegroundColor Green
    } else {
        Write-Host "LibreOffice already on PATH." -ForegroundColor Yellow
    }

    $sofficeVersion = & $sofficePath --headless --version 2>$null
    if ($LASTEXITCODE -eq 0 -and $sofficeVersion) {
        Write-Host "Headless check OK: $sofficeVersion" -ForegroundColor Cyan
    } else {
        Write-Host "Headless check failed. Verify LibreOffice installation manually." -ForegroundColor Yellow
    }
}

# ---------------------------------------------------------------------------
# Step 8: pip install scpi-instrument-toolkit
# ---------------------------------------------------------------------------
Write-Step 8 "Installing scpi-instrument-toolkit..."

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
# Step 9: Install Claude Code
# ---------------------------------------------------------------------------
Write-Step 9 "Installing the TOM-a-natior..."

$claudeDir = $null
try {
    $claudeInstall = Invoke-RestMethod "https://claude.ai/install.ps1"
    # Capture install output to parse the install location
    $installOutput = Invoke-Expression $claudeInstall | Out-String
    Write-Host $installOutput
    # Parse "Location: <path>" from the installer output
    if ($installOutput -match "Location:\s*(.+\.exe)") {
        $claudeExePath = $matches[1].Trim()
        $claudeDir = Split-Path $claudeExePath -Parent
    }
    Write-Host "Claude Code installed." -ForegroundColor Green
} catch {
    Write-Host "Claude Code install failed: $_" -ForegroundColor Red
    Write-Host "Try manually: irm https://claude.ai/install.ps1 | iex" -ForegroundColor Yellow
}

# Fall back to known locations if output parsing missed it
if (-not $claudeDir) {
    $claudeCandidates = @(
        (Join-Path $env:USERPROFILE ".local\bin"),
        (Join-Path $env:USERPROFILE ".claude\local\bin"),
        (Join-Path $env:USERPROFILE ".claude\bin"),
        (Join-Path $env:LOCALAPPDATA "AnthropicClaude\bin"),
        (Join-Path $env:APPDATA "npm")
    )
    foreach ($dir in $claudeCandidates) {
        if ((Test-Path (Join-Path $dir "claude.exe")) -or (Test-Path (Join-Path $dir "claude.cmd"))) {
            $claudeDir = $dir; break
        }
    }
}

if ($claudeDir) {
    $curPath = [Environment]::GetEnvironmentVariable("Path", "User")
    $already = ($curPath -split ";") | Where-Object { $_.TrimEnd("\").ToLowerInvariant() -eq $claudeDir.TrimEnd("\").ToLowerInvariant() }
    if (-not $already) {
        if ([string]::IsNullOrWhiteSpace($curPath)) {
            [Environment]::SetEnvironmentVariable("Path", $claudeDir, "User")
        } else {
            [Environment]::SetEnvironmentVariable("Path", "$curPath;$claudeDir", "User")
        }
        $env:Path = "$env:Path;$claudeDir"
        Write-Host "Added claude to user PATH: $claudeDir" -ForegroundColor Green
    } else {
        Write-Host "claude already on PATH: $claudeDir" -ForegroundColor Yellow
    }
} else {
    Write-Host "Could not detect claude install dir — open a new terminal and run: claude" -ForegroundColor Yellow
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
Write-Host "  soffice --headless --version"
Write-Host "  scpi-repl --mock"
Write-Host ""
Write-Host "NOTE: For real instruments you also need NI-VISA and NI-DCPower system drivers (require admin)." -ForegroundColor Yellow
Write-Host "      NI-VISA:    https://www.ni.com/en/support/downloads/drivers/download.ni-visa.html" -ForegroundColor Yellow
Write-Host "      NI-DCPower: https://www.ni.com/en/support/downloads/drivers/download.ni-dcpower.html" -ForegroundColor Yellow
Write-Host ""

Wait-IfNeeded
