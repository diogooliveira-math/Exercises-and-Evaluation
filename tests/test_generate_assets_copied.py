import subprocess
from pathlib import Path
import sys


def test_assets_are_copied():
    # Generate .tex without compiling and auto-approve to skip preview
    cmd = [sys.executable, "SebentasDatabase/_tools/generate_tests.py", "--config", "SebentasDatabase/_tests_config/default_test_config.json", "--module", "P4_funcoes", "--concept", "4-funcao_inversa", "--no-compile", "--auto-approve"]
    subprocess.check_call(cmd)

    output_dir = Path("SebentasDatabase/matematica/P4_funcoes/4-funcao_inversa/tests")
    assert output_dir.exists(), "Output tests directory not created"
    assets_dir = output_dir / "assets" / "ExerciseDatabase" / "matematica" / "P4_funcoes" / "4-funcao_inversa"
    # Check for a known copied subvariant file
    found = any(assets_dir.rglob("subvariant_*.tex"))
    assert found, f"No subvariant_*.tex found under {assets_dir}"
