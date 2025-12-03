import json
import os


def test_sebenta_generate_and_status_api(client, monkeypatch, tmp_path):
    # Use tmp_path as cwd for isolation
    monkeypatch.chdir(tmp_path)

    # Fake JobManager that writes metadata and log synchronously
    class FakeJM:
        def __init__(self, workspace_root: str = "."):
            self.workspace_root = workspace_root

        def submit_job(self, job_type: str, payload: dict):
            job_id = "JOB_TEST_SYNC_1"
            jobs_dir = os.path.join(self.workspace_root, "temp", "jobs")
            logs_dir = os.path.join(self.workspace_root, "temp", "opencode_logs")
            os.makedirs(jobs_dir, exist_ok=True)
            os.makedirs(logs_dir, exist_ok=True)
            meta = {"id": job_id, "type": job_type, "payload": payload, "status": "finished"}
            with open(os.path.join(jobs_dir, f"{job_id}.json"), "w", encoding="utf-8") as f:
                json.dump(meta, f)
            with open(os.path.join(logs_dir, f"{job_id}.log"), "w", encoding="utf-8") as f:
                f.write("done")
            return job_id

        def get_job_status(self, job_id: str):
            path = os.path.join(self.workspace_root, "temp", "jobs", f"{job_id}.json")
            if not os.path.exists(path):
                return None
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)

    # Monkeypatch JobManager used by the API router
    import service.api_router as api_mod
    monkeypatch.setattr(api_mod, "JobManager", FakeJM)

    # Call generate endpoint
    resp = client.post("/api/v1/sebentas/generate", json={"module": "P1_tests"})
    assert resp.status_code == 200
    data = resp.json()
    job_id = data["job_id"]

    # Get status
    resp2 = client.get(f"/api/v1/sebentas/status/{job_id}")
    assert resp2.status_code == 200
    st = resp2.json()
    assert st["id"] == job_id
    assert st["status"] == "finished"
