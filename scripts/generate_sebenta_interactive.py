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

# Ensure Python IO encoding is compatible with the test harness on Windows.
# Set PYTHONIOENCODING early so the interpreter decodes/encodes stdout/stderr using
# cp1252 with replacement for unsupported characters.
if sys.platform == 'win32':
    try:
        os.environ['PYTHONIOENCODING'] = 'cp1252:replace'
    except Exception:
        pass

# Additionally wrap print to avoid writing raw UTF-8 bytes from helper libraries
try:
    import io, builtins
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='cp1252', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='cp1252', errors='replace', line_buffering=True)
    _orig_print = builtins.print
    def _safe_print(*args, sep=' ', end='\n', file=None, flush=False):
        try:
            text = sep.join(str(a) for a in args) + end
            sys.stdout.buffer.write(text.encode('cp1252', errors='replace'))
            if flush:
                try:
                    sys.stdout.flush()
                except Exception:
                    pass
        except Exception:
            _orig_print(*args, sep=sep, end=end, file=file, flush=flush)
    builtins.print = _safe_print
except Exception:
    try:
        sys.stdout.reconfigure(encoding='cp1252', errors='replace')
        sys.stderr.reconfigure(encoding='cp1252', errors='replace')
    except Exception:
        pass

REPO_ROOT = Path(__file__).resolve().parent.parent
EXERCISE_DB = REPO_ROOT / "ExerciseDatabase"


def list_dirs(p: Path):
    if not p.exists():
        return []
    return [d.name for d in sorted(p.iterdir()) if d.is_dir() and not d.name.startswith('_')]


def pick_from_list(prompt: str, options: list, allow_multiple: bool = False):
    if not options:
        print(f"(Nenhuma opção disponível para {prompt})")
        return [] if allow_multiple else ""
    print(f"\n{prompt}:")
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    if allow_multiple:
        print("  0. (nenhum / skip)")
        print("  Pode escolher múltiplas opções separadas por vírgula (ex: 1,3,5)")
    else:
        print("  0. (leave empty / skip)")
    while True:
        s = input("Escolha: ").strip()
        if s == "0" or s == "":
            return [] if allow_multiple else ""
        
        if allow_multiple:
            # Parse multiple choices
            choices = []
            parts = s.split(',')
            for part in parts:
                part = part.strip()
                if part == "":
                    continue
                try:
                    n = int(part)
                    if 1 <= n <= len(options):
                        choices.append(options[n-1])
                    else:
                        print(f"Número {n} inválido")
                        choices = []
                        break
                except ValueError:
                    print(f"'{part}' não é um número válido")
                    choices = []
                    break
            if choices:
                return choices
        else:
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
        discipline = pick_from_list('Disciplinas (múltiplas permitidas)', disciplines, allow_multiple=True)

        modules = []
        if discipline:
            # Use first discipline to list modules, but allow selection from all
            all_modules = set()
            for disc in discipline:
                all_modules.update(list_dirs(EXERCISE_DB / disc))
            modules = sorted(list(all_modules))
        module = pick_from_list('Módulos (múltiplos permitidos)', modules, allow_multiple=True)

        concepts = []
        if discipline and module:
            # Use first discipline/module to list concepts, but allow selection from all combinations
            all_concepts = set()
            for disc in discipline:
                for mod in module:
                    concept_path = EXERCISE_DB / disc / mod
                    if concept_path.exists():
                        all_concepts.update(list_dirs(concept_path))
            concepts = sorted(list(all_concepts))
        concept = pick_from_list('Conceitos (múltiplos permitidos)', concepts, allow_multiple=True)

        tipos = []
        if discipline and module and concept:
            # Use first path to list tipos, but allow selection from all
            all_tipos = set()
            for disc in discipline:
                for mod in module:
                    for conc in concept:
                        tipo_path = EXERCISE_DB / disc / mod / conc
                        if tipo_path.exists():
                            all_tipos.update(list_dirs(tipo_path))
            tipos = sorted(list(all_tipos))
        tipo = pick_from_list('Tipos (múltiplos permitidos)', tipos, allow_multiple=True)

    # Confirm (skip if auto-mode or explicit auto-approve env var)
    print("\nResumo: ")
    print(f"  Disciplinas: {', '.join(discipline) if discipline else '(todas)'}")
    print(f"  Módulos:     {', '.join(module) if module else '(todos)'}")
    print(f"  Conceitos:   {', '.join(concept) if concept else '(todos)'}")
    print(f"  Tipos:       {', '.join(tipo) if tipo else '(todos)'}")

    auto_approve_env = os.environ.get('SEBENTA_AUTO_APPROVE', '')
    auto_mode_enabled = bool(auto) or str(auto_approve_env).lower() in ('1', 'true', 'yes', 's', 'sim')

    no_preview = '1'  # default to no preview
    no_compile = '1'  # default to no compile
    user_confirmed = False

    if auto_mode_enabled:
        print("Auto-mode enabled: prosseguindo sem confirmação (auto-approve).")
        user_confirmed = True
    else:
        # Ask for preview preference
        preview_input = input('Deseja pré-visualização antes de compilar? [S/n]: ').strip().lower()
        want_preview = preview_input not in ('n', 'no', 'não')
        
        # Ask for compile preference
        compile_input = input('Deseja compilar PDF? [S/n]: ').strip().lower()
        want_compile = compile_input not in ('n', 'no', 'não')
        
        cont = input('Continuar? [s/N]: ').strip().lower()
        if cont not in ('s','y','sim','yes'):
            print('Cancelado pelo utilizador')
            sys.exit(0)
        else:
            user_confirmed = True
        
        # Set flags based on user input
        no_preview = '0' if want_preview else '1'
        no_compile = '0' if want_compile else '1'

    # Prepare env for wrapper
    env = os.environ.copy()
    env['SEBENTA_DISCIPLINE'] = ','.join(discipline) if discipline else ''
    env['SEBENTA_MODULE'] = ','.join(module) if module else ''
    env['SEBENTA_CONCEPT'] = ','.join(concept) if concept else ''
    env['SEBENTA_TIPO'] = ','.join(tipo) if tipo else ''
    # Set preview/compile based on user input or defaults
    env['SEBENTA_NO_PREVIEW'] = no_preview
    env['SEBENTA_NO_COMPILE'] = no_compile
    # If user explicitly confirmed or auto-mode, set auto-approve to avoid nested prompts
    if user_confirmed:
        env['SEBENTA_AUTO_APPROVE'] = '1'
    else:
        # fallback: only auto-approve if no preview and no compile
        if no_preview == '1' and no_compile == '1':
            env['SEBENTA_AUTO_APPROVE'] = '1'
        else:
            env['SEBENTA_AUTO_APPROVE'] = '0'

    # Call wrapper
    wrapper = REPO_ROOT / 'scripts' / 'run_generate_sebenta_task.py'
    cmd = [sys.executable, str(wrapper)]
    print('\nCalling generator...')
    result = subprocess.run(cmd, cwd=str(REPO_ROOT), env=env)
    sys.exit(result.returncode)


if __name__ == '__main__':
    main()
