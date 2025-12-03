import json
from pathlib import Path
import shutil

import pytest


def test_promote_project_dry_run_and_promote(tmp_path, monkeypatch):
    # Import module under test
    from ExerciseDatabase._tools import promote_project_from_staging as promo
    from ExerciseDatabase._tools import index_utils

    # Redirect STAGING_DIR, PROJECTS_DIR and INDEX_FILE to tmp_path to avoid repo pollution
    monkeypatch.setattr(promo, 'STAGING_DIR', tmp_path / 'staging')
    monkeypatch.setattr(promo, 'PROJECTS_DIR', tmp_path / 'projects')
    monkeypatch.setattr(promo, 'INDEX_FILE', tmp_path / 'index.json')

    staged_dir = promo.STAGING_DIR
    staged_dir.mkdir(parents=True)

    staged_id = 'STG_PROMO_TEST'
    staged_path = staged_dir / staged_id
    staged_path.mkdir()

    # Create payload.json and metadata.json inside staged folder
    payload = {
        'id': 'PROJ_PROMO_001',
        'titulo': 'Promo Test',
        'responsavel': 'Tester',
        'summary': 'A test project',
    }
    (staged_path / 'payload.json').write_text(json.dumps(payload, ensure_ascii=False))
    meta = {'status': 'staged', 'staged_id': staged_id}
    (staged_path / 'metadata.json').write_text(json.dumps(meta, ensure_ascii=False))

    # Create a dummy file to be moved
    (staged_path / 'README.md').write_text('# Promo Test')

    # Dry-run should not move files
    result = promo.promote_project(staged_id, dry_run=True)
    assert result['dry_run'] is True
    assert staged_path.exists()

    # Now promote for real
    result = promo.promote_project(staged_id, dry_run=False)
    assert result['promoted'] is True
    # New project dir should exist under PROJECTS_DIR
    project_id = result['project_id']
    dest = promo.PROJECTS_DIR / project_id
    assert dest.exists()
    assert (dest / 'README.md').exists()

    # Index should be updated
    index = json.loads(promo.INDEX_FILE.read_text(encoding='utf-8'))
    assert 'projects' in index
    assert any(p['id'] == project_id for p in index['projects'])
