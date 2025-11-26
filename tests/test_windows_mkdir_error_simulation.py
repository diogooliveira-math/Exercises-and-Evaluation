#!/usr/bin/env python3
"""
Teste para simular erro de mkdir -p no Windows e falha do tool add_exercise_with_types.

Este teste simula o cenário onde:
1. Comando mkdir -p falha no Windows CMD
2. Tool add_exercise_with_types falha ao tentar criar exercício com tipo não reconhecido
"""

import os
import subprocess
import tempfile
import pytest
from pathlib import Path
import json
import sys

# Adicionar o diretório _tools ao path para importar os módulos
sys.path.insert(0, str(Path(__file__).parent.parent / "ExerciseDatabase" / "_tools"))

def test_mkdir_p_fails_on_windows_cmd():
    """Testa que mkdir -p falha no Windows CMD (não PowerShell)"""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_path = Path(temp_dir) / "test" / "nested" / "path"

        # Forçar uso do CMD.exe (não PowerShell)
        cmd = f'cmd.exe /c mkdir -p "{test_path}"'
        result = subprocess.run(cmd, shell=False, capture_output=True, text=True)

        # No CMD do Windows, mkdir -p deve falhar com erro de sintaxe ou processamento
        assert result.returncode != 0, "mkdir -p deveria falhar no Windows CMD"
        assert ("syntax of the command is incorrect" in result.stderr.lower() or 
                "invalid switch" in result.stderr.lower() or
                "error occurred while processing" in result.stderr.lower())

        # Nota: Mesmo com erro, o CMD pode ter criado a pasta -p como diretório
        # O importante é que houve erro de sintaxe

def test_windows_mkdir_command_works():
    """Testa que mkdir com barras invertidas funciona no Windows"""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_path = Path(temp_dir) / "test" / "nested" / "path"

        # Usar mkdir do Windows (sem -p) - deve funcionar no Windows moderno
        cmd = f'mkdir "{test_path}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        # No Windows moderno, mkdir cria diretórios pais automaticamente
        # Então deve funcionar
        assert result.returncode == 0
        assert test_path.exists()
        assert test_path.exists()

def test_add_exercise_with_invalid_type():
    """Testa falha ao tentar adicionar exercício com tipo não existente"""
    from add_exercise_with_types_non_interactive import create_exercise_with_types_non_interactive
    import argparse

    # Criar argumentos com conceito que não existe
    args = argparse.Namespace(
        discipline="matematica",
        module="A8_modelos_discretos",
        concept="conceito_inexistente_xyz",  # Conceito que não existe
        tipo="qualquer_tipo",
        statement="Teste de enunciado",
        difficulty=2,
        author="Test Agent",
        format="standard",
        additional_tags=[],
        subvariant_functions=[],
        has_parts=False,
        parts_count=0,
        solution=None,
        skip_preview=True
    )

    # Deve lançar ValueError
    with pytest.raises(ValueError, match="Tipo inválido|Conceito inválido"):
        create_exercise_with_types_non_interactive(args)

def test_add_exercise_with_new_type_after_creation():
    """Testa criação de exercício após criar manualmente o tipo"""
    from add_exercise_with_types_non_interactive import create_exercise_with_types_non_interactive
    import argparse

    # Primeiro, criar manualmente a estrutura do tipo
    base_dir = Path(__file__).parent.parent / "ExerciseDatabase"
    tipo_path = base_dir / "matematica" / "A8_modelos_discretos" / "1-sistemas_numericos" / "numeros_figurados_test"

    # Criar diretório
    tipo_path.mkdir(parents=True, exist_ok=True)

    # Criar metadata.json com formato correto
    metadata = {
        "tipo": "numeros_figurados_test",
        "tipo_nome": "Números Figurados Test",
        "conceito": "1-sistemas_numericos",
        "conceito_nome": "Sistemas Numéricos",
        "tema": "A8_modelos_discretos",
        "tema_nome": "Módulo A8 - Modelos Discretos",
        "disciplina": "matematica",
        "descricao": "Teste de números figurados",
        "tags_tipo": ["teste", "numeros"],
        "caracteristicas": {
            "requer_calculo": False,
            "requer_grafico": True
        },
        "dificuldade_sugerida": {
            "min": 1,
            "max": 3
        },
        "exercicios": []
    }
    
    with open(tipo_path / "metadata.json", 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    try:
        # Agora tentar criar exercício
        args = argparse.Namespace(
            discipline="matematica",
            module="A8_modelos_discretos",
            concept="1-sistemas_numericos",
            tipo="numeros_figurados_test",
            statement="Teste de enunciado para números figurados",
            difficulty=2,
            author="Test Agent",
            format="standard",
            additional_tags=[],
            subvariant_functions=[],
            has_parts=False,
            parts_count=0,
            solution=None,
            skip_preview=True
        )

        # Deve funcionar agora
        result = create_exercise_with_types_non_interactive(args)
        assert isinstance(result, str)
        assert result.startswith("MAT_A8MODELO_1SX_NFT_")  # ID gerado deve começar com isso
        # Verificar se arquivo foi criado
        exercise_file = tipo_path / f"{result}.tex"
        assert exercise_file.exists()

    finally:
        # Limpar arquivos de teste
        import shutil
        if tipo_path.exists():
            shutil.rmtree(tipo_path)

def test_full_workflow_simulation():
    """Simula o workflow completo que falhou no chat"""
    # Este teste demonstra que o workflow funciona quando o tipo existe
    # Vamos usar um tipo que já existe no projeto
    from add_exercise_with_types_non_interactive import create_exercise_with_types_non_interactive
    import argparse

    args = argparse.Namespace(
        discipline="matematica",
        module="A8_modelos_discretos",
        concept="1-sistemas_numericos",
        tipo="numeros_figurados",  # Tipo que existe
        statement="Teste simples de números figurados - workflow completo",
        difficulty=2,
        author="Test Agent",
        format="standard",
        additional_tags=[],
        subvariant_functions=[],
        has_parts=False,
        parts_count=0,
        solution=None,
        skip_preview=True
    )

    # Deve funcionar pois o tipo existe
    result = create_exercise_with_types_non_interactive(args)
    assert isinstance(result, str)
    assert result.startswith("MAT_A8MODELO_1SX_")  # Deve começar com o prefixo correto

if __name__ == "__main__":
    pytest.main([__file__, "-v"])