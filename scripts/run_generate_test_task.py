"""Wrapper to call SebentasDatabase/_tools/generate_test_template.py
Reads inputs from environment variables and only adds arguments that have values.
This avoids passing empty CLI arguments from VS Code tasks.

Environment variables used (set by tasks.json inputs):
- TEST_DISCIPLINE
- TEST_MODULE
- TEST_CONCEPT
- TEST_TIPO
- TEST_EXERCISE_IDS
- TEST_NO_PREVIEW (1/true)
- TEST_NO_COMPILE (1/true)
- TEST_AUTO_APPROVE (1/true)

Usage (from VS Code task):
python scripts/run_generate_test_task.py
"""
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GENERATOR = REPO_ROOT / "SebentasDatabase" / "_tools" / "generate_tests.py"

if not GENERATOR.exists():
    print(f"Generator not found: {GENERATOR}")
    sys.exit(1)

env = os.environ.copy()

def env_flag(name: str) -> bool:
    v = env.get(name, "")
    return str(v).lower() in ("1", "true", "yes", "s", "sim")

cmd = [sys.executable, str(GENERATOR)]

# Optional string parameters: discipline/module/concept/tipo (take first value if multiple)
for var, arg in [
    ("TEST_DISCIPLINE", "--discipline"),
    ("TEST_MODULE", "--module"),
    ("TEST_CONCEPT", "--concept"),
    ("TEST_TIPO", "--tipo"),
]:
    v = env.get(var, "")
    if v is not None and v != "":
        values = [x.strip() for x in v.split(",") if x.strip()]
        if values:
            cmd.extend([arg, values[0]])

# Handle exercise IDs specially - pass as environment variable to generator
exercise_ids = env.get("TEST_EXERCISE_IDS", "")
if exercise_ids:
    env['TEST_SELECTED_EXERCISES'] = exercise_ids

# Do NOT require filters: the generator now supports running across all combos
# if no filters are provided. Forward boolean flags to generator.
if env_flag("TEST_NO_PREVIEW"):
    cmd.append("--no-preview")
if env_flag("TEST_NO_COMPILE"):
    cmd.append("--no-compile")
if env_flag("TEST_AUTO_APPROVE"):
    cmd.append("--auto-approve")

# Ensure deterministic encoding on Windows
env['PYTHONIOENCODING'] = env.get('PYTHONIOENCODING', 'utf-8')

print("Running:", " ".join(cmd))

result = subprocess.run(cmd, cwd=str(REPO_ROOT), env=env)

sys.exit(result.returncode)