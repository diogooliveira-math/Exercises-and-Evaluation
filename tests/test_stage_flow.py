import json


def test_stage_preview_confirm_flow(client, monkeypatch, tmp_path):
    staged_id = "STG_TEST_001"

    # stub make_staged to create a staging dir
    def fake_make_staged(payload):
        staged_dir = tmp_path / "ExerciseDatabase" / "_staging" / staged_id
        staged_dir.mkdir(parents=True, exist_ok=True)
        # write payload.json
        (staged_dir / "payload.json").write_text(json.dumps(payload), encoding="utf-8")
        # write tex
        (staged_dir / f"{staged_id}.tex").write_text("% tex content", encoding="utf-8")
        return {"status": "staged", "staged_id": staged_id, "staged_path": str(staged_dir)}

    monkeypatch.setattr("service.utils_wrappers.make_staged", fake_make_staged)

    # stub get_staging_preview to read from tmp_path
    def fake_get_preview(sid):
        staged_dir = tmp_path / "ExerciseDatabase" / "_staging" / sid
        if not staged_dir.exists():
            raise FileNotFoundError(sid)
        return {f"{sid}.tex": (staged_dir / f"{sid}.tex").read_text(encoding="utf-8")}

    monkeypatch.setattr("service.utils_wrappers.get_staging_preview", fake_get_preview)

    # stub confirm_staged to perform discard
    def fake_confirm(sid, action):
        if action == "promote":
            return {"action": "promoted"}
        elif action == "discard":
            return {"action": "discarded"}
        else:
            raise ValueError()

    monkeypatch.setattr("service.utils_wrappers.confirm_staged", fake_confirm)

    # Make POST to stage
    payload = {
        "discipline": "matematica",
        "module": "P1_tests",
        "concept": "test_concept",
        "tipo": "exercicios_simples",
        "difficulty": 2,
        "statement": "Enunciado de teste"
    }

    resp = client.post("/api/v1/exercises/stage", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "staged"
    assert data["meta"]["staged_id"] == staged_id

    # Preview
    resp2 = client.get(f"/api/v1/staging/{staged_id}/preview")
    assert resp2.status_code == 200
    pv = resp2.json()
    assert f"{staged_id}.tex" in pv["preview"]

    # Confirm promote
    resp3 = client.post(f"/api/v1/staging/{staged_id}/confirm", json={"action": "promote"})
    assert resp3.status_code == 200
    assert resp3.json()["result"]["action"] == "promoted"
