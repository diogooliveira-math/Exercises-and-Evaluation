#!/usr/bin/env python3
"""
Automated Exercise Generator for Exercises-and-Evaluation project.

This script automates the generation of new exercises based on agent instructions.
It creates files, updates indices, and validates automatically.

Usage:
  python ExerciseDatabase/_tools/generate_exercise_auto.py --tipo "calculo_percentagens_financeiras" --conceito "financas_pessoais" --module "P1_modelos_matematicos_para_a_cidadania"

Arguments:
  --tipo: Type of exercise (e.g., calculo_percentagens_financeiras)
  --conceito: Concept (e.g., financas_pessoais)
  --module: Module (e.g., P1_modelos_matematicos_para_a_cidadania)
  --generate_sebenta: Optional, generate sebenta after creating exercise

Requires Python 3.8+, pathlib, json, shutil, datetime, uuid.
"""
import json
import shutil
import datetime
import uuid
from pathlib import Path
import argparse
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / "ExerciseDatabase" / "index.json"
EXERCISE_DB = ROOT / "ExerciseDatabase"
SEBENTAS_TOOLS = ROOT / "SebentasDatabase" / "_tools" / "generate_sebentas.py"
TESTS = ROOT / "tests" / "quick_validation.py"

def generate_unique_id(module_abbrev, concept_abbrev, tipo_abbrev):
    """Generate unique ID based on existing exercises."""
    with open(INDEX, "r", encoding="utf-8") as f:
        index = json.load(f)

    existing_ids = [e.get("id", "") for e in index.get("exercises", []) if isinstance(e, dict)]
    base_pattern = f"{module_abbrev}_{concept_abbrev}_{tipo_abbrev}"

    counter = 1
    while True:
        candidate = f"MAT_{base_pattern}_{counter:03d}"
        if candidate not in existing_ids:
            return candidate
        counter += 1

def create_metadata_tipo(tipo, tipo_nome, conceito, conceito_nome, tema, tema_nome, disciplina, descricao, tags_tipo, caracteristicas, dificuldade_sugerida):
    """Create metadata.json for the tipo."""
    metadata = {
        "tipo": tipo,
        "tipo_nome": tipo_nome,
        "conceito": conceito,
        "conceito_nome": conceito_nome,
        "tema": tema,
        "tema_nome": tema_nome,
        "disciplina": disciplina,
        "descricao": descricao,
        "tags_tipo": tags_tipo,
        "caracteristicas": caracteristicas,
        "dificuldade_sugerida": dificuldade_sugerida,
        "exercicios": []
    }
    return metadata

def create_exercise_tex(exercise_id, tipo_nome, content):
    """Create LaTeX content for the exercise."""
    tex_content = f"""% meta:
% id: {exercise_id}
% tipo: {tipo_nome}
% author: Agent Generated
% created_at: {datetime.datetime.utcnow().isoformat()}Z

\\section{{{tipo_nome}}}

\\exercicio{{
{content}
}}
"""
    return tex_content

def create_exercise_json(exercise_id, classification, title, difficulty, tags, source_file):
    """Create JSON metadata for the exercise."""
    metadata = {
        "id": exercise_id,
        "classification": classification,
        "title": title,
        "difficulty": difficulty,
        "tags": tags,
        "source_file": source_file,
        "created_at": datetime.datetime.utcnow().isoformat() + "Z",
        "updated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "version": 1
    }
    return metadata

def update_index_json(new_exercise):
    """Update index.json with new exercise."""
    with open(INDEX, "r", encoding="utf-8") as f:
        index = json.load(f)

    # Backup
    ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    backup_path = INDEX.with_name(f"index.json.agent_backup.{ts}.json")
    shutil.copy2(INDEX, backup_path)
    print(f"Backup created: {backup_path}")

    # Add exercise
    index.setdefault("exercises", []).append(new_exercise)
    index["total_exercises"] = len(index["exercises"])
    index["last_updated"] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")

    # Update statistics (simplified)
    # TODO: Implement full statistics update

    with open(INDEX, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    print(f"Index updated: {new_exercise['id']} added")

def run_validation():
    """Run validation tests."""
    try:
        result = subprocess.run([sys.executable, str(TESTS)], capture_output=True, text=True, cwd=ROOT)
        if result.returncode == 0:
            print("Validation: PASSED")
            return True
        else:
            print(f"Validation: FAILED\n{result.stderr}")
            return False
    except Exception as e:
        print(f"Validation error: {e}")
        return False

def generate_sebenta(module, concept):
    """Generate sebenta if requested."""
    try:
        cmd = [sys.executable, str(SEBENTAS_TOOLS), "--module", module, "--concept", concept]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
        if result.returncode == 0:
            print("Sebenta generated successfully")
        else:
            print(f"Sebenta generation failed: {result.stderr}")
    except Exception as e:
        print(f"Sebenta error: {e}")

def main():
    parser = argparse.ArgumentParser(description="Automated Exercise Generator")
    parser.add_argument("--tipo", required=True, help="Tipo do exercício")
    parser.add_argument("--conceito", required=True, help="Conceito")
    parser.add_argument("--module", required=True, help="Módulo")
    parser.add_argument("--generate_sebenta", action="store_true", help="Gerar sebenta após criar exercício")

    args = parser.parse_args()

    # Abbrevs for ID generation
    module_abbrev = args.module.replace("modelos_matematicos_para_a_cidadania", "MODELO").replace("_", "").upper()[:8]
    concept_abbrev = args.conceito.upper()[:4]
    tipo_abbrev = args.tipo.replace("calculo_percentagens", "CALC").replace("_", "").upper()[:3]

    exercise_id = generate_unique_id(module_abbrev, concept_abbrev, tipo_abbrev)

    # Create directory structure
    tipo_dir = EXERCISE_DB / "matematica" / args.module / args.conceito / args.tipo
    tipo_dir.mkdir(parents=True, exist_ok=True)

    # Create metadata.json for tipo
    metadata_tipo = create_metadata_tipo(
        tipo=args.tipo,
        tipo_nome=f"Tipo: {args.tipo.replace('_', ' ').title()}",
        conceito=args.conceito,
        conceito_nome=args.conceito.replace("_", " ").title(),
        tema=args.module,
        tema_nome=f"MÓDULO {args.module.upper().replace('_', ' ')}",
        disciplina="matematica",
        descricao=f"Exercícios do tipo {args.tipo} para o conceito {args.conceito}.",
        tags_tipo=[args.tipo, args.conceito],
        caracteristicas={"requer_calculo": True, "requer_grafico": False, "complexidade_algebrica": "media"},
        dificuldade_sugerida={"min": 1, "max": 3}
    )

    with open(tipo_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata_tipo, f, ensure_ascii=False, indent=2)

    # Create exercise files
    tex_file = tipo_dir / f"{exercise_id}.tex"
    json_file = tipo_dir / f"{exercise_id}.json"

    tex_content = create_exercise_tex(
        exercise_id=exercise_id,
        tipo_nome=metadata_tipo["tipo_nome"],
        content="Conteúdo do exercício aqui. Substitua com enunciado real."
    )

    with open(tex_file, "w", encoding="utf-8") as f:
        f.write(tex_content)

    classification = {
        "discipline": "matematica",
        "module": args.module,
        "concept": args.conceito,
        "tipo": args.tipo,
        "tipo_nome": metadata_tipo["tipo_nome"],
        "tags": metadata_tipo["tags_tipo"],
        "difficulty": 2
    }

    exercise_json = create_exercise_json(
        exercise_id=exercise_id,
        classification=classification,
        title=f"Exercício {exercise_id}",
        difficulty=2,
        tags=metadata_tipo["tags_tipo"],
        source_file=str(tex_file.relative_to(EXERCISE_DB))
    )

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(exercise_json, f, ensure_ascii=False, indent=2)

    # Update index
    index_entry = {
        "id": exercise_id,
        "tipo": args.tipo,
        "tipo_nome": metadata_tipo["tipo_nome"],
        "source_file": str(tex_file.relative_to(EXERCISE_DB.parent))
    }
    update_index_json(index_entry)

    # Update tipo metadata
    metadata_tipo["exercicios"].append(exercise_id)
    with open(tipo_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata_tipo, f, ensure_ascii=False, indent=2)

    # Validation
    if run_validation():
        print(f"Exercise {exercise_id} created successfully!")
        print(f"Files: {tex_file}, {json_file}")
        if args.generate_sebenta:
            generate_sebenta(args.module, args.conceito)
    else:
        print("Validation failed. Check files.")

if __name__ == "__main__":
    main()