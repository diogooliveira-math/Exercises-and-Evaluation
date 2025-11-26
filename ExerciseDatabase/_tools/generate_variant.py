#!/usr/bin/env python3
"""
generate_variant.py

Gera uma nova versão (variante) de um exercício a partir de um ficheiro .tex
existente ou pasta de exercício com sub-variants, mantendo disciplina, módulo e conceito. 
Atualiza metadados .json e o index.json com a nova entrada.

Uso:
  python ExerciseDatabase/_tools/generate_variant.py --source "<path/to/exercise.tex>" [--strategy auto]
  python ExerciseDatabase/_tools/generate_variant.py --source "<path/to/exercise_folder>" [--strategy auto]

Regras:
- Preserva pasta de destino (mesmo conceito) e gera ID sequencial com mesmo prefixo
- Para exercícios com sub-variants: copia toda a pasta e atualiza main.tex e subvariant_*.tex
- Para exercícios simples: copia e varia o ficheiro .tex individual
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
import shutil


ROOT = Path(__file__).resolve().parent.parent
INDEX_FILE = ROOT / "index.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gerar variante de exercício a partir de um .tex ou pasta de exercício")
    parser.add_argument("--source", required=True, help="Caminho para o ficheiro .tex ou pasta do exercício original")
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


def extract_metadata_from_tex(tex_path: Path) -> Optional[dict]:
    """Extract metadata from LaTeX file comments."""
    if not tex_path.exists():
        return None
    
    content = tex_path.read_text(encoding="utf-8")
    metadata = {}
    
    # Extract metadata from comments like % meta: % key: value
    lines = content.splitlines()
    in_meta = False
    
    for line in lines:
        line = line.strip()
        if line.startswith('% meta:'):
            in_meta = True
            continue
        elif in_meta and line.startswith('% ') and ':' in line:
            # Extract key: value from % key: value
            parts = line[2:].split(':', 1)  # Remove % and split on first :
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip()
                metadata[key] = value
        elif in_meta and not line.startswith('%'):
            # End of meta block
            break
    
    return metadata if metadata else None


def add_subvariant_from_existing(exercise_dir: Path, main_tex: Path, template_subvariant: str, strategy: str) -> None:
    """Add a new sub-variant to an existing exercise using an existing subvariant as template."""
    today = datetime.now().strftime("%Y-%m-%d")
    exercise_id = exercise_dir.name

    # Find existing sub-variant files
    subvariant_files = list(exercise_dir.glob("subvariant_*.tex"))
    if not subvariant_files:
        raise SystemExit("❌ Nenhum ficheiro subvariant_*.tex encontrado na pasta.")

    # Find the next sub-variant number
    existing_numbers = []
    for sub_file in subvariant_files:
        match = re.search(r'subvariant_(\d+)\.tex', sub_file.name)
        if match:
            existing_numbers.append(int(match.group(1)))

    if not existing_numbers:
        next_num = 1
    else:
        next_num = max(existing_numbers) + 1

    print(f"[ADD] Proximo numero de sub-variant: {next_num}")

    # Use the specified subvariant as template
    template_file = exercise_dir / template_subvariant
    if not template_file.exists():
        raise SystemExit(f"❌ Template subvariant não encontrado: {template_file}")
    
    template_content = template_file.read_text(encoding="utf-8")

    # Apply variation strategy to the template
    varied_content = apply_variation(template_content, strategy)
    
    # Update subvariant header with correct subvariant number
    varied_content = update_subvariant_header(varied_content, exercise_id, next_num, today)

    # Create new sub-variant file
    new_subvariant_file = exercise_dir / f"subvariant_{next_num}.tex"
    new_subvariant_file.write_text(varied_content, encoding="utf-8")

    # Update main.tex to include the new sub-variant
    main_content = main_tex.read_text(encoding="utf-8")

    # Find the enumerate section and add the new item
    enumerate_pattern = r'(\\begin{enumerate}.*?)(\\end{enumerate})'
    match = re.search(enumerate_pattern, main_content, re.DOTALL)

    if match:
        enumerate_start = match.group(1)
        enumerate_end = match.group(2)

        # Add the new item before \end{enumerate}
        new_item = rf"\n\item \input{{subvariant_{next_num}}}"
        updated_enumerate = enumerate_start + new_item + "\n" + enumerate_end

        # Replace in main content using string replacement instead of regex
        old_enumerate = match.group(0)
        main_content = main_content.replace(old_enumerate, updated_enumerate)

        # Write back to main.tex
        main_tex.write_text(main_content, encoding="utf-8")

    # Open files for editing
    try:
        print(f"\n[TEX] Ficheiro criado: subvariant_{next_num}.tex")
        print("Abrindo ficheiros no editor para que edite a nova sub-variant (salve e feche quando terminar).")
        try:
            os.startfile(str(new_subvariant_file))
            os.startfile(str(main_tex))
        except Exception:
            print("Não foi possível abrir automaticamente. Abra manualmente os ficheiros no seu editor.")

        proceed = input("Pressione [Enter] quando terminar de editar a sub-variant (ou digite 'c' para cancelar): ").strip().lower()
        if proceed == 'c':
            # Cancel: remove the new sub-variant file and revert main.tex
            try:
                new_subvariant_file.unlink()
                # Note: We don't revert main.tex changes for simplicity
                # In a production system, you might want to create a backup
            except Exception:
                pass
            print("Operação cancelada. Sub-variant removida.")
            return

    except KeyboardInterrupt:
        print("\nOperação interrompida pelo utilizador.")
        return

    print("\n" + "="*70)
    print(">> NOVA SUB-VARIANT ADICIONADA COM SUCESSO!")
    print("="*70)
    print(f"\n[PASTA] Exercicio: {exercise_dir.name}/")
    print(f"[TEMPLATE] Baseado em: {template_subvariant}")
    print(f"[TEX] Novo ficheiro: subvariant_{next_num}.tex")
    print(f"[COUNT] Total de sub-variants: {len(subvariant_files) + 1}")
    print(f"\n[TIP] main.tex atualizado com nova entrada")
    print("\n" + "="*70)


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


def update_subvariant_header(tex: str, exercise_id: str, subvariant_num: int, today: str) -> str:
    """Update headers for a subvariant file."""
    lines = tex.splitlines()
    updated_lines = []
    exercise_id_added = False
    subvariant_header_added = False
    
    for line in lines:
        # Remove duplicate Exercise ID lines, keep only one
        if line.startswith('% Exercise ID:'):
            if not exercise_id_added:
                updated_lines.append(f'% Exercise ID: {exercise_id}')
                exercise_id_added = True
            continue
        # Update subvariant header
        elif line.startswith('% Sub-variant'):
            updated_lines.append(f'% Sub-variant {subvariant_num} for {exercise_id}')
            subvariant_header_added = True
            continue
        # Update or add date
        elif line.startswith('% Date:'):
            updated_lines.append(f'% Date: {today}')
            continue
        else:
            updated_lines.append(line)
    
    # If no Exercise ID was found, add it at the top
    if not exercise_id_added:
        updated_lines.insert(0, f'% Exercise ID: {exercise_id}')
    
    # If no subvariant header was found, add it after Exercise ID
    if not subvariant_header_added:
        insert_pos = 1 if exercise_id_added else 0
        updated_lines.insert(insert_pos, f'% Sub-variant {subvariant_num} for {exercise_id}')
    
    # Add date if not present
    if not any(line.startswith('% Date:') for line in updated_lines):
        insert_pos = 2 if exercise_id_added and subvariant_header_added else (1 if exercise_id_added else 0)
        updated_lines.insert(insert_pos, f'% Date: {today}')
    
    return '\n'.join(updated_lines)


def update_tex_header(tex: str, new_id: str, today: str) -> str:
    # Atualiza linha "% Exercise ID: ...", "% id: ...", "% Sub-variant X for ..." e "% Date: ..." se existir
    tex = re.sub(r"^%\s*Exercise ID:\s*.+$", f"% Exercise ID: {new_id}", tex, flags=re.MULTILINE)
    tex = re.sub(r"^%\s*id:\s*.+$", f"% id: {new_id}", tex, flags=re.MULTILINE)
    tex = re.sub(r"^(%\s*Sub-variant\s+\d+\s+for\s+).+$", r"\1" + new_id, tex, flags=re.MULTILINE)
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
    src_path = Path(args.source).resolve()
    if not src_path.exists():
        raise SystemExit(f"❌ Caminho não encontrado: {src_path}")

    # Check if this is a subvariant file - redirect to parent folder
    original_subvariant = None
    if not src_path.is_dir() and src_path.suffix == '.tex' and re.match(r'subvariant_\d+\.tex', src_path.name):
        parent_dir = src_path.parent
        if (parent_dir / "main.tex").exists():
            print(f"[INFO] Ficheiro subvariant detetado: {src_path.name}")
            print(f"[INFO] Sera criada uma variante focada nesta subvariant especifica.")
            original_subvariant = src_path.name  # e.g., 'subvariant_1.tex'
            src_path = parent_dir
        else:
            raise SystemExit(f"[ERROR] Ficheiro subvariant encontrado fora de contexto valido: {src_path}")

    print("="*70)
    print(">> GERADOR DE VARIANTES DE EXERCICIOS <<")
    print("="*70)

    # Determine if this is a folder-based exercise (sub-variants) or single file
    is_folder_exercise = src_path.is_dir()
    focus_single_subvariant = original_subvariant is not None

    # Ask user about subvariant strategy if applicable
    subvariant_strategy = None
    if focus_single_subvariant:
        print(f"\n>> Subvariant detetada: {original_subvariant}")
        print(f"Como deseja proceder?")
        print(f"  1. Criar VARIANTE do exercicio: nova pasta com versao modificada")
        print(f"  2. Adicionar NOVA SUB-VARIANT: novo subvariant_*.tex nesta pasta")
        print(f"  0. Cancelar")

        while True:
            choice = input(f"\nEscolha uma estratégia (1/2/0): ").strip()
            if choice in ['1', '2', '0']:
                break
            print("❌ Opção inválida. Escolha 1, 2 ou 0.")

        if choice == '0':
            print("[CANCEL] Operacao cancelada.")
            return
        elif choice == '1':
            subvariant_strategy = 'variant'
        elif choice == '2':
            subvariant_strategy = 'add_subvariant'
            
    # Handle add_subvariant strategy immediately
    if focus_single_subvariant and subvariant_strategy == 'add_subvariant':
        print(f"\n[ADD] Adicionando nova sub-variant baseada em {original_subvariant}")
        add_subvariant_from_existing(src_path, src_path / "main.tex", original_subvariant, args.strategy)
        return

    if is_folder_exercise:
        # Folder-based exercise
        src_dir = src_path
        src_id = src_path.name  # e.g., MAT_P4FUNCOE_4FIN_ANA_007
        main_tex = src_path / "main.tex"
        if not main_tex.exists():
            raise SystemExit(f"❌ main.tex não encontrado na pasta: {src_path}")

        print(f"\n[PASTA] Exercicio original (pasta): {src_path.name}")
        if focus_single_subvariant:
            if subvariant_strategy == 'variant':
                print(f"[STRATEGY] Criando variante do exercicio baseada em {original_subvariant}")
        print(f"[TEX] Ficheiro main.tex: {main_tex.name}")

        # Check if this exercise has sub-variants
        exercise_meta = extract_metadata_from_tex(main_tex) or {}
        has_subvariants = exercise_meta.get("has_subvariants", "false").lower() == "true"

        if has_subvariants and not focus_single_subvariant:
            print(f"\n>> Este exercicio tem sub-variants (alineas)!")
            print(f"O que deseja fazer?")
            print(f"  1. Criar uma NOVA PASTA de exercicio (variante completa)")
            print(f"  2. Adicionar uma NOVA SUB-VARIANT ao exercicio atual")
            print(f"  0. Cancelar")

            while True:
                choice = input(f"\nEscolha uma opção (1/2/0): ").strip()
                if choice in ['1', '2', '0']:
                    break
                print("❌ Opção inválida. Escolha 1, 2 ou 0.")

            if choice == '0':
                print("[CANCEL] Operacao cancelada.")
                return
            elif choice == '2':
                # Add new sub-variant to existing exercise
                print(f"\n[ADD] Adicionando nova sub-variant ao exercicio {src_id}")
                add_new_subvariant_to_exercise(src_dir, main_tex, args.strategy)
                return

        # Destination is the parent directory (same as source parent)
        dest_parent_dir = src_path.parent

    else:
        # Single file exercise
        src_tex = src_path
        if not src_tex.suffix == '.tex':
            raise SystemExit(f"❌ Ficheiro deve ter extensão .tex: {src_tex}")

        print(f"\n[TEX] Exercicio original: {src_tex.name}")

        # Destination is the same directory as the source
        dest_parent_dir = src_tex.parent
        src_id = src_tex.stem
    
    try:
        prefix, old_num = split_id_parts(src_id)
    except ValueError as e:
        raise SystemExit(f"❌ {e}")
    
    next_num = find_next_number(dest_parent_dir, prefix)
    # For variants, always increment to ensure unique ID
    if next_num == old_num:
        next_num = str(int(old_num) + 1).zfill(3)
    new_id = f"{prefix}{next_num}"
    
    print(f"[INFO] ID original: {src_id}")
    print(f"[NEW] Novo ID: {new_id}")
    print(f"[DIR] Destino: {dest_parent_dir.relative_to(ROOT)}")
    
    # Confirmar antes de prosseguir
    print(f"\n[WARNING] Estrategia de variacao: {args.strategy}")
    if args.strategy == "auto":
        print("   (Variacao automatica de numeros em expressoes matematicas)")
    else:
        print("   (Sem variacao - copia direta)")
    
    response = input(f"\n[QUESTION] Gerar variante? (s/n): ").strip().lower()
    if response not in ['s', 'sim', 'y', 'yes']:
        print("[CANCEL] Operacao cancelada.")
        return

    today = datetime.now().strftime("%Y-%m-%d")

    if is_folder_exercise:
        # Handle folder-based exercise
        new_folder_path = dest_parent_dir / new_id
        new_main_tex = new_folder_path / "main.tex"

        if focus_single_subvariant:
            if subvariant_strategy == 'variant':
                # Create folder and copy only main.tex and the specific subvariant
                new_folder_path.mkdir(parents=True, exist_ok=True)
                
                # Copy main.tex
                shutil.copy2(main_tex, new_main_tex)
                
                # Copy only the specific subvariant
                src_subvariant = src_dir / original_subvariant
                if src_subvariant.exists():
                    shutil.copy2(src_subvariant, new_folder_path / original_subvariant)
                else:
                    raise SystemExit(f"❌ Subvariant original não encontrada: {src_subvariant}")
                
                # Update main.tex to include only this subvariant
                main_content = new_main_tex.read_text(encoding="utf-8")
                # Replace the entire enumerate block with just this subvariant
                new_enumerate_content = rf"""\begin{{enumerate}}[label=\alph*)]

\item \input{{{original_subvariant}}}
\end{{enumerate}}"""
                # Find and replace the enumerate block
                start = main_content.find(r'\begin{enumerate}')
                end = main_content.find(r'\end{enumerate}')
                if start != -1 and end != -1:
                    end += len(r'\end{enumerate}')
                    main_content = main_content[:start] + new_enumerate_content + main_content[end:]
                new_main_tex.write_text(main_content, encoding="utf-8")
                
                # Apply variation only to the specific subvariant
                sub_file = new_folder_path / original_subvariant
                content = sub_file.read_text(encoding="utf-8")
                updated = apply_variation(content, args.strategy)
                updated = update_tex_header(updated, new_id, today)
                sub_file.write_text(updated, encoding="utf-8")
                
                # Update main.tex header
                main_content = new_main_tex.read_text(encoding="utf-8")
                main_content = update_tex_header(main_content, new_id, today)
                new_main_tex.write_text(main_content, encoding="utf-8")
                
        else:
            # Copy entire folder
            shutil.copytree(src_dir, new_folder_path)

            # Update main.tex content
            original = (new_folder_path / "main.tex").read_text(encoding="utf-8")
            varied = apply_variation(original, args.strategy)
            varied = update_tex_header(varied, new_id, today)
            (new_folder_path / "main.tex").write_text(varied, encoding="utf-8")

            # Update subvariant files if they contain IDs
            for sub_file in new_folder_path.glob("subvariant_*.tex"):
                content = sub_file.read_text(encoding="utf-8")
                updated = update_tex_header(content, new_id, today)
                sub_file.write_text(updated, encoding="utf-8")

        target_file = new_main_tex

    else:
        # Handle single file exercise (original logic)
        original = src_tex.read_text(encoding="utf-8")
        varied = apply_variation(original, args.strategy)
        varied = update_tex_header(varied, new_id, today)

        # Escrever novo .tex
        new_tex_path = dest_parent_dir / f"{new_id}.tex"
        new_tex_path.write_text(varied, encoding="utf-8")
        target_file = new_tex_path

    # Abrir a variante para edição pelo utilizador e só depois registar nos metadados/index
    try:
        skip_editing = os.environ.get('SKIP_VARIANT_EDITING', '').lower() in ('1', 'true', 'yes')
        if skip_editing:
            print(f"\n[SKIP] Pulando edição (SKIP_VARIANT_EDITING={os.environ.get('SKIP_VARIANT_EDITING')})")
        else:
            if is_folder_exercise:
                print(f"\n[PASTA] Variante criada: {new_folder_path.name}/")
                if focus_single_subvariant:
                    print(f"Abrindo main.tex e {original_subvariant} no editor para que edite (salve e feche quando terminar).")
                    try:
                        os.startfile(str(new_main_tex))
                        os.startfile(str(new_folder_path / original_subvariant))
                    except Exception:
                        print("Não foi possível abrir automaticamente. Abra manualmente os ficheiros no seu editor.")
                else:
                    print("Abrindo pasta da variante no editor para que edite os ficheiros (salve e feche quando terminar).")
                    try:
                        os.startfile(str(new_folder_path))
                    except Exception:
                        print("Não foi possível abrir automaticamente. Abra manualmente a pasta no seu editor.")
            else:
                print(f"\n[TEX] Variante criada: {new_tex_path.name}")
                print("Abrindo ficheiro no editor para que edite a variante (salve e feche quando terminar).")
                try:
                    os.startfile(str(new_tex_path))
                except Exception:
                    print("Não foi possível abrir automaticamente. Abra manualmente o ficheiro no seu editor.")

            proceed = input("Pressione [Enter] quando terminar de editar a variante (ou digite 'c' para cancelar): ").strip().lower()
            if proceed == 'c':
                # Cancelar: apagar ficheiro/pasta criado
                try:
                    if is_folder_exercise:
                        shutil.rmtree(new_folder_path)
                    else:
                        new_tex_path.unlink()
                except Exception:
                    pass
                print("Operação cancelada. Variante removida.")
                return

            # Verificar conteúdo mínimo
            if is_folder_exercise:
                new_content = (new_folder_path / "main.tex").read_text(encoding='utf-8')
            else:
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
    tipo_metadata_file = dest_parent_dir / "metadata.json"
    if is_folder_exercise:
        # For folder exercises, try to extract metadata from main.tex comments
        exercise_meta = extract_metadata_from_tex(main_tex) or {}
    else:
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
        if is_folder_exercise:
            record.update({
                "id": new_id,
                "path": str(new_folder_path.relative_to(ROOT).as_posix()),
                "points": orig_record.get("points", 0),
                "status": "active"
            })
        else:
            record.update({
                "id": new_id,
                "path": str(new_tex_path.relative_to(ROOT).as_posix()),
                "points": orig_record.get("points", 0),
                "status": "active"
            })
    else:
        # Fallback mínimo
        if is_folder_exercise:
            path = str(new_folder_path.relative_to(ROOT).as_posix())
        else:
            path = str(new_tex_path.relative_to(ROOT).as_posix())
            
        record = {
            "id": new_id,
            "path": path,
            "discipline": "matematica",
            "module": dest_parent_dir.parts[-3],  # ex.: P4_funcoes
            "module_name": "MÓDULO P4 - Funções",
            "concept": dest_parent_dir.name,
            "concept_name": dest_parent_dir.name.replace("-", " ").title(),
            "difficulty": 2,
            "type": "desenvolvimento",
            "tags": [],
            "points": 0,
            "status": "active"
        }

    index = update_index(index, record)
    INDEX_FILE.write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n" + "="*70)
    print(">> VARIANTE REGISTADA COM SUCESSO!")
    print("="*70)
    print(f"\n[TEX] Ficheiros:")
    if is_folder_exercise:
        print(f"   - Original: {src_dir.name}/")
        print(f"   - Variante: {new_folder_path.name}/")
    else:
        print(f"   - Original: {src_tex.name}")
        print(f"   - Variante: {new_tex_path.name}")
    print(f"\n[ID] IDs:")
    print(f"   - Original: {src_id}")
    print(f"   - Variante: {new_id}")
    print(f"\n[LOCATION] Localizacao:")
    if is_folder_exercise:
        print(f"   {new_folder_path.relative_to(ROOT)}/")
    else:
        print(f"   {new_tex_path.relative_to(ROOT)}")
    print(f"\n[STATS] Base de dados atualizada:")
    print(f"   - Total de exercicios: {index['total_exercises']}")
    print(f"   - Metadata do tipo atualizado")
    print(f"   - index.json atualizado")
    
    # Sugestao de proximo passo
    print(f"\n[TIP] Proximos passos:")
    if is_folder_exercise:
        print(f"   1. Verificar a variante em {new_folder_path.name}/")
    else:
        print(f"   1. Verificar a variante em {new_tex_path.name}")
    print(f"   2. Compilar/testar se necessario")
    print("\n" + "="*70)


if __name__ == "__main__":
    main()
