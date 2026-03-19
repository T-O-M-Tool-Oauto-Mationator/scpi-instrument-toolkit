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

Write-Host "=" * 80
Write-Host "SCPI Toolkit - Add GitHub Desktop Git To User PATH"
Write-Host "=" * 80

$desktopRoot = Join-Path $env:LOCALAPPDATA "GitHubDesktop"
if (-not (Test-Path $desktopRoot)) {
    Write-Host "GitHub Desktop installation was not found at: $desktopRoot" -ForegroundColor Red
    Write-Host "Install GitHub Desktop first: https://desktop.github.com/download/" -ForegroundColor Yellow
    Wait-IfNeeded
    exit 1
}

# Prefer direct app-version globbing first; fallback to recursive search for edge cases.
$gitExe = Get-ChildItem -Path "$desktopRoot\app-*\resources\app\git\cmd\git.exe" -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

if (-not $gitExe) {
    $gitExe = Get-ChildItem -Path $desktopRoot -Filter git.exe -Recurse -ErrorAction SilentlyContinue |
        Where-Object { $_.DirectoryName -like "*\git\cmd" } |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
}

if (-not $gitExe) {
    Write-Host "git.exe was not found inside GitHub Desktop." -ForegroundColor Red
    Write-Host "Open GitHub Desktop once, then run this script again." -ForegroundColor Yellow
    Wait-IfNeeded
    exit 1
}

$gitPath = $gitExe.DirectoryName
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$parts = @()
if ($userPath) {
    $parts = $userPath -split ";" | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" }
}

$alreadyPresent = $false
foreach ($part in $parts) {
    if ($part.TrimEnd('\\').ToLowerInvariant() -eq $gitPath.TrimEnd('\\').ToLowerInvariant()) {
        $alreadyPresent = $true
        break
    }
}

if ($alreadyPresent) {
    Write-Host "Git is already on your user PATH:" -ForegroundColor Yellow
    Write-Host "  $gitPath"
} else {
    $newPath = if ([string]::IsNullOrWhiteSpace($userPath)) { $gitPath } else { "$userPath;$gitPath" }
    [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
    Write-Host "Added Git to user PATH:" -ForegroundColor Green
    Write-Host "  $gitPath"
}

$versionOutput = & "$($gitExe.FullName)" --version 2>$null
if ($LASTEXITCODE -eq 0 -and $versionOutput) {
    Write-Host "Detected: $versionOutput" -ForegroundColor Cyan
}

Write-Host "Open a NEW terminal and run: git --version" -ForegroundColor Cyan
Write-Host "This script only updates user PATH and does not require admin rights." -ForegroundColor Cyan

Wait-IfNeeded