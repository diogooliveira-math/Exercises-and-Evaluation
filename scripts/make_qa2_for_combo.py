from pathlib import Path
import importlib.util
import sys
import shutil

REPO = Path(__file__).resolve().parent.parent
gen_path = REPO / 'SebentasDatabase' / '_tools' / 'generate_tests.py'
spec = importlib.util.spec_from_file_location('sebenta_generate_tests', str(gen_path))
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

PROJECT_ROOT = REPO

def make_qa2(discipline: str, module: str, concept: str, qa2_root: Path):
    index = gen.load_index(PROJECT_ROOT / 'ExerciseDatabase' / 'index.json')
    exercises = index.get('exercises', [])
    # find config
    config_path = gen.find_config(discipline, module, concept, None)
    config = gen.load_config(config_path) if config_path else {}
    filters = {'discipline': discipline, 'module': module, 'concept': concept, 'tipo': None}
    rng = gen.random.Random(42)
    selected = gen.select_by_config(exercises, config, filters, rng)
    # If per_tipo in config yields empty selection for this concept, fallback to pool selection
    if not selected:
        # Build pool matching filters
        pool = [e for e in exercises if (not filters['discipline'] or e.get('discipline') == filters['discipline'])
                and (not filters['module'] or e.get('module') == filters['module'])
                and (not filters['concept'] or e.get('concept') == filters['concept'])]
        if pool:
            count = config.get('count') or len(pool)
            selected = pool[:count]
        else:
            print('No exercises selected')
            return
    # build content metadata (we'll not inline exercises; instead reference them)
    _, assets = gen.build_test_content(selected, PROJECT_ROOT, config)

    qa2_concept_tex = qa2_root / discipline / module / concept / 'tex'
    qa2_concept_tex.mkdir(parents=True, exist_ok=True)
    exercises_tex = qa2_concept_tex / 'exercises.tex'

    # Create a minimal wrapper that uses \IncludeExercise for each exercise
    lines = []
    lines.append('% Auto-generated QA2 exercises wrapper')
    lines.append('% This file references source exercises stored in exercises.d/')
    lines.append('\\begin{document}')
    # copy assets
    gen.copy_assets_to_output(assets, qa2_concept_tex, PROJECT_ROOT)
    # copy source files
    exercises_d = qa2_concept_tex / 'exercises.d'
    exercises_d.mkdir(exist_ok=True)
    copied_files = []
    for ex in selected:
        src_rel = ex.get('path')
        if not src_rel:
            continue
        src = PROJECT_ROOT / 'ExerciseDatabase' / src_rel
        print('Considering source:', src)
        if src.is_dir():
            candidate = src / 'main.tex'
            if candidate.exists():
                src = candidate
            else:
                texs = list(src.glob('*.tex'))
                if texs:
                    src = texs[0]
                else:
                    continue
        # If the path lacks extension, try adding .tex
        if not src.exists():
            alt = Path(str(src) + '.tex')
            if alt.exists():
                src = alt
        if src.exists() and src.is_file():
            dest = exercises_d / src.name
            print('Resolved source path exists:', src.exists())
            shutil.copy2(src, dest)
            print('Copied', src, '->', dest)
            copied_files.append(dest.name)

    # Write IncludeExercise lines in the order of selected/copies
    for fname in copied_files:
        include_path = f"exercises.d/{fname}"
        # use double backslash for LaTeX macro escape in Python string literal
        lines.append(f"\\IncludeExercise{{{include_path}}}")

    lines.append('\\end{document}')
    exercises_tex.write_text('\n'.join(lines), encoding='utf-8')

    # copy assets
    gen.copy_assets_to_output(assets, qa2_concept_tex, PROJECT_ROOT)

    print('QA2 generated at', qa2_concept_tex)


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--discipline', required=True)
    p.add_argument('--module', required=True)
    p.add_argument('--concept', required=True)
    p.add_argument('--qa2-root', default=str(REPO / 'temp' / 'QA2_generated'))
    args = p.parse_args()
    make_qa2(args.discipline, args.module, args.concept, Path(args.qa2_root))
