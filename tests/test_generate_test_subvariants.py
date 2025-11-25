#!/usr/bin/env python3
r"""
Tests for Test Generator handling of sub-variant exercises.

Tests that the Test Generator (generate_test_template.py) correctly
handles exercises with the v3.4 sub-variants structure:
  - Folder with main.tex + subvariant_*.tex files
  - Proper resolution of \input{} commands
  - Mixed exercises (normal + sub-variants)

Based on: Test_Generator_Subvariants_Report.md
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from typing import List, Dict

# Add tools directories to path
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "SebentasDatabase" / "_tools"))
sys.path.insert(0, str(REPO_ROOT / "ExerciseDatabase" / "_tools"))


class MockExerciseDatabase:
    """Creates a mock exercise database for testing."""
    
    def __init__(self, temp_dir: Path):
        self.temp_dir = temp_dir
        self.exercise_db = temp_dir / "ExerciseDatabase"
        self.index_path = self.exercise_db / "index.json"
        self.exercises = []
        
    def create_structure(self):
        """Create the base directory structure."""
        self.exercise_db.mkdir(parents=True, exist_ok=True)
        
    def add_normal_exercise(self, exercise_id: str, content: str, 
                           module: str = "P4_funcoes", 
                           concept: str = "1-generalidades_funcoes") -> Dict:
        """Add a normal (single .tex file) exercise."""
        # Create directory structure
        exercise_dir = self.exercise_db / "matematica" / module / concept
        exercise_dir.mkdir(parents=True, exist_ok=True)
        
        # Create .tex file
        tex_file = exercise_dir / f"{exercise_id}.tex"
        tex_file.write_text(content, encoding='utf-8')
        
        # Create exercise entry
        exercise = {
            "id": exercise_id,
            "path": f"matematica/{module}/{concept}/{exercise_id}.tex",
            "discipline": "matematica",
            "module": module,
            "module_name": f"Módulo {module}",
            "concept": concept,
            "concept_name": concept.replace('-', ' ').replace('_', ' ').title(),
            "difficulty": 2,
            "type": "desenvolvimento",
            "tags": ["test"],
            "points": 10,
            "status": "active"
        }
        
        self.exercises.append(exercise)
        return exercise
    
    def add_subvariant_exercise(self, exercise_id: str, main_content: str,
                                subvariants: List[str],
                                module: str = "P4_funcoes",
                                concept: str = "4-funcao_inversa",
                                tipo: str = "determinacao_analitica") -> Dict:
        """Add an exercise with sub-variants (folder structure)."""
        # Create directory structure
        exercise_dir = self.exercise_db / "matematica" / module / concept / tipo / exercise_id
        exercise_dir.mkdir(parents=True, exist_ok=True)
        
        # Create main.tex
        main_tex = exercise_dir / "main.tex"
        main_tex.write_text(main_content, encoding='utf-8')
        
        # Create subvariant files
        for i, subvariant_content in enumerate(subvariants, 1):
            subvariant_file = exercise_dir / f"subvariant_{i}.tex"
            subvariant_file.write_text(subvariant_content, encoding='utf-8')
        
        # Create exercise entry (path is the folder, not a .tex file)
        exercise = {
            "id": exercise_id,
            "path": f"matematica/{module}/{concept}/{tipo}/{exercise_id}",
            "discipline": "matematica",
            "module": module,
            "module_name": f"Módulo {module}",
            "concept": concept,
            "concept_name": concept.replace('-', ' ').replace('_', ' ').title(),
            "tipo": tipo,
            "tipo_nome": tipo.replace('_', ' ').title(),
            "difficulty": 2,
            "type": "desenvolvimento",
            "tags": ["test", "subvariants"],
            "points": 10,
            "status": "active"
        }
        
        self.exercises.append(exercise)
        return exercise
    
    def save_index(self):
        """Save the index.json file."""
        index = {
            "database_version": "3.0",
            "total_exercises": len(self.exercises),
            "exercises": self.exercises
        }
        
        self.index_path.write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding='utf-8')
        return self.index_path


def test_normal_exercise_loading():
    """Test 1: Loading a normal exercise (single .tex file)."""
    print("\n" + "="*60)
    print("TEST 1: Normal Exercise Loading")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create mock database
        db = MockExerciseDatabase(temp_path)
        db.create_structure()
        
        # Add a normal exercise
        content = r"""% Exercise ID: TEST_NORMAL_001
\exercicio{
Considera a função $f(x) = 2x + 3$.
Determina $f(5)$.
}
"""
        exercise = db.add_normal_exercise("TEST_NORMAL_001", content)
        db.save_index()
        
        # Import and test
        from generate_test_template import TestTemplate
        
        generator = TestTemplate()
        generator.exercise_db = db.exercise_db
        
        # Load exercises by ID
        exercises = generator.load_exercises_by_ids(["TEST_NORMAL_001"])
        
        # Generate LaTeX
        latex = generator.generate_test_latex(
            "matematica", 
            "Módulo P4",
            "Generalidades",
            exercises
        )
        
        # Validate
        assert len(exercises) == 1, f"Expected 1 exercise, got {len(exercises)}"
        assert "\\exercicio{" in latex, "LaTeX should contain \\exercicio"
        assert "[Exercício não encontrado" not in latex, "Exercise should be found"
        assert "f(x) = 2x + 3" in latex, "Exercise content should be present"
        
        print("✅ TEST 1 PASSED: Normal exercise loaded correctly")
        return True


def test_subvariant_exercise_loading():
    """Test 2: Loading an exercise with sub-variants (folder structure)."""
    print("\n" + "="*60)
    print("TEST 2: Sub-variant Exercise Loading")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create mock database
        db = MockExerciseDatabase(temp_path)
        db.create_structure()
        
        # Add a sub-variant exercise
        main_content = r"""% Exercise ID: TEST_SUBVAR_001
% has_subvariants: true

\exercicio{
Determina analiticamente a função inversa das seguintes expressões:
}

\begin{enumerate}[label=\alph*)]
\item \input{subvariant_1}
\item \input{subvariant_2}
\item \input{subvariant_3}
\end{enumerate}
"""
        
        subvariants = [
            r"% Subvariant 1" + "\n" + r"$f(x) = 3x - 2$",
            r"% Subvariant 2" + "\n" + r"$f(x) = 5x + 1$",
            r"% Subvariant 3" + "\n" + r"$f(x) = -2x + 7$"
        ]
        
        exercise = db.add_subvariant_exercise(
            "TEST_SUBVAR_001", 
            main_content, 
            subvariants
        )
        db.save_index()
        
        # Import and test
        from generate_test_template import TestTemplate
        
        generator = TestTemplate()
        generator.exercise_db = db.exercise_db
        
        # Load exercises by ID
        exercises = generator.load_exercises_by_ids(["TEST_SUBVAR_001"])
        
        # Generate LaTeX
        latex = generator.generate_test_latex(
            "matematica", 
            "Módulo P4",
            "Função Inversa",
            exercises
        )
        
        # Validate
        assert len(exercises) == 1, f"Expected 1 exercise, got {len(exercises)}"
        assert "[Exercício não encontrado" not in latex, "Exercise should be found (sub-variant support)"
        assert "\\exercicio{" in latex or "Determina analiticamente" in latex, "Exercise content should be present"
        
        # Check that sub-variants are processed (either included or referenced)
        # After fix, sub-variants should be expanded inline
        subvariant_found = any(sv in latex for sv in ["3x - 2", "5x + 1", "-2x + 7"])
        
        print(f"  - Exercises loaded: {len(exercises)}")
        print(f"  - 'Exercício não encontrado' in output: {'[Exercício não encontrado' in latex}")
        print(f"  - Sub-variant content found: {subvariant_found}")
        
        if "[Exercício não encontrado" in latex:
            print("❌ TEST 2 FAILED: Sub-variant exercise not found")
            print("   This is the bug we need to fix!")
            return False
        
        print("✅ TEST 2 PASSED: Sub-variant exercise loaded correctly")
        return True


def test_mixed_exercises_loading():
    """Test 3: Loading a mix of normal and sub-variant exercises."""
    print("\n" + "="*60)
    print("TEST 3: Mixed Exercises Loading")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create mock database
        db = MockExerciseDatabase(temp_path)
        db.create_structure()
        
        # Add a normal exercise
        normal_content = r"""% Exercise ID: TEST_MIXED_NORMAL
\exercicio{
Simplifica a expressão $\frac{x^2 - 4}{x - 2}$.
}
"""
        db.add_normal_exercise("TEST_MIXED_NORMAL", normal_content)
        
        # Add a sub-variant exercise
        main_content = r"""% Exercise ID: TEST_MIXED_SUBVAR
\exercicio{
Determina a função inversa:
}

\begin{enumerate}[label=\alph*)]
\item \input{subvariant_1}
\item \input{subvariant_2}
\end{enumerate}
"""
        
        subvariants = [
            r"$g(x) = x + 1$",
            r"$g(x) = 2x$"
        ]
        
        db.add_subvariant_exercise("TEST_MIXED_SUBVAR", main_content, subvariants)
        db.save_index()
        
        # Import and test
        from generate_test_template import TestTemplate
        
        generator = TestTemplate()
        generator.exercise_db = db.exercise_db
        
        # Load both exercises
        exercises = generator.load_exercises_by_ids(["TEST_MIXED_NORMAL", "TEST_MIXED_SUBVAR"])
        
        # Generate LaTeX
        latex = generator.generate_test_latex(
            "matematica", 
            "Módulo P4",
            "Vários",
            exercises
        )
        
        # Validate
        assert len(exercises) == 2, f"Expected 2 exercises, got {len(exercises)}"
        
        # Count how many exercises are actually found
        not_found_count = latex.count("[Exercício não encontrado")
        
        print(f"  - Exercises loaded: {len(exercises)}")
        print(f"  - 'Exercício não encontrado' count: {not_found_count}")
        
        # Normal exercise should always be found
        assert "x^2 - 4" in latex, "Normal exercise content should be present"
        
        if not_found_count == 0:
            print("✅ TEST 3 PASSED: Both normal and sub-variant exercises loaded correctly")
            return True
        elif not_found_count == 1:
            print("⚠️ TEST 3 PARTIAL: Normal exercise works, sub-variant doesn't")
            return False
        else:
            print("❌ TEST 3 FAILED: Both exercises not found")
            return False


def test_multiple_subvariant_exercises():
    """Test 4: Loading multiple exercises with sub-variants."""
    print("\n" + "="*60)
    print("TEST 4: Multiple Sub-variant Exercises Loading")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create mock database
        db = MockExerciseDatabase(temp_path)
        db.create_structure()
        
        # Add multiple sub-variant exercises
        for i in range(1, 4):
            main_content = f"""% Exercise ID: TEST_MULTI_SUBVAR_{i:03d}
\\exercicio{{
Exercício {i} - Determina a função inversa:
}}

\\begin{{enumerate}}[label=\\alph*)]
\\item \\input{{subvariant_1}}
\\item \\input{{subvariant_2}}
\\end{{enumerate}}
"""
            
            subvariants = [
                f"$f_{i}(x) = {i}x$",
                f"$f_{i}(x) = x + {i}$"
            ]
            
            db.add_subvariant_exercise(
                f"TEST_MULTI_SUBVAR_{i:03d}", 
                main_content, 
                subvariants,
                tipo=f"tipo_{i}"
            )
        
        db.save_index()
        
        # Import and test
        from generate_test_template import TestTemplate
        
        generator = TestTemplate()
        generator.exercise_db = db.exercise_db
        
        # Load all exercises
        exercise_ids = [f"TEST_MULTI_SUBVAR_{i:03d}" for i in range(1, 4)]
        exercises = generator.load_exercises_by_ids(exercise_ids)
        
        # Generate LaTeX
        latex = generator.generate_test_latex(
            "matematica", 
            "Módulo P4",
            "Vários Tipos",
            exercises
        )
        
        # Validate
        assert len(exercises) == 3, f"Expected 3 exercises, got {len(exercises)}"
        
        not_found_count = latex.count("[Exercício não encontrado")
        
        print(f"  - Exercises loaded: {len(exercises)}")
        print(f"  - 'Exercício não encontrado' count: {not_found_count}")
        
        if not_found_count == 0:
            print("✅ TEST 4 PASSED: All sub-variant exercises loaded correctly")
            return True
        else:
            print(f"❌ TEST 4 FAILED: {not_found_count} exercises not found")
            return False


def run_all_tests():
    """Run all tests and report results."""
    print("\n" + "="*70)
    print("🧪 TEST GENERATOR SUB-VARIANTS TEST SUITE")
    print("="*70)
    
    results = {
        "Test 1 - Normal Exercise": test_normal_exercise_loading(),
        "Test 2 - Sub-variant Exercise": test_subvariant_exercise_loading(),
        "Test 3 - Mixed Exercises": test_mixed_exercises_loading(),
        "Test 4 - Multiple Sub-variants": test_multiple_subvariant_exercises(),
    }
    
    print("\n" + "="*70)
    print("📊 FINAL RESULTS")
    print("="*70)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    all_passed = all(results.values())
    print(f"\n🎯 Overall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
