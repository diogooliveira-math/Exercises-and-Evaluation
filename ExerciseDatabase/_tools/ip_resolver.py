"""Resolver utilities for IPs."""
from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Optional
from .ip_registry import IPRegistry

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
EXERCISE_DB = REPO_ROOT / 'ExerciseDatabase'

class IPResolver:
    def __init__(self, registry: Optional[IPRegistry] = None):
        self.registry = registry or IPRegistry()

    def ip_to_path(self, ip: str) -> Optional[Path]:
        v = self.registry.get_by_ip(ip)
        if not v:
            return None
        p = Path(v['path'])
        if not p.is_absolute():
            return EXERCISE_DB / p
        return p

    def resolve_list(self, ips: List[str]) -> List[Dict]:
        return self.registry.resolve_ips(ips)

    def resolve_to_paths(self, ips: List[str]) -> List[Path]:
        out = []
        for e in self.resolve_list(ips):
            if 'path' in e and e['path']:
                p = Path(e['path'])
                if not p.is_absolute():
                    p = EXERCISE_DB / p
                out.append(p)
        return out
