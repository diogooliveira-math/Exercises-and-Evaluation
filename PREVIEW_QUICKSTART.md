# 🚀 Quick Start - Sistema de Preview

**5 minutos para começar a usar o sistema de preview e curadoria**

---

## 🎯 O Que É?

Sistema que permite **revisar antes de adicionar** qualquer conteúdo à base de dados:
- ✅ Ver preview do conteúdo em VS Code
- ✅ Confirmar ou cancelar
- ✅ Controlo total sobre o que entra na base

---

## 📦 Setup Inicial

### 1. Verificar Instalação

```bash
# Verificar se preview_system.py existe
dir ExerciseDatabase\_tools\preview_system.py

# Se não existir, copiar da documentação
```

### 2. VS Code (Opcional)

Para abertura automática de ficheiros:
```bash
# Testar comando
code --version

# Se não funcionar, adicionar ao PATH
```

---

## 🎬 Uso Básico

### Criar Exercício

```bash
python ExerciseDatabase\_tools\add_exercise_with_types.py
```

**Novo comportamento:**
1. Preencher dados (como antes)
2. **PREVIEW aparece automaticamente** ← NOVO
3. Ficheiros abrem em VS Code ← NOVO
4. Confirmar: `[S]im` / `[N]ão` / `[R]ever` ← NOVO
5. Só adiciona se confirmar ← NOVO

### Gerar Sebenta

```bash
# COM preview (padrão)
python SebentasDatabase\_tools\generate_sebentas.py --module P4_funcoes

# SEM preview (modo antigo)
python SebentasDatabase\_tools\generate_sebentas.py --module P4_funcoes --no-preview
```

> **Atenção importante — destino das sebentas geradas**
>
> - As sebentas (ficheiros `.tex` e `.pdf`) geradas por este sistema são guardadas em `SebentasDatabase/`.
> - Evite executar `ExerciseDatabase/_tools/generate_sebentas.py` — use `SebentasDatabase/_tools/generate_sebentas.py` para saídas oficiais.
> - O script legacy requer `ALLOW_EXERCISE_DB_SEBENTA=1` ou `--allow-exercise-output` para ser executado (proteção intencional).


### Gerar Teste

```bash
# COM preview
python SebentasDatabase\_tools\generate_tests.py --config test.json

# SEM preview
python SebentasDatabase\_tools\generate_tests.py --config test.json --no-preview
```

---

## 🎨 Interface

### Preview no Terminal

```
╔══════════════════════════════════════════════════════════════════╗
║  📋 PREVIEW: Novo Exercício: MAT_P4_4FIN_ANA_001               ║
╚══════════════════════════════════════════════════════════════════╝

📄 MAT_P4_4FIN_ANA_001.tex
┌──────────────────────────────────────────────────────────────────┐
│ % Exercise ID: MAT_P4_4FIN_ANA_001                               │
│ % Difficulty: 3/5 (Médio)                                        │
│ \exercicio{Determine a expressão analítica...                   │
│ ...                                                              │
└──────────────────────────────────────────────────────────────────┘

📄 MAT_P4_4FIN_ANA_001_metadata.json
┌──────────────────────────────────────────────────────────────────┐
│ {                                                                │
│   "id": "MAT_P4_4FIN_ANA_001",                                  │
│   "difficulty": 3,                                               │
│   ...                                                            │
└──────────────────────────────────────────────────────────────────┘

🚀 A abrir ficheiros em VS Code...
✓ Ficheiros abertos para revisão

─────────────────────────────────────────────────────────────────────
⚠️  Confirmar e adicionar à base de dados?
─────────────────────────────────────────────────────────────────────

[S]im / [N]ão / [R]ever ficheiros novamente: _
```

### Opções de Resposta

- **`S`** - Confirma e adiciona à base
- **`N`** - Cancela e descarta tudo
- **`R`** - Reabre ficheiros para rever novamente

---

## ⚙️ Flags Úteis

### Para Scripts de Geração

```bash
# Sem preview (modo rápido)
--no-preview

# Auto-aprovar (para CI/automação)
--auto-approve

# Combinar (gera sem interação)
--no-preview --auto-approve
```

### Exemplos

```bash
# Sebenta sem confirmação (automação)
python SebentasDatabase\_tools\generate_sebentas.py --module P4 --auto-approve

# Teste sem preview (modo antigo)
python SebentasDatabase\_tools\generate_tests.py --config test.json --no-preview

# Normal (com preview e confirmação)
python SebentasDatabase\_tools\generate_tests.py --config test.json
```

---

## 🔍 O Que Revisar?

### Em Exercícios

✅ LaTeX está correto  
✅ Metadados completos  
✅ Dificuldade apropriada  
✅ Tags relevantes  
✅ Tipo correto  
✅ Sem erros de digitação  

### Em Sebentas

✅ Todos exercícios incluídos  
✅ Ordem lógica  
✅ Formatação consistente  
✅ Headers corretos  
✅ Sem exercícios duplicados  

### Em Testes

✅ Distribuição balanceada  
✅ Dificuldade apropriada  
✅ Tempo estimado razoável  
✅ Cobertura de conceitos  
✅ Versões diferentes (se aplicável)  

---

## 🐛 Troubleshooting Rápido

### VS Code não abre

```python
# Solução 1: Desabilitar abertura automática
preview = PreviewManager(auto_open=False)

# Solução 2: Usar --no-preview
python script.py --no-preview
```

### Preview system not found

```bash
# Verificar localização
ExerciseDatabase/
  _tools/
    preview_system.py  ← DEVE EXISTIR

# Se não, copiar de outro ambiente ou reinstalar
```

### Ficheiros não limpam

**Causa:** VS Code ainda tem ficheiros abertos

**Solução:** Fechar todos os ficheiros temporários antes de confirmar

---

## 💡 Dicas Pro

### 1. Revisar Rapidamente

```
[R]ever → Analise → Feche VS Code → [S]im
```

### 2. Cancelar Sem Culpa

Melhor cancelar e refazer do que adicionar conteúdo errado

### 3. Usar Preview como Aprendizado

Ver exemplos gerados ajuda a entender padrões

### 4. Combinar com Git

```bash
# Gerar com preview
python add_exercise.py
[S]im

# Testar localmente
git status
git diff

# Se OK, commit
git add .
git commit -m "feat: adicionar exercício X"
```

---

## 📚 Próximos Passos

1. ✅ Ler este quick start
2. 📖 Ver [PREVIEW_SYSTEM.md](PREVIEW_SYSTEM.md) para detalhes
3. 🎯 Experimentar criar um exercício
4. 🔧 Customizar flags conforme necessário
5. 🚀 Integrar no workflow diário

---

## 📊 Diferenças vs. Versão Antiga

| Aspecto | Antes (v3.0) | Agora (v3.1) |
|---------|--------------|--------------|
| Confirmação | No final do wizard | Com preview visual |
| Revisão | Terminal apenas | VS Code + terminal |
| Cancelar | Antes de salvar | Depois de ver conteúdo |
| Transparência | Baixa | Alta (vê tudo) |
| Controlo | Médio | Total |

---

## 🎯 Filosofia

> **"Gere rápido, reveja sempre, confirme conscientemente"**

O preview não atrasa o trabalho - **previne erros** que demorariam mais a corrigir depois.

---

**Tempo de leitura:** 5 min  
**Tempo para dominar:** 15 min  
**Benefício:** ∞ (conteúdo de qualidade garantida)

---

Para mais detalhes, consulte [PREVIEW_SYSTEM.md](PREVIEW_SYSTEM.md)
