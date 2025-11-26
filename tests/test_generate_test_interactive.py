"""Test for generate_test_interactive.py to validate basic functionality."""

import subprocess
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def test_generate_test_interactive_help():
    """Test that the script shows help correctly."""
    script_path = PROJECT_ROOT / "scripts" / "generate_test_interactive.py"

    # Run with --help
    result = subprocess.run(
        [sys.executable, str(script_path), "--help"],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        timeout=10
    )

    print("STDOUT:")
    print(result.stdout)
    print("STDERR:")
    print(result.stderr)
    print(f"Return code: {result.returncode}")

    # Check if help was shown
    assert result.returncode == 0, f"Script failed with return code {result.returncode}"
    assert "usage:" in result.stdout, "Help message not found in output"
    assert "generate_test_interactive.py" in result.stdout, "Script name not in help"

    print("✅ Help test passed!")

if __name__ == "__main__":
    print("Testing generate_test_interactive.py...")

    try:
        test_generate_test_interactive_help()
        print("\n🎉 All tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)