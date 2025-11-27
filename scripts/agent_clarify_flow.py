#!/usr/bin/env python3
"""
Agent helper: process 'needs_clarification' JSON and decide to accept suggestions or ask for clarification.
Usage:
  python scripts/agent_clarify_flow.py --input-file=needs.json [--threshold=0.6]

Outputs JSON to stdout with keys:
 - status: 'accept' or 'clarify'
 - command: (if accept) the wrapper command to run
 - question: (if clarify) the natural language question to the user
"""
import argparse
import json
import shlex
import sys
from pathlib import Path


def build_command(parsed, suggestions):
    # Merge parsed and suggestions (suggestions override missing)
    payload = parsed.copy()
    for k, v in suggestions.items():
        if k not in payload or not payload.get(k):
            payload[k] = v
    # Ensure required fields
    req = ['discipline','module','concept','tipo','difficulty','statement']
    for r in req:
        payload.setdefault(r, '')
    # Escape single quotes in statement
    stmt = payload['statement'].replace("'", "\\'")
    kv = f"discipline={payload['discipline']}, module={payload['module']}, concept={payload['concept']}, tipo={payload['tipo']}, difficulty={payload['difficulty']}, statement='{stmt}'"
    # Prefer the current Python executable to avoid depending on a literal 'python' in PATH
    python_exec = shlex.quote(sys.executable)
    cmd = f"{python_exec} scripts/run_add_exercise.py \"{kv}\""
    return cmd


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input-file', type=Path, help='JSON file with needs_clarification output')
    p.add_argument('--threshold', type=float, default=0.6, help='confidence threshold to auto-accept')
    args = p.parse_args()

    if not args.input_file or not args.input_file.exists():
        print(json.dumps({'status':'error','message':'input-file missing or not found'}))
        return 2

    data = json.loads(args.input_file.read_text(encoding='utf-8'))
    status = data.get('status')
    if status != 'needs_clarification':
        print(json.dumps({'status':'error','message':'input JSON not needs_clarification'}))
        return 2

    missing = data.get('missing', [])
    applied = data.get('applied', {})  # may contain confidences
    suggestions = data.get('suggestions', {})
    parsed = data.get('parsed', {})

    # Decide whether to accept: all missing fields must have applied confidences >= threshold
    th = args.threshold
    can_accept = True
    for m in missing:
        if m in applied and isinstance(applied[m], dict) and 'confidence' in applied[m]:
            if applied[m]['confidence'] < th:
                can_accept = False
                break
        else:
            # no confidence info => cannot accept
            can_accept = False
            break

    if can_accept:
        cmd = build_command(parsed, {m: applied[m]['value'] for m in missing})
        out = {'status':'accept','command':cmd,'accepted':{m:applied[m] for m in missing}}
        print(json.dumps(out, ensure_ascii=False))
        return 0
    else:
        # Build a clarification question showing suggestions (if any)
        parts = []
        for m in missing:
            sug = None
            if m in applied and isinstance(applied[m], dict):
                sug = applied[m]['value']
            elif m in suggestions:
                sug = suggestions[m]
            parts.append(f"{m}: sugestão -> {sug if sug else '<sem sugestão>'}")
        question = "Parece que faltam campos para criar o exercício: " + "; ".join(parts) + ". Aceita estas sugestões? (S/N)"
        out = {'status':'clarify','question':question,'suggestions':suggestions,'missing':missing}
        print(json.dumps(out, ensure_ascii=False))
        return 0

if __name__ == '__main__':
    raise SystemExit(main())
