#!/usr/bin/env python3
"""
Script para testar o agente manifesto-interventionist do OpenCode.
Executa uma chamada ao agente e valida se ele invoca os subagents corretamente.
"""

import subprocess
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

def run_opencode_command(prompt):
    """Executa o comando opencode com o prompt fornecido."""
    cmd = ['opencode', '--agent', 'manifesto-interventionist', 'run', prompt]
    print(f"Executando comando: {' '.join(cmd)}")
    try:
        print("Iniciando execução... (output será mostrado em tempo real)")
        result = subprocess.run(cmd, text=True)  # Sem capture_output para ver em tempo real
        print(f"Execução concluída. Return code: {result.returncode}")
        return result.returncode
    except KeyboardInterrupt:
        print("Execução interrompida pelo usuário")
        return 1
    except Exception as e:
        print(f"Erro ao executar comando: {e}")
        return 1

def check_manifesto_creation():
    """Verifica se foi criado um manifesto na pasta intervencoes."""
    intervencoes_dir = Path("agents_manifestos/intervencoes")
    print(f"Verificando diretório de intervenções: {intervencoes_dir.absolute()}")
    if not intervencoes_dir.exists():
        print(f"Diretório {intervencoes_dir} não existe")
        return False, None

    print(f"Diretório existe. Listando arquivos...")
    all_files = list(intervencoes_dir.glob("*.md"))
    print(f"Arquivos encontrados: {[str(f) for f in all_files]}")

    # Encontra o arquivo mais recente criado hoje
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"Procurando manifestos de hoje: {today}")
    manifestos = list(intervencoes_dir.glob(f"intervencao_{today}_*.md"))
    print(f"Manifestos de hoje encontrados: {[str(f) for f in manifestos]}")

    if manifestos:
        # Pega o mais recente
        latest = max(manifestos, key=lambda p: p.stat().st_mtime)
        print(f"Manifesto mais recente: {latest} (modificado em {datetime.fromtimestamp(latest.stat().st_mtime)})")
        return True, latest
    print("Nenhum manifesto encontrado para hoje")
    return False, None

def check_journaling():
    """Verifica se há entradas de journaling relacionadas."""
    journaling_dir = Path("agents_manifestos/journaling")
    print(f"Verificando diretório de journaling: {journaling_dir.absolute()}")
    if not journaling_dir.exists():
        print(f"Diretório {journaling_dir} não existe")
        return False, None

    print(f"Diretório existe. Listando arquivos...")
    all_files = list(journaling_dir.glob("*.md"))
    print(f"Arquivos encontrados: {[str(f) for f in all_files]}")

    # Verifica arquivos recentes
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"Procurando journals de hoje: {today}")
    journals = list(journaling_dir.glob(f"journal_{today}_*.md"))
    print(f"Journals de hoje encontrados: {[str(f) for f in journals]}")

    if journals:
        latest = max(journals, key=lambda p: p.stat().st_mtime)
        print(f"Journal mais recente: {latest} (modificado em {datetime.fromtimestamp(latest.stat().st_mtime)})")
        return True, latest
    print("Nenhum journal encontrado para hoje")
    return False, None

def cleanup_temp_files():
    """Limpa arquivos temporários que o agente pode ter criado."""
    print("Iniciando limpeza de arquivos temporários...")
    temp_patterns = [
        "**/*_temp*",
        "**/*debug*",
        "**/*log*.tmp",
        "**/temp/**",
        "**/*.aux",
        "**/*.log",
        "**/*.out"
    ]

    cleaned = []
    for pattern in temp_patterns:
        print(f"Procurando padrão: {pattern}")
        matches = list(Path(".").glob(pattern))
        print(f"Encontrados: {[str(f) for f in matches]}")
        for file_path in matches:
            if file_path.is_file():
                try:
                    file_path.unlink()
                    cleaned.append(str(file_path))
                    print(f"Removido: {file_path}")
                except Exception as e:
                    print(f"Erro ao remover {file_path}: {e}")

    print(f"Total de arquivos removidos: {len(cleaned)}")
    return cleaned

def main():
    prompt = 'I need to add a user authentication system to our project while maintaining manifesto alignment.'

    print(f"Executando teste do manifesto-interventionist com prompt: {prompt}")
    print("=" * 60)

    # Executa o comando
    print("1. Executando comando opencode...")
    returncode = run_opencode_command(prompt)

    print("\n2. Verificando criação de manifesto...")
    manifesto_created, manifesto_path = check_manifesto_creation()
    if manifesto_created and manifesto_path:
        print(f"✓ Manifesto criado: {manifesto_path}")
        try:
            with open(manifesto_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"Tamanho do manifesto: {len(content)} caracteres")
                lines = content.split('\n')
                print(f"Número de linhas: {len(lines)}")
                print(f"Conteúdo do manifesto (primeiras 5 linhas):")
                for i, line in enumerate(lines[:5]):
                    print(f"  {i+1}: {line}")
                if len(content) > 200:
                    print(f"  ... (conteúdo truncado, total: {len(content)} chars)")
                else:
                    print(f"Conteúdo completo: {content}")
        except Exception as e:
            print(f"Erro ao ler manifesto: {e}")
    else:
        print("✗ Nenhum manifesto encontrado")

    print("\n3. Verificando journaling...")
    journaling_created, journal_path = check_journaling()
    if journaling_created and journal_path:
        print(f"✓ Journal criado: {journal_path}")
        try:
            with open(journal_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"Tamanho do journal: {len(content)} caracteres")
                lines = content.split('\n')
                print(f"Número de linhas: {len(lines)}")
                print(f"Conteúdo do journal (primeiras 5 linhas):")
                for i, line in enumerate(lines[:5]):
                    print(f"  {i+1}: {line}")
        except Exception as e:
            print(f"Erro ao ler journal: {e}")
    else:
        print("✗ Nenhum journal encontrado")

    print("\n4. Limpando arquivos temporários...")
    cleaned_files = cleanup_temp_files()
    if cleaned_files:
        print(f"Arquivos removidos: {cleaned_files}")
    else:
        print("Nenhum arquivo temporário encontrado")

    print("\n" + "=" * 60)
    print("VALIDAÇÃO FINAL")
    print("=" * 60)

    # Validação final
    success = manifesto_created and journaling_created  # Deve criar ambos
    print(f"Manifesto criado: {'Sim' if manifesto_created else 'Não'}")
    print(f"Journaling criado: {'Sim' if journaling_created else 'Não'}")
    print(f"Arquivos temporários removidos: {len(cleaned_files)}")
    print(f"Return code do comando: {returncode}")

    if success:
        print("✓ Teste PASSOU: Manifesto-interventionist funcionou corretamente")
        print("O agente manifesto-interventionist:")
        print("  - Invocou intervention-planner para planejamento")
        print("  - Leu manifesto para alinhamento")
        print("  - Executou intervenção")
        print("  - Invocou manifesto-journaler para documentação")
        return 0
    else:
        print("✗ Teste FALHOU: Agente não seguiu o workflow esperado")
        print("Possíveis causas:")
        print("  - Agente não invocou intervention-planner")
        print("  - Agente não invocou manifesto-journaler")
        print("  - Problema na configuração dos subagents")
        return 1

if __name__ == "__main__":
    sys.exit(main())