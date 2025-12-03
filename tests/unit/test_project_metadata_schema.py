import pytest


def test_metadata_schema_minimum():
    """Validate minimal payload structure for a project metadata.

    This is a lightweight test skeleton. The implementation project should
    validate against a JSON Schema; here we assert presence and basic types.
    """
    payload = {
        "title": "Projeto de Investigação Exemplo",
        "discipline": "matematica",
        "module": "P4_funcoes",
        "concept": "4-funcao_inversa",
        "tipo": "determinacao_analitica",
        "difficulty": 3,
        "statement": "Enunciado de exemplo"
    }

    assert isinstance(payload.get("title"), str)
    assert payload.get("discipline") == "matematica"
    assert isinstance(payload.get("difficulty"), int)
    assert 1 <= payload.get("difficulty") <= 5
