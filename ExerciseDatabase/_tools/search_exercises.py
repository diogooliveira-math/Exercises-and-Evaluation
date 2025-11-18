"""
Sistema de Pesquisa de Exercícios - Versão Modular
Pesquisa avançada por módulo, conceito, dificuldade, tags
Versão: 2.0
"""

import json
import yaml
from pathlib import Path
from typing import List, Dict, Optional

# Cores para terminal
class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    BLUE = '\033[94m'

BASE_DIR = Path(__file__).parent.parent
CONFIG_FILE = BASE_DIR / "modules_config.yaml"

def load_index() -> Optional[Dict]:
    """Carrega índice de exercícios"""
    index_file = BASE_DIR / "index.json"
    if not index_file.exists():
        print(f"{Colors.YELLOW}⚠ Índice não encontrado. Execute add_exercise.py primeiro{Colors.END}")
        return None
    
    with open(index_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_config() -> Dict:
    """Carrega configuração de módulos"""
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def search_exercises(
    module: Optional[str] = None,
    concept: Optional[str] = None,
    difficulty: Optional[int] = None,
    exercise_type: Optional[str] = None,
    tags: Optional[List[str]] = None,
    min_points: Optional[float] = None,
    max_points: Optional[float] = None
) -> List[Dict]:
    """Pesquisa exercícios com filtros"""
    index = load_index()
    if not index:
        return []
    
    results = []
    
    for exercise in index["exercises"]:
        # Aplicar filtros
        if module and exercise["module"] != module:
            continue
        if concept and exercise["concept"] != concept:
            continue
        if difficulty and exercise["difficulty"] != difficulty:
            continue
        if exercise_type and exercise["type"] != exercise_type:
            continue
        if min_points and exercise["points"] < min_points:
            continue
        if max_points and exercise["points"] > max_points:
            continue
        if tags:
            if not any(tag in exercise["tags"] for tag in tags):
                continue
        
        results.append(exercise)
    
    return results

def display_results(results: List[Dict], config: Dict):
    """Exibe resultados da pesquisa"""
    if not results:
        print(f"\n{Colors.YELLOW}❌ Nenhum exercício encontrado com os critérios especificados.{Colors.END}")
        return
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}RESULTADOS: {len(results)} exercício(s) encontrado(s){Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}\n")
    
    for i, ex in enumerate(results, 1):
        # Obter label de dificuldade
        diff_label = config['difficulty_levels'][ex['difficulty']]['label']
        
        print(f"{Colors.GREEN}{Colors.BOLD}{i}. {ex['id']}{Colors.END}")
        print(f"   {Colors.BOLD}Módulo:{Colors.END} {ex['module_name']}")
        print(f"   {Colors.BOLD}Conceito:{Colors.END} {ex['concept_name']}")
        print(f"   {Colors.BOLD}Dificuldade:{Colors.END} {ex['difficulty']}/5 ({diff_label}) | "
              f"{Colors.BOLD}Tipo:{Colors.END} {ex['type']}")
        print(f"   {Colors.BOLD}Pontos:{Colors.END} {ex['points']} | "
              f"{Colors.BOLD}Tags:{Colors.END} {', '.join(ex['tags'])}")
        print(f"   {Colors.BLUE}📄 {ex['path']}{Colors.END}")
        print()

def display_statistics(index: Dict, config: Dict):
    """Exibe estatísticas da base de dados"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}ESTATÍSTICAS DA BASE DE DADOS{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}\n")
    
    print(f"{Colors.BOLD}Total de Exercícios:{Colors.END} {index['total_exercises']}")
    print(f"{Colors.BOLD}Última Atualização:{Colors.END} {index['last_updated'][:19]}")
    
    # Por módulo
    print(f"\n{Colors.BOLD}{Colors.YELLOW}📚 Por Módulo:{Colors.END}")
    for module_id, count in index["statistics"]["by_module"].items():
        module_name = config['matematica'][module_id]['name']
        print(f"   • {module_name}: {count} exercícios")
    
    # Por conceito
    print(f"\n{Colors.BOLD}{Colors.YELLOW}💡 Por Conceito (Top 10):{Colors.END}")
    sorted_concepts = sorted(
        index["statistics"]["by_concept"].items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]
    
    for concept_id, count in sorted_concepts:
        # Encontrar nome do conceito
        concept_name = concept_id.replace('_', ' ').title()
        for module_id, module_data in config['matematica'].items():
            for concept in module_data['concepts']:
                if concept['id'] == concept_id:
                    concept_name = concept['name']
                    break
        
        print(f"   • {concept_name}: {count} exercícios")
    
    # Por dificuldade
    print(f"\n{Colors.BOLD}{Colors.YELLOW}⭐ Por Dificuldade:{Colors.END}")
    for diff_label, count in index["statistics"]["by_difficulty"].items():
        print(f"   • {diff_label}: {count} exercícios")
    
    # Por tipo
    print(f"\n{Colors.BOLD}{Colors.YELLOW}📝 Por Tipo:{Colors.END}")
    for ex_type, count in index["statistics"]["by_type"].items():
        type_name = config['exercise_types'][ex_type]['name']
        print(f"   • {type_name}: {count} exercícios")
    
    print()

def interactive_search():
    """Interface interativa de pesquisa"""
    config = load_config()
    index = load_index()
    
    if not index:
        return
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'PESQUISAR EXERCÍCIOS'.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}\n")
    
    # Menu principal
    print(f"{Colors.BOLD}Escolha o modo de pesquisa:{Colors.END}")
    print(f"  1. Pesquisa Personalizada")
    print(f"  2. Ver Estatísticas")
    print(f"  3. Listar Todos os Exercícios")
    print(f"  4. Pesquisa Rápida por Módulo")
    print(f"  5. Pesquisa Rápida por Conceito")
    
    mode = input(f"\n{Colors.CYAN}Escolha (1-5): {Colors.END}").strip()
    
    if mode == "2":
        display_statistics(index, config)
        return
    
    if mode == "3":
        display_results(index["exercises"], config)
        return
    
    if mode == "4":
        # Pesquisa rápida por módulo
        print(f"\n{Colors.YELLOW}Módulos disponíveis:{Colors.END}")
        modules = list(config['matematica'].keys())
        for i, module_id in enumerate(modules, 1):
            module_name = config['matematica'][module_id]['name']
            count = index["statistics"]["by_module"].get(module_id, 0)
            print(f"  {i}. {module_name} ({count} exercícios)")
        
        choice = input(f"\n{Colors.CYAN}Escolha o módulo (1-{len(modules)}): {Colors.END}").strip()
        try:
            module_id = modules[int(choice) - 1]
            results = search_exercises(module=module_id)
            display_results(results, config)
        except (ValueError, IndexError):
            print(f"{Colors.RED}Escolha inválida!{Colors.END}")
        return
    
    if mode == "5":
        # Pesquisa rápida por conceito
        print(f"\n{Colors.YELLOW}Escolha o módulo primeiro:{Colors.END}")
        modules = list(config['matematica'].keys())
        for i, module_id in enumerate(modules, 1):
            module_name = config['matematica'][module_id]['name']
            print(f"  {i}. {module_name}")
        
        choice = input(f"\n{Colors.CYAN}Escolha o módulo (1-{len(modules)}): {Colors.END}").strip()
        try:
            module_id = modules[int(choice) - 1]
            concepts = config['matematica'][module_id]['concepts']
            
            print(f"\n{Colors.YELLOW}Conceitos disponíveis:{Colors.END}")
            for i, concept in enumerate(concepts, 1):
                count = index["statistics"]["by_concept"].get(concept['id'], 0)
                print(f"  {i}. {concept['name']} ({count} exercícios)")
            
            choice = input(f"\n{Colors.CYAN}Escolha o conceito (1-{len(concepts)}): {Colors.END}").strip()
            concept_id = concepts[int(choice) - 1]['id']
            results = search_exercises(module=module_id, concept=concept_id)
            display_results(results, config)
        except (ValueError, IndexError):
            print(f"{Colors.RED}Escolha inválida!{Colors.END}")
        return
    
    # Modo 1: Pesquisa personalizada
    print(f"\n{Colors.BLUE}Deixe em branco para não filtrar por esse critério{Colors.END}\n")
    
    # Módulo
    modules = list(config['matematica'].keys())
    module_names = [config['matematica'][m]['name'] for m in modules]
    print(f"{Colors.YELLOW}Módulos disponíveis:{Colors.END}")
    for i, name in enumerate(module_names, 1):
        print(f"  {i}. {name}")
    
    module_input = input(f"\n{Colors.CYAN}Módulo (número ou deixe vazio): {Colors.END}").strip()
    module = None
    if module_input:
        try:
            module = modules[int(module_input) - 1]
        except (ValueError, IndexError):
            pass
    
    # Conceito (se módulo selecionado)
    concept = None
    if module:
        concepts = config['matematica'][module]['concepts']
        print(f"\n{Colors.YELLOW}Conceitos do módulo:{Colors.END}")
        for i, c in enumerate(concepts, 1):
            print(f"  {i}. {c['name']}")
        
        concept_input = input(f"\n{Colors.CYAN}Conceito (número ou deixe vazio): {Colors.END}").strip()
        if concept_input:
            try:
                concept = concepts[int(concept_input) - 1]['id']
            except (ValueError, IndexError):
                pass
    
    # Dificuldade
    diff_input = input(f"\n{Colors.CYAN}Dificuldade (1-5 ou deixe vazio): {Colors.END}").strip()
    difficulty = int(diff_input) if diff_input else None
    
    # Tipo
    types = list(config['exercise_types'].keys())
    type_names = [config['exercise_types'][t]['name'] for t in types]
    print(f"\n{Colors.YELLOW}Tipos disponíveis:{Colors.END}")
    for i, name in enumerate(type_names, 1):
        print(f"  {i}. {name}")
    
    type_input = input(f"\n{Colors.CYAN}Tipo (número ou deixe vazio): {Colors.END}").strip()
    exercise_type = None
    if type_input:
        try:
            exercise_type = types[int(type_input) - 1]
        except (ValueError, IndexError):
            pass
    
    # Tags
    tags_input = input(f"\n{Colors.CYAN}Tags (separadas por vírgula ou deixe vazio): {Colors.END}").strip()
    tags = [t.strip() for t in tags_input.split(",")] if tags_input else None
    
    # Pontos
    min_points_input = input(f"\n{Colors.CYAN}Pontuação mínima (ou deixe vazio): {Colors.END}").strip()
    min_points = float(min_points_input) if min_points_input else None
    
    max_points_input = input(f"\n{Colors.CYAN}Pontuação máxima (ou deixe vazio): {Colors.END}").strip()
    max_points = float(max_points_input) if max_points_input else None
    
    # Executar pesquisa
    results = search_exercises(
        module=module,
        concept=concept,
        difficulty=difficulty,
        exercise_type=exercise_type,
        tags=tags,
        min_points=min_points,
        max_points=max_points
    )
    
    display_results(results, config)

def main():
    """Função principal"""
    try:
        interactive_search()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Operação cancelada.{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}Erro: {str(e)}{Colors.END}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
