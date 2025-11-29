"""Registry repair and rebuild utilities.

Modes:
 - --rebuild: rebuild registry from filesystem (deterministic traversal)
 - --from-exercise-json: rebuild registry using existing exercise.json files (preferred)
 - --backup: backup existing registry before writing
"""
from pathlib import Path
import argparse
import json
import time
import shutil

REPO_ROOT = Path(__file__).resolve().parent.parent
REG_PATH = REPO_ROOT / 'ExerciseDatabase' / '_registry' / 'ip_registry.json'
EX_DB = REPO_ROOT / 'ExerciseDatabase'

from ExerciseDatabase._tools.ip_registry import IPRegistry


def scan_fs_and_register(base: Path, registry: IPRegistry):
    # deterministic traversal
    count = 0
    for disc in sorted([d for d in base.iterdir() if d.is_dir() and not d.name.startswith('_')]):
        for mod in sorted([d for d in disc.iterdir() if d.is_dir() and not d.name.startswith('_')]):
            for conc in sorted([d for d in mod.iterdir() if d.is_dir() and not d.name.startswith('_')]):
                for typ in sorted([d for d in conc.iterdir() if d.is_dir() and not d.name.startswith('_')]):
                    for ex in sorted([d for d in typ.iterdir() if d.is_dir() and not d.name.startswith('_')]):
                        parts = [disc.name, mod.name, conc.name, typ.name, ex.name]
                        rel = str(ex.relative_to(base))
                        registry.register_path(parts, rel, label=ex.name)
                        count += 1
    return count


def rebuild_from_exercise_json(base: Path, registry: IPRegistry):
    count = 0
    for exjson in base.rglob('exercise.json'):
        try:
            with open(exjson, 'r', encoding='utf8') as f:
                meta = json.load(f)
            ip = meta.get('ip')
            path_str = meta.get('path')
            if ip and path_str:
                parts = meta.get('path').split('\\') if '\\' in meta.get('path') else meta.get('path').split('/')
                # last 5 parts may be full path
                parts = parts[-5:]
                registry.register_path(parts, path_str, label=meta.get('label'))
                count += 1
        except Exception:
            pass
    return count


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--rebuild', action='store_true')
    p.add_argument('--from-exercise-json', action='store_true')
    p.add_argument('--backup', action='store_true')
    args = p.parse_args()

    if not EX_DB.exists():
        print('ExerciseDatabase not found')
        return 2

    if args.backup and REG_PATH.exists():
        bak = REG_PATH.with_name(REG_PATH.name + f'.bak_{int(time.time())}')
        shutil.copy2(REG_PATH, bak)
        print('Backup created:', bak)

    registry = IPRegistry(path=REG_PATH)
    # clear current registry
    registry._data = None

    if args.from_exercise_json:
        n = rebuild_from_exercise_json(EX_DB, registry)
        registry.save()
        print('Rebuilt registry from exercise.json files, entries:', n)
        return 0

    if args.rebuild:
        n = scan_fs_and_register(EX_DB, registry)
        registry.save()
        print('Rebuilt registry from filesystem, entries:', n)
        return 0

    print('Specify --rebuild or --from-exercise-json')
    return 1

if __name__ == '__main__':
    raise SystemExit(main())
