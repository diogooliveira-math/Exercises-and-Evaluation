import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
GEN = ROOT / 'ExerciseDatabase' / '_tools' / 'generate_intervalo_pertinencia.py'


def test_generate_small_batch(tmp_path):
    # Run generator with count=3 to stage 3 exercises
    proc = subprocess.run([sys.executable, str(GEN), '--count', '3'], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    out = proc.stdout.strip()
    # ensure output mentions 'Staged:' lines
    assert 'Staged:' in out
    # verify report file created
    temp_dir = ROOT / 'ExerciseDatabase' / 'temp' / 'intervalo_generated'
    assert temp_dir.exists()
    # find latest report
    reports = list(temp_dir.glob('intervalo_report_*.json'))
    assert reports
    latest = sorted(reports)[-1]
    data = json.loads(latest.read_text(encoding='utf-8'))
    assert data['count'] == len(data['generated'])
    assert len(data['generated']) >= 1
