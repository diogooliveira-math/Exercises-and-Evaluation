"""
Automated tester that simulates sending prompts to the .opencode plugin
via the terminal and then runs the existing non-interactive add_exercise tool
for robustness testing.

Behavior:
- Generates N test configs (like test_robustness.py)
- For each test: builds an opencode-style prompt and saves it
- Runs `node .opencode/test-plugin.js` to verify plugin/tools availability
- Calls the Python non-interactive add_exercise script with the config file
- Captures stdout/stderr and saves logs per test in `temp/opencode_logs/`
- Writes a summary report `temp/opencode_terminal_test_report.json`

Usage:
  python opencode_terminal_test.py --tests 20

This script assumes Node is available on PATH and Python can run the
non-interactive add_exercise script located at
`ExerciseDatabase/_tools/add_exercise_with_types_non_interactive.py`.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
import random
import yaml

REPO_ROOT = Path(__file__).parent
EXERCISE_BASE = REPO_ROOT / "ExerciseDatabase"
CONFIG_FILE = EXERCISE_BASE / "modules_config.yaml"
NON_INTERACTIVE_SCRIPT = EXERCISE_BASE / "_tools" / "add_exercise_with_types_non_interactive.py"
OPENCODE_PLUGIN_TEST = REPO_ROOT / ".opencode" / "test-plugin.js"
LOG_DIR = REPO_ROOT / "temp" / "opencode_logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def load_config():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def get_available_options(config):
    options = {
        'disciplines': [],
        'modules': {},
        'concepts': {},
        'types': {}
    }
    for discipline, disc_data in config.items():
        if discipline in ['difficulty_levels', 'exercise_types', 'bloom_taxonomy', 'quick_presets']:
            continue
        options['disciplines'].append(discipline)
        options['modules'][discipline] = []
        options['concepts'][discipline] = {}
        for module, mod_data in disc_data.items():
            if module == '_meta':
                continue
            options['modules'][discipline].append(module)
            options['concepts'][discipline][module] = []
            for concept in mod_data.get('concepts', []):
                cid = concept['id']
                options['concepts'][discipline][module].append(cid)
                # types from FS
                concept_path = EXERCISE_BASE / discipline / module / cid
                types = []
                if concept_path.exists():
                    for item in concept_path.iterdir():
                        if item.is_dir() and (item / 'metadata.json').exists():
                            try:
                                md = json.loads((item / 'metadata.json').read_text(encoding='utf-8'))
                                tipo_id = md.get('tipo') or md.get('type')
                                if tipo_id:
                                    types.append(tipo_id)
                            except Exception:
                                continue
                options['types'][f"{discipline}/{module}/{cid}"] = types
    return options


def make_statement_for(tipo):
    map_statements = {
        'determinacao_analitica': 'Determina analiticamente a função inversa de f(x)=2x+3.',
        'determinacao_grafica': 'Determina graficamente a função inversa de f(x)=x^2, x>=0.',
        'teste_reta_horizontal': 'Verifica injetividade de f(x)=x^3 com o teste da reta horizontal.',
    }
    return map_statements.get(tipo, f'Exercício de teste para {tipo}')


def generate_configs(options, n):
    configs = []
    if not options['disciplines']:
        return configs
    for i in range(n):
        d = random.choice(options['disciplines'])
        modules = options['modules'].get(d, [])
        if not modules:
            continue
        m = random.choice(modules)
        concepts = options['concepts'][d].get(m, [])
        if not concepts:
            continue
        c = random.choice(concepts)
        type_key = f"{d}/{m}/{c}"
        tipos = options['types'].get(type_key, [])
        if not tipos:
            continue
        t = random.choice(tipos)
        cfg = {
            'discipline': d,
            'module': m,
            'concept': c,
            'tipo': t,
            'format': 'desenvolvimento',
            'difficulty': random.randint(1,5),
            'author': 'opencode-terminal-tester',
            'statement': make_statement_for(t),
            'additional_tags': ['opencode_test','terminal'],
            'has_parts': random.choice([True, False]),
            'parts_count': random.randint(1,3),
            'solution': 'Solução exemplo' if random.choice([True, False]) else '',
            'skip_preview': True
        }
        configs.append(cfg)
    return configs


def run_opencode_probe():
    """Runs the node test-plugin.js to list available opencode tools"""
    if not OPENCODE_PLUGIN_TEST.exists():
        return False, 'Plugin test script not found'
    try:
        result = subprocess.run([
            'node', str(OPENCODE_PLUGIN_TEST)
        ], cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=15)
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)


def run_non_interactive(config, config_path):
    cmd = [sys.executable, str(NON_INTERACTIVE_SCRIPT), '--config-file', str(config_path)]
    try:
        result = subprocess.run(cmd, cwd=str(EXERCISE_BASE), capture_output=True, text=True, timeout=40)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, '', str(e)


def main(tests):
    config_yaml = load_config()
    options = get_available_options(config_yaml)
    configs = generate_configs(options, tests)
    if not configs:
        print('No test configs could be generated (no types found).')
        return

    summary = {'total': len(configs), 'success': 0, 'failures': 0, 'details': []}

    # probe opencode plugin once
    ok_probe, probe_out = run_opencode_probe()
    (LOG_DIR / 'opencode_probe.txt').write_text(probe_out, encoding='utf-8')
    print('Opencode probe OK:' , ok_probe)

    for idx, cfg in enumerate(configs, start=1):
        test_dir = LOG_DIR / f'test_{idx:02d}'
        test_dir.mkdir(parents=True, exist_ok=True)
        cfg_file = test_dir / 'config.json'
        cfg_file.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding='utf-8')

        # build a human-friendly opencode prompt string
        prompt = (
            f"Create exercise: discipline={cfg['discipline']}, module={cfg['module']}, "
            f"concept={cfg['concept']}, type={cfg['tipo']}, difficulty={cfg['difficulty']}.\n"
            f"Statement: {cfg['statement']}"
        )
        (test_dir / 'prompt.txt').write_text(prompt, encoding='utf-8')

        # Log the prompt (this simulates sending prompt to opencode terminal)
        print(f"\n--- Test {idx}/{len(configs)} ---")
        print(prompt)

        # Run the non-interactive Python tool (actual creation)
        rc, out, err = run_non_interactive(cfg, cfg_file)
        (test_dir / 'stdout.txt').write_text(out, encoding='utf-8')
        (test_dir / 'stderr.txt').write_text(err, encoding='utf-8')

        success = rc == 0
        summary['details'].append({
            'index': idx,
            'config_path': str(cfg_file.resolve()),
            'returncode': rc,
            'success': success,
            'stdout_file': str((test_dir / 'stdout.txt').resolve()),
            'stderr_file': str((test_dir / 'stderr.txt').resolve()),
            'prompt_file': str((test_dir / 'prompt.txt').resolve())
        })
        if success:
            summary['success'] += 1
            print('✅ Success')
        else:
            summary['failures'] += 1
            print('❌ Failure (see logs)')

    # write summary report
    report_file = LOG_DIR / 'opencode_terminal_test_report.json'
    report_file.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding='utf-8')
    print('\nFinished. Summary saved to:', report_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--tests', type=int, default=10, help='Number of tests to run')
    args = parser.parse_args()
    main(args.tests)
