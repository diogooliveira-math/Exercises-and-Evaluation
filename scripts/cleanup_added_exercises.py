#!/usr/bin/env python3
"""
Cleanup helper to remove exercises created during interactive tests.

Usage:
  python scripts\cleanup_added_exercises.py MAT_P4FUNCOE_1GX_ACX_001 MAT_P4FUNCOE_1GX_ACX_002

If no IDs are provided the script will attempt to remove the two defaults
created in the earlier test run.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def remove_exercise_by_id(base: Path, ex_id: str) -> None:
    # Find tex file under base recursively
    files = list(base.rglob(f"{ex_id}*.tex"))
    for f in files:
        try:
            f.unlink()
            print(f"Removed file: {f}")
        except Exception as e:
            print(f"Failed to remove {f}: {e}")

    # Remove from any metadata.json that lists it
    for md in base.rglob("metadata.json"):
        try:
            data = json.loads(md.read_text(encoding="utf-8"))
        except Exception:
            continue
        changed = False
        if isinstance(data, dict) and "exercicios" in data and ex_id in data["exercicios"]:
            del data["exercicios"][ex_id]
            md.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"Removed {ex_id} from {md}")
            changed = True

    # Remove from global index
    index_file = base / "index.json"
    if index_file.exists():
        idx = json.loads(index_file.read_text(encoding="utf-8"))
        exercises = idx.get("exercises", [])
        new_ex = [e for e in exercises if e.get("id") != ex_id]
        if len(new_ex) != len(exercises):
            idx["exercises"] = new_ex
            index_file.write_text(json.dumps(idx, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"Removed {ex_id} from index.json")


def main():
    base = Path(__file__).resolve().parents[1] / "ExerciseDatabase"
    ids = sys.argv[1:]
    if not ids:
        ids = ["MAT_P4FUNCOE_1GX_ACX_001", "MAT_P4FUNCOE_1GX_ACX_002"]

    for ex_id in ids:
        remove_exercise_by_id(base, ex_id)


if __name__ == "__main__":
    main()
