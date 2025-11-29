"""Simple smoke test for IPRegistry without pytest dependency."""
import sys
from pathlib import Path
import tempfile
import shutil

# Ensure repo root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from ExerciseDatabase._tools.ip_registry import IPRegistry


def main():
    tmp = Path(tempfile.mkdtemp(prefix='ipregtest_'))
    try:
        rp = tmp / 'registry' / 'ip_registry.json'
        print('Using registry path:', rp)
        reg = IPRegistry(path=rp)
        parts = ['matematica','P1','conceito1','tipoA','ex1']
        ip = reg.register_path(parts, 'ExerciseDatabase/matematica/P1/conceito1/tipoA/ex1')
        print('Assigned IP:', ip)
        # re-open
        reg2 = IPRegistry(path=rp)
        info = reg2.get_by_ip(ip)
        if not info:
            print('ERROR: ip not found after save')
            return 2
        print('Lookup OK:', info)
        # idempotency
        ip2 = reg2.register_path(parts, 'ExerciseDatabase/matematica/P1/conceito1/tipoA/ex1')
        if ip != ip2:
            print('ERROR: idempotency failed', ip, ip2)
            return 3
        print('Idempotency OK')
        # prefix resolve
        pref = ip.rsplit('.',1)[0] + '.'
        res = reg2.resolve_ips([pref + '*'])
        if not any(r['ip'] == ip for r in res):
            print('ERROR: prefix resolve failed')
            return 4
        print('Prefix resolve OK. Entries found:', len(res))
        return 0
    finally:
        try:
            shutil.rmtree(tmp)
        except Exception:
            pass

if __name__ == '__main__':
    code = main()
    sys.exit(code)
