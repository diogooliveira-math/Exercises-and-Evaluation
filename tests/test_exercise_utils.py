import json
import importlib.util
import sys
from pathlib import Path


def load_module_from_path(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_generate_next_id_and_saving(tmp_path):
    tools_dir = Path(__file__).resolve().parent.parent / "ExerciseDatabase" / "_tools"
    eu_path = tools_dir / "exercise_utils.py"
    eu = load_module_from_path(eu_path, "exercise_utils")

    base = tmp_path / "repo"
    base.mkdir()

    # Create existing files to simulate existing exercises
    disc = 'matematica'
    mod = 'P4_funcoes'
    concept = '4-funcao_inversa'
    tipo = 'determinacao_analitica'

    tipo_dir = base / disc / mod / concept / tipo
    tipo_dir.mkdir(parents=True, exist_ok=True)
    # create two existing files matching the naming scheme used by generate_next_id
    # concept_abbr = first 4 letters of concept (funcao_inversa -> FUNC)
    # tipo_abbr = initials of tipo words (determinacao_analitica -> DA)
    (tipo_dir / 'MAT_P4FUNCOE_FUNC_DA_001.tex').write_text('% a')
    (tipo_dir / 'MAT_P4FUNCOE_FUNC_DA_002.tex').write_text('% b')

    next_id = eu.generate_next_id(disc, mod, concept, tipo, base_dir=base)
    assert next_id.endswith('_003')

    # Test saving .tex
    latex = "\\exercicio{Test content}"
    tex_path = eu.save_tex_for_exercise(base, disc, mod, concept, tipo, next_id, latex)
    assert tex_path.exists()
    assert tex_path.read_text(encoding='utf-8').strip() == latex


def test_update_type_metadata_and_index(tmp_path):
    tools_dir = Path(__file__).resolve().parent.parent / "ExerciseDatabase" / "_tools"
    eu_path = tools_dir / "exercise_utils.py"
    eu = load_module_from_path(eu_path, "exercise_utils")

    base = tmp_path / 'repo2'
    base.mkdir()

    disc = 'matematica'
    mod = 'P4_funcoes'
    concept = '4-funcao_inversa'
    tipo = 'determinacao_analitica'

    tipo_dir = base / disc / mod / concept / tipo
    tipo_dir.mkdir(parents=True, exist_ok=True)

    exercise_id = 'MAT_TEST_001'

    exercise_metadata = {
        'created': '2025-11-21',
        'author': 'Tester',
        'classification': {'difficulty': 3, 'tags': ['funcoes']}
    }

    eu.update_type_metadata(tipo_dir, exercise_id, exercise_metadata)
    meta_file = tipo_dir / 'metadata.json'
    assert meta_file.exists()
    meta = json.loads(meta_file.read_text(encoding='utf-8'))
    assert exercise_id in meta['exercicios']

    # Test update_index
    metadata_for_index = {
        'id': exercise_id,
        'classification': {
            'discipline': disc,
            'module': mod,
            'module_name': 'Módulo P4',
            'concept': concept,
            'concept_name': 'Função Inversa',
            'tipo': tipo,
            'tipo_nome': 'Determinação Analítica',
            'tags': ['funcoes'],
            'difficulty': 3
        },
        'exercise_type': 'desenvolvimento',
        'status': 'active'
    }

    idx_file = eu.update_index(base, metadata_for_index, str((tipo_dir / f"{exercise_id}.tex").relative_to(base)))
    assert idx_file.exists()
    idx = json.loads(idx_file.read_text(encoding='utf-8'))
    assert any(e['id'] == exercise_id for e in idx['exercises'])
