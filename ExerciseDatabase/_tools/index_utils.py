import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
INDEX_FILE = BASE_DIR / 'index.json'


def update_projects_index(project_metadata: dict, project_path: str, index_file: Path = None) -> None:
    """Add or update a project entry in the global index.json (non-breaking).

    Minimal behaviour: ensure top-level 'projects' exists, append a summary entry,
    and update statistics.by_project_status.
    """
    if index_file is None:
        index_file = INDEX_FILE

    if index_file.exists():
        with open(index_file, 'r', encoding='utf-8') as f:
            idx = json.load(f)
    else:
        idx = {
            'database_version': '3.0',
            'last_updated': '',
            'total_exercises': 0,
            'statistics': {},
            'exercises': [],
            'projects': []
        }

    # Ensure projects list
    if 'projects' not in idx:
        idx['projects'] = []

    entry = {
        'id': project_metadata.get('id', project_metadata.get('titulo', 'UNKNOWN')),
        'titulo': project_metadata.get('titulo', ''),
        'responsavel': project_metadata.get('responsavel', ''),
        'path': project_path.replace('\\', '/'),
        'created_at': project_metadata.get('created_at', datetime.now().isoformat()),
        'status': project_metadata.get('status', 'draft')
    }

    idx['projects'].append(entry)

    # Update statistics.by_project_status
    stats = idx.setdefault('statistics', {})
    by_status = stats.setdefault('by_project_status', {})
    st = entry['status']
    by_status[st] = by_status.get(st, 0) + 1

    idx['last_updated'] = datetime.now().isoformat()

    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(idx, f, indent=2, ensure_ascii=False)
