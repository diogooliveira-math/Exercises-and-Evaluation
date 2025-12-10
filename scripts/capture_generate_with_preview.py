import subprocess
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GEN = REPO / 'SebentasDatabase' / '_tools' / 'generate_tests.py'

env = os.environ.copy()
env['TEST_NO_COMPILE'] = '1'
env['TEST_NO_PREVIEW'] = '0'
env['TEST_AUTO_APPROVE'] = '0'
env['TEST_MODULE'] = 'A8_modelos_discretos'

cmd = [sys.executable, str(GEN), '--module', 'A8_modelos_discretos', '--no-compile']

print('Running:', ' '.join(cmd))

try:
    p = subprocess.run(cmd, cwd=str(REPO), env=env, capture_output=True, text=True, timeout=120)
    print('\n=== STDOUT ===')
    print(p.stdout)
    print('\n=== STDERR ===')
    print(p.stderr)
    sys.exit(p.returncode)
except subprocess.TimeoutExpired:
    print('Timed out after 120s')
    sys.exit(2)
except Exception as e:
    print('Error running generator:', e)
    sys.exit(3)
