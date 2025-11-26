# 🎨 Sistema de Preview v3.1 - Visualização Rápida

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                                                                      ┃
┃         🎯 SISTEMA DE PREVIEW E CURADORIA v3.1                      ┃
┃                                                                      ┃
┃  "Gere rápido, reveja sempre, confirme conscientemente"             ┃
┃                                                                      ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

---

## 🔄 Fluxo do Sistema

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                       │
│  1. UTILIZADOR INICIA GERAÇÃO                                        │
│     └─> python add_exercise_with_types.py                            │
│                                                                       │
│  2. WIZARD INTERACTIVO                                               │
│     ├─> Escolher disciplina                                          │
│     ├─> Escolher módulo                                              │
│     ├─> Escolher conceito                                            │
│     ├─> Escolher tipo                                                │
│     └─> Preencher dados                                              │
│                                                                       │
│  3. GERAÇÃO DE CONTEÚDO                                              │
│     ├─> Criar LaTeX                                                  │
│     ├─> Gerar metadados                                              │
│     └─> Preparar ficheiros                                           │
│                                                                       │
│  4. 🆕 PREVIEW AUTOMÁTICO                                            │
│     ├─> Mostrar no terminal (colorido)                               │
│     ├─> Criar ficheiros temporários                                  │
│     └─> Abrir VS Code automaticamente                                │
│                                                                       │
│  5. 🆕 REVISÃO DO UTILIZADOR                                         │
│     ├─> Analisa LaTeX em VS Code                                     │
│     ├─> Verifica metadados                                           │
│     └─> Valida qualidade                                             │
│                                                                       │
│  6. 🆕 CONFIRMAÇÃO INTERACTIVA                                       │
│     ├─> [S]im  → Adiciona à base                                     │
│     ├─> [N]ão  → Cancela e descarta                                  │
│     └─> [R]ever → Reabre VS Code                                     │
│                                                                       │
│  7. SALVAR (só se confirmado)                                        │
│     ├─> Adicionar a ExerciseDatabase/                                │
│     ├─> Atualizar index.json                                         │
│     ├─> Atualizar metadata do tipo                                   │
│     └─> Limpar ficheiros temporários                                 │
│                                                                       │
│  8. CONCLUSÃO                                                        │
│     └─> ✅ Exercício adicionado com sucesso!                         │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Antes vs. Depois

### ANTES (v3.0)

```
┌──────────────────────┐
│  Gerar Conteúdo      │
│         ↓            │
│  Confirmar (texto)   │  ← Sem visualização
│         ↓            │
│  Salvar Imediato     │  ← Sem revisão
│         ↓            │
│  ❓ Será que está OK? │
└──────────────────────┘
```

### DEPOIS (v3.1)

```
┌─────────────────────────────┐
│  Gerar Conteúdo             │
│         ↓                   │
│  📋 PREVIEW Visual          │  ← Terminal + VS Code
│         ↓                   │
│  👀 Revisar em VS Code      │  ← Análise completa
│         ↓                   │
│  ✓ Confirmar Explícito     │  ← [S]im/[N]ão/[R]ever
│         ↓                   │
│  💾 Salvar se Aprovado      │  ← Controlo total
│         ↓                   │
│  ✅ Qualidade Garantida     │
└─────────────────────────────┘
```

---

## 🎯 Comandos Principais

### 1. Criar Exercício (COM Preview)

```bash
python ExerciseDatabase\_tools\add_exercise_with_types.py
```

```
┌─────────────────────────────────────────────────────────────┐
│  ╔══════════════════════════════════════════════════════╗   │
│  ║  📋 PREVIEW: Novo Exercício                         ║   │
│  ╚══════════════════════════════════════════════════════╝   │
│                                                              │
│  📄 MAT_P4_4FIN_ANA_001.tex                                  │
│  ┌────────────────────────────────────────────────────┐     │
│  │ % Exercise ID: MAT_P4_4FIN_ANA_001                 │     │
│  │ \exercicio{Determine...                            │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  🚀 Ficheiros abertos em VS Code                            │
│                                                              │
│  [S]im / [N]ão / [R]ever: _                                 │
└─────────────────────────────────────────────────────────────┘
```

---

### 2. Gerar Sebenta (COM Preview)

```bash
python SebentasDatabase\_tools\generate_sebentas.py --module P4_funcoes
```

```
┌─────────────────────────────────────────────────────────────┐
│  📚 Gerando sebenta: matematica/P4_funcoes/4-funcao_inversa │
│                                                              │
│  ╔══════════════════════════════════════════════════════╗   │
│  ║  📋 PREVIEW: Sebenta - Função Inversa              ║   │
│  ╚══════════════════════════════════════════════════════╝   │
│                                                              │
│  📄 sebenta_4-funcao_inversa.tex                            │
│  📊 Total de exercícios: 5                                   │
│  📋 Tipos: Determinação Analítica, Gráfica, Teste...       │
│                                                              │
│  🚀 Ficheiros abertos em VS Code                            │
│                                                              │
│  ⚠️  Confirmar e compilar PDF?                              │
│  [S]im / [N]ão / [R]ever: _                                 │
└─────────────────────────────────────────────────────────────┘
```

---

### 3. Gerar Teste (COM Preview)

```bash
python SebentasDatabase\_tools\generate_tests.py --versions 3
```

```
┌─────────────────────────────────────────────────────────────┐
│  📝 Gerando teste: Versão A                                  │
│                                                              │
│  ╔══════════════════════════════════════════════════════╗   │
│  ║  📋 PREVIEW: Teste - Função Inversa (Versão A)     ║   │
│  ╚══════════════════════════════════════════════════════╝   │
│                                                              │
│  📄 test_20251121_153045_A.tex                              │
│  📄 test_20251121_153045_A_exercises.json                   │
│                                                              │
│  Exercícios selecionados:                                    │
│  1. MAT_P4_4FIN_ANA_001 (Dificuldade: 3)                    │
│  2. MAT_P4_4FIN_GRA_001 (Dificuldade: 2)                    │
│  3. MAT_P4_4FIN_TRH_001 (Dificuldade: 4)                    │
│                                                              │
│  🚀 Ficheiros abertos em VS Code                            │
│                                                              │
│  [S]im / [N]ão / [R]ever: _                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Modos de Operação

### Modo Interactivo (Padrão) - COM Preview

```bash
python script.py
```
→ Preview automático  
→ Abre VS Code  
→ Pede confirmação  
→ Utilizador decide  

### Modo Rápido - SEM Preview

```bash
python script.py --no-preview
```
→ Sem preview visual  
→ Confirmação texto simples  
→ Mais rápido  

### Modo Automático - Auto-aprovação

```bash
python script.py --auto-approve
```
→ Sem confirmação  
→ Adiciona automaticamente  
→ Para CI/CD  

### Modo Non-Interactive - Totalmente Automático

```bash
python script.py --no-preview --auto-approve
```
→ Sem preview  
→ Sem confirmação  
→ Comportamento v3.0  

---

## 📁 Estrutura de Ficheiros

```
Exercises-and-Evaluation/
│
├── ExerciseDatabase/
│   └── _tools/
│       ├── preview_system.py           ← 🆕 SISTEMA CENTRAL
│       └── add_exercise_with_types.py  ← ✅ Atualizado
│
├── SebentasDatabase/
│   └── _tools/
│       ├── generate_sebentas.py        ← ✅ Atualizado
│       └── generate_tests.py           ← ✅ Atualizado
│
├── PREVIEW_SYSTEM.md                    ← 🆕 Documentação completa
├── PREVIEW_QUICKSTART.md                ← 🆕 Quick start
├── IMPLEMENTATION_SUMMARY_v3.1.md       ← 🆕 Resumo
├── VALIDATION_CHECKLIST_v3.1.md         ← 🆕 Checklist
├── readme.md                            ← ✅ Atualizado (v3.1)
│
└── .github/
    └── copilot-instructions.md          ← ✅ Atualizado
```

---

## 🎨 Interface Visual

### Terminal Preview

```
╔══════════════════════════════════════════════════════════════════╗
║  📋 PREVIEW: Novo Exercício: MAT_P4_4FIN_ANA_001               ║
╚══════════════════════════════════════════════════════════════════╝

📄 MAT_P4_4FIN_ANA_001.tex
┌──────────────────────────────────────────────────────────────────┐
│ % Exercise ID: MAT_P4_4FIN_ANA_001                               │
│ % Module: MÓDULO P4 - Funções | Concept: Função Inversa         │
│ % Difficulty: 3/5 (Médio) | Format: development                 │
│ % Tags: funcao_inversa, calculo_analitico, algebra              │
│ % Author: Professor | Date: 2025-11-21                          │
│ % Status: active                                                 │
│                                                                  │
│ \exercicio{Considere a função $f(x) = 2x - 3$.}                │
│                                                                  │
│ \subexercicio{Determine a expressão analítica de $f^{-1}(x)$.} │
│                                                                  │
│ \subexercicio{Calcule $f^{-1}(5)$.}                            │
│                                                                  │
│ ... (mais 10 linhas omitidas) ...                               │
└──────────────────────────────────────────────────────────────────┘

📄 MAT_P4_4FIN_ANA_001_metadata.json
┌──────────────────────────────────────────────────────────────────┐
│ {                                                                │
│   "id": "MAT_P4_4FIN_ANA_001",                                  │
│   "version": "1.0",                                              │
│   "classification": {                                            │
│     "discipline": "matematica",                                  │
│     "module": "P4_funcoes",                                      │
│     "concept": "4-funcao_inversa",                              │
│     "tipo": "determinacao_analitica",                           │
│     "difficulty": 3                                              │
│   }                                                              │
│ }                                                                │
└──────────────────────────────────────────────────────────────────┘

📂 Ficheiros temporários criados em:
   C:\Users\user\AppData\Local\Temp\exercise_preview_20251121_153045

🚀 A abrir ficheiros em VS Code...
✓ Ficheiros abertos para revisão

─────────────────────────────────────────────────────────────────────
⚠️  Confirmar e adicionar à base de dados?
─────────────────────────────────────────────────────────────────────

[S]im / [N]ão / [R]ever ficheiros novamente: _
```

---

## 📊 Estatísticas

### Antes da Confirmação

```
Exercícios no conceito: 4
Tipos disponíveis: 3
Próximo número: 005
```

### Depois de Confirmar

```
════════════════════════════════════════════════════════════════
✅ EXERCÍCIO ADICIONADO COM SUCESSO!
════════════════════════════════════════════════════════════════

📍 Localização: matematica/P4_funcoes/4-funcao_inversa/determinacao_analitica/MAT_P4_4FIN_ANA_001
✅ Ficheiro .tex criado: MAT_P4_4FIN_ANA_001.tex
✅ Metadata do tipo atualizado
✅ Índice atualizado: 43 exercícios no total

════════════════════════════════════════════════════════════════
```

### Estatísticas Finais (Sebentas)

```
════════════════════════════════════════════════════════════════
📊 RESUMO
════════════════════════════════════════════════════════════════
Sebentas geradas: 8
PDFs compilados:  6
Ficheiros limpos: 52
Canceladas:       2  ← 🆕 NOVO
Erros:            0
════════════════════════════════════════════════════════════════
```

---

## 🎓 Aprendizado

### Filosofia Central

```
┌─────────────────────────────────────────────────────────────┐
│                                                              │
│  "Gere rápido, reveja sempre, confirme conscientemente"     │
│                                                              │
│  O preview não atrasa - PREVINE erros que demorariam        │
│  mais tempo a corrigir depois.                              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Benefícios

```
✅ CONTROLO    - Nada entra sem aprovação
✅ QUALIDADE   - Revisão antes de commit
✅ CONFIANÇA   - Sabe o que está a adicionar
✅ EDUCATIVO   - Aprende com exemplos gerados
✅ REVERSÍVEL  - Fácil cancelar a qualquer momento
```

---

## 🔗 Links Úteis

- 📖 [PREVIEW_QUICKSTART.md](./PREVIEW_QUICKSTART.md) - Começar em 5 minutos
- 📚 [PREVIEW_SYSTEM.md](./PREVIEW_SYSTEM.md) - Documentação completa
- ✅ [VALIDATION_CHECKLIST_v3.1.md](./VALIDATION_CHECKLIST_v3.1.md) - Checklist
- 📋 [IMPLEMENTATION_SUMMARY_v3.1.md](./IMPLEMENTATION_SUMMARY_v3.1.md) - Resumo

---

## 🎉 Status

```
███████████████████████████████████ 100%

✅ SISTEMA DE PREVIEW v3.1
   IMPLEMENTADO E VALIDADO

   Ready for Production! 🚀
```

---

**Versão:** 3.1  
**Data:** 21 Novembro 2025  
**Criado por:** Sistema Copilot
