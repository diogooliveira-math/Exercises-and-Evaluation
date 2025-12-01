import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ExerciseDatabase._tools.preview_system import PreviewManager, create_sebenta_preview
pm = PreviewManager(auto_open=False, consolidated_preview=True)
content = create_sebenta_preview('debug_sebenta','% teste latex \\\section*{Teste}',{'info':'teste'})
print('Calling show_and_confirm... (auto_open=False)')
res = pm.show_and_confirm(content, 'Debug Sebenta', show_preview=True)
print('show_and_confirm returned:', res)
