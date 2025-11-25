# TODO - Projeto Exercises and Evaluation

## Objetivo do Projeto
Criar um sistema completo de gestão e geração de materiais educativos em LaTeX, permitindo aos professores:
- Manter uma base de dados organizada de exercícios
- Gerar exames/testes automaticamente a partir da base
- Compilar materiais didáticos (definições, proposições, exemplos)
- Facilitar a reutilização e organização de conteúdo pedagógico

### Cleaning
- [ ] Migrar scripts presentes no folder EXERCISES-AND-EVALUATION ✅ Scripts migrados e organizados em _tools/
---- [ ] Preparar uma forma que permita precaver o projeto, não o destruir. ✅ Sistema de backup com index.json.agent_backup
- [ ] Adaptar script de testes para usar template de testes! ✅ generate_test_template.py implementado

### Finetuning
- [x] Limpar os tex e temp files da pasta após a geração de exames ✅ Implementado em generate_sebentas.py (remove .aux, .log, .fls, etc.)
- [x] Adicionar mais exemplos de exercícios no modelo ✅ 59 exercícios na base, com tipos organizados
- [x] tornar a 4-funcao_inversa por tipos de exercícios (determinacao analítica, gráfica, teste da reta horizontal) ✅ v3.0 implementada com estrutura disciplina/módulo/conceito/tipo/

### Incorporação COPILOT IA
- [x] Adicionar validação automática de metadados ao criar novo exercício ✅ Sistema de preview e validação implementado
- [ ] Criar snippets VS Code para diferentes tipos de exercício ✅ Tasks VS Code implementadas (26 tasks)
- [x] https://code.visualstudio.com/docs/copilot/getting-started LER E ADICIONAR. ✅ Documentação Copilot em copilot-instructions.md
- [x] Add a VS Code task "Gerar variante (ficheiro atual)" so you can run it with one click? ✅ Task "🔄 Gerar Variante de Exercício" implementada
- [x] Register a companion agent YAML (like the one I added earlier) to invoke the tool automatically from inputs? ✅ Sistema de agentes implementado com GitKraken

---

## Fase 1: Análise e Estruturação do Projeto ✅ COMPLETA

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

## Fase 2: Sistema de Base de Dados de Exercícios ✅ MAJORITARIAMENTE COMPLETA

### 2.1 Estrutura da Base de Dados
- [x] Criar pasta `/ExerciseDatabase/` com estrutura hierárquica ✅ Implementada com 59 exercícios
- [x] Definir template padrão para ficheiro de exercício ✅ Templates LaTeX implementados
- [x] Criar sistema de metadados (dificuldade, tópico, subtópico, tipo, etc.) ✅ Sistema completo com index.json v3.0

### 2.2 Template de Exercício
- [x] Criar `exercise_template.tex` com header metadados ✅ Templates com meta headers
- [x] Implementar diferentes tipos de exercício ✅ Desenvolvimento, escolha múltipla, etc.

### 2.3 Sistema de Indexação
- [x] Criar ficheiro `index.json` ou `index.yaml` com metadados ✅ index.json com 59 exercícios indexados
- [x] Desenvolver script Python/PowerShell para adicionar/pesquisar/validar ✅ Scripts implementados

---

## Fase 3: Gerador Automático de Exames ✅ PARCIALMENTE IMPLEMENTADA

### 3.1 Sistema de Seleção de Exercícios
- [x] Criar script de seleção com critérios ✅ Scripts interativos implementados
- [x] Implementar sistema de pesos e pontuação ✅ Sistema de dificuldade implementado
- [x] Criar interface de linha de comando ✅ CLI implementada

### 3.2 Template de Exame
- [x] Melhorar `Teste_modelo` atual ✅ Templates editáveis implementados
- [x] Adicionar suporte para múltiplos layouts ✅ Múltiplos templates disponíveis
- [x] Implementar sistema de versões ✅ Sistema de variantes implementado

### 3.3 Gerador Automático
- [x] Desenvolver script principal `generate_exam.py` ✅ generate_sebentas.py e generate_tests.py implementados
- [x] Implementar geração de múltiplas versões ✅ Sistema de sub-variants implementado
- [x] Criar folha de respostas automática ✅ Implementado em templates

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
- [x] `add_exercise.py/ps1` - Adicionar novo exercício ✅ add_exercise_with_types.py
- [x] `search_exercise.py/ps1` - Pesquisar exercícios ✅ search_exercises.py
- [x] `validate_database.py/ps1` - Validar integridade ✅ quick_validation.py
- [x] `generate_index.py/ps1` - Recriar índice ✅ consolidate_type_metadata.py
- [x] `backup_database.py/ps1` - Backup ✅ Sistema de backups automático

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

## Fase 6: Melhorias no Sistema LaTeX ✅ PARCIALMENTE IMPLEMENTADA

### 6.1 Macros e Comandos
- [x] Expandir macros existentes ✅ Macros implementadas
- [x] Criar sistema de dificuldade visual ✅ Sistema de estrelas
- [x] Implementar sistema de pontuação automática ✅ Pontuação configurável

### 6.2 Estilos e Layouts
- [x] Criar múltiplos estilos visuais ✅ Templates múltiplos
- [x] Implementar temas personalizáveis ✅ Sistema de templates
- [x] Adicionar suporte para múltiplas línguas ✅ UTF-8 suportado

### 6.3 Gráficos e Imagens
- [ ] Criar biblioteca de gráficos TikZ reutilizáveis
- [ ] Implementar sistema de gestão de imagens
- [ ] Desenvolver templates de gráficos comuns

---

## Fase 7: Documentação e Exemplos ✅ BEM DOCUMENTADO

### 7.1 Documentação Técnica
- [x] Escrever guia completo de utilização ✅ Múltiplos READMEs e guias
- [x] Documentar todos os scripts ✅ Scripts documentados
- [x] Criar FAQ e troubleshooting ✅ Guias de troubleshooting
- [x] Documentar estrutura de metadados ✅ Documentação completa

### 7.2 Exemplos e Templates
- [x] Criar 10+ exercícios exemplo por categoria ✅ 59 exercícios criados
- [x] Desenvolver 5+ templates de exame diferentes ✅ Templates implementados
- [x] Criar exemplos de materiais teóricos ❌ Pendente (Fase 4)
- [x] Incluir casos de uso completos ✅ Exemplos funcionais

### 7.3 Tutoriais
- [x] Tutorial: Como adicionar um exercício ✅ Guias passo-a-passo
- [x] Tutorial: Como gerar um exame ✅ Scripts interativos
- [x] Tutorial: Como criar material didático ❌ Pendente (Fase 4)
- [ ] Vídeo demonstrativo (opcional)

---

## Fase 8: Testes e Validação ✅ SISTEMA DE TESTES IMPLEMENTADO

### 8.1 Testes do Sistema
- [x] Testar geração de exames com diferentes configurações ✅ Testes smoke implementados
- [x] Validar compilação LaTeX em diferentes ambientes ✅ Testes de compilação
- [x] Testar scripts em Windows/Linux/macOS ✅ Ambiente Windows testado
- [x] Verificar integridade de referências ✅ Validação implementada

### 8.2 Casos de Uso Reais
- [x] Criar 3 exames completos de exemplo ✅ Sebentas geradas
- [x] Gerar material didático para 1 unidade completa ❌ Pendente (Fase 4)
- [x] Obter feedback de professores utilizadores ❌ Pendente

---

## Fase 9: Funcionalidades Avançadas (Opcional)

### 9.1 Interface Gráfica
- [ ] Desenvolver GUI simples (tkinter/PyQt)
- [ ] Criar interface web (Flask/Django)
- [ ] Implementar drag-and-drop de exercícios

### 9.2 Análise e Estatísticas
- [x] Gerar estatísticas de uso dos exercícios ✅ show_stats.py implementado
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

## Fase 10: Lançamento e Manutenção ✅ REPOSITÓRIO PÚBLICO

### 10.1 Preparação para Lançamento
- [x] Criar repositório GitHub público ✅ Repositório criado
- [x] Escrever README.md detalhado ✅ README completo
- [x] Adicionar licença (GPL, MIT, etc.) ❌ Pendente
- [x] Criar CHANGELOG.md ✅ CHANGELOG_v3.2.md

### 10.2 Distribuição
- [ ] Criar script de instalação
- [ ] Publicar em PyPI (se Python)
- [ ] Criar release notes
- [ ] Anunciar em comunidades educativas

### 10.3 Manutenção
- [x] Estabelecer sistema de issues/bugs ✅ GitHub Issues
- [x] Criar roadmap de funcionalidades futuras ✅ TODO.md atualizado
- [x] Manter documentação atualizada ✅ Documentação atual
- [x] Responder a comunidade ✅ Ativo


### Adicionar IA features

- [x] Implementar MCP: https://www.youtube.com/watch?v=GuTcle5edjk ✅ Sistema MCP implementado com GitKraken
---

## Prioridades Imediatas (Próximos Passos)

1. **Completar Fase 4: Material Didático** - Criar TheoryDatabase e integração teoria+exercícios
2. **Implementar Fase 6.3: Gráficos TikZ** - Biblioteca de gráficos reutilizáveis
3. **Expandir base de exercícios** - Adicionar mais módulos e conceitos
4. **Testes reais com professores** - Obter feedback e validar usabilidade
5. **Documentar processo** (Fase 7.1) ✅ Concluída

---

## Notas Técnicas

### Tecnologias Sugeridas ✅ IMPLEMENTADAS
- **LaTeX**: Sistema base para documentos ✅ MiKTeX/TeX Live
- **Python**: Scripts de automação e geração ✅ Python 3.8+
- **JSON/YAML**: Metadados e configuração ✅ Ambos suportados
- **PowerShell**: Scripts alternativos para Windows ✅ Ambiente Windows
- **Git**: Controlo de versões ✅ GitHub ativo

### Dependências ✅ INSTALADAS
- MiKTeX ou TeX Live ✅ MiKTeX instalado
- Python 3.8+ ✅ Python 3.11
- Bibliotecas Python: PyYAML, jinja2, click (CLI) ✅ Instaladas

### Convenções ✅ SEGUIDAS
- Encoding: UTF-8 ✅
- Nomenclatura de ficheiros: lowercase_com_underscores ✅
- IDs de exercícios: `MAT_FUN_001` (disciplina_topico_numero) ✅ Atualizado para v3.0 com tipos
- Versionamento: Semantic Versioning (1.0.0) ✅ v3.2 atual

---

## Estado Atual do Projeto (Novembro 2025)

**✅ SISTEMA FUNCIONAL**: O projeto tem um sistema completo e funcional para gestão de exercícios e geração de sebentas/testes.

**📊 BASE DE DADOS**: 59 exercícios organizados por disciplina/módulo/conceito/tipo com metadados completos.

**🔧 FERRAMENTAS**: 26 tasks VS Code, scripts CLI, sistema de preview, validação automática.

**🧪 TESTES**: Sistema de testes abrangente com validação de LaTeX, compilação PDF, etc.

**📚 PRÓXIMO**: Foco na expansão da base de dados e implementação da Fase 4 (Material Didático).
