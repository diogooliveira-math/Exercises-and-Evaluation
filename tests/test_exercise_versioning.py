"""Test for exercise versioning functionality - generating test versions by swapping exercises within a type."""

import subprocess
import os
import sys
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def test_exercise_versioning():
    """Test that exercise versioning works - generating test versions by swapping exercises within a type."""
    script_path = PROJECT_ROOT / "SebentasDatabase" / "_tools" / "generate_tests.py"

    print("Testing exercise versioning functionality...")

    # First, generate a base test
    print("Generating base test...")
    result_base = subprocess.run(
        [sys.executable, str(script_path), "--module", "P4_funcoes", "--concept", "4-funcao_inversa", "--tipo", "determinacao_analitica", "--no-preview", "--auto-approve", "--no-compile"],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        encoding='utf-8',
        timeout=60
    )

    assert result_base.returncode == 0, f"Base test generation failed: {result_base.stderr}"
    assert ".tex gerado:" in result_base.stdout, "Base LaTeX file generation not found"

    # Extract the generated file path from output
    match = re.search(r'\.tex gerado: ([^\n]+)', result_base.stdout)
    assert match, "Could not extract generated file path"
    base_file = match.group(1).strip()

    print(f"Base test generated: {base_file}")

    # Read the base file to understand its structure
    with open(base_file, 'r', encoding='utf-8') as f:
        base_content = f.read()

    # Count exercises in base test
    exercise_count = base_content.count('\\exercicio')
    print(f"Base test contains {exercise_count} exercises")

    # Generate a version with different exercises (using seed for different randomization)
    print("Generating version B with different exercises...")
    result_version = subprocess.run(
        [sys.executable, str(script_path), "--module", "P4_funcoes", "--concept", "4-funcao_inversa", "--tipo", "determinacao_analitica", "--no-preview", "--auto-approve", "--no-compile", "--seed", "12345"],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        encoding='utf-8',
        timeout=60
    )

    assert result_version.returncode == 0, f"Version test generation failed: {result_version.stderr}"
    assert ".tex gerado:" in result_version.stdout, "Version LaTeX file generation not found"

    # Extract version file path
    match_version = re.search(r'\.tex gerado: ([^\n]+)', result_version.stdout)
    assert match_version, "Could not extract version file path"
    version_file = match_version.group(1).strip()

    print(f"Version test generated: {version_file}")

    # Read version file
    with open(version_file, 'r', encoding='utf-8') as f:
        version_content = f.read()

    # Verify they are different
    assert base_content != version_content, "Generated versions should be different"

    # But should have same structure (same number of exercises)
    version_exercise_count = version_content.count('\\exercicio')
    assert exercise_count == version_exercise_count, f"Exercise count mismatch: {exercise_count} vs {version_exercise_count}"

    # Test compilation of version
    print("Testing compilation of version B...")
    result_compile = subprocess.run(
        [sys.executable, str(script_path), "--module", "P4_funcoes", "--concept", "4-funcao_inversa", "--tipo", "determinacao_analitica", "--no-preview", "--auto-approve", "--seed", "12345"],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        encoding='utf-8',
        timeout=180
    )

    assert result_compile.returncode == 0, f"Version compilation failed: {result_compile.stderr}"
    assert "PDF gerado:" in result_compile.stdout, "Version PDF compilation not found"

    print("✅ Exercise versioning test passed!")

    return base_file, version_file

if __name__ == "__main__":
    print("Testing exercise versioning functionality...")

    try:
        base_file, version_file = test_exercise_versioning()
        print(f"\n📄 Generated test versions:")
        print(f"   Base: {base_file}")
        print(f"   Version: {version_file}")
        print("\n🎉 Exercise versioning test passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)