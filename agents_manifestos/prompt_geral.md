# Manifesto Geral para Intervenções por Agentes - Exercises-and-Evaluation

**Data da Sessão:** [INSERIR DATA]  
**Contexto:** [DESCREVER OBJETIVO GERAL, e.g., "Otimização de scripts de geração de exercícios"]  
**Objetivo:** [SÍNTESE CONCISA DO QUE SE PRETENDE ALCANÇAR]

## Agent Prompt (para coordenação automática)

Agentes que trabalhem nesta intervenção, sigam estas instruções iniciais:

- **Objetivo**: Executar as ações na seção "TODO" abaixo e adicionar entradas ao journaling via `add_journal_entry.py` sempre que concluírem uma ação.
- **Formato de Atualizações**: Ao concluir uma tarefa, usar `add_journal_entry.py` para adicionar entrada em `journaling/` no formato `- YYYY-MM-DD HH:MM: Breve descrição (agent: <agent-name>)`.
- **Marcação de Estado**: Indicar arquivos modificados. Não fazer commits automáticos; apresentar mudanças para revisão humana.
- **Segurança**: Evitar exfiltração de segredos; usar logs em `journaling/`.
- **Como Usar Este Arquivo**: Tratar "TODO" como fonte da verdade; atualizar estados e adicionar subtarefas se necessário.

Exemplo: `- 2025-11-28 10:00: Implementada validação em script X (agent: assistant)`. Use `add_journal_entry.py --intervencao "nome" --data "2025-11-28 10:00" --descricao "Breve descrição" --agente "assistant"`.

---

## TODO (prioridades extraídas do contexto)

- [ ] [DESCREVER TAREFA 1 - PRIORIDADE ALTA]
- [ ] [DESCREVER TAREFA 2 - PRIORIDADE MÉDIA]
- [ ] [Etc.]

---

## Resumo da Intervenção

[SÍNTESE CONCISA: O que foi feito, problemas encontrados, recomendações.]

## O Que Foi Criado/Modificado

- [LISTA SINTÉTICA DE ARQUIVOS/ALTERAÇÕES]

## Problemas/Observações

[LISTA CURTA DE ISSUES-CHAVE]

## Recomendações de Melhoria

[PRIORIDADES CURTO/MÉDIO/LONGO PRAZO]

## Plano de Ação Detalhado

[Fases com métricas simples]

## Próximas Ações Sugeridas

[3-5 AÇÕES IMEDIATAS]

---

**Referência Futura:** Este manifesto é adaptável para outros objetivos. Revisar periodicamente.
