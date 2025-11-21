#!/usr/bin/env python3
"""
Script simples para mostrar estatísticas da base de dados
"""
import json
from pathlib import Path

def show_stats():
    index_file = Path(__file__).parent.parent / "ExerciseDatabase" / "index.json"
    
    with open(index_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print('\n' + '='*60)
    print('  ESTATÍSTICAS DA BASE DE DADOS')
    print('='*60 + '\n')
    
    print(f"📊 Total: {data['total_exercises']} exercícios")
    print(f"📌 Versão: {data['database_version']}")
    print(f"🕐 Última atualização: {data['last_updated']}")
    
    print('\n📚 Por Módulo:')
    for module, count in sorted(data['statistics']['by_module'].items()):
        print(f"  • {module}: {count} exercícios")
    
    print('\n⭐ Por Dificuldade:')
    for diff, count in sorted(data['statistics']['by_difficulty'].items()):
        print(f"  • {diff}: {count} exercícios")
    
    if 'by_type' in data['statistics']:
        print('\n🏷️  Por Tipo:')
        for tipo, count in sorted(data['statistics']['by_type'].items())[:10]:
            print(f"  • {tipo}: {count} exercícios")
    
    print('\n' + '='*60 + '\n')

if __name__ == '__main__':
    show_stats()
