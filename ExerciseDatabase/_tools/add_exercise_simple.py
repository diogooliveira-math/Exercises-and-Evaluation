#!/usr/bin/env python3
"""
Script simplificado para adicionar exercícios - Versão para agentes
Não depende do sistema de preview complexo
Melhorias: usa logging para mensagens e fornece erros claros.
"""

import json
import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Configurar logger básico para o módulo
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Adicionar o diretório base ao path
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

# Caminho para o schema de metadados (opcional)
SCHEMA_FILE = BASE_DIR / "_tools" / "exercise_metadata_schema.json"


def validate_metadata(discipline, module, concept, tipo, difficulty, statement):
    """Validação básica dos metadados antes de criação.

    - Garante presença e tipos mínimos
    - Garante dificuldade entre 1 e 5
    - Se o pacote `jsonschema` estiver disponível e existir o ficheiro de schema,
      tentar validar contra ele (não é obrigatório ter jsonschema instalado)
    """
    errors = []
    if not isinstance(discipline, str) or not discipline.strip():
        errors.append("discipline must be a non-empty string")
    if not isinstance(module, str) or not module.strip():
        errors.append("module must be a non-empty string")
    if not isinstance(concept, str) or not concept.strip():
        errors.append("concept must be a non-empty string")
    if not isinstance(tipo, str) or not tipo.strip():
        errors.append("tipo must be a non-empty string")
    try:
        diff = int(difficulty)
        if not (1 <= diff <= 5):
            errors.append("difficulty must be between 1 and 5")
    except Exception:
        errors.append("difficulty must be an integer")
    if not isinstance(statement, str) or not statement.strip():
        errors.append("statement must be a non-empty string")

    # Tentativa de validação via jsonschema se disponível
    if SCHEMA_FILE.exists():
        try:
            import importlib
            js = importlib.import_module('jsonschema')
            with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
                schema = json.load(f)
            instance = {
                "discipline": discipline,
                "module": module,
                "concept": concept,
                "tipo": tipo,
                "difficulty": difficulty,
                "statement": statement,
            }
            js.validate(instance=instance, schema=schema)
        except ModuleNotFoundError:
            logger.debug("jsonschema not installed; skipping schema validation")
        except Exception as e:
            errors.append(f"jsonschema validation failed: {e}")

    return errors


def create_simple_exercise(discipline, module, concept, tipo, difficulty, statement):
    """Cria um exercício simples sem preview"""

    # Validação básica de metadados
    validation_errors = validate_metadata(discipline, module, concept, tipo, difficulty, statement)
    if validation_errors:
        raise ValueError("Invalid metadata: " + "; ".join(validation_errors))

    # Normalizar parâmetros
    difficulty = int(difficulty)

    # Caminhos
    tipo_path = BASE_DIR / discipline / module / concept / tipo
    tipo_path.mkdir(parents=True, exist_ok=True)

    # Metadata do tipo
    metadata_file = tipo_path / "metadata.json"
    if metadata_file.exists():
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
    else:
        metadata = {
            "tipo": tipo,
            "tipo_nome": tipo.replace('_', ' ').title(),
            "exercicios": {}
        }

    # Gerar ID
    existing = list(tipo_path.glob("*.tex"))
    number = len(existing) + 1
    disc_abbr = discipline[:3].upper()
    module_abbr = module.replace('_', '').upper()[:8]
    concept_abbr = ''.join([word[0].upper() for word in concept.split('-') if word][:3]).ljust(3, 'X')
    tipo_abbr = ''.join([word[0].upper() for word in tipo.split('_')][:3]).ljust(3, 'X')
    exercise_id = f"{disc_abbr}_{module_abbr}_{concept_abbr}_{tipo_abbr}_{number:03d}"

    # Criar conteúdo LaTeX
    today = datetime.now().strftime("%Y-%m-%d")
    content = f"""% Exercise ID: {exercise_id}
% Created: {today}
% Difficulty: {difficulty}/5

\\exercicio{{{statement}}}
"""

    # Salvar arquivo
    tex_file = tipo_path / f"{exercise_id}.tex"
    with open(tex_file, 'w', encoding='utf-8') as f:
        f.write(content)

    # Atualizar metadata
    metadata["exercicios"][exercise_id] = {
        "created": today,
        "difficulty": difficulty,
        "status": "active"
    }

    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    # Atualizar index global (simplificado)
    index_file = BASE_DIR / "index.json"
    if index_file.exists():
        with open(index_file, 'r', encoding='utf-8') as f:
            index = json.load(f)
    else:
        index = {"exercises": []}

    index_entry = {
        "id": exercise_id,
        "path": str(tex_file.relative_to(BASE_DIR)).replace("\\", "/"),
        "discipline": discipline,
        "module": module,
        "concept": concept,
        "tipo": tipo,
        "difficulty": difficulty,
        "status": "active"
    }

    index["exercises"].append(index_entry)

    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

    logger.info("Created exercise %s at %s", exercise_id, tex_file)
    return exercise_id


def parse_kv_string(s: str) -> dict:
    """Parse a single string containing comma-separated key=value pairs.

    Example formats accepted:
    - "discipline=matematica, module=P4_funcoes, concept=1-generalidades_funcoes, ..."
    - with or without surrounding brackets []
    """
    s = s.strip()
    if s.startswith("[") and s.endswith("]"):
        s = s[1:-1].strip()
    parts = [p.strip() for p in s.split(",") if p.strip()]
    out = {}
    for p in parts:
        if "=" not in p:
            continue
        k, v = p.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def main():
    # Setup persistent log file
    logs_dir = BASE_DIR / 'logs'
    logs_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = logs_dir / f"add_exercise_{ts}.log"
    fh = logging.FileHandler(log_file, encoding='utf-8')
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s'))
    logger.addHandler(fh)

    logger.info("a função é chamada com os inputs: %s", sys.argv[1:])
    logger.debug("sys.argv: %s", sys.argv)
    logger.debug("CWD: %s", os.getcwd())
    logger.debug("sys.executable: %s", sys.executable)
    logger.debug("BASE_DIR: %s", BASE_DIR)

    # Support two invocation styles for robustness:
    # 1) Positional args: <discipline> <module> <concept> <tipo> <difficulty> <statement>
    # 2) Key=value pairs either as a single bracketed string or as several

    args_map = {}
    try:
        # Support payload via --payload-file or stdin
        if len(sys.argv) == 2 and sys.argv[1].startswith('--payload-file='):
            payload_path = Path(sys.argv[1].split('=',1)[1])
            logger.info("Loading payload from file: %s", payload_path)
            with open(payload_path, 'r', encoding='utf-8') as f:
                parsed = json.load(f)
            # Validate
            for k in ["discipline","module","concept","tipo","difficulty","statement"]:
                if k not in parsed:
                    logger.error("ERROR: missing required key in payload file: %s", k)
                    sys.exit(1)
            parsed["difficulty"] = int(parsed["difficulty"])
            args_map = parsed
        elif len(sys.argv) == 2 and sys.argv[1] == '--stdin':
            logger.info("Reading payload from stdin...")
            raw = sys.stdin.read()
            parsed = json.loads(raw)
            for k in ["discipline","module","concept","tipo","difficulty","statement"]:
                if k not in parsed:
                    logger.error("ERROR: missing required key in stdin payload: %s", k)
                    sys.exit(1)
            parsed["difficulty"] = int(parsed["difficulty"])
            args_map = parsed
        elif len(sys.argv) == 7:
            # positional form
            discipline = sys.argv[1]
            module = sys.argv[2]
            concept = sys.argv[3]
            tipo = sys.argv[4]
            try:
                difficulty = int(sys.argv[5])
            except Exception:
                logger.error("ERROR: difficulty must be an integer, got: %r", sys.argv[5])
                sys.exit(1)
            statement = sys.argv[6]
            args_map = {
                "discipline": discipline,
                "module": module,
                "concept": concept,
                "tipo": tipo,
                "difficulty": difficulty,
                "statement": statement,
            }
        else:
            # Try to parse key=value style
            kv_source = None
            if len(sys.argv) == 2 and "=" in sys.argv[1]:
                kv_source = sys.argv[1]
            else:
                # join all args except script name; useful when shell split quoted content
                joined = " ".join(sys.argv[1:])
                if "=" in joined:
                    kv_source = joined

            if kv_source is None:
                logger.error("Uso: python add_exercise_simple.py <discipline> <module> <concept> <tipo> <difficulty> <statement>\nOu: python add_exercise_simple.py discipline=... module=... statement='...' (ou um único argumento com pares separados por vírgula)\nOu: python add_exercise_simple.py --payload-file=payload.json\nOu: python add_exercise_simple.py --stdin")
                sys.exit(1)

            parsed = parse_kv_string(kv_source)
            # Required keys
            required = ["discipline", "module", "concept", "tipo", "difficulty", "statement"]
            missing = [k for k in required if k not in parsed]
            if missing:
                logger.error("ERROR: missing required keys: %s", missing)
                sys.exit(1)

            try:
                parsed["difficulty"] = int(parsed["difficulty"])
            except Exception:
                logger.error("ERROR: difficulty must be an integer, got: %r", parsed.get('difficulty'))
                sys.exit(1)

            args_map = parsed

        # Clean up statement quotes if present
        statement_val = args_map["statement"]
        if isinstance(statement_val, str) and statement_val.startswith('"') and statement_val.endswith('"'):
            statement_val = statement_val[1:-1]

        try:
            exercise_id = create_simple_exercise(
                args_map["discipline"],
                args_map["module"],
                args_map["concept"],
                args_map["tipo"],
                int(args_map["difficulty"]),
                statement_val,
            )
            logger.info("SUCCESS: %s", exercise_id)
            print(f"SUCCESS: {exercise_id}")
        except ValueError as ve:
            logger.error("Validation error: %s", ve)
            sys.exit(1)
        except Exception as e:
            logger.exception("Unhandled error during exercise creation: %s", e)
            sys.exit(1)

    except Exception as outer:
        logger.exception("Fatal error: %s", outer)
        sys.exit(2)


if __name__ == "__main__":
    main()
