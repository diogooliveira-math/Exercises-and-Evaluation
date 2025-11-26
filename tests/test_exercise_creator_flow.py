"""
Teste automatizado para o fluxo do agent exercise-creator (add_exercise_minimal.py)
- Cria ficheiro mínimo válido
- Executa o script
- Verifica saída esperada
"""
import subprocess
from pathlib import Path
import sys

# Caminhos
base_dir = Path(__file__).parent.parent
script_path = base_dir / "ExerciseDatabase" / "_tools" / "add_exercise_minimal.py"
temp_file = base_dir / "temp" / "TESTE_EXERCICIO_MINIMO.tex"
temp_file.parent.mkdir(exist_ok=True)

# Conteúdo mínimo válido
conteudo = r'''
% AVISO: Para submissão automática, este ficheiro deve conter APENAS o exercício final, sem exemplos ou placeholders.
% Remova sempre exemplos do template antes de guardar!

% Módulo: P4_funcoes
% Conceito: 4-funcao_inversa

\exercicio{
Determine a função inversa de $f(x) = 2x + 3$.
}

\subexercicio{Verifique que $f(f^{-1}(x)) = x$.}
'''

temp_file.write_text(conteudo, encoding="utf-8")

# Executar script com monkeypatch para usar o ficheiro criado
def run_test():
    print(f"[TESTE] A executar: {script_path} --file {temp_file}")
    proc = subprocess.run([
        sys.executable, str(script_path),
        "--file", str(temp_file)
    ], text=True, capture_output=True, encoding="utf-8", errors="replace")
    print("[STDOUT]\n", proc.stdout)
    print("[STDERR]\n", proc.stderr)
    return proc.returncode

if __name__ == "__main__":
    rc = run_test()
    if rc == 0:
        print("[TESTE] Sucesso: Exercício criado e fluxo completo!")
    else:
        print(f"[TESTE] Falhou com código {rc}")
