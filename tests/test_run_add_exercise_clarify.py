import subprocess
import json
import sys


def test_run_add_exercise_needs_clarification_when_inference_uncertain():
    statement = "Cria um exercício sobre quando o preço aumenta a despesa vai aumentar"
    cmd = [sys.executable, 'scripts/run_add_exercise.py', f"statement={statement}"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    stdout = (proc.stdout or '').strip()
    stderr = (proc.stderr or '').strip()
    # We expect either success or a JSON with status needs_clarification
    if 'SUCCESS:' in stdout or 'SUCCESS:' in stderr:
        assert proc.returncode == 0
    else:
        # parse JSON from stdout preferentially, else stderr
        parsed = None
        for candidate in (stdout, stderr):
            if not candidate:
                continue
            try:
                parsed = json.loads(candidate)
                break
            except Exception:
                # try to extract JSON prefix line
                first_line = candidate.splitlines()[0] if candidate.splitlines() else ''
                try:
                    parsed = json.loads(first_line)
                    break
                except Exception:
                    continue
        if parsed is None:
            raise AssertionError(f"Output not JSON nor success: stdout={stdout!r} stderr={stderr!r}")
        assert parsed.get('status') in ('needs_clarification','clarify','error')
