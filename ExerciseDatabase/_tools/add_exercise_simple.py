#!/usr/bin/env python3
"""
Script simplificado para adicionar exercícios - Versão para agentes
Não depende do sistema de preview complexo
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Adicionar o diretório base ao path
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

def create_simple_exercise(discipline, module, concept, tipo, difficulty, statement):
    """Cria um exercício simples sem preview"""

    # Caminhos
    tipo_path = BASE_DIR / discipline / module / concept / tipo
    tipo_path.mkdir(parents=True, exist_ok=True)

    # Metadata do tipo
    metadata_file = tipo_path / "metadata.json"
    if metadata_file.exists():
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
    else:
        metadata = {
            "tipo": tipo,
            "tipo_nome": tipo.replace('_', ' ').title(),
            "exercicios": {}
        }

    # Gerar ID
    existing = list(tipo_path.glob("*.tex"))
    number = len(existing) + 1
    disc_abbr = discipline[:3].upper()
    module_abbr = module.replace('_', '').upper()[:8]
    concept_abbr = ''.join([word[0].upper() for word in concept.split('-') if word][:3]).ljust(3, 'X')
    tipo_abbr = ''.join([word[0].upper() for word in tipo.split('_')][:3]).ljust(3, 'X')
    exercise_id = f"{disc_abbr}_{module_abbr}_{concept_abbr}_{tipo_abbr}_{number:03d}"

    # Criar conteúdo LaTeX
    today = datetime.now().strftime("%Y-%m-%d")
    content = f"""% Exercise ID: {exercise_id}
% Created: {today}
% Difficulty: {difficulty}/5

\\exercicio{{{statement}}}
"""

    # Salvar arquivo
    tex_file = tipo_path / f"{exercise_id}.tex"
    with open(tex_file, 'w', encoding='utf-8') as f:
        f.write(content)

    # Atualizar metadata
    metadata["exercicios"][exercise_id] = {
        "created": today,
        "difficulty": difficulty,
        "status": "active"
    }

    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    # Atualizar index global (simplificado)
    index_file = BASE_DIR / "index.json"
    if index_file.exists():
        with open(index_file, 'r', encoding='utf-8') as f:
            index = json.load(f)
    else:
        index = {"exercises": []}

    index["exercises"].append({
        "id": exercise_id,
        "path": str(tex_file.relative_to(BASE_DIR)).replace("\\", "/"),
        "discipline": discipline,
        "module": module,
        "concept": concept,
        "tipo": tipo,
        "difficulty": difficulty,
        "status": "active"
    })

    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

    return exercise_id

def main():
    if len(sys.argv) != 7:
        print("Uso: python add_exercise_simple.py <discipline> <module> <concept> <tipo> <difficulty> <statement>")
        sys.exit(1)

    discipline = sys.argv[1]
    module = sys.argv[2]
    concept = sys.argv[3]
    tipo = sys.argv[4]
    difficulty = int(sys.argv[5])
    statement = sys.argv[6]

    # Remover aspas se presentes
    if statement.startswith('"') and statement.endswith('"'):
        statement = statement[1:-1]

    try:
        exercise_id = create_simple_exercise(discipline, module, concept, tipo, difficulty, statement)
        print(f"SUCCESS: {exercise_id}")
    except Exception as e:
        print(f"ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()