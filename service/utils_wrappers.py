"""Lightweight wrappers around repository utilities for server use.

Functions are small adapters and intentionally thin so tests can monkeypatch them.
"""
from typing import Dict, Any
import json
import os


def make_staged(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Call the repository's add_exercise_safe.make_staged if available.

    Returns the metadata dict from make_staged.
    """
    try:
        from ExerciseDatabase._tools.add_exercise_safe import make_staged as repo_make_staged
    except Exception as e:
        raise RuntimeError("make_staged not available: " + str(e))
    return repo_make_staged(payload)


def get_staging_preview(staged_id: str) -> Dict[str, str]:
    """Return preview files for a staged item by using the preview helper or reading files.

    This function raises FileNotFoundError if staged path does not exist.
    """
    staging_root = os.path.join("ExerciseDatabase", "_staging")
    staged_path = os.path.join(staging_root, staged_id)
    if not os.path.isdir(staged_path):
        raise FileNotFoundError(staged_id)
    # Try to use preview helper if present
    try:
        from ExerciseDatabase._tools.preview_system import create_exercise_preview
        # read payload.json and tex
        payload_path = os.path.join(staged_path, "payload.json")
        with open(payload_path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        tex_path = os.path.join(staged_path, f"{staged_id}.tex")
        with open(tex_path, "r", encoding="utf-8") as f:
            tex = f.read()
        metadata = payload.get("metadata", {})
        return create_exercise_preview(staged_id, tex, metadata)
    except Exception:
        # Fallback: return raw files
        files = {}
        for name in os.listdir(staged_path):
            p = os.path.join(staged_path, name)
            if os.path.isfile(p) and name.endswith((".tex", ".json")):
                with open(p, "r", encoding="utf-8") as f:
                    files[name] = f.read()
        return files


def confirm_staged(staged_id: str, action: str) -> Dict[str, Any]:
    """Confirm (promote or discard) a staged item.

    For now, only implement a safe discard (remove staged dir) and raise
    NotImplementedError for promote (needs repository promotion logic).
    """
    staging_root = os.path.join("ExerciseDatabase", "_staging")
    staged_path = os.path.join(staging_root, staged_id)
    if not os.path.isdir(staged_path):
        raise FileNotFoundError(staged_id)
    if action == "discard":
        # remove directory
        import shutil
        shutil.rmtree(staged_path)
        return {"action": "discarded"}
    elif action == "promote":
        # Basic promotion: move staged dir into ExerciseDatabase hierarchy and update index.json
        import shutil
        from datetime import datetime

        # Load payload
        payload_path = os.path.join(staged_path, "payload.json")
        if not os.path.isfile(payload_path):
            raise FileNotFoundError("payload.json missing in staged dir")
        with open(payload_path, "r", encoding="utf-8") as f:
            payload = json.load(f)

        # Required classification fields
        for key in ("discipline", "module", "concept", "tipo"):
            if key not in payload:
                raise ValueError(f"missing required field for promotion: {key}")

        dest_parent = os.path.join("ExerciseDatabase", payload["discipline"], payload["module"], payload["concept"], payload["tipo"])
        os.makedirs(dest_parent, exist_ok=True)
        dest_dir = os.path.join(dest_parent, staged_id)

        # Move staged directory to destination
        if os.path.exists(dest_dir):
            raise FileExistsError(dest_dir)
        shutil.move(staged_path, dest_dir)

        # Update or create index.json
        index_path = os.path.join("ExerciseDatabase", "index.json")
        if os.path.exists(index_path):
            try:
                with open(index_path, "r", encoding="utf-8") as f:
                    index = json.load(f)
            except Exception:
                index = {}
        else:
            index = {}

        index.setdefault("database_version", "1.0")
        index["last_updated"] = datetime.utcnow().isoformat() + "Z"
        exercises = index.setdefault("exercises", [])

        entry = {
            "id": staged_id,
            "path": os.path.relpath(dest_dir).replace("\\", "/"),
            "discipline": payload.get("discipline"),
            "module": payload.get("module"),
            "concept": payload.get("concept"),
            "tipo": payload.get("tipo"),
            "difficulty": payload.get("difficulty"),
            "tags": payload.get("tags", []),
            "status": "active"
        }
        exercises.append(entry)
        index["total_exercises"] = len(exercises)

        # write atomically
        tmp_index = index_path + ".tmp"
        with open(tmp_index, "w", encoding="utf-8") as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
        os.replace(tmp_index, index_path)

        return {"action": "promoted", "new_path": dest_dir}
    else:
        raise ValueError("unknown action")
