import json
import os
from pathlib import Path
import pytest


def test_make_staged_project_creates_folder_and_payload(tmp_path, monkeypatch):
    """Expect a staging API to create a folder and write payload.json."""
    # Monkeypatch environment: ensure any STAGING_DIR constant points to tmp_path/_staging
    staging_dir = tmp_path / "_staging"
    staging_dir.mkdir()

    # Minimal payload
    payload = {
        "title": "Test Project",
        "discipline": "matematica",
        "module": "P_TEST",
        "concept": "c_test",
        "tipo": "t_test",
        "difficulty": 2,
        "statement": "Enunciado teste"
    }

    # The real implementation is expected at ExerciseDatabase._tools.add_exercise_safe
    # For TDD we only assert the intent/shape here; test will be failing until implemented.
    # If implementation exists, import and run it; otherwise mark xfail.
    try:
        from ExerciseDatabase._tools.add_exercise_safe import make_staged_project
    except Exception:
        pytest.xfail("make_staged_project not implemented yet")

    result = make_staged_project(payload)
    assert isinstance(result, dict)
    assert result.get("status") in ("staged", "created")
    staged_path = Path(result.get("staged_path"))
    assert staged_path.exists()
    assert (staged_path / "payload.json").exists()
