"""Gerador de TESTES (SebentasDatabase)

Gera um ficheiro .tex (e opcionalmente .pdf) com uma seleção de exercícios
baseada num ficheiro de configuração JSON. Os PDFs são colocados em
`SebentasDatabase/<discipline>/<module>/<concept>/<output_subdir>/pdfs/`.

NOVO v3.1: Sistema de Preview e Curadoria
- Pré-visualização do teste LaTeX antes de compilar
- Lista de exercícios selecionados para revisão
- Aprovação manual do utilizador
- Abertura automática em VS Code

Uso:
  python generate_tests.py --config SebentasDatabase/_tests_config/default_test_config.json --module P4_funcoes --concept 4-funcao_inversa

Opções:
  --no-compile  Gerar só o .tex, não compilar para PDF
  --config      Caminho para ficheiro JSON de configuração (padrão na pasta _tests_config)
  --discipline/module/concept/tipo permitem filtrar o pool de exercícios
  --no-preview  Não mostrar preview antes de compilar
  --auto-approve Aprovar automaticamente sem pedir confirmação
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import random
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import re

# Importar sistema de preview
try:
    sys.path.insert(0, str(Path(__file__).parent.parent / "ExerciseDatabase" / "_tools"))
    from preview_system import PreviewManager, create_test_preview
except ImportError:
    PreviewManager = None
    create_test_preview = None
    print("⚠️ Sistema de preview não disponível - a continuar sem pré-visualização")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXERCISE_INDEX = PROJECT_ROOT / "ExerciseDatabase" / "index.json"
SEBENTAS_DB = PROJECT_ROOT / "SebentasDatabase"
TEMPLATE_PATH = SEBENTAS_DB / "_templates" / "test_template.tex"
DEFAULT_CONFIG = SEBENTAS_DB / "_tests_config" / "default_test_config.json"

# Extensões de ficheiros temporários do LaTeX (igual às sebentas)
TEMP_EXTENSIONS = {
    '.aux', '.log', '.out', '.toc', '.lof', '.lot',
    '.fls', '.fdb_latexmk', '.synctex.gz', '.synctex(busy)',
    '.nav', '.snm', '.vrb', '.bbl', '.blg', '.idx',
    '.ind', '.ilg', '.bak', '.backup'
}


def find_config(discipline: Optional[str], module: Optional[str], concept: Optional[str], 
                cli_config: Optional[str]) -> Optional[Path]:
    """Procura configuração na seguinte ordem:
    1. CLI --config (se fornecido)
    2. tests/test_config.json local ao conceito
    3. _tests_config/default_test_config.json global
    """
    # 1. Config explícita via CLI
    if cli_config:
        config_path = Path(cli_config)
        if config_path.exists():
            return config_path
        print(f"  ⚠️ Config especificada não encontrada: {cli_config}")
    
    # 2. Config local em tests/
    if discipline and module and concept:
        local_config = SEBENTAS_DB / discipline / module / concept / "tests" / "test_config.json"
        if local_config.exists():
            print(f"  📋 Usando config local: {local_config.relative_to(PROJECT_ROOT)}")
            return local_config
    
    # 3. Config global padrão
    if DEFAULT_CONFIG.exists():
        print(f"  📋 Usando config global: {DEFAULT_CONFIG.relative_to(PROJECT_ROOT)}")
        return DEFAULT_CONFIG
    
    return None


def load_index(path: Path) -> Dict[str, Any]:
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)


def load_config(path: Path) -> Dict[str, Any]:
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)


def select_by_config(
    exercises: List[Dict[str, Any]],
    config: Dict[str, Any],
    filters: Dict[str, Optional[str]],
    rng: random.Random,
) -> List[Dict[str, Any]]:
    # Apply explicit CLI filters first
    pool = []
    for ex in exercises:
        if filters.get('discipline') and ex.get('discipline') != filters['discipline']:
            continue
        if filters.get('module') and ex.get('module') != filters['module']:
            continue
        if filters.get('concept') and ex.get('concept') != filters['concept']:
            continue
        if filters.get('tipo') and ex.get('tipo') != filters['tipo']:
            continue
        pool.append(ex)

    if not pool:
        return []

    selected: List[Dict[str, Any]] = []

    per_tipo = config.get('per_tipo') or {}
    shuffle = bool(config.get('shuffle', True))

    # If per_tipo specified, pick from each tipo
    if per_tipo:
        # Group by tipo
        by_tipo: Dict[str, List[Dict[str, Any]]] = {}
        for ex in pool:
            t = ex.get('tipo') or '__none__'
            by_tipo.setdefault(t, []).append(ex)

        for tipo, count in per_tipo.items():
            candidates = by_tipo.get(tipo, [])
            if not candidates:
                continue
            if shuffle:
                rng.shuffle(candidates)
            selected.extend(candidates[:count])

        # If config specifies total count and selection less than that, fill from remaining
        total_count = config.get('count')
        if total_count and len(selected) < total_count:
            remaining = [e for e in pool if e not in selected]
            if shuffle:
                rng.shuffle(remaining)
            selected.extend(remaining[: (total_count - len(selected)) ])

    else:
        # No per_tipo: use count or include all
        if shuffle:
            rng.shuffle(pool)
        if config.get('count'):
            selected = pool[: config['count']]
        else:
            selected = pool

    return selected


def load_template(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Template not found: {path}")
    return path.read_text(encoding='utf-8')


def build_test_content(selected: List[Dict[str, Any]], repo_root: Path) -> str:
    parts: List[str] = []
    for ex in selected:
        ex_path = repo_root / 'ExerciseDatabase' / Path(ex.get('path', ''))
        parts.append(f"% Exercise: {ex.get('id')}")
        try:
            content = ex_path.read_text(encoding='utf-8')
        except Exception as e:
            content = f"% ERROR reading {ex_path}: {e}\n\\textbf{{Erro ao carregar exercício}}"
        parts.append(content)
        parts.append('')
    return '\n'.join(parts)


def save_tex_and_compile(
    tex_content: str,
    title: str,
    header_left: str,
    header_right: str,
    output_dir: Path,
    no_compile: bool = False,
    version_label: Optional[str] = None,
    selected_exercises: Optional[List[Dict]] = None,
    config: Optional[Dict] = None,
    no_preview: bool = False,
    auto_approve: bool = False,
) -> Optional[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    suffix = f"_{version_label}" if version_label else ""
    tex_file_name = f"test_{ts}{suffix}"

    template = load_template(TEMPLATE_PATH)
    filled = template.replace('%%TITLE%%', title)
    filled = filled.replace('%%HEADER_LEFT%%', header_left)
    filled = filled.replace('%%HEADER_RIGHT%%', header_right)
    filled = filled.replace('%%CONTENT%%', tex_content)

    # PREVIEW E CONFIRMAÇÃO (se habilitado)
    if PreviewManager and not no_preview and not auto_approve:
        preview_manager = PreviewManager(auto_open=True)
        
        # Criar preview com lista de exercícios
        preview_content = create_test_preview(
            tex_file_name,
            filled,
            selected_exercises or [],
            config or {}
        )
        
        test_title = f"Teste: {title}"
        if version_label:
            test_title += f" (Versão {version_label})"
        
        if not preview_manager.show_and_confirm(preview_content, test_title):
            print(f"  ❌ Teste cancelado pelo utilizador")
            return None

    # Salvar .tex (só após confirmação)
    tex_file = output_dir / f"{tex_file_name}.tex"
    tex_file.write_text(filled, encoding='utf-8')
    print(f"  ✅ .tex gerado: {tex_file.relative_to(PROJECT_ROOT)}")

    if no_compile:
        return tex_file

    # Compile using pdflatex if available
    pdflatex = shutil.which('pdflatex')
    if not pdflatex:
        print('  ⚠️ pdflatex não encontrado - a compilação será ignorada')
        return tex_file

    print('  🔨 Compilando PDF...')
    
    # Comando pdflatex com flags igual às sebentas
    cmd = [
        pdflatex,
        '-interaction=nonstopmode',
        '-file-line-error',
        tex_file.name
    ]
    
    try:
        # Executar 2 vezes para resolver referências
        result = None
        for i in range(2):
            result = subprocess.run(
                cmd,
                cwd=str(output_dir),
                capture_output=True,
                text=True,
                timeout=60,
                encoding='utf-8',
                errors='replace'
            )
        
        # Pequeno delay para garantir sincronização do sistema de ficheiros
        import time
        time.sleep(1.0)
        
        # Verificar se PDF foi gerado (independente do exit code)
        pdf_file = output_dir / f"{tex_file.stem}.pdf"
        
        if pdf_file.exists():
            # Criar diretório pdfs se não existir
            pdfs_dir = output_dir / 'pdfs'
            pdfs_dir.mkdir(exist_ok=True)
            
            # Mover PDF para diretório pdfs
            dest = pdfs_dir / pdf_file.name
            if dest.exists():
                dest.unlink()
            pdf_file.rename(dest)
            
            print(f"  ✅ PDF gerado: {dest.relative_to(PROJECT_ROOT)}")
            
            # Limpar TODOS os ficheiros temporários incluindo .tex (mas preservar test_config.json)
            cleaned = 0
            for file in output_dir.iterdir():
                if file.is_file():
                    # Preservar test_config.json
                    if file.name == 'test_config.json':
                        continue
                    if file.suffix in TEMP_EXTENSIONS or file.name.startswith('test_'):
                        try:
                            file.unlink()
                            cleaned += 1
                        except Exception:
                            pass
            
            if cleaned > 0:
                print(f"  🧹 Limpou {cleaned} ficheiros")
            
            return dest
        else:
            print(f"  ❌ Erro na compilação - PDF não gerado")
            # Salvar log de erro se houver output
            if result and (result.stdout or result.stderr):
                logs_dir = output_dir / 'logs'
                logs_dir.mkdir(exist_ok=True)
                error_log_file = logs_dir / f"{tex_file.stem}_error.log"
                with open(error_log_file, 'w', encoding='utf-8') as f:
                    f.write("=== STDOUT ===\n")
                    f.write(result.stdout or "")
                    f.write("\n=== STDERR ===\n")
                    f.write(result.stderr or "")
                print(f"  📄 Log salvo em: {error_log_file.relative_to(PROJECT_ROOT)}")
            return None
    
    except subprocess.TimeoutExpired:
        print(f"  ⏱️ Timeout na compilação")
        return None
    except Exception as e:
        print(f"  ❌ Erro na compilação: {e}")
        return None


def parse_args():
    p = argparse.ArgumentParser(description='Gerador de TESTES (SebentasDatabase)')
    p.add_argument('--config', help='Ficheiro JSON de configuração (opcional, procura em tests/test_config.json primeiro)')
    p.add_argument('--discipline')
    p.add_argument('--module')
    p.add_argument('--concept')
    p.add_argument('--tipo')
    p.add_argument('--no-compile', action='store_true')
    p.add_argument('--create-config', action='store_true', help='Criar test_config.json local em tests/ se não existir')
    p.add_argument('--versions', type=int, help='Número de versões a gerar (default: 1)')
    p.add_argument('--version-labels', help='Rótulos separados por vírgula para as versões (ex: A,B,C)')
    p.add_argument('--seed', type=int, help='Seed base para seleção aleatória e versões')
    p.add_argument('--export-clean', action='store_true', help='Criar cópias dos PDFs finais sem sufixos/version labels em a distribution folder')
    p.add_argument('--no-preview', action='store_true', help='Não mostrar preview antes de compilar')
    p.add_argument('--auto-approve', action='store_true', help='Aprovar automaticamente sem pedir confirmação')
    return p.parse_args()


def _make_clean_copy(src: Path, distribution_dir: Path, base_name: str) -> Path:
    """Copy `src` to `distribution_dir` using `base_name`. If file exists, append a counter.
    Returns the destination Path.
    """
    distribution_dir.mkdir(parents=True, exist_ok=True)
    # sanitize base_name
    base = re.sub(r"[^A-Za-z0-9_\-]", "_", base_name.strip()) or "test"
    dest = distribution_dir / f"{base}.pdf"
    counter = 1
    while dest.exists():
        dest = distribution_dir / f"{base}_{counter}.pdf"
        counter += 1
    shutil.copy2(src, dest)
    return dest


def main():
    args = parse_args()
    if not EXERCISE_INDEX.exists():
        print(f'❌ index.json não encontrado em {EXERCISE_INDEX}')
        return

    index = load_index(EXERCISE_INDEX)
    exercises = index.get('exercises', [])

    # Determinar disciplina/módulo/conceito para buscar config local
    # (pode vir de CLI ou do primeiro exercício encontrado)
    temp_filters = {
        'discipline': args.discipline,
        'module': args.module,
        'concept': args.concept,
        'tipo': args.tipo
    }
    temp_pool = [e for e in exercises 
                 if (not temp_filters['discipline'] or e.get('discipline') == temp_filters['discipline'])
                 and (not temp_filters['module'] or e.get('module') == temp_filters['module'])
                 and (not temp_filters['concept'] or e.get('concept') == temp_filters['concept'])]
    
    discipline = args.discipline or (temp_pool[0].get('discipline') if temp_pool else None)
    module = args.module or (temp_pool[0].get('module') if temp_pool else None)
    concept = args.concept or (temp_pool[0].get('concept') if temp_pool else None)
    
    # Procurar/criar config
    config_path = find_config(discipline, module, concept, args.config)
    
    # Criar config local se solicitado e não existir
    if args.create_config and discipline and module and concept:
        local_config_path = SEBENTAS_DB / discipline / module / concept / "tests" / "test_config.json"
        if not local_config_path.exists():
            local_config_path.parent.mkdir(parents=True, exist_ok=True)
            # Copiar config padrão como template
            if DEFAULT_CONFIG.exists():
                import shutil
                shutil.copy(DEFAULT_CONFIG, local_config_path)
                print(f"  ✅ Config local criada: {local_config_path.relative_to(PROJECT_ROOT)}")
            else:
                # Criar config mínima
                default_content = {
                    "name": f"teste_{concept}",
                    "title_template": "Teste - {concept_name}",
                    "shuffle": True,
                    "count": 5
                }
                with open(local_config_path, 'w', encoding='utf-8') as f:
                    json.dump(default_content, f, indent=2, ensure_ascii=False)
                print(f"  ✅ Config local criada: {local_config_path.relative_to(PROJECT_ROOT)}")
            config_path = local_config_path
    
    config = {}
    if config_path:
        config = load_config(config_path)

    # Se a config for local (em <disc>/<module>/<concept>/tests/test_config.json),
    # forçar os filtros de disciplina/módulo/conceito a partir do path da config
    if config_path and SEBENTAS_DB in config_path.parents:
        try:
            # .../SebentasDatabase/<disc>/<module>/<concept>/tests/test_config.json
            tests_dir = config_path.parent
            concept_dir = tests_dir.parent
            module_dir = concept_dir.parent
            disc_dir = module_dir.parent
            if tests_dir.name == 'tests' and disc_dir.parent == SEBENTAS_DB:
                discipline = disc_dir.name
                module = module_dir.name
                concept = concept_dir.name
                # Atualizar filtros para seleção
                filters = {
                    'discipline': discipline,
                    'module': module,
                    'concept': concept,
                    'tipo': args.tipo,
                }
            else:
                # fallback para filtros informados
                filters = {
                    'discipline': args.discipline,
                    'module': args.module,
                    'concept': args.concept,
                    'tipo': args.tipo,
                }
        except Exception:
            filters = {
                'discipline': args.discipline,
                'module': args.module,
                'concept': args.concept,
                'tipo': args.tipo,
            }
    else:
        # filtros conforme CLI
        filters = {
            'discipline': args.discipline,
            'module': args.module,
            'concept': args.concept,
            'tipo': args.tipo,
        }

    filters = {
        'discipline': args.discipline,
        'module': args.module,
        'concept': args.concept,
        'tipo': args.tipo
    }

    # Preparar múltiplas versões
    versions = args.versions if args.versions is not None else int(config.get('versions', 1) or 1)
    # Gerar labels A, B, C... se não fornecido
    if args.version_labels:
        version_labels = [s.strip() for s in args.version_labels.split(',') if s.strip()]
    else:
        version_labels = config.get('version_labels') or []
    if not version_labels:
        # default labels A, B, C ...
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        version_labels = [alphabet[i % len(alphabet)] if versions <= len(alphabet) else str(i+1) for i in range(versions)]
    # Ajustar tamanho
    if len(version_labels) < versions:
        # completa com números
        version_labels += [str(i+1) for i in range(len(version_labels), versions)]
    version_labels = version_labels[:versions]

    seed_base = args.seed if args.seed is not None else int(datetime.now().timestamp())

    results: List[Tuple[str, Optional[Path]]] = []

    # Output path base
    # Para obter disciplina/module/concept para path e headers, precisamos de uma seleção para extrair nomes amigáveis
    # Usar uma RNG apenas para este peek (não influencia versões)
    peek_rng = random.Random(seed_base)
    peek_selected = select_by_config(exercises, config, filters, peek_rng)
    if not peek_selected:
        print('Nenhum exercício selecionado com os filtros/configuração fornecidos.')
        return

    module = args.module or (peek_selected[0].get('module') if peek_selected else '')
    concept = args.concept or (peek_selected[0].get('concept') if peek_selected else '')
    module_name = peek_selected[0].get('module_name', module) if peek_selected else module
    concept_name = peek_selected[0].get('concept_name', concept) if peek_selected else concept
    discipline = args.discipline or (peek_selected[0].get('discipline') if peek_selected else 'misc')

    output_subdir = config.get('output_subdir', 'tests')
    output_dir = SEBENTAS_DB / discipline / module / concept / output_subdir

    for idx in range(versions):
        label = version_labels[idx]
        rng = random.Random(seed_base + idx)
        selected = select_by_config(exercises, config, filters, rng)
        if not selected:
            print(f'Versão {label}: nenhum exercício selecionado.')
            results.append((label, None))
            continue

        # Build title/header por versão
        title_template = config.get('title_template', 'Teste gerado')
        # Dados base
        title = title_template.format(
            module=module,
            concept=concept,
            module_name=module_name,
            concept_name=concept_name,
            version_label=label,
            version_text='',
        )
        # Não embutir referência de versão por omissão
        embed_title = bool(config.get('embed_version_in_title', False))
        if embed_title and ('version_label' in title_template or 'version_text' in title_template):
            pass  # já está no template
        elif embed_title:
            # template não tinha placeholders; ainda assim utilizador quer embutir
            version_label_template = config.get('version_label_template', 'Versão {label}')
            version_text = version_label_template.format(label=label)
            title = f"{title} - {version_text}"

        header_left = config.get('header_left', module_name or module or '')
        # Header direito: por defeito, sem referência à versão
        embed_header = bool(config.get('embed_version_in_header', False))
        if embed_header:
            version_label_template = config.get('version_label_template', 'Versão {label}')
            version_text = version_label_template.format(label=label)
            header_right_default = f"{concept_name or concept} — {version_text}"
        else:
            header_right_default = f"{concept_name or concept}"
        header_right = config.get('header_right', header_right_default)

        content = build_test_content(selected, PROJECT_ROOT)

        result = save_tex_and_compile(
            content,
            title,
            header_left,
            header_right,
            output_dir,
            no_compile=args.no_compile,
            version_label=label,
            selected_exercises=selected,
            config=config,
            no_preview=args.no_preview,
            auto_approve=args.auto_approve,
        )
        results.append((label, result))

    # If requested, export clean copies (no version suffix) to distribution dir
    if args.export_clean:
        distribution_dir = output_dir / 'pdfs' / 'distribution'
        base_name = config.get('export_base_name') or config.get('name') or f"test_{concept}"
        for label, path in results:
            if path and path.suffix.lower() == '.pdf' and path.exists():
                try:
                    dest = _make_clean_copy(path, distribution_dir, base_name)
                    print(f"  📦 Exportado (clean): {dest.relative_to(PROJECT_ROOT)}")
                except Exception as e:
                    print(f"  ⚠️ Falha ao exportar versão {label}: {e}")
            else:
                print(f"  ℹ️ Versão {label}: sem PDF para exportar")

    # Print resumo
    for label, path in results:
        if path:
            print(f"Versão {label}: {path}")
        else:
            print(f"Versão {label}: falha ou vazia")


if __name__ == '__main__':
    main()
