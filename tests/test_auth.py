import json


def test_write_requires_api_key(client, monkeypatch):
    # set API key in env
    monkeypatch.setenv("API_KEY", "secret123")

    # monkeypatch make_staged to avoid repo imports
    def fake_make_staged(payload):
        return {"status": "staged", "staged_id": "STG_AUTH_1", "staged_path": "/tmp"}

    monkeypatch.setattr("service.utils_wrappers.make_staged", fake_make_staged)

    # no header => forbidden
    payload = {
        "discipline": "matematica",
        "module": "P1_tests",
        "concept": "test_concept",
        "tipo": "exercicios_simples",
        "difficulty": 2,
        "statement": "Enunciado"
    }
    resp = client.post("/api/v1/exercises/stage", json=payload)
    assert resp.status_code == 403


def test_write_with_api_key_allows(client, monkeypatch):
    monkeypatch.setenv("API_KEY", "secret123")

    def fake_make_staged(payload):
        return {"status": "staged", "staged_id": "STG_AUTH_2", "staged_path": "/tmp"}

    monkeypatch.setattr("service.utils_wrappers.make_staged", fake_make_staged)

    payload = {
        "discipline": "matematica",
        "module": "P1_tests",
        "concept": "test_concept",
        "tipo": "exercicios_simples",
        "difficulty": 2,
        "statement": "Enunciado"
    }
    headers = {"X-API-Key": "secret123"}
    resp = client.post("/api/v1/exercises/stage", json=payload, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "staged"
