# 🚀 START HERE - Guia Rápido Visual

## ⚡ 3 Passos para Começar

### 1️⃣ Abrir Terminal
```powershell
# Windows PowerShell
cd "c:\Users\diogo\OneDrive\AAA\Projects\Exercises and Evaluation\ExerciseDatabase\_tools"
```

### 2️⃣ Escolher Ação

#### 🆕 Adicionar Exercício Novo
```powershell
python add_exercise.py
```
→ Wizard interativo abre  
→ Escolhe preset ou manual  
→ 2-3 minutos = exercício pronto!

#### 🔍 Pesquisar Exercícios
```powershell
python search_exercises.py
```
→ 5 modos de pesquisa  
→ Filtros múltiplos  
→ Resultados instantâneos

#### ✅ Validar Sistema
```powershell
python run_tests.py
```
→ 8 testes executam  
→ Verifica integridade  
→ Deve dar 8/8 ✅

### 3️⃣ Seguir Wizard
```
O sistema guia-o passo a passo!
Apenas responda às perguntas.
```

---

## 📋 Fluxo Visual de Criação

```
START
  ↓
python add_exercise.py
  ↓
┌─────────────────────────────────┐
│ Modo de Criação:                │
│ 1. Presets Rápidos ⚡           │
│ 2. Configuração Manual 🎛️       │
└─────────────────────────────────┘
  ↓ [Escolhe 1]
┌─────────────────────────────────┐
│ Escolha Preset:                 │
│ 1. Questão Aula (10min, 2 al)  │
│ 2. Exercício Ficha (15min, 3al)│
│ 3. Teste Rápido (3min, EM)     │
│ 4. Desafio (30min, 4al)        │
└─────────────────────────────────┘
  ↓ [Escolhe 2]
┌─────────────────────────────────┐
│ Selecione MÓDULO:               │
│ 1. Módulo A10 - Funções         │
│ 2. Módulo A11 - Derivadas       │
│ 3. Módulo A12 - Otimização      │
│ 4. Módulo A13 - Limites         │
│ 5. Módulo A14 - Integrais       │
└─────────────────────────────────┘
  ↓ [Escolhe 1]
┌─────────────────────────────────┐
│ Selecione CONCEITO:             │
│ 1. Conceito de Função           │
│ 2. Gráfico de Função            │
│ 3. Monotonia de Funções         │
│ 4. Extremos                     │
│ 5. Função Quadrática            │
│ ...                             │
└─────────────────────────────────┘
  ↓ [Escolhe 5]
┌─────────────────────────────────┐
│ ✓ ID: MAT_A10_FUNCOES_FQX_002   │
│ ✓ Preset: Exercício de Ficha    │
│ ✓ Tags automáticas: parabola,   │
│   vertice, concavidade           │
└─────────────────────────────────┘
  ↓
┌─────────────────────────────────┐
│ Digite ENUNCIADO:               │
│ (linha vazia + Enter = termina) │
│                                 │
│ > Considere a função...         │
│ >                               │
│                                 │
└─────────────────────────────────┘
  ↓
┌─────────────────────────────────┐
│ Alínea a):                      │
│ > Determine o domínio...        │
│                                 │
│ Pontos: [5.0] _                 │
└─────────────────────────────────┘
  ↓ [Repete para b) e c)]
┌─────────────────────────────────┐
│ RESUMO:                         │
│ ID: MAT_A10_FUNCOES_FQX_002     │
│ Módulo: A10 - Funções           │
│ Conceito: Função Quadrática     │
│ Pontos: 15 | Tempo: 15min       │
│ Alíneas: 3                      │
│                                 │
│ Confirmar? [s/n]: _             │
└─────────────────────────────────┘
  ↓ [s]
┌─────────────────────────────────┐
│ ✓ Ficheiro criado!              │
│ ✓ Metadados criados!            │
│ ✓ Índice atualizado!            │
│                                 │
│ ✓ EXERCÍCIO CRIADO!             │
└─────────────────────────────────┘
END
```

---

## 🔍 Fluxo Visual de Pesquisa

```
START
  ↓
python search_exercises.py
  ↓
┌─────────────────────────────────┐
│ Modo de Pesquisa:               │
│ 1. Pesquisa Personalizada       │
│ 2. Ver Estatísticas             │
│ 3. Listar Todos                 │
│ 4. Rápida por Módulo            │
│ 5. Rápida por Conceito          │
└─────────────────────────────────┘
  ↓ [Escolhe 4]
┌─────────────────────────────────┐
│ Módulos disponíveis:            │
│ 1. Módulo A10 (2 exercícios)    │
│ 2. Módulo A11 (1 exercícios)    │
│ 3. Módulo A12 (1 exercícios)    │
│ 4. Módulo A13 (1 exercícios)    │
│ 5. Módulo A14 (0 exercícios)    │
└─────────────────────────────────┘
  ↓ [Escolhe 1]
┌─────────────────────────────────┐
│ RESULTADOS: 2 exercícios        │
│                                 │
│ 1. MAT_A10_FUNCOES_FQX_001      │
│    Conceito: Função Quadrática  │
│    Dif: 2/5 (Fácil) | Pts: 10   │
│    Tags: parabola, vertice...   │
│    📄 matematica/A10_funcoes... │
│                                 │
│ 2. MAT_A10_FUNCOES_MXX_001      │
│    Conceito: Monotonia          │
│    Dif: 3/5 (Médio) | Pts: 10   │
│    Tags: crescente, extremos... │
│    📄 matematica/A10_funcoes... │
└─────────────────────────────────┘
END
```

---

## 📊 Exemplo de Estatísticas

```
python search_exercises.py
→ Escolhe 2 (Ver Estatísticas)

================================================================================
ESTATÍSTICAS DA BASE DE DADOS
================================================================================

Total de Exercícios: 5
Última Atualização: 2025-11-14

📚 Por Módulo:
   • Módulo A10 - Funções: 2 exercícios
   • Módulo A11 - Derivadas: 1 exercícios
   • Módulo A12 - Otimização: 1 exercícios
   • Módulo A13 - Limites: 1 exercícios

💡 Por Conceito:
   • Função Quadrática: 1
   • Monotonia: 1
   • Taxa de Variação: 1
   • Problemas Otimização: 1
   • Cálculo Limites: 1

⭐ Por Dificuldade:
   • Fácil: 1 exercícios
   • Médio: 3 exercícios
   • Difícil: 1 exercícios

📝 Por Tipo:
   • Desenvolvimento: 5 exercícios
```

---

## 🎯 Atalhos Úteis

### Criar Exercício Rápido
```powershell
python add_exercise.py
# → 1 (Presets)
# → 2 (Exercício Ficha)
# → [Escolhe módulo]
# → [Escolhe conceito]
# → [Digite enunciado]
# → s (Confirmar)
```
**Tempo total:** 2-3 minutos ⚡

### Ver O Que Existe
```powershell
python search_exercises.py
# → 2 (Estatísticas)
```
**Resultado:** Visão geral completa 📊

### Validar Tudo
```powershell
python run_tests.py
```
**Resultado:** 8/8 testes ✅

---

## 📁 Onde Estão os Ficheiros?

```
ExerciseDatabase/
├── matematica/              ← Exercícios aqui
│   └── [módulo]/
│       └── [conceito]/
│           ├── [ID].tex     ← Conteúdo LaTeX
│           └── [ID].json    ← Metadados
│
├── modules_config.yaml      ← Configuração
├── index.json              ← Índice (automático)
│
└── _tools/                 ← Scripts
    ├── add_exercise.py    ← Usar este!
    ├── search_exercises.py ← E este!
    └── run_tests.py       ← Validar
```

---

## ❓ FAQ Rápido

**P: Quanto tempo para criar exercício?**  
R: 2-3 minutos com presets ⚡

**P: Quantos módulos disponíveis?**  
R: 5 módulos, 29 conceitos 📚

**P: Como pesquisar?**  
R: `python search_exercises.py` → 5 modos 🔍

**P: Como validar sistema?**  
R: `python run_tests.py` → 8/8 ✅

**P: Onde está documentação?**  
R: `GUIA_RAPIDO.md`, `RESUMO_FINAL.md` 📖

**P: Posso adicionar conceitos?**  
R: Sim! Edite `modules_config.yaml` 🔧

**P: IDs são automáticos?**  
R: Sim! Gerados automaticamente 🤖

**P: Tags são automáticas?**  
R: Sim! Por conceito, mas pode adicionar mais 🏷️

---

## 🎯 Objetivo Alcançado!

✅ Sistema modular implementado  
✅ Controlo granular por conceito  
✅ Criação rápida (2-3 min)  
✅ Pesquisa poderosa  
✅ 100% testado e funcional  

---

## 🚀 COMECE AGORA!

```powershell
cd "c:\Users\diogo\OneDrive\AAA\Projects\Exercises and Evaluation\ExerciseDatabase\_tools"
python add_exercise.py
```

**É só começar a digitar!** 🎓✨

---

**TIP:** Mantenha este ficheiro aberto enquanto usa o sistema!
