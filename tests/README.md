Quick validation tests
======================

This folder contains a small non-destructive validation script used to
check that key files and generator scripts exist and respond to `--help`.

Run from the repository root (PowerShell):

```powershell
python tests/quick_validation.py
```

Exit codes:
- `0` — all checks passed
- `2` — missing critical files or problems detected
