@echo off
REM LaTeX Compilation Wrapper for Windows
REM This wrapper detects missing subvariant files and creates placeholders before compilation

setlocal enabledelayedexpansion

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
set PYTHON_SCRIPT=%SCRIPT_DIR%latex_wrapper.py

REM Check if Python script exists
if not exist "%PYTHON_SCRIPT%" (
    echo Error: latex_wrapper.py not found in %SCRIPT_DIR%
    echo Please ensure the wrapper script is in the same directory as this batch file.
    exit /b 1
)

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Please install Python and add it to your PATH.
    exit /b 1
)

REM If no arguments provided, show help
if "%~1"=="" (
    echo Usage: pdflatex_wrapper.bat [pdflatex_options] file.tex
    echo.
    echo Examples:
    echo   pdflatex_wrapper.bat document.tex
    echo   pdflatex_wrapper.bat -interaction=nonstopmode document.tex
    echo   pdflatex_wrapper.bat --no-cleanup document.tex
    echo   pdflatex_wrapper.bat --cleanup-only document.tex
    echo   pdflatex_wrapper.bat --list-missing document.tex
    echo.
    echo This wrapper automatically creates missing subvariant_N.tex files
    echo before compilation to prevent LaTeX errors.
    exit /b 0
)

REM Pass all arguments to the Python wrapper
python "%PYTHON_SCRIPT%" %*

REM Check exit code and provide helpful messages
if errorlevel 1 (
    echo.
    echo Compilation failed. Check the error messages above.
    echo.
    echo Common issues:
    echo - LaTeX (MiKTeX/TeX Live) not installed or not in PATH
    echo - Missing .tex file or incorrect path
    echo - LaTeX syntax errors in the source files
    echo.
    echo For troubleshooting, try:
    echo   pdflatex_wrapper.bat --list-missing yourfile.tex
    echo   pdflatex_wrapper.bat --no-cleanup yourfile.tex
) else (
    echo.
    echo Compilation completed successfully.
)

exit /b %errorlevel%