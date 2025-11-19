# 🚀 Guia Rápido - Sistema de Gestão de Exercícios v3.0.1

**Sistema Modular com TIPOS de Exercícios - Ensino Modular de Matemática**

---

## 🆕 NOVO: Estrutura com Tipos (v3.0)

Hierarquia: `disciplina → tema → conceito → **TIPO** → exercício`

**Exemplo**: Função Inversa tem 3 tipos:
- `determinacao_analitica` (cálculo algébrico) - 5 exercícios
- `determinacao_grafica` (gráfico por simetria) - 5 exercícios
- `teste_reta_horizontal` (verificar injetividade) - 5 exercícios

---

## ✅ Sistema Testado e Funcional

**8/8 testes passaram com sucesso!**

- ✓ Criação de exercícios **com tipos**
- ✓ Validação de índice
- ✓ Pesquisa por módulo, conceito, **tipo**, dificuldade, tags
- ✓ Pesquisa complexa com múltiplos filtros
- ✓ Integridade de metadados **consolidados**

---

## 📋 Início Rápido

### 1. Adicionar Novo Exercício (COM TIPOS)

```powershell
cd ExerciseDatabase\_tools
python add_exercise_with_types.py  # ← USE ESTE!
```

**Fluxo simplificado:**
1. Escolher preset rápido (questão de aula, exercício de ficha, etc.) **OU** configuração manual
2. Selecionar módulo (A10, A11, A12, A13, A14)
3. Selecionar conceito específico
4. **🆕 Selecionar ou criar TIPO de exercício**
5. Digite enunciado e alíneas
6. Confirmar criação

**Tempo estimado:** 2-3 minutos por exercício

**Script antigo** (sem tipos, evitar):
```powershell
python add_exercise.py  # ⚠️ NÃO usar para novos exercícios
```

### 2. Pesquisar Exercícios

```powershell
cd ExerciseDatabase\_tools
python search_exercises.py
```

**5 modos de pesquisa:**
1. **Pesquisa Personalizada** - Múltiplos filtros combinados
2. **Ver Estatísticas** - Visão geral da base de dados
3. **Listar Todos** - Ver todos os exercícios
4. **Pesquisa Rápida por Módulo** - Filtrar por módulo específico
5. **Pesquisa Rápida por Conceito** - Filtrar por conceito dentro de módulo

### 3. Executar Testes

```powershell
cd ExerciseDatabase\_tools
python run_tests.py
```

Valida todo o sistema e cria exercícios de exemplo.

---

## 📚 Módulos Disponíveis

| Código | Nome | Conceitos |
|--------|------|-----------|
| **A10** | Funções | 8 conceitos (função básica, gráfico, monotonia, extremos, quadrática, módulo, composta, inversa) |
| **A11** | Derivadas | 6 conceitos (taxa variação, definição, regras, cadeia, ordem superior, aplicações) |
| **A12** | Otimização | 4 conceitos (monotonia, extremos, problemas, modelação) |
| **A13** | Limites | 6 conceitos (conceito, cálculo, laterais, infinito, indeterminações, continuidade) |
| **A14** | Integrais | 5 conceitos (primitiva, indefinido, definido, métodos, aplicações) |

---

## 🎯 Presets Rápidos

| Preset | Tipo | Dificuldade | Pontos | Tempo | Alíneas |
|--------|------|-------------|--------|-------|---------|
| **Questão de Aula** | Desenvolvimento | Fácil (2) | 10 | 10 min | 2 |
| **Exercício de Ficha** | Desenvolvimento | Médio (3) | 15 | 15 min | 3 |
| **Teste Rápido** | Escolha Múltipla | Fácil (2) | 5 | 3 min | 1 |
| **Desafio Avançado** | Desenvolvimento | Muito Difícil (5) | 20 | 30 min | 4 |

---

## 📂 Estrutura de Ficheiros (v3.0 com TIPOS)

```
ExerciseDatabase/
├── modules_config.yaml          # Configuração de módulos e conceitos
├── index.json                   # Índice central (gerado automaticamente)
│
├── matematica/                  # Disciplina
│   ├── P4_funcoes/             # Módulo
│   │   ├── 4-funcao_inversa/   # Conceito
│   │   │   ├── determinacao_analitica/     # 🆕 TIPO
│   │   │   │   ├── metadata.json          # Lista de IDs do tipo
│   │   │   │   ├── MAT_P4_..._ANA_001.tex # Exercício
│   │   │   │   └── MAT_P4_..._ANA_005.tex
│   │   │   ├── determinacao_grafica/
│   │   │   │   ├── metadata.json
│   │   │   │   └── [5 .tex files]
│   │   │   └── teste_reta_horizontal/
│   │   │       ├── metadata.json
│   │   │       └── [5 .tex files]
│   │   └── ...
│   └── ...
│
└── _tools/                      # Ferramentas
    ├── add_exercise_with_types.py  # ⭐ Adicionar (COM TIPOS)
    ├── generate_variant.py     # 🔄 Gerar variantes
    ├── consolidate_type_metadata.py # 🔧 Consolidar metadados
    ├── search_exercises.py     # 🔍 Pesquisar
    └── run_tests.py            # ✓ Testes
```

---

## 🏷️ Sistema de IDs

**Formato:** `MAT_MODULO_CONCEITO_NNN`

**Exemplos:**
- `MAT_A10_FUNCOES_FQX_001` - Módulo A10, Função Quadrática, nº 1
- `MAT_A11_DERIVADAS_TVX_002` - Módulo A11, Taxa Variação, nº 2
- `MAT_A12_OTIMIZACAO_POX_001` - Módulo A12, Problemas Otimização, nº 1

IDs são **gerados automaticamente** e sequenciais.

---

## 🔍 Exemplos de Pesquisa

### Exemplo 1: Todos os exercícios do Módulo A10
```python
# Via Python
results = search_exercises(module="A10_funcoes")
```

### Exemplo 2: Exercícios de otimização, dificuldade 4-5
```python
results = search_exercises(
    module="A12_otimizacao",
    min_difficulty=4
)
```

### Exemplo 3: Exercícios com tag "velocidade"
```python
results = search_exercises(tags=["velocidade"])
```

### Exemplo 4: Pesquisa complexa
```python
results = search_exercises(
    module="A10_funcoes",
    concept="funcao_quadratica",
    difficulty=2,
    exercise_type="desenvolvimento",
    min_points=10,
    max_points=15
)
```

---

## 📊 Metadados dos Exercícios (v3.0.1 Consolidado)

### Metadata do Tipo (`tipo/metadata.json`)

```json
{
  "tipo": "determinacao_analitica",
  "tipo_nome": "Determinação Analítica",
  "conceito": "4-funcao_inversa",
  "tema": "P4_funcoes",
  "disciplina": "matematica",
  "descricao": "Exercícios focados no cálculo algébrico...",
  "tags_tipo": ["calculo_analitico", "expressao_analitica"],
  "caracteristicas": {
    "requer_calculo": true,
    "requer_grafico": false
  },
  "dificuldade_sugerida": {"min": 2, "max": 4},
  "exercicios": [
    "MAT_P4FUNCOE_4FIN_ANA_001",
    "MAT_P4FUNCOE_4FIN_ANA_002",
    "MAT_P4FUNCOE_4FIN_ANA_005"
  ]
}
```

**IMPORTANTE**: Apenas o `metadata.json` do tipo existe. Não há ficheiros `.json` individuais por exercício (apenas `.tex`).

---

## 🎨 Personalização

### Adicionar Novo Conceito

Edite `modules_config.yaml`:

```yaml
matematica:
  A10_funcoes:
    concepts:
      - id: novo_conceito
        name: "Nome do Conceito"
        tags: [tag1, tag2, tag3]
```

### Adicionar Novo Preset

```yaml
quick_presets:
  meu_preset:
    name: "Meu Preset Personalizado"
    type: desenvolvimento
    difficulty: 3
    points: 12
    time_minutes: 18
    parts: 3
```

---

## 💡 Dicas de Uso

### Para Rapidez
1. Use **presets** - configuração em segundos
2. Tags são **automáticas** por conceito
3. IDs são **gerados automaticamente**

### Para Organização
1. Cada conceito = pasta própria
2. Índice atualizado automaticamente
3. Pesquisa rápida por qualquer critério

### Para Ensino Modular
1. Exercícios organizados por **módulo** e **conceito**
2. Fácil criar séries para cada módulo
3. Controlo granular por conceito específico

---

## 🔧 Resolução de Problemas

### Erro: "modules_config.yaml não encontrado"
```powershell
# Verificar localização
cd ExerciseDatabase
ls modules_config.yaml
```

### Erro: "ModuleNotFoundError: No module named 'yaml'"
```powershell
# Instalar PyYAML
pip install pyyaml
```

### Índice desatualizado
```powershell
# Recriar índice
cd ExerciseDatabase\_tools
python run_tests.py
```

---

## 📈 Estatísticas Atuais

Após executar `run_tests.py`:

- **Total:** 5 exercícios de exemplo criados
- **Módulos:** 4 módulos com exercícios
- **Conceitos:** 5 conceitos diferentes
- **Dificuldades:** Fácil (1), Médio (3), Difícil (1)
- **Tipo:** 100% desenvolvimento

---

## 🎯 Próximos Passos Sugeridos

1. **Adicionar mais exercícios** ao banco usando `add_exercise.py`
2. **Explorar pesquisas** com `search_exercises.py`
3. **Personalizar presets** em `modules_config.yaml`
4. **Criar scripts de geração de exames** (próxima fase)
5. **Exportar para LaTeX compilável** (integração com Teste_modelo)

---

## 📞 Suporte

- Documentação completa: `README.md` na raiz do projeto
- Roadmap: `TODO.md`
- Testes: `run_tests.py` para validar sistema

---

**Versão:** 3.0.1 (Tipos + Metadados Consolidados)  
**Status:** ✅ Testado e Funcional (8/8 testes)  
**Data:** 2025-11-19  

**Mudanças v3.0 → v3.0.1:**
- 🆕 Tipos de exercícios por conceito
- 📦 Metadados consolidados (`metadata.json` por tipo)
- 🔄 Scripts atualizados (`generate_variant.py`, `import_qa2_exercises.py`)
- 🔧 Novo utilitário: `consolidate_type_metadata.py`
