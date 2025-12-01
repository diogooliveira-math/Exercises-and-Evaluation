import shutil, datetime, pathlib, sys
root = pathlib.Path('temp/opencode_logs/send_prompt')
if not root.exists():
    print('No send_prompt logs found at', root)
    sys.exit(0)
arch_root = pathlib.Path('temp/opencode_logs/archive')
arch = arch_root / datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
arch.mkdir(parents=True, exist_ok=True)
items = list(root.glob('*'))
count=0
for p in items:
    try:
        shutil.move(str(p), str(arch))
        count += 1
    except Exception as e:
        print('Failed to move', p, '->', e)
print(f'Moved {count} items from {root} to {arch}')
