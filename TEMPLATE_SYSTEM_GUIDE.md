# 📝 Template de Exercício - Exemplo Completo

**Sistema:** v3.1.2 - Baseado em Template  
**Ficheiro:** `NOVO_EXERCICIO.tex`  
**Gerado por:** `add_exercise_template.py`

---

## 🎯 Exemplo de Template Gerado

Quando você executa `python ExerciseDatabase/_tools/add_exercise_template.py`, este ficheiro abre automaticamente:

```latex
% ====================================================================
% TEMPLATE DE EXERCÍCIO - Preencha os campos abaixo
% ====================================================================
%
% INSTRUÇÕES:
% 1. Preencha TODOS os campos marcados com [OBRIGATÓRIO]
% 2. Escolha uma das opções listadas abaixo de cada campo
% 3. Mantenha o formato "Campo: valor"
% 4. Salve e feche o ficheiro quando terminar
%
% ====================================================================

% ──────────────────────────────────────────────────────────────────
% CLASSIFICAÇÃO [OBRIGATÓRIO]
% ──────────────────────────────────────────────────────────────────

% Disciplina: matematica
%   ↳ Opções: matematica, teste

% Módulo: A8_modelos_discretos
%   ↳ Opções disponíveis:
%     • A8_modelos_discretos (Modelos Discretos)
%     • A9_funcoes_crescimento (Funções de Crescimento)
%     • A10_funcoes (Funções)
%     • A11_derivadas (Derivadas)
%     • A12_otimizacao (Otimização)
%     • A13_limites (Limites e Continuidade)
%     • A14_integrais (Integrais)
%     • P4_funcoes (MÓDULO P4 - Funções)
%     • P1_modelos_matematicos_para_a_cidadania (Modelos Matemáticos)

% Conceito: 1-sistemas_numericos
%   ↳ Depende do módulo escolhido
%   ↳ Exemplos: 1-sistemas_numericos, 2-numeros_figurados, 0-revisoes

% Tipo: determinacao_valores
%   ↳ Depende do conceito
%   ↳ Exemplos: determinacao_valores, introducao_basica, aplicacao_pratica

% ──────────────────────────────────────────────────────────────────
% METADADOS [OBRIGATÓRIO]
% ──────────────────────────────────────────────────────────────────

% Formato: desenvolvimento
%   ↳ Opções:
%     • desenvolvimento (Resposta aberta com resolução completa)
%     • escolha_multipla (4 opções com uma correta)
%     • verdadeiro_falso (Afirmações para classificar)
%     • resposta_curta (Resposta breve ou valor numérico)

% Dificuldade: 2
%   ↳ Opções:
%     • 1 (Muito Fácil - Aplicação direta de conceitos básicos)
%     • 2 (Fácil - Exercícios de consolidação simples)
%     • 3 (Médio - Requer compreensão sólida dos conceitos)
%     • 4 (Difícil - Problemas complexos, múltiplos conceitos)
%     • 5 (Muito Difícil - Desafios avançados, pensamento crítico)

% Autor: Professor
%   ↳ Seu nome ou "Professor" (padrão)

% ──────────────────────────────────────────────────────────────────
% TAGS [OPCIONAL]
% ──────────────────────────────────────────────────────────────────

% Tags: sistemas_numericos, binario, decimal
%   ↳ Separe por vírgula
%   ↳ Exemplos: funcoes, derivadas, limites, aplicacao, teoria

% ──────────────────────────────────────────────────────────────────
% SOLUÇÃO [OPCIONAL]
% ──────────────────────────────────────────────────────────────────

% TemSolucao: nao
%   ↳ Opções: sim, nao

% ====================================================================
% CONTEÚDO DO EXERCÍCIO [OBRIGATÓRIO]
% ====================================================================
% 
% COMANDOS LATEX DISPONÍVEIS:
% ───────────────────────────────────────────────────────────────────
% \exercicio{...}           → Enunciado principal
% \subexercicio{...}        → Alínea (a, b, c...)
% \opcao{...}               → Opção de escolha múltipla
% 
% EXEMPLOS POR FORMATO:
% ───────────────────────────────────────────────────────────────────
% 
% [DESENVOLVIMENTO]
% \exercicio{Calcule a derivada de $f(x) = x^2 + 3x$.}
% 
% [COM ALÍNEAS]
% \exercicio{Converta para binário:}
% \subexercicio{10}
% \subexercicio{25}
% 
% [ESCOLHA MÚLTIPLA]
% \exercicio{Qual é o valor de $2^3$?}
% \opcao{6}
% \opcao{8}  % ← Correta
% \opcao{9}
% \opcao{12}
% 
% [RESPOSTA CURTA]
% \exercicio{Qual é a raiz quadrada de 144?}
% 
% ====================================================================

\exercicio{
    % ← ESCREVA O ENUNCIADO AQUI
    % Pode usar LaTeX: $x^2$, \frac{1}{2}, \sqrt{x}, etc.
}

% ← SE TIVER ALÍNEAS, ADICIONE AQUI:
% \subexercicio{Primeira alínea}
% \subexercicio{Segunda alínea}

% ====================================================================
% SOLUÇÃO (se TemSolucao: sim)
% ====================================================================
% 
% Remova os % abaixo para adicionar a solução:
%
% \solucao{
%     % ← ESCREVA A SOLUÇÃO AQUI
%     % Pode usar comandos LaTeX normalmente
% }

% ====================================================================
% FIM DO TEMPLATE
% ====================================================================
```

---

## ✏️ Exemplo de Template Preenchido

```latex
% ====================================================================
% TEMPLATE DE EXERCÍCIO - Preencha os campos abaixo
% ====================================================================

% ──────────────────────────────────────────────────────────────────
% CLASSIFICAÇÃO [OBRIGATÓRIO]
% ──────────────────────────────────────────────────────────────────

% Disciplina: matematica
% Módulo: A8_modelos_discretos
% Conceito: 1-sistemas_numericos
% Tipo: determinacao_valores

% ──────────────────────────────────────────────────────────────────
% METADADOS [OBRIGATÓRIO]
% ──────────────────────────────────────────────────────────────────

% Formato: desenvolvimento
% Dificuldade: 3
% Autor: Prof. João Silva

% ──────────────────────────────────────────────────────────────────
% TAGS [OPCIONAL]
% ──────────────────────────────────────────────────────────────────

% Tags: binario, conversao, sistemas_numericos, pratica

% ──────────────────────────────────────────────────────────────────
% SOLUÇÃO [OPCIONAL]
% ──────────────────────────────────────────────────────────────────

% TemSolucao: sim

% ====================================================================
% CONTEÚDO DO EXERCÍCIO [OBRIGATÓRIO]
% ====================================================================

\exercicio{
    Converta os seguintes números decimais para o sistema de numeração binária:
}

\subexercicio{42}
\subexercicio{127}
\subexercicio{255}

% ====================================================================
% SOLUÇÃO (se TemSolucao: sim)
% ====================================================================

\solucao{
    a) $42_{10} = 101010_2$
    
    b) $127_{10} = 1111111_2$
    
    c) $255_{10} = 11111111_2$
}

% ====================================================================
% FIM DO TEMPLATE
% ====================================================================
```

---

## 🎯 Vantagens do Sistema de Template

### 1. **Contexto Visual Completo**
- ✅ Vê todas as opções disponíveis
- ✅ Exemplos diretos no local de uso
- ✅ Sem navegar menus

### 2. **Edição Natural**
- ✅ Editor LaTeX com syntax highlighting
- ✅ Autocomplete do VS Code funciona
- ✅ Pode copiar/colar de outros exercícios

### 3. **Validação Inteligente**
- ✅ Verifica campos obrigatórios
- ✅ Valida valores (dificuldade 1-5, formato válido)
- ✅ Mostra erros específicos
- ✅ Permite reeditar se houver erro

### 4. **Workflow Rápido**
```
1. Executa script → Template abre
2. Preenche campos → Vê opções no próprio template
3. Escreve enunciado → Com exemplos à vista
4. Salva + Enter → Validação automática
5. Confirma → Incorporado na base
```

Tempo total: **~2 minutos** (vs ~5 min no wizard)

---

## 📋 Comandos LaTeX Disponíveis

### Enunciado Principal
```latex
\exercicio{Texto do enunciado}
```

### Alíneas/Subexercícios
```latex
\subexercicio{Texto da alínea a)}
\subexercicio{Texto da alínea b)}
```

### Escolha Múltipla
```latex
\exercicio{Pergunta?}
\opcao{Opção incorreta}
\opcao{Opção correta}  % ← Marque a correta com comentário
\opcao{Opção incorreta}
\opcao{Opção incorreta}
```

### Solução
```latex
\solucao{
    Resolução completa aqui
}
```

### Matemática LaTeX
```latex
$x^2$                    → x²
\frac{1}{2}              → ½
\sqrt{x}                 → √x
\int_0^1 x \, dx         → integral
f(x) = 2x + 3            → função
```

---

## 🔧 Validações Implementadas

### Campos Obrigatórios
- ✅ Disciplina
- ✅ Módulo
- ✅ Conceito
- ✅ Tipo
- ✅ Formato
- ✅ Dificuldade
- ✅ Autor
- ✅ Conteúdo do exercício (comando `\exercicio{}`)

### Validações de Valor
- ✅ Dificuldade: 1-5
- ✅ Formato: desenvolvimento, escolha_multipla, verdadeiro_falso, resposta_curta
- ✅ TemSolucao: sim ou nao
- ✅ Se TemSolucao=sim, verifica presença de `\solucao{}`

### Validações de Conteúdo
- ✅ `\exercicio{}` não pode estar vazio
- ✅ Remove comentários antes de validar
- ✅ Deteta conteúdo real vs placeholder

---

## ❌ Exemplos de Erros

### Erro: Campo Obrigatório Ausente
```
❌ ERROS DE VALIDAÇÃO ENCONTRADOS

  1. Campo obrigatório ausente: Autor
  
Deseja reeditar o template? (s/n):
```

### Erro: Dificuldade Inválida
```
❌ ERROS DE VALIDAÇÃO ENCONTRADOS

  1. Dificuldade deve estar entre 1 e 5
  
Deseja reeditar o template? (s/n):
```

### Erro: Enunciado Vazio
```
❌ ERROS DE VALIDAÇÃO ENCONTRADOS

  1. Enunciado do exercício está vazio
  
Deseja reeditar o template? (s/n):
```

### Erro: Solução Ausente
```
❌ ERROS DE VALIDAÇÃO ENCONTRADOS

  1. TemSolucao=sim mas comando \solucao{} não encontrado
  
Deseja reeditar o template? (s/n):
```

---

## 🚀 Como Usar

### 1. Executar Script
```bash
python ExerciseDatabase/_tools/add_exercise_template.py
```

### 2. Template Abre Automaticamente
- Abre no VS Code ou editor padrão
- Template pré-preenchido com valores default

### 3. Editar Template
- Vê todas as opções disponíveis
- Consulta exemplos diretamente
- Preenche campos
- Escreve enunciado LaTeX

### 4. Salvar e Confirmar
- Salva ficheiro (Ctrl+S)
- Pressiona Enter no terminal
- Sistema valida automaticamente

### 5. Corrigir Erros (se houver)
- Sistema mostra erros específicos
- Pergunta se quer reeditar
- Reabre automaticamente
- Repete validação

### 6. Incorporar na Base
- Se válido, mostra resumo
- Pergunta confirmação
- Adiciona à base de dados

---

## 📊 Comparação com Wizard

| Aspecto | Wizard (Antigo) | Template (Novo) |
|---------|----------------|-----------------|
| **Interação** | 15+ perguntas sequenciais | 1 ficheiro editável |
| **Visualização** | Terminal (limitado) | Editor LaTeX completo |
| **Ajuda** | Tem que lembrar opções | Opções visíveis no template |
| **Exemplos** | Separados | Integrados no template |
| **Correção** | Recomeçar wizard | Editar e revalidar |
| **Flexibilidade** | Opções limitadas | LaTeX livre |
| **Velocidade** | ~5 minutos | ~2 minutos |
| **Curva de aprendizagem** | Baixa (guiado) | Média (mais liberdade) |
| **Para iniciantes** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Para experientes** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 🎯 Próximas Melhorias

1. **Templates Especializados**
   - Template por tipo de exercício
   - Template por módulo
   - Template por formato

2. **Integração Completa**
   - Conectar validação → salvamento real
   - Gerar ID automático
   - Atualizar índices

3. **Modo CLI**
   - `--template` (novo sistema)
   - `--wizard` (sistema antigo)
   - `--tipo determinacao_valores` (pré-preencher)

4. **Snippets VS Code**
   - Snippets para `\exercicio{}`
   - Snippets para `\subexercicio{}`
   - Snippets para matemática comum

---

**Versão:** 3.1.2  
**Status:** ✅ Funcional (validação completa)  
**Pendente:** Integração com salvamento na base de dados
