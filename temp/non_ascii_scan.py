import pathlib

p = pathlib.Path('.')
report = []

for f in p.rglob('*'):
    if not f.is_file():
        continue
    if '.git' in f.parts:
        continue
    try:
        text = f.read_text(encoding='utf-8')
    except Exception:
        continue
    lines = []
    for i, line in enumerate(text.splitlines(), start=1):
        if any(ord(ch) > 127 for ch in line):
            lines.append((i, line))
    if lines:
        report.append(f'FILE: {f}')
        for i, line in lines[:20]:
            report.append(f'  {i}: {line}')
        if len(lines) > 20:
            report.append(f'  ... and {len(lines)-20} more lines')
        report.append('')

outdir = pathlib.Path('temp')
outdir.mkdir(exist_ok=True)
report_path = outdir / 'non_ascii_report.txt'
if not report:
    report = ['NO_NON_ASCII_FOUND']
report_path.write_text('\n'.join(report), encoding='utf-8')
print(f'WROTE {report_path}')
