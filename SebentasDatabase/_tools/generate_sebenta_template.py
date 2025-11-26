#!/usr/bin/env python3
"""
Sistema de Geração de Sebentas por Template
===========================================

Workflow:
1. Seleciona módulo/conceito para sebenta
2. Sistema gera LaTeX completo da sebenta
3. Abre automaticamente no VS Code para revisão/edição
4. Utilizador pode fazer "final touches" no LaTeX
5. Salva e confirma
6. Sistema compila PDF final

Vantagens:
- Controle total sobre o LaTeX final
- Edição antes da compilação
- Preview visual completo
- Sem recompilações desnecessárias
"""

import json
import os
import sys
import tempfile
import time
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List, Tuple

# Adicionar paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "ExerciseDatabase" / "_tools"))

try:
    from preview_system import PreviewManager, Colors
except ImportError:
    PreviewManager = None
    class Colors:
        HEADER = '\033[95m'
        BLUE = '\033[94m'
        CYAN = '\033[96m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        RED = '\033[91m'
        END = '\033[0m'
        BOLD = '\033[1m'


class SebentaTemplate:
    """Gerencia templates de sebentas editáveis."""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.exercise_db = base_path / "ExerciseDatabase"
        self.sebenta_db = base_path / "SebentasDatabase"
        self.temp_file = None
        self.temp_dir = None
        self.config = {}
        
    def load_modules_config(self) -> Dict:
        """Carrega configuração de módulos."""
        config_path = self.exercise_db / "modules_config.yaml"
        
        if not config_path.exists():
            return {}
        
        import yaml
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def load_exercises_for_concept(self, discipline: str, module: str, concept: str) -> List[Dict]:
        """Carrega exercícios de um conceito específico."""
        concept_path = self.exercise_db / discipline / module / concept
        
        if not concept_path.exists():
            return []
        
        exercises = []
        
        # Percorrer todos os tipos dentro do conceito
        for tipo_dir in concept_path.iterdir():
            if not tipo_dir.is_dir():
                continue
            
            # Procurar ficheiros .tex
            for tex_file in tipo_dir.glob("*.tex"):
                # Ler conteúdo
                with open(tex_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                exercises.append({
                    'id': tex_file.stem,
                    'path': tex_file,
                    'tipo': tipo_dir.name,
                    'content': content
                })
        
        return exercises
    
    def generate_sebenta_latex(self, config: Dict, exercises: List[Dict]) -> str:
        """
        Gera LaTeX completo da sebenta.
        
        Args:
            config: Configuração da sebenta (disciplina, módulo, conceito)
            exercises: Lista de exercícios
            
        Returns:
            String com LaTeX completo
        """
        timestamp = datetime.now().strftime("%Y-%m-%d")
        
        latex = f"""% ====================================================================
% SEBENTA - {config.get('module_name', 'Sem Título')}
% ====================================================================
%
% Conceito: {config.get('concept_name', 'N/A')}
% Gerado: {timestamp}
% Total de Exercícios: {len(exercises)}
%
% INSTRUÇÕES:
% • Este é o LaTeX COMPLETO da sebenta
% • Pode editar livremente antes de compilar
% • Adicione/remova exercícios conforme necessário
% • Ajuste formatação, títulos, espaçamentos
% • Salve e feche quando terminar
% • Sistema irá compilar automaticamente
%
% ====================================================================

\\documentclass[12pt,a4paper]{{article}}

% ──────────────────────────────────────────────────────────────────
% PACOTES
% ──────────────────────────────────────────────────────────────────

\\usepackage[utf8]{{inputenc}}
\\usepackage[portuguese]{{babel}}
\\usepackage{{amsmath,amssymb,amsthm}}
\\usepackage{{graphicx}}
\\usepackage{{geometry}}
\\usepackage{{fancyhdr}}
\\usepackage{{hyperref}}
\\usepackage{{enumitem}}

\\geometry{{a4paper, margin=2.5cm}}

% ──────────────────────────────────────────────────────────────────
% MACROS PERSONALIZADAS
% ──────────────────────────────────────────────────────────────────

\\newcommand{{\\exercicio}}[1]{{%
    \\subsection*{{Exercício}}
    #1
}}

\\newcommand{{\\subexercicio}}[1]{{%
    \\begin{{enumerate}}[label=\\alph*)]
        \\item #1
    \\end{{enumerate}}
}}

\\newcommand{{\\opcao}}[1]{{%
    \\item #1
}}

\\newcommand{{\\solucao}}[1]{{%
    \\paragraph{{Solução:}} #1
}}

% ──────────────────────────────────────────────────────────────────
% CONFIGURAÇÃO DE CABEÇALHO
% ──────────────────────────────────────────────────────────────────

\\pagestyle{{fancy}}
\\fancyhf{{}}
\\fancyhead[L]{{{config.get('module_name', '')}}}
\\fancyhead[R]{{{config.get('concept_name', '')}}}
\\fancyfoot[C]{{\\thepage}}

% ──────────────────────────────────────────────────────────────────
% TÍTULO
% ──────────────────────────────────────────────────────────────────

\\title{{
    \\textbf{{{config.get('module_name', 'Sebenta')}}}\\\\
    \\large {config.get('concept_name', '')}
}}
\\author{{}}
\\date{{{timestamp}}}

% ====================================================================
% INÍCIO DO DOCUMENTO
% ====================================================================

\\begin{{document}}

\\maketitle
\\tableofcontents
\\newpage

% ====================================================================
% EXERCÍCIOS
% ====================================================================

"""
        
        # Adicionar exercícios agrupados por tipo
        exercises_by_type = {}
        for ex in exercises:
            tipo = ex['tipo']
            if tipo not in exercises_by_type:
                exercises_by_type[tipo] = []
            exercises_by_type[tipo].append(ex)
        
        for tipo, tipo_exercises in exercises_by_type.items():
            latex += f"""
% ──────────────────────────────────────────────────────────────────
% TIPO: {tipo.replace('_', ' ').title()}
% ──────────────────────────────────────────────────────────────────

\\section{{{tipo.replace('_', ' ').title()}}}

"""
            
            for ex in tipo_exercises:
                latex += f"""
% Exercício: {ex['id']}
{ex['content']}

\\vspace{{1cm}}

"""
        
        latex += """
% ====================================================================
% FIM DO DOCUMENTO
% ====================================================================

\\end{document}
"""
        
        return latex
    
    def create_template(self, config: Dict, exercises: List[Dict]) -> Path:
        """Cria template LaTeX da sebenta."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.temp_dir = Path(tempfile.gettempdir()) / f"sebenta_template_{timestamp}"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Nome do ficheiro
        concept_clean = config.get('concept', 'conceito').replace('-', '_')
        filename = f"sebenta_{concept_clean}.tex"
        self.temp_file = self.temp_dir / filename
        
        # Gerar LaTeX
        latex_content = self.generate_sebenta_latex(config, exercises)
        
        # Salvar
        with open(self.temp_file, 'w', encoding='utf-8') as f:
            f.write(latex_content)
        
        # Criar README
        readme_path = self.temp_dir / "README.txt"
        readme_content = f"""
════════════════════════════════════════════════════════════════
TEMPLATE DE SEBENTA - PRONTO PARA EDIÇÃO
════════════════════════════════════════════════════════════════

Módulo: {config.get('module_name', '')}
Conceito: {config.get('concept_name', '')}
Total de Exercícios: {len(exercises)}

FICHEIRO PRINCIPAL:
→ {filename}

INSTRUÇÕES:
1. O ficheiro LaTeX está completo e pronto para compilar
2. Faça "final touches":
   • Adicione/remova exercícios
   • Ajuste formatação
   • Corrija títulos ou texto
   • Adicione notas ou observações
3. Salve o ficheiro quando terminar (Ctrl+S)
4. Feche o editor
5. Pressione Enter no terminal
6. Sistema irá compilar automaticamente para PDF

EXERCÍCIOS INCLUÍDOS POR TIPO:
"""
        
        # Listar exercícios por tipo
        exercises_by_type = {}
        for ex in exercises:
            tipo = ex['tipo']
            if tipo not in exercises_by_type:
                exercises_by_type[tipo] = []
            exercises_by_type[tipo].append(ex['id'])
        
        for tipo, ids in exercises_by_type.items():
            readme_content += f"\n{tipo}:\n"
            for ex_id in ids:
                readme_content += f"  • {ex_id}\n"
        
        readme_content += f"""
════════════════════════════════════════════════════════════════
Localização: {self.temp_dir}
Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
════════════════════════════════════════════════════════════════
"""
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        self.config = config
        return self.temp_file
    
    def open_for_editing(self) -> bool:
        """Abre template no VS Code para edição."""
        if not self.temp_file:
            return False
        
        print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}📝 EDITANDO SEBENTA LATEX{Colors.END}")
        print(f"{Colors.CYAN}{'='*70}{Colors.END}\n")
        print(f"{Colors.YELLOW}➤ Ficheiro:{Colors.END} {Colors.BOLD}{self.temp_file.name}{Colors.END}")
        print(f"{Colors.YELLOW}➤ Localização:{Colors.END} {self.temp_dir}")
        print(f"\n{Colors.CYAN}Instruções:{Colors.END}")
        print(f"  1. O LaTeX completo da sebenta está aberto")
        print(f"  2. Faça ajustes finais (adicionar/remover/editar)")
        print(f"  3. {Colors.BOLD}Salve (Ctrl+S){Colors.END} quando terminar")
        print(f"  4. Feche o editor")
        print(f"  5. Sistema irá compilar automaticamente para PDF\n")
        print(f"{Colors.CYAN}{'='*70}{Colors.END}\n")
        
        try:
            os.startfile(str(self.temp_file))
            print(f"{Colors.GREEN}✓ Ficheiro aberto para edição{Colors.END}\n")
            return True
        except Exception as e:
            print(f"{Colors.RED}❌ Erro ao abrir: {e}{Colors.END}")
            print(f"{Colors.YELLOW}📂 Abra manualmente: {self.temp_file}{Colors.END}\n")
            return False
    
    def wait_for_edit(self) -> bool:
        """Aguarda que utilizador edite e salve."""
        if not self.temp_file or not self.temp_file.exists():
            return False
        
        initial_mtime = self.temp_file.stat().st_mtime
        
        print(f"{Colors.CYAN}⏳ Aguardando edição...{Colors.END}")
        print(f"{Colors.CYAN}Pressione [Enter] quando terminar...{Colors.END}", end='', flush=True)
        
        try:
            input()
            
            # Verificar se foi modificado
            if self.temp_file.stat().st_mtime > initial_mtime:
                print(f"\n{Colors.GREEN}✓ Ficheiro editado e salvo{Colors.END}\n")
                return True
            else:
                print(f"\n{Colors.YELLOW}⚠️ Ficheiro não foi modificado{Colors.END}")
                retry = input(f"{Colors.CYAN}Compilar mesmo assim? (s/n): {Colors.END}").strip().lower()
                return retry in ['s', 'sim', 'y', 'yes']
        except KeyboardInterrupt:
            print(f"\n\n{Colors.RED}❌ Operação cancelada{Colors.END}")
            return False
    
    def compile_pdf(self, output_path: Optional[Path] = None) -> Tuple[bool, Optional[Path]]:
        """
        Compila LaTeX para PDF.
        
        Args:
            output_path: Caminho de saída para o PDF
            
        Returns:
            Tupla (sucesso, caminho_do_pdf)
        """
        if not self.temp_file or not self.temp_file.exists():
            return False, None
        
        print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}🔨 COMPILANDO PDF{Colors.END}")
        print(f"{Colors.CYAN}{'='*70}{Colors.END}\n")
        
        try:
            # Compilar com pdflatex
            result = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', str(self.temp_file)],
                cwd=str(self.temp_dir),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            pdf_path = self.temp_file.with_suffix('.pdf')
            
            if pdf_path.exists():
                print(f"{Colors.GREEN}✓ PDF compilado com sucesso!{Colors.END}")
                
                # Mover para localização final se especificado
                if output_path:
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    import shutil
                    shutil.copy2(pdf_path, output_path)
                    print(f"{Colors.GREEN}✓ PDF movido para: {output_path}{Colors.END}\n")
                    return True, output_path
                else:
                    print(f"{Colors.GREEN}✓ PDF em: {pdf_path}{Colors.END}\n")
                    return True, pdf_path
            else:
                print(f"{Colors.RED}❌ Falha na compilação{Colors.END}")
                print(f"{Colors.YELLOW}Verifique os erros no log{Colors.END}\n")
                return False, None
                
        except subprocess.TimeoutExpired:
            print(f"{Colors.RED}❌ Timeout na compilação{Colors.END}\n")
            return False, None
        except FileNotFoundError:
            print(f"{Colors.RED}❌ pdflatex não encontrado{Colors.END}")
            print(f"{Colors.YELLOW}Instale LaTeX para compilar PDFs{Colors.END}\n")
            return False, None
        except Exception as e:
            print(f"{Colors.RED}❌ Erro: {e}{Colors.END}\n")
            return False, None
    
    def cleanup(self, keep_pdf: bool = False):
        """Remove ficheiros temporários."""
        if self.temp_dir and self.temp_dir.exists():
            try:
                if keep_pdf and self.temp_file:
                    pdf_path = self.temp_file.with_suffix('.pdf')
                    if pdf_path.exists():
                        print(f"{Colors.CYAN}PDF temporário mantido em: {pdf_path}{Colors.END}")
                
                # Remover ficheiros auxiliares LaTeX
                for ext in ['.aux', '.log', '.out', '.toc']:
                    aux_file = self.temp_file.with_suffix(ext) if self.temp_file else None
                    if aux_file and aux_file.exists():
                        aux_file.unlink()
            except:
                pass


def main():
    """Função principal."""
    base_path = Path(__file__).parent.parent.parent
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}  📚 SISTEMA DE SEBENTAS POR TEMPLATE  {Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}\n")
    
    template = SebentaTemplate(base_path)
    
    # Configuração de exemplo (deve vir de argumentos CLI)
    config = {
        'discipline': 'matematica',
        'module': 'A8_modelos_discretos',
        'module_name': 'Módulo A8 - Modelos Discretos',
        'concept': '1-sistemas_numericos',
        'concept_name': 'Sistemas Numéricos'
    }
    
    # Carregar exercícios
    print(f"{Colors.CYAN}📂 Carregando exercícios...{Colors.END}")
    exercises = template.load_exercises_for_concept(
        config['discipline'],
        config['module'],
        config['concept']
    )
    
    if not exercises:
        print(f"{Colors.RED}❌ Nenhum exercício encontrado para este conceito{Colors.END}")
        return 1
    
    print(f"{Colors.GREEN}✓ {len(exercises)} exercícios carregados{Colors.END}\n")
    
    # 1. Criar template LaTeX
    template_path = template.create_template(config, exercises)
    
    # 2. Abrir para edição
    if not template.open_for_editing():
        print(f"{Colors.RED}Falha ao abrir template{Colors.END}")
        return 1
    
    # 3. Aguardar edição
    if not template.wait_for_edit():
        print(f"{Colors.RED}Operação cancelada{Colors.END}")
        template.cleanup()
        return 1
    
    # 4. Compilar PDF
    output_dir = base_path / "SebentasDatabase" / config['discipline'] / config['module'] / config['concept'] / "pdfs"
    output_path = output_dir / f"sebenta_{config['concept']}.pdf"
    
    success, pdf_path = template.compile_pdf(output_path)
    
    if success:
        print(f"{Colors.GREEN}{'='*70}{Colors.END}")
        print(f"{Colors.GREEN}{Colors.BOLD}✅ SEBENTA GERADA COM SUCESSO!{Colors.END}")
        print(f"{Colors.GREEN}{'='*70}{Colors.END}\n")
        print(f"{Colors.CYAN}📄 PDF:{Colors.END} {pdf_path}")
        print(f"{Colors.CYAN}📊 Exercícios:{Colors.END} {len(exercises)}\n")
        
        # Perguntar se quer abrir PDF
        response = input(f"{Colors.CYAN}Abrir PDF? (s/n): {Colors.END}").strip().lower()
        if response in ['s', 'sim', 'y', 'yes']:
            try:
                os.startfile(str(pdf_path))
            except:
                pass
        
        template.cleanup(keep_pdf=False)
        return 0
    else:
        print(f"{Colors.RED}❌ Falha na geração da sebenta{Colors.END}")
        template.cleanup(keep_pdf=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
