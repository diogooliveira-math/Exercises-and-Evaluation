from pathlib import Path
import sys

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / 'SebentasDatabase' / '_tools'))
sys.path.insert(0, str(REPO / 'ExerciseDatabase' / '_tools'))

import importlib.util
gen_path = REPO / 'SebentasDatabase' / '_tools' / 'generate_tests.py'
spec = importlib.util.spec_from_file_location('sebenta_generate_tests', str(gen_path))
gen_mod = importlib.util.module_from_spec(spec)
try:
     spec.loader.exec_module(gen_mod)
     load_index = gen_mod.load_index
     select_by_config = gen_mod.select_by_config
     build_test_content = gen_mod.build_test_content
except Exception as e:
     print('Failed to load SebentasDatabase/_tools/generate_tests.py:', e)
     raise

try:
    from preview_system import PreviewManager, create_test_preview
except Exception as e:
    print('Failed to import preview_system:', e)
    raise

# Load index and select exercises for A8 module / 1-sistemas_numericos concept
index = load_index(REPO / 'ExerciseDatabase' / 'index.json')
exercises = index.get('exercises', [])

filters = {
    'discipline': 'matematica',
    'module': 'A8_modelos_discretos',
    'concept': '1-sistemas_numericos',
    'tipo': None,
}

import random
rng = random.Random(42)
selected = select_by_config(exercises, {}, filters, rng)
if not selected:
    print('No exercises selected for A8; abort')
    sys.exit(2)

content, assets = build_test_content(selected, REPO, {})

# Create preview content
preview_content = create_test_preview('A8_preview', content, selected, {})
pm = PreviewManager(auto_open=False, consolidated_preview=True)

preview_dir = pm.create_temp_preview(preview_content, 'A8 Preview')
print('PREVIEW_DIR:', preview_dir)
print('Files:')
for p in sorted(preview_dir.rglob('*')):
    print(' -', p.relative_to(preview_dir))

# Keep the preview dir path written to repo temp for convenience
out_file = REPO / 'temp' / 'last_preview_dir_direct.txt'
out_file.parent.mkdir(parents=True, exist_ok=True)
out_file.write_text(str(preview_dir), encoding='utf-8')
print('Wrote', out_file)
