import runpy
from pathlib import Path
import pytest
import os


def test_wrapper_forwards_flags_and_allows_no_filters(monkeypatch):
    # Ensure environment flags are set (no compile, no preview, auto-approve)
    monkeypatch.setenv('TEST_NO_COMPILE', '1')
    monkeypatch.setenv('TEST_NO_PREVIEW', '1')
    monkeypatch.setenv('TEST_AUTO_APPROVE', '1')
    # Ensure filters are not provided to test 'no-filters' behavior
    monkeypatch.delenv('TEST_MODULE', raising=False)
    monkeypatch.delenv('TEST_CONCEPT', raising=False)
    monkeypatch.delenv('TEST_DISCIPLINE', raising=False)

    called = {}

    def fake_run(cmd, cwd=None, env=None, **kwargs):
        # record call and simulate success
        called['cmd'] = cmd
        called['cwd'] = cwd
        called['env'] = env

        class Dummy:
            def __init__(self):
                self.returncode = 0
                self.stdout = ''
                self.stderr = ''

        return Dummy()

    # Patch subprocess.run used in the wrapper
    monkeypatch.setattr('subprocess.run', fake_run)

    script_path = Path(__file__).resolve().parent.parent / 'scripts' / 'run_generate_test_task.py'

    with pytest.raises(SystemExit) as se:
        runpy.run_path(str(script_path), run_name='__main__')

    # script should exit with code 0
    assert se.value.code == 0

    # Ensure the generator command was constructed and contains generate_tests.py
    assert 'generate_tests.py' in ' '.join(called['cmd'])

    # Ensure boolean flags were forwarded
    assert '--no-compile' in called['cmd']
    assert '--no-preview' in called['cmd']
    assert '--auto-approve' in called['cmd']
