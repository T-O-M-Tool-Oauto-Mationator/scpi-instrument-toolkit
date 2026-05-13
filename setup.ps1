# PowerShell Setup Script for SCPI Instrument Toolkit
# Automatically sets up the Python virtual environment and installs all dependencies

Write-Host "=" * 80
Write-Host "SCPI Instrument Toolkit - Environment Setup (PowerShell)"
Write-Host "=" * 80

$projectDir = $PSScriptRoot
$venvDir = Join-Path $projectDir ".venv"

Write-Host "`nProject directory: $projectDir"
Write-Host "Virtual environment: $venvDir"

# Check if virtual environment exists
if (Test-Path $venvDir) {
    Write-Host "`n✓ Virtual environment already exists at $venvDir" -ForegroundColor Green
    $response = Read-Host "Do you want to recreate it? (y/N)"
    if ($response -eq 'y' -or $response -eq 'Y') {
        Write-Host "Removing existing virtual environment..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force $venvDir
    } else {
        Write-Host "Using existing virtual environment" -ForegroundColor Cyan
    }
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path $venvDir)) {
    Write-Host "`nCreating virtual environment..." -ForegroundColor Cyan
    python -m venv $venvDir
    if ($LASTEXITCODE -ne 0) {
        Write-Host "`n❌ Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ Virtual environment created successfully" -ForegroundColor Green
}

# Activate virtual environment
$activateScript = Join-Path $venvDir "Scripts\Activate.ps1"
Write-Host "`nActivating virtual environment..." -ForegroundColor Cyan
& $activateScript

# Upgrade pip
Write-Host "`nUpgrading pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip

# Install requirements
$requirementsFile = Join-Path $projectDir "requirements.txt"
if (Test-Path $requirementsFile) {
    Write-Host "`nInstalling dependencies from requirements.txt..." -ForegroundColor Cyan
    pip install -r $requirementsFile
    if ($LASTEXITCODE -ne 0) {
        Write-Host "`n❌ Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ All dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "`n⚠ Warning: requirements.txt not found" -ForegroundColor Yellow
    Write-Host "Installing basic packages..." -ForegroundColor Cyan
    pip install pyserial pandas pyfunctional numpy scipy matplotlib requests pyserial-asyncio
}

# Print success message
Write-Host "`n" + "=" * 80
Write-Host "✓ Environment setup complete!" -ForegroundColor Green
Write-Host "=" * 80

Write-Host "`nVirtual environment is now activated!"
Write-Host "To activate it in the future, run:"
Write-Host "  .\.venv\Scripts\Activate.ps1" -ForegroundColor Cyan

Write-Host "`nTo launch the interactive REPL:"
Write-Host "  python repl.py" -ForegroundColor Cyan

Write-Host "`nInstalled packages:" -ForegroundColor Cyan
pip list
