from pathlib import Path
import importlib.util
REPO = Path(__file__).resolve().parent.parent
gen_path = REPO / 'SebentasDatabase' / '_tools' / 'generate_tests.py'
spec = importlib.util.spec_from_file_location('genmod', str(gen_path))
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

index = gen.load_index(REPO / 'ExerciseDatabase' / 'index.json')
exercises = index.get('exercises', [])
disc='matematica'; mod='A8_modelos_discretos'; conc='1-sistemas_numericos'
config_path = gen.find_config(disc,mod,conc,None)
print('config_path=', config_path)
config = gen.load_config(config_path) if config_path else {}
filters={'discipline':disc,'module':mod,'concept':conc,'tipo':None}
pool=[]
for ex in exercises:
    if filters.get('discipline') and ex.get('discipline') != filters['discipline']:
        continue
    if filters.get('module') and ex.get('module') != filters['module']:
        continue
    if filters.get('concept') and ex.get('concept') != filters['concept']:
        continue
    pool.append(ex)
print('pool size:', len(pool))
print('sample ids:', [e.get('id') for e in pool[:10]])
import random
rng = random.Random(42)
selected = gen.select_by_config(exercises, config, filters, rng)
print('selected size:', len(selected))
print('selected ids:', [e.get('id') for e in selected[:10]])
print('selected paths sample:')
for e in selected[:10]:
    print(' -', e.get('path'))
