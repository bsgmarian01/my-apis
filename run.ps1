# JIT API Factory Launcher
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "       ⚡ JIT API FACTORY LAUNCHER ⚡       " -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan

# Check for Python installation
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python is not installed or not in your PATH. Please install Python to run this dashboard."
    Exit
}

# Define virtual environment path
$VenvPath = Join-Path $PSScriptRoot ".venv"

if (-not (Test-Path $VenvPath)) {
    Write-Host "Creating python virtual environment in .venv..." -ForegroundColor Yellow
    python -m venv .venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
$ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"
& $ActivateScript

# Install / update requirements
Write-Host "Checking & installing dependencies from requirements.txt..." -ForegroundColor Yellow
python -m pip install --upgrade pip
pip install -r requirements.txt

# Run the UI
Write-Host "Launching UI Dashboard..." -ForegroundColor Green
python factory_ui.py
