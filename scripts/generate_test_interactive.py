"""Interactive picker for generating a test.

Shows numbered menus for discipline → module → concept → tipo → exercises and then calls
`scripts/run_generate_test_task.py` with the chosen values.

For testing/automation, set `TEST_AUTO_CHOICES="discipline,module,concept,tipo,exercise_ids"`
(or pass `--auto discipline,module,concept,tipo,exercise_ids`). Empty items allowed.
"""
from pathlib import Path
import os
import subprocess
import sys
import argparse
import json

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


def load_exercises_index():
    """Load exercises from index.json"""
    index_file = EXERCISE_DB / "index.json"
    if not index_file.exists():
        return []
    with open(index_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('exercises', [])


def get_exercises_for_selection(discipline, module, concept, tipo):
    """Get exercises matching the current selection criteria"""
    all_exercises = load_exercises_index()
    matching = []

    for ex in all_exercises:
        # Handle both old and new classification structures
        if 'classification' in ex:
            ex_discipline = ex['classification'].get('discipline', '')
            ex_module = ex['classification'].get('module', '')
            ex_concept = ex['classification'].get('concept', '')
            ex_tipo = ex['classification'].get('tipo', '')
        else:
            # Fallback for old structure
            ex_discipline = ex.get('discipline', 'matematica')
            ex_module = ex.get('module', '')
            ex_concept = ex.get('concept', '')
            ex_tipo = ex.get('type', '')

        # Check if exercise matches current filters
        if discipline and ex_discipline not in discipline:
            continue
        if module and ex_module not in module:
            continue
        if concept and ex_concept not in concept:
            continue
        if tipo and ex_tipo not in tipo:
            continue

        matching.append(ex)

    return matching


def pick_exercises_interactive(discipline, module, concept, tipo):
    """Interactive exercise selection with detailed display"""
    print("\n" + "="*70)
    print("  SELEÇÃO DE EXERCÍCIOS INDIVIDUAIS")
    print("="*70)

    # Get available exercises
    available_exercises = get_exercises_for_selection(discipline, module, concept, tipo)

    if not available_exercises:
        print("Nenhum exercício encontrado com os critérios selecionados.")
        return []

    print(f"\nExercícios disponíveis: {len(available_exercises)}")

    # Group by concept and tipo for better display
    grouped = {}
    for ex in available_exercises:
        if 'classification' in ex:
            ex_concept = ex['classification'].get('concept_name', ex['classification'].get('concept', 'Desconhecido'))
            ex_tipo = ex['classification'].get('tipo_nome', ex['classification'].get('tipo', 'Sem tipo'))
        else:
            ex_concept = ex.get('concept_name', ex.get('concept', 'Desconhecido'))
            ex_tipo = ex.get('type', 'Sem tipo')

        key = f"{ex_concept} → {ex_tipo}"
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(ex)

    # Display grouped exercises
    print("\nDistribuição por conceito/tipo:")
    for key, exercises in grouped.items():
        print(f"  • {key}: {len(exercises)} exercícios")

    # Selection modes
    print("\nModos de seleção:")
    print("  1. Seleção manual (escolher exercícios específicos)")
    print("  2. Seleção por quantidade (escolher N exercícios aleatórios)")
    print("  3. Seleção balanceada (distribuir entre tipos)")
    print("  0. Cancelar")

    while True:
        choice = input("\nEscolha modo (0-3): ").strip()

        if choice == "0":
            return []
        elif choice == "1":
            return pick_exercises_manual(available_exercises)
        elif choice == "2":
            return pick_exercises_by_count(available_exercises)
        elif choice == "3":
            return pick_exercises_balanced(available_exercises)
        else:
            print("Opção inválida.")


def pick_exercises_manual(available_exercises):
    """Manual selection of specific exercises"""
    print("\n" + "="*70)
    print("  SELEÇÃO MANUAL DE EXERCÍCIOS")
    print("="*70)

    # Display all exercises with details
    print("\nExercícios disponíveis:")
    for i, ex in enumerate(available_exercises, 1):
        ex_id = ex.get('id', 'N/A')
        if 'classification' in ex:
            concept = ex['classification'].get('concept_name', 'Desconhecido')
            tipo = ex['classification'].get('tipo_nome', 'Sem tipo')
            difficulty = ex['classification'].get('difficulty', 'N/A')
        else:
            concept = ex.get('concept_name', 'Desconhecido')
            tipo = ex.get('type', 'Sem tipo')
            difficulty = ex.get('difficulty', 'N/A')

        print(f"  {i:2d}. [{ex_id}] {concept} / {tipo} (dif: {difficulty})")

    print("\nDigite os números dos exercícios desejados, separados por vírgula.")
    print("Exemplo: 1,3,5,8")

    while True:
        selection = input("Exercícios: ").strip()
        if not selection:
            return []

        try:
            indices = []
            parts = selection.split(',')
            for part in parts:
                part = part.strip()
                if part:
                    idx = int(part) - 1
                    if 0 <= idx < len(available_exercises):
                        indices.append(idx)
                    else:
                        print(f"Número {int(part)} inválido.")
                        indices = []
                        break

            if indices:
                selected = [available_exercises[i] for i in indices]
                print(f"\nSelecionados {len(selected)} exercícios:")
                for ex in selected:
                    print(f"  • {ex.get('id', 'N/A')}")
                return selected

        except ValueError:
            print("Entrada inválida. Use apenas números separados por vírgula.")


def pick_exercises_by_count(available_exercises):
    """Select N random exercises"""
    import random

    max_count = len(available_exercises)
    print(f"\nQuantidade máxima: {max_count}")

    while True:
        try:
            count = int(input(f"Quantos exercícios (1-{max_count}): ").strip())
            if 1 <= count <= max_count:
                selected = random.sample(available_exercises, count)
                print(f"\nSelecionados {len(selected)} exercícios aleatórios:")
                for ex in selected:
                    ex_id = ex.get('id', 'N/A')
                    print(f"  • {ex_id}")
                return selected
            else:
                print(f"Escolha entre 1 e {max_count}.")
        except ValueError:
            print("Digite um número válido.")


def pick_exercises_balanced(available_exercises):
    """Balanced selection across types"""
    import random

    # Group by type
    by_type = {}
    for ex in available_exercises:
        if 'classification' in ex:
            tipo = ex['classification'].get('tipo', 'default')
        else:
            tipo = ex.get('type', 'default')

        if tipo not in by_type:
            by_type[tipo] = []
        by_type[tipo].append(ex)

    print(f"\nEncontrados {len(by_type)} tipos diferentes:")
    for tipo, exercises in by_type.items():
        print(f"  • {tipo}: {len(exercises)} exercícios")

    # Ask for distribution
    selected = []
    for tipo, exercises in by_type.items():
        if len(exercises) <= 3:
            # Take all if few exercises
            selected.extend(exercises)
            print(f"  ✓ {tipo}: todos ({len(exercises)})")
        else:
            # Ask how many
            while True:
                try:
                    count = int(input(f"  Quantos de '{tipo}' (0-{len(exercises)}): ").strip())
                    if 0 <= count <= len(exercises):
                        chosen = random.sample(exercises, count)
                        selected.extend(chosen)
                        print(f"  ✓ {tipo}: {count}")
                        break
                    else:
                        print(f"Escolha entre 0 e {len(exercises)}.")
                except ValueError:
                    print("Digite um número válido.")

    print(f"\nTotal selecionados: {len(selected)} exercícios")
    return selected


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--auto', nargs='*', help='Auto choices as CSV or as separate tokens: discipline,module,concept,tipo,exercise_ids')
    args = parser.parse_args()

    auto_env = os.environ.get('TEST_AUTO_CHOICES')
    auto_arg = args.auto

    # Normalize auto choices: prefer CLI args if provided, else env var
    if auto_arg:
        auto = ','.join(auto_arg)
    else:
        auto = auto_env

    exercise_ids = []
    if auto:
        parts = (auto.split(',') + [""]*5)[:5]
        discipline, module, concept, tipo, exercise_ids_str = parts
        discipline = discipline.split('|') if discipline else []
        module = module.split('|') if module else []
        concept = concept.split('|') if concept else []
        tipo = tipo.split('|') if tipo else []
        exercise_ids = exercise_ids_str.split('|') if exercise_ids_str else []
    else:
        # Interactive picks
        disciplines = list_dirs(EXERCISE_DB)
        discipline = pick_from_list('Disciplinas (múltiplas permitidas)', disciplines, allow_multiple=True)

        modules = []
        if discipline:
            all_modules = set()
            for disc in discipline:
                all_modules.update(list_dirs(EXERCISE_DB / disc))
            modules = sorted(list(all_modules))
        module = pick_from_list('Módulos (múltiplos permitidos)', modules, allow_multiple=True)

        concepts = []
        if discipline and module:
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
            all_tipos = set()
            for disc in discipline:
                for mod in module:
                    for conc in concept:
                        tipo_path = EXERCISE_DB / disc / mod / conc
                        if tipo_path.exists():
                            all_tipos.update(list_dirs(tipo_path))
            tipos = sorted(list(all_tipos))
        tipo = pick_from_list('Tipos (múltiplos permitidos)', tipos, allow_multiple=True)

        # Exercise selection
        if discipline or module or concept or tipo:
            exercise_ids = pick_exercises_interactive(discipline, module, concept, tipo)
            exercise_ids = [ex.get('id', '') for ex in exercise_ids if ex.get('id')]
        else:
            exercise_ids = []

    # Confirm (skip if auto-mode or explicit auto-approve env var)
    print("\nResumo da seleção:")
    print(f"  Disciplinas: {', '.join(discipline) if discipline else '(todas)'}")
    print(f"  Módulos:     {', '.join(module) if module else '(todos)'}")
    print(f"  Conceitos:   {', '.join(concept) if concept else '(todos)'}")
    print(f"  Tipos:       {', '.join(tipo) if tipo else '(todos)'}")
    print(f"  Exercícios:  {len(exercise_ids)} selecionados")

    auto_approve_env = os.environ.get('TEST_AUTO_APPROVE', '')
    auto_mode_enabled = bool(auto) or str(auto_approve_env).lower() in ('1', 'true', 'yes', 's', 'sim')

    no_preview = '1'  # default to no preview
    no_compile = '1'  # default to no compile

    if auto_mode_enabled:
        print("Modo automático ativado: prosseguindo sem confirmação.")
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

        # Set flags based on user input
        no_preview = '0' if want_preview else '1'
        no_compile = '0' if want_compile else '1'

    # Prepare env for wrapper
    env = os.environ.copy()
    env['TEST_DISCIPLINE'] = ','.join(discipline) if discipline else ''
    env['TEST_MODULE'] = ','.join(module) if module else ''
    env['TEST_CONCEPT'] = ','.join(concept) if concept else ''
    env['TEST_TIPO'] = ','.join(tipo) if tipo else ''
    env['TEST_EXERCISE_IDS'] = ','.join(exercise_ids) if exercise_ids else ''
    env['TEST_NO_PREVIEW'] = no_preview
    env['TEST_NO_COMPILE'] = no_compile

    # If auto-mode, ensure auto-approve is set
    if auto_mode_enabled:
        env['TEST_AUTO_APPROVE'] = '1'
    else:
        if want_preview or want_compile:
            env['TEST_AUTO_APPROVE'] = '0'
        else:
            env['TEST_AUTO_APPROVE'] = '1'

    # Call wrapper
    wrapper = REPO_ROOT / 'scripts' / 'run_generate_test_task.py'
    cmd = [sys.executable, str(wrapper)]
    print('\nChamando gerador de testes...')
    result = subprocess.run(cmd, cwd=str(REPO_ROOT), env=env)
    sys.exit(result.returncode)


if __name__ == '__main__':
    main()