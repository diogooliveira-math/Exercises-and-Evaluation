"""Cleanup test exercises generated during the assistant session.
Removes MAT_P4FUNCOE_1GX_ARX_004 and MAT_P4FUNCOE_1GX_ARX_005 from index.json and their metadata,
backups original files and deletes generated .tex/.pdf preview files under temp/preview_*
"""
from pathlib import Path
import json
import shutil
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
IDS = ["MAT_P4FUNCOE_1GX_ARX_004", "MAT_P4FUNCOE_1GX_ARX_005"]
INDEX_PATH = ROOT / 'ExerciseDatabase' / 'index.json'
METADATA_PATH = ROOT / 'ExerciseDatabase' / 'matematica' / 'P4_funcoes' / '1-generalidades_funcoes' / 'afirmacoes_relacionais' / 'metadata.json'

stamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')

def backup(path: Path):
    if not path.exists():
        print(f'WARN: {path} not found, skipping backup')
        return None
    dest = path.with_suffix(path.suffix + f'.bak_{stamp}')
    shutil.copy2(path, dest)
    print(f'Backed up {path} -> {dest}')
    return dest

removed_count = 0

# Backup files
backup(INDEX_PATH)
backup(METADATA_PATH)

# Clean index.json
if INDEX_PATH.exists():
    data = json.loads(INDEX_PATH.read_text(encoding='utf-8'))
    exercises = data.get('exercises', [])
    before = len(exercises)
    new_exercises = [e for e in exercises if e.get('id') not in IDS]
    removed = before - len(new_exercises)
    if removed:
        data['exercises'] = new_exercises
        # update total_exercises if present
        if 'total_exercises' in data:
            try:
                data['total_exercises'] = max(0, int(data['total_exercises']) - removed)
            except Exception:
                pass
        INDEX_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f'Removed {removed} entries from {INDEX_PATH}')
        removed_count += removed
    else:
        print('No matching entries found in index.json')
else:
    print(f'ERROR: {INDEX_PATH} does not exist')

# Clean metadata.json
if METADATA_PATH.exists():
    meta = json.loads(METADATA_PATH.read_text(encoding='utf-8'))
    removed_meta = 0
    for id_ in IDS:
        if id_ in meta:
            del meta[id_]
            removed_meta += 1
    if removed_meta:
        METADATA_PATH.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f'Removed {removed_meta} keys from {METADATA_PATH}')
    else:
        print('No matching keys found in metadata.json')
else:
    print(f'WARN: metadata file {METADATA_PATH} not found')

# Remove .tex files under ExerciseDatabase path
for id_ in IDS:
    # try multiple likely locations
    paths = list(ROOT.glob(f'ExerciseDatabase/**/{id_}*.tex'))
    for p in paths:
        try:
            p.unlink()
            print(f'Deleted {p}')
        except Exception as e:
            print(f'Failed to delete {p}: {e}')

# Remove previews in temp/preview_* containing the ids
for preview_dir in ROOT.glob('temp/preview_*'):
    try:
        for p in preview_dir.glob('**/*'):
            if any(id_ in p.name for id_ in IDS):
                try:
                    p.unlink()
                    print(f'Deleted preview file {p}')
                except Exception as e:
                    print(f'Failed to delete preview file {p}: {e}')
        # remove empty directories
        try:
            for sub in preview_dir.glob('**'):
                pass
            # keep directory otherwise
        except Exception:
            pass
    except Exception as e:
        print(f'Error scanning preview dir {preview_dir}: {e}')

print('\nCleanup summary:')
print(f'  IDs targeted: {IDS}')
print(f'  Removed from index.json: {removed_count}')
print('  Review backups with .bak_<timestamp> files in the original locations')
