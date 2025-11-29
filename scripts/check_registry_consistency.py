"""Check consistency between ip_registry.json and on-disk ExerciseDatabase."""
from pathlib import Path
import json
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
REG_PATH = REPO_ROOT / 'ExerciseDatabase' / '_registry' / 'ip_registry.json'
EX_DB = REPO_ROOT / 'ExerciseDatabase'


def load_registry(path: Path):
    if not path.exists():
        print('Registry not found:', path)
        sys.exit(2)
    with open(path, 'r', encoding='utf8') as f:
        return json.load(f)


def main():
    reg = load_registry(REG_PATH)
    ips = reg.get('ips', {})
    errors = []
    # Check that each ip path exists
    for ip, meta in ips.items():
        p = Path(meta.get('path', ''))
        if not p:
            errors.append((ip, 'missing path'))
            continue
        if not p.is_absolute():
            p = EX_DB / p
        if not p.exists():
            errors.append((ip, f'path not found: {p}'))
    # Check for duplicate paths mapping to multiple ips
    path_map = {}
    for ip, meta in ips.items():
        path_map.setdefault(meta.get('path',''), []).append(ip)
    for path, lst in path_map.items():
        if len(lst) > 1:
            errors.append(('duplicate_path', path, lst))
    # Check next_counters sanity
    nc = reg.get('next_counters', {})
    for k,v in nc.items():
        if not isinstance(v, int) or v < 1:
            errors.append(('bad_counter', k, v))

    if errors:
        print('Consistency check FAILED:')
        for e in errors:
            print(' ', e)
        sys.exit(1)
    else:
        print('Consistency check OK')
        sys.exit(0)

if __name__ == '__main__':
    main()
