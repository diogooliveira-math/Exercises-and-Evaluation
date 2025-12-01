from pathlib import Path
import json
root=Path('ExerciseDatabase')
paths=list(root.rglob('*.tex'))
if Path('SebentasDatabase/debug').exists():
    paths += list(Path('SebentasDatabase/debug').rglob('*.tex'))
probs=[]
problem_chars = set(['ℝ','∞','⇒','→','←','≠','∈','⁻','¹','₂','₁','₃','⁻¹','✓','…'])
for p in paths:
    try:
        s=p.read_text(encoding='utf-8')
    except Exception as e:
        probs.append((str(p),'read_error',str(e)))
        continue
    issues=[]
    if s.count('{')!=s.count('}'):
        issues.append("unbalanced_braces:{"+str(s.count('{'))+" vs }:"+str(s.count('}')) )
    if s.count('$')%2==1:
        issues.append(f"odd_dollar_count:{s.count('$')}")
    found=[ch for ch in problem_chars if ch in s]
    if found:
        issues.append('unicode:'+','.join(sorted(found)))
    if '\\n' in s:
        issues.append('literal_backslash_n')
    if '\\\\frac' in s or '\\\\item' in s:
        issues.append('double-escaped-commands')
    if issues:
        probs.append((str(p),issues))
print(json.dumps({'checked':len(paths),'problems':probs},ensure_ascii=False,indent=2))
