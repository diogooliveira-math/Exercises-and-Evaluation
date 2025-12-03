import json
import os


def test_promote_staged_item(client, monkeypatch, tmp_path):
    staged_id = "STG_PROM_001"
    # create staging dir and payload
    staged_dir = tmp_path / "ExerciseDatabase" / "_staging" / staged_id
    staged_dir.mkdir(parents=True)
    payload = {
        "discipline": "matematica",
        "module": "P1_tests",
        "concept": "test_concept",
        "tipo": "exercicios_simples",
        "difficulty": 2,
        "statement": "Enunciado promovido",
        "tags": ["unit"]
    }
    (staged_dir / "payload.json").write_text(json.dumps(payload), encoding="utf-8")
    (staged_dir / f"{staged_id}.tex").write_text("% promoted tex", encoding="utf-8")

    # run inside tmp_path as cwd so utils_wrappers uses the tmp ExerciseDatabase
    monkeypatch.chdir(tmp_path)

    # call API to promote
    resp = client.post(f"/api/v1/staging/{staged_id}/confirm", json={"action": "promote"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["result"]["action"] == "promoted"

    # staged dir removed and dest exists
    staged_path = tmp_path / "ExerciseDatabase" / "_staging" / staged_id
    assert not staged_path.exists()

    dest_dir = tmp_path / "ExerciseDatabase" / payload["discipline"] / payload["module"] / payload["concept"] / payload["tipo"] / staged_id
    assert dest_dir.exists()

    # index.json created and contains the entry
    index_path = tmp_path / "ExerciseDatabase" / "index.json"
    assert index_path.exists()
    idx = json.loads(index_path.read_text(encoding="utf-8"))
    assert any(e.get("id") == staged_id for e in idx.get("exercises", []))
