# Windows Unicode Encoding Fix

This directory contains configuration scripts to fix Unicode encoding issues when running Python scripts on Windows.

## Problem

Python scripts in this project fail with `UnicodeEncodeError` because Windows console uses `cp1252` encoding but the scripts output Unicode characters like ✓, ✗, ℹ, ⚠.

## Solution

Use the provided wrapper scripts to run Python scripts with proper UTF-8 encoding environment.

## Files

- `fix_encoding.bat` - Batch file wrapper for Command Prompt
- `fix_encoding.ps1` - PowerShell wrapper script  
- `test_unicode.py` - Test script to verify Unicode display works correctly

## Usage

### Method 1: Batch File (Command Prompt)

```cmd
# Test the encoding fix
fix_encoding.bat test_unicode.py

# Run any Python script with proper encoding
fix_encoding.bat scripts\run_add_exercise.py
fix_encoding.bat python -m tests.test_add_exercise_simple
```

### Method 2: PowerShell (Recommended)

```powershell
# Test the encoding fix
.\fix_encoding.ps1 test_unicode.py

# Run any Python script with proper encoding
.\fix_encoding.ps1 scripts\run_add_exercise.py
.\fix_encoding.ps1 python -m tests.test_add_exercise_simple
```

### Method 3: Manual Environment Setup

If you prefer to set up the environment manually:

```cmd
# In Command Prompt
chcp 65001
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
set PYTHONPATH=%PYTHONPATH%;%CD%
set PATH=%PATH%;%CD%\scripts
```

```powershell
# In PowerShell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"
$env:PYTHONPATH = $env:PYTHONPATH + ";" + (Get-Location).Path
$env:PATH = $env:PATH + ";" + (Join-Path (Get-Location).Path "scripts")
```

## What the Scripts Do

1. **Set console encoding to UTF-8** (`chcp 65001` in batch, PowerShell encoding in PS)
2. **Set Python environment variables:**
   - `PYTHONIOENCODING=utf-8` - Forces UTF-8 for stdin/stdout/stderr
   - `PYTHONUTF8=1` - Enables UTF-8 mode in Python 3.7+
3. **Configure Python paths:**
   - Adds current directory to `PYTHONPATH` for module imports
   - Adds `scripts` directory to `PATH` for easy script access

## Testing

Run the test script to verify Unicode characters display correctly:

```cmd
fix_encoding.bat test_unicode.py
```

Expected output should show all Unicode characters (✓, ✗, ℹ, ⚠, etc.) without errors.

## Permanent Solution (Optional)

To make this permanent for your Windows environment:

### Option A: System Environment Variables
1. Press `Win + R`, type `sysdm.cpl`
2. Go to "Advanced" → "Environment Variables"
3. Add:
   - `PYTHONIOENCODING = utf-8`
   - `PYTHONUTF8 = 1`

### Option B: PowerShell Profile
Add to your PowerShell profile (`$PROFILE`):

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"
```

### Option C: Command Prompt AutoRun
Add to registry or create a batch file that runs automatically.

## Troubleshooting

- **Characters still show as ?**: Make sure your terminal font supports Unicode (Consolas, Cascadia Code, etc.)
- **Scripts still fail**: Ensure you're using the wrapper scripts, not running Python directly
- **PowerShell execution policy**: Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

## Notes

- This is an **intervention approach** - no existing Python code was modified
- The wrapper scripts work with any Python script in the project
- PowerShell version is recommended for better Unicode support
- Test script verifies the fix works before running other scripts