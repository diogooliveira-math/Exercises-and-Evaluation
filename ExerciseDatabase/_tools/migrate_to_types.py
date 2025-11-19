"""
Script para migrar exercícios da estrutura antiga (sem tipos)
para a nova estrutura v3.0 (com tipos)

Uso:
    python migrate_to_types.py --concept "4-funcao_inversa" --dry-run
    python migrate_to_types.py --concept "4-funcao_inversa" --execute
"""

import json
import shutil
from pathlib import Path
from typing import Dict, List
import argparse

BASE_DIR = Path(__file__).parent.parent

def analyze_exercise_tags(json_file: Path) -> List[str]:
    """Analisa tags do exercício para sugerir tipo"""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    tags = data.get('classification', {}).get('tags', [])
    return tags

def suggest_type(tags: List[str]) -> str:
    """Sugere tipo baseado nas tags"""
    # Regras de decisão
    if any(tag in tags for tag in ['calculo_analitico', 'expressao_analitica', 'calculo']):
        return 'determinacao_analitica'
    elif any(tag in tags for tag in ['grafico', 'simetria', 'bissectriz']):
        return 'determinacao_grafica'
    elif any(tag in tags for tag in ['injetividade', 'teste_reta_horizontal']):
        return 'teste_reta_horizontal'
    elif any(tag in tags for tag in ['composicao', 'fog', 'gof']):
        return 'composicao'
    else:
        return 'indefinido'

def get_exercises_in_concept(discipline: str, module: str, concept: str) -> List[Path]:
    """Retorna lista de exercícios no conceito (sem estrutura de tipos)"""
    concept_path = BASE_DIR / discipline / module / concept
    
    if not concept_path.exists():
        print(f"❌ Conceito não encontrado: {concept_path}")
        return []
    
    # Apenas ficheiros .tex na raiz do conceito (não em subdiretórios)
    exercises = []
    for item in concept_path.glob("*.tex"):
        if item.is_file():
            exercises.append(item)
    
    return exercises

def migrate_exercise(tex_file: Path, target_type: str, dry_run: bool = True):
    """Migra um exercício para a estrutura de tipos"""
    json_file = tex_file.with_suffix('.json')
    
    if not json_file.exists():
        print(f"⚠️  JSON não encontrado para {tex_file.name}")
        return
    
    # Ler metadados
    with open(json_file, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    # Criar diretório do tipo
    type_path = tex_file.parent / target_type
    
    # Novo caminho dos ficheiros
    new_tex = type_path / tex_file.name
    new_json = type_path / json_file.name
    
    if dry_run:
        print(f"  📄 {tex_file.name} → {target_type}/{tex_file.name}")
    else:
        # Criar diretório se não existir
        type_path.mkdir(exist_ok=True)
        
        # Mover ficheiros
        shutil.move(str(tex_file), str(new_tex))
        shutil.move(str(json_file), str(new_json))
        
        # Atualizar metadata do exercício (adicionar campo tipo)
        metadata['classification']['tipo'] = target_type
        metadata['classification']['tipo_nome'] = target_type.replace('_', ' ').title()
        
        with open(new_json, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"  ✅ {tex_file.name} → {target_type}/{tex_file.name}")
        
        # Atualizar metadata do tipo
        update_type_metadata(type_path, metadata['id'])

def update_type_metadata(type_path: Path, exercise_id: str):
    """Atualiza metadata.json do tipo"""
    metadata_file = type_path / "metadata.json"
    
    if metadata_file.exists():
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
    else:
        # Criar metadata básico
        metadata = {
            "tipo": type_path.name,
            "tipo_nome": type_path.name.replace('_', ' ').title(),
            "exercicios": []
        }
    
    if exercise_id not in metadata['exercicios']:
        metadata['exercicios'].append(exercise_id)
    
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

def migrate_concept(discipline: str, module: str, concept: str, dry_run: bool = True):
    """Migra todos os exercícios de um conceito"""
    print(f"\n🔄 Migrando: {discipline}/{module}/{concept}")
    print(f"   Modo: {'DRY-RUN (simulação)' if dry_run else 'EXECUÇÃO REAL'}")
    print("─" * 70)
    
    exercises = get_exercises_in_concept(discipline, module, concept)
    
    if not exercises:
        print("❌ Nenhum exercício encontrado na raiz do conceito.")
        print("   Exercícios já podem estar organizados por tipos.")
        return
    
    print(f"📊 Encontrados {len(exercises)} exercícios\n")
    
    # Analisar e classificar
    type_distribution = {}
    
    for tex_file in exercises:
        json_file = tex_file.with_suffix('.json')
        
        if json_file.exists():
            tags = analyze_exercise_tags(json_file)
            suggested_type = suggest_type(tags)
            
            type_distribution[suggested_type] = type_distribution.get(suggested_type, 0) + 1
            
            migrate_exercise(tex_file, suggested_type, dry_run)
        else:
            print(f"  ⚠️  {tex_file.name} - JSON não encontrado, ignorando")
    
    print("\n" + "─" * 70)
    print("📊 Distribuição por tipo:")
    for tipo, count in sorted(type_distribution.items()):
        print(f"   {tipo}: {count} exercícios")
    
    if dry_run:
        print("\n💡 Execute com --execute para aplicar as mudanças")

def main():
    parser = argparse.ArgumentParser(
        description="Migrar exercícios para estrutura v3.0 com tipos"
    )
    parser.add_argument(
        '--discipline',
        default='matematica',
        help='Disciplina (default: matematica)'
    )
    parser.add_argument(
        '--module',
        default='P4_funcoes',
        help='Módulo (default: P4_funcoes)'
    )
    parser.add_argument(
        '--concept',
        required=True,
        help='Conceito a migrar (ex: 4-funcao_inversa)'
    )
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Executar migração (sem este flag, apenas simula)'
    )
    
    args = parser.parse_args()
    
    dry_run = not args.execute
    
    migrate_concept(args.discipline, args.module, args.concept, dry_run)
    
    if args.execute:
        print("\n✅ Migração concluída!")
        print("💡 Execute 'python rebuild_index.py' para atualizar o índice global")

if __name__ == "__main__":
    main()
