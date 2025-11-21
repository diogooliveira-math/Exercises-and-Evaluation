# 🐛 FIX: P2_Estatística → P2_estatistica

**Problema:** Módulo P2_Estatística não estava acessível  
**Causa:** Nome com acento (í) no YAML  
**Solução:** Renomear para `P2_estatistica` (sem acento)

---

## 🔍 Diagnóstico

### Problema Identificado

**No `modules_config.yaml`:**
```yaml
matematica:
  P2_Estatística:  ← PROBLEMA: Acento + Maiúscula
```

**Por que não funcionava:**
- ❌ Acentos em nomes de diretórios causam problemas em Windows/Python
- ❌ Inconsistência de capitalização (Estatística vs estatistica)
- ❌ Scripts Python não conseguiam criar diretórios com acentos

---

## ✅ Solução Aplicada

### 1. Renomear no YAML

**Antes:**
```yaml
P2_Estatística:
```

**Depois:**
```yaml
P2_estatistica:
```

**Benefício:** 
- ✅ Compatível com sistemas de ficheiros
- ✅ Sem problemas de encoding
- ✅ Consistente com outros módulos (A8, A9, P4)

---

### 2. Criar Estrutura de Diretórios

**ExerciseDatabase:**
```
matematica/
└── P2_estatistica/
    ├── 0-revisoes/
    ├── 1-Medicoes_basicas/
    └── 2-Variabilidade/
```

**SebentasDatabase:**
```
matematica/
└── P2_estatistica/
    ├── 0-revisoes/pdfs/
    ├── 1-Medicoes_basicas/pdfs/
    └── 2-Variabilidade/pdfs/
```

---

## 🎯 Resultado

### Antes
```
Módulos disponíveis em ExerciseDatabase:
  • A8_modelos_discretos
  • A9_funcoes_crescimento
  • P1_modelos_matematicos_para_a_cidadania
  • P4_funcoes
```

### Depois ✅
```
Módulos disponíveis em ExerciseDatabase:
  • P2_estatistica          ← NOVO!
  • A8_modelos_discretos
  • A9_funcoes_crescimento
  • P1_modelos_matematicos_para_a_cidadania
  • P4_funcoes
```

---

## 📋 Conceitos Criados

Dentro de `P2_estatistica`:

1. **0-revisoes** - Revisões Iniciais
   - Tags: revisao, consolidacao, percentagens, regra_de_tres_simples

2. **1-Medicoes_basicas** - Coleta e Organização de Dados
   - Tags: calculos_com_dados, médias, tabelas, manipulacao_dados

3. **2-Variabilidade** - Medidas de Variabilidade
   - Tags: variabilidade, desvio_medio, variancia, desvio_padrao

---

## 🚀 Como Usar Agora

### Via Sistema Mínimo (⚡)

```latex
% Módulo: P2_estatistica
% Conceito: 0-revisoes

\exercicio{
    Calcule 20% de 150.
}
```

### Via Template Completo (📝)

```latex
% Disciplina: matematica
% Módulo: P2_estatistica
% Conceito: 1-Medicoes_basicas
% Tipo: calculo_direto
```

---

## 🛡️ Prevenção Futura

### ✅ Regras para Nomes de Módulos

1. **Usar snake_case** (letras minúsculas + underscore)
2. **Sem acentos** (á, é, í, ó, ú, ã, õ, ç)
3. **Sem espaços** (usar `_`)
4. **Consistente** com padrão existente

### ❌ Evitar

```yaml
P2_Estatística     ❌ Acento + Maiúscula
P2 Estatística     ❌ Espaço
P2-Estatística     ❌ Hífen + Acento
P2_ESTATISTICA     ❌ Tudo maiúscula
```

### ✅ Usar

```yaml
P2_estatistica     ✅ Snake_case
A8_modelos         ✅ Sem acentos
P4_funcoes         ✅ Consistente
```

---

## 🔧 Comandos Executados

```powershell
# 1. Criar diretórios em ExerciseDatabase
New-Item -ItemType Directory -Force -Path "ExerciseDatabase\matematica\P2_estatistica\0-revisoes"
New-Item -ItemType Directory -Force -Path "ExerciseDatabase\matematica\P2_estatistica\1-Medicoes_basicas"
New-Item -ItemType Directory -Force -Path "ExerciseDatabase\matematica\P2_estatistica\2-Variabilidade"

# 2. Criar diretórios em SebentasDatabase
New-Item -ItemType Directory -Force -Path "SebentasDatabase\matematica\P2_estatistica\0-revisoes\pdfs"
New-Item -ItemType Directory -Force -Path "SebentasDatabase\matematica\P2_estatistica\1-Medicoes_basicas\pdfs"
New-Item -ItemType Directory -Force -Path "SebentasDatabase\matematica\P2_estatistica\2-Variabilidade\pdfs"
```

---

## ✅ Verificação

```powershell
# Listar módulos
python -c "import yaml; cfg=yaml.safe_load(open('ExerciseDatabase/modules_config.yaml','r',encoding='utf-8')); print('\n'.join(cfg['matematica'].keys()))"
```

**Output:**
```
P2_estatistica     ✅
A8_modelos_discretos
A9_funcoes_crescimento
P4_funcoes
...
```

---

## 📊 Status Atual

| Módulo | ExerciseDatabase | SebentasDatabase | Status |
|--------|------------------|------------------|--------|
| P2_estatistica | ✅ | ✅ | **Pronto** |
| 0-revisoes | ✅ | ✅ pdfs/ | Pronto |
| 1-Medicoes_basicas | ✅ | ✅ pdfs/ | Pronto |
| 2-Variabilidade | ✅ | ✅ pdfs/ | Pronto |

---

**Problema resolvido!** ✅  
**Módulo P2_estatistica agora está disponível para criar exercícios.**

---

**Data:** 2025-11-21  
**Fix aplicado por:** Sistema de inferência  
**Tempo total:** ~2 minutos
