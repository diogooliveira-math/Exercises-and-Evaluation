import json
import sys
from pathlib import Path
import importlib.util


def load_module_from_path(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def generate_exercise_id_for_test(discipline: str, module_id: str, concept_id: str, tipo_id: str, base_path: Path) -> str:
    # Simple reproduction of ID scheme used in tools but for tmp base
    disc_abbr = discipline[:3].upper()
    module_abbr = module_id.replace('_', '').upper()[:8]
    concept_parts = concept_id.split('-')
    if len(concept_parts) > 1:
        concept_abbr = concept_parts[1][:4].upper()
    else:
        concept_abbr = concept_id[:4].upper()
    tipo_abbr = ''.join([w[0].upper() for w in tipo_id.split('_')])[:3]

    tipo_path = base_path / discipline / module_id / concept_id / tipo_id
    tipo_path.mkdir(parents=True, exist_ok=True)
    existing = list(tipo_path.glob(f"{disc_abbr}_{module_abbr}_{concept_abbr}_{tipo_abbr}_*.tex"))
    next_num = len(existing) + 1
    return f"{disc_abbr}_{module_abbr}_{concept_abbr}_{tipo_abbr}_{next_num:03d}"


def test_template_parse_and_save_flow(tmp_path, monkeypatch):
    """Verify `ExerciseTemplate.parse_template` and simulate saving into tipo folder."""
    # Avoid Windows-specific side-effects during imports
    monkeypatch.setattr(sys, 'platform', 'linux')

    tools_dir = Path(__file__).resolve().parent.parent / "ExerciseDatabase" / "_tools"
    aet_path = tools_dir / "add_exercise_template.py"
    aet = load_module_from_path(aet_path, "add_exercise_template")

    # Prepare a minimal modules_config.yaml expected by users (in tmp base)
    base = tmp_path / "repo"
    base.mkdir()
    modules_config = {
        'matematica': {
            'P4_funcoes': {
                'name': 'MÓDULO P4 - Funções',
                'concepts': [
                    {'id': '4-funcao_inversa', 'name': 'Função Inversa'}
                ]
            }
        }
    }
    (base / 'modules_config.yaml').write_text(json.dumps(modules_config), encoding='utf-8')

    # Create the ExerciseTemplate instance pointing to our tmp repo
    TemplateClass = aet.ExerciseTemplate
    template = TemplateClass(base)

    # Create a filled template file (all required fields)
    content = """% Disciplina: matematica
% Módulo: P4_funcoes
% Conceito: 4-funcao_inversa
% Tipo: determinacao_analitica
% Formato: desenvolvimento
% Dificuldade: 3
% Autor: TestAuthor
% Tags: funcoes, inversa

\exercicio{Determine a função inversa de $f(x)=2x+3$.}
"""

    temp = template.create_template(prefill=None)
    # overwrite with our content
    temp.write_text(content, encoding='utf-8')
    template.temp_file = temp

    # Parse template
    success, data, errors = template.parse_template()
    assert success, f"Parsing failed: {errors}"
    assert data['disciplina'] == 'matematica'
    assert data['módulo'] == 'P4_funcoes'
    assert data['conceito'] == '4-funcao_inversa'

    # Simulate saving: generate exercise id, write .tex into tipo folder, update metadata.json and index.json in tmp base
    disciplina = data['disciplina']
    modulo = data['módulo']
    conceito = data['conceito']
    tipo = data['tipo']

    exercise_id = generate_exercise_id_for_test(disciplina, modulo, conceito, tipo, base)

    tipo_path = base / disciplina / modulo / conceito / tipo
    tipo_path.mkdir(parents=True, exist_ok=True)

    latex_content = data.get('conteudo', '')
    tex_file = tipo_path / f"{exercise_id}.tex"
    tex_file.write_text(latex_content, encoding='utf-8')

    # Update tipo metadata.json
    metadata_file = tipo_path / 'metadata.json'
    if metadata_file.exists():
        meta = json.loads(metadata_file.read_text(encoding='utf-8'))
    else:
        meta = {
            'tipo': tipo,
            'tipo_nome': tipo.replace('_', ' ').title(),
            'exercicios': []
        }
    if 'exercicios' not in meta or not isinstance(meta['exercicios'], list):
        meta['exercicios'] = []
    meta['exercicios'].append(exercise_id)
    metadata_file.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding='utf-8')

    # Update index.json in tmp base
    index_file = base / 'index.json'
    if index_file.exists():
        index = json.loads(index_file.read_text(encoding='utf-8'))
    else:
        index = {'database_version': '3.0', 'last_updated': '', 'total_exercises': 0, 'statistics': {}, 'exercises': []}

    entry = {
        'id': exercise_id,
        'path': str(tex_file.relative_to(base)).replace('\\', '/'),
        'discipline': disciplina,
        'module': modulo,
        'module_name': modules_config['matematica'][modulo]['name'],
        'concept': conceito,
        'concept_name': 'Função Inversa',
        'tipo': tipo,
        'difficulty': int(data.get('dificuldade', 2)),
        'format': data.get('formato', 'desenvolvimento'),
        'tags': data.get('tags', [])
    }

    index['exercises'].append(entry)
    index['total_exercises'] = len(index['exercises'])
    index['last_updated'] = 'now'
    index_file.write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding='utf-8')

    # Assertions
    assert tex_file.exists()
    assert metadata_file.exists()
    idx = json.loads(index_file.read_text(encoding='utf-8'))
    assert any(e['id'] == exercise_id for e in idx['exercises'])
