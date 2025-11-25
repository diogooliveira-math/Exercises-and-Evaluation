#!/usr/bin/env python3
"""
Sistema de Geração de Testes por Template Editável

Filosofia: Gerar LaTeX completo → Editar → Compilar

Uso:
    python generate_test_template.py [--module MODULE] [--concept CONCEPT] [--questions N]
"""

# Fix encoding issues on Windows
import sys
if sys.platform == 'win32':
    import os
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    # Force UTF-8 encoding for stdout/stderr
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

import os
import sys
import json
import yaml
import subprocess
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Adicionar diretório _tools ao path para importar preview_system
TOOLS_DIR = Path(__file__).parent
EXERCISE_TOOLS_DIR = TOOLS_DIR.parent.parent / "ExerciseDatabase" / "_tools"
sys.path.insert(0, str(EXERCISE_TOOLS_DIR))

try:
    from preview_system import GREEN, BLUE, YELLOW, RED, CYAN, RESET, BOLD
except ImportError:
    # Fallback: sem cores
    GREEN = BLUE = YELLOW = RED = CYAN = RESET = BOLD = ""


class TestTemplate:
    """Gera template editável de teste LaTeX"""
    
    def __init__(self, module: Optional[str] = None, concept: Optional[str] = None, 
                 num_questions: int = 10):
        self.module = module
        self.concept = concept
        self.num_questions = num_questions
        
        self.repo_root = Path(__file__).parent.parent.parent
        self.exercise_db = self.repo_root / "ExerciseDatabase"
        self.sebentas_db = self.repo_root / "SebentasDatabase"
        self.config_file = self.exercise_db / "modules_config.yaml"
        
        self.exercises = []
        self.temp_dir = None
        self.tex_file = None
        
    def load_modules_config(self) -> Dict:
        """Carrega configuração de módulos"""
        with open(self.config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def select_module_and_concept(self) -> Tuple[str, str, str]:
        """Seleção interativa de módulo e conceito"""
        config = self.load_modules_config()
        
        # Disciplina (fixo por agora)
        discipline = 'matematica'
        
        # Módulo
        print(f"\n{BLUE}{'='*70}{RESET}")
        print(f"{BOLD}  ESCOLHA O MÓDULO{RESET}")
        print(f"{BLUE}{'='*70}{RESET}\n")
        
        modules = config[discipline]  # Dicionário de módulos
        module_items = list(modules.items())
        
        for i, (mod_id, mod_data) in enumerate(module_items, 1):
            print(f"  {i}. {mod_data['name']}")
        
        choice = input(f"\n{CYAN}Escolha (1-{len(module_items)}): {RESET}").strip()
        try:
            module_id, module_data = module_items[int(choice) - 1]
        except (ValueError, IndexError):
            print(f"{RED}✗ Escolha inválida{RESET}")
            sys.exit(1)
        
        # Conceito (opcional para teste - pode pegar de vários conceitos)
        print(f"\n{BLUE}{'='*70}{RESET}")
        print(f"{BOLD}  ESCOLHA O CONCEITO (ou deixe vazio para todos){RESET}")
        print(f"{BLUE}{'='*70}{RESET}\n")
        
        concepts = module_data['concepts']  # Lista de conceitos
        for i, concept in enumerate(concepts, 1):
            print(f"  {i}. {concept['name']}")
        print(f"  0. {YELLOW}Todos os conceitos do módulo{RESET}")
        
        choice = input(f"\n{CYAN}Escolha (0-{len(concepts)}): {RESET}").strip()
        
        if choice == '0' or choice == '':
            concept_id = None  # Todos os conceitos
        else:
            try:
                concept_id = concepts[int(choice) - 1]['id']
            except (ValueError, IndexError):
                print(f"{RED}✗ Escolha inválida{RESET}")
                sys.exit(1)
        
        return discipline, module_id, concept_id
    
    def load_exercises(self, discipline: str, module: str, concept: Optional[str] = None) -> List[Dict]:
        """Carrega exercícios do módulo/conceito"""
        index_file = self.exercise_db / "index.json"
        
        with open(index_file, 'r', encoding='utf-8') as f:
            index = json.load(f)
        
        # Filtrar exercícios (suporta estruturas antigas e novas)
        exercises = []
        for ex in index.get('exercises', []):
            # Verificar estrutura (antiga vs nova)
            if 'classification' in ex:
                ex_module = ex['classification']['module']
                ex_concept = ex['classification']['concept']
            else:
                ex_module = ex.get('module', '')
                ex_concept = ex.get('concept', '')
            
            if ex_module != module:
                continue
            if concept and ex_concept != concept:
                continue
            exercises.append(ex)
        
        return exercises
    
    def load_exercises_by_ids(self, exercise_ids: List[str]) -> List[Dict]:
        """Carrega exercícios específicos pelos IDs"""
        index_file = self.exercise_db / "index.json"
        
        with open(index_file, 'r', encoding='utf-8') as f:
            index = json.load(f)
        
        exercises = []
        for ex in index.get('exercises', []):
            if ex.get('id') in exercise_ids:
                exercises.append(ex)
        
        # Ordenar pela ordem dos IDs fornecidos
        exercises.sort(key=lambda x: exercise_ids.index(x.get('id', '')))
        
        return exercises
    
    def select_exercises_interactive(self, exercises: List[Dict]) -> List[Dict]:
        """Seleção interativa de exercícios para o teste"""
        print(f"\n{BLUE}{'='*70}{RESET}")
        print(f"{BOLD}  EXERCÍCIOS DISPONÍVEIS{RESET}")
        print(f"{BLUE}{'='*70}{RESET}\n")
        
        print(f"Total disponível: {len(exercises)} exercícios")
        print(f"Quantidade desejada: {self.num_questions}")
        
        # Agrupar por conceito e tipo
        by_concept = {}
        for ex in exercises:
            if 'classification' in ex:
                concept = ex['classification']['concept_name']
                tipo = ex['classification'].get('tipo_nome', 'Sem tipo')
            else:
                concept = ex.get('concept_name', 'Desconhecido')
                tipo = ex.get('type', 'Sem tipo')
            key = f"{concept} → {tipo}"
            
            if key not in by_concept:
                by_concept[key] = []
            by_concept[key].append(ex)
        
        print(f"\n{YELLOW}Distribuição:{RESET}")
        for key, exs in by_concept.items():
            print(f"  • {key}: {len(exs)} exercícios")
        
        # Opções de seleção
        print(f"\n{CYAN}Modo de seleção:{RESET}")
        print(f"  1. Automático (distribuição equilibrada)")
        print(f"  2. Manual (escolher específicos)")
        print(f"  3. Aleatório simples")
        
        choice = input(f"\n{CYAN}Escolha (1-3) [1]: {RESET}").strip() or '1'
        
        if choice == '1':
            return self._select_balanced(exercises, self.num_questions)
        elif choice == '2':
            return self._select_manual(exercises, self.num_questions)
        else:
            import random
            random.shuffle(exercises)
            return exercises[:self.num_questions]
    
    def _select_balanced(self, exercises: List[Dict], num: int) -> List[Dict]:
        """Seleção equilibrada por conceito/tipo"""
        # Agrupar
        by_concept_type = {}
        for ex in exercises:
            if 'classification' in ex:
                concept = ex['classification']['concept']
                tipo = ex['classification'].get('tipo', 'default')
            else:
                concept = ex.get('concept', 'default')
                tipo = ex.get('type', 'default')
            key = (concept, tipo)
            
            if key not in by_concept_type:
                by_concept_type[key] = []
            by_concept_type[key].append(ex)
        
        # Distribuir
        import random
        selected = []
        groups = list(by_concept_type.values())
        
        # Sortear de cada grupo alternadamente
        while len(selected) < num and any(groups):
            for group in groups:
                if group and len(selected) < num:
                    ex = random.choice(group)
                    selected.append(ex)
                    group.remove(ex)
            # Remover grupos vazios
            groups = [g for g in groups if g]
        
        return selected
    
    def _select_manual(self, exercises: List[Dict], num: int) -> List[Dict]:
        """Seleção manual - mostrar lista e escolher IDs"""
        print(f"\n{YELLOW}Lista de Exercícios:{RESET}")
        for i, ex in enumerate(exercises, 1):
            if 'classification' in ex:
                concept = ex['classification']['concept_name']
                tipo = ex['classification'].get('tipo_nome', '')
                diff = ex['classification']['difficulty']
            else:
                concept = ex.get('concept_name', 'Desconhecido')
                tipo = ex.get('type', '')
                diff = ex.get('difficulty', 0)
            print(f"  {i:2d}. [{ex['id']}] {concept} / {tipo} (dif:{diff})")
        
        print(f"\n{CYAN}Digite os números separados por vírgula (ex: 1,5,8,12){RESET}")
        choice = input(f"Escolha {num} exercícios: ").strip()
        
        try:
            indices = [int(x.strip()) - 1 for x in choice.split(',')]
            selected = [exercises[i] for i in indices if 0 <= i < len(exercises)]
            
            if len(selected) != num:
                print(f"{YELLOW}⚠ Selecionou {len(selected)} exercícios (esperado: {num}){RESET}")
                confirm = input(f"Continuar? (s/n): ").strip().lower()
                if confirm != 's':
                    sys.exit(0)
            
            return selected
        except (ValueError, IndexError) as e:
            print(f"{RED}✗ Erro na seleção: {e}{RESET}")
            sys.exit(1)
    
    def generate_test_latex(self, discipline: str, module_name: str, 
                           concept_name: Optional[str], selected_exercises: List[Dict]) -> str:
        """Gera conteúdo LaTeX completo do teste"""
        
        # Data e título
        today = datetime.now()
        date_str = today.strftime("%d/%m/%Y")
        
        if concept_name:
            title = f"Teste - {concept_name}"
            subtitle = module_name
        else:
            title = f"Teste - {module_name}"
            subtitle = "Vários Conceitos"
        
        # Cabeçalho
        latex = r"""\documentclass[12pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[portuguese]{babel}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{geometry}
\usepackage{enumitem}
\usepackage{fancyhdr}

\geometry{margin=2cm}

% Headers e footers
\pagestyle{fancy}
\fancyhf{}
\lhead{\textbf{""" + title + r"""}}
\rhead{""" + date_str + r"""}
\cfoot{\thepage}

% Comandos de exercícios
\newcounter{exercisecounter}
\setcounter{exercisecounter}{1}

\newcommand{\exercicio}[1]{%
    \noindent\textbf{Exercício \arabic{exercisecounter}:} #1
    \stepcounter{exercisecounter}
    \vspace{0.5em}
}

\newcommand{\subexercicio}[1]{%
    \begin{enumerate}[label=\alph*), leftmargin=2em]
        \item #1
    \end{enumerate}
}

\newcommand{\opcao}[1]{%
    \item #1
}

\begin{document}

% ====================================================================
% TÍTULO
% ====================================================================

\begin{center}
    {\LARGE\textbf{""" + title + r"""}} \\[0.5em]
    {\large """ + subtitle + r"""} \\[0.3em]
    {\normalsize """ + date_str + r"""}
\end{center}

\vspace{1em}

% ====================================================================
% INFORMAÇÕES DO ALUNO
% ====================================================================

\noindent
\textbf{Nome:} \rule{10cm}{0.4pt} \hfill \textbf{N.º:} \rule{2cm}{0.4pt}

\vspace{0.5em}
\noindent
\textbf{Turma:} \rule{2cm}{0.4pt} \hfill \textbf{Data:} \rule{3cm}{0.4pt}

\vspace{1.5em}

% ====================================================================
% INSTRUÇÕES (EDITÁVEL)
% ====================================================================

\noindent
\textbf{Instruções:}
\begin{itemize}[leftmargin=2em]
    \item Leia atentamente todas as questões
    \item Apresente todos os cálculos e justificações
    \item Escreva de forma clara e organizada
\end{itemize}

\vspace{1em}

% ====================================================================
% EXERCÍCIOS
% ====================================================================
"""
        
        # Adicionar exercícios
        for i, ex in enumerate(selected_exercises, 1):
            ex_id = ex['id']
            
            if 'classification' in ex:
                concept = ex['classification']['concept_name']
                tipo = ex['classification'].get('tipo_nome', '')
            else:
                concept = ex.get('concept_name', 'Desconhecido')
                tipo = ex.get('type', '')
            
            # Carregar conteúdo .tex do exercício
            source_file = ex.get('source_file') or ex.get('path', '')
            tex_path = self.exercise_db / source_file
            
            # Ensure .tex extension
            if not str(tex_path).endswith('.tex'):
                tex_path = tex_path.with_suffix('.tex')
            
            if tex_path.exists():
                with open(tex_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extrair apenas o conteúdo dentro de \exercicio{}
                # (remover metadados comentados)
                lines = content.split('\n')
                clean_lines = [l for l in lines if not l.strip().startswith('%')]
                clean_content = '\n'.join(clean_lines)
            else:
                clean_content = r"\exercicio{[Exercício não encontrado: " + source_file + "]}"
            
            latex += f"\n% Exercício {i}: {ex_id} - {concept} / {tipo}\n"
            latex += clean_content
            latex += "\n\n\\vspace{2em}\n\n"
        
        # Rodapé
        latex += r"""
% ====================================================================
% ESPAÇO PARA RASCUNHO (opcional)
% ====================================================================

\newpage

\begin{center}
    {\Large\textbf{Folha de Rascunho}}
\end{center}

\vspace{2em}

% (Espaço em branco)

\end{document}
"""
        
        return latex
    
    def create_template(self) -> str:
        """Cria ficheiro template temporário"""
        self.temp_dir = tempfile.mkdtemp(prefix="test_template_")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"teste_{timestamp}.tex"
        self.tex_file = Path(self.temp_dir) / filename
        
        # Verificar se há exercícios pré-selecionados via ambiente
        selected_exercises_env = os.environ.get('TEST_SELECTED_EXERCISES', '')
        if selected_exercises_env:
            # Carregar exercícios específicos pelos IDs
            selected_ids = [x.strip() for x in selected_exercises_env.split(',') if x.strip()]
            if selected_ids:
                print(f"\n{CYAN}📋 Usando exercícios pré-selecionados: {len(selected_ids)}{RESET}")
                self.exercises = self.load_exercises_by_ids(selected_ids)
                
                if not self.exercises:
                    print(f"{RED}✗ Nenhum exercício encontrado com os IDs fornecidos!{RESET}")
                    sys.exit(1)
                
                print(f"{GREEN}✓ {len(self.exercises)} exercícios carregados{RESET}")
                
                # Usar primeiro exercício para determinar módulo/conceito
                first_ex = self.exercises[0]
                if 'classification' in first_ex:
                    self.module = first_ex['classification'].get('module', '')
                    self.concept = first_ex['classification'].get('concept', '')
                else:
                    self.module = first_ex.get('module', '')
                    self.concept = first_ex.get('concept', '')
            else:
                # Fallback para seleção interativa
                if not self.module:
                    discipline, self.module, self.concept = self.select_module_and_concept()
                else:
                    config = self.load_modules_config()
                    discipline = 'matematica'
                    
                # Carregar exercícios
                print(f"\n{CYAN}📂 Carregando exercícios...{RESET}")
                available_exercises = self.load_exercises(discipline, self.module, self.concept)
                
                if not available_exercises:
                    print(f"{RED}✗ Nenhum exercício encontrado!{RESET}")
                    sys.exit(1)
                
                print(f"{GREEN}✓ {len(available_exercises)} exercícios disponíveis{RESET}")
                
                # Seleção de exercícios
                selected = self.select_exercises_interactive(available_exercises)
                self.exercises = selected
                
                print(f"\n{GREEN}✓ {len(selected)} exercícios selecionados{RESET}")
        else:
            # Seleção interativa normal
            if not self.module:
                discipline, self.module, self.concept = self.select_module_and_concept()
            else:
                # CLI: carregar config para obter nomes
                config = self.load_modules_config()
                discipline = 'matematica'  # Default
                
            # Carregar exercícios
            print(f"\n{CYAN}📂 Carregando exercícios...{RESET}")
            available_exercises = self.load_exercises(discipline, self.module, self.concept)
            
            if not available_exercises:
                print(f"{RED}✗ Nenhum exercício encontrado!{RESET}")
                sys.exit(1)
            
            print(f"{GREEN}✓ {len(available_exercises)} exercícios disponíveis{RESET}")
            
            # Seleção de exercícios
            selected = self.select_exercises_interactive(available_exercises)
            self.exercises = selected
            
            print(f"\n{GREEN}✓ {len(selected)} exercícios selecionados{RESET}")
        
        # Obter nomes para o título
        config = self.load_modules_config()
        discipline = 'matematica'  # Default
        module_name = config.get(discipline, {}).get(self.module, {}).get('name', self.module)
        concept_name = None
        if self.concept:
            # Procurar conceito na lista
            concepts = config.get(discipline, {}).get(self.module, {}).get('concepts', [])
            for c in concepts:
                if c['id'] == self.concept:
                    concept_name = c['name']
                    break
        
        # Gerar LaTeX
        latex_content = self.generate_test_latex(
            discipline, module_name, concept_name, self.exercises
        )
        
        # Salvar
        with open(self.tex_file, 'w', encoding='utf-8') as f:
            f.write(latex_content)
        
        return str(self.tex_file)
    
    def open_for_editing(self):
        """Abre ficheiro no editor padrão"""
        print(f"\n{BLUE}{'='*70}{RESET}")
        print(f"{BOLD}EDITANDO TESTE LATEX{RESET}")
        print(f"{BLUE}{'='*70}{RESET}\n")
        
        print(f"➤ Ficheiro: {CYAN}{self.tex_file.name}{RESET}")
        print(f"➤ Localização: {self.tex_file.parent}")
        
        print(f"\n{YELLOW}Instruções:{RESET}")
        print(f"  1. O LaTeX completo do teste está aberto")
        print(f"  2. Faça ajustes finais:")
        print(f"     • Adicionar/remover exercícios")
        print(f"     • Editar instruções e cotações")
        print(f"     • Ajustar espaçamento")
        print(f"     • Personalizar cabeçalho/rodapé")
        print(f"  3. Salve (Ctrl+S) quando terminar")
        print(f"  4. Feche o editor")
        print(f"  5. Sistema irá compilar automaticamente para PDF")
        
        print(f"\n{BLUE}{'='*70}{RESET}\n")
        
        # Abrir ficheiro
        os.startfile(str(self.tex_file))
        print(f"{GREEN}✓ Ficheiro aberto para edição{RESET}")
    
    def wait_for_edit(self) -> bool:
        """Aguarda edição do utilizador"""
        print(f"\n{YELLOW}⏳ Aguardando edição...{RESET}")
        print(f"{YELLOW}Pressione [Enter] quando terminar...{RESET}")
        input()
        
        # Verificar se foi modificado
        original_time = self.tex_file.stat().st_mtime
        current_time = self.tex_file.stat().st_mtime
        
        if current_time == original_time:
            print(f"\n{YELLOW}⚠️ Ficheiro não foi modificado{RESET}")
            choice = input(f"Compilar mesmo assim? (s/n): ").strip().lower()
            return choice == 's'
        
        return True
    
    def compile_pdf(self) -> Optional[Path]:
        """Compila LaTeX para PDF"""
        print(f"\n{BLUE}{'='*70}{RESET}")
        print(f"{BOLD}🔨 COMPILANDO PDF{RESET}")
        print(f"{BLUE}{'='*70}{RESET}\n")
        
        # Executar pdflatex (2x para referencias)
        for run in range(2):
            try:
                result = subprocess.run(
                    ['pdflatex', '-interaction=nonstopmode', str(self.tex_file)],
                    cwd=str(self.temp_dir),
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                # Verificar se realmente falhou (não apenas warnings)
                # Se o PDF foi gerado, é sucesso mesmo com warnings
                pdf_test = self.tex_file.with_suffix('.pdf')
                if result.returncode != 0 and not pdf_test.exists():
                    print(f"{RED}✗ Erro na compilação:{RESET}")
                    print(result.stdout[-1000:])  # Últimas linhas
                    return None
                    
            except subprocess.TimeoutExpired:
                print(f"{RED}✗ Timeout na compilação (>60s){RESET}")
                return None
            except FileNotFoundError:
                print(f"{RED}✗ pdflatex não encontrado! Instale MiKTeX ou TeX Live{RESET}")
                return None
        
        # Verificar PDF gerado
        pdf_file = self.tex_file.with_suffix('.pdf')
        
        if not pdf_file.exists():
            print(f"{RED}✗ PDF não foi gerado{RESET}")
            return None
        
        print(f"{GREEN}✓ PDF compilado com sucesso!{RESET}")
        return pdf_file
    
    def move_to_output(self, pdf_path: Path) -> Path:
        """Move PDF para localização final"""
        # Estrutura: SebentasDatabase/disciplina/modulo/conceito/tests/
        discipline = 'matematica'  # Default
        
        if self.concept:
            output_dir = (self.sebentas_db / discipline / self.module / 
                         self.concept / "tests")
        else:
            output_dir = (self.sebentas_db / discipline / self.module / 
                         "tests")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Nome final
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        final_name = f"teste_{self.module}"
        if self.concept:
            final_name += f"_{self.concept}"
        final_name += f"_{timestamp}.pdf"
        
        final_path = output_dir / final_name
        shutil.copy(pdf_path, final_path)
        
        print(f"{GREEN}✓ PDF movido para:{RESET} {final_path}")
        return final_path
    
    def cleanup(self):
        """Remove ficheiros temporários"""
        if self.temp_dir and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
            print(f"{CYAN}🗑️  Temporários removidos{RESET}")
    
    def run(self):
        """Executa workflow completo"""
        try:
            print(f"\n{BLUE}{'='*70}{RESET}")
            print(f"{BOLD}  SISTEMA DE TESTES POR TEMPLATE  {RESET}")
            print(f"{BLUE}{'='*70}{RESET}")
            
            # 1. Criar template
            tex_path = self.create_template()
            
            # 2. Abrir para edição
            self.open_for_editing()
            
            # 3. Aguardar edição
            if not self.wait_for_edit():
                print(f"\n{YELLOW}❌ Operação cancelada{RESET}")
                self.cleanup()
                return
            
            # 4. Compilar PDF
            pdf_path = self.compile_pdf()
            
            if not pdf_path:
                print(f"\n{RED}❌ Falha na compilação{RESET}")
                self.cleanup()
                return
            
            # 5. Mover para localização final
            final_path = self.move_to_output(pdf_path)
            
            # 6. Resumo
            print(f"\n{BLUE}{'='*70}{RESET}")
            print(f"{BOLD}✅ TESTE GERADO COM SUCESSO!{RESET}")
            print(f"{BLUE}{'='*70}{RESET}\n")
            
            print(f"{CYAN}📄 PDF:{RESET} {final_path}")
            print(f"{CYAN}📊 Exercícios:{RESET} {len(self.exercises)}")
            
            # Distribuição por conceito/tipo
            by_concept = {}
            for ex in self.exercises:
                if 'classification' in ex:
                    concept = ex['classification']['concept_name']
                else:
                    concept = ex.get('concept_name', 'Desconhecido')
                if concept not in by_concept:
                    by_concept[concept] = 0
                by_concept[concept] += 1
            
            print(f"\n{CYAN}📋 Distribuição:{RESET}")
            for concept, count in by_concept.items():
                print(f"  • {concept}: {count} exercícios")
            
            # Abrir PDF
            choice = input(f"\nAbrir PDF? (s/n): ").strip().lower()
            if choice == 's':
                os.startfile(str(final_path))
            
            # 7. Cleanup
            self.cleanup()
            
        except KeyboardInterrupt:
            print(f"\n\n{YELLOW}⚠️  Operação cancelada pelo utilizador{RESET}")
            self.cleanup()
        except Exception as e:
            print(f"\n{RED}✗ Erro: {e}{RESET}")
            import traceback
            traceback.print_exc()
            self.cleanup()


def main():
    """Entrada principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Gerador de Testes por Template Editável",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python generate_test_template.py
  python generate_test_template.py --module P4_funcoes --questions 15
  python generate_test_template.py --module P4_funcoes --concept 4-funcao_inversa
        """
    )
    
    parser.add_argument('--module', help='ID do módulo (ex: P4_funcoes)')
    parser.add_argument('--concept', help='ID do conceito (ex: 4-funcao_inversa)')
    parser.add_argument('--questions', type=int, default=10, 
                       help='Número de questões (padrão: 10)')
    
    args = parser.parse_args()
    
    generator = TestTemplate(
        module=args.module,
        concept=args.concept,
        num_questions=args.questions
    )
    
    generator.run()


if __name__ == '__main__':
    main()
