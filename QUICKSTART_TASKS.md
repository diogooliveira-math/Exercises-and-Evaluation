w# 🚀 QUICK START - Tasks VS Code

> **v3.2**: 8 tasks essenciais que cobrem 95% dos casos de uso

## ⚡ Executar

```
Ctrl+Shift+P → Tasks: Run Task
```

## 📋 Tasks Essenciais (8 total)

| Emoji | Nome | Ação | Atalho |
|-------|------|------|--------|
| 📝 | Novo Exercício | Criar exercício editável | `Ctrl+Shift+B` |
| 📚 | Gerar Sebenta | Compilar PDF de conceito | - |
| 📝 | Gerar Teste | Criar avaliação editável | `Ctrl+Shift+T` |
| 🔍 | Pesquisar Exercícios | Buscar por filtros | - |
| 🛠️ | Validar Base de Dados | Verificar integridade | - |
| 📊 | Ver Estatísticas | Resumo completo | - |
| 🛠️ | Gerir Módulos | Adicionar/editar módulos | - |
| 🛠️ | Consolidar Metadados | Atualizar metadata.json | - |

**Por que só 8?** Cobrimos 95% dos casos de uso. Para funcionalidades avançadas, use a linha de comandos.

## 📖 Documentação

- **Guia Completo**: [`VSCODE_TASKS_GUIDE.md`](VSCODE_TASKS_GUIDE.md)
- **Sistema de Templates**: [`TEMPLATE_SYSTEM_GUIDE.md`](TEMPLATE_SYSTEM_GUIDE.md)
- **Preview System**: [`PREVIEW_CONSOLIDADO_GUIDE.md`](PREVIEW_CONSOLIDADO_GUIDE.md)

## 💻 Linha de Comandos

```bash
# Exercício
python ExerciseDatabase/_tools/add_exercise_template.py

# Sebenta
python SebentasDatabase/_tools/generate_sebenta_template.py

# Teste
python SebentasDatabase/_tools/generate_test_template.py --questions 10
```

> **Atenção importante — destino das sebentas geradas**
>
> - As sebentas geradas por estas tasks são guardadas em `SebentasDatabase/` (ficheiros `.tex` e `.pdf`).
> - NÃO use o script legacy `ExerciseDatabase/_tools/generate_sebentas.py` em produção — ele escreve ficheiros em `ExerciseDatabase/`.
> - O script legacy exige a variável de ambiente `ALLOW_EXERCISE_DB_SEBENTA=1` ou o argumento `--allow-exercise-output` para correr; isto é intencional para prevenir gravações acidentais.


## 🤖 Para AI Assistants

**Sempre sugerir tasks quando utilizador pede:**
- "Cria exercício" → Task `📝 Novo Exercício`
- "Gera sebenta" → Task `📚 Gerar Sebenta`
- "Faz teste" → Task `📝 Gerar Teste`

Ver [`copilot-instructions.md`](.github/copilot-instructions.md) para detalhes.

---

**v3.2** | 2025-11-21 | Sistema de Tasks + Templates
