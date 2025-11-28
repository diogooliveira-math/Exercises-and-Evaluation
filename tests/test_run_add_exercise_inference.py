import subprocess
from pathlib import Path
import json


def test_run_add_exercise_infers_missing_fields_from_statement():
    # Provide minimal args with statement containing hints
    statement = "Quero que cries um exercício no módulo P4_funcoes na generalidades de funcoes onde os alunos analisem afirmacoes tipo 'quando o preço aumenta a despesa vai aumentar'"
    import sys
    cmd = [
        sys.executable,
        'scripts/run_add_exercise.py',
        f"statement={statement}"
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    # Should not fail with missing keys after inference
    assert proc.returncode == 0, f"Wrapper failed: stdout={proc.stdout} stderr={proc.stderr}"
    combined = (proc.stdout or '') + '\n' + (proc.stderr or '')
    assert 'SUCCESS:' in combined
    # Cleanup: remove last created entry
    # Extract id
    exercise_id = combined.split('SUCCESS:')[-1].strip().split()[0]
    base = Path('ExerciseDatabase')
    # The generator may choose a tipo folder. Search for the created tex file under ExerciseDatabase
    tex_path = None
    metadata_path = None
    for p in base.rglob(f"{exercise_id}.tex"):
        tex_path = p
        metadata_path = p.parent / 'metadata.json'
        break
    assert tex_path is not None and tex_path.exists(), f"Expected created tex file for {exercise_id} not found"
    assert metadata_path is not None and metadata_path.exists()

    # Remove created files and index entry
    metadata = json.loads(metadata_path.read_text(encoding='utf-8'))
    metadata['exercicios'].pop(exercise_id, None)
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding='utf-8')
    if tex_path.exists():
        tex_path.unlink()
    with open(base / 'index.json', 'r', encoding='utf-8') as f:
        index = json.load(f)
    index['exercises'] = [e for e in index.get('exercises', []) if e.get('id') != exercise_id]
    with open(base / 'index.json', 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
