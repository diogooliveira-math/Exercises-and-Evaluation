import json
from pathlib import Path
import shutil
import pytest


def test_make_staged_project_creates_staging(tmp_path, monkeypatch):
    repo_root = Path(__file__).resolve().parents[1]
    tools = repo_root / 'ExerciseDatabase' / '_tools'
    mod_path = tools / 'add_exercise_safe.py'
    assert mod_path.exists(), f"Expected {mod_path} to exist"

    # Import module dynamically
    import importlib.util
    spec = importlib.util.spec_from_file_location('add_exercise_safe_mod', str(mod_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # Redirect STAGING_DIR to tmp_path to avoid polluting repo
    staged_dir = tmp_path / 'staging'
    monkeypatch.setattr(mod, 'STAGING_DIR', staged_dir)

    payload = {
        'titulo': 'Teste Projecto',
        'responsavel': 'Prof. Teste',
        'summary': 'Resumo curto do projecto',
        'discipline': 'matematica'
    }

    # call make_staged_project (should exist as a callable)
    assert hasattr(mod, 'make_staged_project'), 'make_staged_project not implemented yet'
    meta = mod.make_staged_project(payload)

    assert isinstance(meta, dict)
    assert 'staged_id' in meta
    staged_path = staged_dir / meta['staged_id']
    assert staged_path.exists()
    # Check metadata file
    mfile = staged_path / 'metadata.json'
    assert mfile.exists()
    data = json.loads(mfile.read_text(encoding='utf-8'))
    assert data.get('status') == 'staged'
