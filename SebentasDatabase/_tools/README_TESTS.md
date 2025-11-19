# Gerador de Testes - SebentasDatabase

## Visão Geral

O `generate_tests.py` permite gerar testes personalizados a partir de exercícios da `ExerciseDatabase`, com controlo fino sobre:
- **Tipos de exercícios** e quantidades por tipo
- **Módulos, conceitos e disciplinas** específicos
- **Embaralhamento** para criar versões diferentes
- **Compilação automática** para PDF
- **Limpeza automática** de ficheiros temporários

## Estrutura de Saída

```
SebentasDatabase/
└── <disciplina>/
    └── <módulo>/
        └── <conceito>/
            └── tests/                    # Testes gerados
                ├── test_config.json      # ⭐ Config LOCAL (opcional)
                ├── pdfs/                 # PDFs compilados
                │   └── test_YYYYMMDD_HHMMSS.pdf
                └── logs/                 # Logs de erro (apenas quando falha)
```

**Nota:** 
- Todos os ficheiros temporários (`.tex`, `.aux`, `.log`, `.synctex.gz`, etc.) são **automaticamente removidos** após compilação bem-sucedida
- `test_config.json` local é **preservado** e tem prioridade sobre configs globais
- Mantém apenas os PDFs em `pdfs/` e a config em `tests/`

## Uso Básico

### 1. Geração Simples (Config Padrão ou Local)

```powershell
# Gerar teste - procura test_config.json local primeiro
python SebentasDatabase\_tools\generate_tests.py --module P4_funcoes --concept 4-funcao_inversa

# Gerar apenas .tex (sem compilar)
python SebentasDatabase\_tools\generate_tests.py --module P4_funcoes --concept 4-funcao_inversa --no-compile
```

### 2. Criar Config Local (⭐ RECOMENDADO)

```powershell
# Criar test_config.json dentro de tests/ e gerar teste
python SebentasDatabase\_tools\generate_tests.py \
    --module P4_funcoes \
    --concept 4-funcao_inversa \
    --create-config

# Depois editar tests/test_config.json e regenerar
python SebentasDatabase\_tools\generate_tests.py --module P4_funcoes --concept 4-funcao_inversa
```

**Prioridade de Configuração:**
1. `--config <path>` (se especificado via CLI)
2. `tests/test_config.json` (config local ao conceito) ⭐
3. `_tests_config/default_test_config.json` (config global)

### 3. Geração com Config Global Específica

```powershell
# Usar ficheiro de config customizado (ignora local)
python SebentasDatabase\_tools\generate_tests.py \
    --module P4_funcoes \
    --concept 4-funcao_inversa \
    --config SebentasDatabase\_tests_config\teste_balanceado.json
```

## Ficheiros de Configuração JSON

### Estrutura do JSON

```json
{
  "name": "nome_do_teste",
  "title_template": "Teste - {concept_name}",
  "per_tipo": {
    "tipo1": 2,
    "tipo2": 1
  },
  "count": null,
  "shuffle": true,
  "include_answers": false,
  "output_subdir": "tests",
  "pdfs_subdir": "pdfs",
  "notes": "Descrição opcional"
}
```

### Campos Disponíveis

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `name` | string | Nome identificador do teste |
| `title_template` | string | Template do título (variáveis: `{module}`, `{concept}`, `{module_name}`, `{concept_name}`) |
| `per_tipo` | object | Número de exercícios por tipo (ex: `{"determinacao_analitica": 2}`) |
| `count` | int/null | Total de exercícios (se `null`, usa `per_tipo`) |
| `shuffle` | boolean | Embaralhar exercícios antes de selecionar |
| `output_subdir` | string | Subdiretório de saída (padrão: `"tests"`) |
| `pdfs_subdir` | string | Subdiretório para PDFs (padrão: `"pdfs"`) |
| `header_left` | string | Cabeçalho esquerdo (opcional) |
| `header_right` | string | Cabeçalho direito (opcional) |

### Exemplos de Configuração

#### Config Padrão (`default_test_config.json`)
```json
{
  "name": "teste_rapido",
  "title_template": "Teste - {module} - {concept}",
  "per_tipo": {
    "determinacao_grafica": 2,
    "determinacao_analitica": 1
  },
  "shuffle": true
}
```

#### Config Balanceado (`teste_balanceado.json`)
```json
{
  "name": "teste_balanceado",
  "title_template": "Teste de Avaliação - {concept_name}",
  "per_tipo": {
    "determinacao_analitica": 2,
    "determinacao_grafica": 2,
    "teste_reta_horizontal": 1
  },
  "shuffle": true
}
```

#### Config Simples (Total Count)
```json
{
  "name": "teste_curto",
  "title_template": "Teste Rápido",
  "count": 5,
  "shuffle": true
}
```

## Filtros CLI

Além da configuração JSON, pode filtrar exercícios via linha de comandos:

```powershell
# Filtrar por disciplina
--discipline matematica

# Filtrar por módulo
--module P4_funcoes

# Filtrar por conceito
--concept 4-funcao_inversa

# Filtrar por tipo
--tipo determinacao_grafica
```

## Debugging e Logs

### Logs de Erro

Quando a compilação **falha**, o script:
1. Guarda stdout/stderr em `tests/logs/<test_name>_error.log`
2. Preserva o ficheiro `.tex` para inspeção
3. Imprime o caminho do log na consola

Exemplo de log salvo:
```
tests/logs/test_20251119_212227_error.log
```

### Limpeza Automática

Quando a compilação **tem sucesso**, o script:
1. Move o PDF para `tests/pdfs/`
2. Remove **todos** os ficheiros temporários:
   - `.tex` (o fonte gerado)
   - `.aux`, `.log`, `.out`, `.toc`
   - `.fls`, `.fdb_latexmk`
   - `.synctex.gz`, `.synctex(busy)`
   - E todos os outros em `TEMP_EXTENSIONS`

### Verificar Estado do Diretório

```powershell
# Listar conteúdo de tests/
Get-ChildItem -Path "SebentasDatabase\matematica\P4_funcoes\4-funcao_inversa\tests" -Recurse
```

Estrutura esperada após geração bem-sucedida:
```
tests/
└── pdfs/
    └── test_20251119_212227.pdf
```

## Comparação com Sebentas

| Aspecto | Sebentas | Testes |
|---------|----------|--------|
| **Template LaTeX** | `sebenta_template.tex` | `test_template.tex` (idêntico) |
| **Macros** | `\exercicio`, `\subexercicio`, `\option` | Mesmas macros |
| **Pacotes** | TikZ, pgfplots, amsmath, placeins | Idênticos |
| **Limpeza** | Automática após compilação | Automática após compilação |
| **Logs** | Salvos em caso de erro | Salvos em `tests/logs/` |
| **Estrutura** | `<concept>/pdfs/sebenta_*.pdf` | `<concept>/tests/pdfs/test_*.pdf` |

## Workflow Recomendado

### 1. Criar Config Personalizada
```powershell
# Copiar e editar config
Copy-Item SebentasDatabase\_tests_config\default_test_config.json `
          SebentasDatabase\_tests_config\meu_teste.json
```

### 2. Gerar Teste
```powershell
python SebentasDatabase\_tools\generate_tests.py \
    --module P4_funcoes \
    --concept 4-funcao_inversa \
    --config SebentasDatabase\_tests_config\meu_teste.json
```

### 3. Verificar Resultado
- PDF gerado em: `SebentasDatabase/<disc>/<mod>/<concept>/tests/pdfs/`
- Em caso de erro: verificar logs em `tests/logs/`

### 4. Gerar Múltiplas Versões
```powershell
# Gerar 3 versões diferentes (shuffle=true)
for ($i=1; $i -le 3; $i++) {
    python SebentasDatabase\_tools\generate_tests.py \
        --module P4_funcoes --concept 4-funcao_inversa
}
```

## Troubleshooting

### PDF não gerado
1. Verificar se `pdflatex` está no PATH: `where pdflatex`
2. Consultar logs em `tests/logs/<test_name>_error.log`
3. Executar com `--no-compile` e compilar manualmente para ver erros

### Exercícios não selecionados
```
Nenhum exercício selecionado com os filtros/configuração fornecidos.
```
- Verificar se os valores de `--module`, `--concept`, `--tipo` existem no `index.json`
- Confirmar que `per_tipo` usa nomes corretos de tipos

### Ficheiros temporários não removidos
- Isto indica que a compilação falhou
- Verificar logs em `tests/logs/`
- Os temporários são preservados propositadamente para debugging

## Integração com VS Code

Adicionar task em `.vscode/tasks.json`:

```json
{
  "label": "Gerar Teste",
  "type": "shell",
  "command": "python",
  "args": [
    "SebentasDatabase/_tools/generate_tests.py",
    "--module", "${input:module}",
    "--concept", "${input:concept}"
  ],
  "problemMatcher": []
}
```

## Notas Finais

- **Alinhamento com sebentas:** Template e comportamento idênticos ao `generate_sebentas.py`
- **Limpeza automática:** Zero manutenção de ficheiros temporários
- **Logs úteis:** Debugging facilitado quando há erros
- **Flexibilidade:** Controlo fino via JSON + filtros CLI
- **Reprodutibilidade:** Timestamp único em cada ficheiro gerado
