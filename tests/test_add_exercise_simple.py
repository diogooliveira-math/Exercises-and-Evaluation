import subprocess
import sys
from pathlib import Path
import shutil
import os
import pytest

def run_add_exercise_simple(args, base_dir):
    script = base_dir / "ExerciseDatabase" / "_tools" / "add_exercise_simple.py"
    proc = subprocess.run([
        sys.executable, str(script), *args
    ], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return proc.returncode, proc.stdout, proc.stderr

@pytest.fixture(scope="module")
def temp_base(tmp_path_factory):
    # Cria um diretório temporário isolado para os testes
    base = tmp_path_factory.mktemp("add_exercise_simple_test")
    return base

def test_add_exercise_simple_success(temp_base):
    # Argumentos válidos
    args = [
        "matematica",
        "P4_funcoes",
        "1-generalidades_funcoes",
        "interpretacao_contexto",
        "2",
        "Considere a seguinte situação: Numa loja, o preço de um produto é representado por x (em euros) e a despesa total dos clientes é dada por D(x). Indique se as seguintes afirmações são verdadeiras ou falsas, justificando a sua resposta."
    ]
    rc, out, err = run_add_exercise_simple(args, Path(os.getcwd()))
    print("[STDOUT]", out)
    print("[STDERR]", err)
    assert rc == 0
    assert "SUCCESS" in out

def test_add_exercise_simple_missing_dir(temp_base):
    # Argumentos com módulo/conceito não existentes (simula erro de diretório)
    args = [
        "matematica",
        "MODULO_INEXISTENTE",
        "CONCEITO_INEXISTENTE",
        "interpretacao_contexto",
        "2",
        "Teste de erro de diretório."
    ]
    rc, out, err = run_add_exercise_simple(args, Path(os.getcwd()))
    print("[STDOUT]", out)
    print("[STDERR]", err)
    # O script deve criar diretórios, mas pode falhar se o nome for inválido
    assert rc == 0 or rc == 1
    if rc == 1:
        assert "ERROR" in out or "ERROR" in err

def test_add_exercise_simple_long_statement(temp_base):
    # Argumento statement muito longo
    long_statement = "A" * 2000
    args = [
        "matematica",
        "P4_funcoes",
        "1-generalidades_funcoes",
        "interpretacao_contexto",
        "2",
        long_statement
    ]
    rc, out, err = run_add_exercise_simple(args, Path(os.getcwd()))
    print("[STDOUT]", out)
    print("[STDERR]", err)
    assert rc == 0
    assert "SUCCESS" in out

def test_add_exercise_simple_invalid_chars(temp_base):
    # Argumento statement com caracteres potencialmente problemáticos
    statement = "Questão com caracteres especiais: % $ & { } [ ] ~ # _ ^ \\"
    args = [
        "matematica",
        "P4_funcoes",
        "1-generalidades_funcoes",
        "interpretacao_contexto",
        "2",
        statement
    ]
    rc, out, err = run_add_exercise_simple(args, Path(os.getcwd()))
    print("[STDOUT]", out)
    print("[STDERR]", err)
    assert rc == 0
    assert "SUCCESS" in out
