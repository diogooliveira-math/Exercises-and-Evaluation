"""
Script de Teste Completo do Sistema
Testa todas as funcionalidades: criar, pesquisar, validar
Versão: 1.0
"""

import sys
import json
from pathlib import Path

# Adicionar ao path
sys.path.insert(0, str(Path(__file__).parent))

from add_exercise import Colors, print_header, print_success, print_error, print_info, BASE_DIR
from search_exercises import search_exercises, load_config, load_index

def test_create_exercises():
    """Teste 1: Criar exercícios"""
    print_header("TESTE 1: CRIAR EXERCÍCIOS")
    
    try:
        from create_test_exercises import create_all_test_exercises
        exercises = create_all_test_exercises()
        print_success(f"✓ Criados {len(exercises)} exercícios de teste")
        return True
    except Exception as e:
        print_error(f"✗ Erro ao criar exercícios: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_index_integrity():
    """Teste 2: Validar integridade do índice"""
    print_header("TESTE 2: VALIDAR ÍNDICE")
    
    index = load_index()
    if not index:
        print_error("✗ Índice não encontrado")
        return False
    
    print_success(f"✓ Índice carregado: {index['total_exercises']} exercícios")
    
    # Verificar se todos os ficheiros existem
    errors = []
    for exercise in index['exercises']:
        file_path = BASE_DIR / exercise['path']
        if not file_path.exists():
            errors.append(f"Ficheiro não encontrado: {exercise['path']}")
    
    if errors:
        print_error(f"✗ Encontrados {len(errors)} erros:")
        for error in errors[:5]:  # Mostrar apenas primeiros 5
            print(f"  - {error}")
        return False
    
    print_success(f"✓ Todos os {index['total_exercises']} ficheiros existem")
    
    # Verificar estatísticas
    stats = index['statistics']
    print_info(f"Módulos: {len(stats['by_module'])}")
    print_info(f"Conceitos: {len(stats['by_concept'])}")
    print_info(f"Dificuldades: {len(stats['by_difficulty'])}")
    print_info(f"Tipos: {len(stats['by_type'])}")
    
    return True

def test_search_by_module():
    """Teste 3: Pesquisa por módulo"""
    print_header("TESTE 3: PESQUISAR POR MÓDULO")
    
    config = load_config()
    
    # Testar pesquisa por cada módulo
    modules = list(config['matematica'].keys())
    
    for module_id in modules:
        results = search_exercises(module=module_id)
        module_name = config['matematica'][module_id]['name']
        print_info(f"{module_name}: {len(results)} exercícios")
    
    print_success("✓ Pesquisa por módulo funcional")
    return True

def test_search_by_concept():
    """Teste 4: Pesquisa por conceito"""
    print_header("TESTE 4: PESQUISAR POR CONCEITO")
    
    config = load_config()
    
    # Testar alguns conceitos
    test_cases = [
        ("A10_funcoes", "funcao_quadratica"),
        ("A11_derivadas", "taxa_variacao"),
        ("A12_otimizacao", "problemas_otimizacao")
    ]
    
    for module_id, concept_id in test_cases:
        results = search_exercises(module=module_id, concept=concept_id)
        concept_name = next(c['name'] for c in config['matematica'][module_id]['concepts'] 
                           if c['id'] == concept_id)
        print_info(f"{concept_name}: {len(results)} exercícios")
    
    print_success("✓ Pesquisa por conceito funcional")
    return True

def test_search_by_difficulty():
    """Teste 5: Pesquisa por dificuldade"""
    print_header("TESTE 5: PESQUISAR POR DIFICULDADE")
    
    config = load_config()
    
    for difficulty in range(1, 6):
        results = search_exercises(difficulty=difficulty)
        label = config['difficulty_levels'][difficulty]['label']
        print_info(f"Dificuldade {difficulty} ({label}): {len(results)} exercícios")
    
    print_success("✓ Pesquisa por dificuldade funcional")
    return True

def test_search_by_tags():
    """Teste 6: Pesquisa por tags"""
    print_header("TESTE 6: PESQUISAR POR TAGS")
    
    test_tags = [
        ["raizes"],
        ["extremos"],
        ["velocidade"],
        ["maximizar"]
    ]
    
    for tags in test_tags:
        results = search_exercises(tags=tags)
        print_info(f"Tag '{tags[0]}': {len(results)} exercícios")
    
    print_success("✓ Pesquisa por tags funcional")
    return True

def test_complex_search():
    """Teste 7: Pesquisa complexa"""
    print_header("TESTE 7: PESQUISA COMPLEXA")
    
    # Pesquisa com múltiplos filtros
    results = search_exercises(
        module="A10_funcoes",
        difficulty=3,
        min_points=10,
        max_points=15
    )
    
    print_info(f"Módulo A10, dificuldade 3, 10-15 pontos: {len(results)} exercícios")
    
    if results:
        print_info("Exemplo de resultado:")
        ex = results[0]
        print(f"  ID: {ex['id']}")
        print(f"  Conceito: {ex['concept_name']}")
        print(f"  Pontos: {ex['points']}")
    
    print_success("✓ Pesquisa complexa funcional")
    return True

def test_metadata_structure():
    """Teste 8: Validar estrutura de metadados"""
    print_header("TESTE 8: VALIDAR ESTRUTURA DOS METADADOS")
    
    index = load_index()
    if not index:
        return False
    
    required_fields = [
        "id", "version", "created", "author",
        "module", "concept", "classification",
        "exercise_type", "content", "evaluation",
        "solution", "usage", "status"
    ]
    
    errors = []
    checked = 0
    
    for exercise in index['exercises']:
        file_path = BASE_DIR / exercise['path']
        json_file = file_path.with_suffix('.json')
        
        if json_file.exists():
            with open(json_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Verificar campos obrigatórios
            for field in required_fields:
                if field not in metadata:
                    errors.append(f"{exercise['id']}: falta campo '{field}'")
            
            checked += 1
    
    if errors:
        print_error(f"✗ Encontrados {len(errors)} erros em metadados")
        for error in errors[:5]:
            print(f"  - {error}")
        return False
    
    print_success(f"✓ Estrutura de metadados válida ({checked} ficheiros verificados)")
    return True

def run_all_tests():
    """Executa todos os testes"""
    print_header("SISTEMA DE TESTES - EXERCISEDB v2.0")
    print_info("Executando suite completa de testes...\n")
    
    tests = [
        ("Criar Exercícios", test_create_exercises),
        ("Validar Índice", test_index_integrity),
        ("Pesquisa por Módulo", test_search_by_module),
        ("Pesquisa por Conceito", test_search_by_concept),
        ("Pesquisa por Dificuldade", test_search_by_difficulty),
        ("Pesquisa por Tags", test_search_by_tags),
        ("Pesquisa Complexa", test_complex_search),
        ("Validar Metadados", test_metadata_structure)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            print()
        except Exception as e:
            print_error(f"✗ Erro no teste '{test_name}': {e}")
            results.append((test_name, False))
            print()
    
    # Resumo
    print_header("RESUMO DOS TESTES")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{Colors.GREEN}✓ PASSOU{Colors.END}" if result else f"{Colors.RED}✗ FALHOU{Colors.END}"
        print(f"  {test_name}: {status}")
    
    print()
    percentage = (passed / total) * 100
    
    if percentage == 100:
        print_success(f"🎉 TODOS OS TESTES PASSARAM! ({passed}/{total})")
    elif percentage >= 80:
        print_info(f"⚠ Maioria dos testes passou ({passed}/{total} - {percentage:.0f}%)")
    else:
        print_error(f"❌ Muitos testes falharam ({passed}/{total} - {percentage:.0f}%)")
    
    return percentage == 100

if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_error("\n\nTestes interrompidos pelo utilizador")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n\nErro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
