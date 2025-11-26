import subprocess
import sys
import os
from pathlib import Path


def test_generate_sebenta_no_compile():
    """Smoke test: run generate_sebentas.py in no-compile/no-preview mode for a known concept.
    Asserts that the script exits normally and that a .tex file is generated.
    """
    project_root = Path(__file__).resolve().parent.parent
    generator = project_root / "SebentasDatabase" / "_tools" / "generate_sebentas.py"

    cmd = [sys.executable, str(generator),
           "--discipline", "matematica",
           "--module", "P4_funcoes",
           "--concept", "4-funcao_inversa",
           "--no-compile",
           "--no-preview"]

    # Ensure UTF-8 output to avoid UnicodeEncodeError on Windows consoles
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'

    result = subprocess.run(cmd, cwd=str(project_root), env=env)
    assert result.returncode == 0, f"generate_sebentas exited with {result.returncode}"

    tex_path = project_root / "SebentasDatabase" / "matematica" / "P4_funcoes" / "4-funcao_inversa" / "sebenta_4-funcao_inversa.tex"
    assert tex_path.exists(), f"Expected generated tex at {tex_path}"
