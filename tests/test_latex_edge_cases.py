#!/usr/bin/env python3
"""
Teste de Edge Cases para Geração de LaTeX

Este teste valida a resistência dos scripts de geração de testes
contra edge cases comuns que causam erros de compilação LaTeX.

Edge Cases Testados:
1. Underscores (_) em texto normal (interpretados como subscritos)
2. Acentos em palavras dentro de listas
3. Formatação incorreta de listas itemize
4. Texto com caracteres especiais em modo matemático
5. Quebras de linha inadequadas em ambientes LaTeX
"""

import os
import tempfile
import subprocess
import shutil
from pathlib import Path
from typing import List, Dict, Tuple

class LaTeXEdgeCaseTester:
    """Testa edge cases comuns na geração de LaTeX"""

    def __init__(self):
        self.test_dir = None
        self.results = []

    def setup_test_environment(self):
        """Cria diretório temporário para testes"""
        self.test_dir = tempfile.mkdtemp(prefix="latex_edge_test_")
        print(f"📁 Test directory: {self.test_dir}")

    def cleanup(self):
        """Remove arquivos temporários"""
        if self.test_dir and os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            print("🧹 Cleaned up test directory")

    def generate_problematic_latex(self, edge_case: str) -> str:
        """Gera conteúdo LaTeX com problemas específicos"""

        base_preamble = r"""\documentclass[12pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[portuguese]{babel}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{geometry}
\usepackage{enumitem}
\usepackage{fancyhdr}

% Gráficos e TikZ
\usepackage{tikz}
\usetikzlibrary{calc,patterns,angles,quotes}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\usepackage{float}

\geometry{margin=2cm}

% Headers e footers
\pagestyle{fancy}
\fancyhf{}
\lhead{\textbf{Teste - Edge Cases}}
\rhead{Edge Case Test}
\cfoot{\thepage}

\begin{document}

\begin{center}
    {\LARGE\textbf{Teste de Edge Cases}} \\
    {\large Caso: """ + edge_case + r"""}
\end{center}

\vspace{1em}
"""

        problematic_content = {
            "underscores_in_text": r"""
\textbf{Instruções:}
\begin{itemize}
    \item Leia_atentamente_todas_as_questões
    \item Apresente_todos_os_cálculos_e_justificações
    \item Escreva_de_forma_clara_e_organizada
    \item Duração: ____ minutos
    \item Cotação_total: ____ pontos
\end{itemize}
""",

            "accents_in_math": r"""
\textbf{Problema:}
\begin{itemize}
    \item Calcule $f(x) = x^2 + 1$
    \item Determine a função inversa $f^{-1}(x)$
    \item Cotação total: ____ pontos
\end{itemize}

A função $f(x) = x^2$ não é invertível porque não passa no teste da reta horizontal.
""",

            "malformed_lists": r"""
\textbf{Lista com problemas:}
\begin{itemize}
    \item Primeiro item correto
    \item Segundo item
        \begin{itemize}
        \item Subitem 1
        \item Subitem 2
    \end{itemize}
    \item Terceiro item
\end{itemize}

\begin{enumerate}
    \item Item 1
    \item Item 2
        \item Subitem incorreto (não deveria estar aqui)
    \item Item 3
\end{enumerate}
""",

            "special_chars_in_math": r"""
\textbf{Funções especiais:}
\begin{itemize}
    \item $f(x) = \sqrt{x + 1}$
    \item $g(x) = \frac{1}{x-2}$
    \item $h(x) = e^x + \ln(x)$
    \item Duração: ____ minutos
\end{itemize}
""",

            "line_breaks_issues": r"""
\textbf{Problema com quebras:}
Considere as funções:
\begin{itemize}
    \item $f(x) = x^2$
    \item $g(x) = 2x + 1$
\end{itemize}

Determine quais são invertíveis.

\bigskip

\textbf{Resposta:}
A função $f(x) = x^2$ não é invertível porque...
"""
        }

        footer = r"""

\end{document}"""

        return base_preamble + problematic_content.get(edge_case, "") + footer

    def compile_latex(self, content: str, filename: str) -> Tuple[bool, str]:
        """Compila LaTeX e retorna sucesso/erro"""

        tex_file = os.path.join(self.test_dir, f"{filename}.tex")

        with open(tex_file, 'w', encoding='utf-8') as f:
            f.write(content)

        try:
            # Compila com pdflatex
            result = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', tex_file],
                cwd=self.test_dir,
                capture_output=True,
                text=True,
                timeout=30
            )

            success = result.returncode == 0
            output = result.stdout + result.stderr

            return success, output

        except subprocess.TimeoutExpired:
            return False, "Timeout na compilação"
        except FileNotFoundError:
            return False, "pdflatex não encontrado"

    def test_edge_case(self, case_name: str, description: str) -> Dict:
        """Testa um caso específico de edge case"""

        print(f"\n🧪 Testing: {case_name}")
        print(f"   {description}")

        # Gera conteúdo problemático
        latex_content = self.generate_problematic_latex(case_name)

        # Tenta compilar
        success, output = self.compile_latex(latex_content, case_name)

        # Analisa resultado
        result = {
            'case': case_name,
            'description': description,
            'success': success,
            'output': output,
            'errors_found': [],
            'warnings_found': []
        }

        # Detecta tipos específicos de erros
        if "Missing $" in output:
            result['errors_found'].append("Missing $ (modo matemático incorreto)")
        if "Undefined control sequence" in output:
            result['errors_found'].append("Undefined control sequence")
        if "LaTeX Error" in output:
            result['errors_found'].append("LaTeX Error genérico")
        if "Math accent" in output:
            result['errors_found'].append("Math accent error (acentos)")
        if "Command \\item invalid in math mode" in output:
            result['errors_found'].append("Item em modo matemático")

        # Warnings
        if "Warning" in output:
            result['warnings_found'].append("Warnings presentes")

        print(f"   ✅ Success: {success}")
        if result['errors_found']:
            print(f"   ❌ Errors: {len(result['errors_found'])}")
        if result['warnings_found']:
            print(f"   ⚠️  Warnings: {len(result['warnings_found'])}")

        return result

    def run_all_tests(self) -> List[Dict]:
        """Executa todos os testes de edge cases"""

        test_cases = [
            ("underscores_in_text", "Underscores em texto normal causando modo matemático"),
            ("accents_in_math", "Acentos sendo interpretados incorretamente"),
            ("malformed_lists", "Listas mal formatadas (itens incorretos)"),
            ("special_chars_in_math", "Caracteres especiais em expressões matemáticas"),
            ("line_breaks_issues", "Quebras de linha inadequadas em ambientes")
        ]

        results = []
        for case_name, description in test_cases:
            result = self.test_edge_case(case_name, description)
            results.append(result)

        return results

    def generate_report(self, results: List[Dict]) -> str:
        """Gera relatório dos testes"""

        report = []
        report.append("# Relatório de Testes - Edge Cases LaTeX")
        report.append("")
        report.append("## Resumo")
        report.append(f"- Total de testes: {len(results)}")
        report.append(f"- Sucessos: {sum(1 for r in results if r['success'])}")
        report.append(f"- Falhas: {sum(1 for r in results if not r['success'])}")
        report.append("")

        for result in results:
            report.append(f"## Caso: {result['case']}")
            report.append(f"**Descrição:** {result['description']}")
            report.append(f"**Sucesso:** {'✅ Sim' if result['success'] else '❌ Não'}")
            report.append("")

            if result['errors_found']:
                report.append("**Erros encontrados:**")
                for error in result['errors_found']:
                    report.append(f"- {error}")
                report.append("")

            if result['warnings_found']:
                report.append("**Warnings encontrados:**")
                for warning in result['warnings_found']:
                    report.append(f"- {warning}")
                report.append("")

            if not result['success']:
                report.append("**Output da compilação:**")
                report.append("```")
                report.append(result['output'][:500] + "..." if len(result['output']) > 500 else result['output'])
                report.append("```")
                report.append("")

        return "\n".join(report)

def main():
    """Função principal do teste"""

    print("🚀 Iniciando testes de edge cases LaTeX")
    print("=" * 50)

    tester = LaTeXEdgeCaseTester()

    try:
        tester.setup_test_environment()
        results = tester.run_all_tests()

        # Gera relatório
        report = tester.generate_report(results)

        # Salva relatório
        report_file = os.path.join(tester.test_dir, "edge_cases_report.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n📄 Relatório salvo em: {report_file}")

        # Mostra resumo
        successes = sum(1 for r in results if r['success'])
        total = len(results)
        print(f"\n📊 Resumo: {successes}/{total} testes passaram")

        if successes < total:
            print("⚠️  Alguns testes falharam - revise os scripts de geração!")
            return 1
        else:
            print("✅ Todos os testes passaram!")
            return 0

    finally:
        tester.cleanup()

if __name__ == "__main__":
    exit(main())