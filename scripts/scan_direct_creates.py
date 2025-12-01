#!/usr/bin/env python3
"""Scan opencode send_prompt logs for direct-created exercises.
Exits 0 when none found; exits 1 if any direct creations are detected.
Prints a short report of findings.
"""
import json
import sys
from pathlib import Path

LOGS_DIR = Path(__file__).parent.parent / 'temp' / 'opencode_logs' / 'send_prompt'

if not LOGS_DIR.exists():
    print(f"Logs directory not found: {LOGS_DIR}")
    sys.exit(0)

sessions = list(LOGS_DIR.glob('session_*.json'))
direct_hits = []

for s in sessions:
    try:
        data = json.loads(s.read_text(encoding='utf-8'))
    except Exception as e:
        print(f"Failed to parse {s}: {e}")
        continue
    created = data.get('created')
    if created and created.get('method') == 'direct':
        direct_hits.append({
            'session': str(s),
            'method': 'created_direct',
            'stdout_path': created.get('stdout_path'),
            'attempt': created.get('attempt')
        })

# Also scan attempt directories for direct_stdout files
for attempt in LOGS_DIR.glob('attempt_*'):
    # direct_stdout.txt at top level of attempt dir
    ds = attempt / 'direct_stdout.txt'
    if ds.exists():
        txt = ds.read_text(encoding='utf-8').strip()
        if txt:
            direct_hits.append({
                'attempt_dir': str(attempt),
                'direct_stdout': txt.splitlines()[0] if txt else ''
            })
    # runs under attempt
    for run in attempt.glob('run_*'):
        rmeta = run / 'meta.json'
        if rmeta.exists():
            try:
                rm = json.loads(rmeta.read_text(encoding='utf-8'))
                desc = rm.get('description','')
                if 'direct add_exercise_simple' in desc.lower() or 'direct' in desc.lower():
                    stdout_path = None
                    paths = rm.get('paths',{})
                    stdout_path = paths.get('stdout') if isinstance(paths, dict) else None
                    direct_hits.append({
                        'run_meta': str(rmeta),
                        'description': desc,
                        'stdout_path': stdout_path
                    })
            except Exception:
                pass
        stdf = run / 'stdout.txt'
        if stdf.exists():
            txt = stdf.read_text(encoding='utf-8').strip()
            if txt.startswith('SUCCESS:'):
                direct_hits.append({
                    'run_stdout': str(stdf),
                    'first_line': txt.splitlines()[0]
                })

# Deduplicate by stringified dict keys
seen = set()
unique_hits = []
for h in direct_hits:
    key = json.dumps(h, sort_keys=True)
    if key in seen:
        continue
    seen.add(key)
    unique_hits.append(h)

if not unique_hits:
    print('No direct-create runs found in opencode send_prompt logs.')
    sys.exit(0)

print('Direct-create runs found:')
for h in unique_hits:
    for k,v in h.items():
        print(f" - {k}: {v}")
    print('')

print(f"Total direct-create events: {len(unique_hits)}")
# exit non-zero so CI can catch it
sys.exit(1)
