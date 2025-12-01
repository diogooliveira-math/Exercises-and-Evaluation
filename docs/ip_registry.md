IP Registry — Hierarchical Exercise Identifiers

Overview
- Every exercise now has a stable hierarchical IP in the format: `D.M.C.T.E` (discipline.module.concept.type.exercise).
- Example: `1.2.3.4.5` maps to a concrete exercise under `ExerciseDatabase/discipline/module/concept/type/exercise`.
- The registry is authoritative and stored at `ExerciseDatabase/_registry/ip_registry.json`.

Goals
- Stable IDs: assigned once and never reassigned to existing items.
- Deterministic migration: migration assigns IDs in a predictable order (sorted traversal).
- Fast resolution: registry provides IP → path + metadata lookups.
- Resilience: per-exercise `exercise.json` and per-concept `_meta.json` are written for faster repair and offline checks.

Key scripts & modules
- `ExerciseDatabase/_tools/ip_registry.py`
  - Core API: `register_path(parts, exercise_relpath, label)` assigns IDs and returns the full IP.
  - Atomic write + locking. Writes `exercise.json` next to the exercise directory when present.
- `ExerciseDatabase/_tools/ip_resolver.py`
  - High-level resolver that returns absolute exercise `Path` from IP strings.
- `scripts/migrate_ips.py`
  - `--dry-run` to preview assigned IPs.
  - `--apply` to write the registry.
- `scripts/registry_repair.py`
  - `--rebuild` rebuilds registry from filesystem (sorted deterministic order).
  - `--from-exercise-json` rebuilds using existing `exercise.json` files.
- `scripts/ip_lookup.py` — CLI to lookup IP(s).
- `scripts/check_registry_consistency.py` — validates registry vs files.
- `scripts/registry_snapshot.py` — creates zip snapshots of registry and metadata.
- `scripts/run_ip_registry_smoketest.py` — basic smoke test (no pytest required)

Integration with generator
- Wrapper: `scripts/run_generate_sebenta_task.py` accepts env var `SEBENTA_IPS` (comma-separated).
  - The wrapper resolves IPs to exercise paths and invokes generator with `--exercise-path` arguments.
- Generator: `SebentasDatabase/_tools/generate_sebentas.py`
  - Accepts `--ips` and `--exercise-path` CLI args.
  - Can generate a sebenta from IPs directly when resolved to exercise paths.

Developer notes
- Locking: the registry prefers `filelock` if installed; otherwise a simple lock file fallback is used.
- Atomic saves use a `*.tmp` write + `os.fsync` + `os.replace`.
- Backups: `save()` makes timestamped `.bak_` files. Migration and repair scripts create backups when requested.

Recommended developer workflow
1. To preview what migration would do:
   - `python scripts/migrate_ips.py --dry-run --base ExerciseDatabase`
2. To apply migration:
   - `python scripts/migrate_ips.py --apply --base ExerciseDatabase`
3. To generate a sebenta by IPs (non-interactive):
   - `SEBENTA_IPS="1.2.3.4.5,1.2.3.4.6" SEBENTA_NO_PREVIEW=1 SEBENTA_AUTO_APPROVE=1 python scripts/run_generate_sebenta_task.py`
4. To lookup an IP:
   - `python scripts/ip_lookup.py 1.2.3.4.5`
5. To check registry consistency:
   - `python scripts/check_registry_consistency.py`
6. To repair the registry (back it up first):
   - `python scripts/registry_repair.py --rebuild --backup`

CI and protections
- A GitHub Actions workflow was added: `.github/workflows/ip_registry.yml`.
  - Installs `filelock` and `pytest`.
  - Runs `scripts/check_registry_consistency.py` and the registry tests.
- Best practice: do not edit `ExerciseDatabase/_registry/ip_registry.json` manually.
  - Use `scripts/migrate_ips.py` or `scripts/registry_repair.py` to change the registry.

Troubleshooting
- If an IP lookup returns no path, run `scripts/check_registry_consistency.py` and `scripts/registry_repair.py --rebuild`.
- If you see locking timeouts, ensure no other process has a stale `.lock` file and try again. Prefer installing `filelock`.

Contact
- For agent integration details, see `agents_manifestos/ip_registry_agents.md`.
