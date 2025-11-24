# Uso das tasks relacionadas com geração de sebentas

- Task principal (interactiva): `📚 Gerar Sebenta (Interactivo)`
  - Abre um assistente interativo na terminal que lista disciplinas, módulos, conceitos e tipos encontrados em `ExerciseDatabase/`.
  - Permite escolher (ou deixar vazio para "todos") e invoca `generate_sebentas.py` com os filtros apropriados.
  - As opções `Desabilitar preview` e `Aprovar automaticamente` podem ser fornecidas pela task (inputs) ou respondidas durante o assistente.

Como usar via VS Code

1. Ctrl+Shift+P → "Tasks: Run Task" → escolher `📚 Gerar Sebenta (Interactivo)`.
2. Selecione disciplina, módulo, conceito e tipo conforme solicitado (ENTER para selecionar todos).
3. O assistente invoca o gerador com as flags escolhidas.

Nota técnica

- O script interativo é `scripts/run_generate_sebenta_interactive.py`.
- A task passa duas variáveis de ambiente para o script: `SEBENTA_NO_PREVIEW` e `SEBENTA_AUTO_APPROVE`.
- Para uso em CI ou automação, execute diretamente:

```powershell
python .\SebentasDatabase\_tools\generate_sebentas.py --discipline matematica --module P4_funcoes --concept 4-funcao_inversa --no-preview --auto-approve
```
