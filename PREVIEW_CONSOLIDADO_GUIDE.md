# 📄 Guia: Preview Consolidado

**Versão:** 3.1.1  
**Data:** 21 Novembro 2025  
**Novo Recurso:** Ficheiro único consolidado para preview

---

## 🎯 O Que Mudou?

### Antes (v3.1.0)
```
preview_temp/
├── exercise.tex
├── metadata.json
├── tipo_metadata.json
└── README_PREVIEW.txt
```
→ Múltiplos ficheiros separados
→ Tinha que abrir cada um individualmente

### Agora (v3.1.1) ✨
```
preview_temp/
├── PREVIEW_CONSOLIDADO.tex    ← TODO o conteúdo aqui!
├── exercise.tex                (mantido para compatibilidade)
├── metadata.json               (mantido para compatibilidade)
├── tipo_metadata.json          (mantido para compatibilidade)
└── README_PREVIEW.txt
```
→ **Um único ficheiro** com tudo estruturado
→ Mais fácil de rever e editar

---

## 📋 Estrutura do Ficheiro Consolidado

### Para Exercícios (.tex)

```latex
% ====================================================================
% PREVIEW CONSOLIDADO: Novo Exercício: MAT_A8MODELO_1SX_DVX_001
% Gerado em: 2025-11-21 10:04:05
% ====================================================================
%
% ATENÇÃO: Este é um ficheiro de PRÉ-VISUALIZAÇÃO
% O conteúdo abaixo será adicionado à base de dados após confirmação.
%
% ====================================================================

% --------------------------------------------------------------------
% FICHEIRO 1: MAT_A8MODELO_1SX_DVX_001.tex
% --------------------------------------------------------------------

% Exercise ID: MAT_A8MODELO_1SX_DVX_001
% Module: Módulo A8 - Modelos Discretos | Concept: Sistemas Numéricos
% Difficulty: 2/5 (Fácil) | Format: resposta_curta
% Tags: sistemas_numericos, binario, decimal
% Author: Professor | Date: 2025-11-21
% Status: active

\exercicio{Representa os seguintes números decimais em sistema de numeração binária}

% --------------------------------------------------------------------
% FICHEIRO 2: MAT_A8MODELO_1SX_DVX_001_metadata.json
% --------------------------------------------------------------------

% {
%   "id": "MAT_A8MODELO_1SX_DVX_001",
%   "version": "1.0",
%   "created": "2025-11-21",
%   "classification": {
%     "discipline": "matematica",
%     "module": "A8_modelos_discretos",
%     "concept": "1-sistemas_numericos",
%     "tipo": "determinacao_valores"
%   }
% }

% --------------------------------------------------------------------
% FICHEIRO 3: tipo_metadata_updated.json
% --------------------------------------------------------------------

% {
%   "tipo": "determinacao_valores",
%   "tipo_nome": "Determinação de valores",
%   "exercicios": ["MAT_A8MODELO_1SX_DVX_001"]
% }

% ====================================================================
% FIM DO PREVIEW
% ====================================================================
```

### Para Sebentas e Testes (.tex)

Mesmo formato, mas com o conteúdo LaTeX completo da sebenta ou teste.

### Para Outros Conteúdos (.txt)

Se não houver ficheiros `.tex`, gera um `.txt` com estrutura similar:
```
======================================================================
  PREVIEW CONSOLIDADO: Título
  Gerado em: 2025-11-21 10:04:05
======================================================================

ATENÇÃO: Este é um ficheiro de PRÉ-VISUALIZAÇÃO
O conteúdo abaixo será adicionado à base de dados após confirmação.

======================================================================

----------------------------------------------------------------------
  FICHEIRO 1: config.json
----------------------------------------------------------------------

{
  "name": "Test Configuration",
  "versions": 3
}

----------------------------------------------------------------------
  FICHEIRO 2: exercises_list.txt
----------------------------------------------------------------------

Exercise 1: MAT_A8...
Exercise 2: MAT_A9...

======================================================================
  FIM DO PREVIEW
======================================================================
```

---

## 🎨 Vantagens do Formato Consolidado

### 1. **Revisão Mais Rápida**
- Tudo num único ficheiro
- Scroll contínuo
- Contexto completo visível

### 2. **Edição Facilitada**
- Pode copiar/colar seções
- Comparar ficheiros lado a lado (no mesmo documento)
- Comentar ou marcar partes específicas

### 3. **Formato LaTeX Nativo**
- Comentários LaTeX válidos (%)
- Pode compilar partes se necessário
- Syntax highlighting funciona

### 4. **Backup Implícito**
- O ficheiro consolidado serve como snapshot completo
- Pode recuperar qualquer parte depois
- Histórico de o que foi gerado

### 5. **CI/CD Friendly**
- Um único ficheiro para validar
- Mais fácil de parsear em pipelines
- Logs mais limpos

---

## 🚀 Como Usar

### Modo Padrão (Consolidado)

```python
from preview_system import PreviewManager

preview = PreviewManager()  # consolidated_preview=True por padrão

content = {
    "exercise.tex": tex_content,
    "metadata.json": json_content
}

if preview.show_and_confirm(content, "Novo Exercício"):
    # Aprovado - salvar
    pass
```

### Modo Legado (Ficheiros Separados)

```python
preview = PreviewManager(consolidated_preview=False)

# Resto igual...
```

### Desabilitar Abertura Automática

```python
preview = PreviewManager(auto_open=False)

# Preview criado mas não abre VS Code automaticamente
```

---

## 📊 Comparação de Modos

| Aspecto | Consolidado (Novo) | Separado (Antigo) |
|---------|-------------------|-------------------|
| Ficheiros criados | 1 principal + originais | Apenas originais |
| Abertura em VS Code | Abre consolidado | Abre todos |
| Revisão | Scroll único | Múltiplos tabs |
| Edição | Num lugar só | Em vários ficheiros |
| Formato | LaTeX/TXT estruturado | Ficheiros originais |
| Performance | ✅ Rápido | ⚠️ Mais lento (múltiplos) |
| Compatibilidade | ✅ Total | ✅ Total |

---

## 🔧 Configuração

### Global (para todos os scripts)

Edite `preview_system.py`:

```python
class PreviewManager:
    def __init__(self, 
                 auto_open: bool = True, 
                 consolidated_preview: bool = True):  # ← Altere aqui
```

### Por Script

No início do script de geração:

```python
# Usar consolidado
preview = PreviewManager(consolidated_preview=True)

# Usar separado
preview = PreviewManager(consolidated_preview=False)

# Sem abertura automática
preview = PreviewManager(auto_open=False)

# Combinações
preview = PreviewManager(auto_open=False, consolidated_preview=True)
```

---

## 📝 Formato Detalhado

### Cabeçalho

```latex
% ====================================================================
% PREVIEW CONSOLIDADO: [Título do Preview]
% Gerado em: [Timestamp]
% ====================================================================
%
% ATENÇÃO: Este é um ficheiro de PRÉ-VISUALIZAÇÃO
% O conteúdo abaixo será adicionado à base de dados após confirmação.
%
% ====================================================================
```

### Seção de Ficheiro

```latex
% --------------------------------------------------------------------
% FICHEIRO [N]: [nome_do_ficheiro.ext]
% --------------------------------------------------------------------

[Conteúdo do ficheiro]
```

### JSON Comentado

Para ficheiros `.json`, cada linha é prefixada com `%`:

```latex
% {
%   "id": "value",
%   "nested": {
%     "key": "value"
%   }
% }
```

### Rodapé

```latex
% ====================================================================
% FIM DO PREVIEW
% ====================================================================
```

---

## 🧪 Exemplos Práticos

### Criar Exercício

```bash
python ExerciseDatabase/_tools/add_exercise_with_types.py
```

**Preview gerado:**
- `PREVIEW_CONSOLIDADO.tex` (principal - abre automaticamente)
- Contém: LaTeX do exercício + JSON de metadata + JSON do tipo

### Gerar Sebenta

```bash
python SebentasDatabase/_tools/generate_sebentas.py --module P4_funcoes
```

**Preview gerado:**
- `PREVIEW_CONSOLIDADO.tex` (principal)
- Contém: LaTeX completo da sebenta + metadados

### Gerar Teste

```bash
python SebentasDatabase/_tools/generate_tests.py --versions 3
```

**Preview gerado (para cada versão):**
- `PREVIEW_CONSOLIDADO.tex` (versão A)
- Contém: LaTeX do teste + JSON com lista de exercícios

---

## ❓ FAQ

### O ficheiro consolidado substitui os originais?

Não! Os ficheiros originais ainda são criados para compatibilidade. O consolidado é um **extra** para facilitar a revisão.

### Posso editar o ficheiro consolidado?

Sim! Você pode fazer alterações nele durante a revisão. Porém, ao confirmar, o sistema salva os ficheiros originais (não editados). O consolidado serve apenas para **revisão visual**.

### E se eu quiser os ficheiros separados?

Use `PreviewManager(consolidated_preview=False)` ou edite a configuração padrão no `preview_system.py`.

### O formato LaTeX é válido?

Sim! Todos os comentários usam `%` (sintaxe LaTeX válida). Você pode até compilar partes se quiser.

### Qual ficheiro abre no VS Code?

Por padrão, o **consolidado** abre primeiro. Se `consolidated_preview=False`, todos os ficheiros originais abrem.

### O preview no terminal mudou?

Não! O preview no terminal continua igual, mostrando as primeiras 20 linhas de cada ficheiro. O consolidado é um **adicional**.

---

## 🎯 Casos de Uso

### 1. Revisão Rápida

"Quero ver tudo de uma vez"
→ Modo consolidado (padrão)

### 2. Edição Detalhada

"Quero editar cada ficheiro separadamente"
→ Modo separado (`consolidated_preview=False`)

### 3. CI/CD Pipeline

"Quero validar automaticamente"
→ Consolidado + `--no-preview --auto-approve`

### 4. Documentação

"Quero guardar o que foi gerado"
→ Consolidado serve como snapshot completo

---

## 🔄 Migração

Se você tem scripts customizados:

### Antes (v3.1.0)
```python
preview = PreviewManager()
```

### Agora (v3.1.1)
```python
# Usar novo formato (recomendado)
preview = PreviewManager()  # consolidado por padrão

# OU manter comportamento antigo
preview = PreviewManager(consolidated_preview=False)
```

**Sem quebrar compatibilidade!** O comportamento padrão mudou, mas você pode voltar ao antigo.

---

## 📚 Referências

- **Sistema de Preview:** `PREVIEW_SYSTEM.md`
- **Quick Start:** `PREVIEW_QUICKSTART.md`
- **Código fonte:** `ExerciseDatabase/_tools/preview_system.py`
- **Conformidade:** `AGENTS_COMPLIANCE_v3.1.md`

---

## 🎉 Benefícios

1. ✅ **Mais rápido** - Um ficheiro em vez de muitos
2. ✅ **Mais limpo** - Tudo organizado e estruturado
3. ✅ **Mais fácil** - Scroll contínuo, contexto completo
4. ✅ **Compatível** - Ficheiros originais mantidos
5. ✅ **Flexível** - Pode desabilitar se preferir o antigo

---

**Versão:** 3.1.1  
**Status:** ✅ Produção  
**Recomendação:** Use o modo consolidado (padrão) para melhor experiência!
