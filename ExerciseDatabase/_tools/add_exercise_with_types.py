"""
Sistema de Gestão de Exercícios com TIPOS - Versão 3.0
Hierarquia: disciplina/tema/conceito/tipo/exercicio.tex
Usa JSON por diretório (Opção A)
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

def get_exercise_types_for_concept(discipline: str, module_id: str, concept_id: str) -> List[Dict]:
    """
    Retorna tipos de exercício disponíveis para um conceito.
    Lê os diretórios existentes e seus metadata.json
    """
    path = BASE_DIR / discipline / module_id / concept_id
    
    if not path.exists():
        return []
    
    types = []
    for item in path.iterdir():
        if item.is_dir():
            metadata_file = item / "metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    types.append({
                        'id': metadata['tipo'],
                        'name': metadata['tipo_nome'],
                        'description': metadata['descricao'],
                        'path': item
                    })
    
    return types

def create_new_exercise_type(discipline: str, module_id: str, concept_id: str, config: ModuleConfig):
    """Cria um novo tipo de exercício"""
    print_header("🆕 CRIAR NOVO TIPO DE EXERCÍCIO")
    
    tipo_id = input(f"{Colors.CYAN}ID do tipo (ex: determinacao_analitica): {Colors.END}").strip()
    tipo_nome = input(f"{Colors.CYAN}Nome do tipo: {Colors.END}").strip()
    descricao = input(f"{Colors.CYAN}Descrição: {Colors.END}").strip()
    
    # Características
    print(f"\n{Colors.YELLOW}Características deste tipo:{Colors.END}")
    requer_calculo = input(f"{Colors.CYAN}Requer cálculo? (s/n): {Colors.END}").lower() == 's'
    requer_grafico = input(f"{Colors.CYAN}Requer gráfico? (s/n): {Colors.END}").lower() == 's'
    
    # Tags automáticas do tipo
    tags_input = input(f"{Colors.CYAN}Tags automáticas para este tipo (separadas por vírgula): {Colors.END}")
    tags_tipo = [t.strip() for t in tags_input.split(',') if t.strip()]
    
    concept_name = config.get_concept_name(discipline, module_id, concept_id)
    module_name = config.get_module_name(discipline, module_id)
    
    # Criar diretório e metadata
    tipo_path = BASE_DIR / discipline / module_id / concept_id / tipo_id
    tipo_path.mkdir(parents=True, exist_ok=True)
    
    metadata = {
        "tipo": tipo_id,
        "tipo_nome": tipo_nome,
        "conceito": concept_id,
        "conceito_nome": concept_name,
        "tema": module_id,
        "tema_nome": module_name,
        "disciplina": discipline,
        "descricao": descricao,
        "tags_tipo": tags_tipo,
        "caracteristicas": {
            "requer_calculo": requer_calculo,
            "requer_grafico": requer_grafico
        },
        "dificuldade_sugerida": {
            "min": 2,
            "max": 4
        },
        "exercicios": []
    }
    
    metadata_file = tipo_path / "metadata.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print_success(f"Tipo criado: {tipo_nome}")
    print_info(f"Localização: {tipo_path.relative_to(BASE_DIR)}")
    
    return tipo_id

def get_next_exercise_id(discipline: str, module_id: str, concept_id: str, tipo_id: str) -> str:
    """Gera próximo ID para exercício (agora com tipo)"""
    # Formato: DISC_MODULO_CONCEITO_TIPO_NNN
    disc_abbr = discipline[:3].upper()
    module_abbr = module_id.replace('_', '').upper()[:8]
    concept_abbr = ''.join([word[0].upper() for word in concept_id.split('-') if word][:3]).ljust(3, 'X')
    tipo_abbr = ''.join([word[0].upper() for word in tipo_id.split('_')][:3]).ljust(3, 'X')
    
    # Encontrar exercícios existentes NO TIPO
    path = BASE_DIR / discipline / module_id / concept_id / tipo_id
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    
    existing_files = list(path.glob(f"{disc_abbr}_{module_abbr}_{concept_abbr}_{tipo_abbr}_*.tex"))
    
    if not existing_files:
        number = 1
    else:
        numbers = []
        for f in existing_files:
            match = re.search(r'_(\d{3})\.tex$', f.name)
            if match:
                numbers.append(int(match.group(1)))
        number = max(numbers) + 1 if numbers else 1
    
    return f"{disc_abbr}_{module_abbr}_{concept_abbr}_{tipo_abbr}_{number:03d}"

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
            desc = option.get('description', '')
            if desc:
                print(f"  {i}. {name}")
                print(f"     {Colors.BLUE}{desc}{Colors.END}")
            else:
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

def update_type_metadata_inline(tipo_path: Path, exercise_id: str, exercise_metadata: Dict):
    """Atualiza metadata.json do tipo com metadados do exercício inline"""
    metadata_file = tipo_path / "metadata.json"
    
    if metadata_file.exists():
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
    else:
        metadata = {"exercicios": {}}
    
    # Garantir que exercicios é um dict
    if not isinstance(metadata.get('exercicios'), dict):
        metadata['exercicios'] = {}
    
    # Adicionar exercício com metadados inline
    metadata['exercicios'][exercise_id] = {
        "created": exercise_metadata.get('created', datetime.now().strftime("%Y-%m-%d")),
        "modified": datetime.now().strftime("%Y-%m-%d"),
        "author": exercise_metadata.get('author', 'Professor'),
        "difficulty": exercise_metadata['classification']['difficulty'],
        "points": exercise_metadata.get('evaluation', {}).get('points', 0),
        "time_estimate_minutes": exercise_metadata.get('evaluation', {}).get('time_estimate_minutes', 0),
        "has_multiple_parts": exercise_metadata['content']['has_multiple_parts'],
        "parts_count": exercise_metadata['content']['parts_count'],
        "tags": exercise_metadata['classification']['tags'],
        "status": exercise_metadata.get('status', 'active')
    }
    
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

def create_exercise_with_types():
    """Wizard para criar exercício com suporte a TIPOS"""
    
    print_header("🎯 ADICIONAR NOVO EXERCÍCIO (com Tipos)")
    
    config = ModuleConfig()
    
    # 1. Escolher disciplina
    disciplines = config.get_disciplines()
    if not disciplines:
        print_error("Nenhuma disciplina encontrada!")
        return
    
    print_info("Disciplinas disponíveis:")
    discipline = select_from_list(disciplines, "Escolha a disciplina:")
    
    # 2. Escolher módulo
    modules = config.get_modules(discipline)
    if not modules:
        print_error(f"Nenhum módulo encontrado em '{discipline}'!")
        return
    
    print_info("\nMódulos disponíveis:")
    module_id = select_from_list(modules, "Escolha o módulo:")
    
    # 3. Escolher conceito
    concepts = config.get_concepts(discipline, module_id)
    if not concepts:
        print_error(f"Nenhum conceito encontrado no módulo '{module_id}'!")
        return
    
    print_info("\nConceitos disponíveis:")
    concept_options = [{'id': c['id'], 'name': c['name']} for c in concepts]
    concept_id = select_from_list(concept_options, "Escolha o conceito:")
    
    # 4. NOVO: Escolher ou criar tipo
    print("\n" + "─" * 70)
    exercise_types = get_exercise_types_for_concept(discipline, module_id, concept_id)
    
    if exercise_types:
        print_info(f"\n{len(exercise_types)} tipos de exercício disponíveis:")
        exercise_types.append({'id': '__novo__', 'name': '➕ Criar novo tipo', 'description': ''})
        tipo_choice = select_from_list(exercise_types, "Escolha o tipo de exercício:")
        
        if tipo_choice == '__novo__':
            tipo_id = create_new_exercise_type(discipline, module_id, concept_id, config)
        else:
            tipo_id = tipo_choice
    else:
        print_warning("Nenhum tipo de exercício encontrado para este conceito.")
        criar = input_with_default("Criar primeiro tipo? (s/n)", "s").lower()
        if criar == 's':
            tipo_id = create_new_exercise_type(discipline, module_id, concept_id, config)
        else:
            print_error("Cancelado. Crie tipos primeiro!")
            return
    
    # Carregar metadata do tipo
    tipo_path = BASE_DIR / discipline / module_id / concept_id / tipo_id
    tipo_metadata_file = tipo_path / "metadata.json"
    with open(tipo_metadata_file, 'r', encoding='utf-8') as f:
        tipo_metadata = json.load(f)
    
    tipo_nome = tipo_metadata['tipo_nome']
    tags_auto_tipo = tipo_metadata.get('tags_tipo', [])
    
    print_success(f"Tipo selecionado: {tipo_nome}")
    
    # 5. Gerar ID automaticamente (agora com tipo)
    exercise_id = get_next_exercise_id(discipline, module_id, concept_id, tipo_id)
    print_success(f"ID do exercício: {exercise_id}")
    
    # 6. Formato do exercício
    print("\n" + "─" * 70)
    format_types = config.get_exercise_types()
    format_options = [{'id': k, 'name': v['name']} for k, v in format_types.items()]
    exercise_format = select_from_list(format_options, "Formato do exercício:")
    
    # 7. Dificuldade
    print("\n" + "─" * 70)
    diff_sugerida = tipo_metadata.get('dificuldade_sugerida', {})
    diff_min = diff_sugerida.get('min', 2)
    diff_max = diff_sugerida.get('max', 4)
    print_info(f"Dificuldade sugerida para este tipo: {diff_min}-{diff_max}")
    
    diff_options = []
    for level in range(1, 6):
        label = config.get_difficulty_label(level)
        diff_options.append({'id': str(level), 'name': f"{level} - {label}"})
    
    diff_choice = select_from_list(diff_options, "Dificuldade:")
    difficulty = int(diff_choice)
    
    # 8. Tags (automaticamente do tipo + conceito)
    print("\n" + "─" * 70)
    concept_data = next((c for c in concepts if c['id'] == concept_id), {})
    auto_tags_concept = concept_data.get('tags', [])
    
    all_auto_tags = list(set(auto_tags_concept + tags_auto_tipo))
    
    print_info(f"Tags automáticas: {', '.join(all_auto_tags)}")
    additional_tags = input_with_default("Tags adicionais (separadas por vírgula)", "")
    if additional_tags:
        tags = all_auto_tags + [t.strip() for t in additional_tags.split(',')]
    else:
        tags = all_auto_tags
    
    # 9. Autor
    print("\n" + "─" * 70)
    author = input_with_default("Nome do autor", "Professor")
    
    # 10. Enunciado
    print("\n" + "─" * 70)
    statement = input_multiline("Digite o ENUNCIADO PRINCIPAL do exercício:")
    
    # 11. Múltiplas alíneas?
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
    
    # 12. Solução?
    print("\n" + "─" * 70)
    has_solution = input_with_default("Adicionar solução agora? (s/n)", "n").lower() == 's'
    solution_text = ""
    if has_solution:
        solution_text = input_multiline("Digite a SOLUÇÃO completa:")
    
    # 13. Confirmar
    print("\n" + "─" * 70)
    print_header("📋 RESUMO DO EXERCÍCIO")
    print(f"ID: {exercise_id}")
    print(f"Disciplina: {discipline}")
    print(f"Módulo: {module_id}")
    print(f"Conceito: {concept_id}")
    print(f"TIPO: {tipo_nome}")
    print(f"Formato: {exercise_format}")
    print(f"Dificuldade: {difficulty} ({config.get_difficulty_label(difficulty)})")
    print(f"Tags: {', '.join(tags) if tags else 'Nenhuma'}")
    print(f"Alíneas: {parts_count if has_parts else 'Não'}")
    print(f"Solução: {'Sim' if has_solution else 'Não'}")
    
    confirm = input_with_default("\nConfirmar criação? (s/n)", "s").lower()
    if confirm != 's':
        print_error("Operação cancelada!")
        return
    
    # 14. Criar ficheiros
    today = datetime.now().strftime("%Y-%m-%d")
    
    module_name = config.get_module_name(discipline, module_id)
    concept_name = config.get_concept_name(discipline, module_id, concept_id)
    
    # Metadados JSON
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
            "tipo": tipo_id,
            "tipo_nome": tipo_nome,
            "tags": tags,
            "difficulty": difficulty,
            "difficulty_label": config.get_difficulty_label(difficulty)
        },
        "exercise_type": exercise_format,
        "content": {
            "has_multiple_parts": has_parts,
            "parts_count": parts_count,
            "has_graphics": tipo_metadata['caracteristicas'].get('requer_grafico', False),
            "requires_packages": ["amsmath", "amssymb"]
        },
        "evaluation": {
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
    
    # LaTeX
    latex_content = f"""% Exercise ID: {exercise_id}
% Module: {module_name} | Concept: {concept_name} | Type: {tipo_nome}
% Difficulty: {difficulty}/5 ({config.get_difficulty_label(difficulty)}) | Format: {exercise_format}
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
    
    # Salvar ficheiro .tex NO DIRETÓRIO DO TIPO
    tex_file = tipo_path / f"{exercise_id}.tex"
    with open(tex_file, 'w', encoding='utf-8') as f:
        f.write(latex_content)
    print_success(f"Ficheiro .tex criado: {tex_file.name}")
    
    # Atualizar metadata do tipo (sem JSON individual)
    update_type_metadata_inline(tipo_path, exercise_id, metadata)
    print_success(f"Metadata do tipo atualizado")
    
    # Atualizar índice global
    update_index(metadata, str(tex_file.relative_to(BASE_DIR)))
    
    print_header("✅ EXERCÍCIO ADICIONADO COM SUCESSO!")
    print_info(f"Localização: {discipline}/{module_id}/{concept_id}/{tipo_id}/{exercise_id}")

def update_index(metadata: Dict, file_path: str):
    """Atualiza índice central (agora com tipo)"""
    index_file = BASE_DIR / "index.json"
    
    if index_file.exists():
        with open(index_file, 'r', encoding='utf-8') as f:
            index = json.load(f)
    else:
        index = {
            "database_version": "3.0",
            "last_updated": "",
            "total_exercises": 0,
            "statistics": {
                "by_discipline": {},
                "by_module": {},
                "by_concept": {},
                "by_type": {},
                "by_difficulty": {},
                "by_format": {}
            },
            "exercises": []
        }
    
    # Adicionar exercício
    exercise_entry = {
        "id": metadata["id"],
        "path": file_path.replace("\\", "/"),
        "discipline": metadata["classification"]["discipline"],
        "module": metadata["classification"]["module"],
        "module_name": metadata["classification"]["module_name"],
        "concept": metadata["classification"]["concept"],
        "concept_name": metadata["classification"]["concept_name"],
        "tipo": metadata["classification"]["tipo"],
        "tipo_nome": metadata["classification"]["tipo_nome"],
        "difficulty": metadata["classification"]["difficulty"],
        "format": metadata["exercise_type"],
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
    
    tipo = metadata["classification"]["tipo_nome"]
    index["statistics"]["by_type"][tipo] = index["statistics"]["by_type"].get(tipo, 0) + 1
    
    diff = metadata["classification"]["difficulty_label"]
    index["statistics"]["by_difficulty"][diff] = index["statistics"]["by_difficulty"].get(diff, 0) + 1
    
    ex_format = metadata["exercise_type"]
    index["statistics"]["by_format"][ex_format] = index["statistics"]["by_format"].get(ex_format, 0) + 1
    
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    
    print_success(f"Índice atualizado: {index['total_exercises']} exercícios no total")

def main():
    """Função principal"""
    try:
        create_exercise_with_types()
    except KeyboardInterrupt:
        print_error("\n\nOperação cancelada pelo utilizador!")
    except Exception as e:
        print_error(f"\n\nErro: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
