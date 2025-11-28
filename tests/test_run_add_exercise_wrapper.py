import json
import os
import subprocess
import sys
from pathlib import Path

def test_run_add_exercise_wrapper_creates_exercise(tmp_path, monkeypatch):
    # Prepare a unique tipo to avoid collisions
    tipo = 'test_wrapper_integration'
    statement = "Teste integração wrapper: classifique afirmações."
    cmd = [
        sys.executable,
        'scripts/run_add_exercise.py',
        f"discipline=matematica, module=P4_funcoes, concept=1-generalidades_funcoes, tipo={tipo}, difficulty=2, statement='{statement}'"
    ]

    # Run the wrapper
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0, f"Wrapper failed: stdout={proc.stdout} stderr={proc.stderr}"

    # Extract ID from stdout or stderr (wrapper logs to stderr)
    combined_out = (proc.stdout or '') + '\n' + (proc.stderr or '')
    if 'SUCCESS:' in combined_out:
        exercise_id = combined_out.split('SUCCESS:')[-1].strip().split()[0]
    else:
        raise AssertionError(f"SUCCESS not found in output. stdout={proc.stdout!r} stderr={proc.stderr!r}")

    # Check files created
    base = Path('ExerciseDatabase')
    tex_path = base / 'matematica' / 'P4_funcoes' / '1-generalidades_funcoes' / tipo / f"{exercise_id}.tex"
    metadata_path = base / 'matematica' / 'P4_funcoes' / '1-generalidades_funcoes' / tipo / 'metadata.json'
    assert tex_path.exists(), f".tex not found at {tex_path}"
    assert metadata_path.exists(), f"metadata.json not found at {metadata_path}"

    # Check index.json contains the entry
    with open(base / 'index.json', 'r', encoding='utf-8') as f:
        index = json.load(f)
    ids = [e['id'] for e in index.get('exercises', [])]
    assert exercise_id in ids

    # Cleanup: remove created files to keep repo state clean for tests
    metadata = json.loads(metadata_path.read_text(encoding='utf-8'))
    metadata['exercicios'].pop(exercise_id, None)
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding='utf-8')
    if tex_path.exists():
        tex_path.unlink()
    # Remove from index.json
    index['exercises'] = [e for e in index.get('exercises', []) if e.get('id') != exercise_id]
    with open(base / 'index.json', 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
