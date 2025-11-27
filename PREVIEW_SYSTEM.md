# 📋 Sistema de Preview e Curadoria - Guia Completo

**Versão:** 3.1  
**Data:** 2025-11-21  
**Objetivo:** Implementar ciclo de geração iniciado por agentes mas confirmado e curado pelo utilizador

---

## 🎯 Visão Geral

O Sistema de Preview e Curadoria transforma o workflow de geração de conteúdo, permitindo que:

1. **Agentes/Scripts geram** conteúdo (exercícios, sebentas, testes)
2. **Sistema abre automaticamente** em VS Code para revisão
3. **Utilizador revê e valida** o conteúdo
4. **Confirmação explícita** antes de adicionar à base de dados

### Vantagens

✅ **Controlo total** - Nada é adicionado sem aprovação  
✅ **Qualidade garantida** - Revisão antes de commit  
✅ **Transparência** - Visualização clara do que será criado  
✅ **Reversível** - Fácil cancelar antes de salvar  
✅ **Educativo** - Permite aprender com exemplos gerados  

---

## 🏗️ Arquitectura

### Componente Central: `preview_system.py`

Localização: `ExerciseDatabase/_tools/preview_system.py`

```python
from preview_system import PreviewManager

preview = PreviewManager(auto_open=True)
content = {
    "exercise.tex": latex_content,
    "metadata.json": json_metadata
}

if preview.show_and_confirm(content, "Novo Exercício"):
    # Utilizador confirmou - prosseguir
    save_to_database()
else:
    # Cancelado
    cleanup()
```

### Integração nos Scripts

Todos os scripts principais foram atualizados:

1. **`add_exercise_with_types.py`** - Adição de exercícios
2. **`generate_sebentas.py`** - Geração de sebentas
3. **`generate_tests.py`** - Geração de testes

---

## 📖 Como Usar

### 1. Criar Exercício (com Preview)

```bash
python ExerciseDatabase\_tools\add_exercise_with_types.py
```

**Fluxo:**
1. Wizard interactivo para dados do exercício
2. **PREVIEW** - Sistema mostra:
   - Conteúdo LaTeX no terminal
   - Ficheiros temporários abertos em VS Code
   - Metadados formatados
3. **Confirmação:**
   - `[S]im` - Adicionar à base de dados
   - `[N]ão` - Cancelar operação
   - `[R]ever` - Reabrir ficheiros para nova análise
4. Se confirmado: ficheiros salvos em `ExerciseDatabase/`

**Exemplo de Output:**
```
╔══════════════════════════════════════════════════════════════════╗
║  📋 PREVIEW: Novo Exercício: MAT_P4FUNCOE_4FIN_ANA_001         ║
╚══════════════════════════════════════════════════════════════════╝

📄 MAT_P4FUNCOE_4FIN_ANA_001.tex
┌──────────────────────────────────────────────────────────────────┐
│ % Exercise ID: MAT_P4FUNCOE_4FIN_ANA_001                         │
│ % Module: MÓDULO P4 - Funções | Concept: Função Inversa         │
│ % Difficulty: 3/5 (Médio) | Format: development                 │
│ ...                                                              │
└──────────────────────────────────────────────────────────────────┘

🚀 A abrir ficheiros em VS Code...
✓ Ficheiros abertos para revisão

─────────────────────────────────────────────────────────────────────
⚠️  Confirmar e adicionar à base de dados?
─────────────────────────────────────────────────────────────────────

[S]im / [N]ão / [R]ever ficheiros novamente: 
```

---

### 2. Gerar Sebenta (com Preview)

```bash
# Com preview (padrão)
python SebentasDatabase\_tools\generate_sebentas.py --module P4_funcoes --concept 4-funcao_inversa

# Sem preview (modo antigo)
python SebentasDatabase\_tools\generate_sebentas.py --module P4_funcoes --no-preview

# Auto-aprovar (CI/automação)
python SebentasDatabase\_tools\generate_sebentas.py --module P4_funcoes --auto-approve
```

**Novas Opções:**
- `--no-preview` - Desabilita pré-visualização
- `--auto-approve` - Aprova automaticamente (útil para CI/CD)

**Fluxo com Preview:**
1. Script gera conteúdo LaTeX da sebenta
2. **PREVIEW** - Mostra:
   - Estrutura do documento
   - Exercícios incluídos
   - Metadados (conceito, módulo, total de exercícios)
3. Abre em VS Code automaticamente
4. Aguarda confirmação
5. Se confirmado: compila PDF e limpa temporários

---

### 3. Gerar Teste (com Preview)

```bash
# Com preview (padrão)
python SebentasDatabase\_tools\generate_tests.py --config default_test_config.json --module P4_funcoes

# Sem preview
python SebentasDatabase\_tools\generate_tests.py --config test.json --no-preview

# Múltiplas versões com preview
python SebentasDatabase\_tools\generate_tests.py --versions 3 --version-labels A,B,C
```

**Fluxo com Preview:**
1. Seleciona exercícios segundo configuração
2. **PREVIEW** - Mostra:
   - LaTeX do teste completo
   - Lista de exercícios selecionados com metadados
   - Configuração usada
3. Abre em VS Code
4. Confirmação para cada versão (se múltiplas)
5. Compila PDFs aprovados

---

## 🎨 Funcionalidades do Preview

### 1. Preview em Terminal

Mostra as primeiras 20 linhas de cada ficheiro com formatação colorida:

```
📄 exercise.tex
┌──────────────────────────────────────────────────────────────────┐
│ \exercicio{Determine a expressão analítica de $f^{-1}(x)$...    │
│ ...                                                              │
└──────────────────────────────────────────────────────────────────┘
```

### 2. Abertura em VS Code

Todos os ficheiros relevantes são abertos automaticamente:
- `.tex` - Conteúdo LaTeX
- `.json` - Metadados formatados
- Informações adicionais

### 3. Ficheiros Temporários

Criados em: `%TEMP%\exercise_preview_TIMESTAMP\`

Conteúdo:
- `README_PREVIEW.txt` - Instruções
- Ficheiros gerados para revisão
- Automaticamente limpos após confirmação

### 4. Opções de Confirmação

```
[S]im / [N]ão / [R]ever ficheiros novamente: 
```

- **S** - Confirma e prossegue
- **N** - Cancela operação
- **R** - Reabre ficheiros em VS Code para nova análise

---

## 🔧 Configuração Avançada

### Desabilitar Preview Globalmente

Editar scripts e adicionar `auto_approve=True`:

```python
# Em generate_sebentas.py
generator = SebentaGenerator(auto_approve=True)
```

### Customizar Comportamento

```python
preview = PreviewManager(
    auto_open=True  # False para não abrir VS Code automaticamente
)

# Mostrar preview sem confirmação
preview.print_preview_summary(content, "Título")

# Apenas confirmar sem preview
if preview.confirm_action("Prosseguir?"):
    # ...
```

### Integração com Novos Scripts

```python
from preview_system import PreviewManager, create_exercise_preview

# 1. Gerar conteúdo
latex_content = generate_latex()
metadata = generate_metadata()

# 2. Criar preview
preview_content = create_exercise_preview(
    exercise_id="EX_001",
    latex_content=latex_content,
    metadata=metadata
)

# 3. Mostrar e confirmar
preview = PreviewManager()
if preview.show_and_confirm(preview_content, "Novo Item"):
    # 4. Salvar apenas se confirmado
    save_to_database(latex_content, metadata)
```

---

## 📊 Estatísticas e Tracking

Os scripts agora rastreiam operações canceladas:

```
📊 RESUMO
════════════════════════════════════════════════════════════════
Sebentas geradas: 5
PDFs compilados:  5
Canceladas:       2  ← NOVO
Erros:            0
════════════════════════════════════════════════════════════════
```

---

## 🤖 Uso com Agentes/Automação

### Modo Interactivo (Padrão)

Para uso manual com revisão:
```bash
python add_exercise_with_types.py
# Preview + confirmação manual
```

### Modo Automático (CI/CD)

Para pipelines automatizadas:
```bash
python generate_sebentas.py --auto-approve --no-preview
# Sem interação humana
```

### Modo Híbrido

Preview mas sem abrir VS Code:
```python
preview = PreviewManager(auto_open=False)
# Mostra no terminal, pede confirmação, mas não abre editor
```

### OpenCode / opencode (Agentes)

- Para interacções controladas por agentes, utilize os utilitários `opencode` disponíveis no repositório (`opencode_terminal_test.py`, `scripts/send_prompt_opencode.py`).
- Regras rápidas de uso:
    - Peça sempre permissão explícita ao utilizador antes de executar scripts que escrevam em `ExerciseDatabase/` ou `SebentasDatabase/`.
    - Não inclua segredos em prompts; solicite valores sensíveis diretamente ao utilizador e não grave esses valores.
    - Grave logs de execução em `temp/opencode_logs/` e apresente um sumário antes de mostrar o ficheiro completo.
    - Em Windows PowerShell use `;` para encadear comandos em uma linha.


---

## 🐛 Troubleshooting

### Preview não abre em VS Code

**Problema:** `code` command não encontrado

**Solução:**
1. Instalar VS Code
2. Adicionar ao PATH: `code` command
3. Ou desabilitar auto-open: `PreviewManager(auto_open=False)`

### Ficheiros temporários não são limpos

**Problema:** Erro ao remover temporários

**Causa:** Ficheiros ainda abertos em VS Code

**Solução:** Fechar ficheiros em VS Code antes de confirmar

### Sistema de preview não disponível

**Problema:** `preview_system.py` não encontrado

**Solução:**
```bash
# Verificar estrutura
ExerciseDatabase/
  _tools/
    preview_system.py  ← Deve existir
```

---

## 📚 Exemplos Práticos

### Exemplo 1: Criar Exercício com Revisão

```bash
# 1. Iniciar wizard
python ExerciseDatabase\_tools\add_exercise_with_types.py

# 2. Preencher dados interactivamente
Disciplina: matematica
Módulo: P4_funcoes
Conceito: 4-funcao_inversa
Tipo: determinacao_analitica
...

# 3. Preview automático
📋 PREVIEW: Novo Exercício...
🚀 Ficheiros abertos em VS Code

# 4. Revisar no VS Code
- Verificar LaTeX está correto
- Validar metadados
- Confirmar tags

# 5. Retornar ao terminal e confirmar
[S]im / [N]ão / [R]ever: S

# 6. Exercício adicionado!
✅ EXERCÍCIO ADICIONADO COM SUCESSO!
```

### Exemplo 2: Gerar Sebenta com Alterações

```bash
# 1. Gerar sebenta
python SebentasDatabase\_tools\generate_sebentas.py --module P4_funcoes --concept 4-funcao_inversa

# 2. Preview abre
📋 PREVIEW: Sebenta...

# 3. Revisar e encontrar problema
# (por exemplo: exercício com erro)

# 4. Cancelar geração
[N]ão

# 5. Corrigir exercício fonte
# Editar ExerciseDatabase/.../exercicio.tex

# 6. Regenerar
python SebentasDatabase\_tools\generate_sebentas.py --module P4_funcoes --concept 4-funcao_inversa

# 7. Confirmar após correção
[S]im
```

### Exemplo 3: Testes com Múltiplas Versões

```bash
# Gerar 3 versões com preview de cada
python SebentasDatabase\_tools\generate_tests.py \
  --versions 3 \
  --version-labels A,B,C \
  --module P4_funcoes

# Preview Versão A → Confirmar
# Preview Versão B → Confirmar
# Preview Versão C → Revisar → Confirmar
```

---

## 🎓 Boas Práticas

### ✅ DO

1. **Sempre revisar** preview antes de confirmar
2. **Verificar metadados** estão corretos
3. **Testar LaTeX** compila sem erros
4. **Cancelar se duvidoso** - melhor prevenir
5. **Usar tags apropriadas** para facilitar pesquisa

### ❌ DON'T

1. Não confirmar sem ler preview
2. Não usar `--auto-approve` em produção sem testes
3. Não ignorar warnings no preview
4. Não adicionar exercícios duplicados
5. Não esquecer de fechar ficheiros antes de confirmar

---

## 🔮 Roadmap Futuro

### Planejado

- [ ] Preview com compilação LaTeX em tempo real
- [ ] Diff visual para alterações em exercícios existentes
- [ ] Histórico de previews cancelados
- [ ] Sugestões automáticas de melhorias
- [ ] Integração com linting LaTeX
- [ ] Preview em formato web (HTML)

### Em Consideração

- [ ] Preview em modo side-by-side
- [ ] Comentários inline no preview
- [ ] Versionamento de drafts
- [ ] Colaboração multi-utilizador

---

## 📝 Notas de Versão

### v3.1 (2025-11-21)

**Novidades:**
- ✨ Sistema de preview e curadoria completo
- 🎨 Interface colorida no terminal
- 🚀 Abertura automática em VS Code
- 📊 Tracking de operações canceladas
- 🔧 Flags `--no-preview` e `--auto-approve`

**Scripts Atualizados:**
- `add_exercise_with_types.py`
- `generate_sebentas.py`
- `generate_tests.py`

**Novo Módulo:**
- `preview_system.py` - Sistema centralizado

---

## 🆘 Suporte

### Problemas Comuns

**Q:** O preview não funciona  
**A:** Verifique se `preview_system.py` existe e está no path correto

**Q:** VS Code não abre  
**A:** Configure `code` no PATH ou use `auto_open=False`

**Q:** Quero desabilitar preview  
**A:** Use flag `--no-preview` ou `--auto-approve`

### Contacto

Para questões ou sugestões:
- Issues no repositório
- Documentação adicional em `/docs`

---

**Filosofia:** _"Gere rápido, reveja sempre, confirme conscientemente"_

Versão: 3.1 | Autor: Sistema de Preview | Data: 2025-11-21
