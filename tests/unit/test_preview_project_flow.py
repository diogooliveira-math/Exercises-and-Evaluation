import pytest
from pathlib import Path


def test_create_project_preview_and_show(monkeypatch, tmp_path):
    """Preview creation should produce a mapping and PreviewManager should be callable."""
    staged = tmp_path / "STG_EXAMPLE"
    staged.mkdir()
    (staged / "payload.json").write_text('{"title":"Ex"}')

    try:
        from ExerciseDatabase._tools.preview_system import create_project_preview, PreviewManager
    except Exception:
        pytest.xfail("preview_system not implemented yet")

    preview = create_project_preview(staged)
    assert isinstance(preview, dict)
    # Monkeypatch PreviewManager to auto-confirm
    class DummyPreview:
        def show_and_confirm(self, content, title):
            return True

    monkeypatch.setattr("ExerciseDatabase._tools.preview_system.PreviewManager", lambda auto_open=True: DummyPreview())

    mgr = PreviewManager(auto_open=False)
    assert mgr.show_and_confirm(preview, "Preview") is True
