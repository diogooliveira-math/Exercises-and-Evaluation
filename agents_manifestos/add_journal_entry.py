#!/usr/bin/env python3
"""
Script para adicionar entradas ao journaling de intervenções.

Este script permite agentes ou usuários adicionar entradas concisas ao journaling de uma intervenção específica.
As entradas são armazenadas em arquivos separados em 'journaling/' para evitar saturação de tokens nos manifestos.

Uso:
    python add_journal_entry.py --intervencao "intervencao_2025-11-28_otimizacao" --data "2025-11-28 10:00" --descricao "Correção aplicada" --agente "assistant"

Ou interativo:
    python add_journal_entry.py
"""

import argparse
import os
from datetime import datetime

# Caminhos relativos à pasta agents_manifestos
JOURNALING_DIR = "journaling"

def collect_inputs_interactive():
    """Coleta inputs do usuário de forma interativa."""
    print("Adicionando entrada ao journaling. Preencha os campos:")
    intervencao = input("Nome da intervenção (e.g., intervencao_2025-11-28_otimizacao): ").strip()
    data = input("Data e hora (YYYY-MM-DD HH:MM, padrão agora): ").strip() or datetime.now().strftime("%Y-%m-%d %H:%M")
    descricao = input("Descrição concisa: ").strip()
    agente = input("Agente (e.g., assistant): ").strip()

    return {
        'intervencao': intervencao,
        'data': data,
        'descricao': descricao,
        'agente': agente
    }

def add_entry_to_journal(intervencao, data, descricao, agente):
    """Adiciona entrada ao arquivo de journaling da intervenção."""
    journal_file = os.path.join(JOURNALING_DIR, f"{intervencao}_journal.md")
    os.makedirs(JOURNALING_DIR, exist_ok=True)

    entry = f"- {data}: {descricao} (agent: {agente})\n"

    # Se o arquivo não existir, cria com cabeçalho
    if not os.path.exists(journal_file):
        with open(journal_file, 'w', encoding='utf-8') as f:
            f.write(f"# Journaling para Intervenção: {intervencao}\n\n")
            f.write("Entradas de implementação concisas:\n\n")

    # Adiciona a entrada
    with open(journal_file, 'a', encoding='utf-8') as f:
        f.write(entry)

    print(f"Entrada adicionada a: {journal_file}")

def main():
    parser = argparse.ArgumentParser(description="Adicionar entrada ao journaling de intervenções.")
    parser.add_argument('--intervencao', help='Nome da intervenção (e.g., intervencao_2025-11-28_otimizacao)', required=True)
    parser.add_argument('--data', help='Data e hora (YYYY-MM-DD HH:MM)', default=datetime.now().strftime("%Y-%m-%d %H:%M"))
    parser.add_argument('--descricao', help='Descrição concisa da ação', required=True)
    parser.add_argument('--agente', help='Nome do agente (e.g., assistant)', required=True)

    args = parser.parse_args()

    # Se não há args obrigatórios via CLI, usar modo interativo
    if not args.intervencao or not args.descricao or not args.agente:
        inputs = collect_inputs_interactive()
    else:
        inputs = {
            'intervencao': args.intervencao,
            'data': args.data,
            'descricao': args.descricao,
            'agente': args.agente
        }

    # Adicionar entrada
    add_entry_to_journal(**inputs)

if __name__ == "__main__":
    main()