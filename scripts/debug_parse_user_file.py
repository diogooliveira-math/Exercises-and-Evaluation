from pathlib import Path
import importlib.util
import json

# Load module from tools
tools_dir = Path(__file__).resolve().parent.parent / "ExerciseDatabase" / "_tools"
aet_path = tools_dir / "add_exercise_template.py"
spec = importlib.util.spec_from_file_location("aet", str(aet_path))
aet = importlib.util.module_from_spec(spec)
spec.loader.exec_module(aet)

base = Path(__file__).resolve().parent.parent / 'ExerciseDatabase'
file_to_check = base / 'matematica' / 'P2_estatistica' / '2-Variabilidade' / 'escolha_m_variabilidade' / 'MAT_P2ESTATI_VARI_EM_001.tex'

print('File exists:', file_to_check.exists())
print('Path:', file_to_check)
print('--- RAW CONTENT ---')
print(file_to_check.read_text(encoding='utf-8'))

template = aet.ExerciseTemplate(base)
# Assign the existing file as temp_file
template.temp_file = file_to_check

success, data, errors = template.parse_template()

print('\n--- PARSE RESULT ---')
print('Success:', success)
print('Errors:', errors)
print('Data keys:', list(data.keys()))
print('Conteudo (raw):')
print(data.get('conteudo'))

# Show extracted subexercicios
print('\nSubexercicios:', data.get('subexercicios'))

# Show cleaned content inside \exercicio{...}
if data.get('conteudo'):
    import re
    m = re.search(r'\\exercicio\{(.*?)\}', data['conteudo'], flags=re.DOTALL)
    if m:
        inner = m.group(1)
        print('\nInner content of \exercicio{...}:')
        print(inner)
    else:
        print('No inner match')

# Dump JSON for further inspection
print('\nJSON DUMP:')
print(json.dumps({'success': success, 'errors': errors, 'data': data}, ensure_ascii=False, indent=2))
