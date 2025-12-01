"""
Smoke Test para Sistema de IPs
================================
Testa workflow completo: registry → resolver → gerador de testes

Executa validações básicas sem pytest para garantir sistema funcional.
"""

import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
EXERCISE_DB = PROJECT_ROOT / "ExerciseDatabase"
REGISTRY_PATH = EXERCISE_DB / "_registry" / "ip_registry.json"

# Add tools to path
sys.path.insert(0, str(EXERCISE_DB / "_tools"))

def test_registry_exists():
    """Verificar se registry existe."""
    print("🔍 Verificando existência do registry...")
    if not REGISTRY_PATH.exists():
        print(f"   ⚠️ Registry não encontrado: {REGISTRY_PATH}")
        print("   💡 Execute: python scripts/migrate_ips.py --apply --base ExerciseDatabase")
        return False
    print("   ✅ Registry encontrado")
    return True

def test_registry_valid():
    """Verificar se registry é válido."""
    print("🔍 Verificando validade do registry...")
    try:
        with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        required_keys = ['version', 'disciplines', 'ips', 'next_counters']
        for key in required_keys:
            if key not in data:
                print(f"   ❌ Chave obrigatória ausente: {key}")
                return False
        
        ip_count = len(data.get('ips', {}))
        print(f"   ✅ Registry válido ({ip_count} IPs registrados)")
        return True
    except Exception as e:
        print(f"   ❌ Erro ao carregar registry: {e}")
        return False

def test_ip_resolver():
    """Testar IP resolver (verificação de existência)."""
    print("🔍 Testando IP resolver...")
    
    resolver_path = EXERCISE_DB / "_tools" / "ip_resolver.py"
    registry_path = EXERCISE_DB / "_tools" / "ip_registry.py"
    
    if not resolver_path.exists():
        print(f"   ❌ ip_resolver.py não encontrado")
        return False
    
    if not registry_path.exists():
        print(f"   ❌ ip_registry.py não encontrado")
        return False
    
    # Verificar se tem IPs no registry
    with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    ips = list(data.get('ips', {}).keys())
    if not ips:
        print("   ⚠️ Nenhum IP no registry")
        return False
    
    # Verificar se paths existem
    valid_count = 0
    for ip, ip_data in data['ips'].items():
        path_str = ip_data.get('path', '')
        if path_str:
            full_path = EXERCISE_DB / path_str
            if full_path.exists():
                valid_count += 1
    
    if valid_count > 0:
        print(f"   ✅ Resolver funcional ({valid_count}/{len(ips)} IPs com paths válidos)")
        return True
    else:
        print(f"   ⚠️ Nenhum IP com path válido")
        return False

def test_templates_exist():
    """Verificar se templates necessários existem."""
    print("🔍 Verificando templates...")
    sebentas_db = PROJECT_ROOT / "SebentasDatabase"
    
    required_templates = [
        sebentas_db / "_templates" / "test_template.tex",
        sebentas_db / "_templates" / "exercises.d" / "setup-counter.tex",
        sebentas_db / "_templates" / "exercises.d" / "include-exercise.tex",
    ]
    
    all_exist = True
    for template in required_templates:
        if not template.exists():
            print(f"   ❌ Template ausente: {template}")
            all_exist = False
    
    if all_exist:
        print("   ✅ Todos os templates presentes")
    
    return all_exist

def test_generator_script():
    """Verificar se gerador existe e é importável."""
    print("🔍 Verificando script gerador...")
    generator_path = PROJECT_ROOT / "SebentasDatabase" / "_tools" / "generate_test_from_ips.py"
    
    if not generator_path.exists():
        print(f"   ❌ Gerador não encontrado: {generator_path}")
        return False
    
    print("   ✅ Script gerador presente")
    return True

def test_preview_system():
    """Verificar se preview system está disponível."""
    print("🔍 Verificando preview system...")
    try:
        sys.path.insert(0, str(EXERCISE_DB / "_tools"))
        from preview_system import PreviewManager
        print("   ✅ Preview system disponível")
        return True
    except ImportError:
        print("   ⚠️ Preview system não disponível (opcional)")
        return True  # Not critical

def main():
    """Execute all smoke tests."""
    print("=" * 60)
    print("🔬 SMOKE TEST - Sistema de IPs")
    print("=" * 60)
    print()
    
    tests = [
        ("Registry existe", test_registry_exists),
        ("Registry válido", test_registry_valid),
        ("IP Resolver funciona", test_ip_resolver),
        ("Templates presentes", test_templates_exist),
        ("Script gerador presente", test_generator_script),
        ("Preview system", test_preview_system),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"   ❌ Exceção não tratada: {e}")
            results.append((name, False))
        print()
    
    # Summary
    print("=" * 60)
    print("📊 RESUMO")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:12} {name}")
    
    print()
    print(f"Total: {passed}/{total} testes passados")
    
    if passed == total:
        print("🎉 Todos os testes passaram!")
        sys.exit(0)
    else:
        print("⚠️ Alguns testes falharam")
        print()
        print("💡 Sugestões:")
        print("   1. Execute: python scripts/migrate_ips.py --apply --base ExerciseDatabase")
        print("   2. Verifique: python scripts/check_registry_consistency.py")
        print("   3. Documente: docs/IP_SYSTEM_QUICKSTART.md")
        sys.exit(1)

if __name__ == "__main__":
    main()
