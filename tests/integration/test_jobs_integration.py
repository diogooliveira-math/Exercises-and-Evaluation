import json
import time


def test_job_manager_with_fake_sebenta_generator(tmp_path, monkeypatch):
    """Integration-style test: run the real JobManager but patch the
    SebentaGenerator used by the background thread so the job does real
    work in a controlled way.
    """
    # Use tmp_path as working directory
    monkeypatch.chdir(tmp_path)

    # Create a Fake generator that writes a marker file when run
    class FakeGen:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def scan_and_generate(self, staged=None):
            import os
            log_dir = os.path.join("temp", "opencode_logs")
            os.makedirs(log_dir, exist_ok=True)
            with open(os.path.join(log_dir, "integration_fake_marker.txt"), "w", encoding="utf-8") as f:
                f.write("ok")

    # Patch the generator in the module that JobManager will import inside the thread
    try:
        import SebentasDatabase._tools.generate_sebentas as genmod
        monkeypatch.setattr(genmod, "SebentaGenerator", FakeGen)
    except Exception:
        # If module not present, set on globals for fallback in service.jobs
        import service.jobs as jobs_mod
        jobs_mod.SebentaGenerator = FakeGen

    # Now create a real JobManager and submit a job
    from service.jobs import JobManager

    jm = JobManager(workspace_root=str(tmp_path))
    job_id = jm.submit_job("sebenta_generate", {"module": "P1_tests"})

    # wait for completion
    timeout = 10.0
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

    # Verify log and marker file exist
    log_path = tmp_path / "temp" / "opencode_logs" / f"{job_id}.log"
    assert log_path.exists()
    marker = tmp_path / "temp" / "opencode_logs" / "integration_fake_marker.txt"
    assert marker.exists()
