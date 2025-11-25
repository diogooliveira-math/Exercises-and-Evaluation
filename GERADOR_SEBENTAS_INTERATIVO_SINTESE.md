# 📚 **SÍNTESE COMPLETA: GERADOR DE SEBENTAS INTERATIVO**

## 🎯 **Visão Geral**
O **Gerador de Sebentas Interativo** (`scripts/generate_sebenta_interactive.py`) é uma interface amigável para criação de coleções de exercícios (sebentas) em formato PDF. Permite seleção visual de disciplinas, módulos, conceitos e tipos de exercício, com opções de preview e compilação customizáveis.

---

## 🚀 **FEATURES PRINCIPAIS**

### **1. Seleção Hierárquica Interativa**
- **Disciplinas** → **Módulos** → **Conceitos** → **Tipos**
- **Seleção múltipla** permitida em todos os níveis
- **Navegação inteligente**: opções disponíveis se adaptam às seleções anteriores
- **Opção "skip"**: permite deixar campos vazios para seleção mais ampla

### **2. Interface de Menu Numerada**
```
Disciplinas (múltiplas permitidas):
  1. matematica
  2. portugues
  3. historia
  0. (nenhum / skip)
  Pode escolher múltiplas opções separadas por vírgula (ex: 1,3,5)
Escolha: 1
```

### **3. Modo Automação (CLI/Environment)**
- **Variável de ambiente**: `SEBENTA_AUTO_CHOICES="disciplina,módulo,conceito,tipo"`
- **Argumento CLI**: `--auto disciplina,módulo,conceito,tipo`
- **Compatibilidade**: Funciona com CI/CD e scripts automatizados

### **4. Controle de Preview e Compilação**
- **Pergunta interativa**: "Deseja pré-visualização antes de compilar? [S/n]"
- **Pergunta interativa**: "Deseja compilar PDF? [S/n]"
- **Confirmação final**: "Continuar? [s/N]"
- **Auto-approve**: Pula confirmações quando apropriado

### **5. Sistema de Preview Integrado**
- **Preview visual** antes da compilação (opcional)
- **Metadados mostrados**: disciplina, módulo, conceito, tipos, total de exercícios
- **Confirmação obrigatória** antes de prosseguir
- **Cancelamento possível** em qualquer etapa

### **6. Integração com VS Code Tasks**
- **Task dedicada**: "📚 Gerar Sebenta (Interativo)"
- **Atalho rápido**: `Ctrl+Shift+P` → "Tasks: Run Task"
- **Output visual**: Resultados mostrados em painel dedicado

---

## 🧪 **TESTES IMPLEMENTADOS**

### **1. Teste de Preview Interativo** (`test_generate_sebenta_interactive_preview.py`)
```python
def test_interactive_asks_for_preview():
    """Test that interactive mode asks for preview and compile options."""
    # Verifica se perguntas aparecem na saída
    assert "Deseja pré-visualização" in stdout
    assert "Deseja compilar PDF" in stdout
```

### **2. Teste de Modo Automação**
```python
def test_auto_mode_does_not_ask():
    """Test that auto mode does not ask for preview."""
    # Verifica que não pergunta em modo auto
    assert "Deseja pré-visualização" not in stdout
    assert "Auto-mode enabled" in stdout
```

### **3. Teste de Fumaça** (`test_generate_sebentas_smoke.py`)
```python
def test_generate_sebenta_no_compile():
    """Smoke test: run generate_sebentas.py in no-compile/no-preview mode"""
    # Testa geração básica sem preview/compilação
    assert result.returncode == 0
    assert tex_path.exists()
```

### **4. Teste de Filtro por Tipo** (`test_generate_sebentas_tipo_filter.py`)
```python
def test_generate_sebenta_with_tipo(tmp_path):
    """Test filtering by tipo (exercise type)"""
    # Cria estrutura temporária com dois tipos
    # Verifica que apenas exercícios do tipo selecionado são incluídos
    assert "Exercicio A" in content
    assert "Exercicio B" not in content
```

---

## ⚙️ **CONFIGURAÇÃO E FLAGS**

### **Variáveis de Ambiente**
| Variável | Descrição | Valores |
|----------|-----------|---------|
| `SEBENTA_AUTO_CHOICES` | Seleções automáticas | `"disciplina,módulo,conceito,tipo"` |
| `SEBENTA_AUTO_APPROVE` | Auto-aprovação | `1`/`true`/`yes` |
| `SEBENTA_NO_PREVIEW` | Desabilitar preview | `1`/`true` |
| `SEBENTA_NO_COMPILE` | Desabilitar compilação | `1`/`true` |

### **Argumentos CLI**
| Argumento | Descrição | Exemplo |
|-----------|-----------|---------|
| `--auto` | Seleções automáticas | `--auto matematica,P4_funcoes` |

### **Flags de Controle**
- **No Preview**: Gera .tex mas não mostra preview
- **No Compile**: Gera .tex mas não compila PDF
- **Auto-approve**: Pula confirmações (para automação)

---

## 🔄 **WORKFLOW COMPLETO**

### **Modo Interativo (Padrão)**
1. **Seleção de Disciplinas** (múltipla)
2. **Seleção de Módulos** (múltipla, filtrada por disciplinas)
3. **Seleção de Conceitos** (múltipla, filtrada por módulos)
4. **Seleção de Tipos** (múltipla, filtrada por conceitos)
5. **Confirmação de Preview** (S/n)
6. **Confirmação de Compilação** (S/n)
7. **Confirmação Final** (s/N)
8. **Execução** com parâmetros selecionados

### **Modo Automação**
1. **Leitura de variáveis** de ambiente/CLI
2. **Execução direta** sem interação
3. **Auto-approve** ativado automaticamente

### **Integração com Sistema Principal**
- Chama `scripts/run_generate_sebenta_task.py`
- Passa parâmetros via variáveis de ambiente
- Suporte completo ao sistema de preview existente
- Compatibilidade com filtros por tipo

---

## 🎨 **EXPERIÊNCIA DO USUÁRIO**

### **Interface Amigável**
- **Menus claros** com numeração
- **Instruções contextuais** em português
- **Validação de entrada** em tempo real
- **Mensagens de erro** descritivas

### **Flexibilidade**
- **Seleção múltipla**: `1,3,5` para escolher itens específicos
- **Skip opcional**: `0` para deixar campos vazios
- **Navegação reversa**: pode voltar em qualquer etapa

### **Feedback Visual**
- **Resumo final** antes da execução
- **Confirmação obrigatória** para ações destrutivas
- **Progress indicators** durante processamento
- **Logs detalhados** para debugging

---

## 🛠️ **INTEGRAÇÃO TÉCNICA**

### **Arquitetura**
```
generate_sebenta_interactive.py
    ↓ (coleta parâmetros)
run_generate_sebenta_task.py
    ↓ (prepara environment)
SebentasDatabase/_tools/generate_sebentas.py
    ↓ (executa geração)
[Preview System + LaTeX Compilation]
```

### **Compatibilidade**
- ✅ **Exercícios individuais** (`.tex` único)
- ✅ **Exercícios com subvariants** (pasta `main.tex` + `subvariant_*.tex`)
- ✅ **Sistema de tipos** (filtragem por tipo de exercício)
- ✅ **Preview system** integrado
- ✅ **VS Code tasks** nativo

### **Tratamento de Erros**
- **Validação de entrada** em todas as etapas
- **Recuperação graceful** de erros
- **Logs estruturados** para debugging
- **Mensagens em português** para usuários finais

---

## 📊 **ESTATÍSTICAS E MÉTRICAS**

### **Coverage de Testes**
- ✅ **Teste de preview interativo**: Valida perguntas aparecem
- ✅ **Teste de modo auto**: Valida não pergunta quando deve
- ✅ **Teste de fumaça**: Valida geração básica funciona
- ✅ **Teste de filtro por tipo**: Valida seleção por categoria

### **Cenários de Uso**
- **Desenvolvimento**: Criação rápida de sebentas para teste
- **Produção**: Geração de materiais para distribuição
- **Automação**: Integração com CI/CD pipelines
- **Educação**: Criação de materiais pedagógicos

---

## 🚀 **EXEMPLOS DE USO**

### **Uso Básico Interativo**
```bash
python scripts/generate_sebenta_interactive.py
# Seguir menus interativos...
```

### **Automação com Seleções Específicas**
```bash
SEBENTA_AUTO_CHOICES="matematica,P4_funcoes,4-funcao_inversa," python scripts/generate_sebenta_interactive.py
```

### **Via VS Code Task**
```
Ctrl+Shift+P → "Tasks: Run Task" → "📚 Gerar Sebenta (Interativo)"
```

### **Com Filtros Avançados**
```bash
python scripts/generate_sebenta_interactive.py --auto "matematica,P4_funcoes,,determinacao_analitica"
```

---

## 🎯 **DIFERENCIAIS COMPETITIVOS**

### **Vs. Interface Direta**
- ✅ **Mais amigável** para usuários não-técnicos
- ✅ **Validação em tempo real** das seleções
- ✅ **Flexibilidade** na navegação (skip, múltipla escolha)
- ✅ **Preview integrado** antes da compilação

### **Vs. Scripts Diretos**
- ✅ **Descoberta visual** da estrutura disponível
- ✅ **Confirmação obrigatória** para evitar erros
- ✅ **Logs amigáveis** em português
- ✅ **Recuperação de erros** com orientação

### **Vs. Outros Geradores**
- ✅ **Integração nativa** com VS Code
- ✅ **Sistema de tipos** avançado
- ✅ **Suporte a subvariants** (exercícios complexos)
- ✅ **Preview system** profissional

---

**Versão**: 3.1 (com subvariants + tipos)  
**Data**: 2025-11-25  
**Status**: ✅ Totalmente funcional e testado  
**Próximas Features**: Integração com IA para sugestões automáticas</content>
<parameter name="filePath">c:\Users\diogo\projects\Exercises-and-Evaluation\GERADOR_SEBENTAS_INTERATIVO_SINTESE.md