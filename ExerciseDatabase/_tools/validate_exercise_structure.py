#!/usr/bin/env python3
"""
Script de teste de robustez para parsing de exercícios.
Valida estrutura LaTeX e metadados de ficheiros .tex existentes.
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple


class ExerciseValidator:
    """Validador de estrutura de exercícios."""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.content = ""
        self.errors = []
        self.warnings = []
        self.metadata = {}
        
    def load_file(self) -> bool:
        """Carrega o ficheiro."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.content = f.read()
            return True
        except Exception as e:
            self.errors.append(f"Erro ao ler ficheiro: {e}")
            return False
    
    def validate_metadata(self) -> bool:
        """Valida os metadados no cabeçalho."""
        
        # Campo obrigatório: Exercise ID
        id_match = re.search(r'% Exercise ID:\s*(.+)', self.content)
        if not id_match:
            self.errors.append("Campo obrigatório 'Exercise ID' em falta")
        else:
            value = id_match.group(1).strip()
            if not value or value.startswith('%'):
                self.errors.append("Campo 'Exercise ID' está vazio")
            else:
                self.metadata['Exercise ID'] = value
        
        # Campos Module/Concept podem estar combinados ou separados
        module_match = re.search(r'% Module:\s*(.+?)(?:\||$)', self.content)
        if module_match:
            value = module_match.group(1).strip()
            if value and not value.startswith('%'):
                self.metadata['Module'] = value
        
        concept_match = re.search(r'(?:% Module:.*?\|\s*Concept:\s*(.+)|% Concept:\s*(.+))', self.content)
        if concept_match:
            value = (concept_match.group(1) or concept_match.group(2)).strip()
            if value and not value.startswith('%'):
                self.metadata['Concept'] = value
        
        if 'Module' not in self.metadata:
            self.errors.append("Campo obrigatório 'Module' em falta ou vazio")
        if 'Concept' not in self.metadata:
            self.errors.append("Campo obrigatório 'Concept' em falta ou vazio")
        
        # Campo Type/Difficulty podem estar combinados
        type_match = re.search(r'% Type:\s*(\w+)', self.content)
        if type_match:
            self.metadata['Type'] = type_match.group(1).strip()
        else:
            self.errors.append("Campo obrigatório 'Type' em falta")
        
        difficulty_match = re.search(r'Difficulty:\s*(\d+)', self.content)
        if difficulty_match:
            self.metadata['Difficulty'] = difficulty_match.group(1).strip()
        else:
            self.errors.append("Campo obrigatório 'Difficulty' em falta")
        
        # Tags
        tags_match = re.search(r'% Tags:\s*(.+)', self.content)
        if tags_match:
            self.metadata['Tags'] = tags_match.group(1).strip()
        else:
            self.warnings.append("Campo 'Tags' não encontrado")
        
        # Author
        author_match = re.search(r'% Author:\s*(.+?)(?:\||$)', self.content)
        if author_match:
            self.metadata['Author'] = author_match.group(1).strip()
        else:
            self.warnings.append("Campo 'Author' não encontrado")
        
        # Date
        date_match = re.search(r'Date:\s*(.+)', self.content)
        if date_match:
            self.metadata['Date'] = date_match.group(1).strip()
        else:
            self.warnings.append("Campo 'Date' não encontrado")
        
        return len(self.errors) == 0
    
    def validate_latex_structure(self) -> bool:
        """Valida a estrutura LaTeX do exercício."""
        
        # 1. Verificar \exercicio{...}
        exercicio_pattern = r'\\exercicio\{(.*?)\}(?=\s*(?:\\sub|%|$))'
        exercicio_match = re.search(exercicio_pattern, self.content, re.DOTALL)
        
        if not exercicio_match:
            self.errors.append("Comando \\exercicio{...} não encontrado ou mal formado")
            return False
        
        enunciado = exercicio_match.group(1)
        
        # 2. Verificar balanceamento de chavetas no enunciado
        if not self._check_balanced_braces(enunciado):
            self.errors.append("Chavetas não balanceadas no enunciado")
        
        # 3. Verificar ambientes LaTeX fechados
        environments = re.findall(r'\\begin\{([^}]+)\}', enunciado)
        for env in environments:
            if f'\\end{{{env}}}' not in enunciado:
                self.errors.append(f"Ambiente '\\begin{{{env}}}' não fechado com '\\end{{{env}}}'")
        
        # 4. Verificar \subexercicio fora do \exercicio{}
        after_exercicio = self.content[exercicio_match.end():]
        subexercicios = re.findall(r'\\subexercicio\{([^}]+)\}', after_exercicio)
        
        if subexercicios:
            print(f"  ✓ {len(subexercicios)} alínea(s) encontrada(s)")
        
        # 5. Avisar se há \subexercicio dentro do \exercicio{}
        if '\\subexercicio' in enunciado:
            self.warnings.append("\\subexercicio{} encontrado DENTRO de \\exercicio{} - deveria estar FORA!")
        
        return len(self.errors) == 0
    
    def _check_balanced_braces(self, text: str) -> bool:
        """Verifica se chavetas estão balanceadas."""
        count = 0
        for char in text:
            if char == '{':
                count += 1
            elif char == '}':
                count -= 1
            if count < 0:
                return False
        return count == 0
    
    def validate_syntax_details(self) -> bool:
        """Valida detalhes de sintaxe LaTeX."""
        
        # 1. Verificar tabular mal fechado
        tabular_begin = re.findall(r'\\begin\{tabular\}', self.content)
        tabular_end = re.findall(r'\\end\{tabular\}', self.content)
        
        if len(tabular_begin) != len(tabular_end):
            self.errors.append(f"Ambientes tabular desbalanceados: {len(tabular_begin)} \\begin vs {len(tabular_end)} \\end")
        
        # 2. Verificar enumerate/itemize mal fechados
        for env in ['enumerate', 'itemize']:
            begin_count = len(re.findall(rf'\\begin\{{{env}\}}', self.content))
            end_count = len(re.findall(rf'\\end\{{{env}\}}', self.content))
            
            if begin_count != end_count:
                self.errors.append(f"Ambiente {env} desbalanceado: {begin_count} \\begin vs {end_count} \\end")
        
        # 3. Verificar $ matemático balanceado
        math_singles = re.findall(r'(?<!\\)\$', self.content)
        if len(math_singles) % 2 != 0:
            self.warnings.append(f"Símbolos $ desbalanceados (encontrados {len(math_singles)}, deveria ser par)")
        
        return len(self.errors) == 0
    
    def check_template_garbage(self) -> bool:
        """Verifica se há lixo do template não removido."""
        garbage_patterns = [
            r'Primeira alínea',
            r'Segunda alínea',
            r'← ESCREVA APENAS',
            r'↳ Exemplos:',
            r'% Exemplo:',
        ]
        
        for pattern in garbage_patterns:
            if re.search(pattern, self.content):
                self.warnings.append(f"Possível lixo do template encontrado: '{pattern}'")
        
        return True
    
    def run_full_validation(self) -> Tuple[bool, Dict]:
        """Executa validação completa."""
        print(f"\n{'='*70}")
        print(f"VALIDANDO: {self.file_path.name}")
        print(f"{'='*70}\n")
        
        if not self.load_file():
            return False, {'errors': self.errors}
        
        # Executar todas as validações
        self.validate_metadata()
        self.validate_latex_structure()
        self.validate_syntax_details()
        self.check_template_garbage()
        
        # Resultados
        print(f"📋 Metadados:")
        for key, value in self.metadata.items():
            print(f"  • {key}: {value}")
        
        print(f"\n🔍 Validação:")
        
        if self.errors:
            print(f"\n❌ ERROS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")
        else:
            print(f"  ✅ Nenhum erro encontrado")
        
        if self.warnings:
            print(f"\n⚠️  AVISOS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        success = len(self.errors) == 0
        
        print(f"\n{'='*70}")
        if success:
            print(f"✅ VALIDAÇÃO BEM-SUCEDIDA!")
        else:
            print(f"❌ VALIDAÇÃO FALHOU!")
        print(f"{'='*70}\n")
        
        return success, {
            'metadata': self.metadata,
            'errors': self.errors,
            'warnings': self.warnings
        }


def test_exercise_robustness():
    """Testa a robustez do parsing de exercícios."""
    
    # Ficheiro teste
    test_file = Path("ExerciseDatabase/matematica/P2_estatistica/0-revisoes/desenvolvimento/MAT_P2ESTATI_REVI_D_999.tex")
    
    if not test_file.exists():
        print(f"❌ Ficheiro teste não encontrado: {test_file}")
        return False
    
    validator = ExerciseValidator(test_file)
    success, results = validator.run_full_validation()
    
    return success


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Validar ficheiro específico
        test_file = Path(sys.argv[1])
        validator = ExerciseValidator(test_file)
        success, _ = validator.run_full_validation()
        sys.exit(0 if success else 1)
    else:
        # Teste padrão
        success = test_exercise_robustness()
        sys.exit(0 if success else 1)
