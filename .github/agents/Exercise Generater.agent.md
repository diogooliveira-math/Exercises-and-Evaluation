---
description: 'Gera novas versões (variantes) de exercícios ou cria exercícios novos alinhados com a filosofia do projeto (pt-PT, LaTeX + JSON metadados, atualização de índice).'
tools: []
---

# Exercise Generator Agent — Guia de Uso

Este agente cria uma nova versão de um exercício a partir de um ficheiro existente (variante) ou ajuda a criar exercícios novos, garantindo consistência com as convenções do repositório.

## ⚠️ REGRA CRÍTICA: Separação de Estruturas

**NUNCA misturar ExerciseDatabase com SebentasDatabase!**

### ExerciseDatabase/
- ✅ Apenas ficheiros `.tex` e `.json` de exercícios individuais
- ✅ Estrutura: `disciplina/módulo/conceito/tipo/exercicio.tex`
- ❌ NUNCA criar `sebenta_*.tex` ou `sebenta_*.pdf` aqui
- ❌ NUNCA compilar PDFs aqui

### SebentasDatabase/
- ✅ Apenas sebentas compiladas (PDFs)
- ✅ Estrutura: `disciplina/módulo/conceito/pdfs/sebenta_X.pdf`
- ✅ Usar `SebentasDatabase/_tools/generate_sebentas.py`
- ❌ NUNCA criar exercícios individuais aqui

## Filosofia e Regras (resumo do projeto)

- Idioma: Português (pt-PT); termos técnicos em inglês quando apropriado (LaTeX, TikZ, API, CLI, JSON, Python).
- LaTeX: usar macros do template em `Teste_modelo/config/style.tex` (ex.: `\exercicio`, `\subexercicio`, `\exercicioDesenvolvimento`). Separar conteúdo (content/*.tex) de configuração.
- Metadados: criar `.json` por exercício seguindo o esquema mínimo do projeto; atualizar `index.json` sempre.
- Nomeação: módulos/ficheiros Python em snake_case; classes PascalCase; funções camelCase; constantes ALL_CAPS; ficheiros LaTeX em kebab-case/snake_case.
- Segurança: nunca incluir credenciais. Pedir confirmação antes de alterações estruturais fora do conceito alvo.

## Quando Usar

- Variar rapidamente um exercício mantendo o mesmo conceito (ex.: mudar ligeiramente números em $f(x)$).
- Criar um novo exercício com o assistente interativo.
- Atualizar PDFs de uma pasta de conceito após mudanças.

## Entradas Ideais

- `source_path` (variante): caminho do `.tex` existente.
- `module_id`/`concept_id`/`tipo_id` (novo): conforme `ExerciseDatabase/modules_config.yaml` e tipos existentes.
- Metadados (novo): `difficulty`, `type`, `tags`, `points`, `time_minutes`, `parts`, `author`.

## Saídas Esperadas

- `.tex` com cabeçalho de meta (ID, dificuldade, tags, data) e LaTeX válido **no diretório do tipo**.
- **Atualização do `metadata.json` do tipo** com novo ID na lista `exercicios[]`.
- `index.json` atualizado e estatísticas recalculadas.
- (Opcional) PDF da sebenta do conceito atualizado (ficheiro `sebenta_*.pdf`).

**IMPORTANTE**: Não cria ficheiro `.json` individual por exercício. Apenas o `metadata.json` do tipo é mantido.

## Fluxos de Trabalho

### A) Gerar Variante (recomendado para pequenos ajustes)

1. Selecionar exercício base (`source_path`).
2. Executar:
```powershell
python ExerciseDatabase/_tools/generate_variant.py --source "<source_path>" --strategy auto
```
3. O agente cria `..._XYZ.tex/.json` com próximo número livre e atualiza `index.json`.
4. (Opcional) Gerar PDF do conceito:
```powershell
python ExerciseDatabase/_tools/generate_sebentas.py
```

### B) Criar Novo Exercício com Tipos (assistido - RECOMENDADO)

1. Correr assistente:
```powershell
python ExerciseDatabase/_tools/add_exercise_with_types.py
```
2. Escolher módulo/conceito/**tipo**, preset e preencher campos.
3. **Permite criar novo tipo** se necessário.
4. Confirmar criação; verificar:
   - Ficheiro `.tex` em `ExerciseDatabase/conceito/tipo/`
   - ID adicionado ao `metadata.json` do tipo
   - `index.json` atualizado
   - ❌ **Nenhum PDF criado em ExerciseDatabase** (correto!)

### C) Gerar Sebenta PDF (depois de criar exercícios)

```powershell
# Para um conceito específico
python SebentasDatabase/_tools/generate_sebentas.py --module P4_funcoes --concept 4-funcao_inversa

# Para todo um módulo
python SebentasDatabase/_tools/generate_sebentas.py --module P4_funcoes

# Para tudo
python SebentasDatabase/_tools/generate_sebentas.py
```

**Resultado**:
- PDF gerado em `SebentasDatabase/disciplina/módulo/conceito/pdfs/sebenta_X.pdf`
- Ficheiros temporários limpos automaticamente
- ExerciseDatabase permanece sem PDFs ✅

### D) Criar Exercício (modo antigo - sem tipos - DEPRECATED)

```powershell
python ExerciseDatabase/_tools/add_exercise.py
```

**NOTA**: Evitar usar este script. Usar `add_exercise_with_types.py` para consistência.

## Restrições e Limites

- Não altera `Teste_modelo/config/style.tex` nem estrutura global sem confirmação.
- Mantém o exercício no mesmo conceito na geração de variantes.
- Evita alterações arriscadas no conteúdo LaTeX (apenas variações numéricas simples dentro de `$...$` no modo `auto`).

## Validação e Erros Comuns

- Compilação LaTeX falha: verificar log em `build/sebenta_<conceito>.build.log` e assegurar que expressões matemáticas estão em `$...$`.
- `style.tex not found`: confirmar caminho relativo correcto no gerador de sebentas.
- `index.json` inconsistente: executar `python ExerciseDatabase/_tools/run_tests.py`.

## Progresso e Pedidos de Ajuda

- O agente reporta: ficheiro origem, novo ID gerado, caminhos criados e atualização do índice.
- Em caso de ambiguidade (módulo/conceito), solicita confirmação antes de escrever ficheiros.

## Exemplos Rápidos

- Variante do exercício atual (v3.0 com tipos):
```powershell
python ExerciseDatabase/_tools/generate_variant.py --source "ExerciseDatabase/matematica/P4_funcoes/4-funcao_inversa/determinacao_analitica/MAT_P4FUNCOE_4FIN_ANA_001.tex" --strategy auto
```

**O que faz**:
- Gera novo ID sequencial no mesmo tipo (ex: `_ANA_002`)
- Atualiza `metadata.json` do tipo automaticamente
- Aplica variações simples ao conteúdo (números, expressões)

- Gerar PDFs de todas as sebentas (em SebentasDatabase):
```powershell
python SebentasDatabase/_tools/generate_sebentas.py
```

**⚠️ LEMBRETE**: Sebentas vão para `SebentasDatabase/`, NUNCA para `ExerciseDatabase/`!
