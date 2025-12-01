# Sanitizer: remove emoji/symbol characters from files
import sys
import re
from pathlib import Path

# Unicode ranges commonly containing emoji/symbols
emoji_pattern = re.compile('[\U0001F300-\U0001F6FF\U0001F900-\U0001F9FF\U00002600-\U000027BF\U0000FE0F\U0001F1E6-\U0001F1FF]')

files = [
    Path(r"ExerciseDatabase\_tools\preview_system.py"),
    Path(r"SebentasDatabase\_tools\generate_sebentas.py")
]

for p in files:
    if not p.exists():
        print(f"Skipping missing file: {p}")
        continue
    txt = p.read_text(encoding='utf-8')
    new = emoji_pattern.sub('', txt)
    # Also remove miscellaneous box-drawing and heavy symbols that caused issues
    new = re.sub('[\u2500-\u257F\u2600-\u26FF\u2700-\u27BF]', '', new)
    if new != txt:
        p.write_text(new, encoding='utf-8')
        print(f"Sanitized emojis from: {p}")
    else:
        print(f"No emojis found in: {p}")
