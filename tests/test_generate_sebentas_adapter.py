import json
import shutil
from pathlib import Path

from SebentasDatabase._tools.generate_sebentas import staged_to_paths


def test_staged_to_paths_smoke():
    """Smoke test for staged_to_paths: creates a staged entry and ensures
    the adapter returns an exercise path with a main.tex containing the statement.
    """
    repo_root = Path(__file__).resolve().parents[1]
    exercise_db = repo_root / 'ExerciseDatabase'
    staging_dir = exercise_db / '_staging'
    staging_dir.mkdir(parents=True, exist_ok=True)

    staged_id = 'STG_TEST_SMOKE'
    staged_path = staging_dir / staged_id
    if staged_path.exists():
        shutil.rmtree(staged_path)
    staged_path.mkdir(parents=True, exist_ok=False)

    payload = {
        'discipline': 'matematica',
        'module': 'P0_testes',
        'concept': 'conceito_teste',
        'tipo': 'exercicios_simples',
        'difficulty': '1',
        'statement': 'Encontre x tal que x + 1 = 2.'
    }

    with open(staged_path / 'payload.json', 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    with open(staged_path / f"{staged_id}.tex", 'w', encoding='utf-8') as f:
        f.write('% preview\n')
        f.write(payload['statement'])

    meta = {
        'status': 'staged',
        'staged_id': staged_id,
        'staged_path': str(staged_path.resolve()),
    }
    with open(staged_path / 'metadata.json', 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    # Run the adapter
    resolved = staged_to_paths([staged_id])
    assert isinstance(resolved, list)
    assert len(resolved) == 1

    exercise_dir = Path(resolved[0])
    main_tex = exercise_dir / 'main.tex'
    assert main_tex.exists(), f"expected main.tex at {main_tex}"

    content = main_tex.read_text(encoding='utf-8')
    assert 'Encontre x tal que x + 1 = 2.' in content

    # cleanup temp staged_for_sebenta and staging entry
    tmp_root = exercise_db / 'temp' / 'staged_for_sebenta'
    try:
        if tmp_root.exists():
            shutil.rmtree(tmp_root)
        if staged_path.exists():
            shutil.rmtree(staged_path)
    except Exception:
        pass
