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

**Versão**: 3.0 (com suporte a tipos de exercícios)  
**Data**: 2025-11-19  
**Filosofia**: Organização hierárquica, metadados ricos, automação inteligente