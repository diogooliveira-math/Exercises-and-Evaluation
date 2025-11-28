#!/usr/bin/env python3
"""
Wrapper helper to normalize calls from agents or opencode wrappers.

Accepts either:
- a single bracketed string with comma-separated key=value pairs, or
- multiple key=value arguments, or
- positional args (falls through to the add_exercise_simple script)

It will invoke `ExerciseDatabase/_tools/add_exercise_simple.py` with
explicit positional arguments to avoid shell-splitting issues.

Usage examples:
  python scripts\run_add_exercise.py "discipline=matematica, module=P4_funcoes, concept=1-generalidades_funcoes, tipo=afirmacoes_contexto, difficulty=2, statement=..."
  python scripts\run_add_exercise.py discipline=matematica module=P4_funcoes concept=1-generalidades_funcoes tipo=afirmacoes_contexto difficulty=2 statement="..."

The script returns the same exit code as the underlying script.
"""
from __future__ import annotations

import shlex
import subprocess
import sys
import logging
from pathlib import Path
import json
import tempfile
import importlib.util
import runpy

# Configurar logger
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def parse_kv_args(argv: list[str]) -> dict:
    # If a single argument contains commas, split it first
    if len(argv) == 1 and "," in argv[0]:
        s = argv[0]
        # remove surrounding brackets if present
        if s.startswith("[") and s.endswith("]"):
            s = s[1:-1]
        parts = [p.strip() for p in s.split(",") if p.strip()]
    else:
        parts = argv

    out = {}
    for p in parts:
        if "=" not in p:
            continue
        k, v = p.split("=", 1)
        out[k.strip()] = v.strip().strip('"')
    return out


def main() -> int:
    logger.info("a função é chamada com os inputs: %s", sys.argv[1:])
    if len(sys.argv) <= 1:
        print("Usage: run_add_exercise.py <key=value>... or a single comma-separated string")
        return 2

    args = sys.argv[1:]
    parsed = parse_kv_args(args)
    required = ["discipline", "module", "concept", "tipo", "difficulty", "statement"]
    missing = [k for k in required if k not in parsed or parsed[k] == '']
    # Load modules_config for better inference
    try:
        import yaml
        config_path = Path(__file__).resolve().parents[1] / 'ExerciseDatabase' / 'modules_config.yaml'
        with open(config_path, 'r', encoding='utf-8') as f:
            modules_cfg = yaml.safe_load(f)
    except Exception:
        modules_cfg = {}

    # simple synonyms map
    synonyms = {
        'funcoes': 'P4_funcoes',
        'funções': 'P4_funcoes',
        'generalidades': '1-generalidades_funcoes',
        'generalidade': '1-generalidades_funcoes',
        'preco': 'preco',
        'despesa': 'despesa',
        'taxa de juro': 'taxa_de_juro',
        'poupanca': 'poupanca',
        'procura': 'procura'
    }

    def infer_from_statement(stmt):
        stmt_l = stmt.lower()
        suggestions = {}
        score = {}
        # modules from config
        if 'matematica' in modules_cfg:
            for mod_key, mod_val in modules_cfg['matematica'].items():
                # mod_key is module id like P4_funcoes
                if isinstance(mod_key, str):
                    key_lower = mod_key.lower()
                    if key_lower in stmt_l or mod_val.get('name','').lower() in stmt_l:
                        suggestions['module'] = mod_key
                        score['module'] = score.get('module',0) + 0.9
                # concepts
                concepts = mod_val.get('concepts', []) if isinstance(mod_val, dict) else []
                for c in concepts:
                    cid = c.get('id','')
                    cname = c.get('name','').lower()
                    if cid and (cid.lower() in stmt_l or cname in stmt_l):
                        suggestions['concept'] = cid
                        score['concept'] = score.get('concept',0) + 0.9
        # synonyms
        for tok, mapped in synonyms.items():
            if tok in stmt_l:
                if mapped.startswith('P'):
                    suggestions['module'] = mapped
                    score['module'] = score.get('module',0) + 0.7
                elif mapped.startswith('1-') or mapped.startswith('0-'):
                    suggestions['concept'] = mapped
                    score['concept'] = score.get('concept',0) + 0.7
                else:
                    # tag
                    suggestions.setdefault('tags', [])
                    suggestions['tags'].append(mapped)
                    score.setdefault('tags',0)
                    score['tags'] += 0.5
        return suggestions, score

    if missing:
        # If statement provided, try to infer
        if 'statement' in parsed and parsed['statement'].strip():
            suggestions, scores = infer_from_statement(parsed['statement'])
            # Fill defaults
            if 'discipline' not in parsed:
                parsed.setdefault('discipline', 'matematica')
            if 'tipo' not in parsed:
                parsed.setdefault('tipo', 'afirmacoes_relacionais')
            if 'difficulty' not in parsed:
                parsed.setdefault('difficulty', '2')

            # Apply suggestions if confident
            confidence_threshold = 0.6
            applied = {}
            for field, val in suggestions.items():
                conf = scores.get(field, 0)
                if conf >= confidence_threshold:
                    parsed.setdefault(field, val)
                    applied[field] = { 'value': val, 'confidence': conf }

            # Recompute missing
            missing = [k for k in required if k not in parsed or parsed[k] == '']
            if missing:
                # Use agent_clarify_flow to decide accept/clarify
                tmp_path = None
                try:
                    tmp = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json', encoding='utf-8')
                    data = {
                        'status': 'needs_clarification',
                        'missing': missing,
                        'applied': applied,
                        'suggestions': suggestions,
                        'parsed': parsed,
                    }
                    tmp.write(json.dumps(data, ensure_ascii=False))
                    tmp.flush()
                    tmp_path = tmp.name
                    tmp.close()

                    clarifier = Path(__file__).resolve().parent / 'agent_clarify_flow.py'
                    # Use sys.executable to avoid relying on a literal 'python' in PATH
                    proc = subprocess.run([sys.executable, str(clarifier), '--input-file', tmp_path], capture_output=True, text=True, encoding='utf-8', errors='replace')
                    if proc.returncode != 0:
                        logger.error('Clarify flow failed: %s', proc.stderr.strip())
                        msg = {'status':'error','message':'clarify flow failed'}
                        try:
                            sys.stdout.buffer.write((json.dumps(msg, ensure_ascii=False) + "\n").encode('utf-8'))
                        except Exception:
                            print(json.dumps(msg))
                        return 3
                    clar_out = json.loads(proc.stdout)
                    if clar_out.get('status') == 'accept' and 'command' in clar_out:
                        # Execute the returned command (shell command)
                        cmd = clar_out['command']
                        logger.info('Clarifier accepted suggestions, running: %s', cmd)
                        # We expect the command to be something like: python scripts/run_add_exercise.py "discipline=..., ..."
                        try:
                            # Try to parse the command and prefer running with sys.executable when possible
                            import shlex as _shlex
                            parts = _shlex.split(cmd)
                            if parts:
                                if parts[0] in ('python', 'python3'):
                                    parts[0] = sys.executable
                                proc2 = subprocess.run(parts, capture_output=True, text=True, encoding='utf-8', errors='replace')
                            else:
                                # fallback to shell execution
                                proc2 = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')

                            if proc2.returncode == 0:
                                return proc2.returncode
                            else:
                                logger.error('Clarifier command exited with non-zero: %s', proc2.returncode)
                                logger.debug('Clarifier stdout: %s', proc2.stdout)
                                logger.debug('Clarifier stderr: %s', proc2.stderr)
                                # Fall through to fallback creation
                        except FileNotFoundError as e:
                            logger.error('Python executable not found when executing clarifier command: %s', e)
                        except Exception as e:
                            logger.exception('Error executing clarifier command: %s', e)
                        # Try to fallback to direct write using add_exercise_simple
                        try:
                            script = Path(__file__).resolve().parents[1] / "ExerciseDatabase" / "_tools" / "add_exercise_simple.py"
                            # Try import via spec
                            spec = importlib.util.spec_from_file_location('add_exercise_simple_fallback', str(script))
                            if spec and getattr(spec, 'loader', None):
                                mod = importlib.util.module_from_spec(spec)
                                spec.loader.exec_module(mod)
                                create_fn = getattr(mod, 'create_simple_exercise')
                                ex_id = create_fn(parsed.get('discipline','matematica'), parsed.get('module','DEFAULT_MODULE'), parsed.get('concept','1-default'), parsed.get('tipo','afirmacoes_relacionais'), int(parsed.get('difficulty', 2)), parsed.get('statement',''))
                            else:
                                # Use runpy as last resort
                                mod_globals = runpy.run_path(str(script))
                                create_fn = mod_globals.get('create_simple_exercise')
                                if not create_fn:
                                    raise RuntimeError('create_simple_exercise not found in add_exercise_simple.py')
                                ex_id = create_fn(parsed.get('discipline','matematica'), parsed.get('module','DEFAULT_MODULE'), parsed.get('concept','1-default'), parsed.get('tipo','afirmacoes_relacionais'), int(parsed.get('difficulty', 2)), parsed.get('statement',''))
                            logger.info('Fallback created exercise %s', ex_id)
                            try:
                                sys.stdout.buffer.write((f'SUCCESS: {ex_id}\n').encode('utf-8'))
                            except Exception:
                                print(f'SUCCESS: {ex_id}')
                            return 0
                        except Exception as ie:
                            logger.exception('Fallback failed: %s', ie)
                            return 4
                    elif clar_out.get('status') == 'clarify':
                        # Print question to caller for human interaction using UTF-8 safe write
                        try:
                            sys.stdout.buffer.write((json.dumps(clar_out, ensure_ascii=False) + "\n").encode('utf-8'))
                        except Exception:
                            print(json.dumps(clar_out))
                        return 0
                    else:
                        msg = {'status':'error','message':'unexpected clarifier output'}
                        try:
                            sys.stdout.buffer.write((json.dumps(msg, ensure_ascii=False) + "\n").encode('utf-8'))
                        except Exception:
                            print(json.dumps(msg))
                        return 3
                finally:
                    try:
                        Path(tmp_path).unlink()
                    except Exception:
                        pass
        else:
            print("Missing keys. Provide:", required)
            return 2

    script = Path(__file__).resolve().parents[1] / "ExerciseDatabase" / "_tools" / "add_exercise_simple.py"
    cmd = [sys.executable, str(script), parsed["discipline"], parsed["module"], parsed["concept"], parsed["tipo"], str(parsed["difficulty"]), parsed["statement"]]

    logger.info("Running: %s", " ".join(shlex.quote(c) for c in cmd))
    try:
        # Prepare logs directory
        logs_dir = Path(__file__).resolve().parents[1] / 'ExerciseDatabase' / 'logs'
        logs_dir.mkdir(parents=True, exist_ok=True)
        ts = __import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = logs_dir / f"run_add_exercise_{ts}.log"

        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
        except FileNotFoundError as e:
            # Likely the python executable in PATH is missing. Try to resolve using sys.executable or python3
            logger.error("Failed to run script: %s", e)
            logger.info("Attempting fallback: load add_exercise_simple module and create exercise directly")
            try:
                script = Path(__file__).resolve().parents[1] / "ExerciseDatabase" / "_tools" / "add_exercise_simple.py"
                spec = importlib.util.spec_from_file_location('add_exercise_simple_fallback', str(script))
                if spec and getattr(spec, 'loader', None):
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    create_fn = getattr(mod, 'create_simple_exercise')
                    ex_id = create_fn(parsed["discipline"], parsed["module"], parsed["concept"], parsed["tipo"], int(parsed.get("difficulty", 2)), parsed["statement"])
                else:
                    # fallback using runpy
                    mod_globals = runpy.run_path(str(script))
                    create_fn = mod_globals.get('create_simple_exercise')
                    if not create_fn:
                        raise RuntimeError('create_simple_exercise not found in add_exercise_simple.py')
                    ex_id = create_fn(parsed["discipline"], parsed["module"], parsed["concept"], parsed["tipo"], int(parsed.get("difficulty", 2)), parsed["statement"])
                # Write a simple log
                with open(log_file, 'w', encoding='utf-8') as lf:
                    lf.write(f"FALLBACK_CREATED: {ex_id}\n")
                print(f"SUCCESS: {ex_id}")
                return 0
            except Exception as ie:
                logger.exception("Fallback creation failed: %s", ie)
                return 4

        # Write log
        with open(log_file, 'w', encoding='utf-8') as lf:
            lf.write(f"COMMAND: {' '.join(cmd)}\n")
            lf.write(f"RETURNCODE: {proc.returncode}\n")
            lf.write("STDOUT:\n")
            lf.write(proc.stdout or '')
            lf.write("\nSTDERR:\n")
            lf.write(proc.stderr or '')

    except FileNotFoundError as e:
        logger.error("Failed to run script: %s", e)
        return 3

    if proc.returncode != 0:
        logger.error("Script exited with code %s", proc.returncode)
        logger.error("Stdout: %s", proc.stdout)
        logger.error("Stderr: %s", proc.stderr)
    else:
        logger.info("Script completed successfully. Stdout: %s", proc.stdout.strip())

    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
