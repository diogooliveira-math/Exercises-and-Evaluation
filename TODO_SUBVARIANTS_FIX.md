# TODO: Correção do Test Generator para Sub-Variants

## Contexto

O `generate_test_template.py` não conseguia processar exercícios com sub-variants (alíneas) que são organizados em pastas com `main.tex` + `subvariant_*.tex`.

### Problema Identificado

No método `generate_test_latex()`, o código assumia que todos os exercícios são ficheiros `.tex` únicos. Para exercícios com sub-variants, o `path` pode apontar para `main.tex` dentro de uma pasta, e o sistema precisava também resolver os `\input{subvariant_N}` contidos no `main.tex`.

## Plano de Implementação

### 1. Criar Testes de Validação ✅

Criados testes para validar o comportamento esperado:

- [x] **Teste 1**: Exercício único com sub-variants (pasta com main.tex + subvariant_*.tex)
- [x] **Teste 2**: Múltiplos exercícios com sub-variants
- [x] **Teste 3**: Exercícios mistos (normal .tex + sub-variants)

Os testes verificam:
- Conteúdo LaTeX é carregado corretamente
- `\input{subvariant_N}` é resolvido e o conteúdo é incluído inline
- Nenhuma mensagem de erro "[Exercício não encontrado]" é gerada

### 2. Implementar Correção no generate_test_template.py ✅

Implementada a correção com:

- [x] Novo método `resolve_inputs()` para resolver comandos `\input{}`
- [x] Atualização do `generate_test_latex()` para detectar pastas com `main.tex`
- [x] Compatibilidade mantida com exercícios normais (ficheiros .tex únicos)

### 3. Validar com Testes Automatizados ✅

- [x] Todos os testes unitários passam
- [x] Testes de validação rápida passam
- [x] Testes de subvariant generation passam

## Exercícios de Teste

### Exercícios com Sub-Variants existentes:
- `MAT_P4FUNCOE_4FIN_ANA_001` - 8 sub-variants
- `MAT_P4FUNCOE_4FIN_ANA_007` - 3 sub-variants

### Exercícios Normais (ficheiros .tex únicos):
- `MAT_P4FUNCOE_1GEN_001`
- `MAT_P4FUNCOE_2FUN_001`
- `MAT_P4FUNCOE_3FUN_001`

## Critérios de Sucesso

1. ✅ Exercícios normais (.tex únicos) continuam a funcionar
2. ✅ Exercícios com sub-variants são carregados corretamente
3. ✅ Conteúdo dos `\input{subvariant_N}` é incluído inline no LaTeX gerado
4. ✅ Nenhuma mensagem de erro para exercícios válidos
5. ✅ Testes unitários passam

## Ficheiros Alterados

- `SebentasDatabase/_tools/generate_test_template.py` - Adicionado `resolve_inputs()` e atualizado `generate_test_latex()`
- `tests/test_generate_test_template_subvariants.py` - Novos testes para sub-variants

## Notas

- O `generate_sebentas.py` já tinha lógica similar implementada
- Manteve-se compatibilidade com ambos os formatos (antigo e novo)
