"""
Sistema de Pré-visualização e Curadoria
========================================
Módulo centralizado para geração de conteúdo com aprovação do utilizador.
Permite visualizar o que será criado antes de adicionar à base de dados.

Características:
- Ficheiro consolidado único com todo o conteúdo estruturado
- Abertura automática de ficheiros em VS Code para revisão
- Interface de confirmação interactiva
- Suporte para ficheiros .tex, .json e .pdf
- Preview em formato LaTeX ou TXT
- Integração com todos os scripts de geração

Uso:
    from preview_system import PreviewManager
    
    # Preview consolidado (padrão - recomendado)
    preview = PreviewManager(consolidated_preview=True)
    content = {"exercise.tex": tex_content, "metadata.json": json_content}
    
    if preview.show_and_confirm(content, "Novo Exercício"):
        # User confirmed, proceed with saving
        pass
    
    # Preview com ficheiros separados (modo antigo)
    preview = PreviewManager(consolidated_preview=False)
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime
import sys

# Cores para terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

# Helper to print safely in terminals with limited encodings
def safe_print(s: str):
    try:
        print(s)
    except UnicodeEncodeError:
        try:
            enc = sys.stdout.encoding or 'utf-8'
            print(s.encode(enc, errors='replace').decode(enc))
        except Exception:
            # last resort: strip non-ascii
            print(''.join((ch if ord(ch) < 128 else '?') for ch in s))



class PreviewManager:
    """Gestor de pré-visualização de conteúdo antes de adicionar à base de dados."""
    
    def __init__(self, auto_open: bool = True, consolidated_preview: bool = True):
        """
        Inicializa o gestor de preview.
        
        Args:
            auto_open: Se True, abre automaticamente os ficheiros em VS Code
            consolidated_preview: Se True, cria um único ficheiro consolidado com todo o conteúdo
        """
        self.auto_open = auto_open
        self.consolidated_preview = consolidated_preview
        self.temp_dir = None
        self.temp_files = []
        
    def create_temp_preview(self, content: Dict[str, str], title: str = "Preview") -> Path:
        """
        Cria ficheiros temporários para preview.
        
        Args:
            content: Dicionário {filename: content}
            title: Título do preview
            
        Returns:
            Path para o diretório temporário
        """
        # Criar diretório temporário
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.temp_dir = Path(tempfile.gettempdir()) / f"exercise_preview_{timestamp}"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Criar ficheiros
        for filename, file_content in content.items():
            file_path = self.temp_dir / filename
            
            # Se for JSON, formatar bonito
            if filename.endswith('.json'):
                try:
                    json_data = json.loads(file_content) if isinstance(file_content, str) else file_content
                    file_content = json.dumps(json_data, indent=2, ensure_ascii=False)
                except:
                    pass
            
            # Salvar ficheiro
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_content)
            
            self.temp_files.append(file_path)
        
        # Criar README com informações
        readme_path = self.temp_dir / "README_PREVIEW.txt"
        readme_content = f"""

  PREVIEW: {title:^54} 


Este diretório contém uma PRÉ-VISUALIZAÇÃO do conteúdo que será
adicionado à base de dados.

FICHEIROS GERADOS:
"""
        for filename in content.keys():
            readme_content += f"  • {filename}\n"
        
        readme_content += f"""
INSTRUÇÕES:
1. Reveja cuidadosamente cada ficheiro
2. Verifique o conteúdo LaTeX, metadados e estrutura
3. Retorne ao terminal e confirme ou cancele

LOCALIZAÇÃO:
{self.temp_dir}

TIMESTAMP: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}


ATENÇÃO: Estes ficheiros são temporários e serão removidos após
         a confirmação ou cancelamento.

"""
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        self.temp_files.append(readme_path)
        
        # Criar ficheiro consolidado se configurado
        if self.consolidated_preview:
            consolidated_path = self.create_consolidated_preview(content, title)
            self.temp_files.insert(0, consolidated_path)  # Primeiro na lista para abrir primeiro
        
        return self.temp_dir
    
    def create_consolidated_preview(self, content: Dict[str, str], title: str) -> Path:
        """
        Cria um ficheiro único consolidado com todo o conteúdo estruturado.
        
        Args:
            content: Dicionário {filename: content}
            title: Título do preview
            
        Returns:
            Path para o ficheiro consolidado
        """
        if not self.temp_dir:
            raise ValueError("Temp directory not initialized. Call create_temp_preview first.")
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Determinar extensão baseada no conteúdo
        has_tex = any(fname.endswith('.tex') for fname in content.keys())
        extension = '.tex' if has_tex else '.txt'
        
        consolidated_path = self.temp_dir / f"PREVIEW_CONSOLIDADO{extension}"
        
        # Construir conteúdo consolidado
        consolidated_content = []
        
        if has_tex:
            # Formato LaTeX
            consolidated_content.append("% " + "=" * 68)
            consolidated_content.append(f"% PREVIEW CONSOLIDADO: {title}")
            consolidated_content.append(f"% Gerado em: {timestamp}")
            consolidated_content.append("% " + "=" * 68)
            consolidated_content.append("%")
            consolidated_content.append("% ATENÇÃO: Este é um ficheiro de PRÉ-VISUALIZAÇÃO")
            consolidated_content.append("% O conteúdo abaixo será adicionado à base de dados após confirmação.")
            consolidated_content.append("%")
            consolidated_content.append("% " + "=" * 68)
            # Insert a defensive preamble: try to include project style.tex from
            # workspace absolute path first, then relative fallbacks. If none are
            # found, define minimal counters/macros so \exercicio / \subexercicio
            # produce numbered output in the consolidated preview.
            try:
                workspace_style = Path(__file__).resolve().parents[2] / "Teste_modelo" / "config" / "style.tex"
                style_path = workspace_style.as_posix()
            except Exception:
                style_path = None

            if style_path:
                consolidated_content.append("")
                consolidated_content.append("% Project style injection - try workspace absolute path then relative fallbacks")
                consolidated_content.append(r"\IfFileExists{" + style_path + r"}{\input{" + style_path + r"}}{%")
                consolidated_content.append(r"  \IfFileExists{../../../../Teste_modelo/config/style.tex}{\input{../../../../Teste_modelo/config/style.tex}}{%")
                consolidated_content.append(r"    \IfFileExists{../../../Teste_modelo/config/style.tex}{\input{../../../Teste_modelo/config/style.tex}}{%")
                consolidated_content.append(r"      \IfFileExists{../../Teste_modelo/config/style.tex}{\input{../../Teste_modelo/config/style.tex}}{%")
                consolidated_content.append(r"        % style.tex not found - define minimal counters/macros defensively")
                consolidated_content.append(r"        \makeatletter")
                consolidated_content.append(r"        \@ifundefined{exerciciocount}{\newcounter{exerciciocount}}{}")
                consolidated_content.append(r"        \@ifundefined{subexerciciocount}{\newcounter{subexerciciocount}}{}")
                consolidated_content.append(r"        \@ifundefined{optioncount}{\newcounter{optioncount}}{}")
                consolidated_content.append(r"        \newcommand{\exercicio}[1]{\par\vspace{1.5em}\refstepcounter{exerciciocount}\setcounter{subexerciciocount}{0}\setcounter{optioncount}{0}\noindent\textbf{Exercício~\theexerciciocount.} #1\par\vspace{0.5em}}")
                consolidated_content.append(r"        \newcommand{\subexercicio}[1]{\par\vspace{0.8em}\refstepcounter{subexerciciocount}\noindent\textbf{\theexerciciocount.\thesubexerciciocount.} #1\par\vspace{0.3em}}")
                consolidated_content.append(r"        \newcommand{\option}[1]{\par\refstepcounter{optioncount}\noindent(\alph{optioncount}) #1}")
                consolidated_content.append(r"        \makeatother")
                consolidated_content.append(r"      }%")
                consolidated_content.append(r"    }%")
                consolidated_content.append(r"  }%")
                consolidated_content.append(r"}%")
                consolidated_content.append("")
            else:
                # Fallback: add a minimal defensive macro block using relative paths
                consolidated_content.append("")
                consolidated_content.append("% Project style injection - relative fallbacks and defensive macros")
                consolidated_content.append(r"\IfFileExists{../../../../Teste_modelo/config/style.tex}{\input{../../../../Teste_modelo/config/style.tex}}{%")
                consolidated_content.append(r"  \IfFileExists{../../../Teste_modelo/config/style.tex}{\input{../../../Teste_modelo/config/style.tex}}{%")
                consolidated_content.append(r"    \IfFileExists{../../Teste_modelo/config/style.tex}{\input{../../Teste_modelo/config/style.tex}}{%")
                consolidated_content.append(r"      \makeatletter")
                consolidated_content.append(r"      \@ifundefined{exerciciocount}{\newcounter{exerciciocount}}{}")
                consolidated_content.append(r"      \@ifundefined{subexerciciocount}{\newcounter{subexerciciocount}}{}")
                consolidated_content.append(r"      \@ifundefined{optioncount}{\newcounter{optioncount}}{}")
                consolidated_content.append(r"      \newcommand{\exercicio}[1]{\par\vspace{1.5em}\refstepcounter{exerciciocount}\setcounter{subexerciciocount}{0}\setcounter{optioncount}{0}\noindent\textbf{Exercício~\theexerciciocount.} #1\par\vspace{0.5em}}")
                consolidated_content.append(r"      \newcommand{\subexercicio}[1]{\par\vspace{0.8em}\refstepcounter{subexerciciocount}\noindent\textbf{\theexerciciocount.\thesubexerciciocount.} #1\par\vspace{0.3em}}")
                consolidated_content.append(r"      \newcommand{\option}[1]{\par\refstepcounter{optioncount}\noindent(\alph{optioncount}) #1}")
                consolidated_content.append(r"      \makeatother")
                consolidated_content.append(r"    }%")
                consolidated_content.append(r"  }%")
                consolidated_content.append(r"}%")
                consolidated_content.append("")
            consolidated_content.append("")
        else:
            # Formato texto
            consolidated_content.append("=" * 70)
            consolidated_content.append(f"  PREVIEW CONSOLIDADO: {title}")
            consolidated_content.append(f"  Gerado em: {timestamp}")
            consolidated_content.append("=" * 70)
            consolidated_content.append("")
            consolidated_content.append("ATENÇÃO: Este é um ficheiro de PRÉ-VISUALIZAÇÃO")
            consolidated_content.append("O conteúdo abaixo será adicionado à base de dados após confirmação.")
            consolidated_content.append("")
            consolidated_content.append("=" * 70)
            consolidated_content.append("")
        
        # Adicionar cada ficheiro como seção
        files_added = 0
        for idx, (filename, file_content) in enumerate(content.items(), 1):
            # Ensure we have something sensible in file_content; if empty, try to read from temp files
            if not file_content and self.temp_dir:
                candidate = self.temp_dir / filename
                if candidate.exists():
                    try:
                        file_content = candidate.read_text(encoding='utf-8')
                    except Exception:
                        file_content = f"% ERRO: Não foi possível ler {filename}"
                else:
                    file_content = f"% AVISO: Conteúdo para {filename} está vazio"

            if has_tex:
                consolidated_content.append("")
                consolidated_content.append("% " + "-" * 68)
                consolidated_content.append(f"% FICHEIRO {idx}: {filename}")
                consolidated_content.append("% " + "-" * 68)
                consolidated_content.append("")
            else:
                consolidated_content.append("")
                consolidated_content.append("-" * 70)
                consolidated_content.append(f"  FICHEIRO {idx}: {filename}")
                consolidated_content.append("-" * 70)
                consolidated_content.append("")
            
            # Adicionar conteúdo do ficheiro
            if filename.endswith('.json'):
                # Formatar JSON bonito
                try:
                    json_data = json.loads(file_content) if isinstance(file_content, str) else file_content
                    formatted_json = json.dumps(json_data, indent=2, ensure_ascii=False)
                    
                    if has_tex:
                        # Comentar cada linha para LaTeX
                        for line in formatted_json.split('\n'):
                            consolidated_content.append(f"% {line}")
                    else:
                        consolidated_content.append(formatted_json)
                    files_added += 1
                except Exception:
                    consolidated_content.append(file_content)
            else:
                # Adicionar conteúdo direto
                consolidated_content.append(file_content)
                files_added += 1
        
        # Rodapé
        if files_added == 0:
            # Log a warning by inserting a visible message in the consolidated file
            consolidated_content.append("")
            consolidated_content.append("% AVISO: Nenhum conteúdo válido foi adicionado ao preview consolidado.")
            consolidated_content.append("% Verifique se os geradores estão a preencher o dicionário de conteúdo corretamente.")
            consolidated_content.append("")

        consolidated_content.append("")
        if has_tex:
            consolidated_content.append("% " + "=" * 68)
            consolidated_content.append("% FIM DO PREVIEW")
            consolidated_content.append("% " + "=" * 68)
        else:
            consolidated_content.append("=" * 70)
            consolidated_content.append("  FIM DO PREVIEW")
            consolidated_content.append("=" * 70)
        
        # Salvar ficheiro consolidado
        with open(consolidated_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(consolidated_content))
        
        return consolidated_path
    
    def open_in_vscode(self, paths: Union[Path, List[Path]]) -> bool:
        """
        Abre ficheiros em VS Code para revisão.
        
        Args:
            paths: Path único ou lista de paths
            
        Returns:
            True se abriu com sucesso
        """
        if isinstance(paths, Path):
            paths = [paths]
        
        # Tentar múltiplos métodos para abrir VS Code
        vscode_commands = [
            "code",
            "code.cmd",
            r"C:\Program Files\Microsoft VS Code\Code.exe",
            r"C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\Code.exe",
            r"C:\Program Files\Microsoft VS Code\bin\code.cmd"
        ]
        
        # Expandir variáveis de ambiente
        import os
        vscode_commands = [os.path.expandvars(cmd) for cmd in vscode_commands]
        
        success = False
        for cmd in vscode_commands:
            try:
                # Abrir todos os ficheiros relevantes (não README)
                for path in paths:
                    if path.name != "README_PREVIEW.txt":
                        result = subprocess.run([cmd, str(path)], 
                                              check=False, 
                                              capture_output=True,
                                              timeout=5)
                        if result.returncode == 0:
                            success = True
                
                if success:
                    return True
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue
            except Exception:
                continue
        
        # Se nenhum método funcionou, usar subprocess.Popen como última tentativa
        if not success:
            try:
                import os
                for path in paths:
                    if path.name != "README_PREVIEW.txt":
                        # Usar o sistema operacional para abrir o ficheiro
                        os.startfile(str(path))
                return True
            except Exception as e:
                print(f"{Colors.YELLOW} Não foi possível abrir em VS Code automaticamente.{Colors.END}")
                print(f"{Colors.CYAN} Abra manualmente: {Colors.BOLD}{self.temp_dir}{Colors.END}")
                return False
        
        return False
    
    def print_preview_summary(self, content: Dict[str, str], title: str):
        """Imprime um resumo do conteúdo a ser criado."""
        try:
            print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
            print(f"{Colors.BOLD}{Colors.CYAN}   PREVIEW: {title}{Colors.END}")
            print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}\n")
        except UnicodeEncodeError:
            # Fallback sem emojis para terminais que não suportam
            print(f"\n{'='*70}")
            print(f"  PREVIEW: {title}")
            print(f"{'='*70}\n")

        
        for filename, file_content in content.items():
            try:
                print(f"{Colors.YELLOW} {filename}{Colors.END}")
            except UnicodeEncodeError:
                print(f"FILENAME: {filename}")
            
            # Mostrar preview do conteúdo
            lines = file_content.split('\n') if isinstance(file_content, str) else str(file_content).split('\n')
            preview_lines = lines[:20]  # Primeiras 20 linhas
            
            try:
                print(f"{Colors.BLUE}{''*66}{Colors.END}")
                for line in preview_lines:
                    # Truncar linhas muito longas
                    display_line = line[:64] if len(line) > 64 else line
                    print(f"{Colors.BLUE}{Colors.END} {display_line:<64} {Colors.BLUE}{Colors.END}")
                
                if len(lines) > 20:
                    print(f"{Colors.BLUE}{Colors.END} {f'... ({len(lines) - 20} linhas omitidas) ...':<64} {Colors.BLUE}{Colors.END}")
                
                print(f"{Colors.BLUE}{''*66}{Colors.END}\n")
            except UnicodeEncodeError:
                # Fallback simple
                for line in preview_lines:
                    print(line[:200])
                if len(lines) > 20:
                    print(f"... ({len(lines) - 20} linhas omitidas) ...")
                print('\n')

    
    def confirm_action(self, message: str = "Confirmar criação?") -> bool:
        """
        Solicita confirmação do utilizador.
        
        Args:
            message: Mensagem de confirmação
            
        Returns:
            True se confirmado
        """
        try:
            safe_print(f"\n{Colors.BOLD}{Colors.CYAN}{'-'*70}{Colors.END}")
            safe_print(f"{Colors.BOLD}{Colors.YELLOW}!! {message}{Colors.END}")
            safe_print(f"{Colors.CYAN}{'-'*70}{Colors.END}\n")
        except Exception:
            safe_print(f"\n{'-'*70}")
            safe_print(f"{message}")
            safe_print(f"{'-'*70}\n")
        
        while True:
            try:
                response = input(f"[S]im / [N]ão / [R]ever ficheiros novamente: ").strip().lower()
            except Exception:
                # If input fails (non-interactive), default to 's' for automated runs
                return True

            
            if response in ['s', 'sim', 'y', 'yes']:
                return True
            elif response in ['n', 'nao', 'não', 'no']:
                print(f"\n{Colors.RED} Operação cancelada pelo utilizador{Colors.END}")
                return False
            elif response in ['r', 'review', 'rever']:
                if self.temp_dir and self.temp_files:
                    print(f"\n{Colors.BLUE} A reabrir ficheiros...{Colors.END}")
                    self.open_in_vscode(self.temp_files)
                    print(f"{Colors.BLUE} Ficheiros abertos em VS Code{Colors.END}\n")
                else:
                    print(f"{Colors.YELLOW} Nenhum ficheiro disponível para rever{Colors.END}\n")
            else:
                print(f"{Colors.RED}Opção inválida! Digite S, N ou R{Colors.END}")
    
    def show_and_confirm(self, 
                        content: Dict[str, str], 
                        title: str = "Conteúdo Novo",
                        show_preview: bool = True) -> bool:
        """
        Mostra preview e solicita confirmação (método principal).
        
        Args:
            content: Dicionário {filename: content}
            title: Título do preview
            show_preview: Se False, apenas confirma sem mostrar preview
            
        Returns:
            True se confirmado
        """
        if not show_preview:
            return self.confirm_action("Prosseguir sem preview?")
        
        # Criar preview em terminal
        self.print_preview_summary(content, title)
        
        # Criar ficheiros temporários
        temp_dir = self.create_temp_preview(content, title)
        logger_msg = f"[preview_system] temp_dir={temp_dir} auto_open={self.auto_open} consolidated={self.consolidated_preview}"
        try:
            # Use safe_print to avoid Unicode problems on some consoles
            safe_print(f"{Colors.CYAN} Ficheiros temporários criados em:{Colors.END}")
            safe_print(f"{Colors.BLUE}   {temp_dir}{Colors.END}\n")
        except Exception:
            pass
        # Log detalhado para ficheiros criados
        try:
            files_list = ','.join(p.name for p in self.temp_files)
            safe_print(f"[preview_system] arquivos: {files_list}")
        except Exception:
            pass

        
        # Destacar ficheiro consolidado
        if self.consolidated_preview:
            consolidated_file = next((f for f in self.temp_files if "PREVIEW_CONSOLIDADO" in f.name), None)
            if consolidated_file:
                try:
                    safe_print(f"{Colors.GREEN}Ficheiro principal para revisão:{Colors.END}")
                    safe_print(f"{Colors.BOLD}   → {consolidated_file.name}{Colors.END}")
                    safe_print(f"{Colors.CYAN}   (Todo o conteúdo num único ficheiro estruturado){Colors.END}\n")
                except UnicodeEncodeError:
                    safe_print(f"Ficheiro principal para revisão: {consolidated_file.name}\n")

        
        # Abrir em VS Code se configurado
        if self.auto_open:
            safe_print(f"{Colors.CYAN} A abrir ficheiro(s) em VS Code...{Colors.END}")
            if self.consolidated_preview:

                # Quando há preview consolidado, abrir apenas o ficheiro consolidado
                consolidated_file = next((f for f in self.temp_files if "PREVIEW_CONSOLIDADO" in f.name), None)
                if consolidated_file:
                    success = self.open_in_vscode([consolidated_file])
                else:
                    success = self.open_in_vscode(self.temp_files)
            else:
                success = self.open_in_vscode(self.temp_files)
            if success:
                safe_print(f"{Colors.GREEN} Ficheiro(s) aberto(s) para revisão{Colors.END}\n")
                try:
                    safe_print(f"[preview_system] open_in_vscode succeeded for files: {self.temp_files}")
                except Exception:
                    pass
        else:
            safe_print(f"{Colors.YELLOW}ℹ Abra manualmente: {temp_dir}{Colors.END}\n")
            try:
                safe_print(f"[preview_system] open_in_vscode failed or not attempted; auto_open={self.auto_open}")
            except Exception:
                pass


        
        # Solicitar confirmação
        confirmed = self.confirm_action("Confirmar e adicionar à base de dados?")
        
        # Limpar ficheiros temporários se confirmado
        if confirmed:
            self.cleanup()
            safe_print(f"{Colors.GREEN} Preview confirmado - a prosseguir...{Colors.END}\n")
        else:
            safe_print(f"{Colors.YELLOW}ℹ Ficheiros temporários mantidos para revisão: {temp_dir}{Colors.END}\n")

        
        return confirmed
    
    def cleanup(self):
        """Remove ficheiros temporários."""
        if self.temp_dir and self.temp_dir.exists():
            try:
                import shutil
                shutil.rmtree(self.temp_dir)
                self.temp_files = []
                self.temp_dir = None
            except Exception as e:
                print(f"{Colors.YELLOW} Não foi possível remover ficheiros temporários: {e}{Colors.END}")


def create_exercise_preview(exercise_id: str, 
                           latex_content: str,
                           metadata: Dict,
                           tipo_metadata: Optional[Dict] = None) -> Dict[str, str]:
    """
    Helper para criar preview de exercício.
    
    Args:
        exercise_id: ID do exercício
        latex_content: Conteúdo LaTeX
        metadata: Metadados do exercício
        tipo_metadata: Metadados do tipo (opcional)
        
    Returns:
        Dicionário {filename: content} para preview
    """
    preview_content = {
        f"{exercise_id}.tex": latex_content,
        f"{exercise_id}_metadata.json": json.dumps(metadata, indent=2, ensure_ascii=False)
    }
    
    if tipo_metadata:
        preview_content["tipo_metadata_updated.json"] = json.dumps(tipo_metadata, indent=2, ensure_ascii=False)
    
    return preview_content


def create_sebenta_preview(sebenta_name: str,
                           latex_content: str,
                           metadata: Optional[Dict] = None) -> Dict[str, str]:
    """
    Helper para criar preview de sebenta.
    
    Args:
        sebenta_name: Nome da sebenta
        latex_content: Conteúdo LaTeX
        metadata: Metadados adicionais (opcional)
        
    Returns:
        Dicionário {filename: content} para preview
    """
    preview_content = {
        f"preview_{sebenta_name}.tex": latex_content
    }
    
    if metadata:
        preview_content[f"{sebenta_name}_info.json"] = json.dumps(metadata, indent=2, ensure_ascii=False)
    
    return preview_content


def create_test_preview(test_name: str,
                       latex_content: str,
                       selected_exercises: List[Dict],
                       config: Dict) -> Dict[str, str]:
    """
    Helper para criar preview de teste.
    
    Args:
        test_name: Nome do teste
        latex_content: Conteúdo LaTeX
        selected_exercises: Lista de exercícios selecionados
        config: Configuração usada
        
    Returns:
        Dicionário {filename: content} para preview
    """
    # Criar resumo dos exercícios selecionados
    exercises_summary = {
        "total_exercises": len(selected_exercises),
        "exercises": [
            {
                "id": ex.get('id'),
                "concept": ex.get('concept_name'),
                "tipo": ex.get('tipo_nome'),
                "difficulty": ex.get('difficulty')
            }
            for ex in selected_exercises
        ],
        "config_used": config
    }
    
    preview_content = {
        f"{test_name}.tex": latex_content,
        f"{test_name}_exercises.json": json.dumps(exercises_summary, indent=2, ensure_ascii=False)
    }
    
    return preview_content


# Exemplo de uso
if __name__ == "__main__":
    # Teste do sistema
    preview = PreviewManager(auto_open=True)
    
    test_content = {
        "exercicio_001.tex": "\\exercicio{Calcule $2+2$}",
        "metadata.json": json.dumps({
            "id": "TEST_001",
            "difficulty": 1,
            "tags": ["teste", "matematica"]
        }, indent=2)
    }
    
    if preview.show_and_confirm(test_content, "Teste do Sistema de Preview"):
        print(" Confirmado! Procederia com a criação...")
    else:
        print(" Cancelado!")
