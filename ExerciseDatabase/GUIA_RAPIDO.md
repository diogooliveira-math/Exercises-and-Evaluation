# 🚀 Guia Rápido - Sistema de Gestão de Exercícios v2.0

**Sistema Modular para Ensino Modular de Matemática**

---

## ✅ Sistema Testado e Funcional

**8/8 testes passaram com sucesso!**

- ✓ Criação de exercícios
- ✓ Validação de índice
- ✓ Pesquisa por módulo, conceito, dificuldade, tags
- ✓ Pesquisa complexa com múltiplos filtros
- ✓ Integridade de metadados

---

## 📋 Início Rápido

### 1. Adicionar Novo Exercício

```powershell
cd ExerciseDatabase\_tools
python add_exercise.py
```

**Fluxo simplificado:**
1. Escolher preset rápido (questão de aula, exercício de ficha, etc.) **OU** configuração manual
2. Selecionar módulo (A10, A11, A12, A13, A14)
3. Selecionar conceito específico
4. Digite enunciado e alíneas
5. Confirmar criação

**Tempo estimado:** 2-3 minutos por exercício

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

## 📂 Estrutura de Ficheiros

```
ExerciseDatabase/
├── modules_config.yaml          # Configuração de módulos e conceitos
├── index.json                   # Índice central (gerado automaticamente)
│
├── matematica/                  # Disciplina
│   ├── A10_funcoes/            # Módulo
│   │   ├── funcao_quadratica/  # Conceito
│   │   │   ├── MAT_A10_FUNCOES_FQX_001.tex
│   │   │   └── MAT_A10_FUNCOES_FQX_001.json
│   │   └── ...
│   └── ...
│
└── _tools/                      # Ferramentas
    ├── add_exercise.py         # ⭐ Adicionar exercícios
    ├── search_exercises.py     # 🔍 Pesquisar
    ├── create_test_exercises.py
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

## 📊 Metadados dos Exercícios

Cada exercício tem ficheiro `.json` com:

```json
{
  "id": "MAT_A10_FUNCOES_FQX_001",
  "module": {"id": "A10_funcoes", "name": "Módulo A10 - Funções"},
  "concept": {"id": "funcao_quadratica", "name": "Função Quadrática"},
  "classification": {
    "difficulty": 2,
    "difficulty_label": "Fácil",
    "tags": ["parabola", "vertice", "raizes"]
  },
  "exercise_type": "desenvolvimento",
  "evaluation": {
    "points": 10,
    "time_estimate_minutes": 15
  },
  "usage": {
    "times_used": 0,
    "contexts": []
  }
}
```

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

**Versão:** 2.0  
**Status:** ✅ Testado e Funcional (8/8 testes)  
**Data:** 2025-11-14
