#!/usr/bin/env python3
"""
Safe wrapper for staging exercises.
Supports: --payload-file=PATH or --stdin with JSON containing required keys and 'mode': 'stage'
Creates a directory under ExerciseDatabase/_staging/<STG_...> with payload.json and returns a JSON status.
"""
from __future__ import annotations
import sys
import json
from pathlib import Path
from datetime import datetime
import logging
import secrets

BASE_DIR = Path(__file__).parent.parent
STAGING_DIR = BASE_DIR / '_staging'
STAGING_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

REQUIRED = ["discipline", "module", "concept", "tipo", "difficulty", "statement"]


def load_payload_from_file(path: Path) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_payload_from_stdin() -> dict:
    raw = sys.stdin.read()
    return json.loads(raw)


def make_staged(payload: dict) -> dict:
    # Basic validation
    for k in REQUIRED:
        if k not in payload:
            raise ValueError(f"missing required key: {k}")

    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    rand = secrets.token_hex(3).upper()
    staged_id = f"STG_{ts}_{rand}"
    staged_path = STAGING_DIR / staged_id
    staged_path.mkdir(parents=True, exist_ok=False)

    # Save payload
    payload_file = staged_path / 'payload.json'
    with open(payload_file, 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    # Also save a small tex preview file for quick inspection
    stmt = payload.get('statement', '')
    tex_file = staged_path / f"{staged_id}.tex"
    try:
        with open(tex_file, 'w', encoding='utf-8') as f:
            f.write(f"% Staged exercise {staged_id}\n")
            f.write(f"% Discipline: {payload.get('discipline')}\n")
            f.write(f"% Module: {payload.get('module')}\n")
            f.write(f"% Concept: {payload.get('concept')}\n")
            f.write(f"% Tipo: {payload.get('tipo')}\n\n")
            f.write(stmt)
    except Exception:
        logger.exception('Failed to write tex preview')

    # Write a simple metadata file
    meta = {
        'status': 'staged',
        'staged_id': staged_id,
        'staged_path': str(staged_path.resolve()),
        'created': datetime.now().isoformat()
    }
    with open(staged_path / 'metadata.json', 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    logger.info('Staged exercise %s at %s', staged_id, staged_path)
    return meta


def main():
    try:
        payload = None
        # Support --payload-file=path
        if len(sys.argv) == 2 and sys.argv[1].startswith('--payload-file='):
            p = Path(sys.argv[1].split('=', 1)[1])
            payload = load_payload_from_file(p)
        elif len(sys.argv) == 2 and sys.argv[1] == '--stdin':
            payload = load_payload_from_stdin()
        else:
            # Also accept positional form for convenience
            # python add_exercise_safe.py discipline module concept tipo difficulty statement
            if len(sys.argv) >= 7:
                payload = {
                    'discipline': sys.argv[1],
                    'module': sys.argv[2],
                    'concept': sys.argv[3],
                    'tipo': sys.argv[4],
                    'difficulty': sys.argv[5],
                    'statement': sys.argv[6]
                }

        if payload is None:
            print(json.dumps({'status': 'error', 'message': 'No payload provided. Use --payload-file= or --stdin or positional args.'}, ensure_ascii=False))
            return 2

        mode = payload.get('mode') or ''
        # allow CLI caller to pass explicit mode via arg --mode=stage as a second arg
        for a in sys.argv[1:]:
            if a.startswith('--mode='):
                mode = a.split('=',1)[1]

        if not mode:
            # default to stage to be safe
            mode = 'stage'

        if mode != 'stage':
            print(json.dumps({'status': 'error', 'message': 'Only mode=stage is supported by this safe wrapper'}, ensure_ascii=False))
            return 3

        meta = make_staged(payload)
        # print JSON status as last line for callers to parse
        print(json.dumps(meta, ensure_ascii=False))
        return 0

    except Exception as e:
        logger.exception('Error in add_exercise_safe')
        print(json.dumps({'status': 'error', 'message': str(e)}, ensure_ascii=False))
        return 4


if __name__ == '__main__':
    sys.exit(main())
