#!/usr/bin/env python3
"""
Tests for generate_test_template.py handling of exercises with sub-variants.

This module tests that the Test Generator correctly processes exercises that:
1. Have sub-variants (main.tex + subvariant_*.tex in a folder)
2. Are normal .tex files
3. Are mixed (combination of both types)

Run with:
    python -m pytest tests/test_generate_test_template_subvariants.py -v
    
Or directly:
    python tests/test_generate_test_template_subvariants.py
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
TESTS_DIR = Path(__file__).parent
PROJECT_ROOT = TESTS_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT / "SebentasDatabase" / "_tools"))
sys.path.insert(0, str(PROJECT_ROOT / "ExerciseDatabase" / "_tools"))

from generate_test_template import TestTemplate


class TestSubvariantHandling:
    """Test cases for sub-variant exercise handling in TestTemplate."""
    
    @classmethod
    def setup_class(cls):
        """Set up test fixtures."""
        cls.project_root = PROJECT_ROOT
        cls.exercise_db = cls.project_root / "ExerciseDatabase"
        
    def test_normal_exercise_loading(self):
        """Test that normal .tex exercises are loaded correctly."""
        generator = TestTemplate()
        
        # Use a known normal exercise
        exercise = {
            'id': 'MAT_P4FUNCOE_1GEN_001',
            'path': 'matematica/P4_funcoes/1-generalidades_funcoes/MAT_P4FUNCOE_1GEN_001.tex',
            'concept_name': 'Generalidades acerca de Funções',
            'type': 'desenvolvimento'
        }
        
        # Generate LaTeX for this exercise
        latex = generator.generate_test_latex(
            'matematica',
            'MÓDULO P4 - Funções',
            'Generalidades',
            [exercise]
        )
        
        # Verify that the exercise content is included (not an error message)
        assert "[Exercício não encontrado" not in latex, \
            "Normal exercise should be found and loaded correctly"
        
        # Verify exercise is mentioned in the LaTeX
        assert 'MAT_P4FUNCOE_1GEN_001' in latex, \
            "Exercise ID should appear in generated LaTeX"
    
    def test_subvariant_exercise_loading(self):
        """Test that exercises with sub-variants are loaded correctly."""
        generator = TestTemplate()
        
        # Use a known sub-variant exercise - MAT_P4FUNCOE_4FIN_ANA_007
        # This exercise has main.tex + subvariant_*.tex files
        exercise = {
            'id': 'MAT_P4FUNCOE_4FIN_ANA_007',
            'path': 'matematica/P4_funcoes/4-funcao_inversa/determinacao_analitica/MAT_P4FUNCOE_4FIN_ANA_007/main.tex',
            'concept_name': 'Função Inversa',
            'tipo_nome': 'Determinação Analítica',
            'type': 'desenvolvimento'
        }
        
        # Generate LaTeX for this exercise
        latex = generator.generate_test_latex(
            'matematica',
            'MÓDULO P4 - Funções',
            'Função Inversa',
            [exercise]
        )
        
        # Verify that the exercise content is included (not an error message)
        assert "[Exercício não encontrado" not in latex, \
            f"Sub-variant exercise should be found and loaded correctly. Got: {latex[:500]}"
        
        # Verify the main exercise content is present
        assert 'MAT_P4FUNCOE_4FIN_ANA_007' in latex, \
            "Exercise ID should appear in generated LaTeX"
        
        # Verify that sub-variant content is resolved (no raw \input commands)
        # The sub-variants contain function definitions like f(x) = x + 4
        assert '\\input{subvariant' not in latex or 'f(x)' in latex, \
            "Sub-variant content should be resolved inline"
    
    def test_subvariant_folder_exercise_loading(self):
        """Test that folder-based sub-variant exercises (path without main.tex) are loaded."""
        generator = TestTemplate()
        
        # Test with folder path (without main.tex in path)
        exercise = {
            'id': 'MAT_P4FUNCOE_4FIN_ANA_001',
            'path': 'matematica/P4_funcoes/4-funcao_inversa/determinacao_analitica/MAT_P4FUNCOE_4FIN_ANA_001',
            'concept_name': 'Função Inversa',
            'tipo_nome': 'Determinação Analítica',
            'type': 'desenvolvimento'
        }
        
        # Generate LaTeX
        latex = generator.generate_test_latex(
            'matematica',
            'MÓDULO P4 - Funções',
            'Função Inversa',
            [exercise]
        )
        
        # This test currently expects failure (before fix) or success (after fix)
        # After fix: should not have error message
        assert "[Exercício não encontrado" not in latex, \
            f"Folder-based sub-variant exercise should be found. Got: {latex[:500]}"
    
    def test_mixed_exercises_loading(self):
        """Test loading a mix of normal and sub-variant exercises."""
        generator = TestTemplate()
        
        # Mix of normal and sub-variant exercises
        exercises = [
            {
                'id': 'MAT_P4FUNCOE_1GEN_001',
                'path': 'matematica/P4_funcoes/1-generalidades_funcoes/MAT_P4FUNCOE_1GEN_001.tex',
                'concept_name': 'Generalidades',
                'type': 'desenvolvimento'
            },
            {
                'id': 'MAT_P4FUNCOE_4FIN_ANA_007',
                'path': 'matematica/P4_funcoes/4-funcao_inversa/determinacao_analitica/MAT_P4FUNCOE_4FIN_ANA_007/main.tex',
                'concept_name': 'Função Inversa',
                'tipo_nome': 'Determinação Analítica',
                'type': 'desenvolvimento'
            }
        ]
        
        # Generate LaTeX
        latex = generator.generate_test_latex(
            'matematica',
            'MÓDULO P4 - Funções',
            None,
            exercises
        )
        
        # Count error messages
        error_count = latex.count("[Exercício não encontrado")
        
        # Both exercises should be loaded correctly
        assert error_count == 0, \
            f"All exercises should be found. Got {error_count} errors in: {latex[:1000]}"
        
        # Both exercise IDs should appear
        assert 'MAT_P4FUNCOE_1GEN_001' in latex, \
            "First exercise ID should appear"
        assert 'MAT_P4FUNCOE_4FIN_ANA_007' in latex, \
            "Second exercise ID should appear"
    
    def test_multiple_subvariant_exercises(self):
        """Test loading multiple exercises with sub-variants."""
        generator = TestTemplate()
        
        # Multiple sub-variant exercises
        exercises = [
            {
                'id': 'MAT_P4FUNCOE_4FIN_ANA_007',
                'path': 'matematica/P4_funcoes/4-funcao_inversa/determinacao_analitica/MAT_P4FUNCOE_4FIN_ANA_007/main.tex',
                'concept_name': 'Função Inversa',
                'tipo_nome': 'Determinação Analítica',
                'type': 'desenvolvimento'
            },
            {
                'id': 'MAT_P4FUNCOE_4FIN_ANA_001',
                'path': 'matematica/P4_funcoes/4-funcao_inversa/determinacao_analitica/MAT_P4FUNCOE_4FIN_ANA_001',
                'concept_name': 'Função Inversa',
                'tipo_nome': 'Determinação Analítica',
                'type': 'desenvolvimento'
            }
        ]
        
        # Generate LaTeX
        latex = generator.generate_test_latex(
            'matematica',
            'MÓDULO P4 - Funções',
            'Função Inversa',
            exercises
        )
        
        # Count error messages
        error_count = latex.count("[Exercício não encontrado")
        
        # All sub-variant exercises should be loaded correctly
        assert error_count == 0, \
            f"All sub-variant exercises should be found. Got {error_count} errors"
        
        # Both exercise IDs should appear
        assert 'MAT_P4FUNCOE_4FIN_ANA_007' in latex
        assert 'MAT_P4FUNCOE_4FIN_ANA_001' in latex


class TestResolveInputs:
    """Test cases for the resolve_inputs helper method."""
    
    def test_resolve_inputs_basic(self):
        r"""Test basic \input resolution."""
        generator = TestTemplate()
        
        # Create temp directory with test files
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Create main file with \input
            main_content = r"""
\exercicio{
Determina a função inversa:
}

\begin{enumerate}[label=\alph*)]
\item \input{subvariant_1}
\item \input{subvariant_2}
\end{enumerate}
"""
            
            # Create sub-variant files
            (tmpdir / "subvariant_1.tex").write_text("$f(x) = x + 1$", encoding='utf-8')
            (tmpdir / "subvariant_2.tex").write_text("$g(x) = 2x - 3$", encoding='utf-8')
            
            # Resolve inputs
            resolved = generator.resolve_inputs(main_content, tmpdir)
            
            # Verify \input is replaced
            assert "\\input{subvariant_1}" not in resolved
            assert "\\input{subvariant_2}" not in resolved
            
            # Verify content is included
            assert "$f(x) = x + 1$" in resolved
            assert "$g(x) = 2x - 3$" in resolved
    
    def test_resolve_inputs_with_tex_extension(self):
        r"""Test \input resolution when files have .tex extension in the command."""
        generator = TestTemplate()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            main_content = r"\item \input{subvariant_1.tex}"
            
            (tmpdir / "subvariant_1.tex").write_text("Content here", encoding='utf-8')
            
            resolved = generator.resolve_inputs(main_content, tmpdir)
            
            assert "Content here" in resolved
            assert "\\input{subvariant_1.tex}" not in resolved
    
    def test_resolve_inputs_missing_file(self):
        r"""Test \input resolution with missing files."""
        generator = TestTemplate()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            main_content = r"\item \input{missing_file}"
            
            resolved = generator.resolve_inputs(main_content, tmpdir)
            
            # Should have error comment
            assert "ERRO" in resolved or "missing_file" in resolved


def run_tests():
    """Run all tests and report results."""
    import traceback
    
    print("=" * 70)
    print("🧪 TESTES: Test Generator com Sub-Variants")
    print("=" * 70)
    
    test_classes = [TestSubvariantHandling, TestResolveInputs]
    results = {'passed': 0, 'failed': 0, 'errors': []}
    
    for test_class in test_classes:
        print(f"\n📋 {test_class.__name__}")
        print("-" * 50)
        
        instance = test_class()
        if hasattr(test_class, 'setup_class'):
            test_class.setup_class()
        
        for method_name in dir(instance):
            if method_name.startswith('test_'):
                try:
                    print(f"  ▶ {method_name}...", end=" ")
                    getattr(instance, method_name)()
                    print("✅ PASS")
                    results['passed'] += 1
                except AssertionError as e:
                    print(f"❌ FAIL: {e}")
                    results['failed'] += 1
                    results['errors'].append((method_name, str(e)))
                except Exception as e:
                    print(f"💥 ERROR: {e}")
                    results['failed'] += 1
                    results['errors'].append((method_name, traceback.format_exc()))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 RESUMO")
    print("=" * 70)
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")
    
    if results['errors']:
        print("\n🔍 Detalhes dos erros:")
        for name, error in results['errors']:
            print(f"\n  {name}:")
            print(f"    {error[:200]}...")
    
    return results['failed'] == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
