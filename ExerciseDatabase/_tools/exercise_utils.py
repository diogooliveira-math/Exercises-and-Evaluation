"""Helper utilities for creating and registering exercises.

This module centralises ID generation, file saving and index/type metadata
updates so the different creation scripts can share behaviour.
"""
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


def get_base_dir() -> Path:
    return Path(__file__).parent.parent


def generate_next_id(discipline: str, module_id: str, concept_id: str, tipo_id: str, base_dir: Optional[Path] = None) -> str:
    if base_dir is None:
        base_dir = get_base_dir()

    disc_abbr = discipline[:3].upper()
    module_abbr = module_id.replace('_', '').upper()[:8]

    concept_parts = concept_id.split('-')
    if len(concept_parts) > 1:
        concept_abbr = concept_parts[1][:4].upper()
    else:
        concept_abbr = concept_id[:4].upper()

    tipo_abbr = ''.join([w[0].upper() for w in tipo_id.split('_')])[:3]

    tipo_path = base_dir / discipline / module_id / concept_id / tipo_id
    tipo_path.mkdir(parents=True, exist_ok=True)

    existing = list(tipo_path.glob(f"{disc_abbr}_{module_abbr}_{concept_abbr}_{tipo_abbr}_*.tex"))
    next_num = 1
    if existing:
        numbers = []
        for f in existing:
            m = re.search(r'_(\d{3})\.tex$', f.name)
            if m:
                try:
                    numbers.append(int(m.group(1)))
                except Exception:
                    continue
        if numbers:
            next_num = max(numbers) + 1

    return f"{disc_abbr}_{module_abbr}_{concept_abbr}_{tipo_abbr}_{next_num:03d}"


def save_tex_for_exercise(base_dir: Path, discipline: str, module_id: str, concept_id: str, tipo_id: str, exercise_id: str, latex_content: str) -> Path:
    tipo_path = base_dir / discipline / module_id / concept_id / tipo_id
    tipo_path.mkdir(parents=True, exist_ok=True)
    tex_file = tipo_path / f"{exercise_id}.tex"
    with open(tex_file, 'w', encoding='utf-8') as f:
        f.write(latex_content)
    return tex_file


def update_type_metadata(tipo_path: Path, exercise_id: str, exercise_metadata: Dict):
    metadata_file = tipo_path / 'metadata.json'
    if metadata_file.exists():
        try:
            metadata = json.loads(metadata_file.read_text(encoding='utf-8'))
        except Exception:
            metadata = {}
    else:
        metadata = {}

    if not isinstance(metadata.get('exercicios'), dict) and not isinstance(metadata.get('exercicios'), list):
        # Support both list and dict shapes
        metadata['exercicios'] = {}

    # Normalize to dict with per-exercise metadata
    if isinstance(metadata.get('exercicios'), list):
        # convert list to dict
        existing_list = metadata['exercicios']
        metadata['exercicios'] = {eid: {} for eid in existing_list}

    metadata['exercicios'][exercise_id] = {
        'created': exercise_metadata.get('created', datetime.now().strftime('%Y-%m-%d')),
        'modified': datetime.now().strftime('%Y-%m-%d'),
        'author': exercise_metadata.get('author', 'Professor'),
        'difficulty': exercise_metadata.get('classification', {}).get('difficulty', exercise_metadata.get('difficulty', 2)),
        'tags': exercise_metadata.get('classification', {}).get('tags', exercise_metadata.get('tags', [])),
        'status': exercise_metadata.get('status', 'active')
    }

    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)


def update_index(base_dir: Path, metadata: Dict, file_path: str):
    index_file = base_dir / 'index.json'
    today = datetime.now().isoformat()

    if index_file.exists():
        try:
            index = json.loads(index_file.read_text(encoding='utf-8'))
        except Exception:
            index = {}
    else:
        index = {}

    index.setdefault('database_version', '3.0')
    index.setdefault('exercises', [])
    index.setdefault('statistics', {})

    entry = {
        'id': metadata.get('id'),
        'path': file_path.replace('\\', '/'),
        'discipline': metadata.get('classification', {}).get('discipline'),
        'module': metadata.get('classification', {}).get('module'),
        'module_name': metadata.get('classification', {}).get('module_name'),
        'concept': metadata.get('classification', {}).get('concept'),
        'concept_name': metadata.get('classification', {}).get('concept_name'),
        'tipo': metadata.get('classification', {}).get('tipo'),
        'tipo_nome': metadata.get('classification', {}).get('tipo_nome'),
        'difficulty': metadata.get('classification', {}).get('difficulty'),
        'format': metadata.get('exercise_type', metadata.get('format', 'desenvolvimento')),
        'tags': metadata.get('classification', {}).get('tags', []),
        'points': metadata.get('evaluation', {}).get('points', 0),
        'status': metadata.get('status', 'active')
    }

    index['exercises'].append(entry)
    index['total_exercises'] = len(index['exercises'])
    index['last_updated'] = today

    # update simple stats
    stats = index.get('statistics', {})
    stats.setdefault('by_module', {})
    mod = entry.get('module') or 'unknown'
    stats['by_module'][mod] = stats['by_module'].get(mod, 0) + 1
    index['statistics'] = stats

    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

    return index_file


def ensure_type_directory(base_dir: Path, discipline: str, module_id: str, concept_id: str, tipo_id: str) -> Path:
    """Ensure the type directory exists and create a minimal metadata.json if missing.

    This may prompt the user interactively for type metadata when creating a new type.
    Returns the Path to the type directory.
    """
    tipo_path = base_dir / discipline / module_id / concept_id / tipo_id
    if tipo_path.exists():
        return tipo_path

    tipo_path.mkdir(parents=True, exist_ok=True)

    # Interactive creation of metadata.json with sensible defaults
    metadata_file = tipo_path / 'metadata.json'
    default_name = tipo_id.replace('_', ' ').title()
    try:
        print(f"Novo tipo detectado: '{tipo_id}'. A criar metadados em: {metadata_file}")
        tipo_nome = input(f"Nome do tipo [{default_name}]: ").strip() or default_name
        default_desc = f"Exercícios de {tipo_id.replace('_',' ')}"
        descricao = input(f"Descrição [{default_desc}]: ").strip() or default_desc
        tags_input = input("Tags iniciais (separadas por vírgula) [deixe vazio para usar tags inferidas]: ").strip()
        if tags_input:
            tags_tipo = [t.strip() for t in tags_input.split(',') if t.strip()]
        else:
            tags_tipo = []

        requer_calculo = input("Requer cálculo? (s/n) [s]: ").strip().lower() or 's'
        requer_calculo = True if requer_calculo in ['s', 'sim', 'y', 'yes'] else False
        requer_grafico = input("Requer gráfico? (s/n) [n]: ").strip().lower() or 'n'
        requer_grafico = True if requer_grafico in ['s', 'sim', 'y', 'yes'] else False

    except KeyboardInterrupt:
        # If the user aborts, leave directory but no metadata
        print("\nOperação cancelada pelo utilizador durante criação de tipo.")
        return tipo_path

    tipo_metadata = {
        "tipo": tipo_id,
        "tipo_nome": tipo_nome,
        "conceito": concept_id,
        "tema": module_id,
        "disciplina": discipline,
        "descricao": descricao,
        "tags_tipo": tags_tipo,
        "caracteristicas": {
            "requer_calculo": requer_calculo,
            "requer_grafico": requer_grafico
        },
        "dificuldade_sugerida": {
            "min": 1,
            "max": 5
        },
        "exercicios": {}
    }

    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(tipo_metadata, f, indent=2, ensure_ascii=False)

    print(f"Tipo criado: {tipo_nome} -> {metadata_file}")
    return tipo_path


def preview_and_confirm(latex_content: str, metadata: Dict, title: str = 'Preview') -> bool:
    """Show a preview using PreviewManager if available, otherwise fall back to a simple input prompt.

    Returns True if the user confirms saving/incorporation.
    """
    try:
        # Try to import preview_system dynamically; it's optional
        from preview_system import PreviewManager, create_exercise_preview
        preview = PreviewManager(auto_open=True)
        preview_content = create_exercise_preview(title, latex_content, metadata)
        return preview.show_and_confirm(preview_content, title)
    except Exception:
        # Fallback: ask user via terminal
        resp = input('Incorporar exercício na base de dados? (s/n): ').strip().lower()
        return resp in ['s', 'sim', 'y', 'yes']
