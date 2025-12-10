from pathlib import Path
import difflib
import sys

def main(ref, gen):
    ref = Path(ref)
    gen = Path(gen)
    if not ref.exists():
        print('REF MISSING', ref)
        return 2
    if not gen.exists():
        print('GEN MISSING', gen)
        return 3
    ref_text = ref.read_text(encoding='utf-8').splitlines()
    gen_text = gen.read_text(encoding='utf-8').splitlines()
    diff = list(difflib.unified_diff(ref_text, gen_text, fromfile=str(ref), tofile=str(gen), lineterm=''))
    meaningful = [ln for ln in diff if ln.strip() and not ln.startswith('---') and not ln.startswith('+++')]
    print(f'meaningful diff lines: {len(meaningful)}')
    print('\n'.join(diff))
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1], sys.argv[2]))
