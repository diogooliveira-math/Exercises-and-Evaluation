"""IP registry for exercises.

Provides atomic registry persistence, id allocation and lookups.
Registry path can be overridden with environment variable `IP_REGISTRY_PATH`.
"""
from __future__ import annotations
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_REGISTRY_DIR = REPO_ROOT / 'ExerciseDatabase' / '_registry'
DEFAULT_REGISTRY_PATH = DEFAULT_REGISTRY_DIR / 'ip_registry.json'
LOCK_SUFFIX = '.lock'

REGISTRY_PATH = Path(os.environ.get('IP_REGISTRY_PATH') or DEFAULT_REGISTRY_PATH)

# Prefer filelock when available
try:
    from filelock import FileLock
    _HAS_FILELOCK = True
except Exception:
    _HAS_FILELOCK = False

# simple cross-platform lock using exclusive creation of a .lock file (fallback)
class SimpleLock:
    def __init__(self, path: Path, timeout: float = 10.0, poll: float = 0.05):
        self.lockfile = Path(str(path) + LOCK_SUFFIX)
        self.timeout = timeout
        self.poll = poll
        self._fd = None

    def acquire(self):
        start = time.time()
        while True:
            try:
                # Use os.O_CREAT|os.O_EXCL to obtain exclusive creation
                fd = os.open(str(self.lockfile), os.O_CREAT | os.O_EXCL | os.O_RDWR)
                # write pid and ts
                os.write(fd, f"pid:{os.getpid()}\n".encode())
                self._fd = fd
                return
            except FileExistsError:
                if time.time() - start > self.timeout:
                    raise TimeoutError(f"Timeout acquiring lock {self.lockfile}")
                time.sleep(self.poll)

    def release(self):
        try:
            if self._fd:
                os.close(self._fd)
            if self.lockfile.exists():
                os.unlink(self.lockfile)
        except Exception:
            pass

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.release()

# Lock helper that uses FileLock if available
class RegistryLock:
    def __init__(self, path: Path, timeout: float = 10.0):
        self.path = path
        self.timeout = timeout
        if _HAS_FILELOCK:
            self.lock = FileLock(str(path) + LOCK_SUFFIX, timeout=timeout)
        else:
            self.lock = SimpleLock(path, timeout=timeout)

    def __enter__(self):
        return self.lock.__enter__()

    def __exit__(self, exc_type, exc, tb):
        return self.lock.__exit__(exc_type, exc, tb)


class IPRegistry:
    def __init__(self, path: Optional[Path] = None):
        self.path = Path(path) if path is not None else REGISTRY_PATH
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._data = None

    def load(self) -> Dict:
        if self._data is not None:
            return self._data
        if not self.path.exists():
            self._data = {
                'version': 1,
                'disciplines': {},
                'ips': {},
                'next_counters': {}
            }
            return self._data
        with open(self.path, 'r', encoding='utf8') as f:
            self._data = json.load(f)
        # ensure fields exist
        for k in ('disciplines','ips','next_counters'):
            if k not in self._data:
                self._data[k] = {}
        return self._data

    def save(self, backup: bool = True):
        if self._data is None:
            raise RuntimeError('No registry loaded')
        if backup and self.path.exists():
            bak = self.path.with_suffix(self.path.suffix + f'.bak_{int(time.time())}')
            try:
                os.replace(self.path, bak)
            except Exception:
                # best-effort backup; ignore
                pass
        tmp = self.path.with_suffix(self.path.suffix + '.tmp')
        # atomic write
        with open(tmp, 'w', encoding='utf8') as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, self.path)

    def _parent_key(self, levels: List[str]) -> str:
        # parent key used in next_counters map, join names by '::'
        return '::'.join(levels)

    def _alloc_counter(self, key: str) -> int:
        data = self.load()
        nc = data.setdefault('next_counters', {})
        val = nc.get(key, 1)
        nc[key] = val + 1
        return val

    def register_path(self, parts: List[str], exercise_relpath: str, label: Optional[str] = None) -> str:
        """Register a full path given parts = [discipline,module,concept,type,exercise]
        Returns assigned IP string.
        Idempotent: registering same path twice returns same IP.
        """
        if len(parts) != 5:
            raise ValueError('parts must be length 5')
        with RegistryLock(self.path):
            data = self.load()
            # traverse creating structure
            disc_name, mod_name, conc_name, type_name, ex_name = parts
            disciplines = data.setdefault('disciplines', {})
            # discipline
            disc = disciplines.get(disc_name)
            if disc is None:
                did = self._alloc_counter(f'discipline')
                disc = {'id': did, 'label': disc_name, 'modules': {}}
                disciplines[disc_name] = disc
            # module
            modules = disc.setdefault('modules', {})
            mod = modules.get(mod_name)
            if mod is None:
                mid = self._alloc_counter(f'discipline.{disc["id"]}.module')
                mod = {'id': mid, 'label': mod_name, 'concepts': {}}
                modules[mod_name] = mod
            # concept
            concepts = mod.setdefault('concepts', {})
            conc = concepts.get(conc_name)
            if conc is None:
                cid = self._alloc_counter(f'discipline.{disc["id"]}.module.{mod["id"]}.concept')
                conc = {'id': cid, 'label': conc_name, 'types': {}}
                concepts[conc_name] = conc
            # type
            types = conc.setdefault('types', {})
            typ = types.get(type_name)
            if typ is None:
                tid = self._alloc_counter(f'discipline.{disc["id"]}.module.{mod["id"]}.concept.{conc["id"]}.type')
                typ = {'id': tid, 'label': type_name, 'exercises': {}}
                types[type_name] = typ
            # exercise
            exercises = typ.setdefault('exercises', {})
            ex = exercises.get(ex_name)
            if ex is None:
                eid = self._alloc_counter(f'discipline.{disc["id"]}.module.{mod["id"]}.concept.{conc["id"]}.type.{typ["id"]}.exercise')
                ex = {'id': eid, 'label': ex_name, 'path': exercise_relpath}
                exercises[ex_name] = ex
            # build IP
            ids = [str(disc['id']), str(mod['id']), str(conc['id']), str(typ['id']), str(ex['id'])]
            ip = '.'.join(ids)
            data_ips = data.setdefault('ips', {})
            # if ip exists but points to different path, add note but keep existing IP
            existing = data_ips.get(ip)
            if existing is None:
                data_ips[ip] = {
                    'path': exercise_relpath,
                    'parts': parts,
                    'label': label or ex_name,
                    'assigned_at': int(time.time())
                }
            else:
                # idempotent; update path/label if missing
                if 'path' not in existing or not existing['path']:
                    existing['path'] = exercise_relpath
                if 'label' not in existing:
                    existing['label'] = label or ex_name

            # persist per-exercise metadata on disk for resilience
            try:
                ex_rel = Path(exercise_relpath)
                # if exercise_relpath starts with 'ExerciseDatabase' strip it
                if ex_rel.parts and ex_rel.parts[0].lower() == 'exercisedatabase':
                    ex_rel = Path(*ex_rel.parts[1:])
                exercise_dir = REPO_ROOT / 'ExerciseDatabase' / ex_rel
                # ensure exercise exists
                if exercise_dir.exists():
                    meta = {
                        'ip': ip,
                        'ids': {
                            'discipline': disc['id'],
                            'module': mod['id'],
                            'concept': conc['id'],
                            'type': typ['id'],
                            'exercise': ex['id']
                        },
                        'label': label or ex_name,
                        'path': str(ex_rel),
                        'assigned_at': int(time.time())
                    }
                    with open(exercise_dir / 'exercise.json', 'w', encoding='utf8') as mf:
                        json.dump(meta, mf, indent=2, ensure_ascii=False)
                # also write per-directory _meta.json for concept directory
                concept_dir = REPO_ROOT / 'ExerciseDatabase' / ex_rel.parent
                concept_meta = {'id': conc['id'], 'label': conc_name}
                with open(concept_dir / '_meta.json', 'w', encoding='utf8') as cm:
                    json.dump(concept_meta, cm, indent=2, ensure_ascii=False)
            except Exception:
                # best-effort; do not fail registration if filesystem write fails
                pass

            # save
            self.save()
            return ip

    def get_by_ip(self, ip: str) -> Optional[Dict]:
        data = self.load()
        return data.get('ips', {}).get(ip)

    def resolve_ips(self, ips: List[str]) -> List[Dict]:
        """Given list of IPs or simple prefix patterns ending with '*', resolve to matching metadata entries."""
        data = self.load()
        out = []
        for token in ips:
            token = token.strip()
            if token.endswith('*'):
                prefix = token[:-1]
                for ipk, v in data.get('ips', {}).items():
                    if ipk.startswith(prefix):
                        out.append({'ip': ipk, **v})
            else:
                v = data.get('ips', {}).get(token)
                if v:
                    out.append({'ip': token, **v})
                else:
                    # not found: continue (caller may handle)
                    pass
        return out


# small helper for CLI usage
def register_from_fs(base_dir: Path) -> Dict[str,str]:
    """Walk a simple filesystem under base_dir with structure disc/module/concept/type/exercise
    returns mapping ip->path (paths relative to base_dir)
    """
    base_dir = Path(base_dir)
    mapping = {}
    for disc in sorted([d for d in base_dir.iterdir() if d.is_dir() and not d.name.startswith('_')]):
        for mod in sorted([d for d in (disc).iterdir() if d.is_dir() and not d.name.startswith('_')]):
            for conc in sorted([d for d in (mod).iterdir() if d.is_dir() and not d.name.startswith('_')]):
                for typ in sorted([d for d in (conc).iterdir() if d.is_dir() and not d.name.startswith('_')]):
                    for ex in sorted([d for d in (typ).iterdir() if d.is_dir() and not d.name.startswith('_')]):
                        parts = [disc.name, mod.name, conc.name, typ.name, ex.name]
                        rel = Path(ex.relative_to(base_dir))
                        rel_str = str(rel)
                        ip = IPRegistry().register_path(parts, rel_str, label=ex.name)
                        mapping[ip] = rel_str
    return mapping
