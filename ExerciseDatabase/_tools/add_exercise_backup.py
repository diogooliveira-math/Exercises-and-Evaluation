"""
Sistema de Gestão de Exercícios - Versão Modular
Para Ensino Modular com controlo granular por conceito
Versão: 2.0
"""

import json
import os
import yaml
from datetime import datetime
from pathlib import Path
import re
from typing import Dict, List, Optional

# Cores para terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

# Configurações
BASE_DIR = Path(__file__).parent.parent
CONFIG_FILE = BASE_DIR / "modules_config.yaml"

class ModuleConfig:
    """Carrega e gere configuração de módulos"""
    
    def __init__(self):
        self.config = self.load_config()
        
    def load_config(self) -> Dict:
        """Carrega configuração YAML"""
        if not CONFIG_FILE.exists():
            print_error(f"Ficheiro de configuração não encontrado: {CONFIG_FILE}")
            print_info("Execute setup para criar a estrutura base")
            exit(1)
            
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def get_modules(self) -> List[tuple]:
        """Retorna lista de módulos (id, nome)"""
        modules = []
        for module_id, module_data in self.config['matematica'].items():
            modules.append((module_id, module_data['name']))
        return modules
    
    def get_concepts(self, module_id: str) -> List[Dict]:
        """Retorna conceitos de um módulo"""
        return self.config['matematica'][module_id]['concepts']
    
    def get_difficulty_label(self, level: int) -> str:
        """Retorna label de dificuldade"""
        return self.config['difficulty_levels'][level]['label']
    
    def get_presets(self) -> Dict:
        """Retorna presets rápidos"""
        return self.config['quick_presets']
    
    def get_exercise_types(self) -> Dict:
        """Retorna tipos de exercício"""
        return self.config['exercise_types']

def get_next_exercise_id(module_id: str, concept_id: str) -> str:
    """Gera próximo ID para exercício"""
    # Formato: MAT_MODULO_CONCEITO_NNN
    module_abbr = module_id.upper()
    concept_abbr = ''.join([word[0].upper() for word in concept_id.split('_')][:3]).ljust(3, 'X')
    
    # Encontrar exercícios existentes
    path = BASE_DIR / "matematica" / module_id / concept_id
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    
    existing_files = list(path.glob(f"MAT_{module_abbr}_{concept_abbr}_*.tex"))
    
    if not existing_files:
        number = 1
    else:
        numbers = []
        for f in existing_files:
            match = re.search(r'_(\d{3})\.tex$', f.name)
            if match:
                numbers.append(int(match.group(1)))
        number = max(numbers) + 1 if numbers else 1
    
    return f"MAT_{module_abbr}_{concept_abbr}_{number:03d}"

def select_from_list(options: List, prompt: str, show_descriptions: bool = False) -> tuple:
    """Menu de seleção genérico"""
    print(f"\n{Colors.YELLOW}{prompt}{Colors.END}")
    
    for i, option in enumerate(options, 1):
        if isinstance(option, tuple):
            print(f"  {i}. {option[1]}")
        elif isinstance(option, dict) and show_descriptions:
            print(f"  {i}. {option.get('name', option.get('label', 'N/A'))}")
            if 'description' in option:
                print(f"     {Colors.BLUE}→ {option['description']}{Colors.END}")
        else:
            print(f"  {i}. {option}")
    
    while True:
        try:
            choice = input(f"\n{Colors.CYAN}Escolha (1-{len(options)}): {Colors.END}").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return idx, options[idx]
            print_error(f"Escolha inválida! Digite um número entre 1 e {len(options)}")
        except ValueError:
            print_error("Por favor, digite um número válido")
        except KeyboardInterrupt:
            raise

def input_with_default(prompt: str, default: str = "") -> str:
    """Input com valor padrão"""
    if default:
        full_prompt = f"{Colors.CYAN}{prompt} [{default}]: {Colors.END}"
    else:
        full_prompt = f"{Colors.CYAN}{prompt}: {Colors.END}"
    
    value = input(full_prompt).strip()
    return value if value else default

def input_multiline(prompt: str) -> str:
    """Input de múltiplas linhas"""
    print(f"\n{Colors.YELLOW}{prompt}{Colors.END}")
    print(f"{Colors.BLUE}(Linha vazia + Enter para terminar){Colors.END}\n")
    
    lines = []
    empty_count = 0
    
    while True:
        line = input()
        if line == "":
            empty_count += 1
            if empty_count >= 2:
                break
        else:
            empty_count = 0
            lines.append(line)
    
    return "\n".join(lines)

def create_exercise_quick():
    """Criação rápida de exercício com presets"""
    
    print_header("ADICIONAR EXERCÍCIO - MODO RÁPIDO")
    
    config = ModuleConfig()
    
    # 1. Escolher preset ou modo manual
    print(f"\n{Colors.BOLD}Escolha o modo de criação:{Colors.END}")
    print(f"  1. {Colors.GREEN}Presets Rápidos{Colors.END} (recomendado para rapidez)")
    print(f"  2. {Colors.BLUE}Configuração Manual{Colors.END} (controlo total)")
    
    mode = input_with_default("Modo (1 ou 2)", "1")
    
    preset_data = None
    if mode == "1":
        presets = config.get_presets()
        preset_list = [(k, v['name']) for k, v in presets.items()]
        _, selected = select_from_list(preset_list, "Escolha o preset:")
        preset_key = selected[0]
        preset_data = presets[preset_key]
        print_success(f"Preset selecionado: {preset_data['name']}")
    
    # 2. Selecionar módulo
    print("\n" + "─" * 70)
    modules = config.get_modules()
    _, selected_module = select_from_list(modules, "Selecione o MÓDULO:")
    module_id = selected_module[0]
    module_name = selected_module[1]
    print_success(f"Módulo: {module_name}")
    
    # 3. Selecionar conceito
    print("\n" + "─" * 70)
    concepts = config.get_concepts(module_id)
    concept_list = [(c['id'], c['name']) for c in concepts]
    _, selected_concept = select_from_list(concept_list, "Selecione o CONCEITO:")
    concept_id = selected_concept[0]
    concept_name = selected_concept[1]
    
    # Obter tags do conceito
    concept_obj = next(c for c in concepts if c['id'] == concept_id)
    auto_tags = concept_obj.get('tags', [])
    print_success(f"Conceito: {concept_name}")
    print_info(f"Tags automáticas: {', '.join(auto_tags)}")
    
    # 4. Gerar ID
    exercise_id = get_next_exercise_id(module_id, concept_id)
    print_success(f"ID do exercício: {exercise_id}")
    
    # 5. Configurações do exercício (preset ou manual)
    print("\n" + "─" * 70)
    
    if preset_data:
        exercise_type = preset_data['type']
        difficulty = preset_data['difficulty']
        points = preset_data['points']
        time_minutes = preset_data['time_minutes']
        parts_count = preset_data['parts']
        
        print_info(f"Tipo: {exercise_type}")
        print_info(f"Dificuldade: {difficulty}/5 ({config.get_difficulty_label(difficulty)})")
        print_info(f"Pontos: {points}")
        print_info(f"Tempo: {time_minutes} min")
        print_info(f"Alíneas: {parts_count}")
        
        # Perguntar se quer ajustar
        adjust = input_with_default("\nAjustar configurações? (s/n)", "n").lower()
        if adjust == 's':
            difficulty = int(input_with_default("Dificuldade (1-5)", str(difficulty)))
            points = float(input_with_default("Pontos", str(points)))
            time_minutes = int(input_with_default("Tempo (min)", str(time_minutes)))
            parts_count = int(input_with_default("Número de alíneas", str(parts_count)))
    else:
        # Modo manual completo
        exercise_types = config.get_exercise_types()
        type_list = [(k, v['name']) for k, v in exercise_types.items()]
        _, selected_type = select_from_list(type_list, "Tipo de exercício:")
        exercise_type = selected_type[0]
        
        difficulty = int(input_with_default("Dificuldade (1-5)", "3"))
        points = float(input_with_default("Pontos", "10"))
        time_minutes = int(input_with_default("Tempo estimado (min)", "15"))
        
        has_parts = input_with_default("Tem múltiplas alíneas? (s/n)", "s").lower() == 's'
        parts_count = int(input_with_default("Quantas alíneas?", "3")) if has_parts else 0
    
    # 6. Tags adicionais
    print("\n" + "─" * 70)
    extra_tags_input = input_with_default("Tags adicionais (separadas por vírgula)", "")
    extra_tags = [tag.strip() for tag in extra_tags_input.split(",")] if extra_tags_input else []
    all_tags = list(set(auto_tags + extra_tags))
    
    # 7. Autor
    author = input_with_default("Nome do autor", "Professor")
    
    # 8. Enunciado
    print("\n" + "─" * 70)
    print_info("Digite o enunciado do exercício")
    statement = input_multiline("ENUNCIADO PRINCIPAL:")
    
    # 9. Alíneas (se aplicável)
    parts = []
    if parts_count > 0:
        print("\n" + "─" * 70)
        print_header(f"ALÍNEAS DO EXERCÍCIO ({parts_count} alíneas)")
        
        for i in range(parts_count):
            print(f"\n{Colors.BOLD}Alínea {chr(97+i)}):{Colors.END}")
            part_text = input_multiline(f"Texto da alínea {chr(97+i)}):")
            
            # Pontos sugeridos
            suggested_points = round(points / parts_count, 1)
            part_points = float(input_with_default(
                f"Pontos da alínea {chr(97+i)})", 
                str(suggested_points)
            ))
            
            parts.append({
                "letter": chr(97+i),
                "text": part_text,
                "points": part_points
            })
    
    # 10. Solução
    print("\n" + "─" * 70)
    has_solution = input_with_default("Adicionar solução? (s/n)", "n").lower() == 's'
    solution_text = ""
    if has_solution:
        solution_text = input_multiline("SOLUÇÃO COMPLETA:")
    
    # 11. Resumo e confirmação
    print_header("RESUMO DO EXERCÍCIO")
    print(f"{Colors.BOLD}ID:{Colors.END} {exercise_id}")
    print(f"{Colors.BOLD}Módulo:{Colors.END} {module_name}")
    print(f"{Colors.BOLD}Conceito:{Colors.END} {concept_name}")
    print(f"{Colors.BOLD}Tipo:{Colors.END} {exercise_type}")
    print(f"{Colors.BOLD}Dificuldade:{Colors.END} {difficulty}/5 ({config.get_difficulty_label(difficulty)})")
    print(f"{Colors.BOLD}Pontos:{Colors.END} {points} | {Colors.BOLD}Tempo:{Colors.END} {time_minutes} min")
    print(f"{Colors.BOLD}Tags:{Colors.END} {', '.join(all_tags)}")
    print(f"{Colors.BOLD}Alíneas:{Colors.END} {parts_count if parts_count > 0 else 'Não'}")
    print(f"{Colors.BOLD}Solução:{Colors.END} {'Sim' if has_solution else 'Não'}")
    
    confirm = input_with_default("\n✓ Confirmar criação? (s/n)", "s").lower()
    
    if confirm != 's':
        print_error("Operação cancelada!")
        return
    
    # 12. Criar ficheiros
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Metadados JSON
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
            "has_multiple_parts": parts_count > 0,
            "parts_count": parts_count,
            "has_graphics": False,
            "requires_packages": ["amsmath", "amssymb"]
        },
        "evaluation": {
            "points": points,
            "time_estimate_minutes": time_minutes,
            "bloom_level": "aplicacao"
        },
        "solution": {
            "available": has_solution,
            "file": f"{exercise_id}_solucao.tex" if has_solution else ""
        },
        "usage": {
            "times_used": 0,
            "last_used": "",
            "contexts": []
        },
        "status": "active"
    }
    
    # Exercício LaTeX
    latex_content = f"""% Exercise ID: {exercise_id}
% Module: {module_name} | Concept: {concept_name}
% Difficulty: {difficulty}/5 ({config.get_difficulty_label(difficulty)}) | Type: {exercise_type}
% Points: {points} | Time: {time_minutes} min
% Tags: {', '.join(all_tags)}
% Author: {author} | Date: {today}
% Status: active

\\exercicio{{{statement}}}
"""
    
    if parts_count > 0:
        latex_content += "\n"
        for part in parts:
            latex_content += f"\\subexercicio{{{part['text']}}}\n\n"
        
        latex_content += "% Evaluation notes:\n"
        for part in parts:
            latex_content += f"% Part {part['letter']}): {part['points']} points\n"
    
    if has_solution:
        latex_content += f"\n% Solution:\n% {solution_text.replace(chr(10), chr(10) + '% ')}\n"
    
    # Salvar ficheiros
    path = BASE_DIR / "matematica" / module_id / concept_id
    path.mkdir(parents=True, exist_ok=True)
    
    # Salvar .tex
    tex_file = path / f"{exercise_id}.tex"
    with open(tex_file, 'w', encoding='utf-8') as f:
        f.write(latex_content)
    print_success(f"Ficheiro criado: {tex_file.relative_to(BASE_DIR.parent)}")
    
    # Salvar .json
    json_file = path / f"{exercise_id}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print_success(f"Metadados criados: {json_file.relative_to(BASE_DIR.parent)}")
    
    # Atualizar índice
    update_index(metadata, tex_file.relative_to(BASE_DIR))
    
    print_header("✓ EXERCÍCIO ADICIONADO COM SUCESSO!")
    print_info(f"ID: {exercise_id}")
    print_info(f"Localização: {path.relative_to(BASE_DIR.parent)}")

def update_index(metadata: Dict, file_path: Path):
    """Atualiza índice central"""
    index_file = BASE_DIR / "index.json"
    
    if index_file.exists():
        with open(index_file, 'r', encoding='utf-8') as f:
            index = json.load(f)
    else:
        index = {
            "database_version": "2.0",
            "last_updated": "",
            "total_exercises": 0,
            "statistics": {
                "by_module": {},
                "by_concept": {},
                "by_difficulty": {},
                "by_type": {}
            },
            "exercises": []
        }
    
    # Adicionar exercício
    exercise_entry = {
        "id": metadata["id"],
        "path": str(file_path).replace("\\", "/"),
        "discipline": "matematica",
        "module": metadata["module"]["id"],
        "module_name": metadata["module"]["name"],
        "concept": metadata["concept"]["id"],
        "concept_name": metadata["concept"]["name"],
        "difficulty": metadata["classification"]["difficulty"],
        "type": metadata["exercise_type"],
        "points": metadata["evaluation"]["points"],
        "tags": metadata["classification"]["tags"],
        "status": metadata["status"]
    }
    
    index["exercises"].append(exercise_entry)
    index["total_exercises"] = len(index["exercises"])
    index["last_updated"] = datetime.now().isoformat()
    
    # Atualizar estatísticas
    module_id = metadata["module"]["id"]
    index["statistics"]["by_module"][module_id] = index["statistics"]["by_module"].get(module_id, 0) + 1
    
    concept_id = metadata["concept"]["id"]
    index["statistics"]["by_concept"][concept_id] = index["statistics"]["by_concept"].get(concept_id, 0) + 1
    
    diff_label = metadata["classification"]["difficulty_label"]
    index["statistics"]["by_difficulty"][diff_label] = index["statistics"]["by_difficulty"].get(diff_label, 0) + 1
    
    ex_type = metadata["exercise_type"]
    index["statistics"]["by_type"][ex_type] = index["statistics"]["by_type"].get(ex_type, 0) + 1
    
    # Salvar índice
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    
    print_success(f"Índice atualizado: {index['total_exercises']} exercícios")

def main():
    """Função principal"""
    try:
        create_exercise_quick()
    except KeyboardInterrupt:
        print_error("\n\nOperação cancelada pelo utilizador!")
    except Exception as e:
        print_error(f"\n\nErro: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
