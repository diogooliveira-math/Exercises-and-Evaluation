import subprocess, traceback, sys, time, os, json

PROMPT = '''Quero que cries um exercício no módulo P4_funcoes na generalidades de funcoes (procurar nomenclatura) e adiciones um novo tipo de exercício (escolhe tu a nomenclatura do tipo de exercício!), onde os alunos afirma coisas tipo "quando o preço aumenta a despesa vai aumentar" para responder às questões..'''

base_dir = os.path.join(os.getcwd(), 'ExerciseDatabase', 'matematica', 'P4_funcoes')
now = time.time()
cutoff = now - 600  # 10 minutes

print('Running opencode CLI via subprocess...')
try:
    proc = subprocess.run(['opencode', '--agent', 'exercise-creator', 'run', PROMPT], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace', timeout=120)
    print('OPENCODE_EXIT_CODE:', proc.returncode)
    print('OPENCODE_OUTPUT:\n' + (proc.stdout or ''))
except FileNotFoundError as e:
    print('OPENCODE_EXECUTABLE_NOT_FOUND: opencode not in PATH or not installed')
    traceback.print_exc()
except subprocess.TimeoutExpired as e:
    print('OPENCODE_TIMEOUT')
    print(e)
except Exception:
    print('OPENCODE_EXCEPTION')
    traceback.print_exc()

# Find recently modified files under the target module
candidates = []
if os.path.isdir(base_dir):
    for root, dirs, files in os.walk(base_dir):
        for f in files:
            path = os.path.join(root, f)
            try:
                if os.path.getmtime(path) >= cutoff:
                    candidates.append(path)
            except Exception:
                pass

print('CANDIDATES_JSON:' + json.dumps(candidates))

# Attempt to remove candidates
removed = []
failed = []
for p in candidates:
    try:
        os.remove(p)
        removed.append(p)
        print('REMOVED:' + p)
    except Exception as e:
        failed.append((p, str(e)))
        print('FAILED_REMOVE:' + p + ' -> ' + str(e))

print('SUMMARY: candidates=%d removed=%d failed=%d' % (len(candidates), len(removed), len(failed)))

# Exit with non-zero if opencode ran and returned non-zero, or if removal failures
if 'proc' in globals():
    if proc.returncode != 0:
        sys.exit(1)
if failed:
    sys.exit(2)

sys.exit(0)
