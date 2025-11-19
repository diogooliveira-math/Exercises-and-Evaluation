# 📦 Estado Atual do ExerciseDatabase (v3.0.1)

## 🆕 IMPORTANTE: Sistema Atualizado para Tipos (v3.0)

**Hierarquia**: `disciplina/tema/conceito/TIPO/exercicio.tex`

**Exemplo atual**:
- `matematica/P4_funcoes/4-funcao_inversa/` tem 3 tipos
- Cada tipo tem 5 exercícios mínimo
- Total: 15 exercícios (5×3 tipos)

**Metadados**: Apenas `metadata.json` por tipo (lista de IDs), sem `.json` individuais.

---

## ✅ Limpeza concluída (v2.0 - arquivo)

- Base de dados limpa: `matematica/` sem exercícios (pastas vazias mantidas).
- Índice reiniciado: `index.json` sem entradas.
- Testes passarão a usar a pasta `test/`.

---

## 🗂️ Estrutura Relevante

```text
ExerciseDatabase/
├── modules_config.yaml         ← Configuração (módulos e conceitos)
├── index.json                  ← Índice (atualmente vazio)
├── matematica/                 ← Base real (vazia por enquanto)
├── test/                       ← Área isolada para dados de teste
└── _tools/                     ← Ferramentas (add/search/tests)
```

---

## 🚀 Como usar

- Adicionar exercício real:

```powershell
cd "c:\Users\diogo\OneDrive\AAA\Projects\Exercises and Evaluation\ExerciseDatabase\_tools"
python add_exercise.py
```

- Pesquisar na base (usa `index.json`):

```powershell
python search_exercises.py
```

- Executar testes (gera exemplos em `test/`):

```powershell
python run_tests.py
```

---

## ℹ️ Notas

- Os exercícios de teste serão gravados em `ExerciseDatabase/test/matematica/...` para não poluir a base real.
- O `index.json` será atualizado quando adicionar exercícios reais (via `add_exercise.py`) ou ao gerar testes.
- Pode remover as pastas vazias em `matematica/` quando quiser; foram mantidas apenas pela estrutura.

---

Atualizado em: 14-11-2025
