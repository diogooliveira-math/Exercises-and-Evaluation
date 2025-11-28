import subprocess, shutil, sys, os
PROMPT='[TEST_DIAG_PROMPT_01] Cria um exercício simples sobre função inversa: "Dada f(x)=2x+3 determine f^{-1} e justifique"'
opencode=shutil.which('opencode')
log='temp/opencode_diag_PROMPT_01.log'
if not opencode:
    print('opencode not found')
    sys.exit(2)
cmd=[opencode,'--agent','exercise-creator','run',PROMPT]
print('Running:', ' '.join(cmd))
try:
    proc=subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120, text=True, encoding='utf-8', errors='replace')
    out=proc.stdout or ''
    os.makedirs(os.path.dirname(log), exist_ok=True)
    with open(log,'w',encoding='utf-8') as f:
        f.write(out)
    print('Returncode',proc.returncode)
    print('Wrote log to',log)
except subprocess.TimeoutExpired as e:
    os.makedirs(os.path.dirname(log), exist_ok=True)
    with open(log,'w',encoding='utf-8') as f:
        f.write('TIMEOUT')
    print('Timeout; wrote log to',log)
except FileNotFoundError:
    print('opencode not found during run')
    sys.exit(2)
