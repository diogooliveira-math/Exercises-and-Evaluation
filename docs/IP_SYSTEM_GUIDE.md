# 🎯 Sistema de Testes baseado em IPs (Itens de Prova)

> **Versão 3.5** - Sistema modular para geração de testes usando identificadores hierárquicos

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Conceitos Fundamentais](#conceitos-fundamentais)
3. [Workflow Completo](#workflow-completo)
4. [Uso Prático](#uso-prático)
5. [Estrutura de Templates](#estrutura-de-templates)
6. [Referência Técnica](#referência-técnica)

---

## Visão Geral

O **Sistema de IPs** permite criar testes selecionando exercícios através de identificadores hierárquicos estáveis. Inspirado na estrutura QA2, oferece:

✅ **IDs Estáveis**: Cada exercício tem um IP único no formato `D.M.C.T.E`  
✅ **Seleção Flexível**: Use IPs individuais ou wildcards (`1.2.3.*`)  
✅ **Numeração Automática**: Exercícios numerados sequencialmente no teste  
✅ **Sub-variants**: Suporte automático para exercícios com múltiplas variantes  
✅ **Preview Integrado**: Revisão antes da compilação  
✅ **Templates Modulares**: Estrutura reutilizável baseada em QA2

---

## Conceitos Fundamentais

### IP (Item de Prova)

Formato: `D.M.C.T.E`

```
1.2.3.4.5
│ │ │ │ └─── Exercise: número do exercício dentro do tipo
│ │ │ └───── Type: tipo de exercício (determinação analítica, gráfica, etc.)
│ │ └─────── Concept: conceito matemático (função inversa, derivadas, etc.)
│ └───────── Module: módulo/tema do currículo
└─────────── Discipline: disciplina (matemática, física, etc.)
```

**Exemplo real:**
```
1.2.4.1.3
│ │ │ │ └─── Exercício #3
│ │ │ └───── Tipo: Determinação Analítica
│ │ └─────── Conceito: Função Inversa
│ └───────── Módulo: P4 - Funções
└─────────── Disciplina: Matemática
```

### Wildcards

Selecione múltiplos exercícios com `*`:

```bash
# Todos os exercícios de determinação analítica de função inversa
1.2.4.1.*

# Todos os exercícios sobre função inversa
1.2.4.*

# Todos os exercícios do módulo P4
1.2.*
```

---

## Workflow Completo

### 1️⃣ Migrar Exercícios para IPs

**Primeira vez** (criar registry):

```bash
# Preview dos IPs que serão atribuídos
python scripts/migrate_ips.py --dry-run --base ExerciseDatabase

# Aplicar migração
python scripts/migrate_ips.py --apply --base ExerciseDatabase
```

Isto cria:
- `ExerciseDatabase/_registry/ip_registry.json` (registry global)
- `exercise.json` em cada pasta de exercício
- `_meta.json` em cada pasta de conceito

### 2️⃣ Consultar IPs Disponíveis

```bash
# Lookup de IP específico
python scripts/ip_lookup.py 1.2.4.1.3

# Ver exercícios de um conceito
python scripts/ip_lookup.py "1.2.4.*"

# Validar consistência do registry
python scripts/check_registry_consistency.py
```

### 3️⃣ Gerar Teste

**Via VS Code Task** (recomendado):
```
Ctrl+Shift+P → Tasks: Run Task → 🎯 Gerar Teste (por IPs)
```

**Via CLI**:
```bash
# Teste com IPs específicos
python SebentasDatabase/_tools/generate_test_from_ips.py \
  --ips "1.2.4.1.3,1.2.4.1.5,1.2.4.2.1" \
  --title "Teste de Funções Inversas" \
  --author "Prof. Silva"

# Teste com wildcard (todos de determinação analítica)
python SebentasDatabase/_tools/generate_test_from_ips.py \
  --ips "1.2.4.1.*" \
  --title "Treino - Determinação Analítica"

# Sem preview e sem compilar
python SebentasDatabase/_tools/generate_test_from_ips.py \
  --ips "1.2.4.1.3" \
  --no-preview \
  --no-compile
```

### 4️⃣ Resultado

Estrutura gerada em `SebentasDatabase/tests/test_ips_TIMESTAMP/`:

```
test_ips_20251201_153045/
├── test.tex              # Documento principal
├── exercises.tex         # Lista de includes modulares
├── test.pdf             # PDF compilado
└── exercises.d/         # Macros de suporte
    ├── setup-counter.tex
    └── include-exercise.tex
```

---

## Uso Prático

### Caso 1: Teste sobre Função Inversa

**Objetivo**: Criar teste com 4 exercícios variados sobre função inversa

```bash
# 1. Descobrir IPs disponíveis
python scripts/ip_lookup.py "1.2.4.*"

# Output mostra:
# 1.2.4.1.1 - Determinação Analítica: f(x) = 2x + 3
# 1.2.4.1.2 - Determinação Analítica: f(x) = x²
# 1.2.4.2.1 - Determinação Gráfica: simetria eixo y=x
# 1.2.4.3.1 - Teste Reta Horizontal

# 2. Gerar teste com seleção manual
python SebentasDatabase/_tools/generate_test_from_ips.py \
  --ips "1.2.4.1.1,1.2.4.1.2,1.2.4.2.1,1.2.4.3.1" \
  --title "Teste - Função Inversa" \
  --author "Prof. João Santos"
```

### Caso 2: Bateria de Treino (Wildcard)

**Objetivo**: Todos os exercícios de determinação analítica para treino

```bash
python SebentasDatabase/_tools/generate_test_from_ips.py \
  --ips "1.2.4.1.*" \
  --title "Treino Intensivo - Determinação Analítica" \
  --no-preview \
  --auto-approve
```

### Caso 3: Teste Misto de Módulo Completo

**Objetivo**: 2 exercícios de cada tipo do módulo P4

```bash
# Usar múltiplos IPs específicos
python SebentasDatabase/_tools/generate_test_from_ips.py \
  --ips "1.2.4.1.1,1.2.4.1.2,1.2.4.2.1,1.2.4.2.2,1.2.4.3.1,1.2.4.3.2" \
  --title "Avaliação Sumativa - Módulo P4"
```

---

## Estrutura de Templates

### Template Modular (QA2-inspired)

Baseado na estrutura de referência em `reference/QA2/`:

```latex
\documentclass[a4paper,12pt]{article}
\input{config/packages}
\input{config/style}

\begin{document}
\maketitle
\espacoAluno

% Exercícios modulares
\input{exercises}

\end{document}
```

### exercises.tex (Gerado Automaticamente)

```latex
% Load counter and include wrapper
\input{exercises.d/setup-counter}
\input{exercises.d/include-exercise}

% Exercise inclusions
\IncludeExercise{../../../ExerciseDatabase/.../MAT_P4.../main}
\IncludeExercise{../../../ExerciseDatabase/.../MAT_P4.../main}
```

### \IncludeExercise Macro

```latex
\providecommand{\IncludeExercise}[1]{%
  \begingroup
    \refstepcounter{exercise}%
    \noindent\textbf{Exercício \theexercise.}\par
    \showexerciciotitlefalse  % Desabilita heading do exercício
    \input{#1}%
    \showexerciciotitletrue   % Re-habilita para próximo
  \endgroup
}
```

**Comportamento:**
1. Incrementa contador de exercício
2. Imprime "**Exercício N.**"
3. Desabilita heading automático do `\exercicio{}`
4. Inclui conteúdo do exercício
5. Restaura heading para próxima inclusão

---

## Referência Técnica

### Scripts Principais

| Script | Função |
|--------|--------|
| `migrate_ips.py` | Atribuir IPs a exercícios existentes |
| `ip_lookup.py` | Consultar IPs e resolver wildcards |
| `generate_test_from_ips.py` | Gerar teste por IPs |
| `check_registry_consistency.py` | Validar registry vs filesystem |
| `registry_repair.py` | Reparar registry corrompido |

### Flags do Gerador

```bash
--ips              # IPs separados por vírgula ou wildcards
--title            # Título do teste
--author           # Autor
--output           # Diretório de saída (padrão: auto)
--no-preview       # Pular preview
--auto-approve     # Aprovar automaticamente
--no-compile       # Só gerar .tex
```

### VS Code Tasks

| Task | Descrição |
|------|-----------|
| `🎯 Gerar Teste (por IPs)` | Interface interativa para geração |
| `📚 Gerar Sebenta (Direto)` | Sebenta com suporte a IPs via `SEBENTA_IPS` |
| `🔍 Pesquisar Exercícios` | Busca tradicional (não por IP) |

### Variáveis de Ambiente

Para usar com sebentas via `run_generate_sebenta_task.py`:

```bash
SEBENTA_IPS="1.2.4.1.3,1.2.4.2.1"
SEBENTA_NO_PREVIEW=1
SEBENTA_AUTO_APPROVE=1
python scripts/run_generate_sebenta_task.py
```

---

## Estrutura de Ficheiros

### Registry (`ExerciseDatabase/_registry/ip_registry.json`)

```json
{
  "version": 1,
  "disciplines": {
    "matematica": {
      "id": 1,
      "label": "matematica",
      "modules": {
        "P4_funcoes": {
          "id": 2,
          "label": "P4_funcoes",
          "concepts": {
            "4-funcao_inversa": {
              "id": 4,
              "label": "4-funcao_inversa",
              "types": {
                "determinacao_analitica": {
                  "id": 1,
                  "label": "determinacao_analitica",
                  "exercises": {
                    "MAT_P4FUNCOE_4FIN_ANA_001": {
                      "id": 3,
                      "label": "MAT_P4FUNCOE_4FIN_ANA_001",
                      "path": "matematica/P4_funcoes/4-funcao_inversa/determinacao_analitica/MAT_P4FUNCOE_4FIN_ANA_001"
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  },
  "ips": {
    "1.2.4.1.3": {
      "path": "matematica/P4_funcoes/4-funcao_inversa/determinacao_analitica/MAT_P4FUNCOE_4FIN_ANA_001",
      "parts": ["matematica", "P4_funcoes", "4-funcao_inversa", "determinacao_analitica", "MAT_P4FUNCOE_4FIN_ANA_001"],
      "label": "MAT_P4FUNCOE_4FIN_ANA_001",
      "assigned_at": 1701435600
    }
  }
}
```

### Metadata por Exercício (`exercise.json`)

```json
{
  "ip": "1.2.4.1.3",
  "ids": {
    "discipline": 1,
    "module": 2,
    "concept": 4,
    "type": 1,
    "exercise": 3
  },
  "label": "MAT_P4FUNCOE_4FIN_ANA_001",
  "path": "matematica/P4_funcoes/4-funcao_inversa/determinacao_analitica/MAT_P4FUNCOE_4FIN_ANA_001",
  "assigned_at": 1701435600
}
```

---

## Troubleshooting

### ❌ "No exercises resolved for IPs"

**Causa**: IP não existe no registry ou wildcard não encontrou matches

**Solução**:
```bash
# Verificar se IP existe
python scripts/ip_lookup.py 1.2.4.1.3

# Verificar consistência
python scripts/check_registry_consistency.py

# Re-migrar se necessário
python scripts/migrate_ips.py --apply --base ExerciseDatabase
```

### ❌ "IP Resolver não disponível"

**Causa**: Módulo `ip_resolver.py` não encontrado

**Solução**:
```bash
# Verificar existência
ls ExerciseDatabase/_tools/ip_resolver.py

# Verificar imports
python -c "from ExerciseDatabase._tools.ip_resolver import IPResolver; print('OK')"
```

### ❌ Paths relativos quebrados

**Causa**: Template compilado em diretório diferente do esperado

**Solução**: O gerador calcula paths relativos automaticamente. Se persistir:
```python
# No generate_test_from_ips.py, ajustar cálculo de rel_path
rel_path = Path("../../..") / "ExerciseDatabase" / exercise_path.relative_to(EXERCISE_DB)
```

---

## Próximos Passos

### Melhorias Planejadas

- [ ] Interface web para seleção visual de IPs
- [ ] Suporte a tags e filtros no lookup
- [ ] Geração de testes aleatórios por critérios (dificuldade, tipo)
- [ ] Estatísticas de uso de exercícios
- [ ] Versionamento de IPs (deprecation, migration)

### Contribuir

Documentação adicional:
- `docs/ip_registry.md` - Documentação completa do registry
- `AGENTS.md` - Instruções para agentes AI
- `copilot-instructions.md` - Guia para Copilot

---

**Versão**: 3.5  
**Data**: 2025-12-01  
**Autor**: Sistema de Exercises and Evaluation  
**Referência**: QA2 modular test system
