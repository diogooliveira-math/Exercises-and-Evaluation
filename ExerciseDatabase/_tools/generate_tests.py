#!/usr/bin/env python3
r"""Gera um ficheiro .tex de teste a partir do índice de exercícios.

Uso:
    python generate_tests.py --module P4_funcoes --tipo determinacao_grafica --count 3 --shuffle

Gera um `test_<timestamp>.tex` em `ExerciseDatabase/_output_tests/` que faz \input dos ficheiros fonte.
"""
from __future__ import annotations

import argparse
import json
import os
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


REPO_ROOT = Path(__file__).resolve().parents[2]
INDEX_PATH = REPO_ROOT / "ExerciseDatabase" / "index.json"


def load_index(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def filter_exercises(exercises: List[Dict[str, Any]], discipline: Optional[str], module: Optional[str], concept: Optional[str], tipo: Optional[str], tags: List[str], difficulty_min: Optional[int], difficulty_max: Optional[int], status: Optional[str]) -> List[Dict[str, Any]]:
    out = []
    for ex in exercises:
        if discipline and ex.get("discipline") != discipline:
            continue
        if module and ex.get("module") != module:
            continue
        if concept and ex.get("concept") != concept:
            continue
        if tipo and ex.get("tipo") != tipo:
            continue
        if status and ex.get("status") != status:
            continue
        if difficulty_min is not None:
            if ex.get("difficulty") is None or ex.get("difficulty") < difficulty_min:
                continue
        if difficulty_max is not None:
            if ex.get("difficulty") is None or ex.get("difficulty") > difficulty_max:
                continue
        if tags:
            ex_tags = ex.get("tags") or []
            # require that at least one requested tag is present
            if not any(t in ex_tags for t in tags):
                continue
        out.append(ex)
    return out


def generate_tex(selected: List[Dict[str, Any]], out_dir: Path, title: str = "Teste gerado") -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = out_dir / f"test_{ts}.tex"

    with out_file.open("w", encoding="utf-8") as f:
        f.write("% Auto-gerado by generate_tests.py\n")
        f.write(f"% Generated: {datetime.now().isoformat()}\n")
        f.write("\\documentclass{article}\n")
        f.write("\\usepackage[utf8]{inputenc}\n")
        f.write("\\usepackage{amsmath,amssymb}\n")
        f.write("\\begin{document}\n")
        f.write(f"\\section*{{{title}}}\n\n")

        for ex in selected:
            ex_id = ex.get("id", "")
            rel_path = Path(ex.get("path", ""))
            # compute path relative to output file (paths in index.json live under ExerciseDatabase/)
            abs_ex = REPO_ROOT / "ExerciseDatabase" / rel_path
            if not abs_ex.exists():
                f.write(f"% WARNING: path not found for {ex_id}: {rel_path}\n")
                continue
            rel = os.path.relpath(abs_ex, start=out_dir)
            f.write(f"% Exercise: {ex_id}\n")
            f.write(f"\\input{{{rel.replace('\\\\', '/')}}}\n\n")

        f.write("\\end{document}\n")

    return out_file


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Gerador de testes a partir do index.json")
    p.add_argument("--discipline", help="discipline id (ex: matematica)")
    p.add_argument("--module", help="module id (ex: P4_funcoes)")
    p.add_argument("--concept", help="concept id (ex: 4-funcao_inversa)")
    p.add_argument("--tipo", help="exercise tipo (ex: determinacao_grafica)")
    p.add_argument("--tags", help="comma-separated tags to match (any)")
    p.add_argument("--difficulty-min", type=int, help="minimum difficulty (inclusive)")
    p.add_argument("--difficulty-max", type=int, help="maximum difficulty (inclusive)")
    p.add_argument("--status", help="status filter (ex: active)")
    p.add_argument("--count", type=int, help="number of exercises to include (default: all)")
    p.add_argument("--shuffle", action="store_true", help="embaralhar seleção antes de escolher")
    p.add_argument("--output-dir", help="diretório de saída (default: ExerciseDatabase/_output_tests)")
    p.add_argument("--title", help="Título do teste no .tex", default="Teste gerado")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    index = load_index(INDEX_PATH)
    exercises = index.get("exercises", [])

    tags = []
    if args.tags:
        tags = [t.strip() for t in args.tags.split(",") if t.strip()]

    filtered = filter_exercises(
        exercises,
        discipline=args.discipline,
        module=args.module,
        concept=args.concept,
        tipo=args.tipo,
        tags=tags,
        difficulty_min=args.difficulty_min,
        difficulty_max=args.difficulty_max,
        status=args.status,
    )

    if not filtered:
        print("No exercises matched the filters. Exiting.")
        return

    if args.shuffle:
        random.shuffle(filtered)

    selected = filtered
    if args.count is not None:
        selected = filtered[: args.count]

    out_dir = Path(args.output_dir) if args.output_dir else (REPO_ROOT / "ExerciseDatabase" / "_output_tests")
    out_file = generate_tex(selected, out_dir, title=args.title)

    print(f"Generated: {out_file}")


if __name__ == "__main__":
    main()
