"""Simple job runner for background tasks (sebenta generation).

This module implements a lightweight JobManager that enqueues jobs,
runs them in a background thread, and records job metadata and logs
under `temp/jobs/` and `temp/opencode_logs/` following repository
conventions.

Jobs are deliberately simple so tests can mock the heavy SebentaGenerator
and remain deterministic.
"""
from __future__ import annotations

import json
import os
import uuid
import threading
import time
from datetime import datetime
from typing import Any, Dict, Optional


class JobManager:
    def __init__(self, workspace_root: str = "."):
        self.workspace_root = workspace_root
        self.jobs_dir = os.path.join(self.workspace_root, "temp", "jobs")
        self.logs_dir = os.path.join(self.workspace_root, "temp", "opencode_logs")
        os.makedirs(self.jobs_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)

    def _job_meta_path(self, job_id: str) -> str:
        return os.path.join(self.jobs_dir, f"{job_id}.json")

    def _job_log_path(self, job_id: str) -> str:
        return os.path.join(self.logs_dir, f"{job_id}.log")

    def submit_job(self, job_type: str, payload: Dict[str, Any]) -> str:
        job_id = f"JOB_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}_{uuid.uuid4().hex[:8]}"
        meta = {
            "id": job_id,
            "type": job_type,
            "payload": payload,
            "status": "queued",
            "created_at": datetime.utcnow().isoformat() + "Z",
        }
        # persist metadata
        with open(self._job_meta_path(job_id), "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)

        # start background thread
        thread = threading.Thread(target=self._run_job_thread, args=(job_id, job_type, payload), daemon=True)
        thread.start()
        return job_id

    def _update_meta(self, job_id: str, **updates: Any) -> None:
        path = self._job_meta_path(job_id)
        try:
            with open(path, "r", encoding="utf-8") as f:
                meta = json.load(f)
        except Exception:
            meta = {"id": job_id}
        meta.update(updates)
        tmp_path = path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)
        # On Windows, dest might be briefly locked by another reader; retry a few times
        attempts = 5
        replaced = False
        for attempt in range(attempts):
            try:
                os.replace(tmp_path, path)
                replaced = True
                break
            except PermissionError:
                time.sleep(0.05)

        if not replaced:
            # Fallback: try to write the meta file directly to avoid leaving the job stalled
            try:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(meta, f, indent=2, ensure_ascii=False)
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
            except Exception:
                # Last-resort: attempt to move tmp into place
                try:
                    import shutil
                    shutil.move(tmp_path, path)
                except Exception:
                    # If everything fails, raise to allow upper-level error handling
                    raise

    def _append_log(self, job_id: str, text: str) -> None:
        path = self._job_log_path(job_id)
        with open(path, "a", encoding="utf-8") as f:
            f.write(text)
            f.write("\n")

    def _run_job_thread(self, job_id: str, job_type: str, payload: Dict[str, Any]) -> None:
        self._update_meta(job_id, status="running", started_at=datetime.utcnow().isoformat() + "Z")
        log_path = self._job_log_path(job_id)
        try:
            # current simple job types
            if job_type == "sebenta_generate":
                # Import inside function so tests can monkeypatch service.jobs.SebentaGenerator
                try:
                    from SebentasDatabase._tools.generate_sebentas import SebentaGenerator
                except Exception:
                    # In test environments SebentaGenerator may be monkeypatched on this module
                    SebentaGenerator = globals().get("SebentaGenerator")

                self._append_log(job_id, f"Starting sebenta generation job {job_id}")
                # create generator with non-interactive defaults
                if SebentaGenerator is None:
                    # fallback: simulate work
                    self._append_log(job_id, "SebentaGenerator not available — simulating work")
                    time.sleep(0.1)
                else:
                    gen = SebentaGenerator(no_preview=True, no_compile=True, auto_approve=True)
                    # Prefer staged path list in payload
                    staged = payload.get("staged_list")
                    if staged:
                        gen.scan_and_generate(staged)
                    else:
                        gen.scan_and_generate()
                    self._append_log(job_id, "SebentaGenerator finished")
            else:
                self._append_log(job_id, f"Unknown job type {job_type} — no-op")
            self._update_meta(job_id, status="finished", finished_at=datetime.utcnow().isoformat() + "Z")
        except Exception as e:
            self._append_log(job_id, f"Job failed: {e}")
            self._update_meta(job_id, status="failed", error=str(e), finished_at=datetime.utcnow().isoformat() + "Z")

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        path = self._job_meta_path(job_id)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
