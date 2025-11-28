import json, subprocess, shutil, os, sys, time, glob
from pathlib import Path

ROOT = Path.cwd()
PROMPTS_FILE = ROOT / 'tests' / 'opencode_exercise_prompts.json'

# Load prompts
with PROMPTS_FILE.open('r', encoding='utf-8') as f:
    prompts = json.load(f)

prompts = prompts[:3]

opencode_bin = shutil.which('opencode')
if not opencode_bin:
    print('OPENCODE_NOT_FOUND')
    sys.exit(2)

logs_dir = ROOT / 'temp' / 'opencode_quick_logs'
logs_dir.mkdir(parents=True, exist_ok=True)

base_dir = ROOT / 'ExerciseDatabase' / 'matematica' / 'P4_funcoes'

results = []

for p in prompts:
    pid = p.get('id')
    stmt = p.get('statement')
    marker = None
    if stmt.startswith('['):
        end = stmt.find(']')
        if end != -1:
            marker = stmt[1:end]

    log_path = logs_dir / f"{pid}.log"
    cmd = [opencode_bin, '--agent', 'exercise-creator', 'run', stmt]
    print(f'RUNNING {pid} -> {" ".join(cmd[:4])} ... (log -> {log_path})')
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=60, text=True, encoding='utf-8', errors='replace')
        out = proc.stdout or ''
    except subprocess.TimeoutExpired as e:
        open(log_path, 'w', encoding='utf-8').write('TIMEOUT')
        results.append((pid, 'timeout', [] , str(log_path)))
        print(f'{pid} TIMEOUT')
        continue
    except FileNotFoundError:
        open(log_path, 'w', encoding='utf-8').write('OPENCODE_NOT_FOUND_ERROR')
        results.append((pid, 'notfound', [], str(log_path)))
        print(f'{pid} OPENCODE NOT FOUND DURING RUN')
        continue
    # write log
    try:
        open(log_path, 'w', encoding='utf-8').write(out)
    except Exception:
        open(log_path, 'w', encoding='utf-8', errors='ignore').write(out)

    # search for created files containing marker
    found = []
    if marker and base_dir.exists():
        for path in base_dir.rglob('*.tex'):
            try:
                txt = path.read_text(encoding='utf-8', errors='ignore')
                if marker in txt:
                    found.append(str(path))
            except Exception:
                continue
        # metadata.json
        for path in base_dir.rglob('metadata.json'):
            try:
                txt = path.read_text(encoding='utf-8', errors='ignore')
                if marker in txt:
                    found.append(str(path))
            except Exception:
                continue

    # cleanup found
    removed = []
    for f in found:
        try:
            os.remove(f)
            removed.append(f)
        except Exception:
            pass

    results.append((pid, proc.returncode, found, str(log_path)))
    print(f'{pid} returncode={proc.returncode} found={len(found)} removed={len(removed)}')

# summary
print('\nSUMMARY:')
all_ok = True
for r in results:
    pid, code, found, log = r
    status = 'OK' if (code == 0 or found) else 'FAIL'
    if status == 'FAIL':
        all_ok = False
    print(f' - {pid}: status={status} returncode={code} found={len(found)} log={log}')

sys.exit(0 if all_ok else 1)
