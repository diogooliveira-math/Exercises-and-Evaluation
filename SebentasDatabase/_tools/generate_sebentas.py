"""
Sistema de Geração de Sebentas v3.0
====================================
Gera PDFs de sebentas a partir da ExerciseDatabase com limpeza automática
de ficheiros temporários do LaTeX.

Características:
- Organiza por disciplina/módulo/conceito/tipo
- Usa templates LaTeX centralizados
- Compila automaticamente com pdflatex
- Remove ficheiros temporários (.aux, .log, .fls, etc.)
- Cria estrutura organizada em SebentasDatabase/

NOVO v3.1: Sistema de Preview e Curadoria
- Pré-visualização do conteúdo LaTeX antes de compilar
- Aprovação manual do utilizador
- Abertura automática em VS Code para revisão

Uso:
    python generate_sebentas.py [opções]
    
Opções:
    --discipline    Filtrar por disciplina (ex: matematica)
    --module        Filtrar por módulo (ex: P4_funcoes)
    --concept       Filtrar por conceito específico
    --tipo          Filtrar por tipo de exercício
    --clean-only    Apenas limpar ficheiros temporários existentes
    --no-compile    Gerar .tex mas não compilar
    --no-preview    Não mostrar preview antes de compilar
    --auto-approve  Aprovar automaticamente sem pedir confirmação
"""

import sys
import json
import shutil
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Set

try:
    import yaml
except ImportError:
    yaml = None

# Logging setup
import logging
import os
from logging.handlers import RotatingFileHandler

# Ensure logs directory exists in SebentasDatabase/logs
LOG_DIR = Path(__file__).parent.parent.parent / "SebentasDatabase" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Create timestamped logfile
_log_filename = LOG_DIR / f"generate_sebentas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logger = logging.getLogger("generate_sebentas")
if not logger.handlers:
    logger.setLevel(logging.DEBUG)
    fh = RotatingFileHandler(str(_log_filename), maxBytes=5 * 1024 * 1024, backupCount=5, encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s")
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # console handler for user-facing messages
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

# Importar sistema de preview
try:
    # garantir que apontamos para a pasta correta do ExerciseDatabase/_tools
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "ExerciseDatabase" / "_tools"))
    from preview_system import PreviewManager, create_sebenta_preview
    from preview_system import Colors  # Import Colors for fine-tuning messages
    logger.info(" Sistema de preview disponível: ExerciseDatabase/_tools/preview_system.py importado com sucesso")
except ImportError:
    PreviewManager = None
    create_sebenta_preview = None
    Colors = None
    logger.warning(" Sistema de preview não disponível - a continuar sem pré-visualização")


# Paths principais
PROJECT_ROOT = Path(__file__).parent.parent.parent
EXERCISE_DB = PROJECT_ROOT / "ExerciseDatabase"
SEBENTAS_DB = PROJECT_ROOT / "SebentasDatabase"
TEMPLATE_PATH = SEBENTAS_DB / "_templates" / "sebenta_template.tex"
MODULES_CONFIG = EXERCISE_DB / "modules_config.yaml"

# Extensões de ficheiros temporários do LaTeX
TEMP_EXTENSIONS = {
    '.aux', '.log', '.out', '.toc', '.lof', '.lot',
    '.fls', '.fdb_latexmk', '.synctex.gz', '.synctex(busy)',
    '.nav', '.snm', '.vrb', '.bbl', '.blg', '.idx',
    '.ind', '.ilg', '.bak', '.backup'
}


class SebentaGenerator:
    """Gerador principal de sebentas."""
    
    def __init__(self, clean_only: bool = False, no_compile: bool = False, 
                 no_module_sebenta: bool = False, no_preview: bool = False,
                 auto_approve: bool = False, dump_tex: bool = False):
        """Add `dump_tex` to optionally save generated .tex for debugging."""
        self.clean_only = clean_only
        self.no_compile = no_compile
        self.no_module_sebenta = no_module_sebenta
        self.no_preview = no_preview
        self.auto_approve = auto_approve
        self.stats = {
            'generated': 0,
            'compiled': 0,
            'cleaned': 0,
            'errors': 0,
            'cancelled': 0
        }
        # Carregar configuração dos módulos
        self.modules_config = self.load_modules_config()
        # Guardar flag dump_tex
        self.dump_tex = dump_tex
        # Inicializar preview manager se disponível
        try:
            self.preview_manager = PreviewManager(auto_open=True) if PreviewManager and not no_preview else None
            if self.preview_manager:
                logger.info("🟢 PreviewManager inicializado (auto_open=True, consolidated_preview default)")
            else:
                logger.info("🟡 PreviewManager não inicializado (preview desativado ou módulo ausente)")
        except Exception as e:
            logger.exception(f" Falha ao inicializar PreviewManager: {e}")
            self.preview_manager = None

        
    def load_modules_config(self) -> Dict:
        """Carrega configuração dos módulos."""
        if not MODULES_CONFIG.exists() or yaml is None:
            return {}
        try:
            with open(MODULES_CONFIG, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.exception(f" Erro ao carregar modules_config.yaml: {e}")
            return {}
    
    def get_module_name(self, discipline: str, module: str) -> str:
        """Obtém o nome completo do módulo a partir do config."""
        try:
            module_info = self.modules_config.get(discipline, {}).get(module, {})
            # If explicit name available in config, prefer it
            if module_info.get('name'):
                return module_info.get('name')
        except:
            pass

        # Derive a friendly display name when config entry is missing.
        # Example: 'P4_funcoes' -> 'P4: Funções'
        if '_' in module:
            left, right = module.split('_', 1)
            # replace remaining underscores with spaces
            right_display = right.replace('_', ' ')

            # small mapping of common Portuguese words to proper accents/capitalization
            accent_map = {
                'funcoes': 'Funções',
                'função': 'Função',
                'funcoes_polinomiais': 'Funções Polinomiais',
                'matematica': 'Matemática',
                'revisoes': 'Revisões',
                'generalidades': 'Generalidades'
            }

            words = right_display.split()
            words = [accent_map.get(w.lower(), w.capitalize()) for w in words]
            right_display = ' '.join(words)

            return f"Módulo {left}: {right_display}"

        # Fallback: nicer title-cased form
        return module.replace('_', ' ').title()
        
    def clean_temp_files(self, directory: Path, recursive: bool = True) -> int:
        """Remove ficheiros temporários do LaTeX."""
        cleaned = 0
        
        if not directory.exists():
            return 0
            
        # Ficheiros na diretoria atual
        for file in directory.iterdir():
            if file.is_file():
                if file.suffix in TEMP_EXTENSIONS:
                    try:
                        file.unlink()
                        cleaned += 1
                        print(f"   Removido: {file.name}")
                    except Exception as e:
                        print(f"   Erro ao remover {file.name}: {e}")
            elif file.is_dir() and recursive:
                cleaned += self.clean_temp_files(file, recursive=True)
                
        return cleaned
    
    def load_template(self) -> str:
        """Carrega o template LaTeX."""
        if not TEMPLATE_PATH.exists():
            raise FileNotFoundError(f"Template não encontrado: {TEMPLATE_PATH}")
        
        with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    
    def get_concept_metadata(self, concept_path: Path) -> Dict:
        """Extrai metadados de um conceito."""
        # Tentar carregar metadata.json do conceito
        concept_metadata_file = concept_path / "metadata.json"
        
        metadata = {
            'concept_id': concept_path.name,
            'concept_name': concept_path.name.replace('_', ' ').replace('-', ' - '),
            'concept_description': '',
            'tipos': [],
            'exercises': []
        }
        
        # Se existir metadata.json, usar informações de lá
        if concept_metadata_file.exists():
            try:
                with open(concept_metadata_file, 'r', encoding='utf-8') as f:
                    concept_data = json.load(f)
                    metadata['concept_name'] = concept_data.get('name', metadata['concept_name'])
                    metadata['concept_description'] = concept_data.get('description', '')
                    
                    # Carregar tipos do metadata se existirem
                    if 'tipos' in concept_data:
                        for tipo_info in concept_data['tipos']:
                            tipo_dir = concept_path / tipo_info['id']
                            if tipo_dir.exists():
                                metadata['tipos'].append({
                                    'id': tipo_info['id'],
                                    'name': tipo_info.get('name', tipo_info['id']),
                                    'description': tipo_info.get('description', ''),
                                    'path': tipo_dir
                                })
            except Exception as e:
                logger.exception(f"   Erro ao ler metadata do conceito: {e}")
        
        # Procurar por tipos (subdiretórios) se não estiverem no metadata
        if not metadata['tipos']:
            for tipo_dir in sorted(concept_path.iterdir()):
                if not tipo_dir.is_dir():
                    continue
                    
                tipo_metadata_file = tipo_dir / "metadata.json"
                if tipo_metadata_file.exists():
                    try:
                        with open(tipo_metadata_file, 'r', encoding='utf-8') as f:
                            tipo_data = json.load(f)
                            metadata['tipos'].append({
                                'id': tipo_dir.name,
                                'name': tipo_data.get('tipo_nome', tipo_dir.name),
                                'description': tipo_data.get('descricao', ''),
                                'path': tipo_dir
                            })
                    except Exception as e:
                        logger.exception(f"   Erro ao ler metadata do tipo {tipo_dir.name}: {e}")
        
        # Coletar exercícios .tex ou pastas com main.tex
        exercises = []
        seen_exercises = set()  # Para evitar duplicatas
        
        for item in concept_path.rglob("*"):
            # Ignorar templates e sebentas geradas
            if item.name.startswith(('sebenta_', 'template_')):
                continue
            
            # Se é uma pasta com main.tex, é um exercício com subvariants
            if item.is_dir() and (item / "main.tex").exists():
                main_tex = item / "main.tex"
                if main_tex not in seen_exercises:
                    exercises.append(main_tex)
                    seen_exercises.add(main_tex)
            # Se é um arquivo .tex individual (não subvariant_*.tex)
            elif item.is_file() and item.suffix == '.tex' and not item.name.startswith('subvariant_'):
                if item not in seen_exercises:
                    exercises.append(item)
                    seen_exercises.add(item)
        
        # Ordenação customizada para exercícios de eleições
        def custom_sort_key(tex_file: Path) -> tuple:
            """Chave de ordenação customizada para exercícios de eleições."""
            name = tex_file.name
            parent_dir = tex_file.parent.name
            
            # Ordem preferida por diretório
            dir_order = {
                'compreensao_termos': 0,        # Associação primeiro
                'conceitos_eleitorais': 1,      # Conceitos segundo
                'analise_tabelas_eleitorais': 2 # Análise de tabelas por último
            }
            
            # Ordem preferida por tipo de arquivo dentro de analise_tabelas_eleitorais
            file_order = {
                'MAT_P1MODELO_ELE_PERC_001.tex': 0,  # Percentagens primeiro
                'MAT_P1MODELO_ELE_TAB1_001.tex': 1,
                'MAT_P1MODELO_ELE_TAB2_001.tex': 2,
                'MAT_P1MODELO_ELE_TAB3_001.tex': 3,
                'MAT_P1MODELO_ELE_CONC_001.tex': 0,  # Conceitos primeiro
                'MAT_P1MODELO_ELE_MATCH_001.tex': 0  # Associação único
            }
            
            dir_priority = dir_order.get(parent_dir, 999)
            file_priority = file_order.get(name, 999)
            
            return (dir_priority, file_priority, name)
        
        # Aplicar ordenação customizada apenas para eleições
        concept_name = concept_path.name
        if concept_name == 'eleicoes':
            exercises.sort(key=custom_sort_key)
        else:
            exercises.sort()  # Ordenação alfabética padrão para outros conceitos
        
        metadata['exercises'] = exercises
        
        return metadata
    
    def generate_content(self, concept_path: Path, metadata: Dict, 
                          output_dir: Path) -> str:
        """Gera o conteúdo LaTeX da sebenta.
        
        Em vez de usar \\input, lê diretamente o conteúdo dos ficheiros .tex
        e incorpora no documento gerado.
        """
        content_lines = []
        
        # Seção introdutória com título adequado
        content_lines.append(f"\\section*{{{metadata['concept_name']}}}")
        content_lines.append("")
        
        # Adicionar descrição se existir
        if metadata.get('concept_description'):
            content_lines.append("\\textit{")
            content_lines.append(metadata['concept_description'])
            content_lines.append("}")
            content_lines.append("")
            content_lines.append("\\vspace{1em}")
            content_lines.append("")
        
        # Listar tipos de exercícios se existirem
        if metadata['tipos']:
            content_lines.append("\\subsection*{Tipos de Exercícios}")
            content_lines.append("\\begin{itemize}")
            for tipo in metadata['tipos']:
                tipo_name_display = tipo['name'].replace('_', ' ')
                tipo_text = f"\\textbf{{{tipo_name_display}}}"
                if tipo.get('description'):
                    tipo_text += f" --- {tipo['description']}"
                content_lines.append(f"  \\item {tipo_text}")
            content_lines.append("\\end{itemize}")
            content_lines.append("")
        
        # Incluir exercícios (sem título "Exercícios")
        if not metadata['exercises']:
            content_lines.append("\\textit{Nenhum exercício disponível.}")
        else:
            # Adicionar espaço antes dos exercícios se houver tipos listados
            if metadata['tipos']:
                content_lines.append("\\vspace{1em}")
                content_lines.append("")
            
            for idx, tex_file in enumerate(metadata['exercises'], 1):
                content_lines.append(f"% Exercício {idx}: {tex_file.name}")
                
                # Ler conteúdo do ficheiro e incorporar diretamente
                try:
                    with open(tex_file, 'r', encoding='utf-8') as f:
                        exercise_content = f.read().strip()
                    
                    # Sanitize agent/auto-generated literal "\\n" sequences into real newlines
                    # This fixes cases where content contains literal backslash-n sequences (e.g. "\\n\\item")
                    exercise_content = exercise_content.replace('\\n', '\n')
                    
                    # Additional, context-aware sanitization: attempt to avoid turning text into math
                    def _sanitize_latex(s: str) -> str:
                        import re
                        # Fix common double-escaped LaTeX commands (but avoid changing standalone "\\" used for linebreaks)
                        safe_cmds = ['frac', 'item', 'begin', 'end', 'label', 'textbf', 'emph', 'left', 'right', 'mathrm', 'mathbb', 'sqrt']
                        for cmd in safe_cmds:
                            s = re.sub(r'\\\\+' + cmd, r'\\' + cmd, s)

                        # Collapse runs of backslashes before commands
                        s = re.sub(r'\\\\+(?=\\[A-Za-z])', r'\\', s)

                        # Unicode -> LaTeX name (no $ wrappers here)
                        uni_map = {
                            'ℝ': r'\mathbb{R}',
                            '∞': r'\infty',
                            '⇒': r'\Rightarrow',
                            '→': r'\to',
                            '←': r'\leftarrow',
                            '≠': r'\neq',
                            '∈': r'\in',
                            '⊂': r'\subset',
                            '…': '...',
                            '✓': r'\checkmark'
                        }

                        # Sub/superscript unicode maps
                        sub_map = {'₁': '_{1}', '₂': '_{2}', '₃': '_{3}', '₄': '_{4}'}
                        sup_map = {'¹': '^{1}', '²': '^{2}', '³': '^{3}', '⁻¹': '^{-1}', '⁻': '-'}

                        # Split into math and non-math segments (simple heuristic)
                        math_pattern = re.compile(r'(\$\$.*?\$\$|\$.*?\$|\\\[.*?\\\])', re.DOTALL)
                        parts = math_pattern.split(s)
                        out_parts = []

                        for part in parts:
                            if not part:
                                continue
                            if math_pattern.match(part):
                                # inside math: apply only lightweight fixes
                                p = part
                                # replace unicode with LaTeX commands (without adding $ wrappers)
                                for k, v in uni_map.items():
                                    p = p.replace(k, v)
                                for k, v in sub_map.items():
                                    p = p.replace(k, v)
                                for k, v in sup_map.items():
                                    p = p.replace(k, v)
                                # fix double-escaped commands inside math
                                p = re.sub(r'\\\\+(?=\\[A-Za-z])', r'\\', p)
                                out_parts.append(p)
                            else:
                                # outside math: be conservative, wrap pure-symbol unicode in $...$ so they become math
                                p = part
                                for k, v in uni_map.items():
                                    p = p.replace(k, f'${v}$')
                                for k, v in sub_map.items():
                                    p = p.replace(k, f'$_{v[1:]}$')
                                for k, v in sup_map.items():
                                    p = p.replace(k, f'${v}$')
                                # fix double-escaped commands outside math
                                p = re.sub(r'\\\\+(?=\\[A-Za-z])', r'\\', p)
                                out_parts.append(p)

                        result = ''.join(out_parts)

                        # Warn if dollar signs are unbalanced (simple heuristic)
                        try:
                            total_single_dollars = len(re.findall(r'(?<!\)\$', result))
                        except Exception:
                            total_single_dollars = result.count('$')
                        if total_single_dollars % 2 == 1:
                            logger.warning('Sanitizer detected odd number of $ in exercise content; leaving as-is and flagging for manual review')

                        return result

                    exercise_content = _sanitize_latex(exercise_content)
                    
                    # Se é um main.tex de exercício com subvariants, processar os \input{}
                    if tex_file.name == 'main.tex' and tex_file.parent.is_dir():
                        exercise_content = self._process_subvariant_inputs(exercise_content, tex_file.parent)
                    
                    content_lines.append(exercise_content)
                    # Force floats (figures) to be placed before continuing
                    content_lines.append("\\FloatBarrier")
                except Exception as e:
                    content_lines.append(f"% ERRO ao ler {tex_file.name}: {e}")
                    content_lines.append(f"\\textbf{{Erro ao carregar exercício: {tex_file.name}}}")
                    logger.exception(f"Erro ao ler exercício {tex_file}: {e}")
                
                content_lines.append("")

        
        return "\n".join(content_lines)
    
    def _process_subvariant_inputs(self, content: str, exercise_dir: Path) -> str:
        """Processa \input{} de subvariants e substitui pelo conteúdo dos arquivos.
        
        Args:
            content: Conteúdo do main.tex
            exercise_dir: Diretório do exercício (que contém os subvariant_*.tex)
        
        Returns:
            Conteúdo processado com subvariants incluídos
        """
        import re
        
        def replace_input(match):
            subvariant_name = match.group(1)
            subvariant_file = exercise_dir / f"{subvariant_name}.tex"
            
            if subvariant_file.exists():
                try:
                    with open(subvariant_file, 'r', encoding='utf-8') as f:
                        return f.read().strip()
                except Exception as e:
                    logger.warning(f"Erro ao ler subvariant {subvariant_file}: {e}")
                    return f"% ERRO: Não foi possível carregar {subvariant_name}"
            else:
                logger.warning(f"Subvariant não encontrado: {subvariant_file}")
                return f"% AVISO: Subvariant {subvariant_name} não encontrado"
        
        # Substituir \input{subvariant_N} pelo conteúdo do arquivo
        pattern = r'\\input\{(subvariant_\d+)\}'
        processed_content = re.sub(pattern, replace_input, content)
        
        return processed_content
    
    def generate_sebenta(self, discipline: str, module: str, concept: str, 
                        concept_path: Path, tipo: Optional[List[str]] = None) -> Optional[Path]:
        """Enhanced logging around preview and optional dump of generated .tex for debugging."""
        """Gera uma sebenta para um conceito específico."""
        
        logger.info(f"\n Gerando sebenta: {discipline}/{module}/{concept}")
        
        # Criar estrutura de output
        output_dir = SEBENTAS_DB / discipline / module / concept
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Limpar ficheiros temporários antigos (mas preservar PDFs existentes)
        cleaned = 0
        for file in output_dir.iterdir():
            if file.is_file() and file.suffix in TEMP_EXTENSIONS and file.suffix != '.pdf':
                try:
                    file.unlink()
                    cleaned += 1
                except Exception:
                    pass
        if cleaned > 0:
            logger.info(f"   Limpou {cleaned} ficheiros temporários antigos")
        
        # Obter metadados
        metadata = self.get_concept_metadata(concept_path)

        # Se foi solicitado um filtro por tipo, filtrar a lista de exercícios
        if tipo:
            filtered = []
            for tipo_id in tipo:
                # Filtrar exercícios que vivem dentro da subpasta do tipo
                tipo_filtered = [p for p in metadata['exercises'] if tipo_id in [a.name for a in p.parents if a.parent == concept_path or a == concept_path]]
                if not tipo_filtered:
                    # Tentar também encontrar por diretório direto: concept_path/tipo_id
                    tipo_dir = concept_path / tipo_id
                    if tipo_dir.exists() and tipo_dir.is_dir():
                        tipo_filtered = [p for p in metadata['exercises'] if tipo_dir in list(p.parents)]
                filtered.extend(tipo_filtered)
            
            # Remover duplicatas
            filtered = list(set(filtered))
            
            if not filtered:
                logger.warning(f"   Nenhum exercício encontrado para tipos '{tipo}' em {concept_path}")
                return None

            metadata['exercises'] = filtered
            # Reduzir lista de tipos mostrada no preview para os tipos solicitados
            metadata['tipos'] = [t for t in metadata.get('tipos', []) if t.get('id') in tipo or t.get('name') in tipo]
        
        if not metadata['exercises']:
            logger.warning(f"   Nenhum exercício encontrado em {concept_path}")
            return None
        
        # Carregar template
        template = self.load_template()
        
        # Gerar conteúdo
        content = self.generate_content(concept_path, metadata, output_dir)
        
        # Carregar informações do módulo
        module_name = self.get_module_name(discipline, module)
        
        # Preencher template (sem título, autor e data no documento)
        title = ""  # Não usado mais no documento
        header_left = module_name
        header_right = metadata['concept_name']
        
        latex_content = template.replace("%%TITLE%%", title)
        latex_content = latex_content.replace("%%AUTHOR%%", "")
        latex_content = latex_content.replace("%%DATE%%", "")
        latex_content = latex_content.replace("%%HEADER_LEFT%%", header_left)
        latex_content = latex_content.replace("%%HEADER_RIGHT%%", header_right)
        latex_content = latex_content.replace("%%CONTENT%%", content)

        # Final post-processing sanitizer for the generated .tex to fix common agent/artifact issues
        import re
        def _final_sanitize(s: str) -> str:
            # Collapse multiple backslashes before a LaTeX command into a single backslash
            s = re.sub(r"\\\\+(?=\\[A-Za-z])", r"\\", s)
            # Fix remaining literal double-escaped sequences (safe replacements)
            s = s.replace('\\\\frac', '\\frac')
            s = s.replace('\\\\item', '\\item')
            s = s.replace('\\\\begin', '\\begin')
            s = s.replace('\\\\end', '\\end')

            # Map common Unicode math symbols to LaTeX (no $ wrappers here; rely on context-aware sanitizer earlier)
            uni_map = {
                'ℝ': r'\mathbb{R}',
                '∞': r'\infty',
                '⇒': r'\Rightarrow',
                '→': r'\to',
                '∈': r'\in',
                '≠': r'\neq',
                '…': '...'
            }

            for k, v in uni_map.items():
                s = s.replace(k, v)


            # Remove obvious agent helper comment lines (they often indicate previous failed auto-fixes)
            s = re.sub(r'(?m)^[ \t]*%+.*Agent added.*\n', '\n', s)

            # Remove solitary lines that contain only a single dollar sign (likely left by agents)
            s = re.sub(r'(?m)^[ \t]*\$(?:[ \t]*)\r?\n', '\n', s)

            # Close simple unclosed \subexercicio{... occurrences that are on a single line
            # e.g. "\subexercicio{Verifique que $f(f^{-1}" -> append a closing brace
            s = re.sub(r'(?m)^(.*\\subexercicio\{[^\}]*)(\r?$)', r'\1}\2', s)

            # ROBUST TikZ node fixes: operate only inside tikzpicture blocks and normalize corruption to 'node'
            try:
                def _fix_tikz_block(match):
                    block = match.group(0)
                    # Replace common corrupted sequences producing 'n\n...ode' or stray backslashes
                    block = re.sub(r'(?m)\bn\s*\r?\n\s*ode', r'\\node', block)
                    block = re.sub(r'(?m)\bn\\+\s*node', r'\\node', block)
                    block = re.sub(r'(?m)\\\s*\r?\n\s*node', r'\\node', block)
                    # Normalize leading backslashes before 'node' to a single backslash (inside paths ' -- (x,y) node[...]')
                    block = re.sub(r'(?m)\\+node', r'\\node', block)
                    # Ensure lines that start with 'node' after a newline are correctly formatted with a backslash
                    block = re.sub(r'(?m)\r?\n\s*node', '\\n\\node', block)
                    return block

                s = re.sub(r'(\\begin\{tikzpicture\}.*?\\end\{tikzpicture\})', _fix_tikz_block, s, flags=re.DOTALL)
            except Exception:
                pass

            # Wrap standalone display-like math commands (e.g., a line containing only a \frac{...}) in $...$
            try:
                def _wrap_math_line(match):
                    indent = match.group('indent') or ''
                    expr = match.group('expr')
                    # don't double-wrap if there's already a $ on the line
                    if '$' in expr or '\\(' in expr or '\\[' in expr:
                        return match.group(0)
                    return f"{indent}${expr}$"

                s = re.sub(r'(?m)^(?P<indent>\s*)(?P<expr>\\(?:frac|dfrac|tfrac|sqrt)\b.*)$', _wrap_math_line, s)
            except Exception:
                pass

            # Remove solitary single-letter artifact lines (e.g., a line containing only 'q')
            s = re.sub(r'(?m)^[ \t]*[A-Za-z]{1}[ \t]*\r?\n', '\n', s)

            # Fix incomplete \end{figure without trailing '}' inserted by agent artifacts
            try:
                s = re.sub(r'(\\end\{figure)(?!\})', r'\1}', s)
            except Exception:
                pass

            # Reduce long runs of blank lines
            s = re.sub(r'\n{3,}', '\n\n', s)

            # Final safety: if total number of unescaped $ is odd, try to escape the last one to avoid runaway math
            try:
                # Count $ not preceded by backslash
                dollars = re.findall(r'(?<!\\)\$', s)
                if len(dollars) % 2 == 1:
                    logger.warning('Final sanitizer detected global odd number of $ characters - escaping the last one')
                    # Escape the last unescaped $ by replacing it with \\
                    s = re.sub(r'(?<!\\)\$(?!.*(?<!\\)\$)', r'\\$', s, count=1)
            except Exception:
                pass

            return s


        latex_content = _final_sanitize(latex_content)

        # Conservative post-sanitize: ensure TikZ 'node' tokens have leading backslash
        import re
        try:
            latex_content = re.sub(r'\bode\[', r'\\node[', latex_content)
            latex_content = re.sub(r'(?m)^(\s*)(?=node\[)', r'\1\\node', latex_content)
            latex_content = re.sub(r'(?m)\r?\n(\s*)node', r'\n\\node', latex_content)
        except Exception:
            pass


        
        # PREVIEW E CONFIRMAÇÃO (se habilitado)
        if self.preview_manager and not self.auto_approve:
            try:
                preview_metadata = {
                    "discipline": discipline,
                    "module": module,
                    "module_name": module_name,
                    "concept": concept,
                    "concept_name": metadata['concept_name'],
                    "total_exercises": len(metadata['exercises']),
                    "tipos": [t['name'] for t in metadata['tipos']]
                }
                
                preview_content = create_sebenta_preview(
                    f"sebenta_{concept}",
                    latex_content,
                    preview_metadata
                )
                
                logger.info(f" Mostrando preview (sebenta_{concept}) - total_exercises={len(metadata['exercises'])}")
                confirmed = self.preview_manager.show_and_confirm(
                    preview_content, 
                    f"Sebenta: {metadata['concept_name']}"
                )

                if not confirmed:
                    logger.info(f"   Cancelado pelo utilizador durante preview")
                    self.stats['cancelled'] += 1
                    return None
            except Exception as e:
                logger.exception(f" Exceção durante preview - prosseguindo sem preview: {e}")
                # Continuar sem preview
        else:
            if not self.preview_manager:
                logger.info("ℹ Preview não configurado - pulando etapa de preview")

        
        # Salvar .tex (só após confirmação)
        tex_file = output_dir / f"sebenta_{concept}.tex"
        with open(tex_file, 'w', encoding='utf-8') as f:
            f.write(latex_content)
        
        logger.info(f"   .tex gerado: {tex_file.relative_to(PROJECT_ROOT)}")
        # Se dump_tex estiver ativo, guardar cópia em SebentasDatabase/debug/
        try:
            if getattr(self, 'dump_tex', False):
                debug_dir = SEBENTAS_DB / "debug"
                debug_dir.mkdir(parents=True, exist_ok=True)
                debug_file = debug_dir / f"{tex_file.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tex"
                with open(debug_file, 'w', encoding='utf-8') as df:
                    df.write(latex_content)
                logger.info(f"   Dump do .tex guardado para debug: {debug_file.relative_to(PROJECT_ROOT)}")
        except Exception as e:
            logger.exception(f" Falha ao gravar dump .tex: {e}")
        
        # FINE-TUNING: Abrir ficheiro para edição antes de compilar
        if not self.no_compile and not self.auto_approve:
            if Colors:
                print(f"\n{Colors.BOLD}{Colors.CYAN} FINE-TUNING: O ficheiro .tex foi gerado e está pronto para edição{Colors.END}")
                print(f"{Colors.BLUE} Ficheiro: {tex_file}{Colors.END}")
            else:
                print(f"\n FINE-TUNING: O ficheiro .tex foi gerado e está pronto para edição")
                print(f" Ficheiro: {tex_file}")
            
            # Tentar abrir em VS Code
            try:
                import subprocess
                import os
                vscode_cmds = ["code", "code.cmd", r"C:\Program Files\Microsoft VS Code\Code.exe"]
                opened = False
                for cmd in vscode_cmds:
                    try:
                        result = subprocess.run([cmd, str(tex_file)], 
                                              check=False, 
                                              capture_output=True,
                                              timeout=5)
                        if result.returncode == 0:
                            opened = True
                            if Colors:
                                print(f"{Colors.GREEN} Aberto em VS Code para edição{Colors.END}")
                            else:
                                print(" Aberto em VS Code para edição")
                            break
                    except:
                        continue
                
                if not opened:
                    if Colors:
                        print(f"{Colors.YELLOW} Não foi possível abrir automaticamente. Edite manualmente:{Colors.END}")
                        print(f"{Colors.BLUE}   {tex_file}{Colors.END}")
                    else:
                        print(" Não foi possível abrir automaticamente. Edite manualmente:")
                        print(f"   {tex_file}")
            
            except Exception as e:
                if Colors:
                    print(f"{Colors.YELLOW} Erro ao abrir ficheiro: {e}{Colors.END}")
                else:
                    print(f" Erro ao abrir ficheiro: {e}")
            
            # Perguntar se quer prosseguir com compilação
            while True:
                if Colors:
                    response = input(f"\n{Colors.GREEN}▶  Fez edições no ficheiro? Pronto para compilar? [S]im / [N]ão / [A]bortar: {Colors.END}").strip().lower()
                else:
                    response = input(f"\n▶  Fez edições no ficheiro? Pronto para compilar? [S]im / [N]ão / [A]bortar: ").strip().lower()
                
                if response in ['s', 'sim', 'y', 'yes']:
                    if Colors:
                        print(f"{Colors.GREEN} Prosseguindo com compilação...{Colors.END}")
                    else:
                        print(" Prosseguindo com compilação...")
                    break
                elif response in ['n', 'não', 'no']:
                    if Colors:
                        print(f"{Colors.BLUE}⏸  Faça as edições necessárias e pressione Enter quando estiver pronto...{Colors.END}")
                    else:
                        print("⏸  Faça as edições necessárias e pressione Enter quando estiver pronto...")
                    input()
                    continue
                elif response in ['a', 'abort', 'abortar']:
                    if Colors:
                        print(f"{Colors.RED} Compilação abortada pelo utilizador{Colors.END}")
                    else:
                        print(" Compilação abortada pelo utilizador")
                    # Remover ficheiro .tex se abortado
                    if tex_file.exists():
                        tex_file.unlink()
                    return None
                else:
                    if Colors:
                        print(f"{Colors.RED}Opção inválida! Digite S, N ou A{Colors.END}")
                    else:
                        print("Opção inválida! Digite S, N ou A")
        
        self.stats['generated'] += 1
        
        return tex_file
    
    def generate_module_sebenta(self, discipline: str, module: str, 
                               concepts: List[Dict]) -> Optional[Path]:
        """Gera uma sebenta consolidada de todo o módulo."""
        
        logger.info(f"\n Gerando sebenta consolidada do módulo: {discipline}/{module}")
        
        # Criar estrutura de output
        output_dir = SEBENTAS_DB / discipline / module
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Criar diretório de PDFs se não existir
        pdfs_dir = output_dir / "pdfs"
        pdfs_dir.mkdir(exist_ok=True)
        
        # Carregar template
        template = self.load_template()
        
        # Obter nome completo do módulo
        module_name = self.get_module_name(discipline, module)
        module_description = ""
        try:
            module_info = self.modules_config.get(discipline, {}).get(module, {})
            module_description = module_info.get('description', '')
        except:
            pass
        
        # Gerar conteúdo consolidado
        content_lines = []
        content_lines.append(f"\\section*{{{module_name}}}")
        content_lines.append("")
        
        if module_description:
            content_lines.append(f"\\textit{{{module_description}}}")
            content_lines.append("")
            content_lines.append("\\vspace{1em}")
            content_lines.append("")
        
        content_lines.append(f"Este documento contém todos os exercícios do módulo, organizados por conceito.")
        content_lines.append("")
        content_lines.append("\\tableofcontents")
        content_lines.append("\\newpage")
        content_lines.append("")
        
        for concept_info in concepts:
            concept_name = concept_info['name'].replace('_', ' ').replace('-', ' - ')
            content_lines.append(f"\\section{{{concept_name}}}")
            content_lines.append("")
            
            # Ler conteúdo do PDF gerado (ou usar o .tex)
            concept_tex = concept_info['tex']
            concept_path = concept_info['path']
            
            # Buscar exercícios do conceito
            metadata = self.get_concept_metadata(concept_path)
            
            if metadata['exercises']:
                for idx, tex_file in enumerate(metadata['exercises'], 1):
                    try:
                        with open(tex_file, 'r', encoding='utf-8') as f:
                            exercise_content = f.read()
                        content_lines.append(exercise_content)
                        # Force floats after each exercise when building module sebenta
                        content_lines.append("\\FloatBarrier")
                        content_lines.append("")
                    except Exception as e:
                        content_lines.append(f"% ERRO ao ler {tex_file.name}: {e}")
            else:
                content_lines.append("\\textit{Nenhum exercício disponível.}")
            
            content_lines.append("")
            content_lines.append("\\newpage")
            content_lines.append("")
        
        content = "\n".join(content_lines)
        
        # Preencher template (sem título, autor e data)
        module_name = self.get_module_name(discipline, module)
        # Usar o nome amigável do módulo no cabeçalho esquerdo
        header_left = module_name
        header_right = ""
        
        latex_content = template.replace("%%TITLE%%", "")
        latex_content = latex_content.replace("%%AUTHOR%%", "")
        latex_content = latex_content.replace("%%DATE%%", "")
        latex_content = latex_content.replace("%%HEADER_LEFT%%", header_left)
        latex_content = latex_content.replace("%%HEADER_RIGHT%%", header_right)
        latex_content = latex_content.replace("%%CONTENT%%", content)
        
        # PREVIEW E CONFIRMAÇÃO para sebenta de módulo (se habilitado)
        if self.preview_manager and not self.auto_approve:
            preview_metadata = {
                "discipline": discipline,
                "module": module,
                "module_name": module_name,
                "type": "module_compilation",
                "total_concepts": len(concepts),
                "concepts": [c['name'] for c in concepts]
            }
            
            preview_content = create_sebenta_preview(
                f"sebenta_modulo_{module}",
                latex_content,
                preview_metadata
            )
            
            if not self.preview_manager.show_and_confirm(
                preview_content,
                f"Sebenta Módulo: {module_name}"
            ):
                logger.info(f"   Cancelado pelo utilizador")
                self.stats['cancelled'] += 1
                return None
        
        # Salvar .tex (só após confirmação)
        tex_file = output_dir / f"sebenta_modulo_{module}.tex"
        with open(tex_file, 'w', encoding='utf-8') as f:
            f.write(latex_content)
        
        logger.info(f"   .tex gerado: {tex_file.relative_to(PROJECT_ROOT)}")
        # Se dump_tex estiver ativo, guardar cópia em SebentasDatabase/debug/
        try:
            if getattr(self, 'dump_tex', False):
                debug_dir = SEBENTAS_DB / "debug"
                debug_dir.mkdir(parents=True, exist_ok=True)
                debug_file = debug_dir / f"{tex_file.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tex"
                with open(debug_file, 'w', encoding='utf-8') as df:
                    df.write(latex_content)
                logger.info(f"   Dump do .tex guardado para debug: {debug_file.relative_to(PROJECT_ROOT)}")
        except Exception as e:
            logger.exception(f" Falha ao gravar dump .tex: {e}")
        
        # FINE-TUNING: Abrir ficheiro para edição antes de compilar
        if not self.no_compile and not self.auto_approve:
            if Colors:
                print(f"\n{Colors.BOLD}{Colors.CYAN} FINE-TUNING: O ficheiro .tex foi gerado e está pronto para edição{Colors.END}")
                print(f"{Colors.BLUE} Ficheiro: {tex_file}{Colors.END}")
            else:
                print(f"\n FINE-TUNING: O ficheiro .tex foi gerado e está pronto para edição")
                print(f" Ficheiro: {tex_file}")
            
            # Tentar abrir em VS Code
            try:
                import subprocess
                import os
                vscode_cmds = ["code", "code.cmd", r"C:\Program Files\Microsoft VS Code\Code.exe"]
                opened = False
                for cmd in vscode_cmds:
                    try:
                        result = subprocess.run([cmd, str(tex_file)], 
                                              check=False, 
                                              capture_output=True,
                                              timeout=5)
                        if result.returncode == 0:
                            opened = True
                            if Colors:
                                print(f"{Colors.GREEN} Aberto em VS Code para edição{Colors.END}")
                            else:
                                print(" Aberto em VS Code para edição")
                            break
                    except:
                        continue
                
                if not opened:
                    if Colors:
                        print(f"{Colors.YELLOW} Não foi possível abrir automaticamente. Edite manualmente:{Colors.END}")
                        print(f"{Colors.BLUE}   {tex_file}{Colors.END}")
                    else:
                        print(" Não foi possível abrir automaticamente. Edite manualmente:")
                        print(f"   {tex_file}")
            
            except Exception as e:
                if Colors:
                    print(f"{Colors.YELLOW} Erro ao abrir ficheiro: {e}{Colors.END}")
                else:
                    print(f" Erro ao abrir ficheiro: {e}")
            
            # Perguntar se quer prosseguir com compilação
            while True:
                if Colors:
                    response = input(f"\n{Colors.GREEN}▶  Fez edições no ficheiro? Pronto para compilar? [S]im / [N]ão / [A]bortar: {Colors.END}").strip().lower()
                else:
                    response = input(f"\n▶  Fez edições no ficheiro? Pronto para compilar? [S]im / [N]ão / [A]bortar: ").strip().lower()
                
                if response in ['s', 'sim', 'y', 'yes']:
                    if Colors:
                        print(f"{Colors.GREEN} Prosseguindo com compilação...{Colors.END}")
                    else:
                        print(" Prosseguindo com compilação...")
                    break
                elif response in ['n', 'não', 'no']:
                    if Colors:
                        print(f"{Colors.BLUE}⏸  Faça as edições necessárias e pressione Enter quando estiver pronto...{Colors.END}")
                    else:
                        print("⏸  Faça as edições necessárias e pressione Enter quando estiver pronto...")
                    input()
                    continue
                elif response in ['a', 'abort', 'abortar']:
                    if Colors:
                        print(f"{Colors.RED} Compilação abortada pelo utilizador{Colors.END}")
                    else:
                        print(" Compilação abortada pelo utilizador")
                    # Remover ficheiro .tex se abortado
                    if tex_file.exists():
                        tex_file.unlink()
                    return None
                else:
                    if Colors:
                        print(f"{Colors.RED}Opção inválida! Digite S, N ou A{Colors.END}")
                    else:
                        print("Opção inválida! Digite S, N ou A")
        
        self.stats['generated'] += 1
        
        # Compilar (PDFs vão para pdfs_dir)
        self.compile_pdf(tex_file)
        
        return tex_file
    
    def compile_pdf(self, tex_file: Path) -> bool:
        """Compila um ficheiro .tex para PDF."""
        
        if self.no_compile:
            logger.info("   no_compile set - pulando compilação")
            return True
        
        # Verificar se pdflatex está disponível
        pdflatex = shutil.which('pdflatex')
        if not pdflatex:
            logger.warning(f"   pdflatex não encontrado no PATH - compilação ignorada")
            return False
        
        logger.info(f"   Compilando PDF...")
        
        output_dir = tex_file.parent
        tex_name = tex_file.name
        
        # Comando pdflatex
        cmd = [
            pdflatex,
            '-interaction=nonstopmode',
            '-file-line-error',
            tex_name
        ]
        
        try:
            # Executar 2 vezes para resolver referências
            result = None
            for i in range(2):
                result = subprocess.run(
                    cmd,
                    cwd=str(output_dir),  # Converter para string
                    capture_output=True,
                    text=True,
                    timeout=60,
                    encoding='utf-8',
                    errors='replace'
                )
            
            # Pequeno delay para garantir que sistema de ficheiros sincronizou
            import time
            time.sleep(1.0)
            
            # Verificar se PDF foi gerado (independente do exit code)
            pdf_file = output_dir / f"{tex_file.stem}.pdf"
            
            if pdf_file.exists():
                # Criar diretório pdfs se não existir
                pdfs_dir = output_dir / "pdfs"
                pdfs_dir.mkdir(exist_ok=True)
                
                # Mover PDF para diretório pdfs
                pdf_dest = pdfs_dir / pdf_file.name
                if pdf_dest.exists():
                    pdf_dest.unlink()
                pdf_file.rename(pdf_dest)
                
                logger.info(f"   PDF gerado: {pdf_dest.relative_to(PROJECT_ROOT)}")
                self.stats['compiled'] += 1
                
                # Limpar TODOS os ficheiros temporários incluindo .tex
                cleaned = 0
                for file in output_dir.iterdir():
                    if file.is_file() and file != tex_file:
                        if file.suffix in TEMP_EXTENSIONS or file.name.startswith('sebenta_'):
                            try:
                                file.unlink()
                                cleaned += 1
                            except Exception:
                                pass
                
                # Remover também o .tex fonte
                if tex_file.exists():
                    try:
                        tex_file.unlink()
                        cleaned += 1
                    except Exception:
                        pass
                
                if cleaned > 0:
                    logger.info(f"   Limpou {cleaned} ficheiros")
                self.stats['cleaned'] += cleaned
                
                return True
            else:
                logger.error(f"   Erro na compilação - PDF não gerado for {tex_file}")
                # Salvar log de erro se houver output
                if result and (result.stdout or result.stderr):
                    error_log_file = output_dir / f"{tex_file.stem}_error.log"
                    with open(error_log_file, 'w', encoding='utf-8') as f:
                        f.write(result.stdout or "")
                        f.write("\n=== STDERR ===\n")
                        f.write(result.stderr or "")
                    logger.info(f"   Log salvo em: {error_log_file.relative_to(PROJECT_ROOT)}")
                self.stats['errors'] += 1
                return False
                
        except subprocess.TimeoutExpired:
            logger.exception(f"  ⏱ Timeout na compilação for {tex_file}")
            self.stats['errors'] += 1
            return False
        except Exception as e:
            logger.exception(f"   Erro na compilação: {e}")
            self.stats['errors'] += 1
            return False
    
    def scan_and_generate(self, discipline: Optional[List[str]] = None,
                         module: Optional[List[str]] = None,
                         concept: Optional[List[str]] = None,
                         tipo: Optional[List[str]] = None,
                         exercise_paths: Optional[List[str]] = None):
        """Escaneia ExerciseDatabase e gera sebentas.
        If `exercise_paths` is provided, generate only for those exercises (list of relative paths).
        """

        
        if self.clean_only:
            logger.info(" Modo limpeza apenas - removendo ficheiros temporários...")
            cleaned = self.clean_temp_files(SEBENTAS_DB, recursive=True)
            logger.info(f"\n Total limpo: {cleaned} ficheiros")
            return
        
        logger.info(" Escaneando ExerciseDatabase...")
        
        if exercise_paths:
            logger.info(" Gerando a partir de caminhos de exercício fornecidos...")
            for p in exercise_paths:
                # normalize relative paths
                pth = Path(p)
                if not pth.is_absolute():
                    pth = PROJECT_ROOT / pth
                if not pth.exists() or not pth.is_dir():
                    logger.warning(f" Caminho de exercício não encontrado ou inválido: {pth}")
                    continue
                # Expect path like ExerciseDatabase/discipline/module/concept/type/exercise
                try:
                    rel = pth.relative_to(EXERCISE_DB)
                    parts = rel.parts
                    if len(parts) < 5:
                        logger.warning(f" Caminho não segue a estrutura esperada (esperado 5 níveis): {pth}")
                        continue
                    # take last 5 parts in case extra prefixes
                    disc_name, mod_name, conc_name, typ_name, ex_name = parts[-5:]
                    concept_path = pth.parent.parent  # pth -> .../concept/type/exercise
                    tex_file = self.generate_sebenta(
                        disc_name,
                        mod_name,
                        conc_name,
                        concept_path,
                        tipo=[typ_name]
                    )

                    if tex_file:
                        success = self.compile_pdf(tex_file)
                        if success:
                            self.stats['generated'] += 1
                            self.stats['compiled'] += 1
                except Exception as e:
                    logger.exception(f" Erro ao gerar a partir do caminho {p}: {e}")
            return

        # Iterar por disciplinas
        for disc_dir in sorted(EXERCISE_DB.iterdir()):
            if not disc_dir.is_dir() or disc_dir.name.startswith('_'):
                continue
            
            if discipline and disc_dir.name not in discipline:
                continue
            
            # Iterar por módulos
            for mod_dir in sorted(disc_dir.iterdir()):
                if not mod_dir.is_dir():
                    continue
                
                if module and mod_dir.name not in module:
                    continue
                
                logger.info(f"\n Módulo: {disc_dir.name}/{mod_dir.name}")
                module_concepts = []
                
                # Iterar por conceitos
                for conc_dir in sorted(mod_dir.iterdir()):
                    if not conc_dir.is_dir():
                        continue
                    
                    if concept and conc_dir.name not in concept:
                        continue
                    
                    # Gerar sebenta
                    tex_file = self.generate_sebenta(
                        disc_dir.name,
                        mod_dir.name,
                        conc_dir.name,
                        conc_dir,
                        tipo=tipo
                    )

                    
                    # Compilar se gerado
                    if tex_file:
                        success = self.compile_pdf(tex_file)
                        if success:
                            module_concepts.append({
                                'name': conc_dir.name,
                                'path': conc_dir,
                                'tex': tex_file,
                                'pdf': tex_file.with_suffix('.pdf')
                            })
                
                # Gerar sebenta consolidada do módulo se houver conceitos
                if module_concepts and not concept and not self.no_module_sebenta:
                    self.generate_module_sebenta(disc_dir.name, mod_dir.name, module_concepts)
        
        # Estatísticas finais
        logger.info("\n" + "="*60)
        logger.info(" RESUMO")
        logger.info("="*60)
        logger.info(f"Sebentas geradas: {self.stats['generated']}")
        logger.info(f"PDFs compilados:  {self.stats['compiled']}")
        logger.info(f"Ficheiros limpos: {self.stats['cleaned']}")
        if self.stats['cancelled'] > 0:
            logger.info(f"Canceladas:       {self.stats['cancelled']}")
        if self.stats['errors'] > 0:
            logger.info(f"Erros:            {self.stats['errors']}")
        logger.info("="*60)


def staged_to_paths(staged_list: list) -> list:
    """Converte uma lista de staged IDs ou paths em caminhos de exercícios temporários.
    For each staged entry, we create a temporary ExerciseDatabase-like directory under
    ExerciseDatabase/temp/staged_for_sebenta/<staged_id>/ with a single exercise folder
    containing a main.tex copied from the staged .tex preview if available.
    Returns a list of exercise directory paths (strings) suitable for --exercise-path handling.
    """
    from shutil import copyfile
    tmp_root = EXERCISE_DB / 'temp' / 'staged_for_sebenta'
    tmp_root.mkdir(parents=True, exist_ok=True)
    resolved = []

    for item in staged_list:
        p = Path(item)
        # if it's a staged ID like STG_..., turn into ExerciseDatabase/_staging/STG_...
        if not p.is_absolute() and not p.exists() and item.startswith('STG_'):
            p = EXERCISE_DB / '_staging' / item
        if p.exists() and p.is_dir():
            staged_id = p.name
            dest_dir = tmp_root / staged_id
            # create a structure discipline/module/concept/tipo/exercise_stub
            # We'll try to infer discipline/module/concept/tipo from payload.json if present
            payload_file = p / 'payload.json'
            disc = 'unknown'
            mod = 'unknown'
            conc = 'unknown'
            tipo = 'unknown'
            if payload_file.exists():
                try:
                    with open(payload_file, 'r', encoding='utf-8') as f:
                        pl = json.load(f)
                        disc = pl.get('discipline', disc)
                        mod = pl.get('module', mod)
                        conc = pl.get('concept', conc)
                        tipo = pl.get('tipo', tipo)
                except Exception:
                    pass
            # Compose destination exercise path
            exercise_dir = dest_dir / disc / mod / conc / tipo / staged_id
            exercise_dir.mkdir(parents=True, exist_ok=True)

            # Copy tex preview if exists
            tex_preview = None
            for ext in ['.tex']:
                candidate = p / f"{staged_id}{ext}"
                if candidate.exists():
                    tex_preview = candidate
                    break
            if tex_preview is None:
                # fallback to payload statement as main.tex
                payload_statement = None
                try:
                    with open(payload_file, 'r', encoding='utf-8') as f:
                        payload_statement = json.load(f).get('statement', '')
                except Exception:
                    payload_statement = ''
                main_tex = exercise_dir / 'main.tex'
                with open(main_tex, 'w', encoding='utf-8') as f:
                    f.write(payload_statement or f'% staged {staged_id} - no statement')
            else:
                # copy preview into main.tex
                main_tex = exercise_dir / 'main.tex'
                try:
                    copyfile(str(tex_preview), str(main_tex))
                except Exception:
                    # attempt to read and write to avoid cross-device issues
                    try:
                        with open(tex_preview, 'r', encoding='utf-8') as src:
                            with open(main_tex, 'w', encoding='utf-8') as dst:
                                dst.write(src.read())
                    except Exception:
                        with open(main_tex, 'w', encoding='utf-8') as dst:
                            dst.write(f'% failed to copy preview for {staged_id}')

            resolved.append(str(exercise_dir))
        else:
            logger.warning(f"Staged entry not found or invalid: {item} -> {p}")
    return resolved


def main():
    """Função principal."""

    parser = argparse.ArgumentParser(
        description="Gerador de Sebentas v3.0 - Sistema Automático"
    )
    
    parser.add_argument(
        '--discipline',
        action='append',
        help='Filtrar por disciplina (ex: matematica). Pode ser usado múltiplas vezes para múltiplas disciplinas.'
    )
    parser.add_argument(
        '--module',
        action='append',
        help='Filtrar por módulo (ex: P4_funcoes). Pode ser usado múltiplas vezes para múltiplos módulos.'
    )
    parser.add_argument(
        '--concept',
        action='append',
        help='Filtrar por conceito específico. Pode ser usado múltiplas vezes para múltiplos conceitos.'
    )
    parser.add_argument(
        '--tipo',
        action='append',
        help='Filtrar por tipo de exercício. Pode ser usado múltiplas vezes para múltiplos tipos.'
    )
    parser.add_argument(
        '--clean-only',
        action='store_true',
        help='Apenas limpar ficheiros temporários'
    )
    parser.add_argument(
        '--no-compile',
        action='store_true',
        help='Gerar .tex mas não compilar PDF'
    )
    parser.add_argument(
        '--no-module-sebenta',
        action='store_true',
        help='Não gerar sebenta consolidada do módulo'
    )
    parser.add_argument(
        '--no-preview',
        action='store_true',
        help='Não mostrar preview antes de compilar'
    )
    parser.add_argument(
        '--auto-approve',
        action='store_true',
        help='Aprovar automaticamente sem pedir confirmação'
    )
    parser.add_argument(
        '--dump-tex',
        action='store_true',
        help='Guardar o .tex gerado em debug/ para análise (não remove)'
    )
    parser.add_argument(
        '--exercise-path',
        action='append',
        help='Fornecer caminho relativo para um exercício específico (pode repetir)'
    )
    parser.add_argument(
        '--ips',
        action='append',
        help='Fornecer IP(s) de exercícios (formato D.M.C.T.E) para gerar sebentas por IP'
    )
    parser.add_argument(
        '--staged',
        action='append',
        help='Fornecer staged IDs ou caminhos de staging (ExerciseDatabase/_staging/STG_...)'
    )
    
    args = parser.parse_args()


    # Allow controlling flags via environment variables when called from VS Code tasks
    # Environment variables: SEBENTA_NO_PREVIEW, SEBENTA_NO_COMPILE, SEBENTA_AUTO_APPROVE
    import os
    def env_flag(name: str) -> Optional[bool]:
        v = os.environ.get(name, None)
        if v is None or v == "":
            return None
        return str(v).lower() in ("1", "true", "yes", "s", "sim")

    env_no_preview = env_flag('SEBENTA_NO_PREVIEW')
    env_no_compile = env_flag('SEBENTA_NO_COMPILE')
    env_auto_approve = env_flag('SEBENTA_AUTO_APPROVE')

    if env_no_preview is True:
        args.no_preview = True
    if env_no_compile is True:
        args.no_compile = True
    if env_auto_approve is True:
        args.auto_approve = True
    
    # Verificar estrutura
    if not EXERCISE_DB.exists():
        print(f" ExerciseDatabase não encontrada: {EXERCISE_DB}")
        sys.exit(1)
    
    # Criar SebentasDatabase se não existir
    SEBENTAS_DB.mkdir(exist_ok=True)
    
    # Resolve IPs to exercise paths if needed
    exercise_paths = None
    if args.ips:
        try:
            from ExerciseDatabase._tools.ip_resolver import IPResolver
            resolver = IPResolver()
            ips = []
            for block in args.ips:
                ips.extend([s.strip() for s in block.split(',') if s.strip()])
            exercise_paths = resolver.resolve_to_paths(ips)
            if not exercise_paths:
                print('Nenhum exercício resolvido a partir dos IPs fornecidos')
                sys.exit(2)
        except Exception as e:
            logger.exception(f"Erro ao resolver IPs: {e}")
            sys.exit(3)
    if args.exercise_path:
        # Use provided exercise paths directly (may be relative)
        exercise_paths = args.exercise_path

    # New: allow generating from staged entries
    if args.staged:
        try:
            # Convert staged IDs / paths into temporary exercise paths
            staged = []
            for block in args.staged:
                staged.extend([s.strip() for s in block.split(',') if s.strip()])
            exercise_paths = staged_to_paths(staged)
            if not exercise_paths:
                print('Nenhum staging resolvido a partir dos staged IDs fornecidos')
                sys.exit(4)
        except Exception as e:
            logger.exception(f"Erro ao resolver staged entries: {e}")
            sys.exit(5)

    # Executar geração
    generator = SebentaGenerator(
        clean_only=args.clean_only,
        no_compile=args.no_compile,
        no_module_sebenta=args.no_module_sebenta,
        no_preview=args.no_preview,
        auto_approve=args.auto_approve,
        dump_tex=args.dump_tex
    )
    
    generator.scan_and_generate(
        discipline=args.discipline,
        module=args.module,
        concept=args.concept,
        tipo=args.tipo,
        exercise_paths=exercise_paths
    )



if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        # Log unexpected exception with stacktrace to logfile
        logger.exception(f"Unhandled exception in generate_sebentas: {e}")
        # Re-raise to ensure process exits with non-zero code
        raise
