#!/usr/bin/env python3
"""
Manifesto Writer Tool - Subagent para criar intervenções

Esta ferramenta permite agentes criarem intervenções automaticamente usando o script Python create_intervention.py.
Pode ser chamada por outros agentes OpenCode.

Uso:
    python .opencode/manifesto-writer.py --data "2025-11-28" --contexto "Otimização" --objetivo "Melhorar X" --todo "Tarefa 1"
"""

import argparse
import subprocess
import sys
import os

def main():
    parser = argparse.ArgumentParser(description="Criar intervenção via subagent.")
    parser.add_argument('--data', default=os.popen('date +%Y-%m-%d').read().strip() or '2025-11-28')
    parser.add_argument('--contexto', required=True)
    parser.add_argument('--objetivo', required=True)
    parser.add_argument('--todo', action='append', default=[])

    args = parser.parse_args()

    # Construir comando
    command = [sys.executable, 'agents_manifestos/create_intervention.py',
               '--data', args.data,
               '--contexto', args.contexto,
               '--objetivo', args.objetivo]
    for todo in args.todo:
        command.extend(['--todo', todo])

    print("Executando:", ' '.join(command))

    # Executar
    result = subprocess.run(command, cwd=os.getcwd(), capture_output=True, text=True)

    if result.returncode != 0:
        print("Erro:", result.stderr)
        sys.exit(result.returncode)

    print("Sucesso:")
    print(result.stdout)

if __name__ == "__main__":
    main()