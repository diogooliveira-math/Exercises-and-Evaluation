"""
Sistema de Gestão de Exercícios com TIPOS - Versão Não-Interativa 3.0
Hierarquia: disciplina/tema/conceito/tipo/exercicio.tex
Usa JSON por diretório (Opção A)

Esta versão aceita argumentos de linha de comando para uso por agentes.
"""

import json
import os
import yaml
import argparse
from datetime import datetime
from pathlib import Path
import re
from typing import Dict, List, Optional

# Importar sistema de preview (desabilitado por padrão para agentes)
from preview_system import PreviewManager, create_exercise_preview

class Colors:
    pass

def print_header(text):
    print(f"\n{'='*70}")
    print(f"{text.center(70)}")
    print(f"{'='*70}\n")

def print_success(text):
    print(f"[OK] {text}")

def print_error(text):
    print(f"[ERRO] {text}")

def print_info(text):
    print(f"[INFO] {text}")

def print_warning(text):
    print(f"[AVISO] {text}")

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
            raise FileNotFoundError(f"Ficheiro de configuração não encontrado: {CONFIG_FILE}")
            
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
    Compatível com formatos antigos ('type') e novos ('tipo')
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
                    
                    # Compatibilidade com formatos antigos e novos
                    tipo_id = metadata.get('tipo') or metadata.get('type')
                    tipo_nome = metadata.get('tipo_nome') or metadata.get('title')
                    descricao = metadata.get('descricao') or metadata.get('description', '')
                    
                    if tipo_id:  # Só adicionar se encontrou o ID do tipo
                        types.append({
                            'id': tipo_id,
                            'name': tipo_nome,
                            'description': descricao,
                            'path': item
                        })
    
    return types

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

def create_exercise_with_types_non_interactive(args):
    """Versão não-interativa para agentes"""
    
    print_header("ADICIONAR NOVO EXERCÍCIO (Não-Interativo)")
    
    config = ModuleConfig()
    
    # Validar disciplina
    disciplines = [d['id'] for d in config.get_disciplines()]
    if args.discipline not in disciplines:
        raise ValueError(f"Disciplina inválida: {args.discipline}. Disponíveis: {disciplines}")
    
    # Validar módulo
    modules = [m['id'] for m in config.get_modules(args.discipline)]
    if args.module not in modules:
        raise ValueError(f"Módulo inválido: {args.module}. Disponíveis: {modules}")
    
    # Validar conceito
    concepts = [c['id'] for c in config.get_concepts(args.discipline, args.module)]
    if args.concept not in concepts:
        raise ValueError(f"Conceito inválido: {args.concept}. Disponíveis: {concepts}")
    
    # Validar tipo
    exercise_types = get_exercise_types_for_concept(args.discipline, args.module, args.concept)
    tipo_ids = [t['id'] for t in exercise_types]
    if args.tipo not in tipo_ids:
        raise ValueError(f"Tipo inválido: {args.tipo}. Disponíveis: {tipo_ids}")
    
    # Carregar metadata do tipo
    tipo_path = BASE_DIR / args.discipline / args.module / args.concept / args.tipo
    tipo_metadata_file = tipo_path / "metadata.json"
    with open(tipo_metadata_file, 'r', encoding='utf-8') as f:
        tipo_metadata = json.load(f)
    
    tipo_nome = tipo_metadata.get('tipo_nome') or tipo_metadata.get('title', args.tipo)
    tags_auto_tipo = tipo_metadata.get('tags_tipo', [])
    
    # Gerar ID
    exercise_id = get_next_exercise_id(args.discipline, args.module, args.concept, args.tipo)
    
    # Validar dificuldade
    if not 1 <= args.difficulty <= 5:
        raise ValueError("Dificuldade deve ser entre 1 e 5")
    
    # Tags
    concept_data = next((c for c in config.get_concepts(args.discipline, args.module) if c['id'] == args.concept), {})
    auto_tags_concept = concept_data.get('tags', [])
    all_auto_tags = list(set(auto_tags_concept + tags_auto_tipo))
    tags = all_auto_tags + args.additional_tags
    
    # Verificar sub-variants
    has_subvariants = tipo_metadata.get('has_subvariants', False)
    subvariant_functions = args.subvariant_functions if has_subvariants and args.subvariant_functions else []
    
    # Preparar metadados
    today = datetime.now().strftime("%Y-%m-%d")
    module_name = config.get_module_name(args.discipline, args.module)
    concept_name = config.get_concept_name(args.discipline, args.module, args.concept)
    
    metadata = {
        "id": exercise_id,
        "version": "1.0",
        "created": today,
        "modified": today,
        "author": args.author,
        "classification": {
            "discipline": args.discipline,
            "module": args.module,
            "module_name": module_name,
            "concept": args.concept,
            "concept_name": concept_name,
            "tipo": args.tipo,
            "tipo_nome": tipo_nome,
            "tags": tags,
            "difficulty": args.difficulty,
            "difficulty_label": config.get_difficulty_label(args.difficulty)
        },
        "exercise_type": args.format,
        "content": {
            "has_multiple_parts": bool(subvariant_functions) or args.has_parts,
            "parts_count": len(subvariant_functions) if subvariant_functions else args.parts_count,
            "has_subvariants": has_subvariants,
            "subvariant_functions": subvariant_functions,
                "has_graphics": tipo_metadata.get('caracteristicas', {}).get('requer_grafico', False),
            "requires_packages": ["amsmath", "amssymb"]
        },
        "evaluation": {
            "bloom_level": "aplicacao"
        },
        "solution": {
            "available": bool(args.solution),
            "file": f"{exercise_id}_solucao.tex" if args.solution else ""
        },
        "usage": {
            "times_used": 0,
            "last_used": "",
            "contexts": []
        },
        "status": "active"
    }
    
    # Gerar LaTeX
    latex_content = f"""% Exercise ID: {exercise_id}
% Module: {module_name} | Concept: {concept_name} | Type: {tipo_nome}
% Difficulty: {args.difficulty}/5 ({config.get_difficulty_label(args.difficulty)}) | Format: {args.format}
% Tags: {', '.join(tags)}
% Author: {args.author} | Date: {today}
% Status: active

\\exercicio{{{args.statement}}}
"""
    
    if subvariant_functions:
        latex_content += "\n\\begin{enumerate}[label=\\alph*)]\n"
        for func in subvariant_functions:
            latex_content += f"\\item $f(x) = {func}$\n"
        latex_content += "\\end{enumerate}\n\n"
    
    if args.solution:
        latex_content += f"\n% Solution:\n% \\begin{{solucao}}\n% {args.solution.replace(chr(10), chr(10) + '% ')}\n% \\end{{solucao}}\n"
    
    # Preview (opcional para agentes)
    if not args.skip_preview:
        preview_content = create_exercise_preview(
            exercise_id,
            latex_content,
            metadata,
            tipo_metadata
        )
        
        preview = PreviewManager(auto_open=False)  # Não abrir automaticamente para agentes
        if not preview.show_and_confirm(preview_content, f"Novo Exercício: {exercise_id}"):
            print_error("Preview rejeitado!")
            return
    
    # Salvar
    if has_subvariants and subvariant_functions:
        # Usar função de sub-variants
        from generate_subvariant_exercise import generate_subvariant_exercise_folder
        
        exercise_folder = generate_subvariant_exercise_folder(
            exercise_id,
            f"{module_name} - {concept_name} - {tipo_nome}",
            subvariant_functions,
            args.statement,
            metadata,
            str(tipo_path)
        )
        main_tex_file = Path(exercise_folder) / "main.tex"
    else:
        tex_file = tipo_path / f"{exercise_id}.tex"
        with open(tex_file, 'w', encoding='utf-8') as f:
            f.write(latex_content)
        main_tex_file = tex_file
    
    # Atualizar metadata do tipo
    update_type_metadata_inline(tipo_path, exercise_id, metadata)
    
    # Atualizar índice
    update_index(metadata, str(main_tex_file.relative_to(BASE_DIR)))
    
    print_success(f"Exercício criado: {exercise_id}")
    return exercise_id

def update_index(metadata: Dict, file_path: str):
    """Atualiza índice central"""
    index_file = BASE_DIR / "index.json"
    
    if index_file.exists():
        with open(index_file, 'r', encoding='utf-8') as f:
            index = json.load(f)
        # Garantir que todas as chaves de estatísticas existam
        stats = index.get("statistics", {})
        for key in ["by_discipline", "by_module", "by_concept", "by_type", "by_difficulty", "by_format"]:
            if key not in stats:
                stats[key] = {}
        index["statistics"] = stats
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

def main():
    parser = argparse.ArgumentParser(description="Adicionar exercício não-interativamente")
    
    # Opção para arquivo de configuração (para evitar problemas com argumentos longos)
    parser.add_argument("--config-file", help="Arquivo JSON com argumentos")
    
    # Argumentos individuais (mantidos para compatibilidade)
    parser.add_argument("--discipline", help="ID da disciplina")
    parser.add_argument("--module", help="ID do módulo")
    parser.add_argument("--concept", help="ID do conceito")
    parser.add_argument("--tipo", help="ID do tipo de exercício")
    parser.add_argument("--format", default="standard", help="Formato do exercício")
    parser.add_argument("--difficulty", type=int, default=3, help="Dificuldade (1-5)")
    parser.add_argument("--author", default="Professor", help="Nome do autor")
    parser.add_argument("--statement", help="Enunciado do exercício")
    parser.add_argument("--additional-tags", nargs='*', default=[], help="Tags adicionais")
    parser.add_argument("--subvariant-functions", nargs='*', default=[], help="Funções para sub-variants")
    parser.add_argument("--has-parts", action='store_true', help="Tem múltiplas partes")
    parser.add_argument("--parts-count", type=int, default=0, help="Número de partes")
    parser.add_argument("--solution", help="Texto da solução")
    parser.add_argument("--skip-preview", action='store_true', help="Pular preview")
    
    args = parser.parse_args()
    
    # Se foi passado arquivo de configuração, carregar argumentos dele
    if args.config_file:
        with open(args.config_file, 'r', encoding='utf-8-sig') as f:
            config_args = json.load(f)
        
        # Criar objeto args com os valores do arquivo
        class ConfigArgs:
            def __init__(self, config_dict):
                for key, value in config_dict.items():
                    setattr(self, key, value)
        
        args = ConfigArgs(config_args)
    
    try:
        result = create_exercise_with_types_non_interactive(args)
        print(f"Sucesso: {result}")
    except Exception as e:
        print_error(f"Erro: {str(e)}")
        raise

if __name__ == "__main__":
    main()