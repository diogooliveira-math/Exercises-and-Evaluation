# ✅ Garantia de Conformidade - Agentes e Scripts v3.1

**Data:** 21 Novembro 2025  
**Objetivo:** Garantir que todos os agentes e scripts seguem o caminho do sistema de preview

---

## 📊 Status de Conformidade

### Scripts Python ✅

| Script | Preview Integrado | Flags Disponíveis | Status |
|--------|------------------|-------------------|--------|
| `add_exercise_with_types.py` | ✅ Sim | N/A | ✅ Conforme |
| `generate_sebentas.py` | ✅ Sim | `--no-preview`, `--auto-approve` | ✅ Conforme |
| `generate_tests.py` | ✅ Sim | `--no-preview`, `--auto-approve` | ✅ Conforme |

### Módulos Core ✅

| Módulo | Funcionalidade | Status |
|--------|---------------|--------|
| `preview_system.py` | Sistema central | ✅ Implementado |
| `PreviewManager` | Gestão de preview | ✅ Funcional |
| Helpers | create_*_preview() | ✅ Disponíveis |

### Documentação ✅

| Documento | Propósito | Status |
|-----------|-----------|--------|
| `PREVIEW_SYSTEM.md` | Guia completo | ✅ Criado |
| `PREVIEW_QUICKSTART.md` | Quick start | ✅ Criado |
| `AGENTS_PREVIEW_GUIDE.md` | Guia para agentes | ✅ Criado |
| `copilot-instructions.md` | Instruções agentes | ✅ Atualizado |
| `readme.md` | Documentação geral | ✅ Atualizado |

### Ficheiros Agent ✅

| Agent | Preview Mencionado | Comandos Corretos | Status |
|-------|-------------------|-------------------|--------|
| Exercise Generator (raiz) | ✅ Sim | ✅ Atualizados | ✅ Conforme |
| Exercise Generator (.github) | ✅ Sim | ✅ Atualizados | ✅ Conforme |
| Sebenta Generator | ✅ Sim | ✅ Atualizados | ✅ Conforme |
| Test Generator | ✅ Sim | ✅ Atualizados | ✅ Conforme |

---

## 🎯 Comportamento Garantido

### 1. Exercise Generator Agent

#### ✅ Comportamento Correto

```python
# Agente executa
python ExerciseDatabase\_tools\add_exercise_with_types.py

# Fluxo garantido:
1. Wizard interactivo ✅
2. Preview automático ✅
3. Abertura VS Code ✅
4. Confirmação [S/N/R] ✅
5. Salvar só se confirmado ✅
```

#### ❌ Comportamento Proibido

- Criar ficheiros `.tex` diretamente
- Salvar sem preview
- Ignorar confirmação

#### 📋 Mensagem do Agente

```
Vou criar um exercício usando add_exercise_with_types.py.

O sistema irá:
1. Solicitar informações (disciplina, módulo, conceito, tipo...)
2. Mostrar PREVIEW automático do conteúdo gerado
3. Abrir ficheiros em VS Code para revisão
4. Pedir sua confirmação antes de adicionar à base

Pode aprovar [S], cancelar [N] ou rever [R].
```

---

### 2. Sebenta Generator Agent

#### ✅ Comportamento Correto

```python
# Agente executa
python SebentasDatabase\_tools\generate_sebentas.py --module P4_funcoes

# Fluxo garantido:
1. Gera LaTeX ✅
2. Preview automático ✅
3. Lista exercícios incluídos ✅
4. Abre VS Code ✅
5. Confirmação ✅
6. Compila PDF só se aprovado ✅
```

#### 🔧 Flags para Casos Especiais

```bash
# CI/CD: totalmente automático
--no-preview --auto-approve

# Rápido sem preview visual
--no-preview

# Preview mas sem confirmação
--auto-approve
```

#### ❌ Comportamento Proibido

- Compilar sem preview (modo padrão)
- Usar flags sem permissão
- Ignorar cancelamento

#### 📋 Mensagem do Agente

```
Vou gerar sebenta do conceito [X] usando generate_sebentas.py.

O sistema irá:
1. Gerar LaTeX com todos exercícios do conceito
2. Mostrar PREVIEW do documento
3. Abrir em VS Code para revisão
4. Pedir confirmação antes de compilar PDF

Se aprovar, o PDF será gerado em:
SebentasDatabase/.../pdfs/sebenta_[conceito].pdf
```

---

### 3. Test Generator Agent

#### ✅ Comportamento Correto

```python
# Agente executa
python SebentasDatabase\_tools\generate_tests.py --config test.json

# Fluxo garantido:
1. Seleciona exercícios ✅
2. Preview automático ✅
3. Lista exercícios com metadados ✅
4. Abre VS Code ✅
5. Confirmação ✅
6. Compila só se aprovado ✅
```

#### 🔄 Múltiplas Versões

```python
# 3 versões → 3 previews separados
python generate_tests.py --versions 3

# Para cada versão:
- Preview individual ✅
- Confirmação separada ✅
- Pode cancelar qualquer uma ✅
```

#### ❌ Comportamento Proibido

- Gerar sem preview por padrão
- Assumir aprovação automática
- Saltar preview em versões

#### 📋 Mensagem do Agente

```
Vou gerar [N] versões de teste.

Para CADA versão, o sistema irá:
1. Selecionar exercícios conforme critérios
2. Mostrar PREVIEW do teste LaTeX
3. Listar exercícios selecionados (ID, dificuldade, tipo)
4. Abrir em VS Code
5. Pedir confirmação individual

Pode aprovar/cancelar cada versão independentemente.
```

---

## 🔐 Regras de Segurança

### Quando Agente PODE usar `--no-preview`

✅ **PERMITIDO:**
- Utilizador solicita explicitamente
- CI/CD confirmado pelo utilizador
- Pipeline automatizada documentada
- Modo batch com aprovação prévia

❌ **PROIBIDO:**
- Por padrão ou conveniência
- Sem permissão explícita
- Para "acelerar" processo
- Assumindo que utilizador não quer ver

### Quando Agente PODE usar `--auto-approve`

✅ **PERMITIDO:**
- Script totalmente automatizado
- CI/CD com aprovação do utilizador
- Geração em massa previamente acordada
- Documentado no comando

❌ **PROIBIDO:**
- Modo interactivo padrão
- Sem confirmação do utilizador
- Para "simplificar" fluxo
- Ignorar workflow de curadoria

---

## 📝 Templates de Mensagens

### Antes de Executar (Padrão)

```
Vou [ação] usando [script].

PREVIEW INCLUÍDO:
→ Terminal mostrará conteúdo
→ VS Code abrirá ficheiros
→ Você poderá rever antes de confirmar

Opções após preview:
[S]im - Confirmar e adicionar
[N]ão - Cancelar operação  
[R]ever - Reabrir VS Code

Prosseguir?
```

### Se Utilizador Pedir Automação

```
Você pediu para [usar flags de automação].

ATENÇÃO: Isto irá:
❌ Desabilitar preview visual
❌ Não pedir confirmação
✅ Adicionar automaticamente à base

Confirmar uso de modo automático?
(Responda "sim" para confirmar)
```

### Após Preview Mostrado

```
Preview gerado!

📄 Ficheiros abertos em VS Code:
- [lista de ficheiros]

Por favor:
1. Reveja o conteúdo em VS Code
2. Verifique se está correto
3. Retorne ao terminal
4. Confirme com [S], cancele com [N], ou reveja com [R]
```

### Se Cancelado

```
Operação cancelada ✓

Os ficheiros de preview estão em:
[caminho temporário]

Pode revisá-los posteriormente.
Nada foi adicionado à base de dados.
```

### Se Confirmado

```
Confirmado! ✓

A processar...
✅ [ação realizada]
✅ Ficheiros criados
✅ Índice atualizado

[Resultado final com paths]
```

---

## 🧪 Casos de Teste

### Teste 1: Criar Exercício

```
INPUT: "Cria um exercício sobre função inversa"

AGENTE DEVE:
1. ✅ Executar add_exercise_with_types.py
2. ✅ Informar que preview aparecerá
3. ✅ Aguardar confirmação do utilizador
4. ✅ Só adicionar se confirmado
5. ❌ NUNCA criar ficheiro diretamente
```

### Teste 2: Gerar Sebenta

```
INPUT: "Gera sebenta do módulo P4"

AGENTE DEVE:
1. ✅ Executar generate_sebentas.py --module P4_funcoes
2. ✅ Informar sobre preview para cada conceito
3. ✅ Explicar que pode cancelar individualmente
4. ✅ Aguardar confirmações
5. ❌ NUNCA usar --auto-approve sem pedir
```

### Teste 3: Teste com 3 Versões

```
INPUT: "Cria 3 versões de teste sobre funções"

AGENTE DEVE:
1. ✅ Executar generate_tests.py --versions 3
2. ✅ Avisar que haverá 3 previews separados
3. ✅ Explicar processo de confirmação individual
4. ✅ Aguardar 3 confirmações
5. ❌ NUNCA assumir aprovação automática
```

### Teste 4: Pedido de Automação

```
INPUT: "Gera sebentas automaticamente sem perguntar"

AGENTE DEVE:
1. ✅ Perguntar confirmação explícita
2. ✅ Explicar consequências (sem preview)
3. ✅ Só prosseguir se utilizador confirmar "sim"
4. ✅ Usar --no-preview --auto-approve
5. ❌ NUNCA assumir automaticamente
```

---

## 📚 Documentação de Referência

### Para Agentes

- 🎯 [AGENTS_PREVIEW_GUIDE.md](.github/agents/AGENTS_PREVIEW_GUIDE.md) - **LEITURA OBRIGATÓRIA**
- 📋 [copilot-instructions.md](.github/copilot-instructions.md) - Instruções detalhadas
- 📚 [PREVIEW_SYSTEM.md](PREVIEW_SYSTEM.md) - Sistema completo

### Para Utilizadores

- 🚀 [PREVIEW_QUICKSTART.md](PREVIEW_QUICKSTART.md) - Começar em 5 minutos
- 🎨 [PREVIEW_VISUAL_GUIDE.md](PREVIEW_VISUAL_GUIDE.md) - Guia visual
- 📖 [readme.md](readme.md) - Visão geral do projeto

---

## ✅ Checklist de Conformidade

Para cada interação com agente:

### Agente
- [ ] Usa comando correto (com preview integrado)
- [ ] Informa utilizador sobre preview
- [ ] Explica opções [S/N/R]
- [ ] Aguarda confirmação
- [ ] Respeita cancelamento
- [ ] Só usa flags com permissão

### Utilizador
- [ ] Vê preview no terminal
- [ ] VS Code abre ficheiros (se disponível)
- [ ] Pode rever conteúdo
- [ ] Confirma ou cancela explicitamente
- [ ] Controlo total sobre o processo

---

## 🎉 Garantias Finais

### Sistema Garante

✅ Nenhum conteúdo adicionado sem aprovação  
✅ Preview visual em todos os fluxos  
✅ Possibilidade de cancelar a qualquer momento  
✅ Ficheiros temporários para revisão  
✅ Tracking de operações canceladas  
✅ Compatibilidade com automação (com permissão)  

### Agentes Garantem

✅ Sempre usar scripts com preview  
✅ Informar utilizador sobre fluxo  
✅ Aguardar confirmação explícita  
✅ Respeitar cancelamento  
✅ Só usar automação com permissão  
✅ Fornecer mensagens claras  

---

**Status:** ✅ CONFORME  
**Versão:** 3.1  
**Data:** 21 Novembro 2025  
**Validado:** Sistema completo operacional
