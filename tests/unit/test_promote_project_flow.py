import pytest
from pathlib import Path


def test_promote_project_dry_run_and_promote(tmp_path, monkeypatch):
    """promote_project should support dry-run and real promotion."""
    staged = tmp_path / "_staging" / "STG_SAMPLE"
    staged.mkdir(parents=True)
    (staged / "payload.json").write_text('{"title":"X"}')

    try:
        from ExerciseDatabase._tools.promote_project_from_staging import promote_project
    except Exception:
        pytest.xfail("promote_project_from_staging not implemented yet")

    plan = promote_project(str(staged), dry_run=True)
    assert isinstance(plan, dict)

    # Attempt real promotion (implementation dependent)
    result = promote_project(str(staged), dry_run=False, force=True)
    assert isinstance(result, dict)
