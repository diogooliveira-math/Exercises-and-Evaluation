#!/usr/bin/env python3
"""
Interactive helper to choose which sebenta(s) to generate.

Scans `ExerciseDatabase` for disciplines, modules, concepts and tipos
and lets the user pick via numbered menus. Then invokes
`SebentasDatabase/_tools/generate_sebentas.py` with the chosen filters.

It also reads environment variables `SEBENTA_NO_PREVIEW` and
`SEBENTA_AUTO_APPROVE` (set by the VS Code task inputs) to default flags.
"""

from pathlib import Path
import os
import subprocess
import sys
from typing import List, Optional

PROJECT_ROOT = Path(__file__).parent.parent
EXERCISE_DB = PROJECT_ROOT / "ExerciseDatabase"
GENERATOR = PROJECT_ROOT / "SebentasDatabase" / "_tools" / "generate_sebentas.py"


def list_dirs(p: Path) -> List[Path]:
    if not p.exists():
        return []
    return [d for d in sorted(p.iterdir()) if d.is_dir() and not d.name.startswith('_')]


def pick_one_or_all(items: List[Path], prompt: str) -> Optional[str]:
    if not items:
        print(f"Nenhuma opção encontrada para: {prompt}")
        return None

    print(f"\n{prompt}")
    print("0) [Todos]")
    for i, it in enumerate(items, start=1):
        print(f"{i}) {it.name}")

    choice = input("Escolha (número, separar por ',' para múltiplas seleções, ENTER = Todos): ").strip()
    if choice == "" or choice == "0":
        return ""  # signify all

    # allow comma separated selection but we will return a comma-joined string
    parts = [c.strip() for c in choice.split(',') if c.strip()]
    selected = []
    for p in parts:
        try:
            idx = int(p)
            if 1 <= idx <= len(items):
                selected.append(items[idx-1].name)
        except ValueError:
            # allow direct name
            if p in [it.name for it in items]:
                selected.append(p)

    return ",".join(selected) if selected else ""


def pick_tipo_for_concept(concept_path: Path) -> Optional[str]:
    tipos = list_dirs(concept_path)
    if not tipos:
        return ""
    print(f"\nTipos de exercício encontrados em {concept_path.name}:")
    print("0) [Todos]")
    for i, t in enumerate(tipos, start=1):
        print(f"{i}) {t.name}")

    choice = input("Escolha tipo (número ou ENTER = Todos): ").strip()
    if choice == "" or choice == "0":
        return ""
    try:
        idx = int(choice)
        if 1 <= idx <= len(tipos):
            return tipos[idx-1].name
    except ValueError:
        if choice in [t.name for t in tipos]:
            return choice

    return ""


def main():
    if not EXERCISE_DB.exists():
        print(f"ExerciseDatabase não encontrada em: {EXERCISE_DB}")
        sys.exit(1)

    disciplines = list_dirs(EXERCISE_DB)
    discipline = pick_one_or_all(disciplines, "Disciplinas disponíveis:")
    # If multiple disciplines selected, for simplicity we only support one here
    if discipline and "," in discipline:
        # take the first
        discipline = discipline.split(',')[0]

    modules = []
    if discipline == "" or discipline is None:
        # all disciplines => show modules across first discipline as example
        # but ask user to type discipline if they want filtering
        print("\nNenhuma disciplina específica selecionada. O sistema irá processar todas as disciplinas.")
        module = ""
    else:
        modules_dir = EXERCISE_DB / discipline
        modules = list_dirs(modules_dir)
        module = pick_one_or_all(modules, f"Módulos em {discipline}:")
        if module and "," in module:
            # If multiple modules selected, we'll iterate them later
            pass

    concept = ""
    tipo = ""

    # If user selected a single module, allow picking a concept
    if module and module != "":
        # If user selected multiple modules, skip per-concept selection and let generator handle
        if "," not in module:
            module_path = EXERCISE_DB / discipline / module
            concepts = list_dirs(module_path)
            concept = pick_one_or_all(concepts, f"Conceitos em {discipline}/{module}:")
            if concept and "," not in concept and concept != "":
                # ask for tipos in that concept
                tipo = pick_tipo_for_concept(module_path / concept)

    # Flags: read from env vars if present
    env_no_preview = os.environ.get('SEBENTA_NO_PREVIEW', '').lower()
    env_auto_approve = os.environ.get('SEBENTA_AUTO_APPROVE', '').lower()
    env_no_compile = os.environ.get('SEBENTA_NO_COMPILE', '').lower()

    def ask_flag(env_val: str, prompt: str, default: bool = False) -> bool:
        if env_val in ['1', 'true', 'yes', 's', 'sim']:
            return True
        if env_val in ['0', 'false', 'no', 'n', 'nao', 'não']:
            return False
        ans = input(f"{prompt} (s/n) [default: {'s' if default else 'n'}]: ").strip().lower()
        if ans in ['s','sim','y','yes']:
            return True
        if ans in ['n','nao','no','não']:
            return False
        return default

    no_compile = ask_flag(env_no_compile, "Gerar apenas .tex (não compilar PDFs)?", default=True)
    no_preview = ask_flag(env_no_preview, "Desabilitar preview antes de compilar?", default=False)
    auto_approve = ask_flag(env_auto_approve, "Aprovar automaticamente sem pedir confirmação?", default=False)

    # Build calls
    python_exec = sys.executable

    # If multiple modules selected (comma-separated), call generator per module
    modules_to_run = []
    if module == "":
        # no module filter -> call once with discipline/concept/tipo as applicable
        modules_to_run = [None]
    elif "," in module:
        modules_to_run = [m.strip() for m in module.split(',') if m.strip()]
    else:
        modules_to_run = [module]

    for mod in modules_to_run:
        cmd = [python_exec, str(GENERATOR)]
        if discipline and discipline != "":
            cmd += ["--discipline", discipline]
        if mod:
            cmd += ["--module", mod]
        if concept and concept != "":
            cmd += ["--concept", concept]
        if tipo and tipo != "":
            cmd += ["--tipo", tipo]
        if no_compile:
            cmd += ["--no-compile"]
        if no_preview:
            cmd += ["--no-preview"]
        if auto_approve:
            cmd += ["--auto-approve"]

        print("\nInvocando:")
        print(" ".join(cmd))

        try:
            result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
            if result.returncode != 0:
                print(f"generate_sebentas.py retornou código {result.returncode}")
        except Exception as e:
            print(f"Erro ao invocar generator: {e}")


if __name__ == '__main__':
    main()
