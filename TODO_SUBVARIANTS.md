# TODO: Implementação do Suporte a Sub-Variants no Test Generator

## Objetivo
Implementar o suporte para exercícios com sub-variants (alíneas) no `generate_test_template.py`, permitindo que a task "Gerar Teste (Dinâmico)" processe corretamente exercícios organizados em pastas com `main.tex` e `subvariant_*.tex`.

## Problema Identificado
O `generate_test_template.py` não processa corretamente exercícios com sub-variants:
- Assume que todos os paths são ficheiros `.tex`
- Adiciona `.tex` a pastas, resultando em ficheiros inexistentes
- Causa erros silenciosos: "Exercício não encontrado"

## Solução de Referência
O `generate_sebentas.py` já tem lógica adequada (linhas 267-276 e 384-413):
```python
# Se é uma pasta com main.tex, é um exercício com subvariants
if item.is_dir() and (item / "main.tex").exists():
    main_tex = item / "main.tex"
    # Processa main.tex e resolve \input{} para sub-variants
```

## Plano de Implementação

### 1. Criar Testes (Prioridade Alta) ✅
- [x] **Teste 1**: Exercício único com alíneas
  - Mock data: exercício com `main.tex` + 3 `subvariant_*.tex`
  - Validar: LaTeX gerado contém conteúdo das alíneas
  
- [x] **Teste 2**: Múltiplos exercícios com alíneas
  - Mock data: 3 exercícios, cada um com sub-variants
  - Validar: Todos os exercícios são carregados corretamente
  
- [x] **Teste 3**: Exercícios mistos
  - Mock data: 2 exercícios normais + 2 com sub-variants
  - Validar: Ambos os tipos funcionam no mesmo teste

### 2. Modificar `generate_test_template.py` ✅
- [x] Adicionar função `_process_subvariant_inputs()` (baseada em `generate_sebentas.py`)
- [x] Modificar método `generate_test_latex()`:
  - Verificar se `tex_path` é diretório
  - Se for, procurar por `main.tex` dentro
  - Processar `\input{}` para resolver sub-variants

### 3. Validação ✅
- [x] Executar testes unitários
- [x] Testar com exercício real: `MAT_P4FUNCOE_4FIN_ANA_001`
- [x] Verificar que testes existentes não tiveram regressão

## Ficheiros Modificados
1. `SebentasDatabase/_tools/generate_test_template.py` - Implementação principal
2. `tests/test_generate_test_subvariants.py` - Novo ficheiro de testes (criado)

## Critérios de Sucesso ✅
1. ✅ Testes passam para todos os cenários (único, múltiplos, mistos)
2. ✅ Exercício `MAT_P4FUNCOE_4FIN_ANA_001` é carregado corretamente
3. ✅ Sem regressões em exercícios normais (ficheiro `.tex` único)
