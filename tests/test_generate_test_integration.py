#!/usr/bin/env python3
r"""
Integration Tests for Test Generator with Sub-variants

Tests the full workflow of the Test Generator using actual exercises
from the ExerciseDatabase, including exercises with sub-variants.

This test validates that the Test Generator can:
1. Load single sub-variant exercises
2. Load mixed exercises (normal + sub-variants)
3. Load multiple sub-variant exercises
4. Handle random samples from the database
"""

import sys
import json
from pathlib import Path

# Setup paths
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "SebentasDatabase" / "_tools"))
sys.path.insert(0, str(REPO_ROOT / "ExerciseDatabase" / "_tools"))


def load_database():
    """Load the exercise database index."""
    index_path = REPO_ROOT / "ExerciseDatabase" / "index.json"
    with open(index_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def categorize_exercises(index):
    """Categorize exercises into sub-variant and normal types."""
    subvariant_exercises = []
    normal_exercises = []
    
    for ex in index['exercises']:
        path = ex.get('path', '')
        if not path.endswith('.tex'):
            subvariant_exercises.append(ex)
        else:
            normal_exercises.append(ex)
    
    return subvariant_exercises, normal_exercises


def test_integration_single_subvariant():
    """Test loading a single sub-variant exercise from the database."""
    from generate_test_template import TestTemplate
    
    index = load_database()
    subvariant_exercises, _ = categorize_exercises(index)
    
    if not subvariant_exercises:
        # Skip if no sub-variant exercises in database
        return
    
    test_ex = subvariant_exercises[0]
    generator = TestTemplate()
    exercises = generator.load_exercises_by_ids([test_ex['id']])
    
    latex = generator.generate_test_latex(
        "matematica",
        "MÓDULO P4 - Funções",
        "Função Inversa",
        exercises
    )
    
    assert len(exercises) == 1, f"Expected 1 exercise, got {len(exercises)}"
    assert "[Exercício não encontrado" not in latex, "Exercise should be found"
    assert "[Subvariant não encontrado" not in latex, "All subvariants should be found"


def test_integration_mixed_exercises():
    """Test loading a mix of normal and sub-variant exercises."""
    from generate_test_template import TestTemplate
    
    index = load_database()
    subvariant_exercises, normal_exercises = categorize_exercises(index)
    
    if not subvariant_exercises or not normal_exercises:
        # Skip if database doesn't have both types
        return
    
    test_ids = [normal_exercises[0]['id'], subvariant_exercises[0]['id']]
    generator = TestTemplate()
    exercises = generator.load_exercises_by_ids(test_ids)
    
    latex = generator.generate_test_latex(
        "matematica",
        "MÓDULO P4 - Funções",
        "Vários",
        exercises
    )
    
    assert len(exercises) == 2, f"Expected 2 exercises, got {len(exercises)}"
    assert latex.count("[Exercício não encontrado") == 0, "All exercises should be found"


def test_integration_all_subvariants():
    """Test loading all sub-variant exercises from the database."""
    from generate_test_template import TestTemplate
    
    index = load_database()
    subvariant_exercises, _ = categorize_exercises(index)
    
    if len(subvariant_exercises) < 2:
        # Skip if not enough sub-variant exercises
        return
    
    test_ids = [ex['id'] for ex in subvariant_exercises]
    generator = TestTemplate()
    exercises = generator.load_exercises_by_ids(test_ids)
    
    latex = generator.generate_test_latex(
        "matematica",
        "MÓDULO P4 - Funções",
        "Função Inversa",
        exercises
    )
    
    assert len(exercises) == len(test_ids), f"Expected {len(test_ids)} exercises"
    assert latex.count("[Exercício não encontrado") == 0, "All exercises should be found"
    assert latex.count("[Subvariant não encontrado") == 0, "All subvariants should be found"


def test_integration_random_sample():
    """Test loading a random sample of exercises including sub-variants."""
    import random
    from generate_test_template import TestTemplate
    
    index = load_database()
    all_exercises = index['exercises']
    
    sample_size = min(5, len(all_exercises))
    sample = random.sample(all_exercises, sample_size)
    test_ids = [ex['id'] for ex in sample]
    
    generator = TestTemplate()
    exercises = generator.load_exercises_by_ids(test_ids)
    
    latex = generator.generate_test_latex(
        "matematica",
        "MÓDULO P4",
        "Vários",
        exercises
    )
    
    assert len(exercises) == sample_size, f"Expected {sample_size} exercises"
    assert latex.count("[Exercício não encontrado") == 0, "All exercises should be found"


def run_all_tests():
    """Run all integration tests and report results."""
    print("\n" + "=" * 70)
    print("🧪 INTEGRATION TESTS: Test Generator with Sub-variants")
    print("=" * 70)
    
    tests = [
        ("Single Sub-variant Exercise", test_integration_single_subvariant),
        ("Mixed Exercises", test_integration_mixed_exercises),
        ("All Sub-variant Exercises", test_integration_all_subvariants),
        ("Random Sample", test_integration_random_sample),
    ]
    
    results = {}
    for name, test_func in tests:
        print(f"\n▶ Running: {name}")
        try:
            test_func()
            print(f"  ✅ PASSED")
            results[name] = True
        except AssertionError as e:
            print(f"  ❌ FAILED: {e}")
            results[name] = False
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            results[name] = False
    
    print("\n" + "=" * 70)
    print("📊 FINAL RESULTS")
    print("=" * 70)
    
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {name}: {status}")
    
    all_passed = all(results.values())
    print(f"\n🎯 Overall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
