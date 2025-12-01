import sys
import os
from pathlib import Path

# Ensure workspace root is in sys.path so we can import local modules
sys.path.insert(0, os.getcwd())
from ExerciseDatabase._tools.preview_system import PreviewManager, create_exercise_preview

pm = PreviewManager(auto_open=False, consolidated_preview=True)
latex = "\\exercicio{Primeiro enunciado}\n\\subexercicio{Alínea a}\n\\subexercicio{Alínea b}\n\\exercicio{Segundo enunciado}\n\\subexercicio{Alínea c}"
content = create_exercise_preview('TEST_E', latex, {'id':'TEST_E'})

tmpdir = pm.create_temp_preview(content, 'Test numbering')
consolidated = next((p for p in pm.temp_files if 'PREVIEW_CONSOLIDADO' in p.name), None)
print('CONSOLIDATED PATH:', consolidated)
if consolidated and consolidated.exists():
    txt = consolidated.read_text(encoding='utf-8')
    print('\n----- START OF CONSOLIDATED (first 1200 chars) -----\n')
    print(txt[:1200])
    print('\n----- END PREVIEW -----\n')
else:
    print('No consolidated file produced')
