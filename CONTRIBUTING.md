# Contributing — Test-Driven Development (TDD) Guide

This repository follows a Test-Driven Development (TDD) workflow for changes to the core tooling in `ExerciseDatabase/_tools/`.

Short workflow
1. Create a small, focused unit test in `tests/unit/` that demonstrates the desired behaviour (it should fail initially).
2. Run the test locally: `python -m pytest -q tests/unit/test_name.py`.
3. Implement the minimal code required in `ExerciseDatabase/_tools/` to make the test pass.
4. Re-run tests, refactor code, keep tests green.
5. Commit on a feature branch and open a PR; CI must pass before merge.

Running tests

Run unit tests only:
```powershell
python -m pytest -q tests/unit
```

Run a single test during development:
```powershell
python -m pytest -q tests/unit/test_wizard_create_project.py
```

Run integration tests (explicit):
```powershell
$env:RUN_INTEGRATION = "1"
python -m pytest -q
```

Design notes
- Use `tmp_path` and `monkeypatch` in tests to avoid touching the real `ExerciseDatabase/` folders.
- Tests should mock external side-effects (opening editors, network, global system state).
- Keep unit tests fast; keep integration tests gated behind `RUN_INTEGRATION`.

Feature: Staging → Preview → Promote

- Staging writes new project work to `ExerciseDatabase/_staging/` and returns a `staged_id` and `staged_path`.
- Preview system shows a friendly summary and requires explicit confirmation.
- Promotion moves staged content into `ExerciseDatabase/projects/` and updates `ExerciseDatabase/index.json`.

CLI examples

Create & preview (interactive):
```powershell
python ExerciseDatabase/_tools/add_exercise_with_types.py --create-project
```

Create + auto-approve (admin/CI only):
```powershell
python ExerciseDatabase/_tools/add_exercise_with_types.py --create-project --auto-approve
```

New: non-interactive helper CLI
--------------------------------

To create research projects programmatically (staging) you can use the helper CLI `scripts/create_project_cli.py`.

Examples:

Create from inline fields and show interactive preview (default):
```powershell
python scripts/create_project_cli.py --title "My Project" --responsavel "Prof" --summary "Short"
```

Create from a JSON payload file (non-interactive preview):
```powershell
python scripts/create_project_cli.py --payload-file temp/payload.json --no-preview
```

Create and auto-promote (CI/admin):
```powershell
python scripts/create_project_cli.py --payload-file temp/payload.json --auto-approve
```

Notes:
- Use `--no-preview` in automation when you only want to stage the project and manually inspect later.
- `--auto-approve` will attempt to promote the staged project immediately; this moves files into `ExerciseDatabase/projects/` and updates `ExerciseDatabase/index.json`.
- The CLI is implemented to be robust when executed from the repository root.

Promote manually (dry-run):
```powershell
python ExerciseDatabase/_tools/promote_project_from_staging.py --staged-id STG_... --dry-run
```

Notes on auto-approve
- The `--auto-approve` flag should be used sparingly. Prefer interactive preview for human workflows.
- When `--auto-approve` is used, ensure logging of the action and that the account running the command is trusted.

If you have questions or need help, open an Issue referencing the feature and include the failing test and the intended behaviour.
