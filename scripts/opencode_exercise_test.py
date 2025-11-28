#!/usr/bin/env python3
"""
Simple test script that invokes the local `opencode` CLI to run the
`exercise-creator` agent with a prompt asking it to create a minimal
exercise inside an isolated temporary folder under this repository's
`temp/` directory. The script then attempts to delete the created folder
to leave the repo clean.

Important safety notes:
- This script DOES NOT run automatically. It is a helper that the user can
  execute manually. The agent may write files when `opencode` runs, so run
  with care and review outputs before reusing in CI.
- The script will silently skip if the `opencode` CLI executable is not
  found in `PATH`.

Usage (PowerShell):
    python scripts\opencode_exercise_test.py

The script prints progress and any stdout/stderr captured from the CLI.
"""
from __future__ import annotations

import shutil
import subprocess
import time
from pathlib import Path
from typing import Optional


def run_test(timeout: int = 120) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    timestamp = int(time.time())
    temp_dir = repo_root / "temp" / f"opencode_test_exercise_{timestamp}"
    temp_dir.mkdir(parents=True, exist_ok=False)

    # Build a prompt that asks the agent to create two files inside the folder:
    # - exercise.tex (minimal LaTeX using \exercicio{})
    # - metadata.json (simple index metadata)
    # The prompt instructs the agent not to modify any other files.
    prompt = (
        f"Create a minimal LaTeX exercise in the exact folder: {temp_dir!s}. "
        "Create two files: 'exercise.tex' with a short exercise using the macro \\exercicio{}, "
        "and 'metadata.json' with minimal metadata (id, title, difficulty). "
        "DO NOT modify any other files in the repository or commit anything. "
        "When finished print a single line starting with 'CREATED:' followed by the absolute path to the created folder."
    )

    cmd = ["opencode", "--agent", "exercise-creator", "run", prompt]

    try:
        print("Running opencode agent (this requires `opencode` in PATH)...")
        completed = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout,
        )

        print("--- CLI output start ---")
        print(completed.stdout)
        print("--- CLI output end ---")

        # Try to detect a CREATED: line from the agent output
        created_path: Optional[Path] = None
        for line in (completed.stdout or "").splitlines():
            if line.startswith("CREATED:"):
                maybe = line.split("CREATED:", 1)[1].strip()
                try:
                    p = Path(maybe)
                    if p.exists():
                        created_path = p
                        break
                except Exception:
                    pass

        # Determine where to look for the two files
        check_dir = created_path if created_path is not None else temp_dir
        exercise_file = check_dir / "exercise.tex"
        metadata_file = check_dir / "metadata.json"

        if exercise_file.exists() and metadata_file.exists():
            print(f"Found created files in {check_dir!s}")
        else:
            print("Created files not found. Check CLI output above for details.")

    except FileNotFoundError:
        print("`opencode` CLI not found in PATH. Skipping run.")
    except subprocess.TimeoutExpired:
        print("`opencode` process timed out.")
    finally:
        # Cleanup: remove the temporary directory if it still exists
        if temp_dir.exists():
            try:
                shutil.rmtree(temp_dir)
                print(f"Removed temporary folder {temp_dir}")
            except Exception as e:
                print(f"Failed to remove temporary folder {temp_dir}: {e}")


if __name__ == "__main__":
    run_test()
