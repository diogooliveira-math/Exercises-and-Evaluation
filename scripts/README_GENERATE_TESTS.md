Generate Test wrapper

This repository includes an interactive wrapper `scripts/run_generate_test_task.py` that calls the internal generator `SebentasDatabase/_tools/generate_tests.py`.

Key behavior (updated):

- The wrapper forwards the following environment variables to the generator as CLI flags (first value when multiple): `TEST_DISCIPLINE` → `--discipline`, `TEST_MODULE` → `--module`, `TEST_CONCEPT` → `--concept`, `TEST_TIPO` → `--tipo`.
- Exercise IDs are forwarded via the environment variable `TEST_SELECTED_EXERCISES` (set from `TEST_EXERCISE_IDS`).
- Boolean flags supported and forwarded: `TEST_NO_PREVIEW` → `--no-preview`, `TEST_NO_COMPILE` → `--no-compile`, `TEST_AUTO_APPROVE` → `--auto-approve`.
- The generator now supports running across all (discipline/module/concept) combos found in `ExerciseDatabase/index.json` when no filters are provided. The wrapper no longer requires filters to be set.

Quick test (PowerShell):

```powershell
# non-interactive: iterate all combos but do not compile PDFs
$env:TEST_NO_COMPILE = '1'
$env:TEST_NO_PREVIEW = '1'
$env:TEST_AUTO_APPROVE = '1'
python scripts/run_generate_test_task.py
```

For interactive use, run `python scripts/generate_test_interactive.py` or use the VS Code task `📝 Gerar Teste (Interativo)`.
