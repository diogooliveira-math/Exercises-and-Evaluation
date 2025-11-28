import json, shutil, subprocess, os, sys, time
from pathlib import Path
ROOT=Path.cwd()
PROMPTS_FILE=ROOT/'tests'/'opencode_exercise_prompts.json'
with PROMPTS_FILE.open('r',encoding='utf-8') as f:
    prompts=json.load(f)
for p in prompts[:3]:
    pid=p['id']
    stmt=p['statement']
    opencode=shutil.which('opencode')
    log=ROOT/'temp'/f'opencode_quick_{pid}.log'
    os.makedirs(log.parent,exist_ok=True)
    if not opencode:
        print(pid,'opencode not found')
        continue
    cmd=[opencode,'--agent','exercise-creator','run',stmt]
    print('RUN',pid)
    try:
        proc=subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30, text=True, encoding='utf-8', errors='replace')
        out=proc.stdout or ''
    except subprocess.TimeoutExpired:
        out='TIMEOUT'
    with open(log,'w',encoding='utf-8') as f:
        f.write(out)
    print(pid,'return', 'TIMEOUT' if out=='TIMEOUT' else 'OK')
