import importlib.util
import sys
from pathlib import Path
import shutil

import pytest

# Carregar o módulo add_exercise_simple.py por caminho
MODULE_PATH = Path(__file__).resolve().parents[1] / "ExerciseDatabase" / "_tools" / "add_exercise_simple.py"

def load_module():
    spec = importlib.util.spec_from_file_location("add_exercise_simple_testmod", MODULE_PATH)
    if spec is None:
        raise RuntimeError("Failed to load module spec")
    mod = importlib.util.module_from_spec(spec)
    if spec.name is None:
        raise RuntimeError("Spec has no name")
    sys.modules[spec.name] = mod
    loader = spec.loader
    if loader is None:
        raise RuntimeError("No loader available for module spec")
    loader.exec_module(mod)
    return mod


def test_validate_metadata_good():
    mod = load_module()
    errs = mod.validate_metadata("matematica", "P4_funcoes", "1-generalidades", "afirmacoes", 3, "Enunciado de teste")
    assert isinstance(errs, list)
    assert len(errs) == 0


def test_validate_metadata_bad():
    mod = load_module()
    errs = mod.validate_metadata("", "", "", "", "notint", "")
    assert isinstance(errs, list)
    assert len(errs) >= 1


def test_create_simple_exercise_creates_files(tmp_path, monkeypatch):
    mod = load_module()

    # Ajustar BASE_DIR do módulo para usar o tmp_path isolado
    monkeypatch.setattr(mod, 'BASE_DIR', tmp_path)

    discipline = "matematica"
    module = "P4_funcoes"
    concept = "1-generalidades_funcoes"
    tipo = "test_tipo"
    difficulty = 2
    statement = "Enunciado de teste para criação de ficheiro"

    eid = mod.create_simple_exercise(discipline, module, concept, tipo, difficulty, statement)
    # Verificar que o ID é retornado e arquivos foram criados
    assert isinstance(eid, str) and len(eid) > 5

    tex_path = tmp_path / discipline / module / concept / tipo / f"{eid}.tex"
    metadata_path = tmp_path / discipline / module / concept / tipo / "metadata.json"
    index_path = tmp_path / "index.json"

    assert tex_path.exists()
    assert metadata_path.exists()
    assert index_path.exists()

    # Ler o .tex e verificar conteúdo mínimo
    content = tex_path.read_text(encoding='utf-8')
    assert "\\exercicio" in content or "Exercise ID" in content

    # Verificar index contém a ID
    idx = mod.json.loads(index_path.read_text(encoding='utf-8'))
    ids = [e['id'] for e in idx.get('exercises', [])]
    assert eid in ids
