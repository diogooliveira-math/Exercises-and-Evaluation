"""Interactive picker for generating a sebenta.

Shows numbered menus for discipline → module → concept → tipo and then calls
`scripts/run_generate_sebenta_task.py` with the chosen values.

For testing/automation, set `SEBENTA_AUTO_CHOICES="discipline,module,concept,tipo"`
(or pass `--auto discipline,module,concept,tipo`). Empty items allowed (e.g. discipline,,concept)
"""
from pathlib import Path
import os
import subprocess
import sys
import argparse

REPO_ROOT = Path(__file__).resolve().parent.parent
EXERCISE_DB = REPO_ROOT / "ExerciseDatabase"


def list_dirs(p: Path):
    if not p.exists():
        return []
    return [d.name for d in sorted(p.iterdir()) if d.is_dir() and not d.name.startswith('_')]


def pick_from_list(prompt: str, options: list):
    if not options:
        print(f"(Nenhuma opção disponível para {prompt})")
        return ""
    print(f"\n{prompt}:")
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    print("  0. (leave empty / skip)")
    while True:
        s = input("Escolha número: ").strip()
        if s == "0" or s == "":
            return ""
        try:
            n = int(s)
            if 1 <= n <= len(options):
                return options[n-1]
        except ValueError:
            pass
        print("Escolha inválida — tente novamente.")


def main():
    parser = argparse.ArgumentParser()
    # Accept either a single CSV string or multiple tokens (PowerShell may split on commas)
    parser.add_argument('--auto', nargs='*', help='Auto choices as CSV or as separate tokens: discipline,module,concept,tipo')
    args = parser.parse_args()

    auto_env = os.environ.get('SEBENTA_AUTO_CHOICES')
    auto_arg = args.auto

    # Normalize auto choices: prefer CLI args if provided, else env var
    if auto_arg:
        # auto_arg can be a list (possibly one item which is a CSV), join with commas
        auto = ','.join(auto_arg)
    else:
        auto = auto_env

    if auto:
        parts = (auto.split(',') + [""]*4)[:4]
        discipline, module, concept, tipo = parts
    else:
        # Interactive picks
        disciplines = list_dirs(EXERCISE_DB)
        discipline = pick_from_list('Disciplina', disciplines)

        modules = list_dirs(EXERCISE_DB / discipline) if discipline else []
        module = pick_from_list('Módulo', modules)

        concepts = list_dirs(EXERCISE_DB / discipline / module) if discipline and module else []
        concept = pick_from_list('Conceito', concepts)

        tipos = []
        if discipline and module and concept:
            concept_path = EXERCISE_DB / discipline / module / concept
            # tipos são subdiretórios do conceito
            tipos = list_dirs(concept_path)
        tipo = pick_from_list('Tipo (opcional)', tipos)

    # Confirm (skip if auto-mode or explicit auto-approve env var)
    print("\nResumo: ")
    print(f"  Disciplina: {discipline or '(todas)'}")
    print(f"  Módulo:     {module or '(todos)'}")
    print(f"  Conceito:   {concept or '(todos)'}")
    print(f"  Tipo:       {tipo or '(todos)'}")

    auto_approve_env = os.environ.get('SEBENTA_AUTO_APPROVE', '')
    auto_mode_enabled = bool(auto) or str(auto_approve_env).lower() in ('1', 'true', 'yes', 's', 'sim')

    if auto_mode_enabled:
        print("Auto-mode enabled: prosseguindo sem confirmação (auto-approve).")
    else:
        cont = input('Continuar? [s/N]: ').strip().lower()
        if cont not in ('s','y','sim','yes'):
            print('Cancelado pelo utilizador')
            sys.exit(0)

    # Prepare env for wrapper
    env = os.environ.copy()
    env['SEBENTA_DISCIPLINE'] = discipline or ''
    env['SEBENTA_MODULE'] = module or ''
    env['SEBENTA_CONCEPT'] = concept or ''
    env['SEBENTA_TIPO'] = tipo or ''
    # Preserve preview/compile choices from env if present; otherwise default to interactive-friendly
    env.setdefault('SEBENTA_NO_PREVIEW', env.get('SEBENTA_NO_PREVIEW', '1'))
    env.setdefault('SEBENTA_NO_COMPILE', env.get('SEBENTA_NO_COMPILE', '1'))
    # If auto-mode (CLI or SEBENTA_AUTO_CHOICES), ensure auto-approve is set
    if auto_mode_enabled:
        env['SEBENTA_AUTO_APPROVE'] = '1'
    else:
        env.setdefault('SEBENTA_AUTO_APPROVE', env.get('SEBENTA_AUTO_APPROVE', '1'))

    # Call wrapper
    wrapper = REPO_ROOT / 'scripts' / 'run_generate_sebenta_task.py'
    cmd = [sys.executable, str(wrapper)]
    print('\nCalling generator...')
    result = subprocess.run(cmd, cwd=str(REPO_ROOT), env=env)
    sys.exit(result.returncode)


if __name__ == '__main__':
    main()
