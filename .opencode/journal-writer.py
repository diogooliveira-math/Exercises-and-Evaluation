#!/usr/bin/env python3
"""
Journal Writer Tool - Subagent para adicionar entradas ao journaling

Esta ferramenta permite agentes adicionarem entradas ao journaling de intervenções usando o script Python add_journal_entry.py.
Pode ser chamada por outros agentes OpenCode.

Uso:
    python .opencode/journal-writer.py --intervencao "intervencao_2025-11-28_teste" --data "2025-11-28 10:00" --descricao "Ação realizada" --agente "assistant"
"""

import argparse
import subprocess
import sys
import os

def main():
    parser = argparse.ArgumentParser(description="Adicionar entrada ao journaling via subagent.")
    parser.add_argument('--intervencao', required=True)
    parser.add_argument('--data', default=os.popen('date +%Y-%m-%d\ %H:%M').read().strip() or '2025-11-28 10:00')
    parser.add_argument('--descricao', required=True)
    parser.add_argument('--agente', required=True)

    args = parser.parse_args()

    # Construir comando
    command = [sys.executable, 'agents_manifestos/add_journal_entry.py',
               '--intervencao', args.intervencao,
               '--data', args.data,
               '--descricao', args.descricao,
               '--agente', args.agente]

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