import json
import shutil
from pathlib import Path

from SebentasDatabase._tools.generate_sebentas import staged_to_paths


def make_staged(base_dir: Path, staged_id: str, payload: dict = None, tex: str = None):
    staged_path = base_dir / staged_id
    if staged_path.exists():
        shutil.rmtree(staged_path)
    staged_path.mkdir(parents=True, exist_ok=False)
    if payload:
        with open(staged_path / 'payload.json', 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    if tex is not None:
        with open(staged_path / f"{staged_id}.tex", 'w', encoding='utf-8') as f:
            f.write(tex)
    with open(staged_path / 'metadata.json', 'w', encoding='utf-8') as f:
        json.dump({'staged_id': staged_id}, f, ensure_ascii=False, indent=2)
    return staged_path


def test_missing_payload_still_creates_main_tex():
    repo_root = Path(__file__).resolve().parents[1]
    exercise_db = repo_root / 'ExerciseDatabase'
    staging_dir = exercise_db / '_staging'
    staging_dir.mkdir(parents=True, exist_ok=True)

    staged_id = 'STG_EDGE_NOPAYLOAD'
    staged_path = make_staged(staging_dir, staged_id, payload=None, tex=None)

    resolved = staged_to_paths([staged_id])
    assert len(resolved) == 1
    main_tex = Path(resolved[0]) / 'main.tex'
    assert main_tex.exists()
    content = main_tex.read_text(encoding='utf-8')
    assert '% staged' in content or 'no statement' in content

    # cleanup
    tmp_root = exercise_db / 'temp' / 'staged_for_sebenta'
    try:
        if tmp_root.exists():
            shutil.rmtree(tmp_root)
        if staged_path.exists():
            shutil.rmtree(staged_path)
    except Exception:
        pass


def test_absolute_staged_path_and_invalid_id():
    repo_root = Path(__file__).resolve().parents[1]
    exercise_db = repo_root / 'ExerciseDatabase'
    staging_dir = exercise_db / '_staging'
    staging_dir.mkdir(parents=True, exist_ok=True)

    staged_id = 'STG_EDGE_ABS'
    staged_path = make_staged(staging_dir, staged_id, payload={'discipline': 'fisica', 'module': 'M1', 'concept': 'conc_abs', 'tipo': 't1', 'statement': 'Stmt'}, tex='content')

    # pass absolute path
    resolved = staged_to_paths([str(staged_path.resolve())])
    assert len(resolved) == 1
    main_tex = Path(resolved[0]) / 'main.tex'
    assert main_tex.exists()

    # invalid staged id should be ignored
    resolved2 = staged_to_paths(['STG_DOES_NOT_EXIST'])
    assert isinstance(resolved2, list)
    assert len(resolved2) == 0

    # cleanup
    tmp_root = exercise_db / 'temp' / 'staged_for_sebenta'
    try:
        if tmp_root.exists():
            shutil.rmtree(tmp_root)
        if staged_path.exists():
            shutil.rmtree(staged_path)
    except Exception:
        pass
