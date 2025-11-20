#!/usr/bin/env python3
"""
Safe index.json patcher for P1 exercises added by the agent.

Usage:
  python ExerciseDatabase/_tools/agent_index_updates/apply_index_patch.py

What it does:
 - Reads ExerciseDatabase/index.json
 - Backs it up to ExerciseDatabase/index.json.agent_backup.TIMESTAMP.json
 - Appends new exercise entries from P1_index_additions.json to the "exercises" array
   if they do not already exist (by id).
 - Writes the updated index.json.

Note: run this in the repository root. A Python 3.8+ environment is expected.
"""
import json
import shutil
import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
INDEX = ROOT / "ExerciseDatabase" / "index.json"
PATCH = ROOT / "ExerciseDatabase" / "_tools" / "agent_index_updates" / "P1_index_additions.json"

def main():
    if not INDEX.exists():
        print(f"Index file not found: {INDEX}")
        return
    with open(PATCH, "r", encoding="utf-8") as f:
        patch = json.load(f)
    with open(INDEX, "r", encoding="utf-8") as f:
        index = json.load(f)

    # Backup
    ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    backup_path = INDEX.with_name(f"index.json.agent_backup.{ts}.json")
    shutil.copy2(INDEX, backup_path)
    print(f"Backup created: {backup_path}")

    existing = {e.get("id") for e in index.get("exercises", []) if isinstance(e, dict)}
    additions = patch.get("exercises", [])
    new_count = 0
    for e in additions:
        if e.get("id") not in existing:
            index.setdefault("exercises", []).append(e)
            new_count += 1
    with open(INDEX, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    print(f"Applied patch: {new_count} new exercises added to {INDEX}")

if __name__ == "__main__":
    main()