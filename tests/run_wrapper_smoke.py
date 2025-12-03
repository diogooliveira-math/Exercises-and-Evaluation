"""Lightweight smoke runner for `scripts/run_generate_test_task.py`.

This script can be executed with `python tests/run_wrapper_smoke.py` and does not
depend on pytest or repository test fixtures. It monkeypatches `subprocess.run`
to avoid executing the real generator and validates that the wrapper constructs
the expected command and forwards boolean flags.
"""
import runpy
import os
import subprocess
from pathlib import Path


def main():
    os.environ.pop('TEST_MODULE', None)
    os.environ.pop('TEST_CONCEPT', None)
    os.environ.pop('TEST_DISCIPLINE', None)

    os.environ['TEST_NO_COMPILE'] = '1'
    os.environ['TEST_NO_PREVIEW'] = '1'
    os.environ['TEST_AUTO_APPROVE'] = '1'

    recorded = {}

    def fake_run(cmd, cwd=None, env=None, **kwargs):
        recorded['cmd'] = cmd
        recorded['cwd'] = cwd
        recorded['env'] = env

        class R:
            def __init__(self):
                self.returncode = 0
                self.stdout = ''
                self.stderr = ''

        return R()

    subprocess_run_orig = subprocess.run
    subprocess.run = fake_run

    try:
        script = Path(__file__).resolve().parent.parent / 'scripts' / 'run_generate_test_task.py'
        try:
            runpy.run_path(str(script), run_name='__main__')
        except SystemExit as se:
            if se.code != 0:
                raise RuntimeError(f"Wrapper exited with code {se.code}")

        cmd = recorded.get('cmd')
        if not cmd:
            raise RuntimeError('subprocess.run was not called')

        cmd_join = ' '.join(cmd)
        if 'generate_tests.py' not in cmd_join:
            raise RuntimeError(f'generate_tests.py not found in command: {cmd_join}')
        if '--no-compile' not in cmd:
            raise RuntimeError('--no-compile flag not forwarded')
        if '--no-preview' not in cmd:
            raise RuntimeError('--no-preview flag not forwarded')
        if '--auto-approve' not in cmd:
            raise RuntimeError('--auto-approve flag not forwarded')

        print('Smoke runner: OK — wrapper forwarded flags and allowed no filters')

    finally:
        subprocess.run = subprocess_run_orig


if __name__ == '__main__':
    main()
