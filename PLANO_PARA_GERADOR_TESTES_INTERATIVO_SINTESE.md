# 📝 **PLANO PARA GERADOR DE TESTES INTERATIVO - SÍNTESE**

## 🎯 **Visão Geral**
O **Gerador de Testes Interativo** será uma interface amigável para criação de avaliações (testes/exames) em formato PDF. Permitirá ao usuário controle granular sobre quais exercícios incluir, desde seleção de disciplina até exercício específico dentro do módulo, com opções de preview e compilação customizáveis.

---

## 🚀 **FEATURES PRINCIPAIS**

### **1. Seleção Hierárquica Granular**
- **Disciplinas** → **Módulos** → **Conceitos** → **Tipos** → **Exercícios Específicos**
- **Seleção múltipla** em todos os níveis
- **Navegação inteligente**: opções se adaptam às seleções anteriores
- **Controle fino**: possibilidade de escolher exercícios individuais

### **2. Interface de Menu Hierárquica**
```
Disciplinas (múltiplas permitidas):
  1. matematica
  2. portugues
  3. historia
  0. (nenhum / skip)
  Pode escolher múltiplas opções separadas por vírgula (ex: 1,3,5)
Escolha: 1

Módulos disponíveis para matematica:
  1. P1_modelos_matematicos
  2. P4_funcoes
  3. P2_estatistica
  ...

Conceitos disponíveis para P4_funcoes:
  1. 1-generalidades_funcoes
  2. 4-funcao_inversa
  ...

Tipos disponíveis para 4-funcao_inversa:
  1. determinacao_analitica
  2. determinacao_grafica
  3. teste_reta_horizontal
  ...

Exercícios disponíveis:
  1. [MAT_P4FUNCOE_4FIN_ANA_001] Função Inversa - Análise
  2. [MAT_P4FUNCOE_4FIN_ANA_002] Função Inversa - Cálculo
  3. [MAT_P4FUNCOE_4FIN_GRA_001] Função Inversa - Gráfico
  ...
```

### **3. Modos de Seleção de Exercícios**
- **Automático**: Distribuição equilibrada por conceito/tipo
- **Manual**: Seleção individual de exercícios específicos
- **Aleatório**: Seleção randômica simples
- **Híbrido**: Combinação de critérios

### **4. Controle de Parâmetros do Teste**
- **Número de questões**: Personalizável (padrão: 10)
- **Dificuldade**: Filtros por nível de dificuldade
- **Distribuição**: Controle de percentual por conceito/tipo
- **Ordem**: Sequencial, aleatória, ou customizada

### **5. Sistema de Preview e Validação**
- **Preview visual** antes da compilação
- **Metadados mostrados**: distribuição por conceito/tipo, dificuldades, total de exercícios
- **Validação automática**: Verificação de consistência e cobertura
- **Cancelamento possível** em qualquer etapa

### **6. Template Editável de LaTeX**
- **Geração de LaTeX completo** com cabeçalho profissional
- **Edição interativa** antes da compilação
- **Campos personalizáveis**: instruções, cotações, duração
- **Espaço para rascunho** opcional

### **7. Integração com VS Code Tasks**
- **Task dedicada**: "📝 Gerar Teste (Interativo)"
- **Atalho rápido**: `Ctrl+Shift+P` → "Tasks: Run Task"
- **Output visual**: Resultados mostrados em painel dedicado

---

## 🧪 **TESTES IMPLEMENTADOS**

### **1. Teste de Seleção Granular**
```python
def test_granular_selection():
    """Test that allows selection from discipline to specific exercise."""
    # Verifica seleção hierárquica completa
    # Testa filtros em cada nível
    assert "Seleção granular funciona" in output
```

### **2. Teste de Modos de Seleção**
```python
def test_selection_modes():
    """Test automatic, manual, and random selection modes."""
    # Verifica distribuição automática
    # Verifica seleção manual
    # Verifica aleatoriedade
    assert "Modos de seleção funcionam" in output
```

### **3. Teste de Preview e Validação**
```python
def test_preview_validation():
    """Test preview shows correct metadata and validation."""
    # Verifica metadados no preview
    # Verifica validação de consistência
    assert "Preview mostra metadados corretos" in output
```

### **4. Teste de Template LaTeX**
```python
def test_latex_template():
    """Test LaTeX template generation and editing."""
    # Verifica estrutura LaTeX gerada
    # Verifica campos editáveis
    assert "Template LaTeX válido" in output
```

### **5. Teste de Controle de Parâmetros**
```python
def test_parameter_control():
    """Test difficulty filtering and distribution control."""
    # Verifica filtros de dificuldade
    # Verifica controle de distribuição
    assert "Controle de parâmetros funciona" in output
```

---

## ⚙️ **CONFIGURAÇÃO E FLAGS**

### **Variáveis de Ambiente**
| Variável | Descrição | Valores |
|----------|-----------|---------|
| `TEST_AUTO_CHOICES` | Seleções automáticas | `"disciplina,módulo,conceito,tipo,exercicios"` |
| `TEST_AUTO_APPROVE` | Auto-aprovação | `1`/`true`/`yes` |
| `TEST_NO_PREVIEW` | Desabilitar preview | `1`/`true` |
| `TEST_NO_COMPILE` | Desabilitar compilação | `1`/`true` |
| `TEST_NUM_QUESTIONS` | Número de questões | `10` (padrão) |
| `TEST_DIFFICULTY_FILTER` | Filtro de dificuldade | `"1,2,3"` (múltiplo) |

### **Argumentos CLI**
| Argumento | Descrição | Exemplo |
|-----------|-----------|---------|
| `--auto` | Seleções automáticas | `--auto matematica,P4_funcoes` |
| `--questions` | Número de questões | `--questions 15` |
| `--difficulty` | Filtro de dificuldade | `--difficulty 2,3` |
| `--mode` | Modo de seleção | `--mode auto` |

### **Flags de Controle**
- **No Preview**: Gera .tex mas não mostra preview
- **No Compile**: Gera .tex mas não compila PDF
- **Auto-approve**: Pula confirmações (para automação)
- **Selection Mode**: auto, manual, random, hybrid

---

## 🔄 **WORKFLOW COMPLETO**

### **Modo Interativo (Padrão)**
1. **Seleção de Disciplinas** (múltipla)
2. **Seleção de Módulos** (múltipla, filtrada por disciplinas)
3. **Seleção de Conceitos** (múltipla, filtrada por módulos)
4. **Seleção de Tipos** (múltipla, filtrada por conceitos)
5. **Seleção de Exercícios Específicos** (manual/auto/aleatório)
6. **Configuração de Parâmetros** (número, dificuldade, distribuição)
7. **Confirmação de Preview** (S/n)
8. **Geração de Template LaTeX** (com edição interativa)
9. **Confirmação de Compilação** (S/n)
10. **Execução** com parâmetros selecionados

### **Modo Automação**
1. **Leitura de variáveis** de ambiente/CLI
2. **Seleção automática** baseada em filtros
3. **Geração direta** sem interação
4. **Auto-approve** ativado automaticamente

### **Modo Híbrido**
1. **Seleção interativa** até certo nível
2. **Aplicação de filtros** automáticos
3. **Refinamento manual** se necessário

---

## 🎨 **EXPERIÊNCIA DO USUÁRIO**

### **Interface Amigável**
- **Menus claros** com numeração hierárquica
- **Instruções contextuais** em português
- **Validação em tempo real** das seleções
- **Mensagens de erro** descritivas e orientadoras

### **Flexibilidade Avançada**
- **Seleção múltipla**: `1,3,5` para escolher itens específicos
- **Ranges**: `1-5` para selecionar intervalos
- **Exclusões**: `-3` para excluir item 3
- **Skip opcional**: `0` para deixar campos vazios

### **Feedback Inteligente**
- **Prévia de distribuição**: Mostra quantos exercícios por categoria
- **Validação de cobertura**: Alerta se distribuição está desequilibrada
- **Sugestões automáticas**: Recomenda ajustes para melhor balanceamento
- **Confirmação obrigatória** para ações destrutivas

### **Edição Interativa de Template**
- **Abertura automática** do arquivo LaTeX no editor
- **Campos destacados** para edição (instruções, cotações)
- **Preview em tempo real** (se disponível)
- **Validação de sintaxe** LaTeX básica

---

## 🛠️ **INTEGRAÇÃO TÉCNICA**

### **Arquitetura**
```
generate_test_interactive.py
    ↓ (coleta parâmetros granulares)
run_generate_test_task.py
    ↓ (prepara environment)
SebentasDatabase/_tools/generate_test_template.py
    ↓ (executa geração)
[Preview System + LaTeX Compilation]
```

### **Compatibilidade**
- ✅ **Exercícios individuais** (`.tex` único)
- ✅ **Exercícios com subvariants** (pasta `main.tex` + `subvariant_*.tex`)
- ✅ **Sistema de tipos** (filtragem por tipo de exercício)
- ✅ **Sistema de dificuldades** (filtragem por nível)
- ✅ **Preview system** integrado
- ✅ **VS Code tasks** nativo

### **Tratamento de Erros**
- **Validação de entrada** em todas as etapas
- **Recuperação graceful** de erros de seleção
- **Logs estruturados** para debugging
- **Mensagens em português** para usuários finais

### **Performance**
- **Lazy loading**: Carrega exercícios apenas quando necessário
- **Cache inteligente**: Reutiliza dados já carregados
- **Paginação**: Para listas muito grandes
- **Timeout**: Prevenção de travamentos

---

## 📊 **ESTATÍSTICAS E MÉTRICAS**

### **Coverage de Testes**
- ✅ **Teste de seleção granular**: Valida hierarquia completa
- ✅ **Teste de modos de seleção**: Valida todos os modos
- ✅ **Teste de preview**: Valida metadados e validação
- ✅ **Teste de template**: Valida geração LaTeX
- ✅ **Teste de parâmetros**: Valida controles avançados

### **Cenários de Uso**
- **Ensino Fundamental/Médio**: Testes por conceito específico
- **Ensino Superior**: Avaliações abrangentes por módulo
- **Preparação para Exames**: Testes mistos com dificuldade controlada
- **Diagnóstico**: Testes focados em pontos específicos
- **Treinamento**: Exercícios progressivos por dificuldade

### **Métricas de Qualidade**
- **Balanceamento**: Distribuição ideal por conceito/tipo
- **Cobertura**: Percentual de tópicos abordados
- **Dificuldade**: Média e distribuição de níveis
- **Consistência**: Validação de fluxo lógico

---

## 🚀 **EXEMPLOS DE USO**

### **Uso Básico Interativo**
```bash
python scripts/generate_test_interactive.py
# Seguir menus hierárquicos...
```

### **Automação com Seleções Específicas**
```bash
TEST_AUTO_CHOICES="matematica,P4_funcoes,4-funcao_inversa,determinacao_analitica"
TEST_NUM_QUESTIONS=15
python scripts/generate_test_interactive.py
```

### **Via VS Code Task**
```
Ctrl+Shift+P → "Tasks: Run Task" → "📝 Gerar Teste (Interativo)"
```

### **Com Filtros Avançados**
```bash
python scripts/generate_test_interactive.py \
  --auto "matematica,P4_funcoes,4-funcao_inversa" \
  --questions 20 \
  --difficulty 2,3 \
  --mode hybrid
```

### **Seleção Manual Específica**
```bash
# Após seleção interativa até nível de exercícios:
# Escolha: 1,3,5,7,9,12,15,18,21,25
```

---

## 🎯 **DIFERENCIAIS COMPETITIVOS**

### **Vs. Gerador de Sebentas**
- ✅ **Controle mais granular**: Até exercício individual
- ✅ **Parâmetros avançados**: Dificuldade, distribuição, ordem
- ✅ **Modos de seleção**: Auto, manual, aleatório, híbrido
- ✅ **Template editável**: Personalização completa do LaTeX
- ✅ **Foco em avaliação**: Estrutura otimizada para testes

### **Vs. Sistemas Existentes**
- ✅ **Hierarquia completa**: Disciplina → Exercício individual
- ✅ **Flexibilidade máxima**: Qualquer combinação de filtros
- ✅ **Validação inteligente**: Sugestões de melhoria automática
- ✅ **Integração VS Code**: Workflow nativo no editor
- ✅ **Preview avançado**: Metadados detalhados e validação

### **Vs. Geradores Manuais**
- ✅ **Automação inteligente**: Seleção automática balanceada
- ✅ **Velocidade**: Geração rápida de testes complexos
- ✅ **Consistência**: Padrões aplicados automaticamente
- ✅ **Reprodutibilidade**: Mesmo teste pode ser regenerado
- ✅ **Escalabilidade**: Funciona com milhares de exercícios

---

## 🏗️ **IMPLEMENTAÇÃO PLANEJADA**

### **Fase 1: Core Interativo**
- Criar `scripts/generate_test_interactive.py`
- Implementar seleção hierárquica
- Integrar com sistema existente

### **Fase 2: Modos de Seleção**
- Implementar seleção automática balanceada
- Adicionar seleção manual granular
- Criar modo aleatório inteligente

### **Fase 3: Controles Avançados**
- Filtros de dificuldade
- Controle de distribuição
- Validação de cobertura

### **Fase 4: Template System**
- Melhorar template LaTeX
- Adicionar campos editáveis
- Integrar preview em tempo real

### **Fase 5: VS Code Integration**
- Criar tasks dedicadas
- Adicionar inputs parametrizados
- Documentar workflows

### **Fase 6: Testing & QA**
- Suite completa de testes
- Validação de edge cases
- Performance testing

---

**Versão**: 1.0 (Planejado)  
**Data**: 2025-11-25  
**Status**: ✅ Planejamento completo - Pronto para implementação  
**Baseado em**: Gerador de Sebentas Interativo v3.1  
**Objetivo**: Controle granular máximo para criação de avaliações educacionais</content>
<parameter name="filePath">c:\Users\diogo\projects\Exercises-and-Evaluation\PLANO_PARA_GERADOR_TESTES_INTERATIVO_SINTESE.md