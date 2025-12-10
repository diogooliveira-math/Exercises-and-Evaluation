import json
import time


def test_sebenta_job_creates_metadata_and_log(tmp_path, monkeypatch):
    # Use tmp_path as workspace root
    monkeypatch.chdir(tmp_path)

    # Create fake SebentaGenerator that writes a marker file when run
    class FakeGen:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def scan_and_generate(self, staged=None):
            # simulate generating output
            import os
            log_dir = os.path.join("temp", "opencode_logs")
            os.makedirs(log_dir, exist_ok=True)
            # write a small file to indicate work
            with open(os.path.join(log_dir, "fake_gen_marker.txt"), "w", encoding="utf-8") as f:
                f.write("generated")

    # Monkeypatch the SebentaGenerator used by service.jobs and the import path
    import service.jobs as jobs_mod
    # ensure the import inside the thread uses our FakeGen
    try:
        import SebentasDatabase._tools.generate_sebentas as genmod
        monkeypatch.setattr(genmod, "SebentaGenerator", FakeGen, raising=False)
    except Exception:
        # if module not importable in test env, set attribute on jobs module so fallback picks it
        jobs_mod.SebentaGenerator = FakeGen

    jm = jobs_mod.JobManager(workspace_root=str(tmp_path))
    payload = {"module": "P1_tests"}
    job_id = jm.submit_job("sebenta_generate", payload)

    # wait for job to finish (timeout)
    timeout = 5.0
    interval = 0.05
    elapsed = 0.0
    status = None
    while elapsed < timeout:
        status = jm.get_job_status(job_id)
        if status and status.get("status") in ("finished", "failed"):
            break
        time.sleep(interval)
        elapsed += interval

    assert status is not None
    assert status.get("status") == "finished"

    # assert log exists and marker file created
    log_path = tmp_path / "temp" / "opencode_logs" / f"{job_id}.log"
    assert log_path.exists()
    marker = tmp_path / "temp" / "opencode_logs" / "fake_gen_marker.txt"
    assert marker.exists()
