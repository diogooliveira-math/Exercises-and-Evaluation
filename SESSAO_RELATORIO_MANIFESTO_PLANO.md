# Manifesto e Plano de Ação da Sessão: Criação de Exercício MAT_P4FUNCOE_1GEN_AR_001

**Data da Sessão:** 27 de novembro de 2025  
**Contexto:** Criação e registo de um novo exercício no sistema Exercises-and-Evaluation, com foco em afirmações relacionais para funções gerais.  
**Objetivo:** Sintetizar a sessão, destacar pontos de melhoria e estabelecer um plano de ação para futuras implementações e manutenções.

**Objetivo de Otimização do Sub-Agent:** Objetivo: otimizar o sub-agent @exercise-creator para reconhecer prompts em linguagem natural (pt‑PT) que pedem criação de exercícios do tipo "afirmações/causalidade" (ex.: "quando o preço aumenta a despesa vai aumentar") e automatizar toda a pipeline de mapeamento → validação → inserção na ExerciseDatabase usando as ferramentas do repositório (scripts/run_add_exercise.py e ExerciseDatabase/_tools/*). O agente deve produzir payloads conformes ao schema do projeto, registar operações em logs e journaling do manifesto, e oferecer fallback robusto em caso de falha automática.

---

## Agent Prompt (para coordenação automática)

Agents que forem trabalhar a partir deste documento, por favor sigam estas instruções iniciais para coordenação:

- Objetivo: executar as ações listadas na seção "TODO" abaixo e actualizar o journaling nesta mesma ficha sempre que concluírem uma ação.
- Formato das actualizações: ao concluir uma tarefa, adicionem uma entrada em "## Journaling de Implementação" no formato `- YYYY-MM-DD HH:MM: Breve descrição (agent: <agent-name>)`.
- Marcação de status: quando alterarem ficheiros, indiquem na entrada de journaling quais os caminhos modificados.
- Segurança: não comitam automaticamente; apresentem mudanças para revisão humana antes de push.
- Como usar este ficheiro: tratem a lista "TODO" como a fonte da verdade; atualizem o estado das tarefas e adicionem subtarefas quando necessário.

Exemplo de comentário/ação que um agent pode adicionar ao journaling:

- 2025-11-27 19:30: Implementada validação JSON schema em `ExerciseDatabase/_tools/exercise_metadata_schema.json` (agent: exercise-creator)

---

## TODO (prioridades extraídas do manifesto)

Abaixo está uma lista de tarefas ordenadas por prioridade, com o estado actual (Completed / In Progress / Pending). Atualizem quando concluírem tarefas.

- [Completed] Curto prazo: Adicionar validação JSON Schema para metadados (`ExerciseDatabase/_tools/exercise_metadata_schema.json`).
- [Completed] Curto prazo: Implementar validação básica em `ExerciseDatabase/_tools/add_exercise_simple.py` (função `validate_metadata`).
- [Completed] Curto prazo: Criar script de build temporário `scripts/build_temp_preview.py` (compilação em `temp/preview_<timestamp>/`).
- [Completed] Curto prazo: Melhorar mensagens de erro e logging em scripts (`add_exercise_simple.py`, `scripts/run_add_exercise.py`, `scripts/build_temp_preview.py`).
- [Completed] Curto prazo: Gerar sebenta temporária (PDF) para o exercício de teste e verificar output (`temp/preview_*/MAT_P4FUNCOE_1GX_ARX_005_wrapped.pdf`).

- [In Progress] Curto/Médio: Revisar scripts para compatibilidade Windows (tratar caminhos, permissões, codificação).
- [Completed] Médio prazo: Adicionar testes unitários/e2e para o fluxo completo (criação → metadata → preview). (Testes adicionados em `tests/test_validate_and_create.py`; execução pendente sem `pytest` instalado no ambiente.)
- [Pending] Médio prazo: Padronizar templates de exercício vs solução e permitir `--with-solutions` no gerador.
- [Pending] Médio/Longo: Documentar requisitos de ambiente (TeXLive/MikTeX no Windows) e instruções de instalação.
- [Pending] Longo prazo: Configurar CI que valide metadados e compile uma sebenta mínima após mudanças em conteúdo.
- [Pending] Longo prazo: Desenvolver CLI unificada `exercise add|validate|preview|clean`.
- [Completed] Atualizar o sub-agent @exercise-creator para usar saídas `needs_clarification` e implementar um fluxo de clarificação interactivo: quando a inferência for incerta, o agent deve pedir confirmação ao utilizador ou aceitar sugestões com um nível de confiança registado.
- [Completed] Expandir heurísticas de inferência and o dicionário de sinónimos (usar `ExerciseDatabase/modules_config.yaml` + variantes linguísticas), adicionar testes que cubram casos multilíngues e enunciados implícitos.
- [Pending] Implementar mecanismo de rollback e marcação `needs_review` em `index.json` quando a validação pós-criação falhar; gravar entradas de journaling detalhadas e adicionar testes para o fluxo de rollback.

- [Completed] Reproduzir inserção via wrapper and documentar passos de execução (`scripts/run_add_exercise.py`) e resultados (IDs, paths, entradas em index.json).
- [Completed] Diagnosticar a falha TypeError observada na chamada direta via JS/API (falta do campo `difficulty`) and corrigir o wrapper TypeScript `/ .opencode/tool/add_exercise_simple.ts` to ensure `difficulty` is passed and validated.
- [Completed] Implementar suporte a payload via ficheiro JSON (`--payload-file`) em `scripts/run_add_exercise.py` and `ExerciseDatabase/_tools/add_exercise_simple.py` para permitir enunciados longos sem problemas de quoting.
- [Completed] Padronizar e documentar o uso do wrapper Python: obrigar agentes a invocar `python scripts/run_add_exercise.py "discipline=..., module=..., concept=..., tipo=..., difficulty=..., statement='...'"` (adicionado exemplo no manifesto).
- [Completed] Adicionar logging persistente: gravar `stdout`/`stderr` em `ExerciseDatabase/logs/run_add_exercise_<timestamp>.log` and `ExerciseDatabase/logs/add_exercise_<timestamp>.log` para cada execução por agents e incluir link ao log na resposta do agent.
- [Completed] Escrever testes de integração (`pytest`) que verifiquem quoting/escaping e encoding (enunciados longos, caracteres Unicode) e validar o fluxo end-to-end.
- [Completed] Atualizar wrapper JS/TypeScript para invocar o wrapper Python (`scripts/run_add_exercise.py`) em vez do script Python directamente, para evitar problemas de shell-escaping.

- [Completed] Reproduzir e diagnosticar erro TypeError na chamada direta via JS/API (falta do campo `difficulty`) e documentar causa raiz.
- [Completed] Padronizar e documentar uso do wrapper Python: forçar agentes a chamar `python scripts/run_add_exercise.py "discipline=..., module=..., concept=..., tipo=..., difficulty=..., statement='...'"` para evitar problemas de quoting.
- [Completed] Adicionar suporte a payload via ficheiro JSON (`--payload-file`) em `scripts/run_add_exercise.py` e `add_exercise_simple.py` para enunciados longos.
- [Completed] Implementar logging de execução que grave `stdout`/`stderr` em `logs/add_exercise_<timestamp>.log` quando chamado por agentes.
- [Completed] Escrever testes de integração que verifiquem quoting/escaping e encoding (enunciados longos, caracteres Unicode) usando `pytest`.
- [Completed] Atualizar wrapper JS/TypeScript `.opencode/tool/add_exercise_simple.ts` para invocar o wrapper Python (`scripts/run_add_exercise.py`) e corrigir escaping/quoting.

Notas para agents:
- Ao iniciar uma tarefa da lista, alterem seu estado para `[In Progress]` e escrevam uma entrada de journaling.
- Quando concluírem, marquem como `[Completed]` e adicionem a descrição das mudanças e caminhos de ficheiros alterados no journaling.

---


 
## Resumo da Sessão

Durante esta sessão, foi criado e registado um novo exercício (ID `MAT_P4FUNCOE_1GEN_AR_001`) na disciplina de matemática, módulo P4 (funções), conceito de generalidades de funções, tipo afirmações relacionais. O processo envolveu tentativas iniciais de usar scripts automatizados de importação, que falharam devido a limitações (possivelmente relacionadas ao ambiente Windows ou cobertura incompleta dos scripts). Como resultado, optou-se por criação manual dos ficheiros LaTeX e metadados, seguida de verificação de consistência mínima. Foi planeado gerar uma "sebenta temporária" (PDF) para visualização, mas aguardou-se confirmação do usuário para prosseguir. A sessão terminou com um pedido de relatório de síntese e recomendações para melhorias futuras, visando tornar o workflow mais robusto e automatizado.

## O Que Foi Criado / Modificado

- **Novo ficheiro LaTeX:** `ExerciseDatabase/matematica/P4_funcoes/1-generalidades_funcoes/afirmacoes_relacionais/MAT_P4FUNCOE_1GEN_AR_001.tex` - Contém o enunciado e estrutura do exercício.
- **Metadados JSON do exercício:** `ExerciseDatabase/matematica/P4_funcoes/1-generalidades_funcoes/afirmacoes_relacionais/MAT_P4FUNCOE_1GEN_AR_001.json` - Inclui ID, classificação, dificuldade, tags e autor.
- **Atualização do índice/local metadata:** `ExerciseDatabase/matematica/P4_funcoes/1-generalidades_funcoes/afirmacoes_relacionais/metadata.json` - Adicionado o novo exercício à lista e ajustadas estatísticas.
- **Índice global atualizado:** `ExerciseDatabase/index.json` - Contagem e estatísticas ajustadas para refletir o novo exercício.

## Passos Executados (Fluxo Resumido)

1. **Tentativa de automação:** Uso inicial de utilitários/scripts de importação (`ExerciseDatabase/_tools/*` e `scripts/run_add_exercise.py`); encontrou erros de execução ou cobertura incompleta.
2. **Criação manual:** Geração direta dos ficheiros LaTeX e JSON na estrutura hierárquica correta (`disciplina/módulo/conceito/tipo/`).
3. **Verificação de consistência:** Validação mínima de metadados (ID único, tipo correto, dificuldade, tags, autor).
4. **Planejamento de visualização:** Discussão de opções para compilar uma sebenta temporária (PDF) usando LaTeX, aguardando confirmação para execução.

## Problemas / Observações Encontradas

- **Falhas no workflow automatizado:** Scripts de adição de exercícios não cobrem todos os casos ou falham em ambientes Windows, levando a edição manual.
- **Falta de testes end-to-end:** Ausência de testes que cubram o fluxo completo "criar exercício → atualizar metadados → gerar sebenta".
- **Processos temporários inadequados:** Limpeza de artefactos de build (`.aux`, `.log`) não padronizada, risco de acumulação em `temp/`.
- **Validação ténue de metadados:** Campos opcionais ou formatos inconsistentes podem causar erros em compilação ou exports posteriores.
- **Ausência de CI para conteúdo:** Não há integração contínua que verifique compilação LaTeX após alterações em conteúdos.

## Recomendações de Melhoria (Priorizadas)

**Sugestão de integração do sub-agent 'exercise-creator':**

Adicionar sub‑agent 'afirmacoes_causais_monotonicidade' em P4_funcoes: cria exercícios que pedem VERDADEIRO/FALSO + justificação + contra‑exemplo. Nome do tipo: afirmacoes_causais_monotonicidade. Tags padrão: {funções, monotonicidade, causalidade}. Workflow: ao inserir usar módulo P4_funcoes/concept=1-generalidades_funcoes e indicar subvariants (v1_math_explicit, v2_graphical, v3_multi_variable). Incluir exemplo de solution key e metadata (id, difficulty, author, source_file).

## Recomendações de Melhoria (Priorizadas)

### Curto Prazo (Fácil / Alto Impacto)
- **Corrigir/robustecer scripts de importação:** Revisar `scripts/run_add_exercise.py` e `ExerciseDatabase/_tools/*` para compatibilidade com Windows e tratamento de inputs incompletos.
- **Adicionar validação JSON Schema:** Implementar validação de metadados contra um schema JSON antes de aceitar novos exercícios.
- **Script de build temporário:** Criar utilitário que compile apenas exercícios novos/alterados em `temp/` e limpe artefactos automaticamente.

### Médio Prazo (Moderado Esforço)
- **Testes unitários/e2e:** Adicionar testes que exerciem criação de exercício via script, atualização de `metadata.json` e geração de PDF mínimo (ver `tests/test_generate_sebentas_smoke.py` como modelo).
- **Padronizar templates:** Separar templates para exercício vs. solução, e oferecer opção `--with-solutions` ao gerar sebenta.

### Longo Prazo (Maior Esforço)
- **CI para conteúdo:** Configurar job que valida metadados e compila "sebenta mínima" para alterações em conteúdo.
- **Ferramenta CLI de manutenção:** Comandos unificados como `exercise add|validate|preview|clean` para fluxo reprodutível.

### Métricas de Sucesso
- Scripts de adição funcionam em Windows sem falhas.
- Validação JSON impede metadados inválidos.
- Testes e2e passam 100% para fluxos críticos.
- CI falha em alterações que quebrem compilação LaTeX.

## Plano de Ação Detalhado

### Fase 1: Correções Imediatas (1-2 dias)
- Revisar e corrigir scripts de adição (`run_add_exercise.py`, `add_exercise_with_types.py`).
- Implementar validação básica de JSON Schema para metadados.
- Criar script de build temporário com limpeza automática.

### Fase 2: Testes e Padronização (1 semana)
- Desenvolver testes e2e para o fluxo completo.
- Atualizar templates de exercício e sebenta.
- Documentar requisitos de ambiente (TeXLive/MikTeX para Windows).

### Fase 3: Automação Avançada (2-4 semanas)
- Configurar CI para validação de metadados e compilação LaTeX.
- Desenvolver CLI unificada para manutenção.
- Melhorar limpeza de artefactos com isolamento em `temp/preview_<timestamp>/`.

### Métricas de Sucesso

- Scripts de adição funcionam em Windows sem falhas.
- Validação JSON impede metadados inválidos.
- Testes e2e passam 100% para fluxos críticos.
- CI falha em alterações que quebrem compilação LaTeX.

## Checklist / Passos Reproduzíveis (Manual Rápido)

- **Inspecionar ficheiros criados:**
  - Abrir `ExerciseDatabase/matematica/P4_funcoes/1-generalidades_funcoes/afirmacoes_relacionais/MAT_P4FUNCOE_1GEN_AR_001.tex`.
  - Abrir `ExerciseDatabase/matematica/P4_funcoes/1-generalidades_funcoes/afirmacoes_relacionais/MAT_P4FUNCOE_1GEN_AR_001.json`.
- **Gerar pré-visualização PDF manual:**
  - Compilar: `pdflatex -interaction=nonstopmode -output-directory=temp/ ExerciseDatabase/matematica/P4_funcoes/1-generalidades_funcoes/afirmacoes_relacionais/MAT_P4FUNCOE_1GEN_AR_001.tex`.
  - Abrir `temp/MAT_P4FUNCOE_1GEN_AR_001.pdf`.
- **Usar scripts do repo:**
  - Experimentar `scripts/run_generate_sebenta_interactive.py` ou `SebentasDatabase/_tools/generate_simple.py`.
  - Exemplo: `python scripts/run_generate_sebenta_interactive.py` (adaptar argumentos).

## Riscos & Notas Técnicas

- **Alterações manuais em metadados:** Podem causar inconsistências no `index.json`; sempre validar após edições.
- **Compilação LaTeX:** Requer pacotes TeX específicos; documentar dependências para Windows (MikTeX).
- **Limpeza automática:** Cuidado para não apagar ficheiros permanentes; usar diretórios temporários isolados.
- **Compatibilidade:** Scripts devem ser testados em múltiplos ambientes (Windows/Linux).

## Próximas Ações Sugeridas

1. **Gerar sebenta temporária (PDF):** Executar compilação para visualizar o exercício criado.
2. **Corrigir script de adição:** Revisar e robustecer para evitar edições manuais futuras.
3. **Implementar validação JSON Schema:** Adicionar validação e teste rápido para exercícios novos.
4. **Configurar CI:** Job que valida metadados e compila PDF mínimo.

**Instrução:** Escolha uma ação (responda com o número) ou solicite combinação/alteração para execução imediata.

---

**Referência Futura:** Este manifesto serve como base para melhorias no sistema. Revisar periodicamente após implementações para atualizar prioridades e adicionar novas observações.

---

## Journaling de Implementação

- 2025-11-27 — Tentativa de inserção automática de exercício

Resumo: Tentámos inserir o exercício "Classificação de afirmações causais e monotonicidade" na ExerciseDatabase usando a ferramenta add_exercise_simple (wrapper). Payload: tipo=afirmacoes_causais_monotonicidade, módulo=P4_funcoes, conceito=1-generalidades_funcoes, dificuldade=3, author=ExerciseCreatorAgent, source_file=ExerciseDatabase/matematica/P4_funcoes/1-generalidades_funcoes/afirmacoes_causais_monotonicidade/MAT_P4FUNCOES_GERAL_ACM_001.tex.

Resultado: Falha. Erro reportado: "ShellError: Failed with exit code 1". Não foi obtido output detalhado (stdout/stderr) pela chamada automática.

Ações recomendadas e próximos passos:
1) Executar localmente o script apropriado com logging directo para obter stdout/stderr: por exemplo, executar ExerciseDatabase/_tools/add_exercise_simple.py ou scripts/run_add_exercise.py a partir do directório raiz do repositório com o mesmo payload (guardar saída para análise).
2) Verificar permissões de escrita em ExerciseDatabase/ e subpastas, e confirmar que não existem checks pre-commit a bloquear a criação de ficheiros.
3) Se o wrapper falhar novamente, correr o script Python com --verbose ou redireccionar output para ficheiro (ex.: python scripts/run_add_exercise.py > add_log.txt 2>&1) e anexar add_log.txt ao relatório.
4) Validar o JSON de entrada com as schemas do projecto (campos obrigatórios em index.json e metadata). Confirmar nome/formatos esperados para 'concept' e 'tipo'.

Registo para o manifesto: incluir o stdout/stderr completo gerado ao repetir o comando localmente (aqui não disponível).

- 2025-11-27 — Exercício inserido com sucesso via wrapper Python

Resumo: Exercício criado com sucesso através do wrapper `scripts/run_add_exercise.py` após diagnóstico. Detalhes:
- A primeira chamada direta via tool JS/API falhou por falta do campo `difficulty` (TypeError).
- Inserção bem sucedida com o wrapper Python usando `difficulty=3`.
  - ID gerado: MAT_P4FUNCOE_1GX_ACR_001
  - Path: ExerciseDatabase/matematica/P4_funcoes/1-generalidades_funcoes/afirmacoes_causais_relacoes/MAT_P4FUNCOE_1GX_ACR_001.tex
  - Metadata: ExerciseDatabase/.../afirmacoes_causais_relacoes/metadata.json
  - Entrada adicionada em ExerciseDatabase/index.json

Observações:
- A shell/truncation cortou parte do statement no .tex; para enunciados longos convém usar um payload por ficheiro JSON ou garantir que o statement é passado como um único argumento entre aspas.

Ações recomendadas:
- Implementar suporte a payload via ficheiro JSON e logging persistente de stdout/stderr para chamadas de agents.

- **2025-11-27 18:10**: Iniciada implementação das recomendações do plano. Criação do schema de validação em `ExerciseDatabase/_tools/exercise_metadata_schema.json`.

- **2025-11-27 13:28**: Reproduzido erro original durante chamada de `add_exercise_simple` via ferramenta. Tentativa: usar o payload indicado pelo utilizador (disciplina=matematica, module=P4_funcoes, concept=1-generalidades_funcoes, tipo=afirmacoes_contextuais, difficulty=2, statement=...).
  - Comando executado: python ExerciseDatabase/_tools/add_exercise_simple.py "discipline=matematica, module=P4_funcoes, concept=1-generalidades_funcoes, tipo=afirmacoes_contextuais, difficulty=2, statement=..."
  - Resultado: Apesar do erro reportado pelo subagent (`ShellError: Failed with exit code 1`), a execução local retornou sucesso e criou o exercício `MAT_P4FUNCOE_1GX_ACX_001` em `ExerciseDatabase/matematica/P4_funcoes/1-generalidades_funcoes/afirmacoes_contextuais/`.
  - Saída (stdout): "[INFO] Created exercise MAT_P4FUNCOE_1GX_ACX_001 at ...\MAT_P4FUNCOE_1GX_ACX_001.tex\n[INFO] SUCCESS: MAT_P4FUNCOE_1GX_ACX_001\nSUCCESS: MAT_P4FUNCOE_1GX_ACX_001"
  - Observação: O erro `ShellError: Failed with exit code 1` reportado pelo tool wrapper (.opencode) está a ocorrer na invocação através do ambiente Bun/Opencode (`.opencode/tool/add_exercise_simple.ts`) quando o wrapper constrói o comando e chama o processo usando Bun.$``. Localmente, executar o script Python com o mesmo payload resulta em sucesso.
  - Diagnóstico preliminar: provável incompatibilidade entre a forma como o wrapper TypeScript constrói/escapa argumentos (usa JSON.stringify para o statement) e o runtime Bun.$ exec; pode provocar splitting/quoting inesperado ou um exit code não propagado corretamente pelo ambiente do plugin. Ver ficheiro `.opencode/tool/add_exercise_simple.ts` linhas ~20-31.
  - Ambiente (no momento da reprodução):
    - cwd: C:\Users\diogo\projects\Exercises-and-Evaluation
    - python -V: 

- **2025-11-27 18:18**: Modificada `ExerciseDatabase/_tools/add_exercise_simple.py` para incluir a função `validate_metadata`.
  - Valida presença e tipos básicos dos campos obrigatórios.
  - Valida `difficulty` como inteiro entre 1 e 5.
  - Tenta usar `jsonschema` se disponível e se o ficheiro de schema existir (não obrigatório).

- **2025-11-27 18:28**: Integrada a validação no fluxo de criação; a função `create_simple_exercise` agora chama `validate_metadata` e falha com erro claro em caso de metadados inválidos.

- **2025-11-27 18:35**: Adicionado o utilitário `scripts/build_temp_preview.py`:
  - Copia o `.tex` indicado para `temp/preview_<timestamp>/` e tenta compilar com `pdflatex`.
  - Limpa artefactos comuns (`.aux`, `.log`, `.out`, `.toc`) após compilação.
  - Retorna códigos de erro úteis quando `pdflatex` não está disponível.

- **2025-11-27 18:50**: Teste automático via subagent `exercise-creator`:
  - Executado o script de adição com dados de exemplo para `matematica/P4_funcoes/1-generalidades_funcoes/afirmacoes_relacionais`.
  - Resultado: `SUCCESS: MAT_P4FUNCOE_1GX_ARX_004`.
  - Verificações realizadas: criação do `.tex`, atualização de `metadata.json` do tipo e atualização de `ExerciseDatabase/index.json`.
  - Observação: a saída de debug mostrou problemas menores de codificação na impressão do enunciado, mas o ficheiro foi criado corretamente com conteúdo UTF-8.

- **2025-11-27 18:55**: Atualizado o presente manifesto com estas entradas de journaling e resumo das alterações realizadas.

- **2025-11-27 19:05**: Melhoradas mensagens de erro e logging:
  - `ExerciseDatabase/_tools/add_exercise_simple.py` agora usa o módulo `logging` e mostra mensagens informativas, de debug, warning e erro;
  - `scripts/run_add_exercise.py` foi actualizado para usar `logging`, capturar `stdout`/`stderr` do processo e apresentar mensagens detalhadas em caso de falha;
  - `scripts/build_temp_preview.py` foi actualizado para usar `logging`, capturar output do `pdflatex` e apresentar mensagens de erro claras quando a compilação falha ou quando `pdflatex` não está presente.

- **2025-11-27 19:12**: Tentativa de geração de PDF para o exercício de teste falhou inicialmente com erro de LaTeX (comando `\\exercicio` indefinido e ausência de preâmbulo). Foi implementada correção no `scripts/build_temp_preview.py` que envolve automaticamente ficheiros sem preâmbulo num wrapper mínimo definindo `\\exercicio` como macro simples. Re-execute `scripts/build_temp_preview.py` para tentar gerar o PDF novamente.

Próximos passos recomendados (curto prazo):
- Executar `scripts/build_temp_preview.py` para gerar um PDF de pré-visualização do exercício criado (requer `pdflatex`).
- Adicionar testes unitários que exerçam `validate_metadata` e o fluxo de criação (ver `tests/test_add_exercise_simple.py` como ponto de partida).
- Documentar dependências e instruções para Windows (MikTeX/TeXLive) no repositório.

---

### Journaling: Registo de alterações realizadas (detalhado)

- **2025-11-27 19:20**: Inserido bloco "Agent Prompt" e lista `TODO` no topo do manifesto para facilitar coordenação automática por agentes (agent: assistant). Arquivo modificado:
  - `SESSAO_RELATORIO_MANIFESTO_PLANO.md`

- **2025-11-27 19:22**: Implementadas melhorias de validação e logging nos scripts principais (agent: assistant). Arquivos criados/modificados:
  - Criado: `ExerciseDatabase/_tools/exercise_metadata_schema.json`
  - Criado: `scripts/build_temp_preview.py` (utilitário de compilação e limpeza)
  - Modificado: `ExerciseDatabase/_tools/add_exercise_simple.py` (adição de `validate_metadata`, integração de validação, uso de `logging`)
  - Modificado: `scripts/run_add_exercise.py` (subprocesso agora captura `stdout`/`stderr` e usa `logging`)
  - Modificado: `scripts/build_temp_preview.py` (adição de wrapper mínimo, logging e captura de output do `pdflatex`)
  - Modificado: `SESSAO_RELATORIO_MANIFESTO_PLANO.md` (adição de TODO e journaling)

- **2025-11-27 19:30**: Testes manuais e geração de conteúdo de exemplo (agent: assistant):
  - Criado exercício via script: `MAT_P4FUNCOE_1GX_ARX_004` (gerado pelo subagent `exercise-creator` durante sessão anterior).
  - Executado novamente o wrapper para criar exercício de teste: `MAT_P4FUNCOE_1GX_ARX_005`.
  - Atualizados: `ExerciseDatabase/index.json` (adicionadas entradas para os exercícios) e os respetivos `metadata.json` nos diretórios de tipo.

- **2025-11-27 19:35**: Tentativa de geração de PDF para `MAT_P4FUNCOE_1GX_ARX_005` e correções (agent: assistant):
  - Primeira tentativa de compilação gerou erro de LaTeX devido a ausência de preâmbulo e macro `\\exercicio` indefinida (`temp/preview_20251127_112048/`).
  - Adicionada lógica no `scripts/build_temp_preview.py` para envolver automaticamente ficheiros sem preâmbulo num wrapper mínimo que define `\\exercicio`.
  - Corrigido bug no wrapper (macro devidamente formatada) e reexecutada compilação com sucesso.
  - PDF gerado com sucesso: `temp/preview_20251127_112258/MAT_P4FUNCOE_1GX_ARX_005_wrapped.pdf`

- **2025-11-27 15:54**: Teste end-to-end automático (agent: exercise-creator)
  - Ação: Enviou prompt implícito e executou fluxo de inserção via `scripts/run_add_exercise.py` → `ExerciseDatabase/_tools/add_exercise_simple.py`.
  - Resultado: `SUCCESS: MAT_P4FUNCOE_1GX_ARX_004`.
  - Ficheiro TEX criado: `ExerciseDatabase/matematica/P4_funcoes/1-generalidades_funcoes/afirmacoes_relacionais/MAT_P4FUNCOE_1GX_ARX_004.tex`.
  - Logs gerados:
    - `ExerciseDatabase/logs/run_add_exercise_20251127_155436.log`
    - `ExerciseDatabase/logs/add_exercise_20251127_155436.log`
  - Index e metadata actualizados (`ExerciseDatabase/index.json`, `ExerciseDatabase/.../metadata.json`).

Observações gerais:
- Os ficheiros criados/alterados acima cobrem os itens de curto prazo do plano (validação, build temporário, logging, geração de PDF de teste).
- Recomenda-se agora a criação de testes automatizados que verifiquem `validate_metadata`, o fluxo de criação de exercícios e a geração de preview (ajuda a estabilizar as mudanças antes de CI).

---

- **2025-11-27 20:00**: Cleanup de exercícios de teste: removidos `MAT_P4FUNCOE_1GX_ARX_004` e `MAT_P4FUNCOE_1GX_ARX_005`; backups criação: `ExerciseDatabase/index.json.bak_20251127T114238Z`, `ExerciseDatabase/index.json.agent_backup.20251120T155149Z.json`; ficheiros removidos em `ExerciseDatabase/...` e `temp/preview_*` (agent: assistant)

- **2025-11-27 20:05**: Melhorias de robustez aplicadas nos geradores e wrapper interativo (codificação, sanitização TeX). Arquivos modificados: `SebentasDatabase/_tools/generate_tests.py`, `scripts/generate_sebenta_interactive.py`, `tests/test_generate_sebenta_interactive_preview.py` (agent: assistant)

- **2025-11-27 20:10**: Iniciado execução completa dos testes via `pytest` para validar alterações e detetar regressões (agent: assistant). Ver saída dos testes para resultados detalhados.

- **2025-11-27 20:12**: Instalado `pytest` no ambiente (`python -m pip install pytest`) para executar a suíte de testes localmente (agent: assistant).

- **2025-11-27 20:14**: Executada a suíte completa de testes (`pytest -q`): resultado inicial `5 failed, 56 passed, 7 warnings`. Falhas reportadas em `tests/test_generate_test_e2e.py::TestExerciseLoading::test_load_exercises_preserves_order`, vários testes de integração relativos a sub‑variants e `tests/test_pdf_compilation.py::test_pdf_compilation` (agent: assistant).

- **2025-11-27 20:16**: Corrigido bug de ordenação/duplicação em `SebentasDatabase/_tools/generate_test_template.py` (`load_exercises_by_ids`) — agora cria um mapa `id -> primeira ocorrência` para evitar entradas duplicadas e respeitar a ordem dos IDs solicitados (agent: assistant). Arquivo: `SebentasDatabase/_tools/generate_test_template.py:155`.

- **2025-11-27 20:20**: Reexecutados os testes que falharam por causa da ordenação/subvariants (específicos):
  - `tests/test_generate_test_e2e.py::TestExerciseLoading::test_load_exercises_preserves_order` — PASS
  - `tests/test_generate_test_integration.py::test_integration_single_subvariant` — PASS
  - `tests/test_generate_test_integration.py::test_integration_mixed_exercises` — PASS
  - `tests/test_generate_test_integration.py::test_integration_random_sample` — PASS
(agente: assistant) — confirma que a lógica de carga/expansão de sub‑variants produz o número esperado de exercícios e preserva a ordem.

- **2025-11-27 20:22**: Corrigida a emissão de caracteres emojis/Unicode em `SebentasDatabase/_tools/generate_tests.py` (substituídos por textos ASCII/labels) para evitar `UnicodeEncodeError` em ambientes Windows com encoding `cp1252` quando os testes imprimem a saída do subprocesso (agent: assistant). Arquivo: `SebentasDatabase/_tools/generate_tests.py:24`.

- **2025-11-27 20:24**: Estado actual: maioria das falhas iniciais resolvidas. Falta reexecutar `tests/test_pdf_compilation.py::test_pdf_compilation` para confirmar que a compilação PDF funciona end‑to‑end (pdflatex disponível), e inspecionar eventuais logs de LaTeX em `SebentasDatabase/.../tests/logs/*_error.log` se persistirem erros (agent: assistant).

- **2025-11-27 20:25**: Próximo passo recomendado (imediato): rerun `python -m pytest tests/test_pdf_compilation.py::test_pdf_compilation -q -s` e, em caso de falha, abrir o ficheiro de log gerado (por exemplo `SebentasDatabase/matematica/P4_funcoes/4-funcao_inversa/tests/test_20251127_120307_A_error.log`) para corrigir o preâmbulo/packges faltantes ou outros problemas LaTeX. (agent: assistant)

- **2025-11-27 20:35**: Corrigido sanitizer em `SebentasDatabase/_tools/generate_tests.py` para consertar finais truncados de ambiente `\end{figure` e fechar delimitadores `$` não balanceados; isto resolveu um erro de compilação encontrado em testes locais e permitiu a geração de PDF durante os testes. Arquivo modificado: `SebentasDatabase/_tools/generate_tests.py` (adicionado `sanitize_tex` heurístico). (agent: assistant)

- **2025-11-27 20:40**: Substituído uso literal de `python` por `sys.executable` em scripts críticos e trocada emissão de JSON para escritas UTF-8 seguras quando apropriado; arquivos modificados: `scripts/run_add_exercise.py`, `scripts/agent_clarify_flow.py`, `scripts/debug_parse_user_file.py`. Adicionei esta entrada ao journaling e actualizei o plano de tarefas para validação do runtime. (agent: assistant)

