#!/usr/bin/env python3
"""
Gera múltiplos exercícios simples sobre pertinência a intervalos reais.
Usa a função create_simple_exercise de `add_exercise_simple.py` para inserir diretamente
exercícios em `ExerciseDatabase/matematica/P4_funcoes/1-intervalo_real/pertinencia_intervalo`.

Uso:
  python generate_intervalo_pertinencia.py --count 10

O script gera variações com diferentes tipos de intervalos e valores (inclui candidatos na fronteira,
fora e no interior), escreve um pequeno relatório e imprime os IDs criados.
"""

import argparse
from datetime import datetime
from pathlib import Path
import random
import json

# We'll stage exercises using the safe wrapper instead of importing create_simple_exercise directly
import sys
BASE_DIR = Path(__file__).parent.parent
REPO_ROOT = BASE_DIR.parent
sys.path.insert(0, str(REPO_ROOT))
import subprocess

SAFE_WRAPPER = BASE_DIR / '_tools' / 'add_exercise_safe.py'

OUT_DIR = BASE_DIR / 'temp' / 'intervalo_generated'
OUT_DIR.mkdir(parents=True, exist_ok=True)

interval_forms = [('[{a}, {b}]', True, True),
                  ('({a}, {b})', False, False),
                  ('[{a}, {b})', True, False),
                  ('({a}, {b}]', False, True)]

# A função que gera uma variação
def make_problem(a, b, form):
    interval_tex = form.format(a=a, b=b)
    # pick a candidate: choose either a boundary or interior or outside
    choice_type = random.choice(['inside','left_out','right_out','left_border','right_border'])
    if choice_type == 'inside':
        # pick integer strictly inside
        val = a + 1 if a+1 < b else (a + (b-a)//2)
    elif choice_type == 'left_out':
        val = a - 1
    elif choice_type == 'right_out':
        val = b + 1
    elif choice_type == 'left_border':
        val = a
    else:
        val = b

    statement = f"Indique se o número {val} pertence ao intervalo {interval_tex}. Justifique a sua resposta."
    return statement, val, choice_type


def generate(count: int = 10):
    created = []
    discipline = 'matematica'
    module = 'P4_funcoes'
    concept = '1-intervalo_real'
    tipo = 'pertinencia_intervalo'

    # use a variety of intervals
    for i in range(count):
        # choose a and b such that b>a and small integers
        a = random.randint(-3, 5)
        b = random.randint(a+1, a+6)
        form_tpl, _, _ = random.choice(interval_forms)
        statement, val, choice_type = make_problem(a, b, form_tpl)

        # stage exercise via safe wrapper
        try:
            # write payload
            payload = {
                'mode': 'stage',
                'discipline': discipline,
                'module': module,
                'concept': concept,
                'tipo': tipo,
                'difficulty': 1,
                'statement': statement
            }
            import tempfile
            tmp = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json', encoding='utf-8')
            tmp.write(json.dumps(payload, ensure_ascii=False))
            tmp.flush()
            tmp_path = tmp.name
            tmp.close()

            proc = subprocess.run([sys.executable, str(SAFE_WRAPPER), f'--payload-file={tmp_path}'], capture_output=True, text=True)
            out = proc.stdout.strip()
            if out:
                # expect JSON output from add_exercise_simple stage
                try:
                    res = json.loads(out.splitlines()[-1])
                    if isinstance(res, dict) and res.get('status') == 'staged' and res.get('staged_id'):
                        created.append({
                            'id': res.get('staged_id'),
                            'statement': statement,
                            'a': a,
                            'b': b,
                            'choice_type': choice_type,
                            'staged_path': res.get('staged_path')
                        })
                        print(f"Staged: {res.get('staged_id')} | {statement}")
                    else:
                        print(f"Unexpected wrapper output: {out}")
                except Exception:
                    print(f"Non-JSON wrapper output: {out}")
            else:
                print(f"No output from wrapper; rc={proc.returncode}; stderr={proc.stderr}")

        except Exception as e:
            print(f"Failed to stage exercise: {str(e)}")


    # salvar relatório
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = OUT_DIR / f'intervalo_report_{ts}.json'
    report_file.write_text(json.dumps({'generated': created, 'count': len(created)}, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"\nReport saved to: {report_file}")
    return created


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--count', type=int, default=10, help='Número de exercícios a gerar')
    args = parser.parse_args()
    generate(args.count)
