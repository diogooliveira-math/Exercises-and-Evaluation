#!/usr/bin/env python3
"""
Simulated agent that calls the OLD script directly with a single
bracketed key=value argument (the failing pattern).
"""
import subprocess
import sys

PROMPT = (
    "[discipline=matematica, module=P4_funcoes, concept=1-generalidades_funcoes, "
    "tipo=afirmacoes_contexto, difficulty=2, statement=Quero que cries um exercício no módulo P4_funcoes na generalidades de funcoes (procura a nomenclatura correta). "
    "Adiciona um novo tipo de exercício (escolhe tu a nomenclatura do tipo), onde os alunos analisem afirmações do tipo \"quando o preço aumenta a despesa vai aumentar\" e indiquem para cada afirmação se é verdadeira ou falsa, justificando a resposta.]"
)

def main():
    # Use safe wrapper to stage instead of direct create
    import tempfile, json
    payload = {
        'mode': 'stage',
        'discipline': 'matematica',
        'module': 'P4_funcoes',
        'concept': '1-generalidades_funcoes',
        'tipo': 'afirmacoes_contexto',
        'difficulty': 2,
        'statement': 'Quero que cries um exercício no módulo P4_funcoes na generalidades de funcoes.'
    }
    tmp = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json', encoding='utf-8')
    tmp.write(json.dumps(payload, ensure_ascii=False))
    tmp.flush()
    tmp_path = tmp.name
    tmp.close()
    cmd = [sys.executable, "ExerciseDatabase/_tools/add_exercise_safe.py", f"--payload-file={tmp_path}", '--mode=stage']
    print("OLD agent (safe) running:", " ".join(cmd))
    proc = subprocess.run(cmd, capture_output=True, text=True)
    print("--- STDOUT ---")
    print(proc.stdout)
    print("--- STDERR ---")
    print(proc.stderr)
    print("RETURNCODE:", proc.returncode)

    print("--- STDOUT ---")
    print(proc.stdout)
    print("--- STDERR ---")
    print(proc.stderr)
    print("RETURNCODE:", proc.returncode)

if __name__ == '__main__':
    main()
