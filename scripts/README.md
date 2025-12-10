# Scripts

This folder contains lightweight helper scripts used by maintainers and CI.

`create_project_cli.py` — Non-interactive helper to stage research projects.

Basic usage:

Stage without preview (useful for automation):
```powershell
python scripts/create_project_cli.py --payload-file temp/payload.json --no-preview
```

Stage and open interactive preview:
```powershell
python scripts/create_project_cli.py --title "My Project" --responsavel "Author" --summary "Short"
```

Auto-promote (CI/admin):
```powershell
python scripts/create_project_cli.py --payload-file temp/payload.json --auto-approve
```

The script loads `ExerciseDatabase/_tools/add_exercise_with_types.py` and calls
`create_research_project(payload, auto_approve)`; it is intended to be executed from
the repository root.
