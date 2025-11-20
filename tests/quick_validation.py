"""Quick validation script for Exercises-and-Evaluation.

Performs non-destructive checks to ensure key files and scripts exist
and that basic commands respond (via --help). Intended as a small
sanity check before running heavy generation tasks.

Run from repository root::

    python tests/quick_validation.py
"""
from pathlib import Path
import json
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def check_exists(path: Path):
    ok = path.exists()
    return ok, str(path)


def try_help(script_path: Path, timeout: int = 8):
    """Try to run the script with --help. Return (ok, rc, out, err)."""
    if not script_path.exists():
        return False, None, "", f"not found: {script_path}"
    try:
        proc = subprocess.run([sys.executable, str(script_path), "--help"], capture_output=True, text=True, timeout=timeout)
        return True, proc.returncode, proc.stdout.strip()[:2000], proc.stderr.strip()[:2000]
    except subprocess.TimeoutExpired:
        return False, None, "", "timeout"
    except Exception as e:
        return False, None, "", str(e)


def main():
    checks = []

    # Key files to check
    files = [
        ROOT / "ExerciseDatabase" / "index.json",
        ROOT / "ExerciseDatabase" / "_tools" / "generate_tests.py",
        ROOT / "ExerciseDatabase" / "_tools" / "run_tests.py",
        ROOT / "SebentasDatabase" / "_tools" / "generate_sebentas.py",
        ROOT / ".github" / "agents" / "Sebenta Generater.agent.md",
        ROOT / ".github" / "agents" / "Test generater.agent.md",
    ]

    print("Quick validation — repository root:", ROOT)
    print()

    for p in files:
        ok, path = check_exists(p)
        checks.append((p, ok))
        print(f"[{'OK' if ok else 'MISSING'}] {path}")

    # Basic index.json sanity
    idx = ROOT / "ExerciseDatabase" / "index.json"
    if idx.exists():
        try:
            data = json.loads(idx.read_text(encoding="utf-8"))
            if isinstance(data, dict) and ("exercises" in data or "database_version" in data):
                print("[OK] index.json parsed and contains expected keys")
            else:
                print("[WARN] index.json parsed but expected keys missing (exercises/database_version)")
        except Exception as e:
            print(f"[ERROR] index.json invalid JSON: {e}")

    # Try running --help for main scripts (non-destructive)
    print()
    scripts_to_probe = [
        ROOT / "ExerciseDatabase" / "_tools" / "generate_tests.py",
        ROOT / "ExerciseDatabase" / "_tools" / "generate_variant.py",
        ROOT / "SebentasDatabase" / "_tools" / "generate_sebentas.py",
    ]

    for s in scripts_to_probe:
        ok, rc, out, err = try_help(s)
        if not ok:
            print(f"[ERR] probe {s.name}: {err}")
        else:
            status = "OK" if rc == 0 else f"HELP-EXIT-{rc}"
            print(f"[PROBE] {s.name}: {status}")

    # Summary
    missing = [p for p, ok in checks if not ok]
    print()
    if missing:
        print("Validation result: PROBLEMS found. Missing files:")
        for m in missing:
            print(" -", m)
        sys.exit(2)
    else:
        print("Validation result: All critical files present (basic checks passed).")
        sys.exit(0)


if __name__ == "__main__":
    main()
