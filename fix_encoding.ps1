# Windows Environment Configuration for Unicode Encoding (PowerShell)
# Fixes UnicodeEncodeError issues in Python scripts on Windows
# Usage: .\fix_encoding.ps1 [python_script_path] [arguments...]

param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$ScriptArgs
)

Write-Host "Setting up Windows Unicode environment..." -ForegroundColor Green
Write-Host ""

# Set PowerShell output encoding to UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# Set Python environment variables for UTF-8 encoding
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"

# Add current directory to Python path for module imports
$env:PYTHONPATH = $env:PYTHONPATH + ";" + (Get-Location).Path

# Add project scripts directory to PATH
$env:PATH = $env:PATH + ";" + (Join-Path (Get-Location).Path "scripts")

Write-Host "Environment configured:" -ForegroundColor Yellow
Write-Host "- Console encoding: UTF-8"
Write-Host "- PYTHONIOENCODING: $($env:PYTHONIOENCODING)"
Write-Host "- PYTHONUTF8: $($env:PYTHONUTF8)"
Write-Host "- PYTHONPATH: $($env:PYTHONPATH)"
Write-Host ""

# Check if a Python script was provided
if ($ScriptArgs.Count -eq 0) {
    Write-Host "Usage: .\fix_encoding.ps1 [python_script_path] [arguments...]" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Example:" -ForegroundColor Cyan
    Write-Host "  .\fix_encoding.ps1 scripts\run_add_exercise.py"
    Write-Host "  .\fix_encoding.ps1 python -m tests.test_add_exercise_simple"
    Write-Host ""
    Write-Host "Environment is now configured. You can run Python scripts manually." -ForegroundColor Green
    exit 0
}

# Run the provided Python script with arguments
Write-Host "Running: $($ScriptArgs -join ' ')" -ForegroundColor Cyan
Write-Host ""

& python @ScriptArgs

Write-Host ""
Write-Host "Done." -ForegroundColor Green