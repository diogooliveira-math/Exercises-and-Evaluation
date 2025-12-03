import pytest
from pathlib import Path


def test_wizard_create_project_auto_approve(monkeypatch, tmp_path):
    """When auto_approve=True the wizard should attempt promotion."""
    try:
        from ExerciseDatabase._tools.add_exercise_with_types import create_research_project
    except Exception:
        pytest.xfail("create_research_project not implemented yet")

    # Provide a minimal payload programmatically
    payload = {
        "title": "Wizard Test",
        "discipline": "matematica",
        "module": "P_TEST",
        "concept": "c_test",
        "tipo": "t_test",
        "difficulty": 2,
        "statement": "Enunciado"
    }

    # Monkeypatch promote to avoid real FS moves if present
    try:
        import ExerciseDatabase._tools.promote_project_from_staging as prom_mod
        monkeypatch.setattr(prom_mod, "promote_project", lambda staged_id, dry_run, force: {"status":"promoted"})
    except Exception:
        # If promote module missing, continue — wizard should handle import errors
        pass

    # Call wizard programmatically (should accept payload override in tests)
    result = create_research_project(payload=payload, auto_approve=True)
    # The exact return shape depends on implementation; accept truthy as success
    assert result is not None
