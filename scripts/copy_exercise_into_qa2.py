"""Helper: copy reference QA2 and a specific ExerciseDatabase exercise into an output QA2 folder.

Usage:
  python scripts/copy_exercise_into_qa2.py \
    --exercise matematica/P4_funcoes/4-funcao_inversa/determinacao_analitica/MAT_P4FUNCOE_4FX_DAX_003 \
    --output SebentasDatabase/tests/agent_run_full3
"""
from pathlib import Path
import argparse
import shutil
import os

ROOT = Path(__file__).resolve().parents[1]
EXDB = ROOT / 'ExerciseDatabase'
REF_QA2 = ROOT / 'reference' / 'QA2'

parser = argparse.ArgumentParser()
parser.add_argument('--exercise', required=True, help='path relative to ExerciseDatabase, e.g. matematica/.../MAT_...')
parser.add_argument('--output', required=True, help='output root (will create <output>/QA2)')
args = parser.parse_args()

exercise_rel = Path(args.exercise)
exercise_src = EXDB / exercise_rel
output_root = Path(args.output)
qa2_dst = output_root / 'QA2'

if not exercise_src.exists():
    print(f'ERROR: exercise source not found: {exercise_src}')
    raise SystemExit(1)

# copy reference QA2 if present, otherwise create minimal structure
if REF_QA2.exists():
    if qa2_dst.exists():
        shutil.rmtree(qa2_dst)
    shutil.copytree(REF_QA2, qa2_dst)
    print(f'Copied reference QA2 -> {qa2_dst}')
else:
    qa2_dst.mkdir(parents=True, exist_ok=True)
    (qa2_dst / 'tex').mkdir(parents=True, exist_ok=True)
    print(f'Created minimal QA2 structure at {qa2_dst}')

# prepare external_exercises location
external_root = qa2_dst / 'external_exercises'
(external_root / exercise_rel.parent).mkdir(parents=True, exist_ok=True)
# destination path
dest = external_root / exercise_rel
if dest.exists():
    shutil.rmtree(dest)
shutil.copytree(exercise_src, dest)
print(f'Copied exercise {exercise_src} -> {dest}')

# Update QA2/tex/exercises.tex: insert an input-path and IncludeExercise entry for the copied exercise
tex_dir = qa2_dst / 'tex'
exercises_file = tex_dir / 'exercises.tex'
if not exercises_file.exists():
    exercises_file.write_text('% Generated exercises.tex\n', encoding='utf-8')

# compute relative path from QA2/tex to external_exercises dest
rel_from_tex = os.path.relpath(dest, tex_dir)
# Build include block
block = []
block.append('\n% Added by copy_exercise_into_qa2.py')
block.append('\\makeatletter')
block.append(f"\\def\\input@path{{{{{rel_from_tex}/}}}}")
block.append('\\makeatother')
# If main.tex exists reference main, else reference folder
from pathlib import Path as _P
rel_posix = _P(rel_from_tex).as_posix()
if (dest / 'main.tex').exists():
    include_ref = f"{rel_posix}/main"
else:
    include_ref = rel_posix
block.append(f"\\IncludeExercise{{{include_ref}}}")

with exercises_file.open('a', encoding='utf-8') as f:
    f.write('\n'.join(block) + '\n')

print(f'Updated {exercises_file} with include for {include_ref}')

print('DONE')
