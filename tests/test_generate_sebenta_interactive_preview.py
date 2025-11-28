"""
Simple test for generate_sebenta_interactive.py to validate preview functionality.

This test checks if the script asks for preview options in interactive mode.
"""
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def test_interactive_asks_for_preview():
    """Test that interactive mode asks for preview and compile options."""
    script_path = PROJECT_ROOT / "scripts" / "generate_sebenta_interactive.py"

    # Provide inputs to go through the menus and check if preview question appears
    # Inputs: matematica (1), P4_funcoes (1), 4-funcao_inversa (1), skip tipo (0), yes preview (s), yes compile (s), yes continue (s)
    inputs = "1\n1\n1\n0\ns\ns\ns\n"

    proc = subprocess.run(
        [sys.executable, str(script_path)],
        input=inputs,
        text=True,
        capture_output=True,
        cwd=str(PROJECT_ROOT)
    )

    stdout = proc.stdout
    stderr = proc.stderr

    # Check that the script asked for preview
    assert "Deseja pré-visualização" in stdout, f"Preview question not found in output: {stdout}"
    assert "Deseja compilar PDF" in stdout, f"Compile question not found in output: {stdout}"

    # Should succeed
    assert proc.returncode == 0, f"Script failed: {stderr}"

    print("Test passed: Interactive mode asks for preview and compile options")


def test_auto_mode_does_not_ask():
    """Test that auto mode does not ask for preview."""
    script_path = PROJECT_ROOT / "scripts" / "generate_sebenta_interactive.py"

    # Set auto mode
    import os
    env = os.environ.copy()
    env["SEBENTA_AUTO_CHOICES"] = "matematica,P4_funcoes,4-funcao_inversa,"

    proc = subprocess.run(
        [sys.executable, str(script_path)],
        text=True,
        capture_output=True,
        cwd=str(PROJECT_ROOT),
        env=env
    )

    stdout = proc.stdout

    # Should not ask for preview in auto mode
    assert "Deseja pré-visualização" not in stdout, f"Should not ask for preview in auto mode: {stdout}"
    assert "Auto-mode enabled" in stdout, f"Auto mode message not found: {stdout}"

    print("✅ Test passed: Auto mode does not ask for preview")

if __name__ == "__main__":
    test_interactive_asks_for_preview()
    test_auto_mode_does_not_ask()
    print("🎉 All tests passed!")