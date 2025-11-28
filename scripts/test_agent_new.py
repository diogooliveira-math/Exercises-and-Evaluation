#!/usr/bin/env python3
"""
Simulated agent that calls the NEW wrapper (`scripts/run_add_exercise.py`)
with a single bracketed key=value argument to ensure proper normalization.
"""
import subprocess
import sys

PROMPT = (
    "[discipline=matematica, module=P4_funcoes, concept=1-generalidades_funcoes, "
    "tipo=afirmacoes_contexto, difficulty=2, statement=Quero que cries um exercício no módulo P4_funcoes na generalidades de funcoes (procura a nomenclatura correta). "
    "Adiciona um novo tipo de exercício (escolhe tu a nomenclatura do tipo), onde os alunos analisem afirmações do tipo \"quando o preço aumenta a despesa vai aumentar\" e indiquem para cada afirmação se é verdadeira ou falsa, justificando a resposta.]"
)

def main():
    cmd = [sys.executable, "scripts/run_add_exercise.py", PROMPT]
    print("NEW agent running:", " ".join(cmd))
    proc = subprocess.run(cmd, capture_output=True, text=True)
    print("--- STDOUT ---")
    print(proc.stdout)
    print("--- STDERR ---")
    print(proc.stderr)
    print("RETURNCODE:", proc.returncode)

if __name__ == '__main__':
    main()
