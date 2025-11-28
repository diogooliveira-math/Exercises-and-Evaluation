import os
import json
import subprocess
import shutil
import sys
import time
import tempfile
from pathlib import Path
import pytest

ROOT = Path(__file__).parent
PROMPTS_FILE = ROOT / "opencode_exercise_prompts.json"
TIMEOUT = 120


def load_prompts():
    with PROMPTS_FILE.open(encoding='utf-8') as f:
        return json.load(f)


@pytest.mark.skipif(shutil.which('opencode') is None, reason="opencode CLI not found in PATH")
@pytest.mark.skipif(os.getenv('RUN_OPENCODE_AGENT_PROMPTS') is None, reason="RUN_OPENCODE_AGENT_PROMPTS not set")
def test_run_opencode_prompts():
    prompts = load_prompts()
    opencode_path = shutil.which('opencode')
    assert opencode_path, 'opencode must be in PATH to run this test'

    failures = []
    created_paths = []

    for p in prompts:
        statement = p['statement']
        marker = None
        # extract marker between [ and ] at start
        if statement.startswith('['):
            end = statement.find(']')
            if end != -1:
                marker = statement[1:end]

        cmd = [opencode_path, '--agent', 'exercise-creator', 'run', statement]
        try:
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=TIMEOUT, text=True)
        except subprocess.TimeoutExpired as e:
            failures.append((p['id'], 'timeout', ''))
            continue

        output = proc.stdout or ''
        ok = (proc.returncode == 0) or ('SUCCESS' in output)

        # Search for created files containing the marker in the repo (quick scan recent files)
        found_files = []
        for root, dirs, files in os.walk(Path.cwd()):
            # limit search to avoid scanning whole disk
            if 'venv' in root or '.git' in root or 'node_modules' in root:
                continue
            for fname in files:
                try:
                    fpath = Path(root) / fname
                    # only scan reasonably small text files
                    if fpath.stat().st_size > 200000:
                        continue
                    with fpath.open(encoding='utf-8', errors='ignore') as fh:
                        content = fh.read()
                        if marker and marker in content:
                            found_files.append(str(fpath))
                except Exception:
                    continue

        created_paths.extend(found_files)

        if not ok and not found_files:
            failures.append((p['id'], proc.returncode, output))

    # cleanup: remove files that contain any TEST_PROMPT marker
    for fpath in created_paths:
        try:
            os.remove(fpath)
        except Exception:
            pass

    if failures:
        # emit debug info
        for fail in failures:
            print("FAIL:", fail)
        pytest.fail(f"{len(failures)} prompts failed. See output above.")


if __name__ == '__main__':
    sys.exit(pytest.main([__file__]))
