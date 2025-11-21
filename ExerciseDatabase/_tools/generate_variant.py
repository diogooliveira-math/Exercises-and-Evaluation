#!/usr/bin/env python3
"""
generate_variant.py

Gera uma nova versão (variante) de um exercício a partir de um ficheiro .tex
existente, mantendo disciplina, módulo e conceito. Atualiza metadados .json e
o index.json com a nova entrada.

Uso:
  python ExerciseDatabase/_tools/generate_variant.py --source "<path/to/exercise>.tex" [--strategy auto]

Regras:
- Preserva pasta de destino (mesmo conceito) e gera ID sequencial com mesmo prefixo
- Atualiza cabeçalho do .tex (ID, Data) e versão do .json (1.0 → 1.1 por omissão)
- Estratégia "auto" tenta variações numéricas simples sem quebrar LaTeX

Requisitos: Python 3.8+
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
import os
from pathlib import Path
from typing import Optional, Tuple


ROOT = Path(__file__).resolve().parent.parent
INDEX_FILE = ROOT / "index.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gerar variante de exercício a partir de um .tex existente")
    parser.add_argument("--source", required=True, help="Caminho para o ficheiro .tex do exercício original")
    parser.add_argument("--strategy", default="auto", choices=["auto", "none"], help="Estratégia de variação de conteúdo")
    return parser.parse_args()


def split_id_parts(ex_id: str) -> Tuple[str, str]:
    """Separa prefixo e sufixo numérico do ID. Ex.: MAT_P4FUNCOE_4FIN_003 -> (MAT_P4FUNCOE_4FIN_, 003)"""
    m = re.match(r"^(.*?)(\d{3})$", ex_id)
    if not m:
        raise ValueError(f"ID inesperado: {ex_id}")
    return m.group(1), m.group(2)


def find_next_number(folder: Path, prefix: str) -> str:
    """Encontra próximo número disponível (3 dígitos) para ficheiros com prefixo no diretório."""
    max_n = 0
    for tex in folder.glob(f"{prefix}[0-9][0-9][0-9].tex"):
        stem = tex.stem
        try:
            _, num = split_id_parts(stem)
            max_n = max(max_n, int(num))
        except Exception:
            continue
    return f"{max_n + 1:03d}"


def load_json_metadata(tex_path: Path) -> Optional[dict]:
    """Tenta carregar metadados JSON com mesmo prefixo do .tex"""
    json_path = tex_path.with_suffix(".json")
    if json_path.exists():
        try:
            return json.loads(json_path.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def bump_version(ver: str) -> str:
    try:
        major, minor = ver.split(".")
        return f"{major}.{int(minor) + 1}"
    except Exception:
        return "1.1"


def vary_inline_math_simple(line: str) -> str:
    """Aplica uma variação muito simples a números inteiros dentro de $...$ (somar 1 a números pequenos)."""
    def inc_num(m: re.Match) -> str:
        num = int(m.group(0))
        if -9 <= num <= 9:
            return str(num + 1)
        return str(num)

    # Só alterar dentro de pares $...$ básicos
    def replace_in_math(match: re.Match) -> str:
        inner = match.group(1)
        inner = re.sub(r"(?<![A-Za-z])(-?\d+)(?![A-Za-z])", inc_num, inner)
        return f"${inner}$"

    return re.sub(r"\$(.+?)\$", replace_in_math, line)


def apply_variation(content: str, strategy: str) -> str:
    if strategy == "none":
        return content
    # Estratégia auto: variação leve e segura
    lines = content.splitlines()
    out = []
    for ln in lines:
        out.append(vary_inline_math_simple(ln))
    return "\n".join(out)


def update_tex_header(tex: str, new_id: str, today: str) -> str:
    # Atualiza linha "% Exercise ID: ..." e "% Date: ..." se existir
    tex = re.sub(r"^%\s*Exercise ID:\s*.+$", f"% Exercise ID: {new_id}", tex, flags=re.MULTILINE)
    tex = re.sub(r"^%\s*Date:\s*.+$", f"% Date: {today}", tex, flags=re.MULTILINE)
    # Se não existir ID, adiciona no topo
    if "% Exercise ID:" not in tex.splitlines()[0:3]:
        tex = f"% Exercise ID: {new_id}\n" + tex
    return tex


def update_index(index: dict, record: dict) -> dict:
    index.setdefault("exercises", []).append(record)
    index["total_exercises"] = len(index["exercises"])
    index["last_updated"] = datetime.now().isoformat()

    # Recalcular estatísticas
    stats = {
        "by_module": {},
        "by_concept": {},
        "by_difficulty": {},
        "by_type": {},
        "by_discipline": {}
    }
    diff_labels = {1: "Muito Fácil", 2: "Fácil", 3: "Médio", 4: "Difícil", 5: "Muito Difícil"}
    for ex in index["exercises"]:
        # Usar .get() para evitar KeyError
        module = ex.get("module", "unknown")
        concept = ex.get("concept_name", ex.get("concept", "unknown"))
        difficulty = ex.get("difficulty", 0)
        ex_type = ex.get("type", "unknown")
        discipline = ex.get("discipline", "unknown")
        
        stats["by_module"][module] = stats["by_module"].get(module, 0) + 1
        stats["by_concept"][concept] = stats["by_concept"].get(concept, 0) + 1
        dl = diff_labels.get(difficulty, "Desconhecido")
        stats["by_difficulty"][dl] = stats["by_difficulty"].get(dl, 0) + 1
        stats["by_type"][ex_type] = stats["by_type"].get(ex_type, 0) + 1
        stats["by_discipline"][discipline] = stats["by_discipline"].get(discipline, 0) + 1
    index["statistics"] = stats
    return index


def main() -> None:
    args = parse_args()
    src_tex = Path(args.source).resolve()
    if not src_tex.exists():
        raise SystemExit(f"❌ Ficheiro não encontrado: {src_tex}")

    print("="*70)
    print("🔄 GERADOR DE VARIANTES DE EXERCÍCIOS")
    print("="*70)
    print(f"\n📄 Exercício original: {src_tex.name}")
    
    # Pasta de destino (mesmo diretório do .tex)
    dest_dir = src_tex.parent
    src_id = src_tex.stem  # ex.: MAT_P4FUNCOE_4FIN_001
    
    try:
        prefix, old_num = split_id_parts(src_id)
    except ValueError as e:
        raise SystemExit(f"❌ {e}")
    
    next_num = find_next_number(dest_dir, prefix)
    new_id = f"{prefix}{next_num}"
    
    print(f"📋 ID original: {src_id}")
    print(f"🆕 Novo ID: {new_id}")
    print(f"📂 Destino: {dest_dir.relative_to(ROOT)}")
    
    # Confirmar antes de prosseguir
    print(f"\n⚠️  Estratégia de variação: {args.strategy}")
    if args.strategy == "auto":
        print("   (Variação automática de números em expressões matemáticas)")
    else:
        print("   (Sem variação - cópia direta)")
    
    response = input(f"\n❓ Gerar variante? (s/n): ").strip().lower()
    if response not in ['s', 'sim', 'y', 'yes']:
        print("❌ Operação cancelada.")
        return

    today = datetime.now().strftime("%Y-%m-%d")

    # Carregar e variar conteúdo
    original = src_tex.read_text(encoding="utf-8")
    varied = apply_variation(original, args.strategy)
    varied = update_tex_header(varied, new_id, today)

    # Escrever novo .tex
    new_tex_path = dest_dir / f"{new_id}.tex"
    new_tex_path.write_text(varied, encoding="utf-8")

    # Abrir a variante para edição pelo utilizador e só depois registar nos metadados/index
    try:
        print(f"\n📄 Variante criada: {new_tex_path.name}")
        print("Abrindo ficheiro no editor para que edite a variante (salve e feche quando terminar).")
        try:
            os.startfile(str(new_tex_path))
        except Exception:
            print("Não foi possível abrir automaticamente. Abra manualmente o ficheiro no seu editor.")

        proceed = input("Pressione [Enter] quando terminar de editar a variante (ou digite 'c' para cancelar): ").strip().lower()
        if proceed == 'c':
            # Cancelar: apagar ficheiro criado
            try:
                new_tex_path.unlink()
            except Exception:
                pass
            print("Operação cancelada. Variante removida.")
            return

        # Verificar conteúdo mínimo
        new_content = new_tex_path.read_text(encoding='utf-8')
        if '\\exercicio{' not in new_content:
            resp = input("Ficheiro não contém '\\exercicio{'. Continuar e registar? (s/n): ").strip().lower()
            if resp not in ['s', 'sim', 'y', 'yes']:
                print("Operação cancelada pelo utilizador. Variante mantida, sem registo.")
                return

    except KeyboardInterrupt:
        print("\nOperação interrompida pelo utilizador.")
        return

    # Agora atualizar metadata do tipo e index.json
    tipo_metadata_file = dest_dir / "metadata.json"
    exercise_meta = load_json_metadata(src_tex) or {}

    # Construir entrada mínima para registo no metadata do tipo
    entry = {
        "id": new_id,
        "created": exercise_meta.get("created", today),
        "modified": today,
        "author": exercise_meta.get("author", "Sistema")
    }

    if tipo_metadata_file.exists():
        try:
            tipo_meta = json.loads(tipo_metadata_file.read_text(encoding="utf-8"))
        except Exception:
            tipo_meta = {"exercicios": []}
    else:
        tipo_meta = {"exercicios": []}

    # Garantir lista
    if not isinstance(tipo_meta.get("exercicios"), list):
        tipo_meta["exercicios"] = []

    # Adicionar novo id se ainda não existir
    if new_id not in tipo_meta["exercicios"]:
        tipo_meta["exercicios"].append(new_id)

    # Guardar metadata do tipo
    tipo_metadata_file.write_text(json.dumps(tipo_meta, indent=2, ensure_ascii=False), encoding="utf-8")

    # Atualizar index.json
    if INDEX_FILE.exists():
        index = json.loads(INDEX_FILE.read_text(encoding="utf-8"))
    else:
        index = {
            "database_version": "2.0",
            "last_updated": today,
            "total_exercises": 0,
            "statistics": {},
            "exercises": []
        }

    # Encontrar registo original no index para copiar campos
    orig_record = None
    for ex in index.get("exercises", []):
        if ex.get("id") == src_id:
            orig_record = ex
            break

    # Construir registo
    if orig_record:
        record = orig_record.copy()
        record.update({
            "id": new_id,
            "path": str(new_tex_path.relative_to(ROOT).as_posix()),
            "points": orig_record.get("points", 0),
            "status": "active"
        })
    else:
        # Fallback mínimo
        record = {
            "id": new_id,
            "path": str(new_tex_path.relative_to(ROOT).as_posix()),
            "discipline": "matematica",
            "module": dest_dir.parts[-3],  # ex.: P4_funcoes
            "module_name": "MÓDULO P4 - Funções",
            "concept": dest_dir.name,
            "concept_name": dest_dir.name.replace("-", " ").title(),
            "difficulty": 2,
            "type": "desenvolvimento",
            "tags": [],
            "points": 0,
            "status": "active"
        }

    index = update_index(index, record)
    INDEX_FILE.write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n" + "="*70)
    print("✅ VARIANTE REGISTADA COM SUCESSO!")
    print("="*70)
    print(f"\n📄 Ficheiros:")
    print(f"   • Original: {src_tex.name}")
    print(f"   • Variante: {new_tex_path.name}")
    print(f"\n🆔 IDs:")
    print(f"   • Original: {src_id}")
    print(f"   • Variante: {new_id}")
    print(f"\n📍 Localização:")
    print(f"   {new_tex_path.relative_to(ROOT)}")
    print(f"\n📊 Base de dados atualizada:")
    print(f"   • Total de exercícios: {index['total_exercises']}")
    print(f"   • Metadata do tipo atualizado")
    print(f"   • index.json atualizado")
    
    # Sugestão de próximo passo
    print(f"\n💡 Próximos passos:")
    print(f"   1. Verificar a variante em {new_tex_path.name}")
    print(f"   2. Compilar/testar se necessário")
    print("\n" + "="*70)


if __name__ == "__main__":
    main()
