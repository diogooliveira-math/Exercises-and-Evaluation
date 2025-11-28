@echo off
REM Windows Environment Configuration for Unicode Encoding
REM Fixes UnicodeEncodeError issues in Python scripts on Windows
REM Usage: fix_encoding.bat [python_script_path] [arguments...]

echo Setting up Windows Unicode environment...
echo.

REM Set Windows console to UTF-8 encoding
chcp 65001 >nul
if %errorlevel% neq 0 (
    echo Warning: Failed to set console code page to UTF-8
)

REM Set Python environment variables for UTF-8 encoding
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

REM Add current directory to Python path for module imports
set PYTHONPATH=%PYTHONPATH%;%CD%

REM Add project scripts directory to PATH
set PATH=%PATH%;%CD%\scripts

echo Environment configured:
echo - Console encoding: UTF-8 (chcp 65001)
echo - PYTHONIOENCODING: utf-8
echo - PYTHONUTF8: 1
echo - PYTHONPATH: %PYTHONPATH%
echo.

REM Check if a Python script was provided
if "%~1"=="" (
    echo Usage: fix_encoding.bat [python_script_path] [arguments...]
    echo.
    echo Example:
    echo   fix_encoding.bat scripts\run_add_exercise.py
    echo   fix_encoding.bat python -m tests.test_add_exercise_simple
    echo.
    echo Environment is now configured. You can run Python scripts manually.
    goto :end
)

REM Run the provided Python script with arguments
echo Running: %*
echo.

python %*

:end
echo.
echo Done.