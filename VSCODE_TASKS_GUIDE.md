# 🎯 GUIA DE TASKS VS CODE - Exercises and Evaluation

> **Versão**: 1.0  
> **Data**: 2025-11-21  
> **Propósito**: Referência completa de tasks do VS Code para interação com a base de dados

---

## 📋 ÍNDICE

1. [Visão Geral](#visão-geral)
2. [Tasks de Exercícios](#tasks-de-exercícios)
3. [Tasks de Sebentas](#tasks-de-sebentas)
4. [Tasks de Testes](#tasks-de-testes)
5. [Tasks de Pesquisa](#tasks-de-pesquisa)
6. [Tasks de Manutenção](#tasks-de-manutenção)
7. [Workflows Compostos](#workflows-compostos)
8. [Para Agentes](#para-agentes)

---

## 🎯 VISÃO GERAL

### Como Executar Tasks

**Interface Visual:**
1. `Ctrl+Shift+P` → "Tasks: Run Task"
2. Escolher task da lista
3. Seguir instruções interativas

**Atalhos Rápidos:**
- `Ctrl+Shift+B` → Tarefa de build padrão
- `Ctrl+Shift+T` → Tarefa de teste padrão

**Linha de Comandos:**
```bash
# Listar tasks disponíveis
code --list-extensions

# Executar task específica
# (não há comando direto, usar interface)
```

### Categorias de Tasks

| Categoria | Emoji | Descrição |
|-----------|-------|-----------|
| **Exercícios** | 📝 | Criar e gerir exercícios |
| **Sebentas** | 📚 | Gerar PDFs de coleções |
| **Testes** | 📝 | Criar avaliações |
| **Pesquisa** | 🔍 | Buscar e filtrar exercícios |
| **Manutenção** | 🛠️ | Gestão da base de dados |
| **Testes Dev** | 🧪 | Desenvolvimento e validação |
| **Estatísticas** | 📊 | Análise de dados |
| **Migração** | 🔄 | Importação e conversão |
| **Workflows** | 🚀 | Sequências automáticas |

---

## 📝 TASKS DE EXERCÍCIOS

### `📝 Novo Exercício (Template)`

**Script:** `ExerciseDatabase/_tools/add_exercise_template.py`

**Descrição:** Sistema de criação baseado em template editável.

**Workflow:**
1. Gera ficheiro `.tex` com template comentado
2. Abre automaticamente no editor
3. Preenche campos e conteúdo
4. Valida ao salvar
5. Incorpora na base de dados

**Vantagens:**
- ✅ Visualização completa das opções inline
- ✅ Edição livre sem wizard sequencial
- ✅ Validação automática pós-edição
- ✅ Controle de criação (tipos vs módulos)

**Campos Obrigatórios:**
```latex
% Disciplina: matematica
% Módulo: A8_modelos_discretos
% Conceito: 1-sistemas_numericos
% Tipo: determinacao_valores
% Formato: desenvolvimento | escolha_multipla | verdadeiro_falso | resposta_curta
% Dificuldade: 1-5
% Tags: tag1, tag2, tag3
```

**Quando Usar:**
- Criação rápida com liberdade total
- Quando já conhece a estrutura
- Para copiar/adaptar exercícios existentes

---

### `📝 Novo Exercício (Wizard Interativo)`

**Script:** `ExerciseDatabase/_tools/add_exercise_with_types.py`

**Descrição:** Wizard passo-a-passo com validação em tempo real.

**Workflow:**
1. Escolher disciplina → módulo → conceito → tipo
2. Selecionar formato e dificuldade
3. Adicionar tags
4. Escrever enunciado (suporta múltiplas alíneas)
5. Opcional: adicionar solução
6. Preview consolidado
7. Confirmar e guardar

**Vantagens:**
- ✅ Guiado para iniciantes
- ✅ Validação a cada passo
- ✅ Preview antes de salvar
- ✅ Criação de novos tipos inline

**Quando Usar:**
- Primeira vez criando exercícios
- Quando não lembra estrutura exata
- Para criar novo tipo de exercício

---

## 📚 TASKS DE SEBENTAS

> **Atenção importante — destino das sebentas geradas**
>
> - As sebentas (ficheiros `.tex` e `.pdf`) geradas por estas tasks **são guardadas em `SebentasDatabase/`** e não em `ExerciseDatabase/`.
> - Não execute o script legacy `ExerciseDatabase/_tools/generate_sebentas.py` para produção: ele gera ficheiros diretamente na árvore `ExerciseDatabase/`. Use sempre `SebentasDatabase/_tools/generate_sebentas.py`.
> - O script legacy foi protegido no repositório: é necessário definir `ALLOW_EXERCISE_DB_SEBENTA=1` ou passar `--allow-exercise-output` para forçar a sua execução.

### `📚 Gerar Sebenta (Template Editável)`

**Script:** `SebentasDatabase/_tools/generate_sebenta_template.py`

**Descrição:** Gera sebenta completa com LaTeX editável antes de compilar.

**Workflow:**
1. Escolhe módulo e conceito interativamente
2. Carrega todos os exercícios do conceito
3. Gera LaTeX completo da sebenta
4. **Abre para "final touches"** (editar, adicionar, remover)
5. Compila para PDF após confirmação
6. Guarda em `SebentasDatabase/.../pdfs/`

**LaTeX Gerado Inclui:**
- Preamble completo (packages, macros)
- Título e metadados
- Exercícios agrupados por tipo
- Formatação profissional

**Vantagens:**
- ✅ Controle total do LaTeX final
- ✅ Ajustar formatação/espaçamento
- ✅ Adicionar seções extras
- ✅ Remover exercícios específicos

**Quando Usar:**
- Sebentas para distribuição oficial
- Quando precisa customizar layout
- Para adicionar notas/instruções extras

---

### `📚 Gerar Sebenta (Específica)`

**Parâmetros:**
- `--module`: ID do módulo (ex: `P4_funcoes`)
- `--concept`: ID do conceito (ex: `4-funcao_inversa`)
 - `--tipo`: (novo) Filtrar por tipo de exercício dentro do conceito

**Observação:** usar `--tipo` permite gerar uma sebenta contendo apenas os exercícios de um tipo específico (por exemplo `determinacao_analitica`). Isto é útil para criar compilações por categoria sem incluir todo o conceito.

**Descrição:** Geração direta sem interatividade.

**Quando Usar:**
- Regenerar sebentas já conhecidas
- Automação/scripts
- CI/CD pipelines

---

### `📚 Gerar TODAS as Sebentas`

**Script:** `SebentasDatabase/_tools/generate_sebentas.py`

**Descrição:** Gera sebentas de todos os conceitos de todos os módulos.

**⚠️ Atenção:**
- Processo demorado (vários PDFs)
- Usa recursos significativos
- Recomendado executar fora de horário crítico

**Quando Usar:**
- Atualização geral da base
- Preparação para distribuição
- Após múltiplas alterações de exercícios

---

## 📝 TASKS DE TESTES

### `📝 Gerar Teste (Template Editável)`

**Script:** `SebentasDatabase/_tools/generate_test_template.py`

**Descrição:** Cria teste/exame com seleção de exercícios e LaTeX editável.

**Workflow:**
1. Escolhe módulo (opcional: conceito específico ou todos)
2. Define número de questões
3. **Seleção de exercícios:**
   - **Automático:** Distribuição equilibrada por conceito/tipo
   - **Manual:** Escolher IDs específicos
   - **Aleatório:** Seleção randômica
4. Gera LaTeX completo do teste
5. **Abre para edição** (ajustar cotações, instruções)
6. Compila PDF
7. Guarda em `SebentasDatabase/.../tests/`

**LaTeX Gerado Inclui:**
- Cabeçalho profissional (nome, data, turma)
- Instruções editáveis
- Campos de cotação (editáveis)
- Exercícios formatados
- Folha de rascunho

**Estatísticas Fornecidas:**
- Distribuição por conceito
- Distribuição por tipo de exercício
- Total de questões

**Quando Usar:**
- Criação de testes/exames
- Avaliações personalizadas
- Múltiplas versões (aleatório)

---

### `📝 Gerar Teste (N Questões)`

**Parâmetro:** `--questions N`

**Descrição:** Seleção interativa com número de questões pré-definido.

---

### `📝 Gerar Teste (Módulo Específico)`

**Parâmetros:**
- `--module`: ID do módulo
- `--questions`: Número de questões

**Descrição:** Teste focado num módulo específico.

---

## 🔍 TASKS DE PESQUISA

### `🔍 Pesquisar Exercícios`

**Script:** `ExerciseDatabase/_tools/search_exercises.py`

**Descrição:** Interface interativa de pesquisa.

**Filtros Disponíveis:**
- Módulo
- Conceito
- Tipo
- Dificuldade
- Tags
- Formato
- Autor

**Resultados Mostram:**
- ID do exercício
- Título/descrição
- Classificação completa
- Metadados relevantes

---

### `🔍 Pesquisar por Módulo`

**Parâmetro:** `--module MODULE_ID`

**Descrição:** Lista todos os exercícios de um módulo.

---

### `🔍 Pesquisar por Tag`

**Parâmetro:** `--tag TAG_NAME`

**Descrição:** Encontra exercícios com tag específica.

---

## 🛠️ TASKS DE MANUTENÇÃO

### `🛠️ Gerir Módulos`

**Script:** `ExerciseDatabase/_tools/manage_modules.py`

**Descrição:** CRUD de módulos e conceitos no `modules_config.yaml`.

**Operações:**
- Adicionar novo módulo
- Adicionar conceito a módulo existente
- Editar metadados
- Remover (com confirmação)

**⚠️ Restrição para Agentes:**
Agentes **NÃO PODEM** criar novos módulos/conceitos via templates.
Usar este script explicitamente quando necessário.

---

### `🛠️ Consolidar Metadados de Tipos`

**Script:** `ExerciseDatabase/_tools/consolidate_type_metadata.py`

**Descrição:** Atualiza e valida `metadata.json` de cada tipo.

**Quando Executar:**
- Após adicionar múltiplos exercícios
- Antes de gerar sebentas
- Para corrigir inconsistências

---

### `🛠️ Validar Base de Dados`

**Script:** `tests/quick_validation.py`

**Descrição:** Verifica integridade da base de dados.

**Validações:**
- Estrutura de diretórios
- Ficheiros .tex existentes
- Metadados JSON válidos
- Consistência de `index.json`
- Referências entre ficheiros

**Saída:**
- ✅ Validações com sucesso
- ❌ Erros encontrados (com detalhes)
- ⚠️ Avisos (não críticos)

---

## 🧪 TASKS DE TESTES E DESENVOLVIMENTO

### `🧪 Executar Testes`

**Script:** `ExerciseDatabase/_tools/run_tests.py`

**Descrição:** Suite de testes unitários e de integração.

**Testes Incluídos:**
- Parsing de templates
- Validação de metadados
- Geração de IDs únicos
- Compilação LaTeX básica

---

### `🧪 Gerar Exercícios de Teste`

**Script:** `ExerciseDatabase/_tools/create_test_exercises.py`

**Descrição:** Cria exercícios de exemplo para desenvolvimento/testes.

---

## 📊 TASKS DE ESTATÍSTICAS

### `📊 Ver Estatísticas da Base de Dados`

**Descrição:** Mostra resumo estatístico em tempo real.

**Informações:**
- Total de exercícios
- Versão da base de dados
- Última atualização
- **Por Módulo:** Contagem de exercícios
- **Por Dificuldade:** Distribuição
- **Por Tipo:** Tipos mais usados
- **Por Formato:** Formatos disponíveis

**Fonte:** `ExerciseDatabase/index.json`

---

## 🔄 TASKS DE MIGRAÇÃO

### `🔄 Importar Exercícios QA2`

**Script:** `ExerciseDatabase/_tools/import_qa2_exercises.py`

**Descrição:** Importa exercícios de formato legado QA2.

---

### `🔄 Migrar para Sistema de Tipos`

**Script:** `ExerciseDatabase/_tools/migrate_to_types.py`

**Descrição:** Converte estrutura antiga (sem tipos) para v3.0 (com tipos).

**Processo:**
1. Analisa exercícios existentes
2. Infere tipos por tags/metadados
3. Cria estrutura de diretórios
4. Move ficheiros
5. Atualiza metadados
6. Regenera `index.json`

---

## 🚀 WORKFLOWS COMPOSTOS

### `🚀 Workflow: Criar + Gerar Sebenta`

**Sequência:**
1. `📝 Novo Exercício (Template)`
2. `📚 Gerar Sebenta (Template Editável)`

**Descrição:** Cria exercício e gera sebenta atualizada imediatamente.

---

### `🚀 Workflow: Validar + Estatísticas`

**Sequência:**
1. `🛠️ Validar Base de Dados`
2. `📊 Ver Estatísticas da Base de Dados`

**Descrição:** Valida integridade e mostra resumo completo.

**Quando Usar:**
- Antes de commits importantes
- Após múltiplas alterações
- Troubleshooting de problemas

---

## 🤖 PARA AGENTES (AI ASSISTANTS)

### Quando Sugerir Tasks ao Utilizador

**✅ SEMPRE sugerir task quando utilizador pede:**
- "Cria um exercício sobre X"
- "Gera uma sebenta de Y"
- "Faz um teste com Z questões"
- "Pesquisa exercícios de W"
- "Valida a base de dados"

**Exemplo de Resposta:**
```
Posso ajudar! Recomendo usar a task:
📝 Novo Exercício (Template)

Para executar:
1. Ctrl+Shift+P
2. "Tasks: Run Task"
3. Escolher "📝 Novo Exercício (Template)"

Alternativa (comando direto):
python ExerciseDatabase/_tools/add_exercise_template.py
```

---

### Como Referenciar Tasks em Instruções

**❌ NÃO:**
- "Vou usar a task X para..." (não mencionar internals)
- "Execute manualmente python script.py..." (preferir task)

**✅ SIM:**
- "Recomendo usar a task 📝 Novo Exercício"
- "Para isso existe a task 🔍 Pesquisar Exercícios"
- "A task 🛠️ Validar Base de Dados pode ajudar"

---

### Decisão: Task vs Comando Direto

| Situação | Usar Task | Usar Comando Direto |
|----------|-----------|---------------------|
| Utilizador pede explicitamente | ✅ | ❌ |
| Workflow interativo esperado | ✅ | ❌ |
| Parte de automação maior | ❌ | ✅ |
| Debugging/troubleshooting | ❌ | ✅ |
| Necessita parsing de output | ❌ | ✅ |

---

### Parâmetros CLI Importantes

**Scripts com `--help` detalhado:**
```bash
# Ver opções completas
python ExerciseDatabase/_tools/add_exercise_template.py --help
python SebentasDatabase/_tools/generate_sebenta_template.py --help
python SebentasDatabase/_tools/generate_test_template.py --help
```

**Flags comuns:**
- `--no-preview`: Desabilitar preview (automação)
- `--auto-approve`: Auto-aprovar sem confirmação (CI/CD)
- `--module MODULE`: Especificar módulo
- `--concept CONCEPT`: Especificar conceito
- `--questions N`: Número de questões (testes)

---

### Atualizar `inputs` em tasks.json

**Quando adicionar novos módulos:**

```json
"inputs": [
  {
    "id": "moduleId",
    "options": [
      "P4_funcoes",
      "NOVO_MODULO",  // ← ADICIONAR AQUI
      "..."
    ]
  }
]
```

**Processo:**
1. Editar `.vscode/tasks.json`
2. Adicionar ID na lista `options` de `moduleId`
3. Salvar (auto-reload do VS Code)

---

### Troubleshooting de Tasks

**Problema:** Task não aparece na lista

**Solução:**
1. Verificar sintaxe JSON (`tasks.json`)
2. Recarregar janela: `Ctrl+Shift+P` → "Reload Window"
3. Verificar output: Terminal → "Tasks" output

---

**Problema:** Script não é encontrado

**Solução:**
1. Verificar `cwd` (diretório de trabalho)
2. Usar caminhos relativos à raiz do projeto
3. Verificar que ficheiro existe

---

**Problema:** Task fica "pendurada" (não termina)

**Solução:**
1. Verificar se script aguarda input
2. Usar `"presentation": { "reveal": "always" }` para debug
3. Adicionar timeout se necessário

---

## 📚 REFERÊNCIAS RELACIONADAS

- **Guia de Templates**: `TEMPLATE_SYSTEM_GUIDE.md`
- **Preview System**: `PREVIEW_CONSOLIDADO_GUIDE.md`
- **Estrutura de Tipos**: `ExerciseDatabase/README_TIPOS.md`
- **Configuração de Módulos**: `ExerciseDatabase/modules_config.yaml`
- **Copilot Instructions**: `.github/copilot-instructions.md`

---

## 📝 CHANGELOG

### v1.0 (2025-11-21)
- ✅ Criação inicial do sistema de tasks
- ✅ 26 tasks categorizadas
- ✅ 2 workflows compostos
- ✅ 4 inputs parametrizados
- ✅ Documentação completa para agentes
- ✅ Exemplos de uso para cada categoria

---

## 🆘 SUPORTE

**Para problemas com tasks:**
1. Verificar este guia
2. Executar `🛠️ Validar Base de Dados`
3. Verificar output em Terminal → Tasks
4. Consultar logs de scripts individuais

**Para adicionar novas tasks:**
1. Editar `.vscode/tasks.json`
2. Seguir estrutura existente
3. Adicionar emoji de categoria
4. Documentar neste guia
5. Testar antes de commitar

---

**Última atualização:** 2025-11-21  
**Mantenedor:** Sistema de Exercícios v3.1  
**Feedback:** Sempre bem-vindo via Issues ou PRs
