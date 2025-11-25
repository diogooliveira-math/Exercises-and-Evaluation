#!/usr/bin/env python3
"""
Tests for Test Generator sub-variants support.

Tests validate that generate_test_template.py correctly processes exercises 
with sub-variants (folders with main.tex + subvariant_*.tex files).

Test Scenarios:
1. Single exercise with sub-variants (alíneas)
2. Multiple exercises with sub-variants
3. Mixed exercises (normal .tex files + sub-variants)
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

# Add parent directories to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SEBENTAS_TOOLS = PROJECT_ROOT / "SebentasDatabase" / "_tools"
sys.path.insert(0, str(SEBENTAS_TOOLS))

from generate_test_template import TestTemplate


class MockExerciseDB:
    """Helper to create mock exercise database for testing."""
    
    def __init__(self, temp_dir: Path):
        self.temp_dir = temp_dir
        self.exercise_db = temp_dir / "ExerciseDatabase"
        self.exercise_db.mkdir(parents=True, exist_ok=True)
        
        # Create index.json
        self.index = {"exercises": [], "database_version": "3.0", "total_exercises": 0}
        
    def create_normal_exercise(self, ex_id: str, content: str) -> Path:
        """Create a normal .tex exercise file."""
        concept_dir = self.exercise_db / "matematica" / "P4_funcoes" / "4-funcao_inversa" / "determinacao_grafica"
        concept_dir.mkdir(parents=True, exist_ok=True)
        
        tex_file = concept_dir / f"{ex_id}.tex"
        tex_file.write_text(content, encoding='utf-8')
        
        # Add to index
        self.index["exercises"].append({
            "id": ex_id,
            "path": str(tex_file.relative_to(self.exercise_db)),
            "discipline": "matematica",
            "module": "P4_funcoes",
            "concept": "4-funcao_inversa",
            "concept_name": "Função Inversa",
            "tipo": "determinacao_grafica",
            "tipo_nome": "Determinação Gráfica",
            "difficulty": 2,
            "type": "desenvolvimento",
            "status": "active",
            "classification": {
                "discipline": "matematica",
                "module": "P4_funcoes",
                "concept": "4-funcao_inversa",
                "concept_name": "Função Inversa",
                "tipo": "determinacao_grafica",
                "tipo_nome": "Determinação Gráfica",
                "difficulty": 2
            }
        })
        
        self.index["total_exercises"] = len(self.index["exercises"])
        return tex_file
    
    def create_subvariant_exercise(self, ex_id: str, main_intro: str, subvariants: list) -> Path:
        """Create an exercise with sub-variants (folder structure)."""
        concept_dir = self.exercise_db / "matematica" / "P4_funcoes" / "4-funcao_inversa" / "determinacao_analitica"
        concept_dir.mkdir(parents=True, exist_ok=True)
        
        ex_dir = concept_dir / ex_id
        ex_dir.mkdir(parents=True, exist_ok=True)
        
        # Create main.tex
        main_content = f"""% Exercise ID: {ex_id}
% has_subvariants: true

\\exercicio{{
{main_intro}
}}

\\begin{{enumerate}}[label=\\alph*)]
"""
        for i in range(1, len(subvariants) + 1):
            main_content += f"\\item \\input{{subvariant_{i}}}\n"
        main_content += "\\end{enumerate}\n"
        
        (ex_dir / "main.tex").write_text(main_content, encoding='utf-8')
        
        # Create subvariant files
        for i, subvar in enumerate(subvariants, 1):
            subvar_content = f"% Sub-variant {i}\n{subvar}\n"
            (ex_dir / f"subvariant_{i}.tex").write_text(subvar_content, encoding='utf-8')
        
        # Add to index (path is the folder, not a .tex file)
        self.index["exercises"].append({
            "id": ex_id,
            "path": str(ex_dir.relative_to(self.exercise_db)),
            "source_file": str(ex_dir.relative_to(self.exercise_db)),
            "discipline": "matematica",
            "module": "P4_funcoes",
            "concept": "4-funcao_inversa",
            "concept_name": "Função Inversa",
            "tipo": "determinacao_analitica",
            "tipo_nome": "Determinação Analítica",
            "difficulty": 2,
            "type": "desenvolvimento",
            "status": "active",
            "classification": {
                "discipline": "matematica",
                "module": "P4_funcoes",
                "concept": "4-funcao_inversa",
                "concept_name": "Função Inversa",
                "tipo": "determinacao_analitica",
                "tipo_nome": "Determinação Analítica",
                "difficulty": 2
            }
        })
        
        self.index["total_exercises"] = len(self.index["exercises"])
        return ex_dir
    
    def save_index(self):
        """Save index.json to disk."""
        index_file = self.exercise_db / "index.json"
        index_file.write_text(json.dumps(self.index, indent=2, ensure_ascii=False), encoding='utf-8')
        return index_file


def test_single_exercise_with_subvariants():
    """Test 1: Single exercise with sub-variants (alíneas)."""
    print("\n" + "="*60)
    print("TEST 1: Single exercise with sub-variants")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        mock_db = MockExerciseDB(temp_path)
        
        # Create a subvariant exercise
        ex_id = "TEST_SUBVAR_001"
        subvariants = [
            "$f(x) = x + 4$",
            "$g(x) = 2x - 3$",
            "$h(x) = 5 - x$"
        ]
        mock_db.create_subvariant_exercise(
            ex_id,
            "Determina analiticamente a função inversa:",
            subvariants
        )
        mock_db.save_index()
        
        # Create TestTemplate and override paths
        generator = TestTemplate()
        generator.exercise_db = mock_db.exercise_db
        
        # Load exercise by ID
        exercises = generator.load_exercises_by_ids([ex_id])
        
        assert len(exercises) == 1, f"Expected 1 exercise, got {len(exercises)}"
        print(f"✓ Loaded exercise: {exercises[0]['id']}")
        
        # Generate LaTeX
        latex = generator.generate_test_latex(
            "matematica",
            "P4: Funções",
            "Função Inversa",
            exercises
        )
        
        # Verify content
        assert ex_id in latex, f"Exercise ID {ex_id} not found in LaTeX"
        
        # Check if subvariants content is included (expanded, not \input)
        for subvar in subvariants:
            assert subvar in latex, f"Subvariant content '{subvar}' not found in LaTeX"
        
        # Check that \input{subvariant_*} is NOT in the output (should be expanded)
        assert "\\input{subvariant_" not in latex, "\\input{subvariant_*} should be expanded"
        
        print(f"✓ All {len(subvariants)} subvariants included in LaTeX")
        print("✅ TEST 1 PASSED")
        return True


def test_multiple_exercises_with_subvariants():
    """Test 2: Multiple exercises with sub-variants."""
    print("\n" + "="*60)
    print("TEST 2: Multiple exercises with sub-variants")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        mock_db = MockExerciseDB(temp_path)
        
        # Create 3 subvariant exercises
        exercises_data = [
            {
                "id": "TEST_MULTI_001",
                "intro": "Funções lineares:",
                "subvariants": ["$f(x) = x + 1$", "$f(x) = 2x$"]
            },
            {
                "id": "TEST_MULTI_002", 
                "intro": "Funções quadráticas:",
                "subvariants": ["$f(x) = x^2$", "$f(x) = x^2 + 1$", "$f(x) = 2x^2$"]
            },
            {
                "id": "TEST_MULTI_003",
                "intro": "Funções racionais:",
                "subvariants": ["$f(x) = \\frac{1}{x}$", "$f(x) = \\frac{x+1}{x-1}$"]
            }
        ]
        
        for ex_data in exercises_data:
            mock_db.create_subvariant_exercise(
                ex_data["id"],
                ex_data["intro"],
                ex_data["subvariants"]
            )
        mock_db.save_index()
        
        # Create TestTemplate
        generator = TestTemplate()
        generator.exercise_db = mock_db.exercise_db
        
        # Load all exercises
        exercise_ids = [ex["id"] for ex in exercises_data]
        exercises = generator.load_exercises_by_ids(exercise_ids)
        
        assert len(exercises) == 3, f"Expected 3 exercises, got {len(exercises)}"
        print(f"✓ Loaded {len(exercises)} exercises")
        
        # Generate LaTeX
        latex = generator.generate_test_latex(
            "matematica",
            "P4: Funções",
            "Função Inversa",
            exercises
        )
        
        # Verify all exercises are included
        for ex_data in exercises_data:
            assert ex_data["id"] in latex, f"Exercise {ex_data['id']} not found"
            for subvar in ex_data["subvariants"]:
                assert subvar in latex, f"Subvariant '{subvar}' not found"
        
        print("✓ All 3 exercises with subvariants included correctly")
        print("✅ TEST 2 PASSED")
        return True


def test_mixed_exercises():
    """Test 3: Mixed exercises (normal .tex + sub-variants)."""
    print("\n" + "="*60)
    print("TEST 3: Mixed exercises (normal + sub-variants)")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        mock_db = MockExerciseDB(temp_path)
        
        # Create 2 normal exercises
        normal_1 = mock_db.create_normal_exercise(
            "TEST_NORMAL_001",
            "\\exercicio{Desenha o gráfico de $f(x) = x^2$ e determina graficamente a função inversa.}"
        )
        normal_2 = mock_db.create_normal_exercise(
            "TEST_NORMAL_002",
            "\\exercicio{Verifica se $f(x) = 3x - 1$ é injetiva.}"
        )
        
        # Create 2 subvariant exercises
        mock_db.create_subvariant_exercise(
            "TEST_SUBVAR_MIX_001",
            "Determina a inversa:",
            ["$f(x) = x + 5$", "$g(x) = 3x$"]
        )
        mock_db.create_subvariant_exercise(
            "TEST_SUBVAR_MIX_002",
            "Calcula:",
            ["$h(x) = \\frac{1}{x+1}$", "$k(x) = 2x - 7$", "$m(x) = x^3$"]
        )
        mock_db.save_index()
        
        # Create TestTemplate
        generator = TestTemplate()
        generator.exercise_db = mock_db.exercise_db
        
        # Load all exercises (mixed order)
        exercise_ids = [
            "TEST_NORMAL_001",
            "TEST_SUBVAR_MIX_001",
            "TEST_NORMAL_002",
            "TEST_SUBVAR_MIX_002"
        ]
        exercises = generator.load_exercises_by_ids(exercise_ids)
        
        assert len(exercises) == 4, f"Expected 4 exercises, got {len(exercises)}"
        print(f"✓ Loaded {len(exercises)} mixed exercises")
        
        # Generate LaTeX
        latex = generator.generate_test_latex(
            "matematica",
            "P4: Funções",
            "Teste Misto",
            exercises
        )
        
        # Verify normal exercises
        assert "Desenha o gráfico" in latex, "Normal exercise 1 content not found"
        assert "Verifica se" in latex, "Normal exercise 2 content not found"
        
        # Verify subvariant exercises
        assert "$f(x) = x + 5$" in latex, "Subvariant content not found"
        assert "$h(x) = \\frac{1}{x+1}$" in latex, "Subvariant content not found"
        
        # Verify no raw \input commands remain
        assert "\\input{subvariant_" not in latex, "\\input should be expanded"
        
        # Verify no "não encontrado" errors
        assert "não encontrado" not in latex.lower(), "Exercise not found error detected"
        assert "not found" not in latex.lower(), "Exercise not found error detected"
        
        print("✓ 2 normal exercises loaded correctly")
        print("✓ 2 subvariant exercises loaded and expanded correctly")
        print("✅ TEST 3 PASSED")
        return True


def test_real_exercise():
    """Test with real exercise from database (if available)."""
    print("\n" + "="*60)
    print("TEST 4: Real exercise MAT_P4FUNCOE_4FIN_ANA_001 (optional)")
    print("="*60)
    
    # Check if real exercise exists
    real_exercise_path = PROJECT_ROOT / "ExerciseDatabase" / "matematica" / "P4_funcoes" / "4-funcao_inversa" / "determinacao_analitica" / "MAT_P4FUNCOE_4FIN_ANA_001"
    
    if not real_exercise_path.exists():
        print("⚠ Real exercise not found, skipping test")
        return True
    
    # Create TestTemplate with real paths
    generator = TestTemplate()
    
    # Load exercise by ID
    exercises = generator.load_exercises_by_ids(["MAT_P4FUNCOE_4FIN_ANA_001"])
    
    if not exercises:
        print("⚠ Exercise not found in index.json, skipping test")
        return True
    
    print(f"✓ Loaded exercise: {exercises[0]['id']}")
    
    # Generate LaTeX
    latex = generator.generate_test_latex(
        "matematica",
        "P4: Funções",
        "Função Inversa",
        exercises
    )
    
    # Verify no "não encontrado" errors
    if "não encontrado" in latex.lower() or "[exercício não encontrado" in latex.lower():
        print("❌ Exercise not found error detected!")
        print("This is the bug we are fixing.")
        return False
    
    # Check subvariants are expanded
    assert "f(x) = x + 4" in latex, "Subvariant 1 not found"
    assert "\\input{subvariant_" not in latex, "\\input should be expanded"
    
    print("✓ Real exercise loaded and expanded correctly")
    print("✅ TEST 4 PASSED")
    return True


def run_all_tests():
    """Run all tests and report results."""
    print("\n" + "="*70)
    print("  TEST GENERATOR SUB-VARIANTS SUPPORT TESTS")
    print("="*70)
    
    results = {}
    
    try:
        results["test_single"] = test_single_exercise_with_subvariants()
    except Exception as e:
        print(f"❌ TEST 1 FAILED: {e}")
        import traceback
        traceback.print_exc()
        results["test_single"] = False
    
    try:
        results["test_multiple"] = test_multiple_exercises_with_subvariants()
    except Exception as e:
        print(f"❌ TEST 2 FAILED: {e}")
        import traceback
        traceback.print_exc()
        results["test_multiple"] = False
    
    try:
        results["test_mixed"] = test_mixed_exercises()
    except Exception as e:
        print(f"❌ TEST 3 FAILED: {e}")
        import traceback
        traceback.print_exc()
        results["test_mixed"] = False
    
    try:
        results["test_real"] = test_real_exercise()
    except Exception as e:
        print(f"❌ TEST 4 FAILED: {e}")
        import traceback
        traceback.print_exc()
        results["test_real"] = False
    
    # Summary
    print("\n" + "="*70)
    print("  TEST SUMMARY")
    print("="*70)
    
    all_passed = True
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False
    
    print("="*70)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED")
    
    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
