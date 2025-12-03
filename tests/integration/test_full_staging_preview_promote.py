import pytest
from pathlib import Path


def test_end_to_end_staging_preview_promote(tmp_path, monkeypatch):
    """Full flow: staging -> preview -> promote (integration).

    This test is intended to run only when integration tests are enabled.
    Set environment variable `RUN_INTEGRATION=1` to run it.
    """
    import os
    if os.environ.get("RUN_INTEGRATION") != "1":
        pytest.skip("Integration tests not enabled")

    # This test expects the full stack to be present in ExerciseDatabase._tools
    try:
        from ExerciseDatabase._tools.add_exercise_safe import make_staged_project
        from ExerciseDatabase._tools.preview_system import PreviewManager, create_project_preview
        from ExerciseDatabase._tools.promote_project_from_staging import promote_project
    except Exception:
        pytest.xfail("Full stack modules not available for integration test")

    payload = {
        "title": "E2E Test",
        "discipline": "matematica",
        "module": "P4_funcoes",
        "concept": "4-funcao_inversa",
        "tipo": "determinacao_analitica",
        "difficulty": 2,
        "statement": "E2E enunciado"
    }

    meta = make_staged_project(payload)
    staged_path = meta.get("staged_path")
    preview = create_project_preview(staged_path)
    preview_mgr = PreviewManager(auto_open=False)
    ok = preview_mgr.show_and_confirm(preview, "E2E Preview")
    if ok:
        res = promote_project(meta.get("staged_id"), dry_run=False, force=True)
        assert res.get("status") in ("promoted", "moved")
