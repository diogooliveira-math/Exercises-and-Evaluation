"""Migration script to assign IPs to existing exercises."""
from pathlib import Path
import argparse
from ExerciseDatabase._tools.ip_registry import IPRegistry, register_from_fs

REPO_ROOT = Path(__file__).resolve().parent
EXERCISE_DB = REPO_ROOT / 'ExerciseDatabase'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--base', type=str, default=str(Path(__file__).resolve().parent.parent / 'ExerciseDatabase'))
    args = parser.parse_args()
    base = Path(args.base)
    reg = IPRegistry()
    if args.dry_run:
        mapping = register_from_fs(base)
        for ip, path in mapping.items():
            print(f"{ip} -> {path}")
        print(f"Assigned {len(mapping)} IPs (dry-run).")
    elif args.apply:
        mapping = register_from_fs(base)
        print(f"Assigned {len(mapping)} IPs and saved registry to {reg.path}")
    else:
        print('Specify --dry-run or --apply')

if __name__ == '__main__':
    main()
