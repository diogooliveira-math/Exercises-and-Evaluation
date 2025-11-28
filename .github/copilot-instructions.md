# copilot-instructions.md
# Exercises and Evaluation - AI Coding Assistant Guidelines

## Project Overview
Educational content management system for LaTeX exercises and automated PDF generation. Dual-database architecture: `ExerciseDatabase/` (source exercises) and `SebentasDatabase/` (compiled PDFs). Hierarchical organization by discipline/module/concept/type.

## Architecture Fundamentals
- **ExerciseDatabase/**: Source LaTeX exercises with JSON metadata
  - Structure: `disciplina/módulo/conceito/tipo/exercício.tex`
  - Example: `matematica/A12_otimizacao/estudo_monotonia/monotonia_pura/`
- **SebentasDatabase/**: Generated PDFs from exercises
  - Never create exercises here; only compiled outputs
- **Preview System**: Mandatory approval workflow before saving content
- **Configuration**: `modules_config.yaml` drives module/concept definitions

## Critical Workflows
### Exercise Creation
```bash
# Use this script (not legacy versions)
python ExerciseDatabase/_tools/add_exercise_with_types.py
```
- Always goes through preview system
- Generates ID: `MAT_[MODULE]_[CONCEPT]_[TYPE]_[NUMBER]`
- Creates both `.tex` and `.json` files

### Sebenta Generation
```bash
python SebentasDatabase/_tools/generate_sebentas.py --module P4_funcoes
```
- Compiles exercises into PDFs
- Auto-cleans LaTeX temp files
- Filters by discipline/module/concept/type

### Validation & Testing
```bash
python tests/quick_validation.py  # Database integrity
python tests/show_stats.py        # Statistics overview
```

## Code Patterns & Conventions
### Naming
- **Classes**: PascalCase (`ExerciseGenerator`, `PreviewManager`)
- **Functions**: camelCase (`generateExam`, `validateDatabase`)
- **Files**: snake_case (`add_exercise_with_types.py`)
- **Constants**: ALL_CAPS (`DEFAULT_TEMPLATE`)

### Language Standards
- **Content**: Portuguese (pt-PT)
- **Technical terms**: English (`LaTeX`, `API`, `JSON`, `Python`)
- **Comments**: English for code, Portuguese for educational content

### LaTeX Patterns
```latex
\exercicio{Enunciado principal}
\subexercicio{Primeira alínea}
\exercicioEscolha{Pergunta?}
\opcao{Opção A}
```

### Python Patterns
- Type hints mandatory
- Docstrings required
- Pure functions for data processing
- CLI with argparse/click
- Preview system integration for all generators

## VS Code Integration
### Essential Tasks (Ctrl+Shift+P → "Tasks: Run Task")
- `⚡ Novo Exercício (Mínimo)` - Quick exercise creation
- `📚 Gerar Sebenta (Direto)` - PDF generation with filters
- `🔍 Pesquisar Exercícios` - Search database
- `🛠️ Validar Base de Dados` - Integrity checks

### File Organization Rules
- **ExerciseDatabase/**: Source `.tex` + `.json` files only
- **SebentasDatabase/**: Generated PDFs + temp LaTeX files (auto-cleaned)
- **Never mix**: Exercises belong in ExerciseDatabase, PDFs in SebentasDatabase

## Preview & Quality Control
### Mandatory for All Generation
```python
from preview_system import PreviewManager

preview = PreviewManager(auto_open=True)
if not preview.show_and_confirm(content_dict, "Title"):
    return  # User cancelled
# Proceed with saving
```

### Behavior Expectations
- Opens files in VS Code automatically
- Shows terminal preview (first 20 lines)
- Requires explicit user confirmation `[S]im / [N]ão / [R]ever`
- Tracks cancelled operations

## Common Pitfalls
- ❌ Creating exercises directly in SebentasDatabase
- ❌ Bypassing preview system
- ❌ Manual LaTeX compilation (use scripts)
- ❌ Not updating metadata when adding exercises
- ❌ Mixing Portuguese/English inconsistently

## Key Files for Reference
- `modules_config.yaml` - Module/concept definitions
- `ExerciseDatabase/index.json` - Global exercise index
- `preview_system.py` - Quality control system
- `add_exercise_with_types.py` - Primary exercise creation
- `generate_sebentas.py` - PDF compilation

## Development Commands
```bash
# Create exercise with full workflow
python ExerciseDatabase/_tools/add_exercise_with_types.py

# Generate PDFs for specific module
python SebentasDatabase/_tools/generate_sebentas.py --module A12_otimizacao

# Search exercises
python ExerciseDatabase/_tools/search_exercises.py

# Validate everything
python tests/quick_validation.py
```

## Integration Points
- **VS Code Tasks**: 12+ automated workflows
- **Preview System**: Centralized approval for all content
- **Configuration**: YAML-driven structure
- **LaTeX**: Automated compilation with cleanup
- **Git**: Feature branches with conventional commits

## OpenCode / opencode Integration

- **Purpose**: This repository includes lightweight "opencode" utilities and test scripts to exercise the agent's ability to run commands, parse terminal output, and validate generated content. These are intended for safe, reproducible interactions with the project — not for exposing secrets or making unilateral persistent changes to the databases.
- **Important scripts**: `opencode_terminal_test.py` (root), `scripts/send_prompt_opencode.py`, and `scripts/run_generate_sebenta_task.py` (helpers used by tasks).
- **Agent behaviour rules when using opencode**:
  - Always ask for explicit user permission before running scripts that modify the repository or databases (any script under `ExerciseDatabase/` or `SebentasDatabase/` that writes files).  
  - Do not include secrets, credentials, or private tokens in prompts or logs. If a secret is required, prompt the user to provide it interactively and avoid persisting it in files.
  - Capture and store opencode outputs in `temp/opencode_logs/` (or similar) and present a concise summary to the user; do not auto-commit logs to the repo.
  - Use PowerShell semantics on Windows: when chaining commands in a single line use `;` (e.g. `python script.py --flag ; python other.py`).
  - When a script produces long output, show a short preview (first ~40 lines) and offer to open the full log file in VS Code.
  - When executing tests or validation scripts (`tests/quick_validation.py`, `tests/test_subvariant_generation.py`, `opencode_terminal_test.py`), prefer local-only execution and never run CI pipelines or remote deployment steps.

- **How to call opencode scripts (examples)**:

  - Run the basic terminal test (local, read-only checks preferred):

    ```powershell
    python opencode_terminal_test.py
    ```

  - Send a crafted prompt to the opencode helper (the helper will run a safe local command and return output):

    ```powershell
    python scripts/send_prompt_opencode.py --prompt "Run quick validation" ;
    ```

  - If chaining tasks in PowerShell, separate with `;` and avoid `&&` (PowerShell v5.1). Example:

    ```powershell
    python scripts/send_prompt_opencode.py --prompt "validate" ; python tests/quick_validation.py
    ```

- **Logging & hygiene**:
  - Write opencode logs to `temp/opencode_logs/{timestamp}_opencode.log` and do not commit these files.  
  - If the agent needs to propose changes based on opencode output, present a patch and request user approval before applying (use `git` only after user confirmation).

- **When allowed to make changes**:
  - The agent may create or modify documentation files (`*.md`) with user consent. For edits that affect `ExerciseDatabase/` structure or `index.json` the agent must either: (a) ask the user to run the change locally, or (b) create a PR with the changes (do not push directly to `main`).


---
**Version**: 4.0 (Architecture-focused update)
**Last updated**: 2025-11-26
**Purpose**: Enable AI agents to be immediately productive in this educational content management system

# Idioma principal
- Português (pt-PT).
- Para snippets de código e comentários técnicos use inglês em termos técnicos (`LaTeX`, `TikZ`, `API`, `CLI`, `JSON`, `Python`).

# Escopo do Assistente
- Gerar e corrigir:
  - Scripts Python de automação (3.8+)
  - Scripts de build (PowerShell, Batch)
  - Templates LaTeX e macros
  - Schemas JSON para indexação/metadados
  - Exemplos de conteúdo pedagógico em LaTeX
  - Tasks e configurações para VS Code
- Evitar gerar:
  - Conteúdo irrelevante ao domínio pedagógico/LaTeX
  - Texto de licença sem confirmação do mantenedor

# Convenções de Nomeação
- Componentes, classes e tipos: PascalCase (ex.: ExerciseGenerator, DatabaseIndex)
- Funções, variáveis e métodos: camelCase (ex.: generateExam, validateDatabase)
- Módulos e ficheiros Python: snake_case (ex.: generate_exam.py, validate_database.py)
- Constantes: ALL_CAPS (ex.: DEFAULT_TEMPLATE)
- Ficheiros LaTeX: kebab-case ou snake_case preferível (ex.: exam_full.tex, title_page.tex)
- Branches git: feature/descricao-curta, fix/descricao-curta, chore/docs

# Formato de Metadados (index.json)
- Sempre validar contra este esquema mínimo ao criar/expor entradas.
{
  "id": "string (UUID)",
  "title": "string",
  "subject": "string",
  "topic": "string",
  "subtopic": "string",
  "difficulty": "enum('easy','medium','hard')",
  "type": "enum('exercise','theory','example')",
  "tags": ["string"],
  "author": "string",
  "created_at": "ISO8601",
  "updated_at": "ISO8601",
  "version": "int",
  "source_file": "relative/path/to/file.tex"
}

# Boas práticas para LaTeX (project-specific)
- Usar macros definidas em config/style.tex para consistência:
  - \exercicio{}, \subexercicio{}, \exercicioDesenvolvimento{}, \exercicioEscolha{}, \opcao{}
- Separar conteúdo (content/*.tex) da configuração (config/*.tex).
- Evitar redefinições de macros no conteúdo. Alterações de estilo no config/style.tex.
- Para figuras e TikZ: colocar ficheiros em Teste_modelo/Base/graphics/ e usar \input{...} ou \includegraphics.
- Documentar opções de template (ex.: exam_short, exam_full) no cabeçalho do .tex.

# Padrões para scripts Python
- Usar tipagem (type hints) e docstrings.
- Expor CLI com argparse or click.
- Funções puras retornam dados; efeitos colaterais (I/O) em funções separadas.
- Testes unitários mínimos para:
  - parsing/validating index.json
  - geração de ficheiros tex básicos
- Exemplo de layout de função:
def generate_exam(index: dict, criteria: dict) -> str:
    """Gera conteúdo LaTeX do exame e devolve o caminho para o ficheiro .tex."""
    ...

# Sugestões de commits e PRs
- Commit message: <tipo>(escopo): descrição curta
  - tipos: feat, fix, chore, docs, refactor, test
  - exemplo: feat(generator): add random-order option for exam versions
- PR description: objetivo, mudanças principais, como testar, checklist (lint, build, testes)

# Testes e CI
- Validar:
  - index.json com JSON Schema
  - build.tex via pdflatex (no CI, apenas passagem básica)
  - scripts Python com pytest
- CI mínimo: checkout, setup Python, instalar TeX (ou usar imagem com TeX), executar build simples de Teste_modelo/exame.tex

# Formato de exemplos pedagógicos gerados
- Preferir enunciados claros e curtos.
- Incluir metadados mínimos no topo do ficheiro .tex quando gerado automaticamente:
% meta:
% id: UUID
% title: "..."
% difficulty: "medium"
% tags: "funcoes, derivadas"

# Segurança e permissões
- Não incluir credenciais em ficheiros (API keys, tokens).
- Para operações que alteram Base/ ou ExerciseDatabase/ pedir confirmação.

# ⚠️ ESTRUTURA DE DIRETÓRIOS CRÍTICA
## ExerciseDatabase vs SebentasDatabase

**NUNCA misturar as duas estruturas!**

### ExerciseDatabase/
- **Propósito**: Armazenamento de exercícios fonte (.tex e .json)
- **Estrutura**: `disciplina/módulo/conceito/tipo/exercicio.tex`
- **Conteúdo**: Exercícios individuais, metadados, configurações
- **NÃO CRIAR**: Sebentas, PDFs compilados, ficheiros temporários LaTeX

### SebentasDatabase/
- **Propósito**: Geração e armazenamento de sebentas compiladas (PDFs)
- **Estrutura**: `disciplina/módulo/conceito/pdfs/sebenta_X.pdf`
- **Conteúdo**: Templates, PDFs finais organizados
- **Geração**: Usar `SebentasDatabase/_tools/generate_sebentas.py`

### Regras de Ouro:
1. ✅ Exercícios fonte → **ExerciseDatabase/**
2. ✅ Sebentas compiladas → **SebentasDatabase/**
3. ❌ NUNCA criar `sebenta_*.tex` ou `sebenta_*.pdf` em ExerciseDatabase
4. ❌ NUNCA criar exercícios individuais em SebentasDatabase
5. ✅ Para gerar sebentas: `python SebentasDatabase/_tools/generate_sebentas.py`
6. ✅ Ficheiros temporários LaTeX (.aux, .log) devem ser limpos automaticamente

# Estilo de respostas do Copilot
- Preferência por snippets minimalistas e comentados.
- Quando gerar LaTeX: incluir bloco completo pronto a compilar (preamble mínimo se necessário).
- Quando gerar JSON/CLI: validar e mostrar comando de teste.
- Fornecer alternativa curta e uma explicação de 1–2 linhas quando necessário.

# Exemplos rápidos (uso interno)
- JSON entry:
{
  "id": "c9b1e5a8-1234-4f12-9b8a-0d3e2f1a2b3c",
  "title": "Raízes de um polinómio quadrático",
  "subject": "Matemática",
  "topic": "Funções",
  "subtopic": "Polinómios",
  "difficulty": "medium",
  "type": "exercise",
  "tags": ["quadrática","raízes"],
  "author": "Nome",
  "created_at": "2025-11-01T12:00:00Z",
  "updated_at": "2025-11-01T12:00:00Z",
  "version": 1,
  "source_file": "ExerciseDatabase/matematica/funcoes/ex1.tex"
}

# Alterações e manutenção deste ficheiro
- Atualizar quando forem adicionados novos tipos de macros ou mudanças na estrutura do repositório.
- Mantê-lo conciso e orientado a ação.

# Versão do copilot_instructions
- v1.0 — adaptado ao repositório "Exercises and Evaluation"
- v3.1 — adicionado sistema de preview e curadoria
- v3.2 — adicionado sistema de tasks VS Code e template system

# 🆕 Sistema de Preview e Curadoria (v3.1)

**CRÍTICO**: TODOS os scripts de geração DEVEM usar o sistema de preview antes de adicionar conteúdo à base de dados.

## Filosofia
> "Gere rápido, reveja sempre, confirme conscientemente"

Agentes iniciam o ciclo de geração, mas o utilizador SEMPRE confirma após revisão visual.

## Implementação Obrigatória

### 1. Importar Preview System
```python
from preview_system import PreviewManager, create_exercise_preview
```

### 2. Gerar Conteúdo (como antes)
```python
latex_content = generate_exercise()
metadata = build_metadata()
```

### 3. **PREVIEW E CONFIRMAÇÃO** (NOVO)
```python
preview_content = create_exercise_preview(
    exercise_id,
    latex_content,
    metadata
)

preview = PreviewManager(auto_open=True)
if not preview.show_and_confirm(preview_content, "Novo Exercício"):
    # Utilizador cancelou - NÃO adicionar
    return

# Só adicionar se confirmado
save_to_database(...)
```

### 4. Comportamento Esperado
- ✅ Mostrar preview no terminal (primeiras 20 linhas)
- ✅ Abrir ficheiros em VS Code automaticamente
- ✅ Aguardar confirmação explícita `[S]im / [N]ão / [R]ever`
- ✅ Só salvar após confirmação
- ✅ Limpar temporários após uso

## Scripts Atualizados (v3.1)

### ExerciseDatabase/_tools/
- ✅ `add_exercise_with_types.py` - COM preview
- ✅ `preview_system.py` - Sistema central

### SebentasDatabase/_tools/
- ✅ `generate_sebentas.py` - COM preview
  - Flags: `--no-preview`, `--auto-approve`
- ✅ `generate_tests.py` - COM preview
  - Flags: `--no-preview`, `--auto-approve`

## Flags para Automação

Para CI/CD ou scripts não-interactivos:
```bash
# Desabilitar preview
python script.py --no-preview

# Auto-aprovar sem confirmação
python script.py --auto-approve

# Combinar (totalmente não-interactivo)
python script.py --no-preview --auto-approve
```

## Criar Novo Script de Geração

**Template obrigatório:**
```python
from preview_system import PreviewManager

def my_generator():
    # 1. Gerar conteúdo
    content = generate_something()
    
    # 2. Preparar preview
    preview_content = {
        "output.tex": content,
        "metadata.json": json.dumps(metadata, indent=2)
    }
    
    # 3. PREVIEW E CONFIRMAÇÃO
    preview = PreviewManager(auto_open=True)
    if not preview.show_and_confirm(preview_content, "Título do Preview"):
        print("❌ Cancelado pelo utilizador")
        return None
    
    # 4. Salvar (só após confirmação)
    save_file(content)
    return True
```

## Documentação

- 📚 `PREVIEW_SYSTEM.md` - Documentação completa
- 🚀 `PREVIEW_QUICKSTART.md` - Quick start 5 minutos
- 📖 `readme.md` - Atualizado com v3.1

## Estatísticas

Scripts devem rastrear:
```python
stats = {
    'generated': 0,    # Conteúdo gerado
    'compiled': 0,     # PDFs compilados
    'cancelled': 0,    # 🆕 Cancelados pelo utilizador
    'errors': 0        # Erros
}
```

## Comportamento do Agente (NOVO)

Quando utilizador pede para:

### "Cria um exercício sobre X"
```
Agente:
1. ✅ Gerar conteúdo LaTeX
2. ✅ Gerar metadados
3. ✅ Mostrar PREVIEW automático
4. ✅ Abrir em VS Code
5. ⏸️ AGUARDAR confirmação do utilizador
6. ✅ Só adicionar se confirmado
```

### "Gera uma sebenta de Y"
```
Agente:
1. ✅ Compilar exercícios do módulo
2. ✅ Gerar LaTeX da sebenta
3. ✅ Mostrar PREVIEW
4. ⏸️ AGUARDAR confirmação
5. ✅ Compilar PDF se confirmado
```

### "Cria um teste com Z"
```
Agente:
1. ✅ Selecionar exercícios
2. ✅ Gerar LaTeX do teste
3. ✅ Mostrar lista de exercícios selecionados
4. ✅ PREVIEW do teste completo
5. ⏸️ AGUARDAR confirmação
6. ✅ Compilar se confirmado
```

## NUNCA Fazer

❌ Adicionar conteúdo sem preview  
❌ Salvar antes de confirmação  
❌ Ignorar cancelamento do utilizador  
❌ Omitir flags `--no-preview` em scripts automatizados  
❌ Criar scripts novos sem integrar preview  

## Use case — adicionar exercícios via VS Code (workflow suave)
Objetivo: permitir que um colaborador crie um novo exercício de forma rápida a partir do VS Code, com template LaTeX, metadados válidos e validação mínima local.

Passos resumidos:
1. Criar novo ficheiro .tex em content/ ou ExerciseDatabase/ usando o snippet "new-exercise".
2. Gerar/editar index.json entry correspondente (incluir UUID, source_file relativo).
3. Executar task VS Code "Validate exercise" para validar index.json e compilar um build.tex mínimo (opcional).
4. Fazer commit e abrir PR com mensagem seguindo convenções.

Sugestões de implementação rápida (adicionar ao .vscode no repositório):

- snippets para criar um exercício (.vscode/snippets/exercise.code-snippets)
Um snippet mínimo (exemplo):
{
  "New Exercise (LaTeX)": {
    "prefix": "new-exercise",
    "body": [
      "% meta:",
      "% id: ${1:$(uuidgen)}",
      "% title: \"${2:Title}\"",
      "% difficulty: \"${3:medium}\"",
      "% tags: \"${4:tag1,tag2}\"",
      "% author: \"${5:Author}\"",
      "\\section{${2:Title}}",
      "",
      "\\exercicio{",
      "  ${6:Enunciado aqui}",
      "}",
      ""
    ],
    "description": "Create new exercise template with meta header"
  }
}

- task para validar e compilar (.vscode/tasks.json)
Exemplo de task que executa validação Python e pdflatex (opcional):
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Validate exercise",
      "type": "shell",
      "command": "python scripts/validate_index.py ${file}",
      "problemMatcher": []
    },
    {
      "label": "Quick build pdf",
      "type": "shell",
      "command": "pdflatex -interaction=nonstopmode -halt-on-error ${file}",
      "problemMatcher": []
    }
  ]
}

- script mínimo de validação sugerido (scripts/validate_index.py)
Esboço: validar presença de meta no .tex e checar index.json schema — ver Padrões para scripts Python.

- Boas práticas no fluxo VS Code:
  - Use o snippet "new-exercise" para criar ficheiro e preencher meta.
  - Atualize index.json com a mesma id e source_file.
  - Execute "Validate exercise" antes de commitar.
  - Incluir preview do PDF com a extensão LaTeX Workshop, se instalada.
  - Se o repositório tiver um gerador CLI, adicionar task para executar: python -m generator create --source path/to/file.tex

Notas:
- O snippet usa $(uuidgen) como placeholder; no Windows sem uuidgen ajustar para geração manual ou script.
- Não incluir credenciais nem caminhos absolutos no snippet/task.
- Manter tasks/snippets opcionais; documentar no README CONTRIBUTING.md.

# 🆕 VERSÃO 3.4 - SUB-VARIANTS COM ESTRUTURA DE PASTAS

## Nova Estrutura para Exercícios com Sub-Variants

A partir da **versão 3.4**, exercícios com `has_subvariants: true` agora usam uma estrutura de pastas organizada:

```
MAT_P4FUNCOE_4FIN_ANA_001/
├── main.tex              # Arquivo principal que inclui sub-variants
├── subvariant_1.tex      # Primeira função: f(x) = x + 4
├── subvariant_2.tex      # Segunda função: f(x) = 2x - 1
└── subvariant_3.tex      # Terceira função: f(x) = \frac{1}{x-1}
```

### Vantagens da Nova Estrutura

- **Modularidade**: Cada sub-variant é um arquivo separado, facilitando edição individual
- **Reutilização**: Sub-variants podem ser facilmente movidos ou combinados
- **Manutenção**: Mudanças em uma função não afetam outras
- **Versionamento**: Melhor controle de versão por componente
- **Escalabilidade**: Suporte infinito para número de sub-variants

### Como Funciona

1. **main.tex**: Contém o enunciado principal e inclui cada sub-variant via `\input{}`
2. **subvariant_N.tex**: Cada arquivo contém apenas uma função específica
3. **Preview System**: Mostra todos os arquivos da pasta antes da confirmação
4. **Index Global**: Registra o caminho para `main.tex`

### Scripts Atualizados

- `generate_subvariant_exercise.py`: Agora cria estrutura de pastas
- `add_exercise_with_types.py`: Detecta `has_subvariants` e usa nova estrutura
- `test_subvariant_generation.py`: Testa validação de pastas

### Exemplo de main.tex Gerado

```latex
% meta:
% id: MAT_P4FUNCOE_4FIN_ANA_001
% title: "Determinação Analítica da Função Inversa"
% difficulty: 2
% tags: funcao_inversa, determinacao_analitica
% author: Professor
% has_subvariants: true
% subvariant_count: 3

\section{Determinação Analítica da Função Inversa}

\exercicio{
Determina analiticamente a função inversa das seguintes expressões:
}

\begin{enumerate}[label=\alph*)]
\item \input{subvariant_1}
\item \input{subvariant_2}
\item \input{subvariant_3}
\end{enumerate}
```

### Exemplo de subvariant_1.tex

```latex
% Sub-variant 1 for MAT_P4FUNCOE_4FIN_ANA_001
% Function: f(x) = x + 4

$f(x) = x + 4$
```

### Comportamento do Agente (v3.4)

Quando criar exercício com sub-variants:

```
Utilizador: "Cria um exercício sobre determinar f^(-1)(x) para várias funções"

Agente:
1. ✅ Detecta tipo com has_subvariants: true
2. ✅ Solicita lista de funções ou usa padrões
3. ✅ Gera estrutura de pastas com main.tex + subvariant_*.tex
4. ✅ Preview mostra todos os arquivos
5. ✅ Só salva após confirmação do usuário
6. ✅ Atualiza index.json com caminho para main.tex
```

### Regras para Sub-Variants

1. **Pasta por Exercício**: Cada exercício com sub-variants tem sua própria pasta
2. **Nomenclatura**: `subvariant_N.tex` onde N é sequencial (1, 2, 3...)
3. **Conteúdo Simples**: Cada sub-variant contém apenas a expressão da função
4. **Include no Main**: main.tex usa `\input{subvariant_N}` para incluir cada um
5. **Preview Completo**: Sistema de preview mostra todos os arquivos da pasta

### Compatibilidade

- Exercícios sem `has_subvariants` continuam usando arquivos únicos
- Estrutura antiga permanece válida
- Migração gradual: novos exercícios podem usar nova estrutura

## Melhorias na Geração de Sebentas

A partir da **versão 3.3**, o sistema de geração de sebentas suporta **seleção múltipla** de disciplinas, módulos, conceitos e tipos de exercício.

### Novos Recursos

#### ✅ Seleção Múltipla
- **Disciplinas**: `--discipline matematica,test`
- **Módulos**: `--module P4_funcoes,P1_modelos`  
- **Conceitos**: `--concept 4-funcao_inversa,2-funcoes_polinomiais`
- **Tipos**: `--tipo determinacao_analitica,grafica`

#### ✅ Interface Interativa Aprimorada
O script `generate_sebenta_interactive.py` agora permite:
- Selecionar múltiplas opções separadas por vírgula (ex: `1,3,5`)
- Navegação inteligente através de todas as combinações selecionadas
- Resumo claro das seleções múltiplas

#### ✅ Tasks VS Code Atualizadas
As tasks do VS Code agora aceitam múltiplos valores separados por vírgula nos inputs.

### Exemplos de Uso

```bash
# Gerar sebentas para múltiplos módulos
python generate_sebentas.py --module P4_funcoes,P1_modelos

# Múltiplos conceitos específicos
python generate_sebentas.py --concept 4-funcao_inversa,2-funcoes_polinomiais

# Combinação: múltiplos módulos e tipos
python generate_sebentas.py --module P4_funcoes --tipo determinacao_analitica,grafica

# Interface interativa (recomendado para múltiplas seleções)
python scripts/generate_sebenta_interactive.py
```

### Comportamento

- **Filtragem OR**: Se múltiplas opções são selecionadas, o sistema inclui todos os exercícios que correspondem a **qualquer** uma das opções
- **Navegação**: A interface interativa coleta opções de todas as combinações selecionadas
- **Compatibilidade**: Scripts antigos continuam funcionando (seleção única ainda suportada)

### Benefícios

🎯 **Maior Controle**: Crie sebentas personalizadas combinando diferentes módulos/temas/tipos
🔄 **Flexibilidade**: Misture conceitos de diferentes módulos em uma única sebenta
⚡ **Eficiência**: Interface interativa acelera seleção de múltiplas opções
🔧 **Compatibilidade**: Mantém compatibilidade com workflows existentes

# 🔄 WORKFLOW COMPLETO: Do Exercício ao PDF

## 1. Criar Exercício (em ExerciseDatabase)
```bash
# Usar script de adição com tipos
python ExerciseDatabase/_tools/add_exercise_with_types.py
```
- Cria `.tex` e `.json` em `ExerciseDatabase/disciplina/módulo/conceito/tipo/`
- Atualiza `index.json` global
- Atualiza `metadata.json` do tipo

## 2. Diversificar Exercícios (quando necessário)
- Manter exercícios do mesmo tipo com variações significativas
- Diferentes funções, valores, desafios pedagógicos
- Evitar repetições ou cópias com mudanças mínimas

## 3. Gerar Sebenta (em SebentasDatabase)
```bash
# Gerar sebenta de um conceito específico
python SebentasDatabase/_tools/generate_sebentas.py --module P4_funcoes --concept 4-funcao_inversa

# Gerar sebentas de todo o módulo
python SebentasDatabase/_tools/generate_sebentas.py --module P4_funcoes

# Gerar tudo
python SebentasDatabase/_tools/generate_sebentas.py
```
- Cria `.tex` temporário em `SebentasDatabase/disciplina/módulo/conceito/`
- Compila para PDF
- Move PDF para `SebentasDatabase/disciplina/módulo/conceito/pdfs/`
- Limpa ficheiros temporários automaticamente

## 4. Verificar Resultado
- ✅ PDF em: `SebentasDatabase/disciplina/módulo/conceito/pdfs/sebenta_X.pdf`
- ✅ ExerciseDatabase/ limpo (sem PDFs ou sebentas)
- ✅ SebentasDatabase/ organizado (PDFs em pdfs/, sem temporários)

## ⚠️ ERROS COMUNS A EVITAR
1. ❌ Criar sebenta diretamente em ExerciseDatabase
2. ❌ Compilar PDFs manualmente sem usar o script de geração
3. ❌ Deixar ficheiros temporários (.aux, .log) sem limpar
4. ❌ Misturar estruturas ou criar PDFs em locais errados
5. ❌ Exercícios muito semelhantes/repetidos dentro do mesmo tipo

---

# 🆕 VERSÃO 3.0 - ESTRUTURA COM TIPOS DE EXERCÍCIOS

## Nova Hierarquia: `disciplina/tema/conceito/tipo/exercicio`

A partir da **versão 3.0**, o sistema implementa uma camada adicional de organização: **tipos de exercícios**.

### Estrutura Atualizada

```
ExerciseDatabase/
├── modules_config.yaml          # Configuração central
├── index.json                    # Índice global (agora com campo "tipo")
├── matematica/                   # Disciplina
│   ├── P4_funcoes/              # Tema/Módulo
│   │   ├── 4-funcao_inversa/    # Conceito
│   │   │   ├── determinacao_analitica/     # 🆕 TIPO de exercício
│   │   │   │   ├── metadata.json           # Metadados do TIPO (Opção A)
│   │   │   │   ├── MAT_P4_..._ANA_001.json # Metadados exercício
│   │   │   │   └── MAT_P4_..._ANA_001.tex  # Exercício LaTeX
│   │   │   ├── determinacao_grafica/       # 🆕 TIPO de exercício
│   │   │   │   ├── metadata.json
│   │   │   │   └── [exercícios...]
│   │   │   └── teste_reta_horizontal/      # 🆕 TIPO de exercício
│   │   │       ├── metadata.json
│   │   │       └── [exercícios...]
└── _tools/
    ├── add_exercise_with_types.py  # 🆕 SCRIPT PRINCIPAL (USE ESTE!)
    ├── add_exercise.py              # Script antigo (deprecated)
    └── [outros scripts...]
```

### Metadata do Tipo (JSON por Diretório - Opção A)

Cada **tipo** de exercício tem um `metadata.json`:

```json
{
  "tipo": "determinacao_analitica",
  "tipo_nome": "Determinação Analítica da Função Inversa",
  "conceito": "4-funcao_inversa",
  "conceito_nome": "Função Inversa",
  "tema": "P4_funcoes",
  "tema_nome": "MÓDULO P4 - Funções",
  "disciplina": "matematica",
  "descricao": "Exercícios focados no cálculo da expressão analítica da função inversa através de manipulação algébrica.",
  "tags_tipo": [
    "calculo_analitico",
    "expressao_analitica",
    "algebra",
    "resolucao_equacao"
  ],
  "caracteristicas": {
    "requer_calculo": true,
    "requer_grafico": false,
    "complexidade_algebrica": "media"
  },
  "dificuldade_sugerida": {
    "min": 2,
    "max": 4
  },
  "exercicios": [
    "MAT_P4FUNCOE_4FIN_ANA_001",
    "MAT_P4FUNCOE_4FIN_ANA_002"
  ]
}
```

### Formato Atualizado de IDs de Exercícios

Novo formato **com tipo**:

```
MAT_P4FUNCOE_4FIN_ANA_001
│   │        │    │   └── Número sequencial (001-999)
│   │        │    └────── Abreviação do TIPO (3 letras: ANA, GRA, TRH)
│   │        └─────────── Abreviação do conceito (3-4 letras: 4FIN)
│   └──────────────────── Abreviação do módulo (até 8 letras: P4FUNCOE)
└──────────────────────── Disciplina (3 letras: MAT)
```

### Metadados de Exercício Atualizados

Ficheiro `.json` do exercício agora inclui:

```json
{
  "id": "MAT_P4FUNCOE_4FIN_ANA_001",
  "classification": {
    "discipline": "matematica",
    "module": "P4_funcoes",
    "concept": "4-funcao_inversa",
    "tipo": "determinacao_analitica",       // 🆕 Campo TIPO
    "tipo_nome": "Determinação Analítica",  // 🆕 Nome do tipo
    "tags": [...],
    "difficulty": 3
  }
}
```

### Índice Global Atualizado

O `index.json` agora rastreia tipos:

```json
{
  "database_version": "3.0",
  "statistics": {
    "by_type": {                              // 🆕 Estatísticas por tipo
      "Determinação Analítica": 5,
      "Determinação Gráfica": 3,
      "Teste da Reta Horizontal": 2
    }
  },
  "exercises": [
    {
      "id": "MAT_P4FUNCOE_4FIN_ANA_001",
      "tipo": "determinacao_analitica",       // 🆕 Campo tipo
      "tipo_nome": "Determinação Analítica"
    }
  ]
}
```

## 🛠️ Scripts Atualizados

### Script Principal: `add_exercise_with_types.py`

**SEMPRE use este script** para criar novos exercícios na v3.0:

```bash
python ExerciseDatabase/_tools/add_exercise_with_types.py
```

Funcionalidades:
- ✅ Solicita: disciplina → tema → conceito → **tipo**
- ✅ Permite criar novo tipo interativamente
- ✅ Gera ID com componente de tipo
- ✅ Tags automáticas do tipo + conceito
- ✅ Atualiza `metadata.json` do tipo
- ✅ Atualiza `index.json` global

### Criar Novo Tipo de Exercício

Interativamente via `add_exercise_with_types.py` ou manualmente:

1. Criar diretório: `conceito/novo_tipo/`
2. Criar `metadata.json` do tipo com estrutura acima
3. Adicionar exercícios dentro deste diretório

## 🎯 Comportamento do Agente Copilot (v3.0)

### Ao criar exercício:

```
Utilizador: "Cria um exercício sobre determinar f^(-1)(x)"

Agente:
1. Identifico: matematica/P4_funcoes/4-funcao_inversa
2. Tipo apropriado: determinacao_analitica
3. Verifico se tipo existe (metadata.json)
4. Se não existe, pergunto se crio
5. Uso add_exercise_with_types.py
6. Atualizo metadata do tipo
```

### Ao reorganizar:

```
Utilizador: "Organiza os exercícios de função inversa por tipos"

Agente:
1. Leio exercícios em 4-funcao_inversa/
2. Analiso tags para determinar tipo
3. Crio estrutura de tipos
4. Movo ficheiros .tex e .json
5. Crio/atualizo metadata.json de cada tipo
6. Atualizo index.json
```

### Ao pesquisar:

```
Utilizador: "Lista exercícios de determinação gráfica"

Agente:
1. Pesquiso em index.json por "tipo": "determinacao_grafica"
2. OU navego para matematica/.../determinacao_grafica/
3. Leio metadata.json do tipo
4. Listo exercícios
```

## ⚠️ Regras Importantes v3.0

1. **SEMPRE use tipos**: Novos exercícios DEVEM ir em `conceito/tipo/`
2. **Não misture**: Não coloque exercícios diretamente em `conceito/` (usar tipo)
3. **Metadata do tipo**: Sempre atualizar `exercicios[]` no `metadata.json` do tipo
4. **IDs únicos**: Incluir componente de tipo no ID
5. **Tags automáticas**: Combinar tags do conceito + tags do tipo
6. **Script correto**: Use `add_exercise_with_types.py`, NÃO `add_exercise.py`

## 🔄 Migração de Exercícios Antigos

Para migrar exercícios da estrutura antiga (sem tipos):

1. Identificar tipos naturais pelos metadados/tags
2. Criar estrutura de tipos
3. Mover ficheiros para tipos apropriados
4. Renomear IDs (adicionar componente de tipo)
5. Atualizar todos os metadados
6. Regenerar `index.json`

Exemplo:
```
Antes: matematica/P4_funcoes/4-funcao_inversa/MAT_P4_4FIN_001.tex

Depois: matematica/P4_funcoes/4-funcao_inversa/determinacao_analitica/MAT_P4_4FIN_ANA_001.tex
```

## 📊 Estatísticas e Análise

Com tipos, agora é possível:
- Contar exercícios por tipo
- Gerar sebentas por tipo específico
- Criar exames balanceados por tipo
- Analisar cobertura de tipos por conceito

## 🎓 Exemplos de Tipos Comuns

### Função Inversa
- `determinacao_analitica`: Cálculo algébrico de f⁻¹(x)
- `determinacao_grafica`: Obter gráfico por simetria
- `teste_reta_horizontal`: Verificar injetividade

### Derivadas (futuro)
- `aplicacao_regras`: Usar regras de derivação
- `derivada_composta`: Regra da cadeia
- `interpretacao_geometrica`: Reta tangente

### Limites (futuro)
- `calculo_direto`: Substituição direta
- `levantamento_indeterminacao`: Resolver 0/0
- `limites_laterais`: Esquerda e direita

---

# 🎯 TASKS VS CODE - INTERAÇÃO RÁPIDA (v3.2)

> **Sistema completo de tasks para executar scripts essenciais**

## Como Sugerir Tasks ao Utilizador

**✅ SEMPRE recomende tasks quando utilizador pede:**
- "Cria um exercício" → `📝 Novo Exercício (Template)`
- "Gera uma sebenta" → `📚 Gerar Sebenta (Template Editável)`
- "Faz um teste" → `📝 Gerar Teste (Template Editável)`
- "Pesquisa exercícios" → `🔍 Pesquisar Exercícios`
- "Valida a base" → `🛠️ Validar Base de Dados`

**Exemplo de resposta correta:**
```
Recomendo usar a task:
📝 Novo Exercício (Template)

Para executar:
Ctrl+Shift+P → "Tasks: Run Task" → Escolher task
```

## Tasks Essenciais (8 total - 95% dos casos)

| Emoji | Task | Script |
|-------|------|---------|
| 📝 | Novo Exercício | `add_exercise_template.py` |
| 📚 | Gerar Sebenta | `generate_sebenta_template.py` |
| 📝 | Gerar Teste | `generate_test_template.py` |
| 🔍 | Pesquisar Exercícios | `search_exercises.py` |
| 🛠️ | Validar Base de Dados | `quick_validation.py` |
| 📊 | Ver Estatísticas | (inline Python) |
| 🛠️ | Gerir Módulos | `manage_modules.py` |
| 🛠️ | Consolidar Metadados | `consolidate_type_metadata.py` |

**Documentação completa:** `VSCODE_TASKS_GUIDE.md`

## Quando NÃO sugerir tasks

❌ Durante automação/scripts (usar CLI)  
❌ Quando precisa parsing de output  
❌ CI/CD pipelines (usar flags `--no-preview --auto-approve`)

---

**Versão**: 3.3 (seleção múltipla + tasks VS Code + template system)  
**Data**: 2025-11-24  
**Filosofia**: Organização hierárquica, metadados ricos, automação inteligente, interação visual, seleção múltipla flexível