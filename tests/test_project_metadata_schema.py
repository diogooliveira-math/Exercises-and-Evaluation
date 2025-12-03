import json
from pathlib import Path
import pytest

try:
    from jsonschema import validate
except Exception:
    pytest.skip("jsonschema not installed", allow_module_level=True)


def test_project_schema_validates_example():
    repo_root = Path(__file__).resolve().parents[1]
    schema_path = repo_root / 'ExerciseDatabase' / '_tools' / 'project_metadata_schema.json'
    assert schema_path.exists(), f"Schema not found at {schema_path}"

    schema = json.loads(schema_path.read_text(encoding='utf-8'))

    example = {
        "id": "PROJ_P4FUNCOE_001",
        "titulo": "Exploração de Contextos Reais para Função Inversa",
        "responsavel": "Prof. Ana Silva",
        "discipline": "matematica",
        "module": "P4_funcoes",
        "tags": ["investigacao","funcoes"],
        "summary": "Projeto para desenvolver problemas e fichas que relacionem função inversa com contextos reais.",
        "status": "draft",
        "created_at": "2025-12-02T09:00:00Z",
        "version": 1
    }

    # Should not raise
    validate(instance=example, schema=schema)
