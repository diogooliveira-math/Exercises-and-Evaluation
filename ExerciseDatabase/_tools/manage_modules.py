"""
Sistema de Gestão de Módulos e Disciplinas
Permite criar, editar e remover disciplinas, módulos e conceitos
Versão: 2.1
"""

import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# Cores
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

BASE_DIR = Path(__file__).parent.parent
CONFIG_FILE = BASE_DIR / "modules_config.yaml"

def load_config() -> Dict:
    """Carrega configuração"""
    if not CONFIG_FILE.exists():
        return create_base_config()
    
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def save_config(config: Dict):
    """Salva configuração"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
    print_success(f"Configuração salva em {CONFIG_FILE.name}")

def create_base_config() -> Dict:
    """Cria configuração base"""
    return {
        "difficulty_levels": {
            1: {"label": "Muito Fácil", "description": "Aplicação direta de conceitos básicos", "color": "#4CAF50"},
            2: {"label": "Fácil", "description": "Exercícios de consolidação simples", "color": "#8BC34A"},
            3: {"label": "Médio", "description": "Requer compreensão sólida dos conceitos", "color": "#FFC107"},
            4: {"label": "Difícil", "description": "Problemas complexos, múltiplos conceitos", "color": "#FF9800"},
            5: {"label": "Muito Difícil", "description": "Desafios avançados, pensamento crítico", "color": "#F44336"}
        },
        "exercise_types": {
            "desenvolvimento": {
                "name": "Desenvolvimento",
                "description": "Resposta aberta com resolução completa",
                "latex_macro": "\\exercicioDesenvolvimento"
            },
            "escolha_multipla": {
                "name": "Escolha Múltipla",
                "description": "4 opções com uma correta",
                "latex_macro": "\\exercicioEscolha"
            },
            "verdadeiro_falso": {
                "name": "Verdadeiro ou Falso",
                "description": "Afirmações para classificar",
                "latex_macro": "\\exercicioVerdadeiroFalso"
            },
            "resposta_curta": {
                "name": "Resposta Curta",
                "description": "Resposta breve ou valor numérico",
                "latex_macro": "\\exercicioRespostaCurta"
            }
        },
        "bloom_taxonomy": {
            "conhecimento": {"level": 1, "description": "Recordar factos, termos, conceitos básicos"},
            "compreensao": {"level": 2, "description": "Explicar ideias ou conceitos"},
            "aplicacao": {"level": 3, "description": "Usar informação em novas situações"},
            "analise": {"level": 4, "description": "Estabelecer conexões entre ideias"},
            "sintese": {"level": 5, "description": "Criar ou gerar novos padrões"},
            "avaliacao": {"level": 6, "description": "Julgar valor de ideias ou materiais"}
        },
        "quick_presets": {
            "questao_aula": {
                "name": "Questão de Aula (10 min)",
                "type": "desenvolvimento",
                "difficulty": 2,
                "points": 10,
                "time_minutes": 10,
                "parts": 2
            },
            "exercicio_ficha": {
                "name": "Exercício de Ficha (15 min)",
                "type": "desenvolvimento",
                "difficulty": 3,
                "points": 15,
                "time_minutes": 15,
                "parts": 3
            },
            "teste_rapido": {
                "name": "Teste Rápido - Escolha Múltipla",
                "type": "escolha_multipla",
                "difficulty": 2,
                "points": 5,
                "time_minutes": 3,
                "parts": 1
            },
            "desafio": {
                "name": "Desafio Avançado (30 min)",
                "type": "desenvolvimento",
                "difficulty": 5,
                "points": 20,
                "time_minutes": 30,
                "parts": 4
            }
        }
    }

def input_with_default(prompt: str, default: str = "") -> str:
    """Input com valor padrão"""
    if default:
        full_prompt = f"{Colors.CYAN}{prompt} [{default}]: {Colors.END}"
    else:
        full_prompt = f"{Colors.CYAN}{prompt}: {Colors.END}"
    
    value = input(full_prompt).strip()
    return value if value else default

def input_list(prompt: str) -> List[str]:
    """Input de lista separada por vírgulas"""
    value = input_with_default(prompt, "")
    if not value:
        return []
    return [item.strip() for item in value.split(",")]

def create_discipline():
    """Criar nova disciplina"""
    print_header("CRIAR NOVA DISCIPLINA")
    
    config = load_config()
    
    # Mostrar disciplinas existentes
    if any(key not in ['difficulty_levels', 'exercise_types', 'bloom_taxonomy', 'quick_presets'] 
           for key in config.keys()):
        print_info("Disciplinas existentes:")
        for key in config.keys():
            if key not in ['difficulty_levels', 'exercise_types', 'bloom_taxonomy', 'quick_presets']:
                print(f"  • {key}")
        print()
    
    # Dados da disciplina
    disc_id = input_with_default("ID da disciplina (ex: matematica, fisica, teste)", "").lower().replace(" ", "_")
    if not disc_id:
        print_error("ID é obrigatório!")
        return
    
    if disc_id in config:
        print_error(f"Disciplina '{disc_id}' já existe!")
        return
    
    disc_name = input_with_default("Nome completo da disciplina", disc_id.title())
    disc_description = input_with_default("Descrição breve", f"Exercícios de {disc_name}")
    
    # Criar disciplina
    config[disc_id] = {
        "_meta": {
            "name": disc_name,
            "description": disc_description,
            "created": datetime.now().strftime("%Y-%m-%d"),
            "total_modules": 0
        }
    }
    
    save_config(config)
    
    # Criar pasta
    disc_path = BASE_DIR / disc_id
    disc_path.mkdir(exist_ok=True)
    print_success(f"Pasta criada: {disc_path}")
    
    print_header(f"✓ DISCIPLINA '{disc_name}' CRIADA!")
    print_info(f"ID: {disc_id}")
    print_info("Próximo passo: Adicione módulos com 'Criar Módulo'")

def create_module():
    """Criar novo módulo em uma disciplina"""
    print_header("CRIAR NOVO MÓDULO")
    
    config = load_config()
    
    # Selecionar disciplina
    disciplines = [k for k in config.keys() 
                  if k not in ['difficulty_levels', 'exercise_types', 'bloom_taxonomy', 'quick_presets']]
    
    if not disciplines:
        print_error("Nenhuma disciplina encontrada! Crie uma disciplina primeiro.")
        return
    
    print_info("Disciplinas disponíveis:")
    for i, disc in enumerate(disciplines, 1):
        disc_name = config[disc].get('_meta', {}).get('name', disc)
        print(f"  {i}. {disc_name} ({disc})")
    
    choice = input_with_default(f"\nEscolha a disciplina (1-{len(disciplines)})", "1")
    try:
        disc_id = disciplines[int(choice) - 1]
    except (ValueError, IndexError):
        print_error("Escolha inválida!")
        return
    
    print()
    print_info(f"Criando módulo em: {config[disc_id]['_meta']['name']}")
    
    # Dados do módulo
    module_id = input_with_default("ID do módulo (ex: A10_funcoes, M01_introducao)", "").lower().replace(" ", "_")
    if not module_id:
        print_error("ID é obrigatório!")
        return
    
    if module_id in config[disc_id]:
        print_error(f"Módulo '{module_id}' já existe nesta disciplina!")
        return
    
    module_name = input_with_default("Nome do módulo", module_id.replace("_", " ").title())
    module_description = input_with_default("Descrição", "")
    duration_hours = input_with_default("Duração estimada (horas)", "20")
    
    # Criar módulo
    config[disc_id][module_id] = {
        "name": module_name,
        "description": module_description,
        "duration_hours": int(duration_hours),
        "created": datetime.now().strftime("%Y-%m-%d"),
        "concepts": []
    }
    
    # Atualizar meta
    if '_meta' in config[disc_id]:
        config[disc_id]['_meta']['total_modules'] = len([k for k in config[disc_id].keys() if k != '_meta'])
    
    save_config(config)
    
    # Criar pasta
    module_path = BASE_DIR / disc_id / module_id
    module_path.mkdir(parents=True, exist_ok=True)
    print_success(f"Pasta criada: {module_path}")
    
    print_header(f"✓ MÓDULO '{module_name}' CRIADO!")
    print_info(f"Disciplina: {disc_id}")
    print_info(f"ID do Módulo: {module_id}")
    print_info("Próximo passo: Adicione conceitos ao módulo")

def add_concept():
    """Adicionar conceito a um módulo"""
    print_header("ADICIONAR CONCEITO AO MÓDULO")
    
    config = load_config()
    
    # Selecionar disciplina
    disciplines = [k for k in config.keys() 
                  if k not in ['difficulty_levels', 'exercise_types', 'bloom_taxonomy', 'quick_presets']]
    
    if not disciplines:
        print_error("Nenhuma disciplina encontrada!")
        return
    
    print_info("Disciplinas disponíveis:")
    for i, disc in enumerate(disciplines, 1):
        disc_name = config[disc].get('_meta', {}).get('name', disc)
        print(f"  {i}. {disc_name}")
    
    choice = input_with_default(f"\nEscolha a disciplina (1-{len(disciplines)})", "1")
    try:
        disc_id = disciplines[int(choice) - 1]
    except (ValueError, IndexError):
        print_error("Escolha inválida!")
        return
    
    # Selecionar módulo
    modules = [k for k in config[disc_id].keys() if k != '_meta']
    
    if not modules:
        print_error(f"Nenhum módulo em '{disc_id}'! Crie um módulo primeiro.")
        return
    
    print(f"\n{Colors.BLUE}Módulos em {disc_id}:{Colors.END}")
    for i, mod in enumerate(modules, 1):
        mod_name = config[disc_id][mod]['name']
        concepts_count = len(config[disc_id][mod].get('concepts', []))
        print(f"  {i}. {mod_name} ({concepts_count} conceitos)")
    
    choice = input_with_default(f"\nEscolha o módulo (1-{len(modules)})", "1")
    try:
        module_id = modules[int(choice) - 1]
    except (ValueError, IndexError):
        print_error("Escolha inválida!")
        return
    
    print()
    print_info(f"Adicionando conceito em: {config[disc_id][module_id]['name']}")
    
    # Dados do conceito
    # Número opcional/automático para ordenação: 'auto' atribui próximo número natural,
    # vazio = sem prefixo, '0' reservado para revisões.
    number_input = input_with_default(
        "Número do conceito (digite 'auto' para próximo número, deixe vazio para sem prefixo, 0 para revisão)",
        "auto"
    ).strip()

    raw_concept_id = input_with_default("ID do conceito (ex: conceito_funcao, introducao)", "").lower().replace(" ", "_")
    if not raw_concept_id:
        print_error("ID é obrigatório!")
        return

    # Determinar ID final com prefixo opcional
    concept_id = raw_concept_id

    def get_next_number(module_cfg):
        nums = []
        for c in module_cfg.get('concepts', []):
            cid = c.get('id', '')
            # procurar prefixo numérico como 'N-...'
            try:
                if '-' in cid:
                    prefix = cid.split('-', 1)[0]
                    if prefix.isdigit():
                        nums.append(int(prefix))
            except Exception:
                continue
        return max(nums) + 1 if nums else 1

    if number_input and number_input.lower() != '':
        if number_input.lower() == 'auto':
            number = get_next_number(config[disc_id][module_id])
        else:
            if not number_input.isdigit():
                print_error("Número inválido! Use um número natural, 'auto' ou deixe vazio.")
                return
            number = int(number_input)

        # Reservar 0 para revisões (permitido, mas mostrar aviso)
        if number == 0:
            print_warning("Usou o número 0 (reservado para revisões). Será prefixado como '0-'.")

        concept_id = f"{number}-{raw_concept_id}"
    if not concept_id:
        print_error("ID é obrigatório!")
        return
    
    # Verificar se já existe
    existing_ids = [c['id'] for c in config[disc_id][module_id].get('concepts', [])]
    if concept_id in existing_ids:
        print_error(f"Conceito '{concept_id}' já existe!")
        return
    
    concept_name = input_with_default("Nome do conceito", concept_id.replace("_", " ").title())
    tags = input_list("Tags (separadas por vírgula)")
    
    # Adicionar conceito
    concept = {
        "id": concept_id,
        "name": concept_name,
        "tags": tags if tags else []
    }
    
    config[disc_id][module_id]['concepts'].append(concept)
    
    save_config(config)
    
    # Criar pasta
    concept_path = BASE_DIR / disc_id / module_id / concept_id
    concept_path.mkdir(parents=True, exist_ok=True)
    print_success(f"Pasta criada: {concept_path}")
    
    print_header(f"✓ CONCEITO '{concept_name}' ADICIONADO!")
    print_info(f"Caminho: {disc_id}/{module_id}/{concept_id}")
    print_info(f"Tags: {', '.join(tags) if tags else 'Nenhuma'}")

def list_structure():
    """Listar toda a estrutura"""
    print_header("ESTRUTURA ATUAL")
    
    config = load_config()
    
    disciplines = [k for k in config.keys() 
                  if k not in ['difficulty_levels', 'exercise_types', 'bloom_taxonomy', 'quick_presets']]
    
    if not disciplines:
        print_warning("Nenhuma disciplina criada ainda!")
        return
    
    for disc_id in disciplines:
        disc_name = config[disc_id].get('_meta', {}).get('name', disc_id)
        disc_meta = config[disc_id].get('_meta', {})
        
        print(f"\n{Colors.BOLD}{Colors.GREEN}📚 {disc_name}{Colors.END} ({disc_id})")
        if 'description' in disc_meta:
            print(f"   {disc_meta['description']}")
        
        modules = [k for k in config[disc_id].keys() if k != '_meta']
        
        if not modules:
            print(f"   {Colors.YELLOW}(Sem módulos){Colors.END}")
            continue
        
        for module_id in modules:
            module = config[disc_id][module_id]
            print(f"\n   {Colors.BOLD}{Colors.CYAN}📖 {module['name']}{Colors.END} ({module_id})")
            print(f"      Duração: {module.get('duration_hours', 'N/A')} horas")
            
            concepts = module.get('concepts', [])
            if not concepts:
                print(f"      {Colors.YELLOW}(Sem conceitos){Colors.END}")
                continue
            
            print(f"      {Colors.BOLD}Conceitos:{Colors.END}")
            for concept in concepts:
                tags_str = f" [{', '.join(concept['tags'])}]" if concept['tags'] else ""
                print(f"        • {concept['name']}{tags_str}")

def delete_concept():
    """Remover conceito"""
    print_header("REMOVER CONCEITO")
    print_warning("Esta ação NÃO remove exercícios já criados!")
    
    config = load_config()
    
    # Selecionar disciplina
    disciplines = [k for k in config.keys() 
                  if k not in ['difficulty_levels', 'exercise_types', 'bloom_taxonomy', 'quick_presets']]
    
    if not disciplines:
        print_error("Nenhuma disciplina encontrada!")
        return
    
    print_info("Disciplinas:")
    for i, disc in enumerate(disciplines, 1):
        print(f"  {i}. {config[disc].get('_meta', {}).get('name', disc)}")
    
    choice = input_with_default(f"Disciplina (1-{len(disciplines)})", "1")
    try:
        disc_id = disciplines[int(choice) - 1]
    except (ValueError, IndexError):
        print_error("Escolha inválida!")
        return
    
    # Selecionar módulo
    modules = [k for k in config[disc_id].keys() if k != '_meta']
    if not modules:
        print_error("Nenhum módulo!")
        return
    
    print(f"\n{Colors.BLUE}Módulos:{Colors.END}")
    for i, mod in enumerate(modules, 1):
        print(f"  {i}. {config[disc_id][mod]['name']}")
    
    choice = input_with_default(f"Módulo (1-{len(modules)})", "1")
    try:
        module_id = modules[int(choice) - 1]
    except (ValueError, IndexError):
        print_error("Escolha inválida!")
        return
    
    # Selecionar conceito
    concepts = config[disc_id][module_id].get('concepts', [])
    if not concepts:
        print_error("Nenhum conceito!")
        return
    
    print(f"\n{Colors.BLUE}Conceitos:{Colors.END}")
    for i, concept in enumerate(concepts, 1):
        print(f"  {i}. {concept['name']} ({concept['id']})")
    
    choice = input_with_default(f"Conceito (1-{len(concepts)})", "1")
    try:
        concept_idx = int(choice) - 1
        concept = concepts[concept_idx]
    except (ValueError, IndexError):
        print_error("Escolha inválida!")
        return
    
    # Confirmar
    confirm = input_with_default(f"\nRemover '{concept['name']}'? (s/n)", "n").lower()
    if confirm != 's':
        print_info("Cancelado.")
        return
    
    # Remover
    config[disc_id][module_id]['concepts'].pop(concept_idx)
    save_config(config)
    
    print_success(f"Conceito '{concept['name']}' removido da configuração!")
    print_warning(f"Pasta e exercícios em '{disc_id}/{module_id}/{concept['id']}' não foram removidos.")

def main_menu():
    """Menu principal"""
    while True:
        print_header("GESTÃO DE MÓDULOS E DISCIPLINAS")
        
        print(f"{Colors.BOLD}Escolha uma opção:{Colors.END}\n")
        print(f"  {Colors.GREEN}1. Criar Nova Disciplina{Colors.END}")
        print(f"  {Colors.GREEN}2. Criar Novo Módulo{Colors.END}")
        print(f"  {Colors.GREEN}3. Adicionar Conceito{Colors.END}")
        print(f"  {Colors.CYAN}4. Ver Estrutura Completa{Colors.END}")
        print(f"  {Colors.RED}5. Remover Conceito{Colors.END}")
        print(f"  {Colors.YELLOW}0. Sair{Colors.END}")
        
        choice = input(f"\n{Colors.CYAN}Opção: {Colors.END}").strip()
        
        if choice == "1":
            create_discipline()
        elif choice == "2":
            create_module()
        elif choice == "3":
            add_concept()
        elif choice == "4":
            list_structure()
        elif choice == "5":
            delete_concept()
        elif choice == "0":
            print_success("Até breve!")
            break
        else:
            print_error("Opção inválida!")
        
        input(f"\n{Colors.CYAN}Pressione Enter para continuar...{Colors.END}")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print_error("\n\nInterrompido pelo utilizador!")
    except Exception as e:
        print_error(f"\n\nErro: {str(e)}")
        import traceback
        traceback.print_exc()
