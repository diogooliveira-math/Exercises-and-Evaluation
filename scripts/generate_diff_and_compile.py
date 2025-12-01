#!/usr/bin/env python
"""Generate unified diff between reference QA2 exercises.tex and a generated one,
and optionally compile the generated test.tex to PDF (pdflatex).

Usage:
    python scripts/generate_diff_and_compile.py --output SebentasDatabase/tests/test_ips_20251201_201350
"""
from pathlib import Path
import argparse
import difflib
import subprocess


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", required=True, help="Output test directory (contains QA2/ and test.tex)")
    args = p.parse_args()

    out_dir = Path(args.output)
    ref_file = Path("reference") / "QA2" / "tex" / "exercises.tex"
    gen_file = out_dir / "QA2" / "tex" / "exercises.tex"

    if not ref_file.exists():
        print(f"Reference file not found: {ref_file}")
        return 2
    if not gen_file.exists():
        print(f"Generated exercises.tex not found: {gen_file}")
        return 3

    ref_lines = ref_file.read_text(encoding='utf-8').splitlines()
    gen_lines = gen_file.read_text(encoding='utf-8').splitlines()

    diff = list(difflib.unified_diff(ref_lines, gen_lines, fromfile=str(ref_file), tofile=str(gen_file), lineterm=''))
    diff_path = out_dir / "exercises.diff"
    diff_path.write_text('\n'.join(diff), encoding='utf-8')
    print(f"Wrote diff to {diff_path} ({len(diff)} lines)")

    # Try to compile a minimal, safe test that includes QA2/tex/exercises
    # This avoids loading project style.tex which may re-define macros and
    # cause compilation errors when comparing generated files.
    safe_tex = out_dir / "safe_test.tex"
    safe_content = r'''% Minimal safe test to include generated QA2 exercises
\documentclass[a4paper,12pt]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[portuguese]{babel}
\usepackage{lmodern}
\usepackage{geometry}
\usepackage{amsmath,amssymb}
\usepackage{enumitem}
\usepackage{tcolorbox}
\geometry{margin=2.5cm}
% minimal macros if missing
\makeatletter
\@ifundefined{exerciciocount}{\newcounter{exerciciocount}}{}
\@ifundefined{subexerciciocount}{\newcounter{subexerciciocount}}{}
\@ifundefined{optioncount}{\newcounter{optioncount}}{}
\@ifundefined{exercise}{\newcounter{exercise}}{}
% Keep counters in sync: alias internal registers so either name works
\@ifundefined{c@exerciciocount}{\newcounter{exerciciocount}}{}
\let\c@exercise\c@exerciciocount
% showexerciciotitle flag
\@ifundefined{showexerciciotitletrue}{%
    \newif\ifshowexerciciotitle
    \showexerciciotitletrue
}{}
% minimal exercise macros
\@ifundefined{exercicio}{\newcommand{\exercicio}[1]{\par\vspace{1.5em}\refstepcounter{exercise}\noindent\textbf{Exercício~\theexercise.} ##1\par\vspace{0.5em}}}{}
\@ifundefined{subexercicio}{\newcommand{\subexercicio}[1]{\par\vspace{0.8em}\refstepcounter{subexerciciocount}\noindent\textbf{\theexercise.\thesubexerciciocount.} ##1\par\vspace{0.3em}}}{}
\@ifundefined{espacoAluno}{\newcommand{\espacoAluno}{\vspace{1cm}}}{}
\makeatother
\begin{document}
\section*{Teste (versão segura)}
\espacoAluno
\input{QA2/tex/exercises}
\end{document}
'''
    safe_tex.write_text(safe_content, encoding='utf-8')

    print("Attempting to compile safe_test.tex with pdflatex (this requires TeX installed)...")
    log_path = out_dir / "compile.log"
    try:
        # run pdflatex twice for references
        with open(log_path, 'wb') as logf:
            for i in range(2):
                proc = subprocess.run(["pdflatex", "-interaction=nonstopmode", str(safe_tex.name)], cwd=str(out_dir), stdout=logf, stderr=logf, timeout=120)
                if proc.returncode != 0:
                    print(f"pdflatex failed (return code {proc.returncode}), see {log_path}")
                    return 4

        pdf_path = out_dir / "safe_test.pdf"
        if pdf_path.exists():
            print(f"Safe PDF compiled: {pdf_path}")
            return 0
        else:
            print(f"pdflatex finished but safe PDF not found; check {log_path}")
            return 5
    except FileNotFoundError:
        print("pdflatex not found in PATH. Install TeX or ensure pdflatex is available.")
        return 6
    except Exception as e:
        print(f"Exception during compilation: {e}")
        return 7


if __name__ == '__main__':
    raise SystemExit(main())
