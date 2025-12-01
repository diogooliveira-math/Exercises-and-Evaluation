#!/usr/bin/env python3
"""Helper: run the generator into a fixed output dir and produce a unified diff
between the generated `QA2/tex/exercises.tex` and the reference file.

Usage:
    python scripts/generate_and_diff_helper.py [--output OUTPUT_DIR]

Exits with 0 on success (writes diff file), non-zero on error.
"""
import subprocess
import sys
from pathlib import Path
import difflib
import argparse


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = REPO_ROOT / "SebentasDatabase" / "tests" / "integration_tmp"


def run_generator(output_dir: Path) -> int:
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

    print("Running:", " ".join(cmd))
    proc = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
    (output_dir / "generator.stdout").write_text(proc.stdout, encoding="utf-8")
    (output_dir / "generator.stderr").write_text(proc.stderr, encoding="utf-8")
    return proc.returncode


def make_diff(ref: Path, gen: Path, out_diff: Path) -> int:
    if not gen.exists():
        print(f"Generated file not found: {gen}")
        return 2
    if not ref.exists():
        print(f"Reference file not found: {ref}")
        return 3

    ref_lines = ref.read_text(encoding="utf-8").splitlines()
    gen_lines = gen.read_text(encoding="utf-8").splitlines()
    diff = list(difflib.unified_diff(ref_lines, gen_lines, fromfile=str(ref), tofile=str(gen), lineterm=""))
    out_diff.write_text("\n".join(diff), encoding="utf-8")
    print(f"Wrote diff to: {out_diff} (lines: {len(diff)})")
    return 0


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", default=str(DEFAULT_OUT))
    args = p.parse_args()

    out = Path(args.output)
    if out.exists():
        import shutil
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)

    rc = run_generator(out)
    if rc != 0:
        print(f"Generator exited with code {rc}; see logs in {out}")
        sys.exit(rc)

    gen_ex = out / "QA2" / "tex" / "exercises.tex"
    ref_ex = REPO_ROOT / "reference" / "QA2" / "tex" / "exercises.tex"
    diff_file = out / "exercises.diff"
    rc2 = make_diff(ref_ex, gen_ex, diff_file)
    sys.exit(rc2)


if __name__ == "__main__":
    main()
