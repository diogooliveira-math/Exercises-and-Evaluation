# TODO - Projeto Exercises and Evaluation

## Objetivo do Projeto
Criar um sistema completo de gestão e geração de materiais educativos em LaTeX, permitindo aos professores:
- Manter uma base de dados organizada de exercícios
- Gerar exames/testes automaticamente a partir da base
- Compilar materiais didáticos (definições, proposições, exemplos)
- Facilitar a reutilização e organização de conteúdo pedagógico


### Finetuning
- [ ] Limpar os tex e temp files da pasta após a geração de exames
- [ ] Adicionar mais exemplos de exercícios no modelo
- [x] tornar a 4-funcao_inversa por tipos de exercícios (determinacao analítica, gráfica, teste da reta horizontal) ✅ v3.0 implementada!

### Incorporação COPILOT IA
- [ ] Adicionar validação automática de metadados ao criar novo exercício
- [ ] Criar snippets VS Code para diferentes tipos de exercício
- [ ] https://code.visualstudio.com/docs/copilot/getting-started LER E ADICIONAR.
- [ ] Add a VS Code task “Gerar variante (ficheiro atual)” so you can run it with one click?
- [ ] Register a companion agent YAML (like the one I added earlier) to invoke the tool automatically from inputs?

---

## Fase 1: Análise e Estruturação do Projeto ✅

### 1.1 Documentação Inicial ✅
- [x] Analisar o modelo existente (`Teste_modelo`)
- [x] Criar TODO.md com roadmap do projeto
- [x] Atualizar README.md com informação detalhada

### 1.2 Definir Arquitetura do Sistema
- [x] Definir estrutura de pastas para a base de exercícios ✅ v3.0: disciplina/tema/conceito/tipo/exercicio
- [x] Criar esquema de categorização/tags para exercícios ✅ Tags automáticas por tipo + conceito
- [x] Definir formato padrão para metadados dos exercícios ✅ JSON por diretório (Opção A)
- [x] Desenhar fluxo de trabalho: criação → armazenamento → seleção → geração ✅ Scripts add_exercise_with_types.py

---

## Fase 2: Sistema de Base de Dados de Exercícios

### 2.1 Estrutura da Base de Dados
- [ ] Criar pasta `/ExerciseDatabase/` com estrutura hierárquica:
  ```
  ExerciseDatabase/
  ├── matematica/
  │   ├── funcoes/
  │   ├── derivadas/
  │   ├── otimizacao/
  │   └── ...
  ├── fisica/
  └── ...
  ```
- [ ] Definir template padrão para ficheiro de exercício
- [ ] Criar sistema de metadados (dificuldade, tópico, subtópico, tipo, etc.)

### 2.2 Template de Exercício
- [ ] Criar `exercise_template.tex` com:
  - Header com metadados (ID, autor, data, tags, dificuldade)
  - Corpo do exercício
  - Solução (opcional)
  - Critérios de avaliação (opcional)
- [ ] Implementar diferentes tipos de exercício:
  - Desenvolvimento
  - Escolha múltipla
  - Verdadeiro/Falso
  - Resposta curta

### 2.3 Sistema de Indexação
- [ ] Criar ficheiro `index.json` ou `index.yaml` com metadados de todos os exercícios
- [ ] Desenvolver script Python/PowerShell para:
  - Adicionar novos exercícios ao índice
  - Pesquisar exercícios por critérios
  - Validar integridade da base de dados

---

## Fase 3: Gerador Automático de Exames

### 3.1 Sistema de Seleção de Exercícios
- [ ] Criar script de seleção com critérios:
  - Por tópico/subtópico
  - Por dificuldade
  - Por tipo de exercício
  - Aleatória com constraints
- [ ] Implementar sistema de pesos e pontuação total
- [ ] Criar interface de linha de comando para seleção

### 3.2 Template de Exame
- [ ] Melhorar `Teste_modelo` atual:
  - Tornar configurável (título, data, escola, etc.)
  - Adicionar suporte para múltiplos layouts
  - Implementar sistema de versões (A, B, C, etc.)
- [ ] Criar diferentes templates:
  - Teste curto (questão de aula)
  - Teste completo
  - Exame final
  - Fichas de trabalho

### 3.3 Gerador Automático
- [ ] Desenvolver script principal `generate_exam.py` ou `.ps1`:
  - Input: ficheiro de configuração (JSON/YAML)
  - Processo: seleciona exercícios, aplica template, compila
  - Output: PDF do exame + ficheiro de soluções
- [ ] Implementar geração de múltiplas versões com ordem aleatória
- [ ] Criar folha de respostas automática

---

## Fase 4: Gerador de Material Didático

### 4.1 Base de Conteúdo Teórico
- [ ] Criar pasta `/TheoryDatabase/` com estrutura:
  ```
  TheoryDatabase/
  ├── definicoes/
  ├── proposicoes/
  ├── demonstracoes/
  ├── exemplos/
  ├── explicacoes/
  └── ...
  ```
- [ ] Criar templates para cada tipo de conteúdo teórico
- [ ] Implementar sistema de referências cruzadas

### 4.2 Compilador de Material
- [ ] Desenvolver script para agregar conteúdo teórico
- [ ] Criar sistema de geração de:
  - Apontamentos de aula
  - Resumos por tópico
  - Manuais de estudo
  - Fichas de fórmulas

### 4.3 Integração Exercícios + Teoria
- [ ] Implementar links entre teoria e exercícios relacionados
- [ ] Criar gerador de fichas mistas (teoria + prática)

---

## Fase 5: Ferramentas e Automação

### 5.1 Scripts de Gestão
- [ ] `add_exercise.py/ps1` - Adicionar novo exercício à base
- [ ] `search_exercise.py/ps1` - Pesquisar exercícios
- [ ] `validate_database.py/ps1` - Validar integridade
- [ ] `generate_index.py/ps1` - Recriar índice completo
- [ ] `backup_database.py/ps1` - Backup da base

### 5.2 Interface de Linha de Comando
- [ ] Criar CLI unificada com comandos:
  - `exam-tool add` - Adicionar conteúdo
  - `exam-tool search` - Pesquisar
  - `exam-tool generate` - Gerar exame/material
  - `exam-tool validate` - Validar base
  - `exam-tool stats` - Estatísticas da base

### 5.3 Integração com VS Code
- [ ] Criar snippets LaTeX para exercícios
- [ ] Configurar tasks para compilação
- [ ] Criar extensão ou scripts de atalhos

---

## Fase 6: Melhorias no Sistema LaTeX

### 6.1 Macros e Comandos
- [ ] Expandir macros existentes:
  - `\exercicioVerdadeiroFalso{}`
  - `\exercicioRespostaCurta{}`
  - `\exercicioProblema{}`
- [ ] Criar sistema de dificuldade visual (★☆☆)
- [ ] Implementar sistema de pontuação automática

### 6.2 Estilos e Layouts
- [ ] Criar múltiplos estilos visuais
- [ ] Implementar temas personalizáveis
- [ ] Adicionar suporte para múltiplas línguas

### 6.3 Gráficos e Imagens
- [ ] Criar biblioteca de gráficos TikZ reutilizáveis
- [ ] Implementar sistema de gestão de imagens
- [ ] Desenvolver templates de gráficos comuns

---

## Fase 7: Documentação e Exemplos

### 7.1 Documentação Técnica
- [ ] Escrever guia completo de utilização
- [ ] Documentar todos os scripts e suas opções
- [ ] Criar FAQ e troubleshooting
- [ ] Documentar estrutura de metadados

### 7.2 Exemplos e Templates
- [ ] Criar 10+ exercícios exemplo por categoria
- [ ] Desenvolver 5+ templates de exame diferentes
- [ ] Criar exemplos de materiais teóricos
- [ ] Incluir casos de uso completos

### 7.3 Tutoriais
- [ ] Tutorial: Como adicionar um exercício
- [ ] Tutorial: Como gerar um exame
- [ ] Tutorial: Como criar material didático
- [ ] Vídeo demonstrativo (opcional)

---

## Fase 8: Testes e Validação

### 8.1 Testes do Sistema
- [ ] Testar geração de exames com diferentes configurações
- [ ] Validar compilação LaTeX em diferentes ambientes
- [ ] Testar scripts em Windows/Linux/macOS
- [ ] Verificar integridade de referências

### 8.2 Casos de Uso Reais
- [ ] Criar 3 exames completos de exemplo
- [ ] Gerar material didático para 1 unidade completa
- [ ] Obter feedback de professores utilizadores

---

## Fase 9: Funcionalidades Avançadas (Opcional)

### 9.1 Interface Gráfica
- [ ] Desenvolver GUI simples (tkinter/PyQt)
- [ ] Criar interface web (Flask/Django)
- [ ] Implementar drag-and-drop de exercícios

### 9.2 Análise e Estatísticas
- [ ] Gerar estatísticas de uso dos exercícios
- [ ] Análise de dificuldade vs. resultados
- [ ] Relatórios de cobertura de tópicos

### 9.3 Colaboração
- [ ] Sistema de controlo de versões para exercícios
- [ ] Plataforma de partilha entre professores
- [ ] Sistema de revisão e aprovação

### 9.4 Integração com Plataformas
- [ ] Exportação para Moodle/Blackboard
- [ ] Integração com Google Classroom
- [ ] Suporte para formatos adicionais (Word, HTML)

---

## Fase 10: Lançamento e Manutenção

### 10.1 Preparação para Lançamento
- [ ] Criar repositório GitHub público
- [ ] Escrever README.md detalhado
- [ ] Adicionar licença (GPL, MIT, etc.)
- [ ] Criar CHANGELOG.md

### 10.2 Distribuição
- [ ] Criar script de instalação
- [ ] Publicar em PyPI (se Python)
- [ ] Criar release notes
- [ ] Anunciar em comunidades educativas

### 10.3 Manutenção
- [ ] Estabelecer sistema de issues/bugs
- [ ] Criar roadmap de funcionalidades futuras
- [ ] Manter documentação atualizada
- [ ] Responder a comunidade

---

## Prioridades Imediatas (Próximos Passos)

1. **Definir estrutura da base de dados** (Fase 2.1)
2. **Criar template de exercício padrão** (Fase 2.2)
3. **Desenvolver script básico de seleção** (Fase 3.1)
4. **Criar gerador mínimo de exames** (Fase 3.3)
5. **Documentar processo** (Fase 7.1)

---

## Notas Técnicas

### Tecnologias Sugeridas
- **LaTeX**: Sistema base para documentos
- **Python**: Scripts de automação e geração
- **JSON/YAML**: Metadados e configuração
- **PowerShell**: Scripts alternativos para Windows
- **Git**: Controlo de versões

### Dependências
- MiKTeX ou TeX Live
- Python 3.8+
- Bibliotecas Python: PyYAML, jinja2, click (CLI)

### Convenções
- Encoding: UTF-8
- Nomenclatura de ficheiros: lowercase_com_underscores
- IDs de exercícios: `MAT_FUN_001` (disciplina_topico_numero)
- Versionamento: Semantic Versioning (1.0.0)
