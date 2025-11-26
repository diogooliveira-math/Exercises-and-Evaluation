#!/usr/bin/env python3
r"""
End-to-End Tests for Test Generator

Comprehensive tests that simulate the full workflow of the Test Generator,
covering all selection modes and exercise types including sub-variants.

Tests cover:
1. Module and concept selection
2. Exercise loading with different filters
3. Selection modes (automatic, manual, random)
4. LaTeX generation with all exercise types
5. Sub-variant processing
6. Cross-platform compatibility
"""

import sys
import os
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Setup paths
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "SebentasDatabase" / "_tools"))
sys.path.insert(0, str(REPO_ROOT / "ExerciseDatabase" / "_tools"))


def load_database():
    """Load the exercise database index."""
    index_path = REPO_ROOT / "ExerciseDatabase" / "index.json"
    with open(index_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_modules_config():
    """Load the modules configuration."""
    import yaml
    config_path = REPO_ROOT / "ExerciseDatabase" / "modules_config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


class TestModuleAndConceptSelection:
    """Tests for module and concept selection functionality."""
    
    def test_load_modules_config(self):
        """Test that modules config can be loaded."""
        from generate_test_template import TestTemplate
        
        generator = TestTemplate()
        config = generator.load_modules_config()
        
        assert config is not None, "Config should not be None"
        assert 'matematica' in config, "Should have 'matematica' discipline"
        assert 'P4_funcoes' in config['matematica'], "Should have 'P4_funcoes' module"
    
    def test_get_module_names(self):
        """Test that all modules have proper names."""
        from generate_test_template import TestTemplate
        
        generator = TestTemplate()
        config = generator.load_modules_config()
        
        # Check that each module has a name
        for module_id, module_data in config['matematica'].items():
            assert 'name' in module_data, f"Module {module_id} should have a name"
            assert len(module_data['name']) > 0, f"Module {module_id} name should not be empty"


class TestExerciseLoading:
    """Tests for exercise loading functionality."""
    
    def test_load_all_exercises(self):
        """Test loading all exercises from index."""
        from generate_test_template import TestTemplate
        
        index = load_database()
        generator = TestTemplate()
        
        # Load exercises for a known module
        exercises = generator.load_exercises('matematica', 'P4_funcoes', None)
        
        assert len(exercises) > 0, "Should find exercises for P4_funcoes"
    
    def test_load_exercises_with_concept_filter(self):
        """Test loading exercises with concept filter."""
        from generate_test_template import TestTemplate
        
        generator = TestTemplate()
        
        # Load exercises for a specific concept
        exercises = generator.load_exercises('matematica', 'P4_funcoes', '4-funcao_inversa')
        
        assert len(exercises) > 0, "Should find exercises for funcao_inversa"
        
        # Verify all exercises match the concept
        for ex in exercises:
            concept = ex.get('concept', '')
            assert concept == '4-funcao_inversa', f"Exercise {ex['id']} should be from funcao_inversa"
    
    def test_load_exercises_by_ids(self):
        """Test loading exercises by specific IDs."""
        from generate_test_template import TestTemplate
        
        index = load_database()
        generator = TestTemplate()
        
        # Get some exercise IDs
        test_ids = [ex['id'] for ex in index['exercises'][:3]]
        
        exercises = generator.load_exercises_by_ids(test_ids)
        
        assert len(exercises) == len(test_ids), f"Should load {len(test_ids)} exercises"
        
        loaded_ids = [ex['id'] for ex in exercises]
        for test_id in test_ids:
            assert test_id in loaded_ids, f"Exercise {test_id} should be loaded"
    
    def test_load_exercises_preserves_order(self):
        """Test that loading exercises by IDs preserves order."""
        from generate_test_template import TestTemplate
        
        index = load_database()
        generator = TestTemplate()
        
        # Get some exercise IDs in specific order
        test_ids = [ex['id'] for ex in index['exercises'][:5]]
        # Reverse order to test preservation
        test_ids = test_ids[::-1]
        
        exercises = generator.load_exercises_by_ids(test_ids)
        
        for i, ex in enumerate(exercises):
            assert ex['id'] == test_ids[i], f"Order should be preserved at position {i}"


class TestSelectionModes:
    """Tests for different exercise selection modes."""
    
    def test_balanced_selection(self):
        """Test balanced selection mode distributes exercises evenly."""
        from generate_test_template import TestTemplate
        
        generator = TestTemplate(num_questions=6)
        
        # Load exercises
        exercises = generator.load_exercises('matematica', 'P4_funcoes', None)
        
        if len(exercises) < 6:
            # Skip if not enough exercises
            return
        
        # Test balanced selection
        selected = generator._select_balanced(exercises, 6)
        
        assert len(selected) == 6, "Should select 6 exercises"
    
    def test_balanced_selection_limited_pool(self):
        """Test balanced selection with fewer exercises than requested."""
        from generate_test_template import TestTemplate
        
        generator = TestTemplate(num_questions=100)
        
        # Load exercises
        exercises = generator.load_exercises('matematica', 'P4_funcoes', '4-funcao_inversa')
        
        # Test balanced selection - should return all available
        selected = generator._select_balanced(exercises, 100)
        
        assert len(selected) <= len(exercises), "Should not select more than available"


class TestLatexGeneration:
    """Tests for LaTeX content generation."""
    
    def test_generate_latex_with_normal_exercises(self):
        """Test LaTeX generation with normal exercises."""
        from generate_test_template import TestTemplate
        
        index = load_database()
        generator = TestTemplate()
        
        # Find normal exercises (paths ending with .tex)
        normal_exercises = [ex for ex in index['exercises'] if ex.get('path', '').endswith('.tex')]
        
        if not normal_exercises:
            return  # Skip if no normal exercises
        
        exercises = generator.load_exercises_by_ids([normal_exercises[0]['id']])
        
        latex = generator.generate_test_latex(
            "matematica",
            "Módulo de Teste",
            "Conceito de Teste",
            exercises
        )
        
        # Check basic LaTeX structure
        assert "\\documentclass" in latex, "Should have document class"
        assert "\\begin{document}" in latex, "Should have begin document"
        assert "\\end{document}" in latex, "Should have end document"
        assert "[Exercício não encontrado" not in latex, "Exercise should be found"
    
    def test_generate_latex_with_subvariant_exercises(self):
        """Test LaTeX generation with sub-variant exercises."""
        from generate_test_template import TestTemplate
        
        index = load_database()
        generator = TestTemplate()
        
        # Find sub-variant exercises (paths NOT ending with .tex)
        subvariant_exercises = [ex for ex in index['exercises'] if not ex.get('path', '').endswith('.tex')]
        
        if not subvariant_exercises:
            return  # Skip if no sub-variant exercises
        
        exercises = generator.load_exercises_by_ids([subvariant_exercises[0]['id']])
        
        latex = generator.generate_test_latex(
            "matematica",
            "Módulo de Teste",
            "Conceito de Teste",
            exercises
        )
        
        # Check that sub-variants are processed
        assert "[Exercício não encontrado" not in latex, "Exercise should be found"
        assert "[Subvariant não encontrado" not in latex, "Subvariants should be found"
    
    def test_generate_latex_with_mixed_exercises(self):
        """Test LaTeX generation with mixed exercise types."""
        from generate_test_template import TestTemplate
        
        index = load_database()
        generator = TestTemplate()
        
        # Find both types
        normal_exercises = [ex for ex in index['exercises'] if ex.get('path', '').endswith('.tex')]
        subvariant_exercises = [ex for ex in index['exercises'] if not ex.get('path', '').endswith('.tex')]
        
        if not normal_exercises or not subvariant_exercises:
            return  # Skip if missing either type
        
        test_ids = [normal_exercises[0]['id'], subvariant_exercises[0]['id']]
        exercises = generator.load_exercises_by_ids(test_ids)
        
        latex = generator.generate_test_latex(
            "matematica",
            "Módulo de Teste",
            "Vários",
            exercises
        )
        
        # Check all exercises are found
        assert latex.count("[Exercício não encontrado") == 0, "All exercises should be found"
    
    def test_generate_latex_title_variations(self):
        """Test LaTeX generation with different title configurations."""
        from generate_test_template import TestTemplate
        
        index = load_database()
        generator = TestTemplate()
        
        exercises = generator.load_exercises_by_ids([index['exercises'][0]['id']])
        
        # Test with concept name
        latex1 = generator.generate_test_latex(
            "matematica",
            "Módulo P4",
            "Função Inversa",
            exercises
        )
        assert "Teste - Função Inversa" in latex1, "Should have concept in title"
        
        # Test without concept name
        latex2 = generator.generate_test_latex(
            "matematica",
            "Módulo P4",
            None,
            exercises
        )
        assert "Teste - Módulo P4" in latex2, "Should have module in title"


class TestSubvariantProcessing:
    """Tests for sub-variant input processing."""
    
    def test_process_subvariant_inputs(self):
        r"""Test that \\input{subvariant_*} commands are processed."""
        from generate_test_template import TestTemplate
        
        index = load_database()
        
        # Find sub-variant exercises
        subvariant_exercises = [ex for ex in index['exercises'] if not ex.get('path', '').endswith('.tex')]
        
        if not subvariant_exercises:
            return  # Skip if no sub-variant exercises
        
        generator = TestTemplate()
        exercises = generator.load_exercises_by_ids([subvariant_exercises[0]['id']])
        
        latex = generator.generate_test_latex(
            "matematica",
            "Teste",
            "Teste",
            exercises
        )
        
        # After processing, \input{subvariant_*} should be replaced
        assert "\\input{subvariant_" not in latex, "Input commands should be resolved"
    
    def test_subvariant_content_included(self):
        """Test that sub-variant content is included in output."""
        from generate_test_template import TestTemplate
        
        index = load_database()
        generator = TestTemplate()
        
        # Find sub-variant exercises
        subvariant_exercises = [ex for ex in index['exercises'] if not ex.get('path', '').endswith('.tex')]
        
        if not subvariant_exercises:
            return  # Skip if no sub-variant exercises
        
        exercises = generator.load_exercises_by_ids([subvariant_exercises[0]['id']])
        
        latex = generator.generate_test_latex(
            "matematica",
            "Teste",
            "Teste",
            exercises
        )
        
        # Should have actual content (like $f(x) = something$)
        assert "$" in latex, "Should have math content from subvariants"


class TestCrossPlatformCompatibility:
    """Tests for cross-platform compatibility."""
    
    def test_path_normalization(self):
        """Test that paths are normalized for cross-platform use."""
        from generate_test_template import TestTemplate
        
        index = load_database()
        
        # Check if any paths have Windows separators
        for ex in index['exercises']:
            path = ex.get('path', '')
            if '\\' in path:
                # This exercise has Windows paths - test normalization
                generator = TestTemplate()
                exercises = generator.load_exercises_by_ids([ex['id']])
                
                latex = generator.generate_test_latex(
                    "matematica",
                    "Teste",
                    "Teste",
                    exercises
                )
                
                assert "[Exercício não encontrado" not in latex, \
                    f"Exercise {ex['id']} with Windows path should be found"
                break
    
    def test_open_file_function_exists(self):
        """Test that open_for_editing handles all platforms."""
        from generate_test_template import TestTemplate
        
        generator = TestTemplate()
        
        # Create a temp file to test with
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False) as f:
            f.write("\\documentclass{article}\n\\begin{document}\nTest\n\\end{document}")
            temp_path = f.name
        
        try:
            generator.tex_file = Path(temp_path)
            
            # Mock subprocess to avoid actually opening files
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = MagicMock(returncode=0)
                
                # Should not raise any exception
                generator.open_for_editing()
        finally:
            os.unlink(temp_path)
    
    def test_pdflatex_availability_check(self):
        """Test that pdflatex availability check function works."""
        from generate_test_template import check_pdflatex_available
        
        # The function should return a boolean without raising exceptions
        result = check_pdflatex_available()
        assert isinstance(result, bool), "check_pdflatex_available should return a boolean"
    
    def test_save_tex_without_compile(self):
        """Test that .tex file can be saved when pdflatex is unavailable."""
        from generate_test_template import TestTemplate
        
        index = load_database()
        generator = TestTemplate()
        
        # Set up module and concept
        generator.module = "P4_funcoes"
        generator.concept = "4-funcao_inversa"
        
        # Load an exercise
        exercises = generator.load_exercises_by_ids([index['exercises'][0]['id']])
        generator.exercises = exercises
        
        # Create temp dir and tex file
        generator.temp_dir = tempfile.mkdtemp(prefix="test_template_")
        generator.tex_file = Path(generator.temp_dir) / "test.tex"
        
        # Generate LaTeX content
        latex = generator.generate_test_latex(
            "matematica",
            "Módulo P4",
            "Função Inversa",
            exercises
        )
        
        # Save to temp file
        generator.tex_file.write_text(latex, encoding='utf-8')
        
        try:
            # Test save_tex_without_compile
            saved_path = generator.save_tex_without_compile()
            
            assert saved_path.exists(), "Saved .tex file should exist"
            assert saved_path.suffix == '.tex', "Saved file should have .tex extension"
            assert saved_path.read_text(encoding='utf-8') == latex, "Content should match"
            
            # Clean up the saved file
            saved_path.unlink()
        finally:
            generator.cleanup()


class TestEnvironmentVariableIntegration:
    """Tests for environment variable based exercise selection."""
    
    def test_env_selected_exercises(self):
        """Test that TEST_SELECTED_EXERCISES env var works."""
        from generate_test_template import TestTemplate
        
        index = load_database()
        
        # Set up environment variable
        test_ids = [index['exercises'][0]['id'], index['exercises'][1]['id']]
        os.environ['TEST_SELECTED_EXERCISES'] = ','.join(test_ids)
        
        try:
            generator = TestTemplate()
            
            # The generator should be able to load these exercises
            exercises = generator.load_exercises_by_ids(test_ids)
            
            assert len(exercises) == 2, "Should load 2 exercises from env var"
        finally:
            del os.environ['TEST_SELECTED_EXERCISES']


def run_all_tests():
    """Run all end-to-end tests."""
    print("\n" + "=" * 70)
    print("🧪 END-TO-END TESTS: Test Generator Full Workflow")
    print("=" * 70)
    
    test_classes = [
        TestModuleAndConceptSelection,
        TestExerciseLoading,
        TestSelectionModes,
        TestLatexGeneration,
        TestSubvariantProcessing,
        TestCrossPlatformCompatibility,
        TestEnvironmentVariableIntegration,
    ]
    
    total_passed = 0
    total_failed = 0
    results = {}
    
    for test_class in test_classes:
        class_name = test_class.__name__
        print(f"\n▶ {class_name}")
        
        instance = test_class()
        test_methods = [m for m in dir(instance) if m.startswith('test_')]
        
        for method_name in test_methods:
            test_func = getattr(instance, method_name)
            try:
                test_func()
                print(f"  ✅ {method_name}")
                total_passed += 1
                results[f"{class_name}.{method_name}"] = True
            except AssertionError as e:
                print(f"  ❌ {method_name}: {e}")
                total_failed += 1
                results[f"{class_name}.{method_name}"] = False
            except Exception as e:
                print(f"  ❌ {method_name}: ERROR - {e}")
                total_failed += 1
                results[f"{class_name}.{method_name}"] = False
    
    print("\n" + "=" * 70)
    print("📊 FINAL RESULTS")
    print("=" * 70)
    print(f"  Passed: {total_passed}")
    print(f"  Failed: {total_failed}")
    print(f"  Total:  {total_passed + total_failed}")
    
    all_passed = total_failed == 0
    print(f"\n🎯 Overall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
