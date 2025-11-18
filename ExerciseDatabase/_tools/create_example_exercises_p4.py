from pathlib import Path
import json
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
DISC = 'matematica'
MODULE = 'P4_funcoes'

exercises = [
    {
        'concept': '1-generalidades_funcoes',
        'short': 'Generalidades acerca de Funções',
        'statement': 'Defina o conceito de função entre conjuntos e dê dois exemplos simples.'
    },
    {
        'concept': '2-funcoes_polinomiais',
        'short': 'Funções Polinomiais',
        'statement': 'Dê a definição de função polinomial e escreva um polinómio de grau 2.'
    },
    {
        'concept': '3-funcoes_polinomiais_grau_nao_superior_3',
        'short': 'Funções polinomiais de grau não superior a 3',
        'statement': 'Considere a função p(x)=x^3-2x^2+3x-1. Determine o seu grau e identifique termos principais.'
    }
]

# Helper to create an ID consistent with existing convention
def make_id(disc, module, concept, idx):
    disc_abbr = disc[:3].upper()
    module_abbr = module.replace('_','').upper()[:8]
    # concept abbrev: take up to 4 alnum chars from concept name
    import re
    cpart = re.sub('[^A-Za-z0-9]','', concept)
    concept_abbr = (cpart.upper()[:4]) if cpart else 'C'
    return f"{disc_abbr}_{module_abbr}_{concept_abbr}_{idx:03d}"

# Load or init index
index_file = BASE_DIR / 'index.json'
if index_file.exists():
    with open(index_file, 'r', encoding='utf-8') as f:
        index = json.load(f)
else:
    index = {
        "database_version": "2.0",
        "last_updated": "",
        "total_exercises": 0,
        "statistics": {
            "by_discipline": {},
            "by_module": {},
            "by_concept": {},
            "by_difficulty": {},
            "by_type": {}
        },
        "exercises": []
    }

created = 0
for i, ex in enumerate(exercises, start=1):
    ex_id = make_id(DISC, MODULE, ex['concept'], 1)  # use 001 for examples
    path = Path(DISC) / MODULE / ex['concept'] / f"{ex_id}.tex"
    full_path = BASE_DIR / path
    full_path.parent.mkdir(parents=True, exist_ok=True)

    today = datetime.now().strftime('%Y-%m-%d')

    # metadata
    metadata = {
        "id": ex_id,
        "version": "1.0",
        "created": today,
        "modified": today,
        "author": "Exemplo",
        "classification": {
            "discipline": DISC,
            "module": MODULE,
            "module_name": "MÓDULO P4 - Funções",
            "concept": ex['concept'],
            "concept_name": ex['short'],
            "tags": [],
            "difficulty": 2,
            "difficulty_label": "Fácil"
        },
        "exercise_type": "desenvolvimento",
        "content": {
            "has_multiple_parts": False,
            "parts_count": 0,
            "has_graphics": False,
            "requires_packages": ["amsmath", "amssymb"]
        },
        "evaluation": {
            "bloom_level": "compreensao"
        },
        "solution": {
            "available": False,
            "file": ""
        },
        "usage": {
            "times_used": 0,
            "last_used": "",
            "contexts": []
        },
        "status": "active"
    }

    latex = f"% Exercise ID: {ex_id}\n% Module: MÓDULO P4 - Funções | Concept: {ex['short']}\n% Difficulty: 2/5 (Fácil) | Type: desenvolvimento\n% Author: Exemplo | Date: {today}\n% Status: active\n\n\\exercicio{{{ex['statement']}}}\n"

    # write files
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(latex)
    with open(full_path.with_suffix('.json'), 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    # update index
    entry = {
        "id": metadata["id"],
        "path": str(path.as_posix()),
        "discipline": DISC,
        "module": MODULE,
        "module_name": metadata['classification']['module_name'],
        "concept": metadata['classification']['concept'],
        "concept_name": metadata['classification']['concept_name'],
        "difficulty": metadata['classification']['difficulty'],
        "type": metadata['exercise_type'],
        "tags": metadata['classification']['tags'],
        "points": 0,
        "status": metadata['status']
    }
    index['exercises'].append(entry)
    index['total_exercises'] = len(index['exercises'])

    # statistics
    disc = DISC
    index['statistics'].setdefault('by_discipline', {})
    index['statistics']['by_discipline'][disc] = index['statistics']['by_discipline'].get(disc, 0) + 1
    mod = MODULE
    index['statistics'].setdefault('by_module', {})
    index['statistics']['by_module'][mod] = index['statistics']['by_module'].get(mod, 0) + 1
    conc = metadata['classification']['concept_name']
    index['statistics'].setdefault('by_concept', {})
    index['statistics']['by_concept'][conc] = index['statistics']['by_concept'].get(conc, 0) + 1
    diff = metadata['classification']['difficulty_label']
    index['statistics'].setdefault('by_difficulty', {})
    index['statistics']['by_difficulty'][diff] = index['statistics']['by_difficulty'].get(diff, 0) + 1
    ex_type = metadata['exercise_type']
    index['statistics'].setdefault('by_type', {})
    index['statistics']['by_type'][ex_type] = index['statistics']['by_type'].get(ex_type, 0) + 1

    created += 1

index['last_updated'] = datetime.now().isoformat()
with open(index_file, 'w', encoding='utf-8') as f:
    json.dump(index, f, indent=2, ensure_ascii=False)

print(f"Criados {created} exercícios de exemplo em {BASE_DIR / DISC / MODULE}")
