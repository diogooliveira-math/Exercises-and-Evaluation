#!/usr/bin/env python3
"""Promote a staged project from _staging to ExerciseDatabase/projects

Usage (importable functions):
    promote_project(staged_id, dry_run=True|False, force=False)

CLI usage:
    python promote_project_from_staging.py --staged-id=STG_... [--dry-run] [--force]
"""
from __future__ import annotations
import json
import shutil
import argparse
from pathlib import Path
import os
from datetime import datetime
import logging

from ExerciseDatabase._tools import index_utils

BASE_DIR = Path(__file__).parent.parent
STAGING_DIR = BASE_DIR / '_staging'
PROJECTS_DIR = BASE_DIR / 'projects'
INDEX_FILE = BASE_DIR / 'index.json'

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def validate_metadata(metadata: dict) -> bool:
    # Minimal validation: require titulo/responsavel/summary
    required = ['titulo', 'responsavel', 'summary']
    for k in required:
        if k not in metadata:
            return False
    return True


def promote_project(staged_id: str, dry_run: bool = True, force: bool = False) -> dict:
    # Accept either a staged id (basename) or a full path string to the staged folder
    staged_path_candidate = Path(staged_id)
    if staged_path_candidate.is_absolute() or str(staged_id).count(os.sep) > 0:
        staged_path = staged_path_candidate
    else:
        staged_path = STAGING_DIR / staged_id

    if not staged_path.exists():
        raise FileNotFoundError(f"Staged id/path not found: {staged_path}")

    # Read payload if present
    payload_file = staged_path / 'payload.json'
    if payload_file.exists():
        payload = json.loads(payload_file.read_text(encoding='utf-8'))
    else:
        payload = {}

    # Determine project id
    project_id = payload.get('id') or payload.get('titulo') or f"PROJ_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    # Sanitize project_id to a filesystem-friendly name
    project_id = str(project_id).replace(' ', '_')

    dest = PROJECTS_DIR / project_id

    if dry_run:
        logger.info('Dry-run: would move %s -> %s', staged_path, dest)
        return {'dry_run': True, 'staged_id': staged_id, 'would_move_to': str(dest)}

    # Create projects dir
    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)

    if dest.exists():
        if not force:
            raise FileExistsError(f"Destination project already exists: {dest}")
        else:
            shutil.rmtree(dest)

    # Move staged folder to projects
    shutil.move(str(staged_path), str(dest))

    # Update index
    project_metadata = payload.copy()
    # Ensure minimal fields
    if 'created_at' not in project_metadata:
        project_metadata['created_at'] = datetime.now().isoformat()
    if 'status' not in project_metadata:
        project_metadata['status'] = 'active'

    # Pass INDEX_FILE so tests can monkeypatch promote_module.INDEX_FILE
    index_utils.update_projects_index(project_metadata, str(dest), index_file=INDEX_FILE)

    logger.info('Promoted staged project %s to %s', staged_id, dest)
    return {'status': 'promoted', 'promoted': True, 'staged_id': staged_id, 'project_id': project_id, 'project_path': str(dest)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--staged-id', required=True)
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--force', action='store_true')
    args = parser.parse_args()

    res = promote_project(args.staged_id, dry_run=args.dry_run, force=args.force)
    print(json.dumps(res, ensure_ascii=False))


if __name__ == '__main__':
    main()
