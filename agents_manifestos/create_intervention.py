#!/usr/bin/env python3
"""
Script para criar uma nova intervenção por agentes no projeto Exercises-and-Evaluation.

Este script formaliza o processo de criação de intervenções, permitindo personalização via inputs.
Ele copia o template em 'intervencoes/template.md', substitui placeholders com dados fornecidos
e salva um novo arquivo em 'intervencoes/' com nome único.

Uso:
    python create_intervention.py --data "2025-11-28" --contexto "Otimização de scripts" --objetivo "Melhorar performance" --todo "Corrigir bug X" --todo "Adicionar teste Y"

Ou interativo:
    python create_intervention.py

Dependências: Python 3.8+
"""

import argparse
import os
from datetime import datetime

# Caminhos relativos à pasta agents_manifestos
TEMPLATE_PATH = "intervencoes/template.md"
OUTPUT_DIR = "intervencoes"

def load_template():
    """Carrega o template de intervenção."""
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"Template não encontrado: {TEMPLATE_PATH}")
    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        return f.read()

def collect_inputs_interactive():
    """Coleta inputs do usuário de forma interativa."""
    print("Criando nova intervenção. Preencha os campos (pressione Enter para pular opcionais):")
    data = input("Data (YYYY-MM-DD, padrão hoje): ").strip() or datetime.now().strftime("%Y-%m-%d")
    contexto = input("Contexto (descrição breve): ").strip()
    objetivo = input("Objetivo (síntese concisa): ").strip()

    todos = []
    print("TODO items (digite um por linha, vazio para parar):")
    while True:
        todo = input("- ").strip()
        if not todo:
            break
        todos.append(todo)

    return {
        'data': data,
        'contexto': contexto,
        'objetivo': objetivo,
        'todos': todos
    }

def generate_filename(data, contexto):
    """Gera nome único para o arquivo de intervenção."""
    safe_contexto = contexto.replace(' ', '_').replace('/', '_')[:30]  # Limita tamanho
    return f"intervencao_{data}_{safe_contexto}.md"

def fill_template(template, data, contexto, objetivo, todos):
    """Substitui placeholders no template."""
    todo_list = '\n'.join(f'- [ ] {todo}' for todo in todos)
    filled = template.replace('[INSERIR DATA]', data)
    filled = filled.replace('[DESCREVER OBJETIVO ESPECÍFICO, e.g., "Correção de bugs em scripts de validação"]', contexto)
    filled = filled.replace('[SÍNTESE CONCISA: O que alcançar]', objetivo)
    filled = filled.replace('- [ ] [TAREFA 1]\n- [ ] [TAREFA 2]', todo_list)
    return filled

def save_intervention(content, filename):
    """Salva o conteúdo em um novo arquivo."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Intervenção criada: {filepath}")
    return filepath

def main():
    parser = argparse.ArgumentParser(description="Criar nova intervenção por agentes.")
    parser.add_argument('--data', help='Data da sessão (YYYY-MM-DD)', default=datetime.now().strftime("%Y-%m-%d"))
    parser.add_argument('--contexto', help='Contexto da intervenção', required=True)
    parser.add_argument('--objetivo', help='Objetivo conciso', required=True)
    parser.add_argument('--todo', action='append', help='Itens TODO (use múltiplas vezes)', default=[])

    args = parser.parse_args()

    # Se não há args obrigatórios via CLI, usar modo interativo
    if not args.contexto or not args.objetivo:
        inputs = collect_inputs_interactive()
    else:
        inputs = {
            'data': args.data,
            'contexto': args.contexto,
            'objetivo': args.objetivo,
            'todos': args.todo
        }

    # Carregar template
    template = load_template()

    # Gerar nome do arquivo
    filename = generate_filename(inputs['data'], inputs['contexto'])

    # Preencher template
    content = fill_template(template, **inputs)

    # Salvar
    save_intervention(content, filename)

if __name__ == "__main__":
    main()