import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
import difflib
import time
import os

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]


def run_generator(output_dir: Path) -> int:
    """Run the generator script to create a QA2 copy with the provided exercise.

    Returns the subprocess return code.
    """
    # Use an explicit exercise path that exists in the repository (example used during development)
    exercise_rel = (
        "ExerciseDatabase/matematica/P4_funcoes/4-funcao_inversa/"
        "determinacao_analitica/MAT_P4FUNCOE_4FX_DAX_003"
    )

    cmd = [
        sys.executable,
        str(REPO_ROOT / "SebentasDatabase" / "_tools" / "generate_test_from_ips.py"),
        "--ips",
        "1.1.1.1",
        "--exercise-path",
        exercise_rel,
        "--output",
        str(output_dir),
        "--no-compile",
    ]

    proc = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=120)
    # Write stdout/stderr to files for debugging
    (output_dir / "generator.stdout").write_text(proc.stdout, encoding="utf-8")
    (output_dir / "generator.stderr").write_text(proc.stderr, encoding="utf-8")
    return proc.returncode


def read_optional(path: Path) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


@pytest.mark.integration
def test_generate_and_diff_exercises_tex():
    """Integration test: generate QA2 copy and diff exercises.tex vs reference.

    The test fails if the unified diff has more than `MAX_DIFF_LINES` non-empty lines.
    """
    MAX_DIFF_LINES = 40

    with tempfile.TemporaryDirectory(prefix="test_generate_diff_") as td:
        out = Path(td)

        # Run generator
        rc = run_generator(out)
        assert rc == 0, f"Generator exited with code {rc}; see {out / 'generator.stderr'}"

        # Locate generated exercises.tex inside QA2/tex
        gen_ex = out / "QA2" / "tex" / "exercises.tex"
        assert gen_ex.exists(), f"Generated exercises.tex not found at {gen_ex}"

        # Reference file
        ref_ex = REPO_ROOT / "reference" / "QA2" / "tex" / "exercises.tex"
        if not ref_ex.exists():
            pytest.skip("reference/QA2/tex/exercises.tex not present in repository; skipping diff check")

        gen_text = gen_ex.read_text(encoding="utf-8").splitlines()
        ref_text = ref_ex.read_text(encoding="utf-8").splitlines()

        diff = list(difflib.unified_diff(ref_text, gen_text, fromfile=str(ref_ex), tofile=str(gen_ex), lineterm=""))

        # Filter out trivial header lines or timestamp differences if desired (optional)
        meaningful = [ln for ln in diff if ln.strip() and not ln.startswith('---') and not ln.startswith('+++')]

        # Save the diff for inspection on failure
        diff_file = out / "exercises.diff"
        diff_file.write_text("\n".join(diff), encoding="utf-8")

        # Allow small differences but fail if diff is large
        if len(meaningful) > MAX_DIFF_LINES:
            pytest.fail(f"Generated exercises.tex diverges from reference (meaningful diff lines={len(meaningful)}). See {diff_file}")

        # If we reach here, test passed
        assert True
