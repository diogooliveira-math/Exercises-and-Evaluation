"""Create a compressed snapshot of the registry and metadata files."""
from pathlib import Path
import argparse
import shutil
import time

REPO_ROOT = Path(__file__).resolve().parent.parent
REG_DIR = REPO_ROOT / 'ExerciseDatabase' / '_registry'
META_GLOB = REPO_ROOT / 'ExerciseDatabase'
OUT_DIR = REPO_ROOT / 'temp' / 'registry_snapshots'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--out', type=str, default='')
    args = p.parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = time.strftime('%Y%m%d_%H%M%S')
    name = args.out or f'registry_snapshot_{ts}.zip'
    target = OUT_DIR / name
    # include registry dir and all _meta.json and exercise.json files
    to_zip = []
    if REG_DIR.exists():
        to_zip.append(str(REG_DIR))
    for f in META_GLOB.rglob('_meta.json'):
        to_zip.append(str(f))
    for f in META_GLOB.rglob('exercise.json'):
        to_zip.append(str(f))
    if not to_zip:
        print('Nothing to snapshot')
        return 2
    shutil.make_archive(str(target.with_suffix('')), 'zip', root_dir=REPO_ROOT, base_dir='ExerciseDatabase')
    print('Snapshot created:', target)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
