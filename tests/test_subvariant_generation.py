#!/usr/bin/env python3
"""
Automated test script for sub-variant exercise generation.

Tests the generation of exercises with sub-variants (alíneas) using 3 mock variations:
1. Linear functions
2. Quadratic functions
3. Rational functions

Validates LaTeX generation, metadata consistency, and basic structure.
"""

import os
import sys
import json
import tempfile
from pathlib import Path

# Add parent directory to path to import tools
sys.path.append(str(Path(__file__).parent.parent / "ExerciseDatabase" / "_tools"))

from generate_subvariant_exercise import generate_subvariant_exercise_folder


def test_subvariant_generation():
    """Test generation of exercises with sub-variants."""

    # Test data for 3 variations
    test_cases = [
        {
            "name": "Linear Functions",
            "subvariant_texts": ["f(x) = x + 4", "f(x) = 2x - 3", "f(x) = 5 - x"],
            "exercise_description": "Determina analiticamente a função inversa das seguintes expressões:",
            "metadata": {
                "difficulty": 2,
                "tags": ["funcao_inversa", "determinacao_analitica", "linear"],
                "author": "Test Script"
            }
        },
        {
            "name": "Quadratic Functions",
            "subvariant_texts": ["f(x) = x^2 + 1", "f(x) = 2x^2 - 4x + 1", "f(x) = (x-1)^2"],
            "exercise_description": "Determina analiticamente a função inversa das seguintes expressões:",
            "metadata": {
                "difficulty": 3,
                "tags": ["funcao_inversa", "determinacao_analitica", "quadratica"],
                "author": "Test Script"
            }
        },
        {
            "name": "Rational Functions",
            "subvariant_texts": ["f(x) = \\frac{1}{x}", "f(x) = \\frac{2}{x-1}", "f(x) = \\frac{x+1}{x-2}"],
            "exercise_description": "Determina analiticamente a função inversa das seguintes expressões:",
            "metadata": {
                "difficulty": 4,
                "tags": ["funcao_inversa", "determinacao_analitica", "racional"],
                "author": "Test Script"
            }
        }
    ]

    results = []

    # Create temporary directory for all tests
    with tempfile.TemporaryDirectory() as temp_dir:
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🧪 Testing Variation {i}: {test_case['name']}")

            exercise_id = f"MAT_P4FUNCOE_4FIN_ANA_TEST_{i:03d}"

            # Generate exercise folder
            exercise_folder = generate_subvariant_exercise_folder(
                exercise_id,
                test_case["name"],
                test_case["subvariant_texts"],
                test_case["exercise_description"],
                test_case["metadata"],
                temp_dir
            )

            # Validate folder structure
            validation_results = validate_folder_structure(exercise_folder, test_case)

            results.append({
                "variation": i,
                "name": test_case["name"],
                "exercise_id": exercise_id,
                "exercise_folder": exercise_folder,
                "validation": validation_results
            })

            print(f"✅ Generated exercise folder: {exercise_id}")
            print(f"📁 Folder: {exercise_folder}")
            print(f"🔍 Validation: {'PASS' if all(validation_results.values()) else 'FAIL'}")

    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)

    all_passed = True
    for result in results:
        status = "✅ PASS" if all(result["validation"].values()) else "❌ FAIL"
        print(f"Variation {result['variation']}: {result['name']} - {status}")
        if not all(result["validation"].values()):
            all_passed = False
            for check, passed in result["validation"].items():
                if not passed:
                    print(f"  - {check}: FAILED")

    print(f"\n🎯 Overall Result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")

    # Cleanup temp files (optional, for inspection)
    # for result in results:
    #     os.unlink(result["latex_file"])

    return all_passed


def validate_folder_structure(exercise_folder: str, test_case: dict) -> dict:
    """Validate the generated folder structure."""
    results = {}

    # Check folder exists
    results["folder_exists"] = os.path.exists(exercise_folder) and os.path.isdir(exercise_folder)

    if not results["folder_exists"]:
        return results

    # Check for main.tex
    main_tex = os.path.join(exercise_folder, "main.tex")
    results["has_main_tex"] = os.path.exists(main_tex)

    # Check for sub-variant files
    expected_subvariants = len(test_case["subvariant_texts"])
    subvariant_files = [f for f in os.listdir(exercise_folder) if f.startswith("subvariant_") and f.endswith(".tex")]
    results["correct_subvariant_count"] = len(subvariant_files) == expected_subvariants

    # Validate main.tex content
    if results["has_main_tex"]:
        with open(main_tex, 'r', encoding='utf-8') as f:
            main_content = f.read()
        results["main_has_exercicio_macro"] = "\\exercicio{" in main_content
        results["main_has_enumerate"] = "\\begin{enumerate}" in main_content and "\\end{enumerate}" in main_content
        results["main_has_correct_includes"] = main_content.count("\\input{subvariant_") == expected_subvariants

    # Validate sub-variant files
    for i, text in enumerate(test_case["subvariant_texts"], 1):
        sub_file = os.path.join(exercise_folder, f"subvariant_{i}.tex")
        results[f"subvariant_{i}_exists"] = os.path.exists(sub_file)
        if results[f"subvariant_{i}_exists"]:
            with open(sub_file, 'r', encoding='utf-8') as f:
                content = f.read()
            results[f"subvariant_{i}_has_content"] = text in content

    return results


if __name__ == "__main__":
    success = test_subvariant_generation()
    sys.exit(0 if success else 1)