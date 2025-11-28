# LaTeX Compilation Wrapper for Windows (PowerShell)
# This wrapper detects missing subvariant files and creates placeholders before compilation

param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Arguments
)

# Get the directory where this script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonScript = Join-Path $ScriptDir "latex_wrapper.py"

# Check if Python script exists
if (-not (Test-Path $PythonScript)) {
    Write-Host "Error: latex_wrapper.py not found in $ScriptDir" -ForegroundColor Red
    Write-Host "Please ensure the wrapper script is in the same directory as this PowerShell file." -ForegroundColor Red
    exit 1
}

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }
} catch {
    Write-Host "Error: Python not found. Please install Python and add it to your PATH." -ForegroundColor Red
    exit 1
}

# If no arguments provided, show help
if (-not $Arguments -or $Arguments.Count -eq 0) {
    Write-Host "Usage: .\pdflatex_wrapper.ps1 [pdflatex_options] file.tex" -ForegroundColor Green
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\pdflatex_wrapper.ps1 document.tex"
    Write-Host "  .\pdflatex_wrapper.ps1 -interaction=nonstopmode document.tex"
    Write-Host "  .\pdflatex_wrapper.ps1 --no-cleanup document.tex"
    Write-Host "  .\pdflatex_wrapper.ps1 --cleanup-only document.tex"
    Write-Host "  .\pdflatex_wrapper.ps1 --list-missing document.tex"
    Write-Host ""
    Write-Host "This wrapper automatically creates missing subvariant_N.tex files"
    Write-Host "before compilation to prevent LaTeX errors." -ForegroundColor Cyan
    exit 0
}

# Build the argument list for Python
$pythonArgs = @($PythonScript) + $Arguments

# Execute the Python wrapper
try {
    & python $pythonArgs
    $exitCode = $LASTEXITCODE
    
    if ($exitCode -eq 0) {
        Write-Host ""
        Write-Host "Compilation completed successfully." -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "Compilation failed. Check the error messages above." -ForegroundColor Red
        Write-Host ""
        Write-Host "Common issues:" -ForegroundColor Yellow
        Write-Host "- LaTeX (MiKTeX/TeX Live) not installed or not in PATH"
        Write-Host "- Missing .tex file or incorrect path"
        Write-Host "- LaTeX syntax errors in the source files"
        Write-Host ""
        Write-Host "For troubleshooting, try:" -ForegroundColor Cyan
        Write-Host "  .\pdflatex_wrapper.ps1 --list-missing yourfile.tex"
        Write-Host "  .\pdflatex_wrapper.ps1 --no-cleanup yourfile.tex"
    }
    
    exit $exitCode
} catch {
    Write-Host "Error executing Python wrapper: $_" -ForegroundColor Red
    exit 1
}