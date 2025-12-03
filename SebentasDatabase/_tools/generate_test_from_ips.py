"""
Sistema de Geração de Testes baseado em IPs v1.0
=================================================
Gera testes usando IPs (Itens de Prova) para selecionar exercícios.

Sistema modular compatível com estrutura QA2:
- Usa templates com exercises.d/
- Suporta sub-variants automáticos
- Numeração automática de exercícios
- Preview e curadoria integrados

Uso:
    # Por IPs específicos
    python generate_test_from_ips.py --ips 1.2.3.4.5,1.2.3.4.6
    
    # Usando wildcard para selecionar múltiplos
    python generate_test_from_ips.py --ips "1.2.3.4.*"
    
    # Com metadados personalizados
    python generate_test_from_ips.py --ips 1.2.3.4.5 --title "Teste de Funções" --author "Prof. Silva"

Flags:
    --ips              Lista de IPs separados por vírgula ou com wildcard
    --title            Título do teste (padrão: Questão de Aula)
    --author           Autor do teste (padrão: EPRALIMA)
    --output           Diretório de saída (padrão: auto)
    --no-preview       Não mostrar preview antes de compilar
    --auto-approve     Aprovar automaticamente
    --no-compile       Apenas gerar .tex, não compilar PDF
"""

import sys
import json
import argparse
import subprocess
import shutil
import os
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime

# Basic repository paths and constants (needed by resolver and generator)
# PROJECT_ROOT should be the repository root. The script lives in
# SebentasDatabase/_tools/, so use parents[2] to reach the repo root.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXERCISE_DB = PROJECT_ROOT / "ExerciseDatabase"
SEBENTAS_DB = PROJECT_ROOT / "SebentasDatabase"
EXERCISES_D_PATH = SEBENTAS_DB / "_templates" / "exercises.d"
TEMPLATE_PATH = SEBENTAS_DB / "_templates" / "test_template.tex"
REGISTRY_PATH = EXERCISE_DB / "_registry" / "ip_registry.json"

# Lightweight logger for the script
logger = logging.getLogger("generate_test_from_ips")
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logger.addHandler(ch)
logger.setLevel(logging.INFO)
logger.propagate = False

class SimpleIPResolver:
    """Simple IP resolver that doesn't use complex module imports."""

    def __init__(self):
        self.registry_data = None
        self.load_registry()

    def load_registry(self):
        """Load registry directly from JSON."""
        if not REGISTRY_PATH.exists():
            logger.error(f"Registry not found: {REGISTRY_PATH}")
            return

        try:
            with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
                self.registry_data = json.load(f)
            logger.info("✅ Registry loaded")
        except Exception as e:
            logger.error(f"Failed to load registry: {e}")

    def resolve_to_paths(self, ip_list: List[str]) -> List[Path]:
        """Resolve IPs to absolute paths."""
        if not self.registry_data:
            return []

        ips_map = self.registry_data.get('ips', {})
        resolved = []

        for ip_token in ip_list:
            ip_token = ip_token.strip()

            # Wildcard support
            if ip_token.endswith('*'):
                prefix = ip_token[:-1]
                for ip_key, ip_data in ips_map.items():
                    if ip_key.startswith(prefix):
                        path_str = ip_data.get('path', '')
                        if path_str:
                            full_path = EXERCISE_DB / path_str
                            if full_path.exists():
                                resolved.append(full_path)
            else:
                # Exact match
                ip_data = ips_map.get(ip_token)
                if ip_data:
                    path_str = ip_data.get('path', '')
                    if path_str:
                        full_path = EXERCISE_DB / path_str
                        if full_path.exists():
                            resolved.append(full_path)

        return resolved
        
        for ip_token in ip_list:
            ip_token = ip_token.strip()
            
            # Wildcard support
            if ip_token.endswith('*'):
                prefix = ip_token[:-1]
                for ip_key, ip_data in ips_map.items():
                    if ip_key.startswith(prefix):
                        path_str = ip_data.get('path', '')
                        if path_str:
                            full_path = EXERCISE_DB / path_str
                            if full_path.exists():
                                resolved.append(full_path)
            else:
                # Exact match
                ip_data = ips_map.get(ip_token)
                if ip_data:
                    path_str = ip_data.get('path', '')
                    if path_str:
                        full_path = EXERCISE_DB / path_str
                        if full_path.exists():
                            resolved.append(full_path)
        
        return resolved

try:
    RESOLVER = SimpleIPResolver()
    logger.info("✅ IP Resolver loaded (simple mode)")
except Exception as e:
    logger.error(f"❌ Failed to load IP resolver: {e}")
    RESOLVER = None

# Import preview system
try:
    from preview_system import PreviewManager
    logger.info("✅ Preview system loaded")
except ImportError:
    PreviewManager = None
    logger.warning("⚠️ Preview system not available")


class IPTestGenerator:
    """Gerador de testes baseado em IPs."""
    
    def __init__(self, no_preview: bool = False, auto_approve: bool = False, no_compile: bool = False):
        self.no_preview = no_preview
        self.auto_approve = auto_approve
        self.no_compile = no_compile
        self.preview_manager = PreviewManager(auto_open=True) if PreviewManager and not no_preview else None
        
    def resolve_ips(self, ip_list: List[str]) -> List[Path]:
        """Resolve IPs para paths absolutos de exercícios."""
        if not RESOLVER:
            logger.error("❌ IP Resolver não disponível")
            return []
        
        resolved = []
        for ip_token in ip_list:
            ip_token = ip_token.strip()
            logger.info(f"🔍 Resolvendo IP: {ip_token}")
            
            try:
                paths = RESOLVER.resolve_to_paths([ip_token])
                if paths:
                    resolved.extend(paths)
                    logger.info(f"   ✅ {len(paths)} exercício(s) encontrado(s)")
                else:
                    logger.warning(f"   ⚠️ Nenhum exercício encontrado para IP: {ip_token}")
            except Exception as e:
                logger.error(f"   ❌ Erro ao resolver IP {ip_token}: {e}")
        
        return resolved
    
    def generate_exercises_tex(self, exercise_paths: List[Path], output_dir: Path) -> str:
        """Gera ficheiro exercises.tex com includes modulares."""
        exercises_tex = output_dir / "exercises.tex"
        exercises_d_dir = output_dir / "exercises.d"
        exercises_d_dir.mkdir(parents=True, exist_ok=True)
        
        # Copiar ficheiros de suporte de exercises.d
        for support_file in ["setup-counter.tex", "include-exercise.tex"]:
            src = EXERCISES_D_PATH / support_file
            dst = exercises_d_dir / support_file
            if src.exists():
                dst.write_text(src.read_text(encoding='utf-8'), encoding='utf-8')
        
        # Gerar conteúdo do exercises.tex
        content = []
        content.append("% Modular exercise inclusion file")
        content.append("% Generated by generate_test_from_ips.py")
        content.append("")
        content.append("% Load counter and include wrapper")
        content.append(r"\input{exercises.d/setup-counter}")
        content.append(r"\input{exercises.d/include-exercise}")
        content.append("")
        content.append("% Exercise inclusions")
        
        for exercise_path in exercise_paths:
            # Determinar path relativo de output_dir para exercise
            try:
                rel_path = exercise_path.relative_to(output_dir)
            except ValueError:
                # Não está no mesmo tree, usar path absoluto via ../
                # Calcular path relativo manualmente
                rel_path = Path("../../..")  / "ExerciseDatabase" / exercise_path.relative_to(EXERCISE_DB)
            
            # Se o exercício tem main.tex (sub-variants), usar main
            main_tex = exercise_path / "main.tex"
            if main_tex.exists():
                include_path = rel_path / "main"
            else:
                # Exercício único
                include_path = rel_path.parent / rel_path.stem
            
            content.append(f"\\IncludeExercise{{{include_path}}}")
        
        exercises_tex.write_text('\n'.join(content), encoding='utf-8')
        logger.info(f"✅ Gerado exercises.tex com {len(exercise_paths)} exercício(s)")
        return str(exercises_tex)
    
    def generate_test(self, 
                      ips: List[str],
                      title: str = "Questão de Aula",
                      author: str = "EPRALIMA - Escola Profissional Alto Lima",
                      output_dir: Optional[Path] = None) -> Optional[Path]:
        """Gera teste completo a partir de IPs."""
        
        logger.info("=" * 60)
        logger.info(f"📝 Geração de Teste por IPs")
        logger.info(f"   IPs solicitados: {', '.join(ips)}")
        logger.info("=" * 60)
        
        # 1. Resolver IPs para paths
        exercise_paths = self.resolve_ips(ips)
        if not exercise_paths:
            logger.error("❌ Nenhum exercício resolvido. Abortando.")
            return None
        
        logger.info(f"✅ {len(exercise_paths)} exercício(s) resolvido(s)")
        
        # 2. Determinar output directory
        if output_dir is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = SEBENTAS_DB / "tests" / f"test_ips_{timestamp}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 3. Copiar referência QA2 para o output (manter estrutura e ficheiros)
        ref_qa2 = PROJECT_ROOT / 'reference' / 'QA2'
        copied_qa2 = output_dir / 'QA2'
        try:
            if ref_qa2.exists():
                # copytree requires destination not to exist
                if copied_qa2.exists():
                    shutil.rmtree(copied_qa2)
                shutil.copytree(ref_qa2, copied_qa2)
                logger.info(f"✅ Copiada referência QA2 para: {copied_qa2}")
            else:
                logger.warning(f"⚠️ Referência QA2 não encontrada em: {ref_qa2}")
        except Exception as e:
            logger.warning(f"⚠️ Falha ao copiar QA2: {e}")

        # 4. Gerar exercises.tex — sobrescrever o ficheiro de exercises dentro da cópia QA2/tex
        try:
            qa2_tex_dir = copied_qa2 / 'tex'
            qa2_exercises_tex = qa2_tex_dir / 'exercises.tex'
            # If the copied structure has exercises.tex, overwrite; otherwise create in output root
            exercises_target = qa2_exercises_tex if qa2_exercises_tex.parent.exists() else output_dir / 'exercises.tex'
            # Build content similar to reference: load counter/include wrapper then list IncludeExercise lines
            lines = []
            lines.append("% Modular exercise inclusion file (generated)")
            lines.append("% Generated by generate_test_from_ips.py")
            lines.append("")
            lines.append("% Load path, counter and the include wrapper")
            # Use relative path inside QA2/tex: exercises.d is expected at same level
            lines.append(r"\input{exercises.d/input-path}")
            lines.append(r"\input{exercises.d/setup-counter}")
            lines.append(r"\input{exercises.d/include-exercise}")
            lines.append("")
            lines.append("% Exercise inclusions")

            for exercise_path in exercise_paths:
                # Compute the path to refer from QA2/tex to ExerciseDatabase (../../..)
                # Keep the reference-style path: ../../../ExerciseDatabase/<relpath>
                try:
                    rel = exercise_path.relative_to(EXERCISE_DB)
                except Exception:
                    rel = exercise_path
                # compute relative path from QA2/tex to the repository's ExerciseDatabase
                try:
                    qa2_tex_dir = qa2_tex_dir  # defined above
                except NameError:
                    qa2_tex_dir = copied_qa2 / 'tex'
                rel_to_exdb = Path(os.path.relpath(EXERCISE_DB, qa2_tex_dir))
                ref_path = rel_to_exdb / rel
                # If exercise contains main.tex, reference the main, else reference folder or file
                if (exercise_path / 'main.tex').exists():
                    include_ref = str((ref_path / 'main').as_posix())
                else:
                    include_ref = str(ref_path.as_posix())
                lines.append(f"\\IncludeExercise{{{include_ref}}}")

            exercises_target.write_text('\n'.join(lines), encoding='utf-8')
            logger.info(f"✅ Gerado exercises.tex em: {exercises_target}")
        except Exception as e:
            logger.error(f"❌ Erro ao gerar exercises.tex: {e}")

        # 5. Gerar ficheiro principal do teste
        test_tex = output_dir / "test.tex"
        if not TEMPLATE_PATH.exists():
            logger.error(f"❌ Template não encontrado: {TEMPLATE_PATH}")
            return None

        template_content = TEMPLATE_PATH.read_text(encoding='utf-8')

        # Determine module_name from the first resolved exercise (if available)
        module_name = None
        try:
            if exercise_paths:
                # exercise_paths are absolute: EXERCISE_DB / discipline / module / ...
                first = exercise_paths[0]
                parts = first.relative_to(EXERCISE_DB).parts
                if len(parts) >= 2:
                    discipline = parts[0]
                    module_key = parts[1]
                    # Try to read modules_config.yaml
                    modules_cfg_path = EXERCISE_DB / 'modules_config.yaml'
                    if modules_cfg_path.exists():
                        try:
                            import yaml as _yaml
                            mcfg = _yaml.safe_load(modules_cfg_path.read_text(encoding='utf-8')) or {}
                            discipline_cfg = mcfg.get(discipline, {})
                            module_cfg = discipline_cfg.get(module_key, {})
                            module_name = module_cfg.get('name')
                        except Exception:
                            module_name = None
        except Exception:
            module_name = None

        # If module_name found use the requested title format, otherwise fall back to provided title
        final_title = f"Questão de aula do {module_name}" if module_name else title

        # Substituir placeholders
        template_content = template_content.replace("%%TITLE%%", final_title)
        template_content = template_content.replace("%%AUTHOR%%", author)
        template_content = template_content.replace("%%DATE%%", datetime.now().strftime("%d/%m/%Y"))
        template_content = template_content.replace("%%HEADER_LEFT%%", title)
        template_content = template_content.replace("%%HEADER_RIGHT%%", datetime.now().strftime("%d/%m/%Y"))
        template_content = template_content.replace("%%CONTENT%%", rf"\\input{{{include_exercises_ref}}}")

        test_tex.write_text(template_content, encoding='utf-8')
        logger.info(f"✅ Teste gerado: {test_tex}")
        
        # 5. Preview (se habilitado)
        if self.preview_manager:
            preview_content = {
                "test.tex": template_content,
                "exercises.tex": (output_dir / "exercises.tex").read_text(encoding='utf-8'),
                "_info.txt": f"Teste com {len(exercise_paths)} exercícios\nIPs: {', '.join(ips)}"
            }
            
            if not self.preview_manager.show_and_confirm(preview_content, f"Teste: {title}"):
                logger.warning("❌ Geração cancelada pelo utilizador")
                return None
        
        # 6. Compilar (se habilitado)
        if not self.no_compile:
            logger.info("🔨 Compilando PDF...")
            try:
                result = subprocess.run(
                    ["pdflatex", "-interaction=nonstopmode", "test.tex"],
                    cwd=str(output_dir),
                    capture_output=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    pdf_path = output_dir / "test.pdf"
                    if pdf_path.exists():
                        logger.info(f"✅ PDF compilado: {pdf_path}")
                        self.cleanup_temp_files(output_dir)
                        return pdf_path
                    else:
                        logger.error("❌ PDF não foi gerado")
                else:
                    logger.error(f"❌ Erro na compilação LaTeX (exit code {result.returncode})")
                    logger.debug(result.stdout.decode('utf-8', errors='ignore'))
            except Exception as e:
                logger.error(f"❌ Exceção durante compilação: {e}")
        
        return test_tex
    
    def cleanup_temp_files(self, directory: Path):
        """Remove ficheiros temporários do LaTeX."""
        temp_extensions = {'.aux', '.log', '.out', '.fls', '.fdb_latexmk', '.synctex.gz'}
        for temp_file in directory.glob("*"):
            if temp_file.suffix in temp_extensions:
                try:
                    temp_file.unlink()
                except Exception:
                    pass


def main():
    parser = argparse.ArgumentParser(description="Gerador de testes baseado em IPs")
    parser.add_argument("--ips", required=True, help="Lista de IPs separados por vírgula (ex: 1.2.3.4.5,1.2.3.4.6 ou 1.2.3.4.*)")
    parser.add_argument("--exercise-path", action='append', help="Caminho para um exercício (absoluto, relativo ao repo ou contendo 'ExerciseDatabase') - pode usar múltiplos")
    parser.add_argument("--title", default="Questão de Aula", help="Título do teste")
    parser.add_argument("--author", default="EPRALIMA - Escola Profissional Alto Lima", help="Autor do teste")
    parser.add_argument("--output", type=str, help="Diretório de saída (padrão: auto)")
    parser.add_argument("--no-preview", action="store_true", help="Não mostrar preview")
    parser.add_argument("--auto-approve", action="store_true", help="Aprovar automaticamente")
    parser.add_argument("--no-compile", action="store_true", help="Não compilar PDF")
    
    args = parser.parse_args()
    
    # Parse IPs
    ip_list = [ip.strip() for ip in args.ips.split(",")] if args.ips else []

    # Parse exercise paths (if provided)
    exercise_path_inputs = args.exercise_path or []

    # By default the test will include `exercises.tex` at repo root; when
    # exercise-paths are provided we will place the generated exercises under
    # the copied QA2 tree and include `QA2/tex/exercises` from the test.
    include_exercises_ref = "exercises"
    
    # Output directory
    output_dir = Path(args.output) if args.output else None
    
    # Generate test
    generator = IPTestGenerator(
        no_preview=args.no_preview,
        auto_approve=args.auto_approve,
        no_compile=args.no_compile
    )
    
    # If exercise paths provided, convert them to absolute Paths and pass to generator
    if exercise_path_inputs:
        ex_paths = []

        def normalize_exercise_input(p: str) -> Path:
            """Try multiple strategies to convert an input string to an existing exercise Path.

            Strategies (in order):
            - If the string contains 'ExerciseDatabase', take the substring after it and join with EXERCISE_DB.
            - Treat the string as an absolute or repo-relative path.
            - Try to locate the exercise by name under EXERCISE_DB using rglob (first match).
            - As a last resort return the repo-relative candidate (may not exist).
            """
            s = p.strip()

            # 1) direct 'ExerciseDatabase' reference
            if 'ExerciseDatabase' in s:
                idx = s.find('ExerciseDatabase')
                rel = s[idx + len('ExerciseDatabase'):].lstrip('/\\')
                candidate = EXERCISE_DB / Path(rel)
                logger.info(f"normalize: detected 'ExerciseDatabase' in input -> candidate={candidate}")
                if candidate.exists():
                    logger.info(f"normalize: candidate exists -> {candidate}")
                    return candidate

            # 2) absolute or repo-relative
            cand = Path(s)
            if not cand.is_absolute():
                cand = PROJECT_ROOT / s
            logger.info(f"normalize: trying repo-relative/absolute -> {cand} (exists={cand.exists()})")
            if cand.exists():
                return cand

            # 3) try searching by basename under ExerciseDatabase
            try:
                name = Path(s).name
                matches = list(EXERCISE_DB.rglob(name))
                logger.info(f"normalize: searching EXERCISE_DB for name='{name}' -> found {len(matches)} matches")
                if matches:
                    return matches[0]
            except Exception:
                pass

            # 4) try to recover from odd prefixes (e.g. accidentally prefixed with SebentasDatabase)
            try:
                if 'ExerciseDatabase' in s:
                    # already tried above; fallthrough
                    pass
                else:
                    # look for substring 'ExerciseDatabase' anywhere in a longer path
                    if 'ExerciseDatabase' in s:
                        idx = s.find('ExerciseDatabase')
                        rel = s[idx + len('ExerciseDatabase'):].lstrip('/\\')
                        candidate = EXERCISE_DB / Path(rel)
                        if candidate.exists():
                            return candidate
            except Exception:
                pass

            # fallback: return the repo-relative candidate even if it may not exist
            logger.info(f"normalize: fallback candidate -> {cand}")
            return cand

        for p in exercise_path_inputs:
            exp = normalize_exercise_input(p)
            if not exp.exists():
                logger.warning(f"⚠️ Exercise path resolved but not found on disk: {exp} (input: {p})")
            ex_paths.append(exp)

        # create output dir if not exists
        if output_dir is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = SEBENTAS_DB / "tests" / f"test_ips_{timestamp}"
        output_dir.mkdir(parents=True, exist_ok=True)

        # 1) Copy reference QA2 into output_dir/QA2 so the structure matches
        ref_qa2 = PROJECT_ROOT / 'reference' / 'QA2'
        copied_qa2 = output_dir / 'QA2'
        try:
            if ref_qa2.exists():
                if copied_qa2.exists():
                    shutil.rmtree(copied_qa2)
                shutil.copytree(ref_qa2, copied_qa2)
                logger.info(f"✅ Copiada referência QA2 para: {copied_qa2}")
            else:
                logger.warning(f"⚠️ Referência QA2 não encontrada em: {ref_qa2}")
        except Exception as e:
            logger.warning(f"⚠️ Falha ao copiar QA2: {e}")

        # 2) Ensure exercises.d exists in the copied QA2 tex dir and copy template support files
        qa2_tex_dir = copied_qa2 / 'tex'
        qa2_exercises_d = qa2_tex_dir / 'exercises.d'
        qa2_exercises_d.mkdir(parents=True, exist_ok=True)

        # create an input-path file pointing to the copied external_exercises
        # (when using explicit exercise-path inputs we prefer the copied folders)
        input_path_content = (
            "% Auto-generated input-path for exercises (points to copied external_exercises)\n"
            "\\makeatletter\n"
            "\\def\\input@path{{../external_exercises/}}\n"
            "\\makeatother\n"
        )
        (qa2_exercises_d / 'input-path').write_text(input_path_content, encoding='utf-8')

        # copy support files from templates if available
        for support_file in ['setup-counter.tex', 'include-exercise.tex']:
            src = EXERCISES_D_PATH / support_file
            dst = qa2_exercises_d / support_file
            try:
                if src.exists():
                    dst.write_text(src.read_text(encoding='utf-8'), encoding='utf-8')
            except Exception:
                pass

        # 3) Write exercises.tex inside QA2/tex
        try:
            exercises_target = qa2_tex_dir / 'exercises.tex' if qa2_tex_dir.exists() else output_dir / 'exercises.tex'
            lines = []
            lines.append("% Modular exercise inclusion file (generated from exercise-path inputs)")
            lines.append("% Generated by generate_test_from_ips.py")
            lines.append("")
            lines.append("% Load path, counter and the include wrapper")
            # Use the exercises.d files copied into the QA2 copy and reference them
            lines.append(r"\input{exercises.d/input-path}")
            lines.append(r"\input{exercises.d/setup-counter}")
            lines.append(r"\input{exercises.d/include-exercise}")
            lines.append("")
            lines.append("% Exercise inclusions")

            # Copy each exercise directory into the QA2 copy (external_exercises)
            external_root = copied_qa2 / 'external_exercises'
            for exercise_path in ex_paths:
                try:
                    try:
                        rel = exercise_path.relative_to(EXERCISE_DB)
                    except Exception:
                        rel = Path(exercise_path.name)

                    dest = external_root / rel
                    # ensure parent exists and copy the exercise directory
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(exercise_path, dest)

                    # compute path from QA2/tex to the copied exercise
                    # Compute a path to the copied exercise relative to the test root
                    # (output_dir). This produces paths like
                    # 'QA2/external_exercises/discipline/module/.../main' which are
                    # robust when the main test (`test.tex`) includes the QA2 file.
                    try:
                        rel_from_testroot = Path(os.path.relpath(dest, output_dir))
                    except Exception:
                        rel_from_testroot = Path('QA2') / 'external_exercises' / rel

                    if (dest / 'main.tex').exists():
                        include_ref = str((rel_from_testroot / 'main').as_posix())
                    else:
                        include_ref = str(rel_from_testroot.as_posix())

                    # Before including the exercise, set TeX's input path to the
                    # copied exercise directory so any `\input{subvariant_*.tex}`
                    # inside the exercise will be resolved correctly.
                    try:
                        exercise_dir_for_tex = str(rel_from_testroot.as_posix())
                    except Exception:
                        exercise_dir_for_tex = str((Path('QA2') / 'external_exercises' / rel).as_posix())

                    # Also add an include that references the repository ExerciseDatabase
                    # using a relative path from QA2/tex to keep similarity with reference.
                    try:
                        rel = exercise_path.relative_to(EXERCISE_DB)
                        rel_to_exdb = Path(os.path.relpath(EXERCISE_DB, qa2_tex_dir))
                        if (exercise_path / 'main.tex').exists():
                            original_ref = str((rel_to_exdb / rel / 'main').as_posix())
                        else:
                            original_ref = str((rel_to_exdb / rel).as_posix())
                        lines.append(f"\\IncludeExercise{{{original_ref}}}")
                    except Exception:
                        # Fallback to the copied external_exercises reference (keeps compatibility)
                        lines.append(r"\makeatletter")
                        lines.append(f"\\def\\input@path{{{{{exercise_dir_for_tex}/}}}}")
                        lines.append(r"\makeatother")
                        lines.append(f"\IncludeExercise{{{include_ref}}}")
                except Exception as e:
                    logger.warning(f"⚠️ Could not copy or reference exercise {exercise_path}: {e}")

            exercises_target.write_text('\n'.join(lines), encoding='utf-8')
            logger.info(f"✅ Gerado exercises.tex (from exercise-path) em: {exercises_target}")
        except Exception as e:
            logger.error(f"❌ Erro ao gerar exercises.tex a partir de exercise-paths: {e}")

        # Make the test include point to the QA2 exercises file
        include_exercises_ref = "QA2/tex/exercises"

        # 4) Generate a test.tex in the output root that includes the QA2 exercises
        try:
            if TEMPLATE_PATH.exists():
                template_content = TEMPLATE_PATH.read_text(encoding='utf-8')

                # Determine module_name from the first provided exercise path
                module_name = None
                try:
                    if ex_paths:
                        first = ex_paths[0]
                        parts = first.relative_to(EXERCISE_DB).parts
                        if len(parts) >= 2:
                            discipline = parts[0]
                            module_key = parts[1]
                            modules_cfg_path = EXERCISE_DB / 'modules_config.yaml'
                            if modules_cfg_path.exists():
                                try:
                                    import yaml as _yaml
                                    mcfg = _yaml.safe_load(modules_cfg_path.read_text(encoding='utf-8')) or {}
                                    discipline_cfg = mcfg.get(discipline, {})
                                    module_cfg = discipline_cfg.get(module_key, {})
                                    module_name = module_cfg.get('name')
                                except Exception:
                                    module_name = None
                except Exception:
                    module_name = None

                final_title = f"Questão de aula do {module_name}" if module_name else args.title

                # Replace placeholders and inject include path
                tc = template_content
                tc = tc.replace("%%TITLE%%", final_title)
                tc = tc.replace("%%AUTHOR%%", args.author)
                tc = tc.replace("%%DATE%%", datetime.now().strftime("%d/%m/%Y"))
                tc = tc.replace("%%HEADER_LEFT%%", args.title)
                tc = tc.replace("%%HEADER_RIGHT%%", datetime.now().strftime("%d/%m/%Y"))
                tc = tc.replace("%%CONTENT%%", rf"\input{{{include_exercises_ref}}}")
                # copy fallback style to output so template can \input{fallback_style.tex}
                fallback_src = SEBENTAS_DB / '_templates' / 'fallback_style.tex'
                try:
                    if fallback_src.exists():
                        shutil.copy2(fallback_src, output_dir / 'fallback_style.tex')
                except Exception:
                    pass

                test_tex = output_dir / "test.tex"
                test_tex.write_text(tc, encoding='utf-8')
                logger.info(f"✅ Teste gerado: {test_tex}")
            else:
                logger.error(f"❌ Template não encontrado: {TEMPLATE_PATH}")
        except Exception as e:
            logger.error(f"❌ Erro ao gerar test.tex: {e}")

        result = output_dir
    else:
        result = generator.generate_test(
            ips=ip_list,
            title=args.title,
            author=args.author,
            output_dir=output_dir
        )
    
    if result:
        logger.info("=" * 60)
        logger.info(f"✅ SUCESSO: {result}")
        logger.info("=" * 60)
        sys.exit(0)
    else:
        logger.error("=" * 60)
        logger.error("❌ FALHA na geração do teste")
        logger.error("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
