\begin{enumerate}
    \item $(11)_{3}$
    \vspace{1cm}
    \item $(13)_{4}$
    \vspace{1cm}
    \item $(39)_{10}$
    \vspace{1cm}
    \item $(110)_{3}$
    \vspace{1cm}
    \item $(1A)_{16}$
    \vspace{1cm}
    \item $(A1)_{16}$
    \vspace{1cm}
\end{enumerate}# ⚡ SISTEMA MÍNIMO - Guia Rápido

**Criação ultra-rápida de exercícios: 3 campos + Enter**

---

## 🎯 Tempo de Criação

| Método | Campos | Tempo | Exercícios/Hora |
|--------|--------|-------|-----------------|
| **Antigo (Template Completo)** | 13+ | ~5 min | 12 |
| **⚡ NOVO (Mínimo)** | 3 | ~30-60 seg | **60-120** |

**Ganho: 5-10x mais rápido!** 🚀

---

## 📝 Como Usar

### Via VS Code (Recomendado)

1. **Abrir Tasks:** `Ctrl+Shift+B` (ou `Ctrl+Shift+P` → "Tasks: Run Task")
2. **Escolher:** `⚡ Novo Exercício (Mínimo - RECOMENDADO)`
3. **Preencher 3 campos:**
   - Módulo (ex: `P4_funcoes`)
   - Conceito (ex: `4-funcao_inversa`)
   - Enunciado (ex: `Determine $f^{-1}(x)$ se $f(x) = 2x + 3$.`)
4. **Salvar e fechar**
5. **Pressionar Enter** no terminal
6. **Confirmar** incorporação

**Tempo total: ~30-60 segundos** ⚡

---

## 🤖 O Que é Inferido Automaticamente?

### ✅ Sempre Inferido

| Campo | Como Funciona | Exemplo |
|-------|---------------|---------|
| **Disciplina** | Do módulo escolhido | `matematica` |
| **Formato** | Análise do enunciado | `desenvolvimento` |
| **Autor** | Padrão | `Professor` |

### 🧠 Inferência Inteligente

| Campo | Palavras-Chave | Exemplo |
|-------|----------------|---------|
| **Tipo** | "determine" → `determinacao_analitica` | Auto-detectado |
| | "gráfico" → `determinacao_grafica` | |
| | "prove" → `demonstracao` | |
| **Dificuldade** | "básico" → 1, "complexo" → 3 | Padrão: 2 |
| **Tags** | Do conceito + enunciado | `inversa`, `calculo` |

---

## 📋 Template Mínimo

```latex
% Módulo: P4_funcoes
% Conceito: 4-funcao_inversa

% ─── OPCIONAIS (deixe vazio para auto) ───
% Tipo: 
% Dificuldade: 
% Tags: 

\exercicio{
    Determine a função inversa de $f(x) = 2x + 3$.
}
```

**Sistema preenche:**
- ✅ Tipo: `determinacao_analitica` (palavra "determine")
- ✅ Dificuldade: `2` (padrão)
- ✅ Tags: `inversa, funcao_linear, calculo`

---

## 🎨 Exemplos de Inferência

### Exemplo 1: Determinação Analítica

**Input:**
```latex
% Módulo: P4_funcoes
% Conceito: 4-funcao_inversa

\exercicio{
    Calcule a expressão analítica de $f^{-1}(x)$ para $f(x) = 3x - 5$.
}
```

**Inferido:**
- Tipo: `determinacao_analitica` ✅ ("calcule", "expressão")
- Dificuldade: `2` (Fácil)
- Tags: `inversa, funcao_linear, expressao_analitica, calculo`

---

### Exemplo 2: Gráfico

**Input:**
```latex
% Módulo: P4_funcoes
% Conceito: 4-funcao_inversa

\exercicio{
    Represente graficamente $f^{-1}(x)$ dado o gráfico de $f(x) = x^2$.
}
```

**Inferido:**
- Tipo: `determinacao_grafica` ✅ ("represente graficamente")
- Dificuldade: `2`
- Tags: `inversa, grafico, funcao_quadratica`

---

### Exemplo 3: Demonstração (Difícil)

**Input:**
```latex
% Módulo: P4_funcoes
% Conceito: 4-funcao_inversa

\exercicio{
    Prove que se $f$ é estritamente crescente, então $f^{-1}$ também é.
}
```

**Inferido:**
- Tipo: `demonstracao` ✅ ("prove")
- Dificuldade: `4` ✅ (Difícil - palavra "prove")
- Tags: `inversa, demonstracao, propriedades`

---

## 🔧 Sobrescrever Inferência

Se não gostar da inferência, **basta preencher manualmente:**

```latex
% Módulo: P4_funcoes
% Conceito: 4-funcao_inversa
% Tipo: aplicacao_pratica        ← Forçar tipo
% Dificuldade: 3                  ← Forçar dificuldade
% Tags: inversa, contexto_real    ← Forçar tags

\exercicio{...}
```

Sistema usa valores manuais, **não infere**.

---

## 📊 Estatísticas de Inferência

Ao finalizar, sistema mostra o que foi inferido:

```
✓ EXERCÍCIO VALIDADO COM SUCESSO!

📋 Resumo:
  Módulo: P4_funcoes
  Conceito: 4-funcao_inversa
  Disciplina: matematica (inferida)
  Tipo: determinacao_analitica (inferido)
  Dificuldade: 2/5 (inferida)
  Formato: desenvolvimento
  Tags: inversa, funcao_linear, calculo (inferidas)

💡 Campos inferidos automaticamente marcados em azul
```

---

## 🚀 Workflow Completo (30 segundos)

1. **`Ctrl+Shift+B`** → Task abre
2. **Preencher:**
   ```latex
   % Módulo: P4_funcoes
   % Conceito: 4-funcao_inversa
   
   \exercicio{Determine $f^{-1}(x)$ se $f(x) = 2x+3$.}
   ```
3. **`Ctrl+S`** → Salvar
4. **Fechar ficheiro**
5. **`Enter`** no terminal
6. **`s`** → Confirmar
7. **✅ Pronto!**

---

## 💡 Dicas de Produtividade

### 1. Criar Múltiplos Exercícios Rápido

**Contexto comum:**
- Módulo: `P4_funcoes`
- Conceito: `4-funcao_inversa`

**Exercícios:**
```latex
\exercicio{Determine $f^{-1}$ para $f(x) = 2x+3$.}
\exercicio{Determine $f^{-1}$ para $f(x) = 3x-5$.}
\exercicio{Determine $f^{-1}$ para $f(x) = -x+7$.}
```

**3 exercícios em ~2 minutos!** (vs 15 minutos antes)

---

### 2. Palavras-Chave Mágicas

Use estas palavras para controlar inferência:

| Palavra | Tipo Inferido | Exemplo |
|---------|---------------|---------|
| `determine` | determinacao_analitica | Determine $f^{-1}$ |
| `gráfico` | determinacao_grafica | Represente graficamente |
| `prove` | demonstracao | Prove que... |
| `calcule` | calculo_direto | Calcule o valor |
| `problema` | aplicacao_pratica | Um tanque... |

---

### 3. Ajustar Dificuldade Rapidamente

**Fácil:**
```latex
\exercicio{Calcule diretamente $f^{-1}$ para $f(x) = x+2$.}
```
→ Dificuldade: 1 (palavra "diretamente")

**Difícil:**
```latex
\exercicio{Prove que $f \circ f^{-1} = id$ para toda função bijetiva.}
```
→ Dificuldade: 4 (palavra "prove")

---

## ⚙️ Configuração Avançada

### Editar Regras de Inferência

Ficheiro: `ExerciseDatabase/_tools/add_exercise_minimal.py`

**Adicionar novo tipo:**
```python
TYPE_KEYWORDS = {
    'meu_novo_tipo': ['palavra1', 'palavra2', 'palavra3']
}
```

**Ajustar dificuldade:**
```python
DIFFICULTY_KEYWORDS = {
    1: ['básico', 'simples', 'direto'],
    5: ['muito difícil', 'prove', 'generalize']
}
```

---

## 🆚 Comparação com Template Completo

| | Mínimo ⚡ | Completo 📝 |
|---|---|---|
| **Campos obrigatórios** | 3 | 13+ |
| **Tempo** | 30-60 seg | 3-5 min |
| **Inferência** | ✅ Sim | ❌ Não |
| **Controle** | Médio | Total |
| **Uso** | 95% dos casos | Casos especiais |

**Recomendação:** Use Mínimo para produção rápida, Completo para casos especiais.

---

## 🐛 Troubleshooting

### "Módulo não encontrado"
- Verifique nome exato em `modules_config.yaml`
- Formato: `P4_funcoes` (com underscore)

### "Inferência errada"
- Sobrescreva manualmente preenchendo campo
- Ou ajuste palavras-chave em `add_exercise_minimal.py`

### "Quero Template Completo"
- Use task: `📝 Novo Exercício (Template Completo)`
- Ou: `python ExerciseDatabase/_tools/add_exercise_template.py`

---

## 📚 Recursos

- **Script:** `ExerciseDatabase/_tools/add_exercise_minimal.py`
- **Task VS Code:** `⚡ Novo Exercício (Mínimo - RECOMENDADO)`
- **Atalho:** `Ctrl+Shift+B`
- **Configuração:** `modules_config.yaml`

---

## ✅ Checklist Rápido

- [ ] `Ctrl+Shift+B`
- [ ] Preencher Módulo
- [ ] Preencher Conceito
- [ ] Escrever enunciado em `\exercicio{...}`
- [ ] Salvar (`Ctrl+S`)
- [ ] Fechar ficheiro
- [ ] `Enter` no terminal
- [ ] Confirmar com `s`
- [ ] 🎉 Exercício criado!

**Tempo total: ~30 segundos**

---

**Versão:** 1.0  
**Data:** 2025-11-21  
**Sistema:** Inferência Inteligente v1.0
