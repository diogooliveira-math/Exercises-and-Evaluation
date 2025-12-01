import json
import shutil
from pathlib import Path


def make_staged(staging_dir: Path, staged_id: str, payload: dict, tex: str = None):
    staged_path = staging_dir / staged_id
    if staged_path.exists():
        shutil.rmtree(staged_path)
    staged_path.mkdir(parents=True, exist_ok=False)
    with open(staged_path / 'payload.json', 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    if tex is not None:
        with open(staged_path / f"{staged_id}.tex", 'w', encoding='utf-8') as f:
            f.write(tex)
    with open(staged_path / 'metadata.json', 'w', encoding='utf-8') as f:
        json.dump({'staged_id': staged_id}, f, ensure_ascii=False, indent=2)
    return staged_path


def test_e2e_stage_and_generate_programmatic(gen_module):
    """Programmatic e2e: create staged entries in the isolated ExerciseDatabase,
    convert to exercise paths with staged_to_paths(), and call the generator directly.
    """
    gen = gen_module
    exercise_db = gen.EXERCISE_DB
    staging_dir = exercise_db / '_staging'
    staging_dir.mkdir(parents=True, exist_ok=True)

    # Stage two exercises
    p1 = {
        'discipline': 'matematica',
        'module': 'P1_funcoes',
        'concept': 'funcoes_basicas',
        'tipo': 'exercicios',
        'difficulty': '2',
        'statement': 'Calcule f(2) para f(x)=x+1.'
    }
    p2 = {
        'discipline': 'matematica',
        'module': 'P1_funcoes',
        'concept': 'funcoes_basicas',
        'tipo': 'exercicios',
        'difficulty': '3',
        'statement': 'Encontre o domínio de f(x)=1/x.'
    }

    sid1 = 'STG_E2E_1'
    sid2 = 'STG_E2E_2'
    make_staged(staging_dir, sid1, p1, tex='% preview\n' + p1['statement'])
    make_staged(staging_dir, sid2, p2, tex='% preview\n' + p2['statement'])

    staged_ids = [sid1, sid2]

    # Convert staged entries into exercise paths
    exercise_paths = gen.staged_to_paths(staged_ids)
    assert len(exercise_paths) == 2

    # Each returned exercise path should contain a main.tex with the staged statement
    main_texts = [ 'Calcule f(2) para f(x)=x+1.', 'Encontre o domínio de f(x)=1/x.' ]
    for idx, p in enumerate(exercise_paths):
        mt = Path(p) / 'main.tex'
        assert mt.exists(), f"expected main.tex at {mt}"
        txt = mt.read_text(encoding='utf-8')
        assert main_texts[idx] in txt

    # Call generator programmatically
    generator = gen.SebentaGenerator(no_compile=True, no_preview=True, auto_approve=True, dump_tex=True)
    generator.scan_and_generate(exercise_paths=exercise_paths)

    # Check that .tex file was created in the isolated SEBENTAS_DB layout
    expected = gen.SEBENTAS_DB / 'matematica' / 'P1_funcoes' / 'funcoes_basicas' / 'sebenta_funcoes_basicas.tex'
    assert expected.exists(), f"Expected generated file at {expected}"

    # Read .tex and assert it contains at least one of the staged statements (generator may overwrite on multiple calls)
    content = expected.read_text(encoding='utf-8')
    assert any(s in content for s in main_texts), 'Expected at least one staged statement in the generated sebenta'

    # generator.stats should reflect at least two generation attempts (one per staged entry)
    assert generator.stats['generated'] >= 2
    assert generator.stats['errors'] == 0
    assert generator.stats['cancelled'] == 0

    # Check that a debug dump was created since dump_tex=True
    debug_dir = gen.SEBENTAS_DB / 'debug'
    debug_files = list(debug_dir.glob('*.tex')) if debug_dir.exists() else []
    assert len(debug_files) >= 1
    # debug file should mention concept name
    assert any('funcoes_basicas' in f.name for f in debug_files)

    # .tex should contain exercise markers and float barrier
    assert '% Exerc' in content
    assert '\\FloatBarrier' in content

    # cleanup: tmp directories are under pytest tmp_path via gen_module fixture, no further cleanup required
