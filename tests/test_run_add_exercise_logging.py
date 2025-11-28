import subprocess
from pathlib import Path

def test_run_add_exercise_creates_log(tmp_path):
    import sys
    cmd = [
        sys.executable,
        'scripts/run_add_exercise.py',
        "discipline=matematica, module=P4_funcoes, concept=1-generalidades_funcoes, tipo=test_logging, difficulty=2, statement='Teste logging'"
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0

    # Check logs directory
    logs_dir = Path('ExerciseDatabase') / 'logs'
    assert logs_dir.exists()
    # Find most recent log
    logs = sorted(logs_dir.glob('run_add_exercise_*.log'))
    assert logs, "No run_add_exercise log found"
    latest = logs[-1]
    content = latest.read_text(encoding='utf-8')
    assert 'COMMAND:' in content
    assert 'RETURNCODE:' in content
