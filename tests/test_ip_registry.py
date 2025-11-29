import tempfile
from pathlib import Path
import shutil
import os
import time

from ExerciseDatabase._tools.ip_registry import IPRegistry


def test_registry_roundtrip_and_allocation(tmp_path):
    # use temp registry path
    rp = tmp_path / 'registry' / 'ip_registry.json'
    reg = IPRegistry(path=rp)
    # register a simple path
    parts = ['matematica','P1','conceito1','tipoA','ex1']
    ip = reg.register_path(parts, 'ExerciseDatabase/matematica/P1/conceito1/tipoA/ex1')
    assert ip.count('.') == 4
    # reload new instance
    reg2 = IPRegistry(path=rp)
    data = reg2.load()
    assert 'ips' in data
    assert ip in data['ips']


def test_idempotent_register(tmp_path):
    rp = tmp_path / 'registry' / 'ip_registry.json'
    reg = IPRegistry(path=rp)
    parts = ['sci','mod','conc','t','e']
    ip1 = reg.register_path(parts, 'ExerciseDatabase/sci/mod/conc/t/e')
    ip2 = reg.register_path(parts, 'ExerciseDatabase/sci/mod/conc/t/e')
    assert ip1 == ip2


def test_resolve_prefix(tmp_path):
    rp = tmp_path / 'registry' / 'ip_registry.json'
    reg = IPRegistry(path=rp)
    p1 = ['d1','m1','c1','t1','e1']
    p2 = ['d1','m1','c1','t1','e2']
    ip1 = reg.register_path(p1, 'p1')
    ip2 = reg.register_path(p2, 'p2')
    res = reg.resolve_ips([ip1[:-2] + '*'])
    assert any(r['ip'] == ip1 for r in res)
    assert any(r['ip'] == ip2 for r in res)
