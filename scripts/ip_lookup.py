"""Lookup IPs in the registry."""
from pathlib import Path
import argparse
from ExerciseDatabase._tools.ip_resolver import IPResolver


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('ips', nargs='+')
    args = parser.parse_args()
    r = IPResolver()
    res = r.resolve_list(args.ips)
    if not res:
        print('No matches')
    for e in res:
        print(f"{e.get('ip')} -> {e.get('path')} (label: {e.get('label')})")

if __name__ == '__main__':
    main()
