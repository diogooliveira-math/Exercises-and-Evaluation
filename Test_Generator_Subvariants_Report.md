# Relatório: Como o Test Generator Lida com Exercícios com Sub-Variants

**Data:** 25 de novembro de 2025  
**Autor:** Análise Automática  
**Objetivo:** Avaliar o comportamento do sistema de geração de testes (`generate_test_template.py`) quando confrontado com exercícios que possuem sub-variants (várias alíneas organizadas em pastas com `main.tex` e `subvariant_*.tex`).

## Contexto

### Estrutura de Exercícios com Sub-Variants

A partir da versão 3.4 do sistema, exercícios complexos podem ser organizados em pastas com a seguinte estrutura:

```
MAT_P4FUNCOE_4FIN_ANA_001/
├── main.tex              # Arquivo principal que inclui sub-variants
├── subvariant_1.tex      # Primeira alínea
├── subvariant_2.tex      # Segunda alínea
└── ...
```

O `main.tex` contém `\input{subvariant_N}` para incluir cada alínea.

### Sistema Testado

- **Script:** `SebentasDatabase/_tools/generate_test_template.py`
- **Versão:** Atual (25/11/2025)
- **Método:** Análise do código fonte + testes funcionais

## Metodologia de Testes

Foram realizados 4 testes principais:

1. **Teste 1:** Carregamento de exercício normal (arquivo `.tex` único)
2. **Teste 2:** Carregamento de exercício com sub-variants (pasta com `main.tex`)
3. **Teste 3:** Carregamento misto (exercícios normais + com sub-variants)
4. **Teste 4:** Comparação com `generate_sebentas.py` (que lida corretamente com sub-variants)

## Resultados dos Testes

### Teste 1: Exercício Normal ✅
- **Exercício:** `MAT_P4FUNCOE_1GEN_001` (arquivo `.tex` único)
- **Resultado:** ✅ **SUCESSO**
- **Comportamento:** Conteúdo carregado corretamente
- **LaTeX Gerado:** Inclui o conteúdo do exercício

### Teste 2: Exercício com Sub-Variants ❌
- **Exercício:** `MAT_P4FUNCOE_4FIN_ANA_001` (pasta com `main.tex` + 11 sub-variants)
- **Resultado:** ❌ **FALHA**
- **Comportamento:** Sistema não consegue localizar o arquivo
- **LaTeX Gerado:** `\exercicio{[Exercício não encontrado: matematica/P4_funcoes/4-funcao_inversa/determinacao_analitica/MAT_P4FUNCOE_4FIN_ANA_001]}`
- **Causa:** Código assume que `path` no `index.json` é sempre um arquivo `.tex`, não uma pasta

### Teste 3: Carregamento Misto ⚠️
- **Exercícios:** `MAT_P4FUNCOE_1GEN_001` (normal) + `MAT_P4FUNCOE_4FIN_ANA_001` (sub-variants)
- **Resultado:** ⚠️ **PARCIAL**
- **Comportamento:** Carrega o exercício normal, falha no com sub-variants
- **LaTeX Gerado:** 1 exercício válido + 1 erro "não encontrado"

### Teste 4: Comparação com generate_sebentas.py ✅
- **Sistema:** `generate_sebentas.py`
- **Resultado:** ✅ **SUCESSO**
- **Comportamento:** Detecta corretamente pastas com `main.tex` como exercícios com sub-variants
- **Implementação:** Possui lógica específica para `if item.is_dir() and (item / "main.tex").exists():`

## Análise Técnica

### Código Problemático

No `generate_test_template.py`, o método `generate_test_latex()` contém:

```python
# Carregar conteúdo .tex do exercício
source_file = ex.get('source_file') or ex.get('path', '')
tex_path = self.exercise_db / source_file

# Ensure .tex extension
if not str(tex_path).endswith('.tex'):
    tex_path = tex_path.with_suffix('.tex')

if tex_path.exists():
    # Carrega conteúdo
else:
    # Erro: Exercício não encontrado
```

**Problema:** Para exercícios com sub-variants, `path` é uma pasta. O código adiciona `.tex` mas a pasta não se torna um arquivo válido.

### Comparação com generate_sebentas.py

O `generate_sebentas.py` possui lógica adequada:

```python
# Se é uma pasta com main.tex, é um exercício com subvariants
if item.is_dir() and (item / "main.tex").exists():
    main_tex = item / "main.tex"
    # Processa main.tex e resolve \input{} para sub-variants
```

## Impacto

### Exercícios Afetados
- Todos os exercícios criados com `has_subvariants: true` (versão 3.4+)
- Atualmente: `MAT_P4FUNCOE_4FIN_ANA_001` e similares

### Usuários Afetados
- Professores que tentam gerar testes contendo exercícios com múltiplas alíneas
- Sistema falha silenciosamente, gerando PDFs com mensagens de erro

### Gravidade
- **Alta:** Sistema não consegue incluir exercícios importantes
- **Invisível:** Erro só aparece no PDF final, não no console

## Recomendações

### Correção Imediata
Implementar lógica similar ao `generate_sebentas.py` no `generate_test_template.py`:

```python
# No generate_test_latex()
source_file = ex.get('source_file') or ex.get('path', '')
tex_path = self.exercise_db / source_file

if tex_path.is_dir():
    # Nova estrutura: pasta com main.tex
    main_tex = tex_path / 'main.tex'
    if main_tex.exists():
        tex_path = main_tex
    else:
        # Fallback ou erro
else:
    # Estrutura antiga: arquivo .tex
    if not str(tex_path).endswith('.tex'):
        tex_path = tex_path.with_suffix('.tex')

if tex_path.exists():
    # Carregar conteúdo
```

### Testes Adicionais
- Adicionar testes unitários para carregamento de sub-variants
- Incluir exercícios com sub-variants nos testes de integração
- Validar que `\input{}` são resolvidos corretamente

### Documentação
- Atualizar documentação do Test Generator
- Avisar sobre limitação atual
- Incluir exemplos de uso com sub-variants

## Conclusão

O **Test Generator não lida corretamente com exercícios com sub-variants**. Enquanto o sistema de sebentas possui lógica adequada para detectar e processar pastas com `main.tex`, o Test Generator assume que todos os exercícios são arquivos `.tex` únicos, causando falhas silenciosas na geração de testes.

**Status:** ❌ **NECESSITA CORREÇÃO IMEDIATA**

---

**Anexo:** Código de teste usado para validação

```python
# Testes executados
from generate_test_template import TestTemplate

# Teste sub-variants
generator = TestTemplate()
generator.exercises = generator.load_exercises_by_ids(['MAT_P4FUNCOE_4FIN_ANA_001'])
latex = generator.generate_test_latex('matematica', 'MÓDULO P4 - Funções', 'Função Inversa', generator.exercises)
# Resultado: contém "[Exercício não encontrado"
```