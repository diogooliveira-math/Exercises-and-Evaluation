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

Uso:
    python generate_sebentas.py [opções]
    
Opções:
    --discipline    Filtrar por disciplina (ex: matematica)
    --module        Filtrar por módulo (ex: P4_funcoes)
    --concept       Filtrar por conceito específico
    --tipo          Filtrar por tipo de exercício
    --clean-only    Apenas limpar ficheiros temporários existentes
    --no-compile    Gerar .tex mas não compilar
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
                 no_module_sebenta: bool = False):
        self.clean_only = clean_only
        self.no_compile = no_compile
        self.no_module_sebenta = no_module_sebenta
        self.stats = {
            'generated': 0,
            'compiled': 0,
            'cleaned': 0,
            'errors': 0
        }
        # Carregar configuração dos módulos
        self.modules_config = self.load_modules_config()
        
    def load_modules_config(self) -> Dict:
        """Carrega configuração dos módulos."""
        if not MODULES_CONFIG.exists() or yaml is None:
            return {}
        try:
            with open(MODULES_CONFIG, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"⚠️ Erro ao carregar modules_config.yaml: {e}")
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
                        print(f"  🧹 Removido: {file.name}")
                    except Exception as e:
                        print(f"  ⚠️ Erro ao remover {file.name}: {e}")
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
                print(f"  ⚠️ Erro ao ler metadata do conceito: {e}")
        
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
                        print(f"  ⚠️ Erro ao ler metadata do tipo {tipo_dir.name}: {e}")
        
        # Coletar exercícios .tex
        for tex_file in sorted(concept_path.rglob("*.tex")):
            # Ignorar templates e sebentas geradas
            if tex_file.name.startswith(('sebenta_', 'template_')):
                continue
            metadata['exercises'].append(tex_file)
        
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
                tipo_text = f"\\textbf{{{tipo['name']}}}"
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
                    content_lines.append(exercise_content)
                    # Force floats (figures) to be placed before continuing
                    content_lines.append("\\FloatBarrier")
                except Exception as e:
                    content_lines.append(f"% ERRO ao ler {tex_file.name}: {e}")
                    content_lines.append(f"\\textbf{{Erro ao carregar exercício: {tex_file.name}}}")
                
                content_lines.append("")
        
        return "\n".join(content_lines)
    
    def generate_sebenta(self, discipline: str, module: str, concept: str, 
                        concept_path: Path) -> Optional[Path]:
        """Gera uma sebenta para um conceito específico."""
        
        print(f"\n📚 Gerando sebenta: {discipline}/{module}/{concept}")
        
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
            print(f"  🧹 Limpou {cleaned} ficheiros temporários antigos")
        
        # Obter metadados
        metadata = self.get_concept_metadata(concept_path)
        
        if not metadata['exercises']:
            print(f"  ⚠️ Nenhum exercício encontrado")
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
        
        # Salvar .tex
        tex_file = output_dir / f"sebenta_{concept}.tex"
        with open(tex_file, 'w', encoding='utf-8') as f:
            f.write(latex_content)
        
        print(f"  ✅ Gerado: {tex_file.relative_to(PROJECT_ROOT)}")
        self.stats['generated'] += 1
        
        return tex_file
    
    def generate_module_sebenta(self, discipline: str, module: str, 
                               concepts: List[Dict]) -> Optional[Path]:
        """Gera uma sebenta consolidada de todo o módulo."""
        
        print(f"\n📚 Gerando sebenta consolidada do módulo: {discipline}/{module}")
        
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
            concept_path = concept_tex.parent
            
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
        header_right = module_name
        
        latex_content = template.replace("%%TITLE%%", "")
        latex_content = latex_content.replace("%%AUTHOR%%", "")
        latex_content = latex_content.replace("%%DATE%%", "")
        latex_content = latex_content.replace("%%HEADER_LEFT%%", header_left)
        latex_content = latex_content.replace("%%HEADER_RIGHT%%", header_right)
        latex_content = latex_content.replace("%%CONTENT%%", content)
        
        # Salvar .tex
        tex_file = output_dir / f"sebenta_modulo_{module}.tex"
        with open(tex_file, 'w', encoding='utf-8') as f:
            f.write(latex_content)
        
        print(f"  ✅ Gerado: {tex_file.relative_to(PROJECT_ROOT)}")
        self.stats['generated'] += 1
        
        # Compilar (PDFs vão para pdfs_dir)
        self.compile_pdf(tex_file)
        
        return tex_file
    
    def compile_pdf(self, tex_file: Path) -> bool:
        """Compila um ficheiro .tex para PDF."""
        
        if self.no_compile:
            return True
        
        # Verificar se pdflatex está disponível
        pdflatex = shutil.which('pdflatex')
        if not pdflatex:
            print(f"  ⚠️ pdflatex não encontrado no PATH - compilação ignorada")
            return False
        
        print(f"  🔨 Compilando PDF...")
        
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
                
                print(f"  ✅ PDF gerado: {pdf_dest.relative_to(PROJECT_ROOT)}")
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
                    print(f"  🧹 Limpou {cleaned} ficheiros")
                self.stats['cleaned'] += cleaned
                
                return True
            else:
                print(f"  ❌ Erro na compilação - PDF não gerado")
                # Salvar log de erro se houver output
                if result and (result.stdout or result.stderr):
                    error_log_file = output_dir / f"{tex_file.stem}_error.log"
                    with open(error_log_file, 'w', encoding='utf-8') as f:
                        f.write(result.stdout or "")
                        f.write("\n=== STDERR ===\n")
                        f.write(result.stderr or "")
                    print(f"  📄 Log salvo em: {error_log_file.name}")
                self.stats['errors'] += 1
                return False
                
        except subprocess.TimeoutExpired:
            print(f"  ⏱️ Timeout na compilação")
            self.stats['errors'] += 1
            return False
        except Exception as e:
            print(f"  ❌ Erro na compilação: {e}")
            self.stats['errors'] += 1
            return False
    
    def scan_and_generate(self, discipline: Optional[str] = None,
                         module: Optional[str] = None,
                         concept: Optional[str] = None,
                         tipo: Optional[str] = None):
        """Escaneia ExerciseDatabase e gera sebentas."""
        
        if self.clean_only:
            print("🧹 Modo limpeza apenas - removendo ficheiros temporários...")
            cleaned = self.clean_temp_files(SEBENTAS_DB, recursive=True)
            print(f"\n✅ Total limpo: {cleaned} ficheiros")
            return
        
        print("📂 Escaneando ExerciseDatabase...")
        
        # Iterar por disciplinas
        for disc_dir in sorted(EXERCISE_DB.iterdir()):
            if not disc_dir.is_dir() or disc_dir.name.startswith('_'):
                continue
            
            if discipline and disc_dir.name != discipline:
                continue
            
            # Iterar por módulos
            for mod_dir in sorted(disc_dir.iterdir()):
                if not mod_dir.is_dir():
                    continue
                
                if module and mod_dir.name != module:
                    continue
                
                print(f"\n📦 Módulo: {disc_dir.name}/{mod_dir.name}")
                module_concepts = []
                
                # Iterar por conceitos
                for conc_dir in sorted(mod_dir.iterdir()):
                    if not conc_dir.is_dir():
                        continue
                    
                    if concept and conc_dir.name != concept:
                        continue
                    
                    # Gerar sebenta
                    tex_file = self.generate_sebenta(
                        disc_dir.name,
                        mod_dir.name,
                        conc_dir.name,
                        conc_dir
                    )
                    
                    # Compilar se gerado
                    if tex_file:
                        success = self.compile_pdf(tex_file)
                        if success:
                            module_concepts.append({
                                'name': conc_dir.name,
                                'tex': tex_file,
                                'pdf': tex_file.with_suffix('.pdf')
                            })
                
                # Gerar sebenta consolidada do módulo se houver conceitos
                if module_concepts and not concept and not self.no_module_sebenta:
                    self.generate_module_sebenta(disc_dir.name, mod_dir.name, module_concepts)
        
        # Estatísticas finais
        print("\n" + "="*60)
        print("📊 RESUMO")
        print("="*60)
        print(f"Sebentas geradas: {self.stats['generated']}")
        print(f"PDFs compilados:  {self.stats['compiled']}")
        print(f"Ficheiros limpos: {self.stats['cleaned']}")
        if self.stats['errors'] > 0:
            print(f"Erros:            {self.stats['errors']}")
        print("="*60)


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description="Gerador de Sebentas v3.0 - Sistema Automático"
    )
    
    parser.add_argument(
        '--discipline',
        help='Filtrar por disciplina (ex: matematica)'
    )
    parser.add_argument(
        '--module',
        help='Filtrar por módulo (ex: P4_funcoes)'
    )
    parser.add_argument(
        '--concept',
        help='Filtrar por conceito específico'
    )
    parser.add_argument(
        '--tipo',
        help='Filtrar por tipo de exercício'
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
    
    args = parser.parse_args()
    
    # Verificar estrutura
    if not EXERCISE_DB.exists():
        print(f"❌ ExerciseDatabase não encontrada: {EXERCISE_DB}")
        sys.exit(1)
    
    # Criar SebentasDatabase se não existir
    SEBENTAS_DB.mkdir(exist_ok=True)
    
    # Executar geração
    generator = SebentaGenerator(
        clean_only=args.clean_only,
        no_compile=args.no_compile,
        no_module_sebenta=args.no_module_sebenta
    )
    
    generator.scan_and_generate(
        discipline=args.discipline,
        module=args.module,
        concept=args.concept,
        tipo=args.tipo
    )


if __name__ == '__main__':
    main()
