import sys
import subprocess
import shutil
from pathlib import Path
import builtins
import importlib

import pytest

from scripts import run_add_exercise


def test_fallback_when_python_executable_missing(monkeypatch, tmp_path, capsys):
    # Prepare argv to call the script in positional form
    monkeypatch.setattr(sys, 'argv', [
        'scripts/run_add_exercise.py',
        'matematica',
        'TEMP_MODULE_FOR_TEST',
        '1-temp',
        'temp_tipo',
        '2',
        'Enunciado de teste para fallback'
    ])

    # Make subprocess.run raise FileNotFoundError to simulate missing python in PATH
    def fake_run(*args, **kwargs):
        raise FileNotFoundError('Executable not found in $PATH: "python"')

    monkeypatch.setattr(subprocess, 'run', fake_run)

    # Ensure target path does not exist before
    base = Path(__file__).resolve().parents[1] / 'ExerciseDatabase'
    target = base / 'matematica' / 'TEMP_MODULE_FOR_TEST'
    if target.exists():
        shutil.rmtree(target)

    # Call main - it should catch FileNotFoundError and fallback to creating files directly
    rc = run_add_exercise.main()

    # Capture printed output
    captured = capsys.readouterr()

    # Assert returned success
    assert rc == 0
    assert 'SUCCESS:' in captured.out or target.exists()

    # Verify that an exercise file was created under the expected tree
    assert target.exists()
    # Clean up created files
    try:
        shutil.rmtree(target)
    except Exception:
        pass
