# 🎯 Guia para Agentes - Sistema de Preview v3.1

**Data:** 21 Novembro 2025  
**Versão:** 3.1  
**Obrigatório para TODOS os agentes**

---

## 🚨 REGRA CRÍTICA

**TODOS** os agentes que geram conteúdo (exercícios, sebentas, testes) DEVEM seguir o fluxo com preview.

---

## 📋 Fluxo Obrigatório

```
1. Gerar Conteúdo
   ↓
2. 🆕 PREVIEW AUTOMÁTICO
   ├─ Terminal mostra preview
   ├─ VS Code abre ficheiros
   └─ Aguarda confirmação: [S]im / [N]ão / [R]ever
   ↓
3. Salvar (SÓ se confirmado)
```

---

## 🎯 Por Tipo de Agente

### Exercise Generator Agent

#### Comando Correto (COM Preview)
```bash
python ExerciseDatabase\_tools\add_exercise_with_types.py
```

**O que acontece:**
1. Wizard interactivo
2. Preview automático do LaTeX + metadados
3. Abre em VS Code
4. Pede confirmação
5. Só adiciona se confirmado

#### ❌ NUNCA Fazer
- Criar ficheiros `.tex` diretamente
- Salvar sem preview
- Usar `--no-preview` sem permissão explícita

#### ✅ Responsabilidades
- Informar utilizador que preview aparecerá
- Explicar que pode cancelar após rever
- Aguardar confirmação antes de prosseguir

---

### Sebenta Generator Agent

#### Comando Correto (COM Preview)
```bash
python SebentasDatabase\_tools\generate_sebentas.py --module P4_funcoes --concept 4-funcao_inversa
```

**O que acontece:**
1. Gera LaTeX da sebenta
2. Preview automático:
   - Mostra estrutura
   - Lista exercícios incluídos
   - Abre em VS Code
3. Pede confirmação
4. Só compila PDF se aprovado

#### Flags Disponíveis
```bash
# Sem preview (só para automação)
--no-preview

# Auto-aprovar (CI/CD)
--auto-approve

# Combinar (comportamento v3.0)
--no-preview --auto-approve
```

#### ❌ NUNCA Fazer
- Usar flags de automação sem permissão
- Compilar PDF sem preview
- Ignorar cancelamento do utilizador

#### ✅ Responsabilidades
- SEMPRE usar comando padrão (com preview)
- Avisar que preview aparecerá
- Explicar que pode cancelar

---

### Test Generator Agent

#### Comando Correto (COM Preview)
```bash
python SebentasDatabase\_tools\generate_tests.py --config test.json
```

**O que acontece:**
1. Seleciona exercícios
2. Preview automático:
   - LaTeX do teste
   - Lista de exercícios com metadados
   - Abre em VS Code
3. Pede confirmação
4. Só compila se aprovado

#### Múltiplas Versões
```bash
python SebentasDatabase\_tools\generate_tests.py --versions 3 --version-labels A,B,C
```

**Comportamento:**
- Preview SEPARADO para cada versão
- Utilizador pode aprovar/cancelar individualmente

#### Flags Disponíveis
```bash
--no-preview       # Desabilitar preview
--auto-approve     # Auto-aprovar tudo
--versions N       # Gerar N versões
--version-labels   # Rótulos (A,B,C...)
```

#### ❌ NUNCA Fazer
- Gerar sem preview por padrão
- Assumir aprovação automática
- Usar flags sem permissão

#### ✅ Responsabilidades
- Avisar sobre preview para cada versão
- Mostrar lista de exercícios selecionados
- Explicar processo de confirmação

---

## 🎨 Interface do Preview

### Terminal

```
╔══════════════════════════════════════════════════════════════════╗
║  📋 PREVIEW: Novo Exercício                                     ║
╚══════════════════════════════════════════════════════════════════╝

📄 exercicio.tex
┌──────────────────────────────────────────────────────────────────┐
│ Conteúdo aqui...                                                 │
└──────────────────────────────────────────────────────────────────┘

🚀 Ficheiros abertos em VS Code

─────────────────────────────────────────────────────────────────────
⚠️  Confirmar e adicionar à base de dados?
─────────────────────────────────────────────────────────────────────

[S]im / [N]ão / [R]ever ficheiros novamente: _
```

### Opções de Resposta

- **S** / **sim** - Confirma e adiciona
- **N** / **não** - Cancela operação
- **R** / **rever** - Reabre VS Code para nova análise

---

## 📚 Quando Usar Cada Modo

### Modo Interactivo (Padrão)
**Usar:** Sempre que possível, especialmente em desenvolvimento

```bash
python script.py
```
- Preview automático
- Confirmação manual
- Controlo total

### Modo Sem Preview
**Usar:** Apenas quando solicitado explicitamente

```bash
python script.py --no-preview
```
- Sem preview visual
- Confirmação texto simples
- Mais rápido

### Modo Auto-Aprovação
**Usar:** CI/CD, automação, pipelines

```bash
python script.py --auto-approve
```
- Sem confirmação
- Adiciona automaticamente
- **Requer permissão explícita**

### Modo Non-Interactive
**Usar:** Scripts totalmente automatizados

```bash
python script.py --no-preview --auto-approve
```
- Comportamento v3.0
- Sem interação
- **Só com permissão**

---

## ✅ Checklist para Agentes

Antes de executar qualquer script:

- [ ] Verificar se é modo interactivo (padrão)
- [ ] Informar utilizador que preview aparecerá
- [ ] Explicar opções: [S]im / [N]ão / [R]ever
- [ ] Aguardar confirmação do utilizador
- [ ] Só prosseguir se confirmado
- [ ] Respeitar cancelamento

Se usar flags de automação:

- [ ] Obter permissão explícita do utilizador
- [ ] Explicar que não haverá preview
- [ ] Confirmar que é intencional
- [ ] Documentar motivo (ex: "para CI/CD")

---

## 📊 Mensagens do Agente

### Antes de Executar

```
Vou criar [tipo de conteúdo] usando [script].

O sistema irá:
1. Gerar o conteúdo
2. Mostrar PREVIEW automático no terminal
3. Abrir ficheiros em VS Code para revisão
4. Pedir a sua confirmação

Pode aprovar [S], cancelar [N] ou rever novamente [R].

Prosseguir?
```

### Após Preview

```
Preview gerado! Os ficheiros foram abertos em VS Code.

Por favor, reveja:
- [ficheiro1.tex] - Conteúdo LaTeX
- [ficheiro2.json] - Metadados

Quando estiver pronto, retorne ao terminal para confirmar.
```

### Se Cancelado

```
Operação cancelada pelo utilizador.

Os ficheiros temporários de preview foram mantidos em:
[caminho]

Pode revisá-los posteriormente se desejar.
```

### Se Confirmado

```
Confirmado! A adicionar à base de dados...

✅ Ficheiro criado: [caminho]
✅ Metadados atualizados
✅ Índice global atualizado

Exercício adicionado com sucesso!
```

---

## 🐛 Troubleshooting

### VS Code não abre

**Agente deve:**
1. Informar que preview apareceu no terminal
2. Explicar que VS Code pode ser aberto manualmente
3. Fornecer caminho dos ficheiros temporários
4. Continuar com confirmação

### Utilizador cancela frequentemente

**Agente deve:**
- Perguntar se deseja ajustar parâmetros
- Oferecer rever configuração
- Sugerir melhorias no conteúdo gerado

### Erro no preview

**Agente deve:**
1. Reportar erro
2. Oferecer gerar novamente
3. Sugerir usar `--no-preview` como fallback (se apropriado)

---

## 📖 Documentação

Para mais detalhes, consultar:

- 📚 [PREVIEW_SYSTEM.md](../PREVIEW_SYSTEM.md) - Documentação completa
- 🚀 [PREVIEW_QUICKSTART.md](../PREVIEW_QUICKSTART.md) - Quick start
- 📋 [.github/copilot-instructions.md](../.github/copilot-instructions.md) - Instruções detalhadas
- 🎨 [PREVIEW_VISUAL_GUIDE.md](../PREVIEW_VISUAL_GUIDE.md) - Guia visual

---

## 🎓 Filosofia

> **"Gere rápido, reveja sempre, confirme conscientemente"**

O preview não atrasa - **previne erros** que demorariam mais a corrigir.

---

## ⚖️ Regras Finais

### SEMPRE Fazer ✅

1. Usar comandos padrão (com preview)
2. Informar utilizador sobre preview
3. Aguardar confirmação explícita
4. Respeitar cancelamento
5. Fornecer mensagens claras

### NUNCA Fazer ❌

1. Salvar ficheiros sem preview
2. Usar flags de automação sem permissão
3. Ignorar confirmação do utilizador
4. Assumir aprovação automática
5. Criar ficheiros diretamente

---

**Versão:** 3.1  
**Obrigatório para:** Todos os agentes  
**Última atualização:** 21 Novembro 2025
