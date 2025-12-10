import json
import os


def test_make_staged_wrapper_monkeypatch(monkeypatch, tmp_path):
    # prepare fake repo function
    def fake_repo_make_staged(payload):
        return {"status": "staged", "staged_id": "STG_FAKE", "staged_path": "/fake/path"}

    # inject into module namespace
    monkeypatch.setattr("ExerciseDatabase._tools.add_exercise_safe.make_staged", fake_repo_make_staged, raising=False)

    from service.utils_wrappers import make_staged

    meta = make_staged({"discipline": "x", "module": "y", "concept": "z", "tipo": "t", "difficulty": 1, "statement": "s"})
    assert meta["status"] == "staged"
    assert "staged_id" in meta


def test_get_staging_preview_fallback(tmp_path, monkeypatch):
    staged_id = "STG_FB"
    staged_dir = tmp_path / "ExerciseDatabase" / "_staging" / staged_id
    staged_dir.mkdir(parents=True)
    (staged_dir / f"{staged_id}.tex").write_text("hello tex", encoding="utf-8")
    (staged_dir / "payload.json").write_text(json.dumps({}), encoding="utf-8")

    # monkeypatch os.path to point to tmp_path by adjusting cwd behavior
    monkeypatch.chdir(tmp_path)

    from service.utils_wrappers import get_staging_preview

    files = get_staging_preview(staged_id)
    assert f"{staged_id}.tex" in files
