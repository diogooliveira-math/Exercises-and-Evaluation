import json
import subprocess
from pathlib import Path

def test_add_exercise_payload_file_creates_exercise(tmp_path):
    base = Path('ExerciseDatabase')
    payload = {
        "discipline": "matematica",
        "module": "P4_funcoes",
        "concept": "1-generalidades_funcoes",
        "tipo": "test_payload_file",
        "difficulty": 2,
        "statement": "Teste payload file: classifique as afirmações."
    }
    payload_file = tmp_path / 'payload.json'
    payload_file.write_text(json.dumps(payload, ensure_ascii=False), encoding='utf-8')

    import sys
    cmd = [sys.executable, 'ExerciseDatabase/_tools/add_exercise_simple.py', f'--payload-file={payload_file}']
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0, f"Failed: stdout={proc.stdout} stderr={proc.stderr}"
    assert 'SUCCESS:' in (proc.stdout + proc.stderr)

    # Cleanup: remove created files and index entry
    # Extract exercise id
    out = (proc.stdout + proc.stderr)
    exercise_id = out.split('SUCCESS:')[-1].strip().split()[0]
    tipo_dir = base / 'matematica' / 'P4_funcoes' / '1-generalidades_funcoes' / 'test_payload_file'
    tex_path = tipo_dir / f"{exercise_id}.tex"
    metadata_path = tipo_dir / 'metadata.json'
    assert tex_path.exists()
    assert metadata_path.exists()

    # Remove created files
    metadata = json.loads(metadata_path.read_text(encoding='utf-8'))
    metadata['exercicios'].pop(exercise_id, None)
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding='utf-8')
    if tex_path.exists():
        tex_path.unlink()
    # Remove from index
    with open(base / 'index.json', 'r', encoding='utf-8') as f:
        index = json.load(f)
    index['exercises'] = [e for e in index.get('exercises', []) if e.get('id') != exercise_id]
    with open(base / 'index.json', 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
