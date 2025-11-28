#!/usr/bin/env python3
"""Lightweight subprocess logger used by opencode wrappers.

Provides helpers to run commands, capture stdout/stderr and metadata,
and write a structured JSON log alongside raw outputs.
"""
from pathlib import Path
import subprocess
import time
import json
from typing import List, Dict, Any, Optional


def ensure_dir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p


def timestamp() -> float:
    return time.time()


def run_and_log(
    cmd: List[str],
    cwd: Optional[Path],
    log_dir: Path,
    description: str = "",
    env: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Run a command (no shell) and save structured logs.

    Returns a dict with metadata, returncode, stdout, stderr and paths to files.
    """
    ensure_dir(log_dir)
    start = timestamp()
    meta: Dict[str, Any] = {
        "description": description,
        "cmd": cmd,
        "cwd": str(cwd) if cwd else None,
        "env": env if env else None,
        "start": start,
    }

    try:
        proc = subprocess.run(cmd, cwd=str(cwd) if cwd else None, env=env, capture_output=True, text=True)
        rc = proc.returncode
        stdout = proc.stdout
        stderr = proc.stderr
    except FileNotFoundError as e:
        rc = 127
        stdout = ""
        stderr = str(e)

    end = timestamp()
    meta.update({"end": end, "elapsed": end - start, "returncode": rc})

    # save raw outputs
    base = log_dir / f"run_{int(start)}"
    ensure_dir(base)
    out_path = base / "stdout.txt"
    err_path = base / "stderr.txt"
    meta_path = base / "meta.json"

    out_path.write_text(stdout, encoding="utf-8")
    err_path.write_text(stderr, encoding="utf-8")
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")

    # augment meta with paths
    meta["paths"] = {"stdout": str(out_path), "stderr": str(err_path), "meta": str(meta_path)}
    return meta


def save_session_log(session: Dict[str, Any], log_dir: Path) -> Path:
    ensure_dir(log_dir)
    ts = int(time.time())
    path = log_dir / f"session_{ts}.json"
    path.write_text(json.dumps(session, indent=2, ensure_ascii=False), encoding="utf-8")
    return path
