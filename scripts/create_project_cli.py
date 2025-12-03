#!/usr/bin/env python3
"""CLI helper to create a research project (staging) non-interactively.

Usage examples:
  # From a JSON payload file
  python scripts/create_project_cli.py --payload-file temp/payload.json

  # Inline args
  python scripts/create_project_cli.py --title "My Project" --responsavel "Prof" --summary "Short" --auto-approve

This script calls `create_research_project(payload, auto_approve)` from
`ExerciseDatabase._tools.add_exercise_with_types` and prints the result JSON.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

# Ensure project root is on sys.path so package imports work when running the script
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main():
    parser = argparse.ArgumentParser(description="Create research project (staging) non-interactively")
    parser.add_argument('--payload-file', help='Path to JSON payload file', type=str)
    parser.add_argument('--title', help='Project title', type=str)
    parser.add_argument('--responsavel', help='Responsible person', type=str)
    parser.add_argument('--summary', help='Short summary', type=str)
    parser.add_argument('--discipline', help='Discipline', type=str, default='')
    parser.add_argument('--module', help='Module', type=str, default='')
    parser.add_argument('--concept', help='Concept', type=str, default='')
    parser.add_argument('--tags', help='Comma-separated tags', type=str, default='')
    parser.add_argument('--auto-approve', help='Promote immediately after staging', action='store_true')
    parser.add_argument('--no-preview', help='Do not open interactive preview (just stage)', action='store_true')

    args = parser.parse_args()

    payload = None
    if args.payload_file:
        p = Path(args.payload_file)
        if not p.exists():
            print(json.dumps({'status': 'error', 'message': f'Payload file not found: {p}'}))
            sys.exit(2)
        with open(p, 'r', encoding='utf-8') as f:
            payload = json.load(f)
    else:
        # Build payload from args; only include provided fields
        payload = {}
        if args.title:
            payload['title'] = args.title
        if args.responsavel:
            payload['responsavel'] = args.responsavel
        if args.summary:
            payload['summary'] = args.summary
        if args.discipline:
            payload['discipline'] = args.discipline
        if args.module:
            payload['module'] = args.module
        if args.concept:
            payload['concepts'] = [args.concept]
        if args.tags:
            payload['tags'] = [t.strip() for t in args.tags.split(',') if t.strip()]

    # Ensure we have at least a title to avoid immediate failure
    if not payload.get('title') and not payload.get('titulo'):
        print(json.dumps({'status': 'error', 'message': 'Missing project title (use --title or --payload-file)'}))
        sys.exit(3)

    # Import the helper function by loading the module file directly (robust across exec contexts)
    try:
        import importlib.util
        mod_path = Path(PROJECT_ROOT) / 'ExerciseDatabase' / '_tools' / 'add_exercise_with_types.py'
        if not mod_path.exists():
            raise FileNotFoundError(f"Module file not found: {mod_path}")
        # Ensure _tools directory is on sys.path so module-local imports like
        # `from preview_system import ...` work when executing the file directly.
        tools_dir = str(mod_path.parent)
        if tools_dir not in sys.path:
            sys.path.insert(0, tools_dir)

        spec = importlib.util.spec_from_file_location('add_exercise_with_types', str(mod_path))
        module = importlib.util.module_from_spec(spec)
        loader = spec.loader
        assert loader is not None
        loader.exec_module(module)
        create_research_project = getattr(module, 'create_research_project')
    except Exception as e:
        print(json.dumps({'status': 'error', 'message': f'Could not load create_research_project: {e}'}))
        sys.exit(4)

    # If user wants no preview, stage directly via add_exercise_safe.make_staged_project
    if args.no_preview:
        try:
            # Load add_exercise_safe from _tools
            import importlib.util
            safe_path = Path(PROJECT_ROOT) / 'ExerciseDatabase' / '_tools' / 'add_exercise_safe.py'
            if not safe_path.exists():
                raise FileNotFoundError(f"Module file not found: {safe_path}")
            spec2 = importlib.util.spec_from_file_location('add_exercise_safe', str(safe_path))
            mod2 = importlib.util.module_from_spec(spec2)
            loader2 = spec2.loader
            assert loader2 is not None
            loader2.exec_module(mod2)
            make_staged_project = getattr(mod2, 'make_staged_project')
        except Exception as e:
            print(json.dumps({'status': 'error', 'message': f'Could not load make_staged_project: {e}'}))
            sys.exit(6)

        try:
            meta = make_staged_project(payload)
            print(json.dumps({'status': 'ok', 'staged': meta}, ensure_ascii=False, indent=2))
            return 0
        except Exception as e:
            print(json.dumps({'status': 'error', 'message': str(e)}))
            return 7

    # Call the function (interactive preview will be shown unless create_research_project handles auto_approve)
    try:
        res = create_research_project(payload=payload, auto_approve=bool(args.auto_approve))
        print(json.dumps({'status': 'ok', 'result': res}, ensure_ascii=False, indent=2))
        return 0
    except Exception as e:
        print(json.dumps({'status': 'error', 'message': str(e)}))
        return 5


if __name__ == '__main__':
    raise SystemExit(main())
