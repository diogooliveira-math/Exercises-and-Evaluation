"""
Sistema de Gestão de Exercícios - Versão Modular (SEM pontos/tempo)
Para Ensino Modular com controlo granular por conceito
Versão: 2.1
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
            print_info("Execute 'python manage_modules.py' para criar disciplinas/módulos")
            exit(1)
            
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def get_disciplines(self) -> List[Dict]:
        """Retorna lista de disciplinas"""
        disciplines = []
        for key in self.config.keys():
            if key not in ['difficulty_levels', 'exercise_types', 'bloom_taxonomy', 'quick_presets']:
                disc_meta = self.config[key].get('_meta', {})
                disciplines.append({
                    'id': key,
                    'name': disc_meta.get('name', key.title())
                })
        return disciplines
    
    def get_modules(self, discipline: str) -> List[Dict]:
        """Retorna lista de módulos de uma disciplina"""
        modules = []
        if discipline not in self.config:
            return modules
        
        for module_id, module_data in self.config[discipline].items():
            if module_id != '_meta':
                modules.append({
                    'id': module_id,
                    'name': module_data['name']
                })
        return modules
    
    def get_concepts(self, discipline: str, module_id: str) -> List[Dict]:
        """Retorna conceitos de um módulo"""
        if discipline not in self.config:
            return []
        if module_id not in self.config[discipline]:
            return []
        return self.config[discipline][module_id].get('concepts', [])
    
    def get_module_name(self, discipline: str, module_id: str) -> str:
        """Retorna nome do módulo"""
        if discipline in self.config and module_id in self.config[discipline]:
            return self.config[discipline][module_id].get('name', module_id)
        return module_id
    
    def get_concept_name(self, discipline: str, module_id: str, concept_id: str) -> str:
        """Retorna nome do conceito"""
        concepts = self.get_concepts(discipline, module_id)
        for concept in concepts:
            if concept['id'] == concept_id:
                return concept['name']
        return concept_id
    
    def get_difficulty_label(self, level: int) -> str:
        """Retorna label de dificuldade"""
        return self.config['difficulty_levels'][level]['label']
    
    def get_presets(self) -> Dict:
        """Retorna presets rápidos"""
        return self.config.get('quick_presets', {})
    
    def get_exercise_types(self) -> Dict:
        """Retorna tipos de exercício"""
        return self.config.get('exercise_types', {})

def get_next_exercise_id(discipline: str, module_id: str, concept_id: str) -> str:
    """Gera próximo ID para exercício"""
    # Formato: DISC_MODULO_CONCEITO_NNN
    disc_abbr = discipline[:3].upper()
    module_abbr = module_id.replace('_', '').upper()[:8]
    concept_abbr = ''.join([word[0].upper() for word in concept_id.split('_')][:3]).ljust(3, 'X')
    
    # Encontrar exercícios existentes
    path = BASE_DIR / discipline / module_id / concept_id
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    
    existing_files = list(path.glob(f"{disc_abbr}_{module_abbr}_{concept_abbr}_*.tex"))
    
    if not existing_files:
        number = 1
    else:
        numbers = []
        for f in existing_files:
            match = re.search(r'_(\d{3})\.tex$', f.name)
            if match:
                numbers.append(int(match.group(1)))
        number = max(numbers) + 1 if numbers else 1
    
    return f"{disc_abbr}_{module_abbr}_{concept_abbr}_{number:03d}"

def input_with_default(prompt: str, default: str = "") -> str:
    """Input com valor padrão"""
    if default:
        full_prompt = f"{Colors.CYAN}{prompt} [{default}]: {Colors.END}"
    else:
        full_prompt = f"{Colors.CYAN}{prompt}: {Colors.END}"
    
    value = input(full_prompt).strip()
    return value if value else default

def input_multiline(prompt: str) -> str:
    """Input de múltiplas linhas (termina com duas linhas vazias)"""
    print(f"\n{Colors.YELLOW}{prompt}{Colors.END}")
    print(f"{Colors.BLUE}(Pressione Enter duas vezes para terminar){Colors.END}\n")
    
    lines = []
    empty_count = 0
    
    while True:
        try:
            line = input()
            if line == "":
                empty_count += 1
                if empty_count >= 2:
                    break
                lines.append(line)
            else:
                empty_count = 0
                lines.append(line)
        except EOFError:
            break
    
    # Remove trailing empty lines
    while lines and lines[-1] == "":
        lines.pop()
    
    return "\n".join(lines)

def select_from_list(options: List, prompt: str) -> str:
    """Menu de seleção genérico"""
    print(f"\n{Colors.YELLOW}{prompt}{Colors.END}")
    for i, option in enumerate(options, 1):
        if isinstance(option, dict):
            name = option.get('name', option.get('id', ''))
            print(f"  {i}. {name}")
        else:
            print(f"  {i}. {option}")
    
    while True:
        choice = input(f"\n{Colors.CYAN}Escolha (1-{len(options)}): {Colors.END}").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                if isinstance(options[idx], dict):
                    return options[idx].get('id', options[idx].get('name', ''))
                return options[idx]
        except ValueError:
            pass
        print_error(f"Escolha inválida! Digite um número entre 1 e {len(options)}")

def create_exercise_quick():
    """Wizard rápido para criar exercício (SEM pontos/tempo)"""
    
    print_header("🎯 ADICIONAR NOVO EXERCÍCIO")
    
    config = ModuleConfig()
    
    # 1. Escolher disciplina
    disciplines = config.get_disciplines()
    if not disciplines:
        print_error("Nenhuma disciplina encontrada!")
        print_info("Execute 'python manage_modules.py' para criar disciplinas")
        return
    
    print_info("Disciplinas disponíveis:")
    discipline = select_from_list(disciplines, "Escolha a disciplina:")
    
    # 2. Escolher módulo
    modules = config.get_modules(discipline)
    if not modules:
        print_error(f"Nenhum módulo encontrado em '{discipline}'!")
        print_info("Execute 'python manage_modules.py' para criar módulos")
        return
    
    print_info("\nMódulos disponíveis:")
    module_id = select_from_list(modules, "Escolha o módulo:")
    
    # 3. Escolher conceito
    concepts = config.get_concepts(discipline, module_id)
    if not concepts:
        print_error(f"Nenhum conceito encontrado no módulo '{module_id}'!")
        print_info("Execute 'python manage_modules.py' para adicionar conceitos")
        return
    
    print_info("\nConceitos disponíveis:")
    concept_options = [{'id': c['id'], 'name': c['name']} for c in concepts]
    concept_id = select_from_list(concept_options, "Escolha o conceito:")
    
    # 4. Gerar ID automaticamente
    exercise_id = get_next_exercise_id(discipline, module_id, concept_id)
    print_success(f"ID do exercício: {exercise_id}")
    
    # 5. Tipo de exercício
    print("\n" + "─" * 70)
    exercise_types = config.get_exercise_types()
    type_options = [{'id': k, 'name': v['name']} for k, v in exercise_types.items()]
    exercise_type = select_from_list(type_options, "Tipo de exercício:")
    
    # 6. Preset rápido?
    print("\n" + "─" * 70)
    use_preset = input_with_default("Usar preset rápido? (s/n)", "s").lower()
    
    if use_preset == 's':
        presets = config.get_presets()
        print_info("\nPresets disponíveis:")
        preset_list = []
        for key, preset in presets.items():
            diff = preset.get('difficulty', 3)
            diff_label = config.get_difficulty_label(diff)
            preset_list.append({
                'id': key,
                'name': f"{preset['name']} - {diff_label}"
            })
        
        preset_key = select_from_list(preset_list, "Escolha o preset:")
        preset = presets[preset_key]
        
        difficulty = preset['difficulty']
        bloom_level = preset.get('bloom', 'aplicacao')
        print_success(f"Preset aplicado: {config.get_difficulty_label(difficulty)}")
    else:
        # Dificuldade manual
        print("\n" + "─" * 70)
        diff_options = []
        for level in range(1, 6):
            label = config.get_difficulty_label(level)
            diff_options.append({'id': str(level), 'name': f"{level} - {label}"})
        
        diff_choice = select_from_list(diff_options, "Dificuldade:")
        difficulty = int(diff_choice)
        
        # Bloom manual
        print("\n" + "─" * 70)
        bloom_taxonomy = config.config.get('bloom_taxonomy', {})
        bloom_options = [{'id': k, 'name': v['description']} for k, v in bloom_taxonomy.items()]
        bloom_level = select_from_list(bloom_options, "Nível de Bloom:")
    
    # 7. Tags
    print("\n" + "─" * 70)
    concept_data = next((c for c in concepts if c['id'] == concept_id), {})
    auto_tags = concept_data.get('tags', [])
    
    if auto_tags:
        print_info(f"Tags automáticas: {', '.join(auto_tags)}")
    
    additional_tags = input_with_default("Tags adicionais (separadas por vírgula)", "")
    if additional_tags:
        tags = auto_tags + [t.strip() for t in additional_tags.split(',')]
    else:
        tags = auto_tags
    
    # 8. Autor
    print("\n" + "─" * 70)
    author = input_with_default("Nome do autor", "Professor")
    
    # 9. Enunciado
    print("\n" + "─" * 70)
    statement = input_multiline("Digite o ENUNCIADO PRINCIPAL do exercício:")
    
    # 10. Múltiplas alíneas?
    print("\n" + "─" * 70)
    has_parts = input_with_default("Tem múltiplas alíneas? (s/n)", "n").lower() == 's'
    
    parts = []
    parts_count = 0
    if has_parts:
        parts_count = int(input_with_default("Quantas alíneas?", "3"))
        for i in range(parts_count):
            print(f"\n{Colors.YELLOW}Alínea {chr(97+i)}):{Colors.END}")
            part_text = input_multiline(f"Texto da alínea {chr(97+i)}):")
            parts.append({"letter": chr(97+i), "text": part_text})
    
    # 11. Solução?
    print("\n" + "─" * 70)
    has_solution = input_with_default("Adicionar solução agora? (s/n)", "n").lower() == 's'
    solution_text = ""
    if has_solution:
        solution_text = input_multiline("Digite a SOLUÇÃO completa:")
    
    # 12. Confirmar
    print("\n" + "─" * 70)
    print_header("📋 RESUMO DO EXERCÍCIO")
    print(f"ID: {exercise_id}")
    print(f"Disciplina: {discipline}")
    print(f"Módulo: {module_id}")
    print(f"Conceito: {concept_id}")
    print(f"Tipo: {exercise_type}")
    print(f"Dificuldade: {difficulty} ({config.get_difficulty_label(difficulty)})")
    print(f"Bloom: {bloom_level}")
    print(f"Tags: {', '.join(tags) if tags else 'Nenhuma'}")
    print(f"Alíneas: {parts_count if has_parts else 'Não'}")
    print(f"Solução: {'Sim' if has_solution else 'Não'}")
    
    confirm = input_with_default("\nConfirmar criação? (s/n)", "s").lower()
    if confirm != 's':
        print_error("Operação cancelada!")
        return
    
    # 13. Criar ficheiros
    today = datetime.now().strftime("%Y-%m-%d")
    
    module_name = config.get_module_name(discipline, module_id)
    concept_name = config.get_concept_name(discipline, module_id, concept_id)
    
    # Metadados JSON (SEM points e time)
    metadata = {
        "id": exercise_id,
        "version": "1.0",
        "created": today,
        "modified": today,
        "author": author,
        "classification": {
            "discipline": discipline,
            "module": module_id,
            "module_name": module_name,
            "concept": concept_id,
            "concept_name": concept_name,
            "tags": tags,
            "difficulty": difficulty,
            "difficulty_label": config.get_difficulty_label(difficulty)
        },
        "exercise_type": exercise_type,
        "content": {
            "has_multiple_parts": has_parts,
            "parts_count": parts_count,
            "has_graphics": False,
            "requires_packages": ["amsmath", "amssymb"]
        },
        "evaluation": {
            "bloom_level": bloom_level
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
    
    # LaTeX (SEM Points e Time)
    latex_content = f"""% Exercise ID: {exercise_id}
% Module: {module_name} | Concept: {concept_name}
% Difficulty: {difficulty}/5 ({config.get_difficulty_label(difficulty)}) | Type: {exercise_type}
% Tags: {', '.join(tags)}
% Author: {author} | Date: {today}
% Status: active

\\exercicio{{{statement}}}
"""
    
    if has_parts:
        latex_content += "\n"
        for part in parts:
            latex_content += f"\\subexercicio{{{part['text']}}}\n\n"
    
    if has_solution:
        latex_content += f"\n% Solution:\n% \\begin{{solucao}}\n% {solution_text.replace(chr(10), chr(10) + '% ')}\n% \\end{{solucao}}\n"
    
    # Salvar ficheiros
    path = BASE_DIR / discipline / module_id / concept_id
    path.mkdir(parents=True, exist_ok=True)
    
    tex_file = path / f"{exercise_id}.tex"
    with open(tex_file, 'w', encoding='utf-8') as f:
        f.write(latex_content)
    print_success(f"Ficheiro .tex criado: {tex_file.name}")
    
    json_file = path / f"{exercise_id}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print_success(f"Metadados .json criados: {json_file.name}")
    
    # Atualizar índice
    update_index(metadata, str(tex_file.relative_to(BASE_DIR)))
    
    print_header("✅ EXERCÍCIO ADICIONADO COM SUCESSO!")
    print_info(f"Localização: {discipline}/{module_id}/{concept_id}/{exercise_id}")

def update_index(metadata: Dict, file_path: str):
    """Atualiza índice central (SEM points)"""
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
                "by_discipline": {},
                "by_module": {},
                "by_concept": {},
                "by_difficulty": {},
                "by_type": {}
            },
            "exercises": []
        }
    
    # Adicionar exercício (inclui points quando disponível)
    exercise_entry = {
        "id": metadata["id"],
        "path": file_path.replace("\\", "/"),
        "discipline": metadata["classification"]["discipline"],
        "module": metadata["classification"]["module"],
        "module_name": metadata["classification"]["module_name"],
        "concept": metadata["classification"]["concept"],
        "concept_name": metadata["classification"]["concept_name"],
        "difficulty": metadata["classification"]["difficulty"],
        "type": metadata["exercise_type"],
        "tags": metadata["classification"]["tags"],
        "points": metadata.get("evaluation", {}).get("points", 0),
        "status": metadata["status"]
    }
    
    index["exercises"].append(exercise_entry)
    index["total_exercises"] = len(index["exercises"])
    index["last_updated"] = datetime.now().isoformat()
    
    # Estatísticas
    disc = metadata["classification"]["discipline"]
    index["statistics"]["by_discipline"][disc] = index["statistics"]["by_discipline"].get(disc, 0) + 1
    
    mod = metadata["classification"]["module"]
    index["statistics"]["by_module"][mod] = index["statistics"]["by_module"].get(mod, 0) + 1
    
    conc = metadata["classification"]["concept_name"]
    index["statistics"]["by_concept"][conc] = index["statistics"]["by_concept"].get(conc, 0) + 1
    
    diff = metadata["classification"]["difficulty_label"]
    index["statistics"]["by_difficulty"][diff] = index["statistics"]["by_difficulty"].get(diff, 0) + 1
    
    ex_type = metadata["exercise_type"]
    index["statistics"]["by_type"][ex_type] = index["statistics"]["by_type"].get(ex_type, 0) + 1
    
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    
    print_success(f"Índice atualizado: {index['total_exercises']} exercícios no total")

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
