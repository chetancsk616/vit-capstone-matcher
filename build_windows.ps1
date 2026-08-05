$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

if (-not (Test-Path ".venv-build")) {
    python -m venv .venv-build
}

. .\.venv-build\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements-build.txt

python -m PyInstaller `
    --name VITCapstoneMatcher `
    --onefile `
    --clean `
    --add-data "app.py;." `
    --collect-data streamlit `
    --collect-all jobspy `
    --collect-all tls_client `
    --hidden-import jobspy `
    --hidden-import tls_client `
    --exclude-module PyQt5 `
    --exclude-module PySide6 `
    --exclude-module PyQt6 `
    --exclude-module matplotlib `
    --exclude-module torch `
    --exclude-module scipy `
    --exclude-module pygame `
    --exclude-module pygame_gui `
    --exclude-module IPython `
    launcher.py

Write-Host ""
Write-Host "Windows executable created at: $ProjectRoot\dist\VITCapstoneMatcher.exe"
