"""
Script de Teste - Cria exercícios de exemplo automaticamente
Para testar o sistema completo
Versão: 1.0
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Adicionar diretório tools ao path
sys.path.insert(0, str(Path(__file__).parent))

# Importar funções do add_exercise
from add_exercise import (
    BASE_DIR, ModuleConfig, get_next_exercise_id,
    update_index, print_header, print_success, print_info
)

def create_test_exercise(
    module_id: str,
    concept_id: str,
    exercise_type: str,
    difficulty: int,
    statement: str,
    parts: list,
    points: float,
    time_minutes: int,
    tags: list,
    author: str = "Sistema de Testes"
):
    """Cria um exercício de teste"""
    
    config = ModuleConfig()
    
    # Obter nomes
    module_name = config.config['matematica'][module_id]['name']
    concept_obj = next(c for c in config.config['matematica'][module_id]['concepts'] 
                      if c['id'] == concept_id)
    concept_name = concept_obj['name']
    auto_tags = concept_obj.get('tags', [])
    all_tags = list(set(auto_tags + tags))
    
    # Gerar ID (discipline fixa: matematica)
    exercise_id = get_next_exercise_id("matematica", module_id, concept_id)
    
    # Data
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Metadados
    metadata = {
        "id": exercise_id,
        "version": "1.0",
        "created": today,
        "modified": today,
        "author": author,
        "module": {
            "id": module_id,
            "name": module_name
        },
        "concept": {
            "id": concept_id,
            "name": concept_name
        },
        "classification": {
            "discipline": "matematica",
            "module": module_id,
            "concept": concept_id,
            "tags": all_tags,
            "difficulty": difficulty,
            "difficulty_label": config.get_difficulty_label(difficulty)
        },
        "exercise_type": exercise_type,
        "content": {
            "has_multiple_parts": len(parts) > 0,
            "parts_count": len(parts),
            "has_graphics": False,
            "requires_packages": ["amsmath", "amssymb"]
        },
        "evaluation": {
            "points": points,
            "time_estimate_minutes": time_minutes,
            "bloom_level": "aplicacao"
        },
        "solution": {
            "available": False,
            "file": ""
        },
        "usage": {
            "times_used": 0,
            "last_used": "",
            "contexts": []
        },
        "status": "active"
    }
    
    # Conteúdo LaTeX
    latex_content = f"""% Exercise ID: {exercise_id}
% Module: {module_name} | Concept: {concept_name}
% Difficulty: {difficulty}/5 ({config.get_difficulty_label(difficulty)}) | Type: {exercise_type}
% Points: {points} | Time: {time_minutes} min
% Tags: {', '.join(all_tags)}
% Author: {author} | Date: {today}
% Status: active

\\exercicio{{{statement}}}
"""
    
    if parts:
        latex_content += "\n"
        for part in parts:
            latex_content += f"\\subexercicio{{{part['text']}}}\n\n"
        
        latex_content += "% Evaluation notes:\n"
        for part in parts:
            latex_content += f"% Part {part['letter']}): {part['points']} points\n"
    
    # Salvar ficheiros na pasta de testes para não poluir a BD real
    path = BASE_DIR / "test" / "matematica" / module_id / concept_id
    path.mkdir(parents=True, exist_ok=True)
    
    # Salvar .tex
    tex_file = path / f"{exercise_id}.tex"
    with open(tex_file, 'w', encoding='utf-8') as f:
        f.write(latex_content)
    
    # Salvar .json
    json_file = path / f"{exercise_id}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    # Atualizar índice
    update_index(metadata, tex_file.relative_to(BASE_DIR))
    
    print_success(f"Exercício criado: {exercise_id}")
    
    return exercise_id

def create_all_test_exercises():
    """Cria conjunto completo de exercícios de teste"""
    
    print_header("CRIAR EXERCÍCIOS DE TESTE (guardados em test/)")
    print_info("Criando 5 exercícios de exemplo para testar o sistema...\n")
    
    exercises_created = []
    
    # Exercício 1: Função Quadrática (Fácil)
    print("1/5 - Função Quadrática...")
    ex1 = create_test_exercise(
        module_id="A10_funcoes",
        concept_id="funcao_quadratica",
        exercise_type="desenvolvimento",
        difficulty=2,
        statement="Considere a função $f(x) = x^2 - 4x + 3$.",
        parts=[
            {"letter": "a", "text": "Determine o domínio e contradomínio da função.", "points": 3},
            {"letter": "b", "text": "Calcule as raízes da função.", "points": 4},
            {"letter": "c", "text": "Identifique o vértice da parábola.", "points": 3}
        ],
        points=10,
        time_minutes=15,
        tags=["raizes", "vertice"]
    )
    exercises_created.append(ex1)
    
    # Exercício 2: Monotonia (Médio)
    print("2/5 - Monotonia de Funções...")
    ex2 = create_test_exercise(
        module_id="A10_funcoes",
        concept_id="monotonia",
        exercise_type="desenvolvimento",
        difficulty=3,
        statement="A função $g(x) = -x^3 + 6x^2 - 9x + 4$ está representada graficamente.",
        parts=[
            {"letter": "a", "text": "Determine os intervalos de monotonia da função.", "points": 6},
            {"letter": "b", "text": "Identifique os pontos de máximo e mínimo relativos.", "points": 4}
        ],
        points=10,
        time_minutes=20,
        tags=["analise_grafica", "extremos_relativos"]
    )
    exercises_created.append(ex2)
    
    # Exercício 3: Taxa de Variação (Médio)
    print("3/5 - Taxa de Variação...")
    ex3 = create_test_exercise(
        module_id="A11_derivadas",
        concept_id="taxa_variacao",
        exercise_type="desenvolvimento",
        difficulty=3,
        statement="Um carro percorre uma distância dada por $d(t) = 5t^2 + 10t$ metros, onde $t$ é o tempo em segundos.",
        parts=[
            {"letter": "a", "text": "Calcule a taxa de variação média da distância no intervalo $[1, 3]$.", "points": 5},
            {"letter": "b", "text": "Determine a velocidade instantânea em $t = 2$ segundos.", "points": 5}
        ],
        points=10,
        time_minutes=15,
        tags=["velocidade", "problema_aplicado"]
    )
    exercises_created.append(ex3)
    
    # Exercício 4: Otimização (Difícil)
    print("4/5 - Problema de Otimização...")
    ex4 = create_test_exercise(
        module_id="A12_otimizacao",
        concept_id="problemas_otimizacao",
        exercise_type="desenvolvimento",
        difficulty=4,
        statement="Um agricultor tem 100 metros de vedação para criar um cercado retangular junto a um muro existente. O muro servirá como um dos lados do retângulo.",
        parts=[
            {"letter": "a", "text": "Exprima a área do cercado em função da largura $x$.", "points": 5},
            {"letter": "b", "text": "Determine as dimensões que maximizam a área do cercado.", "points": 8},
            {"letter": "c", "text": "Calcule a área máxima possível.", "points": 2}
        ],
        points=15,
        time_minutes=25,
        tags=["area", "maximizar"]
    )
    exercises_created.append(ex4)
    
    # Exercício 5: Limites (Médio)
    print("5/5 - Cálculo de Limites...")
    ex5 = create_test_exercise(
        module_id="A13_limites",
        concept_id="calculo_limites",
        exercise_type="desenvolvimento",
        difficulty=3,
        statement="Calcule os seguintes limites:",
        parts=[
            {"letter": "a", "text": "$\\displaystyle\\lim_{x \\to 2} \\frac{x^2 - 4}{x - 2}$", "points": 3},
            {"letter": "b", "text": "$\\displaystyle\\lim_{x \\to +\\infty} \\frac{3x^2 + 2x - 1}{x^2 + 5}$", "points": 4},
            {"letter": "c", "text": "$\\displaystyle\\lim_{x \\to 0} \\frac{\\sin(3x)}{x}$", "points": 3}
        ],
        points=10,
        time_minutes=18,
        tags=["indeterminacoes", "limites_notaveis"]
    )
    exercises_created.append(ex5)
    
    print()
    print_header("✓ EXERCÍCIOS DE TESTE CRIADOS COM SUCESSO!")
    print_info(f"Total: {len(exercises_created)} exercícios")
    print_info("IDs criados:")
    for ex_id in exercises_created:
        print(f"  • {ex_id}")
    
    return exercises_created

if __name__ == "__main__":
    try:
        create_all_test_exercises()
    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()
