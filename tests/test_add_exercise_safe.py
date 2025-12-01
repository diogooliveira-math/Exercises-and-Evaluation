import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
SAFE = ROOT / 'ExerciseDatabase' / '_tools' / 'add_exercise_safe.py'


def test_stage_payload_file(tmp_path):
    payload = {
        'mode': 'stage',
        'discipline': 'matematica',
        'module': 'P4_funcoes',
        'concept': '1-intervalo_real',
        'tipo': 'pertinencia_intervalo',
        'difficulty': 1,
        'statement': 'Teste unitário: pertence ao intervalo?'
    }
    p = tmp_path / 'payload.json'
    p.write_text(json.dumps(payload, ensure_ascii=False), encoding='utf-8')

    proc = subprocess.run([sys.executable, str(SAFE), f'--payload-file={p}'], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    out = proc.stdout.strip()
    assert out
    res = json.loads(out.splitlines()[-1])
    assert res.get('status') == 'staged'
    staged_path = Path(res.get('staged_path'))
    assert staged_path.exists()
    assert (staged_path / 'payload.json').exists()


def test_stage_via_positional(tmp_path):
    proc = subprocess.run([sys.executable, str(SAFE), 'matematica', 'P4_funcoes', '1-intervalo_real', 'pertinencia_intervalo', '1', 'Positional staging test'], capture_output=True, text=True)
    assert proc.returncode == 0
    res = json.loads(proc.stdout.strip().splitlines()[-1])
    assert res.get('status') == 'staged'
    staged_path = Path(res.get('staged_path'))
    assert staged_path.exists()
    assert (staged_path / f"{res.get('staged_id')}.tex").exists()
