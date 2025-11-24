import os
import subprocess
import sys
from pathlib import Path
import shutil

REPO_ROOT = Path(__file__).resolve().parent.parent
EXERCISE_DB = REPO_ROOT / "ExerciseDatabase"
SEBENTAS_DB = REPO_ROOT / "SebentasDatabase"
TEMPLATE_DIR = SEBENTAS_DB / "_templates"
TEMPLATE_FILE = TEMPLATE_DIR / "sebenta_template.tex"


def write_minimal_template():
    TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
    if not TEMPLATE_FILE.exists():
        TEMPLATE_FILE.write_text(
            """\\documentclass{article}
\\usepackage{placeins}
\\begin{document}
%%CONTENT%%
\\end{document}
""",
            encoding="utf-8"
        )


def test_generate_sebenta_with_tipo(tmp_path):
    # Prepare minimal template
    write_minimal_template()

    # Create a temporary discipline/module/concept with two tipos
    disc = EXERCISE_DB / "tmp_test_tipo"
    mod = disc / "test_module"
    concept = mod / "test_concept"
    tipo_a = concept / "tipoA"
    tipo_b = concept / "tipoB"

    # Ensure clean state
    if disc.exists():
        shutil.rmtree(disc)
    if (SEBENTAS_DB / "tmp_test_tipo").exists():
        shutil.rmtree(SEBENTAS_DB / "tmp_test_tipo")

    tipo_a.mkdir(parents=True, exist_ok=True)
    tipo_b.mkdir(parents=True, exist_ok=True)

    # Create sample tex files
    ex_a = tipo_a / "ex_a.tex"
    ex_b = tipo_b / "ex_b.tex"
    ex_a.write_text("\\begin{exercise}Exercicio A\\end{exercise}", encoding="utf-8")
    ex_b.write_text("\\begin{exercise}Exercicio B\\end{exercise}", encoding="utf-8")

    # Run generator filtering by tipoA
    cmd = [sys.executable, str(REPO_ROOT / "SebentasDatabase" / "_tools" / "generate_sebentas.py"),
           "--discipline", "tmp_test_tipo",
           "--module", "test_module",
           "--concept", "test_concept",
           "--tipo", "tipoA",
           "--no-compile",
           "--no-preview",
           "--auto-approve"]

    env = os.environ.copy()
    # Ensure deterministic encoding on Windows terminals
    env['PYTHONIOENCODING'] = 'utf-8'

    proc = subprocess.run(cmd, cwd=str(REPO_ROOT), env=env, capture_output=True, text=True)
    if proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr)
    assert proc.returncode == 0, f"Generator failed: {proc.stderr}"

    # Verify that sebenta was generated and contains content from ex_a but not ex_b
    out_tex = SEBENTAS_DB / "tmp_test_tipo" / "test_module" / "test_concept" / "sebenta_test_concept.tex"
    assert out_tex.exists(), f"Expected output tex {out_tex} not found"
    content = out_tex.read_text(encoding="utf-8")
    assert "Exercicio A" in content
    assert "Exercicio B" not in content

    # Cleanup
    shutil.rmtree(disc)
    shutil.rmtree(SEBENTAS_DB / "tmp_test_tipo")