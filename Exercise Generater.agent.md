# Exercise Generator Agent Instructions

## Visão Geral
Este documento contém instruções específicas para o agente de geração de exercícios no repositório "Exercises and Evaluation". O agente deve seguir as convenções estabelecidas na versão 3.0 da estrutura, priorizando português (pt-PT) para descrições e inglês para termos técnicos.

## Estrutura de Resposta
- Sempre validar contra o esquema de metadados definido em `copilot-instructions.md`
- Usar formato JSON para metadados e LaTeX para conteúdo
- Incluir UUIDs únicos para novos exercícios
- Seguir convenções de nomeação: PascalCase para tipos, camelCase para funções

## Melhorias Implementadas (v1.1)
- **Automação**: O agente agora executa scripts automaticamente após gerar conteúdo.
- **Geração de IDs Únicos**: Verificação contra `index.json` para evitar duplicatas.
- **Criação Direta de Arquivos**: Arquivos `.tex` e `.json` são criados diretamente.
- **Validação**: Testes automatizados pós-geração.
- **Integração com Sebentas**: Opção para gerar PDFs automaticamente.
- **Feedback**: Resumos claros de ações realizadas.

## 🆕 Sistema de Preview e Curadoria (v3.1)

**CRÍTICO**: O agente DEVE sempre usar o sistema de preview antes de adicionar conteúdo.

### Fluxo Obrigatório com Preview

1. **Gerar Conteúdo** (LaTeX + metadados)
2. **🆕 PREVIEW AUTOMÁTICO**
   - Sistema mostra preview no terminal
   - Abre ficheiros em VS Code automaticamente
   - Aguarda confirmação do utilizador: `[S]im / [N]ão / [R]ever`
3. **Salvar** (só após confirmação)

### Comando com Preview (Padrão)

```bash
# Criar exercício COM PREVIEW
python ExerciseDatabase\_tools\add_exercise_with_types.py
# → Wizard interactivo
# → Preview automático
# → Confirmação necessária
```

### Flags de Automação

Para scripts não-interactivos:

```bash
# Sem preview (modo rápido)
python script.py --no-preview

# Auto-aprovar (CI/CD)
python script.py --auto-approve

# Totalmente automático
python script.py --no-preview --auto-approve
```

### Responsabilidades do Agente

- ✅ SEMPRE usar `add_exercise_with_types.py` (tem preview integrado)
- ✅ NUNCA salvar ficheiros diretamente sem preview
- ✅ INFORMAR utilizador que preview será mostrado
- ✅ AGUARDAR confirmação antes de prosseguir
- ❌ NUNCA usar flags `--no-preview` ou `--auto-approve` sem permissão explícita

### Documentação

- 📚 [PREVIEW_SYSTEM.md](./PREVIEW_SYSTEM.md) - Documentação completa
- 🚀 [PREVIEW_QUICKSTART.md](./PREVIEW_QUICKSTART.md) - Quick start
- 📖 Ver `.github/copilot-instructions.md` para detalhes

## Capacidades do Agente

### Fluxo Automatizado de Geração
O agente segue estes passos para gerar exercícios de forma autónoma:

1. **Análise do Prompt**: Identificar tipo base, conceito e contexto.
2. **Verificação de Unicidade**: Consultar `index.json` para gerar ID único.
3. **Geração de Metadados**: Criar `metadata.json` do tipo se necessário.
4. **Criação de Arquivos**: Gerar `.tex` e `.json` diretamente.
5. **Atualização de Índices**: Modificar `index.json` automaticamente.
6. **Validação**: Executar testes e compilar LaTeX.
7. **Feedback**: Informar usuário sobre sucesso/falhas.

### Geração de Tipos de Exercícios
O agente pode criar novos tipos de exercícios baseados em tipos existentes, adaptando-os para novos contextos pedagógicos.

#### Exemplo: Geração de Tipo Similar
**Prompt:** "Gera-me um tipo de exercício semelhante a calculo_percentagens mas agora aplicada à finança pessoal/familiar"

**Resposta do Agente:**
1. **Identificar Tipo Base:**
   - Localizar `calculo_percentagens` em `ExerciseDatabase/matematica/P1_modelos_matematicos_para_a_cidadania/percentagens/calculo_percentagens/`
   - Analisar `metadata.json` do tipo existente para entender estrutura

2. **Verificar Unicidade:**
   - Consultar `index.json` para próximos IDs disponíveis (ex.: último é `MAT_P1MODELO_PERC_CALC_001`, então próximo é `MAT_P1MODELO_FIN_CALC_001`)

3. **Adaptar para Novo Contexto:**
   - **Novo Tipo:** `calculo_percentagens_financeiras`
   - **Nome do Tipo:** "Cálculo de Percentagens em Finanças Pessoais/Familiares"
   - **Conceito:** Criar novo conceito `financas_pessoais` em módulo apropriado (ex.: `P1_modelos_matematicos_para_a_cidadania` ou novo módulo `P2_financas_pessoais`)
   - **Descrição:** "Exercícios focados no cálculo de percentagens aplicadas a contextos financeiros pessoais e familiares, como juros, impostos, orçamentos e investimentos."

4. **Gerar Metadados do Tipo:**
   ```json
   {
     "tipo": "calculo_percentagens_financeiras",
     "tipo_nome": "Cálculo de Percentagens em Finanças Pessoais/Familiares",
     "conceito": "financas_pessoais",
     "conceito_nome": "Finanças Pessoais e Familiares",
     "tema": "P1_modelos_matematicos_para_a_cidadania",
     "tema_nome": "MÓDULO P1 - Modelos Matemáticos para a Cidadania",
     "disciplina": "matematica",
     "descricao": "Exercícios focados no cálculo de percentagens aplicadas a contextos financeiros pessoais e familiares, incluindo juros compostos, impostos sobre rendimento, orçamentos familiares e cálculos de investimento.",
     "tags_tipo": [
       "percentagens",
       "financas_pessoais",
       "juros",
       "impostos",
       "orcamento_familiar",
       "investimentos"
     ],
     "caracteristicas": {
       "requer_calculo": true,
       "requer_grafico": false,
       "complexidade_algebrica": "baixa_media"
     },
     "dificuldade_sugerida": {
       "min": 1,
       "max": 3
     },
     "exercicios": []
   }
   ```

5. **Criar Estrutura de Diretórios:**
   - Criar diretório: `ExerciseDatabase/matematica/P1_modelos_matematicos_para_a_cidadania/financas_pessoais/calculo_percentagens_financeiras/`
   - Salvar `metadata.json` no diretório do tipo

6. **Gerar Exercício Exemplo:**
   - Criar arquivo `.tex` e `.json` para um exercício inicial
   - ID: `MAT_P1MODELO_FIN_CALC_001`
   - Conteúdo LaTeX focado em cálculo de percentagens em contexto financeiro

7. **Atualizar Índices:**
   - Adicionar entrada ao `index.json` global automaticamente
   - Executar validação: `python tests/quick_validation.py`

8. **Feedback:**
   - "Exercício criado com sucesso! Arquivos gerados: [lista]. Validação: OK. Próximos passos: Gerar sebenta com `python SebentasDatabase/_tools/generate_sebentas.py --module P1_modelos_matematicos_para_a_cidadania --concept financas_pessoais`"

### Validação e Testes
Após geração:
- Validar JSON contra schema
- Compilar LaTeX para verificar sintaxe
- Executar testes unitários se disponíveis

### Limitações
- Não gerar conteúdo que viole direitos autorais
- Manter foco pedagógico e matemático
- Evitar tópicos sensíveis sem confirmação

## Comandos Úteis
- Criar exercício: `python ExerciseDatabase/_tools/add_exercise_with_types.py`
- Atualizar índice: `python ExerciseDatabase/_tools/agent_index_updates/apply_index_patch.py`
- Validar: `python tests/quick_validation.py`
- Gerar sebenta: `python SebentasDatabase/_tools/generate_sebentas.py --module [module] --concept [concept]`

## Troubleshooting
- **Patch não adiciona exercícios**: Verificar se IDs já existem no `index.json`. Use grep para procurar duplicatas.
- **Erro de compilação LaTeX**: Verificar macros em `config/style.tex` e sintaxe no arquivo `.tex`.
- **Diretório não criado**: Garantir que o conceito pai existe antes de criar tipos.
- **IDs duplicados**: O agente agora verifica unicidade automaticamente.

## Exemplos de Prompts
- "Cria um exercício sobre juros compostos em finanças pessoais"
- "Gera um tipo similar a determinacao_analitica para funções exponenciais"
- "Adiciona exercícios de análise gráfica para função inversa"

## Versão
v1.1 - Com automação, validação e feedback melhorados