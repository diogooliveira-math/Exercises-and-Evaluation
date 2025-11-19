"""
Insert \FloatBarrier after \end{figure} in .tex files under ExerciseDatabase

Behavior:
- Walks the ExerciseDatabase directory tree.
- For each `.tex` file, finds occurrences of `\end{figure}`.
- If the next non-empty line after `\end{figure}` is not `\FloatBarrier`, inserts `\FloatBarrier` on the next line.
- Makes a backup copy of the original file with `.bak` appended (only if changed).
- Prints a summary of modified files.

Run from project root with the repo's Python environment.
"""
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
EX_DIR = ROOT

FIG_END_RE = re.compile(r"(\\end\{figure\})(\s*)", re.MULTILINE)

modified = []

for tex in EX_DIR.rglob("*.tex"):
    # skip directories that shouldn't be touched
    if any(part.startswith(".") for part in tex.parts):
        continue
    text = tex.read_text(encoding="utf-8")
    new_text = text

    # We'll iterate matches from end to start to preserve offsets while replacing
    matches = list(FIG_END_RE.finditer(text))
    if not matches:
        continue

    offset = 0
    for m in reversed(matches):
        end_pos = m.end()
        # Get following text starting at end_pos
        following = text[end_pos: end_pos + 200]  # peek a short window
        # If \FloatBarrier already present soon after, skip
        if re.search(r"\\FloatBarrier", following):
            continue
        # Insert \FloatBarrier after the matched \end{figure}
        insert_at = end_pos + offset
        new_text = new_text[:insert_at] + "\\n\\FloatBarrier\\n" + new_text[insert_at:]
        offset += len("\\n\\FloatBarrier\\n")

    if new_text != text:
        bak = tex.with_suffix(tex.suffix + ".bak")
        tex.write_text(new_text, encoding="utf-8")
        # write backup only if doesn't exist
        if not bak.exists():
            bak.write_text(text, encoding="utf-8")
        modified.append(str(tex.relative_to(ROOT)))

print(f"Modified {len(modified)} files:")
for p in modified:
    print(" - ", p)
