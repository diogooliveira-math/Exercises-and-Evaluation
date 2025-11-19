"""
Consolidate per-exercise JSON files into a single `metadata.json` per TYPE directory
and optionally remove the individual per-exercise .json files.

Uso:
  python ExerciseDatabase/_tools/consolidate_type_metadata.py --concept 4-funcao_inversa [--dry-run]

Por omissão processa apenas o conceito `4-funcao_inversa` em `P4_funcoes`.
"""
from pathlib import Path
import json
import argparse

ROOT = Path(__file__).resolve().parent.parent

def consolidate(concept_path: Path, dry_run: bool = True):
    if not concept_path.exists():
        print(f"❌ Conceito não encontrado: {concept_path}")
        return

    print(f"🔎 Consolidando tipos em: {concept_path}")

    for tipo_dir in sorted(concept_path.iterdir()):
        if not tipo_dir.is_dir():
            continue
        metadata_file = tipo_dir / "metadata.json"
        print(f"\n➡ Tipo: {tipo_dir.name}")

        # Carregar metadata existente ou inicializar
        if metadata_file.exists():
            try:
                tipo_meta = json.loads(metadata_file.read_text(encoding="utf-8"))
            except Exception:
                tipo_meta = {"tipo": tipo_dir.name, "tipo_nome": tipo_dir.name.replace('_',' ').title(), "exercicios": []}
        else:
            tipo_meta = {"tipo": tipo_dir.name, "tipo_nome": tipo_dir.name.replace('_',' ').title(), "exercicios": []}

        if not isinstance(tipo_meta.get("exercicios"), list):
            tipo_meta["exercicios"] = []

        found = 0
        # Procurar ficheiros .json (exclui metadata.json)
        for jf in sorted(tipo_dir.glob("*.json")):
            if jf.name == "metadata.json":
                continue
            try:
                data = json.loads(jf.read_text(encoding="utf-8"))
                ex_id = data.get('id') or jf.stem
            except Exception:
                ex_id = jf.stem

            if ex_id not in tipo_meta['exercicios']:
                tipo_meta['exercicios'].append(ex_id)
                print(f"   + incluir {ex_id} em metadata.json")
            else:
                print(f"   - {ex_id} já presente em metadata.json")

            found += 1

            if not dry_run:
                # remover o ficheiro JSON individual
                try:
                    jf.unlink()
                    print(f"     (removido {jf.name})")
                except Exception as e:
                    print(f"     ⚠ erro ao remover {jf.name}: {e}")

        if found == 0:
            print("   (nenhum .json individual encontrado)")
        else:
            print(f"   encontrados {found} .json individuais")

        if not dry_run:
            # gravar metadata consolidado
            try:
                metadata_file.write_text(json.dumps(tipo_meta, indent=2, ensure_ascii=False), encoding="utf-8")
                print(f"   metadata.json atualizado: {metadata_file}")
            except Exception as e:
                print(f"   ⚠ erro ao escrever metadata.json: {e}")
        else:
            print("   dry-run: metadata.json não será alterado; execute com --execute para aplicar")

def main():
    parser = argparse.ArgumentParser(description="Consolidar per-exercise JSON em metadata.json por tipo")
    parser.add_argument('--concept', default='4-funcao_inversa', help='Conceito a processar (default: 4-funcao_inversa)')
    parser.add_argument('--module', default='P4_funcoes', help='Módulo (default: P4_funcoes)')
    parser.add_argument('--discipline', default='matematica', help='Disciplina (default: matematica)')
    parser.add_argument('--execute', action='store_true', help='Executar alterações (por omissão faz dry-run)')

    args = parser.parse_args()
    concept_path = ROOT / args.discipline / args.module / args.concept
    consolidate(concept_path, dry_run=not args.execute)

if __name__ == '__main__':
    main()
