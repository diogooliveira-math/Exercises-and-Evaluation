"""Wrapper to call SebentasDatabase/_tools/generate_sebentas.py
Reads inputs from environment variables and only adds arguments that have values.
This avoids passing empty CLI arguments from VS Code tasks.

Environment variables used (set by tasks.json inputs):
- SEBENTA_DISCIPLINE
- SEBENTA_MODULE
- SEBENTA_CONCEPT
- SEBENTA_TIPO
- SEBENTA_NO_PREVIEW (1/true)
- SEBENTA_NO_COMPILE (1/true)
- SEBENTA_AUTO_APPROVE (1/true)

Usage (from VS Code task):
python scripts/run_generate_sebenta_task.py
"""
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GENERATOR = REPO_ROOT / "SebentasDatabase" / "_tools" / "generate_sebentas.py"

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
    ("SEBENTA_DISCIPLINE", "--discipline"),
    ("SEBENTA_MODULE", "--module"),
    ("SEBENTA_CONCEPT", "--concept"),
    ("SEBENTA_TIPO", "--tipo"),
]:
    v = env.get(var, "")
    if v is not None and v != "":
        cmd.extend([arg, v])

# Validation: require at least one of discipline/module/concept to be provided
provided_any = any(env.get(x, "") for x in ("SEBENTA_DISCIPLINE", "SEBENTA_MODULE", "SEBENTA_CONCEPT"))
if not provided_any:
    print("❌ Nenhum filtro fornecido: por favor especifique pelo menos uma das opções:")
    print("   - SEBENTA_DISCIPLINE (ex: matematica)")
    print("   - SEBENTA_MODULE (ex: P4_funcoes)")
    print("   - SEBENTA_CONCEPT (ex: 4-funcao_inversa)")
    print("")
    print("Sugestão: na Task do VS Code, preencha pelo menos um campo ou use a task interativa.")
    sys.exit(2)

# Boolean flags
if env_flag("SEBENTA_NO_PREVIEW"):
    cmd.append("--no-preview")
if env_flag("SEBENTA_NO_COMPILE"):
    cmd.append("--no-compile")
if env_flag("SEBENTA_AUTO_APPROVE"):
    cmd.append("--auto-approve")

# Ensure deterministic encoding on Windows
env['PYTHONIOENCODING'] = env.get('PYTHONIOENCODING', 'utf-8')

print("Running:", " ".join(cmd))

result = subprocess.run(cmd, cwd=str(REPO_ROOT), env=env)

sys.exit(result.returncode)
