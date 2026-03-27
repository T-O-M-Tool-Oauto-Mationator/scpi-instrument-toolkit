param(
    [switch]$NoPause
)

function Wait-IfNeeded {
    if (-not $NoPause) {
        try {
            [void](Read-Host "Press Enter to close")
        } catch {}
    }
}

function Write-Step { param($n, $msg)
    Write-Host ""
    Write-Host "[$n] $msg" -ForegroundColor Cyan
    Write-Host ("-" * 60)
}

Write-Host ("=" * 60)
Write-Host "  SCPI Toolkit - TAMU Managed Machine Uninstall"
Write-Host ("=" * 60)

# ---------------------------------------------------------------------------
# Step 1: Uninstall scpi-instrument-toolkit
# ---------------------------------------------------------------------------
Write-Step 1 "Uninstalling scpi-instrument-toolkit..."

$pipCmd = $null
if (Get-Command pip -ErrorAction SilentlyContinue)        { $pipCmd = "pip" }
elseif (Get-Command pip3 -ErrorAction SilentlyContinue)   { $pipCmd = "pip3" }
elseif (Get-Command python -ErrorAction SilentlyContinue) { $pipCmd = "python -m pip" }

if (-not $pipCmd) {
    Write-Host "pip not found — skipping." -ForegroundColor Yellow
} else {
    if ($pipCmd -eq "python -m pip") {
        & python -m pip uninstall scpi-instrument-toolkit -y
    } else {
        & $pipCmd uninstall scpi-instrument-toolkit -y
    }
    if ($LASTEXITCODE -eq 0) {
        Write-Host "scpi-instrument-toolkit removed." -ForegroundColor Green
    } else {
        Write-Host "scpi-instrument-toolkit was not installed or removal failed." -ForegroundColor Yellow
    }
}

# ---------------------------------------------------------------------------
# Step 2: Uninstall GitHub CLI (gh)
# ---------------------------------------------------------------------------
Write-Step 2 "Uninstalling GitHub CLI (gh)..."

$ghInstallDir = Join-Path $env:LOCALAPPDATA "Programs\gh"
$ghExe        = Join-Path $ghInstallDir "gh.exe"
if (Test-Path $ghInstallDir) {
    Remove-Item -Recurse -Force $ghInstallDir -ErrorAction SilentlyContinue
    Write-Host "GitHub CLI removed." -ForegroundColor Green
    # Remove from user PATH
    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($userPath) {
        $parts = $userPath -split ";" | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" }
        $filtered = $parts | Where-Object { $_.TrimEnd("\").ToLowerInvariant() -ne $ghInstallDir.TrimEnd("\").ToLowerInvariant() }
        [Environment]::SetEnvironmentVariable("Path", ($filtered -join ";"), "User")
    }
} else {
    Write-Host "GitHub CLI not found. Skipping." -ForegroundColor Yellow
}

# ---------------------------------------------------------------------------
# Step 3: Remove PATH entries added by setup-tamu.ps1
# ---------------------------------------------------------------------------
Write-Step 3 "Cleaning up user PATH entries..."

$pathsToRemove = @(
    (Join-Path $env:LOCALAPPDATA "Programs\Git\cmd"),
    (Join-Path $env:LOCALAPPDATA "Programs\Git"),
    (Join-Path $env:LOCALAPPDATA "Programs\Git\usr\bin")
)

# Also remove GitHub Desktop git paths added as fallback
$desktopRoot = Join-Path $env:LOCALAPPDATA "GitHubDesktop"
if (Test-Path $desktopRoot) {
    $gitExe = Get-ChildItem -Path "$desktopRoot\app-*\resources\app\git\cmd\git.exe" `
                  -ErrorAction SilentlyContinue |
              Sort-Object LastWriteTime -Descending |
              Select-Object -First 1
    if ($gitExe) {
        $gitCmdPath  = $gitExe.DirectoryName
        $gitRootPath = Split-Path $gitCmdPath -Parent
        $pathsToRemove += $gitCmdPath
        $pathsToRemove += $gitRootPath
    }
}

$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath) {
    $parts = $userPath -split ";" | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" }
    $filtered = $parts | Where-Object {
        $p = $_.TrimEnd("\").ToLowerInvariant()
        -not ($pathsToRemove | Where-Object { $_.TrimEnd("\").ToLowerInvariant() -eq $p })
    }
    $newPath = $filtered -join ";"
    [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
    Write-Host "PATH entries removed." -ForegroundColor Green
}

# ---------------------------------------------------------------------------
# Step 3: Remove CLAUDE_CODE_GIT_BASH_PATH env var
# ---------------------------------------------------------------------------
Write-Step 4 "Removing CLAUDE_CODE_GIT_BASH_PATH environment variable..."

[Environment]::SetEnvironmentVariable("CLAUDE_CODE_GIT_BASH_PATH", $null, "User")
Write-Host "Done." -ForegroundColor Green

# ---------------------------------------------------------------------------
# Step 4: Uninstall Claude Code
# ---------------------------------------------------------------------------
Write-Step 5 "Uninstalling Claude Code..."

$claudeExe = $null
$claudeCandidates = @(
    (Join-Path $env:USERPROFILE ".local\bin\claude.exe"),
    (Join-Path $env:USERPROFILE ".claude\local\bin\claude.exe"),
    (Join-Path $env:USERPROFILE ".claude\bin\claude.exe"),
    (Join-Path $env:LOCALAPPDATA "AnthropicClaude\bin\claude.exe")
)
foreach ($c in $claudeCandidates) {
    if (Test-Path $c) { $claudeExe = $c; break }
}
if (-not $claudeExe) {
    $found = Get-ChildItem -Path (Join-Path $env:USERPROFILE ".claude") `
        -Filter "claude.exe" -Recurse -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if ($found) { $claudeExe = $found.FullName }
}

if ($claudeExe) {
    $claudeDir = Split-Path $claudeExe -Parent
    try {
        Remove-Item -Force $claudeExe -ErrorAction Stop
        Write-Host "Removed $claudeExe" -ForegroundColor Green
    } catch {
        Write-Host "Could not remove $claudeExe`: $_" -ForegroundColor Yellow
    }
    # Remove claude dir from user PATH
    $userPath2 = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($userPath2) {
        $parts2 = $userPath2 -split ";" | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" }
        $filtered2 = $parts2 | Where-Object { $_.TrimEnd("\").ToLowerInvariant() -ne $claudeDir.TrimEnd("\").ToLowerInvariant() }
        [Environment]::SetEnvironmentVariable("Path", ($filtered2 -join ";"), "User")
        Write-Host "Removed $claudeDir from user PATH." -ForegroundColor Green
    }
} else {
    Write-Host "Claude Code not found — skipping." -ForegroundColor Yellow
}

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host ("=" * 60)
Write-Host "  Uninstall complete!" -ForegroundColor Green
Write-Host ("=" * 60)
Write-Host ""
Write-Host "Note: Git for Windows, GitHub Desktop, and Python were NOT" -ForegroundColor Yellow
Write-Host "removed — use winget or the Microsoft Store to remove them." -ForegroundColor Yellow
Write-Host ""

Wait-IfNeeded
