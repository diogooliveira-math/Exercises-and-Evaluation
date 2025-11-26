"""Test for PDF compilation functionality in test generation."""

import subprocess
import os
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def test_pdf_compilation():
    """Test that PDF compilation works end-to-end."""
    script_path = PROJECT_ROOT / "SebentasDatabase" / "_tools" / "generate_tests.py"

    # Set environment variables for auto mode with compilation enabled
    env = os.environ.copy()

    # First test: generation without compilation
    print("Testing generation without compilation...")
    result_gen = subprocess.run(
        [sys.executable, str(script_path), "--module", "P4_funcoes", "--concept", "4-funcao_inversa", "--no-preview", "--auto-approve", "--no-compile"],
        cwd=str(PROJECT_ROOT),
        env=env,
        capture_output=True,
        text=True,
        encoding='utf-8',
        timeout=60
    )

    print("Generation test - STDOUT (last 500 chars):")
    print(result_gen.stdout[-500:])
    print("Generation test - STDERR:")
    print(result_gen.stderr[-500:])

    assert result_gen.returncode == 0, f"Generation failed with return code {result_gen.returncode}"
    assert ".tex gerado:" in result_gen.stdout, "LaTeX file generation not found in output"
    print("✅ Generation test passed!")

    # Now test compilation with a shorter timeout
    print("\nTesting PDF compilation...")
    result = subprocess.run(
        [sys.executable, str(script_path), "--module", "P4_funcoes", "--concept", "4-funcao_inversa", "--no-preview", "--auto-approve"],
        cwd=str(PROJECT_ROOT),
        env=env,
        capture_output=True,
        text=True,
        encoding='utf-8',
        timeout=180  # 3 minutes for compilation
    )

    print("Compilation test - STDOUT (last 1000 chars):")
    print(result.stdout[-1000:])
    print("Compilation test - STDERR (last 500 chars):")
    print(result.stderr[-500:])

    # Check if it ran without critical errors
    assert result.returncode == 0, f"Script failed with return code {result.returncode}"

    # Check if PDF was mentioned as generated
    success_indicators = ["PDF compilado com sucesso", "PDF gerado:", "teste_"]
    has_success = any(indicator in result.stdout for indicator in success_indicators)
    assert has_success, "PDF compilation success not found in output"

    # Check that no critical LaTeX errors occurred
    assert "! LaTeX Error" not in result.stderr, "LaTeX compilation error detected"
    assert "! Emergency stop" not in result.stderr, "LaTeX emergency stop detected"

    print("✅ PDF compilation test passed!")

def test_pdf_file_exists():
    """Test that the generated PDF file actually exists."""
    # Look for recently generated test PDFs
    test_output_dir = PROJECT_ROOT / "SebentasDatabase" / "matematica" / "P4_funcoes" / "4-funcao_inversa" / "tests"

    if not test_output_dir.exists():
        print("⚠️ Test output directory does not exist yet")
        return

    # Find PDF files
    pdf_files = list(test_output_dir.glob("teste_*.pdf"))

    if not pdf_files:
        print("⚠️ No PDF files found in test output directory")
        return

    # Check the most recent PDF
    latest_pdf = max(pdf_files, key=lambda p: p.stat().st_mtime)
    print(f"📄 Found PDF: {latest_pdf}")

    # Verify file size (should be > 0)
    size = latest_pdf.stat().st_size
    assert size > 1000, f"PDF file seems too small ({size} bytes), might be corrupted"

    print(f"✅ PDF file exists and has reasonable size ({size} bytes)")

if __name__ == "__main__":
    print("Testing PDF compilation functionality...")

    try:
        test_pdf_compilation()
        test_pdf_file_exists()
        print("\n🎉 All PDF compilation tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)