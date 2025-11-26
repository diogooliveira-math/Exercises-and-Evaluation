import json
import os
import sys
import importlib.util
from pathlib import Path


def load_module_from_path(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_minimal_parse_and_incorporate(tmp_path, monkeypatch):
    """Test parse_minimal_template and incorporate_exercise flow (including new-type creation)."""
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    # Prevent windows-specific stdout rewrapping in imported modules during tests
    monkeypatch.setattr(sys, 'platform', 'linux')

    tools_dir = Path(__file__).resolve().parent.parent / "ExerciseDatabase" / "_tools"
    add_minimal_path = tools_dir / "add_exercise_minimal.py"
    mod = load_module_from_path(add_minimal_path, "add_exercise_minimal")

    # Create minimal modules_config.yaml in tmp repo
    cfg = {
        'matematica': {
            'P4_funcoes': {
                'name': 'MÓDULO P4 - Funções',
                'concepts': [
                    {'id': '4-funcao_inversa', 'name': 'Função Inversa'}
                ]
            }
        }
    }
    (repo_root / 'modules_config.yaml').write_text(json.dumps(cfg), encoding='utf-8')

    # Prepare a template file with required fields
    content = (
        "% Módulo: P4_funcoes\n"
        "% Conceito: 4-funcao_inversa\n"
        "\\exercicio{\nDetermine a função inversa de $f(x)=2x+3$.\n}\n"
    )

    # Instantiate template with our repo_root
    TemplateClass = mod.MinimalExerciseTemplate
    template = TemplateClass(repo_root)

    tmp_file = repo_root / "NOVO_EXERCICIO_MINIMO.tex"
    tmp_file.write_text(content, encoding='utf-8')
    template.temp_file = tmp_file

    success, data, errors = template.parse_minimal_template()
    assert success, f"Parse failed: {errors}"
    assert data['módulo'] == 'P4_funcoes'
    assert data['conceito'] == '4-funcao_inversa'
    assert 'enunciado' in data

    # Now test incorporate_exercise. Ensure inputs for interactive creation of tipo.
    # Sequence of inputs: tipo_nome, descricao, tags_input, requer_calculo, requer_grafico
    inputs = iter(["determinacao_analitica", "Determinação analítica", "analitica, inversa", "s", "n"])
    monkeypatch.setattr('builtins.input', lambda prompt='': next(inputs))

    # Run incorporation
    ok = template.incorporate_exercise(data)
    assert ok, "incorporate_exercise failed"

    # Check files created
    tipo_dir = repo_root / 'matematica' / 'P4_funcoes' / '4-funcao_inversa' / data['tipo']
    assert tipo_dir.exists()
    assert (tipo_dir / 'metadata.json').exists()
    # There should be at least one .tex in directory
    texs = list(tipo_dir.glob('*.tex'))
    assert len(texs) >= 1

    # Index should be created/updated
    index_file = repo_root / 'index.json'
    assert index_file.exists()
    idx = json.loads(index_file.read_text(encoding='utf-8'))
    assert idx['total_exercises'] >= 1


def test_generate_variant_core_functions(tmp_path, monkeypatch):
    # Prevent windows-specific stdout rewrapping in imported modules during tests
    monkeypatch.setattr(sys, 'platform', 'linux')
    """Test core helper functions of generate_variant.py (split_id_parts, find_next_number, apply_variation, update_tex_header)."""
    tools_dir = Path(__file__).resolve().parent.parent / "ExerciseDatabase" / "_tools"
    gv_path = tools_dir / "generate_variant.py"
    mod = load_module_from_path(gv_path, "generate_variant")

    # Test split_id_parts
    prefix, num = mod.split_id_parts('MAT_P4FUNCOE_4FIN_003')
    assert prefix.endswith('_')
    assert num == '003'

    # Setup a folder with existing files to test find_next_number
    folder = tmp_path / 'tipo_dir'
    folder.mkdir()
    # create files with suffixes 001 and 002
    (folder / 'MAT_P4FUNCOE_4FIN_001.tex').write_text('% ex 1')
    (folder / 'MAT_P4FUNCOE_4FIN_002.tex').write_text('% ex 2')

    next_num = mod.find_next_number(folder, 'MAT_P4FUNCOE_4FIN_')
    assert next_num == '003'

    # Test apply_variation: small numeric changes inside $...$
    src = "This has $2$ and $-1$ and $15$ and text"
    varied = mod.apply_variation(src, 'auto')
    assert '$3$' in varied
    assert '$0$' in varied  # -1 -> 0
    # Números fora do intervalo pequeno permanecem inalterados (ex.: 15 stays 15)
    assert '$15$' in varied

    # Test update_tex_header
    tex = "% Exercise ID: OLD_ID\n% Date: 2025-01-01\n\exercicio{Hi}"
    updated = mod.update_tex_header(tex, 'NEW_ID_001', '2025-11-21')
    assert '% Exercise ID: NEW_ID_001' in updated
    assert '% Date: 2025-11-21' in updated
