"""
Script para testar robustez do sistema de geração de exercícios
Testa várias combinações de disciplina, módulo, conceito e tipo
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Dict
import yaml

# Configurações
BASE_DIR = Path(__file__).parent / "ExerciseDatabase"
CONFIG_FILE = BASE_DIR / "modules_config.yaml"

def load_config():
    """Carrega configuração YAML"""
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def get_available_options():
    """Retorna todas as opções disponíveis"""
    config = load_config()
    options = {
        'disciplines': [],
        'modules': {},
        'concepts': {},
        'types': {}
    }

    for discipline, disc_data in config.items():
        if discipline not in ['difficulty_levels', 'exercise_types', 'bloom_taxonomy', 'quick_presets']:
            options['disciplines'].append(discipline)
            options['modules'][discipline] = []
            options['concepts'][discipline] = {}

            for module, mod_data in disc_data.items():
                if module != '_meta':
                    options['modules'][discipline].append(module)
                    options['concepts'][discipline][module] = []

                    concepts = mod_data.get('concepts', [])
                    for concept in concepts:
                        concept_id = concept['id']
                        options['concepts'][discipline][module].append(concept_id)

                        # Verificar tipos disponíveis
                        concept_path = BASE_DIR / discipline / module / concept_id
                        if concept_path.exists():
                            types = []
                            for item in concept_path.iterdir():
                                if item.is_dir() and (item / "metadata.json").exists():
                                    with open(item / "metadata.json", 'r', encoding='utf-8') as f:
                                        metadata = json.load(f)
                                        tipo_id = metadata.get('tipo') or metadata.get('type')
                                        if tipo_id:
                                            types.append(tipo_id)
                            options['types'][f"{discipline}/{module}/{concept_id}"] = types

    return options

def generate_test_configs(num_tests: int = 10) -> List[Dict]:
    """Gera configurações de teste"""
    options = get_available_options()
    configs = []

    import random

    for i in range(num_tests):
        # Selecionar disciplina aleatória
        discipline = random.choice(options['disciplines'])

        # Selecionar módulo aleatório
        if discipline in options['modules'] and options['modules'][discipline]:
            module = random.choice(options['modules'][discipline])
        else:
            continue

        # Selecionar conceito aleatório
        if discipline in options['concepts'] and module in options['concepts'][discipline]:
            concepts = options['concepts'][discipline][module]
            if concepts:
                concept = random.choice(concepts)
            else:
                continue
        else:
            continue

        # Selecionar tipo aleatório
        type_key = f"{discipline}/{module}/{concept}"
        if type_key in options['types'] and options['types'][type_key]:
            tipo = random.choice(options['types'][type_key])
        else:
            continue

        # Gerar enunciado baseado no tipo
        statements = {
            'determinacao_analitica': 'Determina analiticamente a função inversa de f(x) = 2x + 3.',
            'determinacao_grafica': 'Determina graficamente a função inversa de f(x) = x², para x ≥ 0.',
            'teste_reta_horizontal': 'Verifica se a função f(x) = x³ é injetiva usando o teste da reta horizontal.',
            'determinacao_analitica_plus_grafica': 'Determina analiticamente e representa graficamente a função inversa de f(x) = e^x.'
        }

        statement = statements.get(tipo, f'Exercício de teste para {tipo}')

        config = {
            "discipline": discipline,
            "module": module,
            "concept": concept,
            "tipo": tipo,
            "format": "desenvolvimento",
            "difficulty": random.randint(1, 5),
            "author": "Teste Automático",
            "statement": statement,
            "additional_tags": ["teste", "automacao"],
            "has_parts": random.choice([True, False]),
            "parts_count": random.randint(1, 3) if random.choice([True, False]) else 0,
            "solution": "Solução de exemplo" if random.choice([True, False]) else "",
            "skip_preview": True  # Pular preview para testes
        }

        configs.append(config)

    return configs

def run_test(config: Dict, config_file: str) -> bool:
    """Executa um teste individual"""
    print(f"\n🧪 Testando: {config['discipline']} / {config['module']} / {config['concept']} / {config['tipo']}")

    # Caminho para o script não-interativo
    script_path = BASE_DIR / "_tools" / "add_exercise_with_types_non_interactive.py"

    # Comando
    cmd = [
        sys.executable,
        str(script_path),
        "--config-file",
        config_file
    ]

    try:
        result = subprocess.run(
            cmd,
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            print(f"✅ Sucesso: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Erro: {result.stderr.strip()}")
            return False

    except subprocess.TimeoutExpired:
        print("⏰ Timeout")
        return False
    except Exception as e:
        print(f"💥 Exceção: {str(e)}")
        return False

def main():
    print("🚀 Iniciando testes de robustez do sistema de exercícios")

    # Verificar opções disponíveis
    options = get_available_options()
    print(f"📊 Opções disponíveis:")
    print(f"  Disciplinas: {len(options['disciplines'])}")
    print(f"  Módulos: {sum(len(mods) for mods in options['modules'].values())}")
    print(f"  Conceitos: {sum(len(concs) for concs in options['concepts'].values() for concs_mod in concs.values())}")
    print(f"  Tipos: {sum(len(tipos) for tipos in options['types'].values())}")

    # Gerar configurações de teste
    configs = generate_test_configs(50)  # 50 testes

    if not configs:
        print("❌ Nenhuma configuração válida encontrada")
        return

    print(f"📋 Gerados {len(configs)} testes")

    # Criar diretório para arquivos de config
    test_dir = Path("temp/test_configs")
    test_dir.mkdir(parents=True, exist_ok=True)

    results = {
        'total': len(configs),
        'success': 0,
        'failures': 0,
        'errors': []
    }

    # Executar testes
    for i, config in enumerate(configs):
        config_file = test_dir / f"test_{i+1:02d}.json"

        # Salvar config
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        # Executar teste
        success = run_test(config, str(config_file.absolute()))
        if success:
            results['success'] += 1
        else:
            results['failures'] += 1
            results['errors'].append({
                'config': config,
                'index': i+1
            })

    # Relatório final
    print(f"\n📊 RELATÓRIO FINAL")
    print(f"Total de testes: {results['total']}")
    print(f"Sucessos: {results['success']}")
    print(f"Falhas: {results['failures']}")
    print(".1f")

    if results['errors']:
        print(f"\n❌ Detalhes das falhas:")
        for error in results['errors']:
            config = error['config']
            print(f"  Teste {error['index']}: {config['discipline']}/{config['module']}/{config['concept']}/{config['tipo']}")

    # Salvar relatório
    report_file = Path("temp/test_report.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Relatório salvo em: {report_file}")

if __name__ == "__main__":
    main()