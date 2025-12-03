import pytest
from fastapi.testclient import TestClient
from service.fastapi_app import app


@pytest.fixture
def client():
    return TestClient(app)
import importlib
from pathlib import Path
import shutil

import pytest


@pytest.fixture
def gen_module(tmp_path, monkeypatch):
    """Import the generate_sebentas module and monkeypatch its PROJECT_ROOT,
    EXERCISE_DB, and SEBENTAS_DB to point to an isolated tmp_path.
    Returns the imported module object.
    """
    # Create isolated project layout
    project_root = tmp_path / 'project'
    exercise_db = project_root / 'ExerciseDatabase'
    sebentas_db = project_root / 'SebentasDatabase'
    exercise_db.mkdir(parents=True, exist_ok=True)
    sebentas_db.mkdir(parents=True, exist_ok=True)

    # Import module fresh
    mod_name = 'SebentasDatabase._tools.generate_sebentas'
    if mod_name in globals().get('__import__', {}):
        pass
    # Import using importlib
    gen = importlib.import_module(mod_name)

    # Monkeypatch module-level paths
    monkeypatch.setattr(gen, 'PROJECT_ROOT', project_root)
    monkeypatch.setattr(gen, 'EXERCISE_DB', exercise_db)
    monkeypatch.setattr(gen, 'SEBENTAS_DB', sebentas_db)

    # Ensure log dir exists in the temporary sebentas db
    (sebentas_db / 'logs').mkdir(parents=True, exist_ok=True)

    yield gen

    # cleanup: remove temp project (pytest tmp_path is auto-removed)
    try:
        shutil.rmtree(str(project_root))
    except Exception:
        pass
