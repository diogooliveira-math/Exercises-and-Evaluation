import multiprocessing
import tempfile
import os
from pathlib import Path
import time

from ExerciseDatabase._tools.ip_registry import IPRegistry


def worker(reg_path, base_dir, index):
    reg = IPRegistry(path=Path(reg_path))
    parts = ['disc', 'mod', 'conc', 'type', f'ex_{index}']
    rel = Path('disc/mod/conc/type') / f'ex_{index}'
    ip = reg.register_path(parts, str(rel), label=parts[-1])
    print('worker', index, 'got', ip)


def main():
    tmp = tempfile.mkdtemp(prefix='ipreg_conc_')
    try:
        reg_path = Path(tmp) / 'ip_registry.json'
        procs = []
        N = 8
        for i in range(N):
            p = multiprocessing.Process(target=worker, args=(str(reg_path), str(tmp), i))
            p.start()
            procs.append(p)
        for p in procs:
            p.join()
        # verify
        reg = IPRegistry(path=reg_path)
        data = reg.load()
        ips = data.get('ips', {})
        assert len(ips) == N
        print('concurrency test OK, registered', len(ips))
    finally:
        try:
            import shutil
            shutil.rmtree(tmp)
        except Exception:
            pass

if __name__ == '__main__':
    main()
