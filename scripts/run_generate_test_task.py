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
GENERATOR = REPO_ROOT / "SebentasDatabase" / "_tools" / "generate_test_template.py"

if not GENERATOR.exists():
    print(f"Generator not found: {GENERATOR}")
    sys.exit(1)

env = os.environ.copy()

def env_flag(name: str) -> bool:
    v = env.get(name, "")
    return str(v).lower() in ("1", "true", "yes", "s", "sim")

cmd = [sys.executable, str(GENERATOR)]

# Optional string parameters
for var, arg in [
    ("TEST_MODULE", "--module"),
    ("TEST_CONCEPT", "--concept"),
]:
    v = env.get(var, "")
    if v is not None and v != "":
        # For module/concept, take first value if multiple
        values = [x.strip() for x in v.split(",") if x.strip()]
        if values:
            cmd.extend([arg, values[0]])

# Handle exercise IDs specially - pass as environment variable to generator
exercise_ids = env.get("TEST_EXERCISE_IDS", "")
if exercise_ids:
    env['TEST_SELECTED_EXERCISES'] = exercise_ids

# Validation: require at least module or concept to be provided
provided_any = any(env.get(x, "") for x in ("TEST_MODULE", "TEST_CONCEPT"))
if not provided_any:
    print("❌ Nenhum filtro fornecido: por favor especifique pelo menos uma das opções:")
    print("   - TEST_MODULE (ex: P4_funcoes)")
    print("   - TEST_CONCEPT (ex: 4-funcao_inversa)")
    print("")
    print("Sugestão: na Task do VS Code, preencha pelo menos um campo ou use a task interativa.")
    sys.exit(2)

# Boolean flags - NOT USED by test generator (it has different logic)
# if env_flag("TEST_NO_PREVIEW"):
#     cmd.append("--no-preview")
# if env_flag("TEST_NO_COMPILE"):
#     cmd.append("--no-compile")
# if env_flag("TEST_AUTO_APPROVE"):
#     cmd.append("--auto-approve")

# Ensure deterministic encoding on Windows
env['PYTHONIOENCODING'] = env.get('PYTHONIOENCODING', 'utf-8')

print("Running:", " ".join(cmd))

result = subprocess.run(cmd, cwd=str(REPO_ROOT), env=env)

sys.exit(result.returncode)