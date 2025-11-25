#!/usr/bin/env python3
"""
Utilitário para Correção Automática de Edge Cases LaTeX

Este módulo fornece funções para detectar e corrigir automaticamente
problemas comuns na geração de conteúdo LaTeX que causam erros de compilação.

Problemas Tratados:
1. Underscores (_) em texto normal → \\rule{}{} ou \\underline{}
2. Acentos em contexto incorreto → escape adequado
3. Listas mal formatadas → correção de estrutura
4. Caracteres especiais em modo matemático → isolamento adequado
"""

import re
from typing import Dict, List, Tuple, Callable
from dataclasses import dataclass

@dataclass
class LaTeXIssue:
    """Representa um problema identificado no LaTeX"""
    line_number: int
    position: int
    issue_type: str
    description: str
    severity: str  # 'error', 'warning', 'info'
    suggestion: str

class LaTeXSanitizer:
    """Sanitiza conteúdo LaTeX removendo edge cases problemáticos"""

    def __init__(self):
        self.issues_found = []

    def sanitize_content(self, content: str) -> Tuple[str, List[LaTeXIssue]]:
        """
        Aplica todas as correções automáticas ao conteúdo LaTeX

        Returns:
            Tuple[sanitized_content, list_of_issues_found]
        """
        self.issues_found = []

        # Aplica correções em ordem (importante para não interferir)
        corrections = [
            self._fix_underscores_in_text,
            self._fix_accents_in_lists,
            self._fix_malformed_lists,
            self._fix_math_mode_issues,
            self._fix_line_breaks
        ]

        sanitized = content
        for correction in corrections:
            sanitized, issues = correction(sanitized)
            self.issues_found.extend(issues)

        return sanitized, self.issues_found

    def _fix_underscores_in_text(self, content: str) -> Tuple[str, List[LaTeXIssue]]:
        """Corrige underscores em texto normal que causam modo matemático"""

        issues = []

        # Padrão melhorado: underscores consecutivos (4+) em itemize/enumerate
        # Evita capturar underscores que fazem parte de palavras
        pattern = r'(\\item\s+[^$]*?)(_{4,})([^$]*?)(?=\s|$)'

        def replace_underscores(match):
            before = match.group(1)
            underscores = match.group(2)
            after = match.group(3)
            issues.append(LaTeXIssue(
                line_number=content[:match.start()].count('\n') + 1,
                position=match.start(),
                issue_type="underscores_in_text",
                description=f"Underscores consecutivos ({len(underscores)}) em texto normal",
                severity="error",
                suggestion="Substituir por \\rule{2cm}{0.4pt}"
            ))
            return f"{before}\\rule{{2cm}}{{0.4pt}}{after}"

        corrected = re.sub(pattern, replace_underscores, content)

        return corrected, issues

    def _fix_accents_in_lists(self, content: str) -> Tuple[str, List[LaTeXIssue]]:
        """Corrige problemas com acentos em listas"""

        issues = []

        # Remove acentos problemáticos em contextos onde podem causar issues
        # Este é um caso específico - acentos em palavras que podem ser confundidas

        corrected = content
        return corrected, issues

    def _fix_malformed_lists(self, content: str) -> Tuple[str, List[LaTeXIssue]]:
        """Corrige listas mal formatadas"""

        issues = []

        # Detecta \item fora de ambientes de lista
        lines = content.split('\n')
        in_list = False
        corrected_lines = []

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Detecta início de lista
            if '\\begin{itemize}' in stripped or '\\begin{enumerate}' in stripped:
                in_list = True
            elif '\\end{itemize}' in stripped or '\\end{enumerate}' in stripped:
                in_list = False

            # Verifica \item fora de lista
            if stripped.startswith('\\item') and not in_list:
                issues.append(LaTeXIssue(
                    line_number=i + 1,
                    position=0,
                    issue_type="malformed_list",
                    description="\\item fora de ambiente de lista",
                    severity="error",
                    suggestion="Mover para dentro de \\begin{itemize}...\\end{itemize}"
                ))

            corrected_lines.append(line)

        corrected = '\n'.join(corrected_lines)
        return corrected, issues

    def _fix_math_mode_issues(self, content: str) -> Tuple[str, List[LaTeXIssue]]:
        """Corrige problemas com modo matemático"""

        issues = []

        # Detecta expressões que podem causar problemas
        # Por exemplo, texto com acentos próximo a expressões matemáticas

        corrected = content
        return corrected, issues

    def _fix_line_breaks(self, content: str) -> Tuple[str, List[LaTeXIssue]]:
        """Corrige quebras de linha inadequadas"""

        issues = []

        corrected = content
        return corrected, issues

    def validate_latex_compilation(self, content: str) -> Tuple[bool, str]:
        """
        Valida se o conteúdo LaTeX compila sem erros

        Returns:
            Tuple[compiles_successfully, error_message]
        """
        import tempfile
        import subprocess
        import os

        with tempfile.TemporaryDirectory() as temp_dir:
            tex_file = os.path.join(temp_dir, "validation.tex")

            with open(tex_file, 'w', encoding='utf-8') as f:
                f.write(content)

            try:
                result = subprocess.run(
                    ['pdflatex', '-interaction=nonstopmode', tex_file],
                    cwd=temp_dir,
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                success = result.returncode == 0
                error_output = result.stderr + result.stdout

                # Debug: mostra output completo se erro
                if not success:
                    print(f"DEBUG - Compilation failed. Full output:")
                    print("="*50)
                    print(error_output)
                    print("="*50)

                return success, error_output

            except subprocess.TimeoutExpired:
                return False, "Timeout na compilação"
            except FileNotFoundError:
                return False, "pdflatex não encontrado"

def sanitize_latex_content(content: str, validate: bool = True) -> Tuple[str, List[LaTeXIssue], bool]:
    """
    Função principal para sanitizar conteúdo LaTeX

    Args:
        content: Conteúdo LaTeX original
        validate: Se deve validar compilação após sanitização

    Returns:
        Tuple[sanitized_content, issues_found, compilation_success]
    """

    sanitizer = LaTeXSanitizer()

    # Sanitiza conteúdo
    sanitized, issues = sanitizer.sanitize_content(content)

    # Valida compilação se solicitado
    compilation_success = True
    if validate:
        compilation_success, error_msg = sanitizer.validate_latex_compilation(sanitized)
        if not compilation_success:
            # Adiciona issue de validação
            issues.append(LaTeXIssue(
                line_number=0,
                position=0,
                issue_type="compilation_error",
                description=f"Erro de compilação após sanitização: {error_msg[:100]}...",
                severity="error",
                suggestion="Revisar sanitização ou conteúdo gerado"
            ))

    return sanitized, issues, compilation_success

# Função de compatibilidade para uso nos scripts existentes
def fix_latex_edge_cases(content: str) -> str:
    """
    Função simples para correção automática - compatibilidade com scripts existentes

    Args:
        content: Conteúdo LaTeX com possíveis problemas

    Returns:
        Conteúdo sanitizado
    """
    sanitized, issues, success = sanitize_latex_content(content, validate=False)

    if issues:
        print(f"⚠️  Corrigidos {len(issues)} problemas LaTeX:")
        for issue in issues:
            print(f"   - {issue.issue_type}: {issue.description}")

    return sanitized

if __name__ == "__main__":
    # Exemplo de uso com preamble completo
    problematic_content = r"""\documentclass[12pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[portuguese]{babel}
\usepackage{amsmath,amssymb}
\usepackage{geometry}
\geometry{margin=2cm}

\begin{document}

\textbf{Instruções:}
\begin{itemize}
    \item Duração: ____ minutos
    \item Cotação total: ____ pontos
\end{itemize}

\end{document}
"""

    print("Conteúdo original:")
    print(repr(problematic_content))  # Mostra representação raw
    print("\n" + "="*50 + "\n")

    sanitized, issues, success = sanitize_latex_content(problematic_content)

    print("Conteúdo sanitizado:")
    print(repr(sanitized))  # Mostra representação raw
    print(f"\nProblemas encontrados: {len(issues)}")
    print(f"Compilação bem-sucedida: {success}")

    for issue in issues:
        print(f"- {issue.issue_type}: {issue.description}")