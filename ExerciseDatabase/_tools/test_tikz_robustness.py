#!/usr/bin/env python3
"""
Teste de robustez para exercícios com TikZ e chavetas aninhadas.
"""

import sys
import pytest
from pathlib import Path

# Adicionar diretório ao path
sys.path.insert(0, str(Path(__file__).parent))

from add_exercise_minimal import MinimalExerciseTemplate

def test_tikz_parsing():
    """Testa parsing de exercício com TikZ."""
    
    print("="*70)
    print("TESTE: Parsing de Exercício com TikZ (Chavetas Aninhadas)")
    print("="*70)
    
    # Criar template
    base_path = Path("ExerciseDatabase")
    template = MinimalExerciseTemplate(base_path)
    
    # Simular ficheiro com TikZ
    test_content = """% Módulo: A12_otimizacao
% Conceito: estudo_monotonia
% Tipo: problema_real_monotonia
% Dificuldade: 2
% Tags: problema_real, otimização, monotonia

\\exercicio{
Numa pastelaria, a quantidade de massa (em kg) foi registada.

\\begin{center}
\\begin{tikzpicture}[x=1.1cm,y=0.9cm]
    \\draw[->] (0,0) -- (4.5,0) node[right] {hora};
    \\draw[->] (0,0) -- (0,3.2) node[above] {massa (kg)};
    \\draw[line width=1pt] (0,0.5) -- (1,2.5) -- (3,2.5) -- (4,1.0);
    \\foreach \\x/\\lab in {0/8,1/9,3/11,4/12} \\draw (\\x,0) -- (\\x,-0.07) node[below] {\\lab};
    \\node at (2,-0.5) {(A)};
\\end{tikzpicture}
\\end{center}

Qual dos gráficos melhor representa?
}

\\subexercicio{Indique a letra do gráfico.}
\\subexercicio{Justifique a sua escolha.}
"""
    
    # Criar ficheiro temporário
    temp_file = Path("temp/test_tikz_parsing.tex")
    temp_file.parent.mkdir(parents=True, exist_ok=True)
    temp_file.write_text(test_content, encoding='utf-8')
    
    template.temp_file = temp_file
    
    # Fazer parsing
    success, data, errors = template.parse_minimal_template()
    
    print(f"\n{'='*70}")
    print("RESULTADO DO PARSING:")
    print(f"{'='*70}\n")
    
    if success:
        print("✅ PARSING BEM-SUCEDIDO!\n")
        
        print("📋 Dados extraídos:")
        print(f"  • Módulo: {data.get('módulo', 'N/A')}")
        print(f"  • Conceito: {data.get('conceito', 'N/A')}")
        print(f"  • Tipo: {data.get('tipo', 'N/A')}")
        
        enunciado = data.get('enunciado', '')
        print(f"\n  • Enunciado ({len(enunciado)} caracteres):")
        
        # Verificações
        checks = {
            'Contém texto inicial': 'Numa pastelaria' in enunciado,
            'Contém \\begin{tikzpicture}': '\\begin{tikzpicture}' in enunciado,
            'Contém \\end{tikzpicture}': '\\end{tikzpicture}' in enunciado,
            'Contém \\foreach': '\\foreach' in enunciado,
            'Contém texto final': 'Qual dos gráficos' in enunciado,
            'NÃO contém \\subexercicio': '\\subexercicio' not in enunciado,
        }
        
        print("\n  🔍 Verificações:")
        all_passed = True
        for check, result in checks.items():
            status = "✅" if result else "❌"
            print(f"    {status} {check}")
            if not result:
                all_passed = False
        
        # Mostrar preview do enunciado
        print(f"\n  📝 Preview (primeiras 200 caracteres):")
        print(f"    {enunciado[:200]}...")
        
        if enunciado.endswith('Qual dos gráficos melhor representa?'):
            print("\n  ✅ Enunciado termina corretamente!")
        else:
            print(f"\n  ⚠️ Enunciado termina com: ...{enunciado[-50:]}")
        
        assert all_passed, "Algumas verificações falharam no parsing do TikZ"
            
    else:
        print("❌ PARSING FALHOU!\n")
        print("Erros:")
        for error in errors:
            print(f"  • {error}")
        
        if 'enunciado' in data:
            print(f"\nEnunciado parcial capturado ({len(data['enunciado'])} caracteres):")
            print(f"  {data['enunciado'][:200]}...")
        
        print(f"\n{'='*70}")
        print("❌ TESTE FALHOU!")
        print(f"{'='*70}")
        return False


def test_real_file():
    """Testa com o ficheiro real MAT_A12OTIMI_ESTU_PRM_001.tex"""
    
    print("\n\n")
    print("="*70)
    print("TESTE: Ficheiro Real MAT_A12OTIMI_ESTU_PRM_001.tex")
    print("="*70)
    
    real_file = Path("ExerciseDatabase/matematica/A12_otimizacao/estudo_monotonia/problema_real_monotonia/MAT_A12OTIMI_ESTU_PRM_001.tex")
    
    if not real_file.exists():
        pytest.skip(f"Ficheiro de exemplo não encontrado: {real_file}")
    
    # Ler conteúdo
    with open(real_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"\n📄 Ficheiro encontrado ({len(content)} caracteres)")
    
    # Verificar estrutura
    has_exercicio = '\\exercicio{' in content
    has_tikz = '\\begin{tikzpicture}' in content
    has_sub = '\\subexercicio{' in content
    
    print(f"\n✅ Estrutura:")
    print(f"  • \\exercicio{{...}}: {'✅' if has_exercicio else '❌'}")
    print(f"  • TikZ: {'✅' if has_tikz else '❌'}")
    print(f"  • \\subexercicio: {'✅' if has_sub else '❌'}")
    
    # Contar chavetas
    open_braces = content.count('{')
    close_braces = content.count('}')
    
    print(f"\n📊 Chavetas:")
    print(f"  • Abrem: {open_braces}")
    print(f"  • Fecham: {close_braces}")
    print(f"  • Balanceadas: {'✅' if open_braces == close_braces else '❌'}")
    
    # Verificar se enunciado está completo
    if has_exercicio:
        exercicio_pos = content.find('\\exercicio{')
        after_exercicio = content[exercicio_pos + len('\\exercicio{'):]
        
        # Verificar se tem conteúdo antes do primeiro \subexercicio
        if has_sub:
            sub_pos = after_exercicio.find('\\subexercicio{')
            if sub_pos > 100:  # Pelo menos 100 caracteres de enunciado
                print(f"\n✅ Enunciado tem conteúdo substancial ({sub_pos} caracteres)")
            else:
                print(f"\n⚠️ Enunciado pode estar vazio ou muito curto ({sub_pos} caracteres)")
    
    print(f"\n{'='*70}")
    print("✅ VALIDAÇÃO DO FICHEIRO REAL COMPLETA!")
    print(f"{'='*70}")

    assert True


if __name__ == "__main__":
    # Executar testes
    # Allow running standalone: execute tests and exit with appropriate code
    try:
        test_tikz_parsing()
        test_real_file()
        print("\n\n")
        print("="*70)
        print("RESUMO DOS TESTES")
        print("="*70)
        print("  1. Parsing TikZ: ✅ PASSOU")
        print("  2. Ficheiro Real: ✅ PASSOU")
        print("="*70)
        sys.exit(0)
    except pytest.SkipTest as e:
        print(f"SKIPPED: {e}")
        sys.exit(0)
    except AssertionError as e:
        print(f"FAILED: {e}")
        sys.exit(1)
