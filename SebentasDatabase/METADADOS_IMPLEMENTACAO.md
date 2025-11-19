# Sistema de Metadados para Sebentas v3.0

## Implementação Completa

### 📋 O que foi feito

1. **Criação de Metadados para Conceitos**
   - Ficheiro `metadata.json` em cada diretório de conceito
   - Contém: id, nome, descrição, módulo, ordem, tags, dificuldade, horas estimadas
   - Para conceitos com tipos: inclui lista de tipos com descrições

2. **Integração com `modules_config.yaml`**
   - Já existia configuração de módulos com nomes e descrições
   - Agora usado automaticamente pelo gerador de sebentas

3. **Atualização do `generate_sebentas.py`**
   - Carrega metadados do conceito (`metadata.json`)
   - Usa nome do módulo do `modules_config.yaml`
   - Gera sebentas com:
     - Título correto (ex: "Função Inversa" em vez de "4-funcao_inversa")
     - Descrição do conceito em itálico
     - Lista de tipos de exercícios com descrições
     - Cabeçalho: Módulo à esquerda, Conceito à direita

4. **Estrutura de Ficheiros Criados**

```
ExerciseDatabase/matematica/P4_funcoes/
├── 1-generalidades_funcoes/
│   └── metadata.json  ✅ NOVO
├── 2-funcoes_polinomiais/
│   └── metadata.json  ✅ NOVO
├── 3-funcoes_polinomiais_grau_nao_superior_3/
│   └── metadata.json  ✅ NOVO
└── 4-funcao_inversa/
    ├── metadata.json  ✅ NOVO (com tipos incluídos)
    ├── determinacao_analitica/
    │   └── metadata.json  (já existia)
    ├── determinacao_grafica/
    │   └── metadata.json  (já existia)
    └── teste_reta_horizontal/
        └── metadata.json  (já existia)
```

### 📄 Exemplo de metadata.json (Função Inversa)

```json
{
  "id": "4-funcao_inversa",
  "name": "Função Inversa",
  "description": "Conceito de função inversa, condições de existência (injetividade), determinação analítica e gráfica, simetria e propriedades.",
  "module": "P4_funcoes",
  "module_name": "MÓDULO P4 - Funções",
  "order": 4,
  "tags": ["inversa", "injetividade", "sobrejetividade", "simetria", "bijecao"],
  "difficulty_range": {
    "min": 3,
    "max": 5
  },
  "estimated_hours": 5,
  "tipos": [
    {
      "id": "determinacao_analitica",
      "name": "Determinação Analítica",
      "description": "Cálculo da expressão analítica da função inversa através de manipulação algébrica"
    },
    {
      "id": "determinacao_grafica",
      "name": "Determinação Gráfica",
      "description": "Obtenção do gráfico da função inversa por simetria relativamente à bissetriz dos quadrantes ímpares"
    },
    {
      "id": "teste_reta_horizontal",
      "name": "Teste da Reta Horizontal",
      "description": "Verificação da injetividade de uma função através do teste da reta horizontal"
    }
  ]
}
```

### 🎯 Resultado nas Sebentas

#### Sebenta Individual (ex: Função Inversa)

```
┌─────────────────────────────────────────────────────────┐
│ MÓDULO P4 - Funções             Função Inversa     Pág 1│
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Função Inversa                                          │
│                                                         │
│ Conceito de função inversa, condições de existência    │
│ (injetividade), determinação analítica e gráfica,      │
│ simetria e propriedades.                                │
│                                                         │
│ Tipos de Exercícios                                     │
│ • Determinação Analítica — Cálculo da expressão        │
│   analítica da função inversa através de manipulação   │
│   algébrica                                             │
│ • Determinação Gráfica — Obtenção do gráfico da        │
│   função inversa por simetria...                       │
│ • Teste da Reta Horizontal — Verificação da            │
│   injetividade...                                       │
│                                                         │
│ Exercícios                                              │
│                                                         │
│ Exercício 1. [conteúdo do exercício]                   │
│ ...                                                     │
└─────────────────────────────────────────────────────────┘
```

#### Sebenta Consolidada do Módulo

```
┌─────────────────────────────────────────────────────────┐
│ matematica              MÓDULO P4 - Funções        Pág 1│
├─────────────────────────────────────────────────────────┤
│                                                         │
│ MÓDULO P4 - Funções                                     │
│                                                         │
│ Introdução às funções e funções polinomiais             │
│                                                         │
│ Este documento contém todos os exercícios do módulo,   │
│ organizados por conceito.                               │
│                                                         │
│ Índice                                                  │
│ 1. Generalidades acerca de Funções ............... 2    │
│ 2. Funções Polinomiais ........................... 5    │
│ 3. Funções Polinomiais de Grau não Superior a 3 .. 8    │
│ 4. Função Inversa ............................... 12    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 🔧 Alterações nos Scripts

#### `generate_sebentas.py`

1. **Adicionado import**: `import yaml`
2. **Novos métodos**:
   - `load_modules_config()`: Carrega `modules_config.yaml`
   - `get_module_name()`: Obtém nome do módulo
3. **Atualizado `get_concept_metadata()`**:
   - Lê `metadata.json` do conceito
   - Extrai nome, descrição e tipos
4. **Atualizado `generate_content()`**:
   - Adiciona descrição do conceito
   - Lista tipos com descrições formatadas
5. **Atualizado `generate_sebenta()`**:
   - Usa nome do módulo no cabeçalho
   - Usa nome do conceito (não o ID)
6. **Atualizado `generate_module_sebenta()`**:
   - Usa nome e descrição do módulo
   - Cabeçalho com nome completo

#### `add_exercise_with_types.py`

- Nenhuma alteração necessária
- Já funciona com a estrutura de metadados existente
- Cria/atualiza automaticamente metadados dos tipos

### ✅ Validação

Todos os PDFs foram regenerados com sucesso:
- ✅ `sebenta_1-generalidades_funcoes.pdf` (60.4 KB)
- ✅ `sebenta_2-funcoes_polinomiais.pdf` (61.8 KB)
- ✅ `sebenta_3-funcoes_polinomiais_grau_nao_superior_3.pdf` (90.4 KB)
- ✅ `sebenta_4-funcao_inversa.pdf` (139.4 KB)
- ✅ `sebenta_modulo_P4_funcoes.pdf` (80.1 KB)

### 🚀 Como Usar

#### Gerar sebentas com títulos corretos:

```powershell
# Gerar todo o módulo
python SebentasDatabase/_tools/generate_sebentas.py --module P4_funcoes

# Gerar apenas um conceito
python SebentasDatabase/_tools/generate_sebentas.py --module P4_funcoes --concept "4-funcao_inversa"

# Gerar todas as disciplinas
python SebentasDatabase/_tools/generate_sebentas.py
```

#### Adicionar novos exercícios (já suporta metadados):

```powershell
python ExerciseDatabase/_tools/add_exercise_with_types.py
```

### 📝 Para Adicionar Novos Conceitos

1. Criar `metadata.json` no diretório do conceito:

```json
{
  "id": "conceito-id",
  "name": "Nome do Conceito",
  "description": "Descrição do conceito",
  "module": "modulo_id",
  "module_name": "Nome do Módulo",
  "order": 1,
  "tags": ["tag1", "tag2"],
  "difficulty_range": {"min": 2, "max": 4},
  "estimated_hours": 3
}
```

2. Se tiver tipos, adicionar no metadata:

```json
{
  ...
  "tipos": [
    {
      "id": "tipo-id",
      "name": "Nome do Tipo",
      "description": "Descrição do tipo"
    }
  ]
}
```

3. Garantir que o módulo está em `modules_config.yaml`

4. Regenerar sebentas

### 🎓 Benefícios

1. **Títulos Profissionais**: "Função Inversa" em vez de "4-funcao_inversa"
2. **Contexto Pedagógico**: Descrições explicam o objetivo de cada conceito
3. **Organização Clara**: Tipos de exercícios listados com explicações
4. **Manutenibilidade**: Metadados centralizados e fáceis de editar
5. **Automação**: Scripts usam metadados automaticamente
6. **Escalabilidade**: Fácil adicionar novos conceitos/módulos

### 🔮 Próximos Passos (Opcional)

1. Adicionar metadados para outros módulos (A10, A11, etc.)
2. Usar metadados para filtrar exercícios por dificuldade
3. Gerar estatísticas baseadas em metadados
4. Exportar metadados para outros formatos (HTML, Markdown)

---

**Versão**: 3.0  
**Data**: 2025-11-19  
**Autor**: Sistema Automático de Geração de Sebentas
