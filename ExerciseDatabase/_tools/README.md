# 🛠️ Ferramentas do Sistema - ExerciseDatabase

Ferramentas Python para gestão da base de dados de exercícios.

---

## 📋 Ficheiros

### 1. `add_exercise.py` ⭐
**Adicionar novos exercícios à base de dados**

```powershell
python add_exercise.py
```

**Funcionalidades:**
- Wizard interativo passo a passo
- Presets rápidos (questão aula, ficha, teste, desafio)
- Seleção de módulo e conceito
- Tags automáticas por conceito
- Geração automática de IDs
- Validação de dados
- Atualização automática do índice

**Tempo:** 2-3 minutos por exercício

---

### 2. `search_exercises.py` 🔍
**Pesquisar exercícios na base de dados**

```powershell
python search_exercises.py
```

**5 Modos de Pesquisa:**
1. Pesquisa Personalizada (múltiplos filtros)
2. Ver Estatísticas Globais
3. Listar Todos os Exercícios
4. Pesquisa Rápida por Módulo
5. Pesquisa Rápida por Conceito

**Filtros Disponíveis:**
- Módulo (A10, A11, A12, A13, A14)
- Conceito específico
- Dificuldade (1-5)
- Tipo de exercício
- Tags
- Pontuação (min/max)

---

### 3. `create_test_exercises.py` 🧪
**Criar exercícios de teste automaticamente**

```powershell
python create_test_exercises.py
```

Cria 5 exercícios de exemplo:
1. Função Quadrática (Fácil)
2. Monotonia (Médio)
3. Taxa de Variação (Médio)
4. Otimização (Difícil)
5. Limites (Médio)

Útil para:
- Testar o sistema
- Ver exemplos de estrutura
- Popular base de dados inicial

---

### 4. `run_tests.py` ✅
**Suite completa de testes do sistema**

```powershell
python run_tests.py
```

**8 Testes Executados:**
1. ✓ Criar Exercícios
2. ✓ Validar Índice
3. ✓ Pesquisa por Módulo
4. ✓ Pesquisa por Conceito
5. ✓ Pesquisa por Dificuldade
6. ✓ Pesquisa por Tags
7. ✓ Pesquisa Complexa
8. ✓ Validar Metadados

**Resultado:** Todos os testes passam (8/8) ✅

---

## 🚀 Uso Rápido

### Workflow Típico

1. **Adicionar exercício**
   ```powershell
   python add_exercise.py
   ```

2. **Pesquisar para verificar**
   ```powershell
   python search_exercises.py
   # Escolher opção 4 ou 5 para pesquisa rápida
   ```

3. **Ver estatísticas**
   ```powershell
   python search_exercises.py
   # Escolher opção 2
   ```

---

## 📦 Dependências

```powershell
pip install pyyaml
```

**Requisitos:**
- Python 3.7+
- PyYAML
- Módulos padrão: json, pathlib, datetime, re

---

## 🔧 Configuração

Todas as ferramentas usam:

**Ficheiro de configuração:** `../modules_config.yaml`
- Definição de módulos
- Conceitos por módulo
- Presets rápidos
- Níveis de dificuldade
- Tipos de exercício

**Índice central:** `../index.json`
- Gerado e atualizado automaticamente
- Não editar manualmente
- Contém todos os metadados para pesquisa rápida

---

## 📊 Estrutura de Dados

### Metadados de Exercício (.json)

```json
{
  "id": "MAT_A10_FUNCOES_FQX_001",
  "version": "1.0",
  "created": "2025-11-14",
  "modified": "2025-11-14",
  "author": "Nome do Professor",
  "module": {
    "id": "A10_funcoes",
    "name": "Módulo A10 - Funções"
  },
  "concept": {
    "id": "funcao_quadratica",
    "name": "Função Quadrática"
  },
  "classification": {
    "discipline": "matematica",
    "module": "A10_funcoes",
    "concept": "funcao_quadratica",
    "tags": ["parabola", "vertice", "concavidade", "raizes"],
    "difficulty": 2,
    "difficulty_label": "Fácil"
  },
  "exercise_type": "desenvolvimento",
  "content": {
    "has_multiple_parts": true,
    "parts_count": 3,
    "has_graphics": false,
    "requires_packages": ["amsmath", "amssymb"]
  },
  "evaluation": {
    "points": 10,
    "time_estimate_minutes": 15,
    "bloom_level": "aplicacao"
  },
  "solution": {
    "available": false,
    "file": ""
  },
  "usage": {
    "times_used": 0,
    "last_used": "",
    "contexts": []
  },
  "status": "active"
}
```

### Ficheiro LaTeX (.tex)

```latex
% Exercise ID: MAT_A10_FUNCOES_FQX_001
% Module: Módulo A10 - Funções | Concept: Função Quadrática
% Difficulty: 2/5 (Fácil) | Type: desenvolvimento
% Points: 10 | Time: 15 min
% Tags: parabola, vertice, concavidade, raizes
% Author: Nome do Professor | Date: 2025-11-14
% Status: active

\exercicio{Considere a função $f(x) = x^2 - 4x + 3$.}

\subexercicio{Determine o domínio e contradomínio da função.}

\subexercicio{Calcule as raízes da função.}

\subexercicio{Identifique o vértice da parábola.}

% Evaluation notes:
% Part a): 3 points
% Part b): 4 points
% Part c): 3 points
```

---

## 🎯 Exemplos de Uso

### Exemplo 1: Adicionar Exercício Rápido

```powershell
PS> python add_exercise.py

# 1. Escolher preset "Questão de Aula"
# 2. Módulo: A10_funcoes
# 3. Conceito: funcao_quadratica
# 4. Digite enunciado
# 5. Digite 2 alíneas
# 6. Confirmar

# ✓ Exercício criado em ~2 minutos
```

### Exemplo 2: Pesquisar Exercícios de Derivadas

```powershell
PS> python search_exercises.py

# Escolher opção 4 (Pesquisa Rápida por Módulo)
# Escolher: 2. Módulo A11 - Derivadas

# Resultado: Lista de todos exercícios de derivadas
```

### Exemplo 3: Ver Estatísticas

```powershell
PS> python search_exercises.py

# Escolher opção 2 (Ver Estatísticas)

# Mostra:
# - Total de exercícios
# - Por módulo
# - Por conceito (top 10)
# - Por dificuldade
# - Por tipo
```

---

## 🐛 Troubleshooting

### Erro: ImportError yaml

```powershell
pip install pyyaml
```

### Erro: "Config file not found"

Verifique que está na pasta correta:
```powershell
cd ExerciseDatabase\_tools
ls ../modules_config.yaml  # Deve existir
```

### Erro: "Index not found"

Execute primeiro:
```powershell
python create_test_exercises.py
# OU
python add_exercise.py
```

### Índice corrompido

Recrie executando:
```powershell
python run_tests.py
```

---

## 📈 Performance

- **Adicionar exercício:** < 3 segundos (após input do utilizador)
- **Pesquisa simples:** < 0.1 segundos
- **Pesquisa complexa:** < 0.5 segundos
- **Validação completa:** < 2 segundos

**Testado com:** 5+ exercícios  
**Escalável para:** 1000+ exercícios

---

## 🔄 Workflow de Desenvolvimento

### Para Adicionar Nova Funcionalidade

1. Editar `modules_config.yaml` (se necessário)
2. Modificar scripts conforme necessário
3. Testar com `run_tests.py`
4. Verificar integridade do índice

### Para Adicionar Novo Módulo

1. Editar `modules_config.yaml`:
   ```yaml
   A15_novo_modulo:
     name: "Módulo A15 - Nome"
     duration_hours: 25
     concepts:
       - id: conceito1
         name: "Conceito 1"
         tags: [tag1, tag2]
   ```

2. Executar `python add_exercise.py` - novo módulo aparece automaticamente

---

## 📝 Notas

- IDs são gerados automaticamente e sequenciais
- Tags automáticas vêm da configuração de conceitos
- Índice é atualizado a cada exercício adicionado
- Metadados JSON facilitam pesquisas rápidas
- LaTeX é legível e editável manualmente se necessário

---

**Versão:** 2.0  
**Status:** Testado e Funcional  
**Manutenção:** Consulte `run_tests.py` para validação
