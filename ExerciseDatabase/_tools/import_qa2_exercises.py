#!/usr/bin/env python3
"""
Import exercises from temp/QA2 folder into ExerciseDatabase
For concept: funcao_inversa (A10_funcoes)
"""

import json
import shutil
from pathlib import Path
from datetime import datetime

# Paths
ROOT = Path(__file__).parent.parent
TEMP_CONTENT = ROOT / "../temp/QA2/content"
DB_BASE = ROOT / "matematica/P4_funcoes/4-funcao_inversa"
INDEX_FILE = ROOT / "index.json"

# Create concept folder if needed
DB_BASE.mkdir(parents=True, exist_ok=True)

# Exercise data
exercises = [
    {
        "num": "001",
        "source": "exercise1.tex",
        "title": "Função inversa de uma função linear",
        "description": "Determinar expressão analítica e representar graficamente função e inversa",
        "difficulty": 2,
        "points": 10,
        "time_minutes": 10,
        "parts": 2,
        "tags": ["inversa", "funcao_linear", "grafico", "expressao_analitica"]
    },
    {
        "num": "002",
        "source": "exercise2.tex",
        "title": "Representação gráfica da função inversa",
        "description": "Dado o gráfico de ramos de funções, desenhar o gráfico da inversa",
        "difficulty": 2,
        "points": 10,
        "time_minutes": 10,
        "parts": 2,
        "tags": ["inversa", "grafico", "simetria", "funcao_quadratica"]
    },
    {
        "num": "003",
        "source": "exercise3.tex",
        "title": "Identificar funções invertíveis",
        "description": "Determinar quais funções são invertíveis usando teste da reta horizontal",
        "difficulty": 2,
        "points": 10,
        "time_minutes": 10,
        "parts": 1,
        "tags": ["inversa", "injetividade", "teste_reta_horizontal", "grafico"]
    },
    {
        "num": "004",
        "source": "exercise4.tex",
        "title": "Determinação analítica da função inversa",
        "description": "Calcular a expressão da inversa de funções simples",
        "difficulty": 2,
        "points": 10,
        "time_minutes": 10,
        "parts": 2,
        "tags": ["inversa", "expressao_analitica", "calculo"]
    }
]

def generate_id(num: str) -> str:
    """Generate exercise ID: MAT_P4FUNCOE_4FIN_XXX"""
    return f"MAT_P4FUNCOE_4FIN_{num}"

def create_exercise_files(ex_data: dict):
    """Create .tex and .json for one exercise"""
    ex_id = generate_id(ex_data["num"])
    
    # Read source content
    source_path = TEMP_CONTENT / ex_data["source"]
    if not source_path.exists():
        print(f"⚠️  Source not found: {source_path}")
        return None
    
    content = source_path.read_text(encoding="utf-8")
    
    # Remove comment lines (first line is typically a comment)
    lines = content.splitlines()
    filtered_lines = [line for line in lines if not line.strip().startswith('%')]
    clean_content = '\n'.join(filtered_lines).strip()
    
    # Create header
    header = f"""% Exercise ID: {ex_id}
% Module: MÓDULO P4 - Funções | Concept: Função Inversa
% Difficulty: {ex_data['difficulty']}/5 (Fácil) | Type: desenvolvimento
% Points: {ex_data['points']} | Time: {ex_data['time_minutes']} min
% Tags: {', '.join(ex_data['tags'])}
% Author: Professor | Date: {datetime.now().strftime('%Y-%m-%d')}
% Status: active
% Description: {ex_data['description']}

"""
    
    # Determinar tipo (diretório) com base em tags e criar se necessário
    def suggest_type(tags: list) -> str:
        if any(tag in tags for tag in ['calculo_analitico', 'expressao_analitica', 'calculo']):
            return 'determinacao_analitica'
        if any(tag in tags for tag in ['grafico', 'simetria', 'bissectriz']):
            return 'determinacao_grafica'
        if any(tag in tags for tag in ['injetividade', 'teste_reta_horizontal']):
            return 'teste_reta_horizontal'
        return 'outros'

    tipo_id = suggest_type(ex_data["tags"])
    tipo_path = DB_BASE / tipo_id
    tipo_path.mkdir(parents=True, exist_ok=True)

    # Write .tex file inside the type folder
    tex_path = tipo_path / f"{ex_id}.tex"
    tex_path.write_text(header + clean_content, encoding="utf-8")

    # Atualizar metadata do tipo (um único metadata.json por tipo)
    tipo_metadata_file = tipo_path / "metadata.json"
    if tipo_metadata_file.exists():
        try:
            tipo_meta = json.loads(tipo_metadata_file.read_text(encoding="utf-8"))
        except Exception:
            tipo_meta = {"tipo": tipo_id, "tipo_nome": tipo_id.replace('_', ' ').title(), "exercicios": []}
    else:
        tipo_meta = {"tipo": tipo_id, "tipo_nome": tipo_id.replace('_', ' ').title(), "exercicios": []}

    if not isinstance(tipo_meta.get("exercicios"), list):
        tipo_meta["exercicios"] = []

    if ex_id not in tipo_meta["exercicios"]:
        tipo_meta["exercicios"].append(ex_id)

    tipo_metadata_file.write_text(json.dumps(tipo_meta, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "id": ex_id,
        "path": f"matematica/P4_funcoes/4-funcao_inversa/{tipo_id}/{ex_id}.tex",
        "discipline": "matematica",
        "module": "P4_funcoes",
        "module_name": "MÓDULO P4 - Funções",
        "concept": "4-funcao_inversa",
        "concept_name": "Função Inversa",
        "difficulty": ex_data["difficulty"],
        "type": tipo_id,
        "tags": ex_data["tags"],
        "points": ex_data["points"],
        "status": "active"
    }

def update_index(new_exercises: list):
    """Update index.json with new exercises"""
    if not INDEX_FILE.exists():
        index = {
            "database_version": "2.0",
            "last_updated": datetime.now().isoformat(),
            "total_exercises": 0,
            "statistics": {
                "by_module": {},
                "by_concept": {},
                "by_difficulty": {},
                "by_type": {},
                "by_discipline": {}
            },
            "exercises": []
        }
    else:
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            index = json.load(f)
    
    # Add new exercises
    index["exercises"].extend(new_exercises)
    index["total_exercises"] = len(index["exercises"])
    index["last_updated"] = datetime.now().isoformat()
    
    # Update statistics
    stats = index["statistics"]
    
    # By module
    for ex in index["exercises"]:
        mod = ex["module"]
        stats["by_module"][mod] = stats["by_module"].get(mod, 0) + 1
    
    # By concept
    stats["by_concept"] = {}
    for ex in index["exercises"]:
        concept = ex["concept_name"]
        stats["by_concept"][concept] = stats["by_concept"].get(concept, 0) + 1
    
    # By difficulty
    difficulty_labels = {1: "Muito Fácil", 2: "Fácil", 3: "Médio", 4: "Difícil", 5: "Muito Difícil"}
    stats["by_difficulty"] = {}
    for ex in index["exercises"]:
        diff_label = difficulty_labels.get(ex["difficulty"], "Desconhecido")
        stats["by_difficulty"][diff_label] = stats["by_difficulty"].get(diff_label, 0) + 1
    
    # By type
    stats["by_type"] = {}
    for ex in index["exercises"]:
        typ = ex["type"]
        stats["by_type"][typ] = stats["by_type"].get(typ, 0) + 1
    
    # By discipline
    stats["by_discipline"] = {}
    for ex in index["exercises"]:
        disc = ex["discipline"]
        stats["by_discipline"][disc] = stats["by_discipline"].get(disc, 0) + 1
    
    # Rebuild statistics properly (avoid duplicates)
    stats["by_module"] = {}
    stats["by_concept"] = {}
    stats["by_difficulty"] = {}
    stats["by_type"] = {}
    stats["by_discipline"] = {}
    
    for ex in index["exercises"]:
        # Module
        mod = ex["module"]
        stats["by_module"][mod] = stats["by_module"].get(mod, 0) + 1
        
        # Concept
        concept = ex["concept_name"]
        stats["by_concept"][concept] = stats["by_concept"].get(concept, 0) + 1
        
        # Difficulty
        diff_label = difficulty_labels.get(ex["difficulty"], "Desconhecido")
        stats["by_difficulty"][diff_label] = stats["by_difficulty"].get(diff_label, 0) + 1
        
        # Type
        typ = ex["type"]
        stats["by_type"][typ] = stats["by_type"].get(typ, 0) + 1
        
        # Discipline
        disc = ex["discipline"]
        stats["by_discipline"][disc] = stats["by_discipline"].get(disc, 0) + 1
    
    # Write updated index
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Index atualizado: {index['total_exercises']} exercícios totais")

def main():
    """Main import routine"""
    print("🔄 Importar exercícios QA2 (Função Inversa)...\n")
    
    if not TEMP_CONTENT.exists():
        print(f"❌ Pasta não encontrada: {TEMP_CONTENT}")
        return
    
    new_exercises = []
    
    for ex_data in exercises:
        print(f"  Processando: {ex_data['source']} → {generate_id(ex_data['num'])}")
        result = create_exercise_files(ex_data)
        if result:
            new_exercises.append(result)
            print(f"    ✅ {result['id']}")
    
    print(f"\n📝 Atualizando index.json...")
    update_index(new_exercises)
    
    print(f"\n✅ Importação concluída!")
    print(f"   📁 Pasta: {DB_BASE}")
    print(f"   📊 Exercícios importados: {len(new_exercises)}")
    print(f"\n💡 Próximo passo: python generate_sebentas.py (para criar sebenta de funcao_inversa)")

if __name__ == "__main__":
    main()
