r"""
Script para adicionar \vspace{3cm} no final de cada exercício,
exceto os que têm "representa graficamente".
"""

import os
import re
from pathlib import Path

def should_skip_file(content):
    """Verifica se o ficheiro deve ser ignorado (tem 'representa graficamente')"""
    return 'representa graficamente' in content.lower() or 'representa gráficamente' in content.lower()

def add_vspace_to_exercise(content):
    r"""Adiciona \vspace{3cm} no final do exercício"""
    
    # Verificar se já tem vspace no final
    if content.rstrip().endswith(r'\vspace{3cm}') or content.rstrip().endswith(r'\vspace{3cm}}'):
        return content
    
    # Remover espaços em branco do final
    content = content.rstrip()
    
    # Padrão 1: Termina com }
    if content.endswith('}'):
        return content[:-1] + '\n\\vspace{3cm}\n}\n'
    
    # Padrão 2: Não tem fechamento explícito (termina com texto ou comando)
    # Adicionar no final
    return content + '\n\n\\vspace{3cm}\n'

def process_file(filepath):
    """Processa um ficheiro .tex individual"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se deve ignorar
        if should_skip_file(content):
            print(f"⊘ Ignorado (representa graficamente): {filepath.name}")
            return False
        
        # Verificar se já tem vspace
        if '\\vspace{3cm}' in content:
            print(f"⊘ Já tem vspace: {filepath.name}")
            return False
        
        # Adicionar vspace
        new_content = add_vspace_to_exercise(content)
        
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✓ Atualizado: {filepath.name}")
            return True
        else:
            print(f"⊘ Sem alterações: {filepath.name}")
            return False
            
    except Exception as e:
        print(f"✗ Erro em {filepath.name}: {e}")
        return False

def main():
    """Processa todos os ficheiros .tex na ExerciseDatabase"""
    base_path = Path(__file__).parent.parent
    
    # Encontrar todos os .tex exceto em _output_tests e _tools
    tex_files = []
    for root, dirs, files in os.walk(base_path):
        # Ignorar diretórios específicos
        dirs[:] = [d for d in dirs if d not in ['_output_tests', '_tools', '_templates', '__pycache__']]
        
        for file in files:
            if file.endswith('.tex'):
                tex_files.append(Path(root) / file)
    
    print(f"\n🔍 Encontrados {len(tex_files)} ficheiros .tex\n")
    
    updated = 0
    for tex_file in sorted(tex_files):
        if process_file(tex_file):
            updated += 1
    
    print(f"\n✅ Concluído: {updated} ficheiros atualizados de {len(tex_files)} total")

if __name__ == '__main__':
    main()
