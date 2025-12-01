#!/usr/bin/env python3
"""
Small example that stages an exercise payload using the safe wrapper.
This script is intentionally minimal and safe for local experimentation.
It writes a temporary payload file, calls the safe wrapper, parses JSON
from the wrapper's stdout and prints the staged id/path if present.

Usage: python stage_example.py
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

# Path to the safe wrapper script in this repo
WRAPPER = Path("ExerciseDatabase/_tools/add_exercise_safe.py")


def extract_first_json(text: str):
    """Return first JSON object parsed from text or None."""
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None


def main() -> int:
    # Create a tiny payload dict. Adjust fields to match your real schema.
    payload = {
        "discipline": "matematica",
        "module": "P4_funcoes",
        "concept": "1-intervalo_real",
        "tipo": "pertinencia_intervalo",
        "difficulty": 1,
        "statement": "Playground: exemplo de enunciado para staging",
        "uid": str(uuid.uuid4()),
    }

    # Write payload to a temp file (idempotent - uses a unique filename)
    tmp = tempfile.NamedTemporaryFile(prefix="payload_", suffix=".json", delete=False, encoding="utf-8")
    try:
        tmp_path = Path(tmp.name)
        tmp.write(json.dumps(payload, ensure_ascii=False, indent=2))
        tmp.close()

        # Call the safe wrapper using the current Python interpreter
        cmd = [sys.executable, str(WRAPPER), f'--payload-file={tmp_path}']
        print("Running:", " ".join(cmd))
        proc = subprocess.run(cmd, capture_output=True, text=True)

        # Print raw outputs for debugging
        print("--- wrapper stdout ---")
        print(proc.stdout)
        print("--- wrapper stderr ---")
        print(proc.stderr)

        # Try to parse JSON from stdout
        parsed = extract_first_json(proc.stdout)
        if not parsed:
            print("No JSON object found in wrapper output. Exit code:", proc.returncode)
            return proc.returncode or 1

        # Try common keys; wrapper implementations may vary
        staged_id = parsed.get("staged_id") or parsed.get("id") or parsed.get("exercise_id")
        staged_path = parsed.get("staged_path") or parsed.get("path") or parsed.get("staged")

        print("Parsed wrapper JSON:")
        print(json.dumps(parsed, ensure_ascii=False, indent=2))
        print()
        print("Staged ID:", staged_id)
        print("Staged path:", staged_path)

        return 0
    finally:
        # Clean up the temp file; keep the rest idempotent
        try:
            tmp_path.unlink()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
