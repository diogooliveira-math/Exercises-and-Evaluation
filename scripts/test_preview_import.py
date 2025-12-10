import sys
from pathlib import Path

preview_tools = Path(__file__).resolve().parent.parent / 'ExerciseDatabase' / '_tools'
sys.path.insert(0, str(preview_tools))
print('inserted', preview_tools)
try:
    import preview_system
    print('import ok, PreviewManager:', hasattr(preview_system, 'PreviewManager'))
except Exception as e:
    print('import failed:', e)
