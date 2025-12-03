import time
import os


def test_sebenta_generate_api_integration(client, monkeypatch, tmp_path):
    """Integration test: call the API endpoint to enqueue a sebenta job and poll status.

    We patch the SebentaGenerator used by the background thread so work is deterministic.
    """
    # run inside isolated tmp_path
    monkeypatch.chdir(tmp_path)

    # Fake generator writes a marker file
    class FakeGen:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def scan_and_generate(self, staged=None):
            log_dir = os.path.join("temp", "opencode_logs")
            os.makedirs(log_dir, exist_ok=True)
            with open(os.path.join(log_dir, "api_integration_marker.txt"), "w", encoding="utf-8") as f:
                f.write("ok")

    # Patch the module that JobManager will import inside the worker thread
    try:
        import SebentasDatabase._tools.generate_sebentas as genmod
        monkeypatch.setattr(genmod, "SebentaGenerator", FakeGen, raising=False)
    except Exception:
        # fallback to set attribute on jobs module
        import service.jobs as jobs_mod
        jobs_mod.SebentaGenerator = FakeGen

    # Call API to generate
    resp = client.post("/api/v1/sebentas/generate", json={"module": "P1_tests"})
    assert resp.status_code == 200
    job_id = resp.json()["job_id"]

    # Poll status until finished
    timeout = 10.0
    interval = 0.05
    elapsed = 0.0
    status = None
    while elapsed < timeout:
        resp2 = client.get(f"/api/v1/sebentas/status/{job_id}")
        if resp2.status_code == 200:
            status = resp2.json()
            if status.get("status") in ("finished", "failed"):
                break
        time.sleep(interval)
        elapsed += interval

    assert status is not None
    assert status.get("status") == "finished"

    # Check marker file exists
    marker = tmp_path / "temp" / "opencode_logs" / "api_integration_marker.txt"
    assert marker.exists()
