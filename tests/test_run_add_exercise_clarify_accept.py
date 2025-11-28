import importlib.util
import sys
import json
import subprocess
from pathlib import Path

import pytest


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("run_add_exercise_mod", str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_clarify_accept_runs_command(monkeypatch, tmp_path):
    script_path = Path("scripts") / "run_add_exercise.py"
    mod = load_module(script_path)

    # Prepare argv to simulate a call with a statement that leaves some fields missing
    monkeypatch.setattr(sys, 'argv', [str(script_path), "statement=Um enunciado genérico sem módulo nem conceito"])

    calls = []

    def fake_run(args, capture_output=False, text=False, shell=False, **kwargs):
        # Detect clarifier invocation (python <path>/agent_clarify_flow.py --input-file ...)
        if isinstance(args, list) and len(args) >= 2 and str(args[1]).endswith('agent_clarify_flow.py'):
            calls.append(('clarifier', args))
            clar_out = {'status': 'accept', 'command': 'echo accepted'}
            return subprocess.CompletedProcess(args, 0, stdout=json.dumps(clar_out), stderr='')
        # Detect the shell execution of the returned command
        if shell and isinstance(args, str) and args.strip().startswith('echo'):
            calls.append(('shell', args))
            return subprocess.CompletedProcess(args, 0, stdout='accepted\n', stderr='')
        # Fallback to a successful no-op
        calls.append(('other', args))
        return subprocess.CompletedProcess(args, 0, stdout='', stderr='')

    # Patch subprocess.run used in the module
    monkeypatch.setattr(mod, 'subprocess', subprocess)
    monkeypatch.setattr(mod.subprocess, 'run', fake_run)

    # Run main
    rc = mod.main()

    # Assert main returned the shell command exit code (0)
    assert rc == 0
    # Assert clarifier was invoked and shell executed
    assert any(c[0] == 'clarifier' for c in calls), f"Clarifier not called, calls={calls}"
    assert any(c[0] == 'shell' for c in calls), f"Shell command not executed, calls={calls}"
