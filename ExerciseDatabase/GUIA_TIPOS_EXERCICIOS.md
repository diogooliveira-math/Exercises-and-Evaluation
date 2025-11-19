# 📘 Guia: Sistema de Tipos de Exercícios (v3.0)

## Visão Geral

O sistema agora suporta uma **hierarquia de 5 níveis** para melhor organização:

```
disciplina → tema → conceito → TIPO → exercício
```

O **tipo** permite diferenciar exercícios dentro do mesmo conceito. Por exemplo, em "Função Inversa":
- Tipo 1: Determinação Analítica (cálculo algébrico)
- Tipo 2: Determinação Gráfica (obter gráfico por simetria)
- Tipo 3: Teste da Reta Horizontal (verificar injetividade)

---

## 🏗️ Estrutura de Diretórios

### Antes (v2.0 - sem tipos)
```
matematica/P4_funcoes/4-funcao_inversa/
├── MAT_P4FUNCOE_4FIN_001.tex
├── MAT_P4FUNCOE_4FIN_001.json
├── MAT_P4FUNCOE_4FIN_002.tex
├── MAT_P4FUNCOE_4FIN_002.json
└── ...
```

### Agora (v3.0 - com tipos)
```
matematica/P4_funcoes/4-funcao_inversa/
├── determinacao_analitica/           # Tipo 1
│   ├── metadata.json                 # Metadados do TIPO
│   ├── MAT_P4FUNCOE_4FIN_ANA_001.tex
│   ├── MAT_P4FUNCOE_4FIN_ANA_001.json
│   └── MAT_P4FUNCOE_4FIN_ANA_002.tex
├── determinacao_grafica/             # Tipo 2
│   ├── metadata.json
│   ├── MAT_P4FUNCOE_4FIN_GRA_001.tex
│   └── MAT_P4FUNCOE_4FIN_GRA_001.json
└── teste_reta_horizontal/            # Tipo 3
    ├── metadata.json
    ├── MAT_P4FUNCOE_4FIN_TRH_001.tex
    └── MAT_P4FUNCOE_4FIN_TRH_001.json
```

---

## 📄 Metadata do Tipo (Opção A: JSON por Diretório)

Cada diretório de tipo contém um ficheiro `metadata.json`:

### Estrutura do `metadata.json`

```json
{
  "tipo": "determinacao_analitica",
  "tipo_nome": "Determinação Analítica da Função Inversa",
  "conceito": "4-funcao_inversa",
  "conceito_nome": "Função Inversa",
  "tema": "P4_funcoes",
  "tema_nome": "MÓDULO P4 - Funções",
  "disciplina": "matematica",
  "descricao": "Exercícios focados no cálculo da expressão analítica da função inversa através de manipulação algébrica.",
  "tags_tipo": [
    "calculo_analitico",
    "expressao_analitica",
    "algebra",
    "resolucao_equacao"
  ],
  "caracteristicas": {
    "requer_calculo": true,
    "requer_grafico": false,
    "complexidade_algebrica": "media"
  },
  "dificuldade_sugerida": {
    "min": 2,
    "max": 4
  },
  "exercicios": [
    "MAT_P4FUNCOE_4FIN_ANA_001",
    "MAT_P4FUNCOE_4FIN_ANA_002",
    "MAT_P4FUNCOE_4FIN_ANA_003",
    "MAT_P4FUNCOE_4FIN_ANA_004",
    "MAT_P4FUNCOE_4FIN_ANA_005"
  ]
}
```

**IMPORTANTE**: O array `exercicios` contém apenas a **lista de IDs**. Metadados detalhados de cada exercício estão nos ficheiros `.json` individuais (se existirem) ou podem ser omitidos (apenas `.tex` é obrigatório).

### Campos Explicados

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `tipo` | string | ID do tipo (snake_case) |
| `tipo_nome` | string | Nome descritivo do tipo |
| `conceito` | string | ID do conceito pai |
| `conceito_nome` | string | Nome do conceito |
| `tema` | string | ID do tema/módulo |
| `tema_nome` | string | Nome do tema |
| `disciplina` | string | ID da disciplina |
| `descricao` | string | Descrição detalhada do tipo |
| `tags_tipo` | array | Tags automáticas para exercícios deste tipo |
| `caracteristicas` | object | Características específicas do tipo |
| `dificuldade_sugerida` | object | Intervalo de dificuldade recomendado |
| `exercicios` | array | Lista de IDs dos exercícios neste tipo |

---

## 🆔 Nomenclatura de IDs

### Formato com Tipo (v3.0)

```
MAT_P4FUNCOE_4FIN_ANA_001
│   │        │    │   └── Número sequencial (001-999)
│   │        │    └────── Abreviação do TIPO (3 letras)
│   │        └─────────── Abreviação do conceito (3-4 letras)
│   └──────────────────── Abreviação do módulo (até 8 letras)
└──────────────────────── Disciplina (3 letras)
```

### Exemplos de Abreviações de Tipos

| Tipo | Abreviação | Exemplo ID |
|------|------------|------------|
| determinacao_analitica | ANA | MAT_P4FUNCOE_4FIN_ANA_001 |
| determinacao_grafica | GRA | MAT_P4FUNCOE_4FIN_GRA_001 |
| teste_reta_horizontal | TRH | MAT_P4FUNCOE_4FIN_TRH_001 |
| aplicacao_regras | APR | MAT_A11DERIV_3REG_APR_001 |
| interpretacao_geometrica | IGE | MAT_A11DERIV_5INT_IGE_001 |

---

## 🛠️ Como Criar Novo Tipo

### Método 1: Via Script Interativo (Recomendado)

```bash
python ExerciseDatabase/_tools/add_exercise_with_types.py
```

Ao escolher o conceito, selecione "➕ Criar novo tipo" e siga o wizard.

**Nota**: Este é o método recomendado pois atualiza automaticamente o `metadata.json` do tipo.

### Método 2: Manualmente

1. **Criar diretório do tipo**
   ```bash
   mkdir "matematica/P4_funcoes/4-funcao_inversa/novo_tipo"
   ```

2. **Criar `metadata.json`**
   ```json
   {
     "tipo": "novo_tipo",
     "tipo_nome": "Nome Descritivo",
     "conceito": "4-funcao_inversa",
     "conceito_nome": "Função Inversa",
     "tema": "P4_funcoes",
     "tema_nome": "MÓDULO P4 - Funções",
     "disciplina": "matematica",
     "descricao": "Descrição do tipo de exercício",
     "tags_tipo": ["tag1", "tag2"],
     "caracteristicas": {
       "requer_calculo": false,
       "requer_grafico": true
     },
     "dificuldade_sugerida": {
       "min": 2,
       "max": 4
     },
     "exercicios": []
   }
   ```

3. **Começar a adicionar exercícios**
   Use `add_exercise_with_types.py` e selecione o novo tipo.

---

## 📝 Como Adicionar Exercício a um Tipo

### Usando o Script (Método Principal)

```bash
python ExerciseDatabase/_tools/add_exercise_with_types.py
```

O wizard irá:
1. Solicitar disciplina, tema, conceito
2. Mostrar tipos disponíveis
3. Permitir criar novo tipo se necessário
4. Gerar ID automaticamente (incluindo componente de tipo)
5. Aplicar tags automáticas do tipo + conceito
6. Salvar ficheiro `.tex` no diretório do tipo
7. **Adicionar ID à lista** `exercicios[]` no `metadata.json` do tipo
8. Atualizar `index.json` global

### Usando Gerador de Variantes

```bash
python ExerciseDatabase/_tools/generate_variant.py --source "path/to/exercise.tex" --strategy auto
```

Gera variante de exercício existente:
- Mantém mesmo tipo
- Gera novo ID sequencial
- Atualiza `metadata.json` do tipo automaticamente
- Aplica variações simples ao conteúdo (modo `auto`)

### Estrutura dos Ficheiros Criados

**Ficheiro `.tex`** (exemplo):
```latex
% Exercise ID: MAT_P4FUNCOE_4FIN_ANA_001
% Module: MÓDULO P4 - Funções | Concept: Função Inversa | Type: Determinação Analítica
% Difficulty: 3/5 (Médio) | Format: desenvolvimento
% Tags: inversa, calculo_analitico, expressao_analitica
% Author: Professor | Date: 2025-11-19
% Status: active

\exercicio{Considere a função $f(x) = 2x + 3$. Determine a expressão analítica de $f^{-1}(x)$.}
```

**Ficheiro `.json`** (exemplo):
```json
{
  "id": "MAT_P4FUNCOE_4FIN_ANA_001",
  "version": "1.0",
  "created": "2025-11-19",
  "modified": "2025-11-19",
  "author": "Professor",
  "classification": {
    "discipline": "matematica",
    "module": "P4_funcoes",
    "module_name": "MÓDULO P4 - Funções",
    "concept": "4-funcao_inversa",
    "concept_name": "Função Inversa",
    "tipo": "determinacao_analitica",
    "tipo_nome": "Determinação Analítica",
    "tags": ["inversa", "calculo_analitico", "expressao_analitica"],
    "difficulty": 3,
    "difficulty_label": "Médio"
  },
  "exercise_type": "desenvolvimento",
  "status": "active"
}
```

---

## 🔍 Pesquisar Exercícios por Tipo

### Via Script

```bash
python ExerciseDatabase/_tools/search_exercises.py --type determinacao_analitica
```

### Via Python API

```python
from pathlib import Path
import json

# Ler metadata do tipo
tipo_path = Path("ExerciseDatabase/matematica/P4_funcoes/4-funcao_inversa/determinacao_analitica")
metadata_file = tipo_path / "metadata.json"

with open(metadata_file, 'r', encoding='utf-8') as f:
    tipo_data = json.load(f)

print(f"Tipo: {tipo_data['tipo_nome']}")
print(f"Exercícios: {len(tipo_data['exercicios'])}")
print(f"IDs: {', '.join(tipo_data['exercicios'])}")
```

---

## 📊 Índice Global Atualizado

O `index.json` agora rastreia tipos:

```json
{
  "database_version": "3.0",
  "last_updated": "2025-11-19T...",
  "total_exercises": 15,
  "statistics": {
    "by_type": {
      "Determinação Analítica": 5,
      "Determinação Gráfica": 3,
      "Teste da Reta Horizontal": 2
    }
  },
  "exercises": [
    {
      "id": "MAT_P4FUNCOE_4FIN_ANA_001",
      "path": "matematica/P4_funcoes/4-funcao_inversa/determinacao_analitica/MAT_P4FUNCOE_4FIN_ANA_001.tex",
      "tipo": "determinacao_analitica",
      "tipo_nome": "Determinação Analítica",
      "difficulty": 3
    }
  ]
}
```

---

## 🔄 Migrar Exercícios Antigos

### Passo a Passo

1. **Analisar exercícios existentes**
   - Ler tags e metadados
   - Identificar tipos naturais

2. **Criar estrutura de tipos**
   ```bash
   mkdir conceito/tipo1
   mkdir conceito/tipo2
   ```

3. **Mover ficheiros**
   ```bash
   mv conceito/exercicio1.* conceito/tipo1/
   ```

4. **Renomear IDs** (adicionar componente de tipo)
   - Editar ficheiros `.tex` e `.json`
   - Atualizar ID: `MAT_P4_4FIN_001` → `MAT_P4_4FIN_ANA_001`

5. **Criar `metadata.json` dos tipos**
   - Seguir template acima
   - Listar exercícios em `exercicios[]`

6. **Atualizar `index.json`**
   ```bash
   python ExerciseDatabase/_tools/rebuild_index.py
   ```

---

## 💡 Boas Práticas

### Quando Criar Novo Tipo?

✅ **CRIAR** quando:
- Exercícios do mesmo conceito têm abordagens diferentes
- Requerem competências distintas (gráfico vs. cálculo)
- Têm níveis de dificuldade claramente separados
- Podem ser agrupados pedagogicamente

❌ **NÃO CRIAR** quando:
- Diferença é apenas cosmética
- Pode ser resolvida com tags
- Tipo teria apenas 1-2 exercícios

### Nomenclatura de Tipos

- Use `snake_case` para IDs
- Seja descritivo mas conciso
- Exemplos:
  - ✅ `determinacao_analitica`
  - ✅ `teste_reta_horizontal`
  - ✅ `interpretacao_geometrica`
  - ❌ `exercicios_de_calculo_da_funcao_inversa`

### Tags Automáticas

- Tags do **conceito**: amplas (ex: `inversa`, `funcao`)
- Tags do **tipo**: específicas (ex: `calculo_analitico`, `grafico`)
- Tags **adicionais**: contextuais (ex: `funcao_linear`, `parabola`)

---

## 🎯 Exemplos de Tipos por Conceito

### Função Inversa
1. `determinacao_analitica` - Cálculo algébrico de f⁻¹(x)
2. `determinacao_grafica` - Obter gráfico por simetria y=x
3. `teste_reta_horizontal` - Verificar injetividade graficamente
4. `composicao` - f(f⁻¹(x)) = x e f⁻¹(f(x)) = x

### Derivadas (sugestão futura)
1. `aplicacao_regras` - Usar regras diretas
2. `derivada_composta` - Regra da cadeia
3. `interpretacao_geometrica` - Reta tangente
4. `taxa_variacao` - Aplicações práticas

### Limites (sugestão futura)
1. `calculo_direto` - Substituição
2. `levantamento_indeterminacao` - Resolver 0/0
3. `limites_laterais` - Esquerda e direita
4. `limites_infinito` - Comportamento assintótico

---

## 📚 Referências

- `add_exercise_with_types.py` - Script principal
- `modules_config.yaml` - Configuração de módulos e conceitos
- `index.json` - Índice global
- `.github/copilot-instructions.md` - Instruções para o agente Copilot

---

## 🔧 Scripts Utilitários

### Consolidar Metadados Existentes

Se tiver ficheiros `.json` individuais por exercício (estrutura antiga):

```bash
# Simular consolidação (dry-run)
python ExerciseDatabase/_tools/consolidate_type_metadata.py --concept 4-funcao_inversa

# Executar consolidação real (move IDs para metadata.json e remove .json individuais)
python ExerciseDatabase/_tools/consolidate_type_metadata.py --concept 4-funcao_inversa --execute
```

### Migrar Exercícios Antigos (sem tipos)

```bash
# Simular migração
python ExerciseDatabase/_tools/migrate_to_types.py --concept "4-funcao_inversa" --dry-run

# Executar migração
python ExerciseDatabase/_tools/migrate_to_types.py --concept "4-funcao_inversa" --execute
```

---

**Versão**: 3.0.1 (Metadados Consolidados)  
**Data**: 2025-11-19  
**Autor**: Sistema Exercises and Evaluation
