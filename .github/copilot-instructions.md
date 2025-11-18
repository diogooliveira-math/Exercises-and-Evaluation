# copilot-instructions.md
# Configurações específicas para o repositório "Exercises and Evaluation"
# Objetivo: orientar sugestões automáticas de código e conteúdo gerado por Copilot para este projeto.

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

# Use case — adicionar exercícios via VS Code (workflow suave)
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

# Versão do copilot_instructions
- v1.1 — adicionada secção "Use case" para integração com VS Code