# 🎯 Sistema de Tipos de Exercícios - Quick Start

## 📌 Resumo da Estrutura v3.0

```
disciplina/tema/conceito/TIPO/exercicio.tex
```

**NOVO**: Camada de **tipos** para melhor organização!

## 🚀 Uso Rápido

### Criar Novo Exercício

```bash
cd ExerciseDatabase/_tools
python add_exercise_with_types.py
```

O script vai:
1. ✅ Pedir disciplina → tema → conceito → **tipo**
2. ✅ Permitir criar novo tipo se necessário
3. ✅ Gerar ID automaticamente com componente de tipo
4. ✅ Aplicar tags automáticas
5. ✅ Atualizar metadados do tipo e índice global

### Estrutura Criada

```
4-funcao_inversa/
├── determinacao_analitica/           # TIPO 1
│   ├── metadata.json                 # Lista de IDs dos exercícios deste tipo
│   ├── MAT_P4_..._ANA_001.tex       # Exercício 1
│   ├── MAT_P4_..._ANA_002.tex       # Exercício 2
│   └── MAT_P4_..._ANA_005.tex       # Exercício 5 (mínimo 5 por tipo)
├── determinacao_grafica/             # TIPO 2
│   ├── metadata.json                 # Lista de 5+ IDs
│   └── [5+ exercícios .tex...]
└── teste_reta_horizontal/            # TIPO 3
    ├── metadata.json                 # Lista de 5+ IDs
    └── [5+ exercícios .tex...]
```

## 📖 Documentação Completa

- **`GUIA_TIPOS_EXERCICIOS.md`** - Guia detalhado com exemplos
- **`.github/copilot-instructions.md`** - Instruções para Copilot Agent
- **`TODO.md`** - Roadmap do projeto

## 🔑 Conceitos-Chave

- **Tipo**: Categoria de exercício dentro de um conceito
- **Metadata do Tipo**: JSON com info do tipo e lista de exercícios
- **IDs com Tipo**: `MAT_P4FUNCOE_4FIN_ANA_001` (ANA = tipo)
- **Tags Automáticas**: Combinação de tags do conceito + tipo

## 🎓 Exemplo: Função Inversa

### Tipos Criados

1. **determinacao_analitica** - Cálculo de f⁻¹(x) algebricamente
2. **determinacao_grafica** - Obter gráfico por simetria
3. **teste_reta_horizontal** - Verificar injetividade

### Tags Automáticas

- Conceito: `inversa`, `funcao`
- Tipo 1: `calculo_analitico`, `expressao_analitica`
- Tipo 2: `grafico`, `simetria`, `bissectriz`
- Tipo 3: `injetividade`, `teste_reta_horizontal`

## 💡 Quando Criar Novo Tipo?

✅ **SIM**: Abordagens diferentes, competências distintas  
❌ **NÃO**: Diferença apenas cosmética

## 🛠️ Scripts Disponíveis

| Script | Função |
|--------|--------|
| `add_exercise_with_types.py` | ⭐ Criar exercício com tipos |
| `generate_variant.py` | 🔄 Gerar variantes (atualiza metadata.json) |
| `consolidate_type_metadata.py` | 🔧 Consolidar IDs em metadata.json |
| `migrate_to_types.py` | 📦 Migrar exercícios antigos para tipos |
| `add_exercise.py` | ⚠️ Antigo (sem tipos, evitar) |
| `search_exercises.py` | 🔍 Pesquisar exercícios |
| `manage_modules.py` | ⚙️ Gerir módulos e conceitos |

## 🤖 Copilot Agent

O agente está configurado para:
- Entender a estrutura de tipos
- Sugerir tipos apropriados
- Criar/organizar automaticamente
- Atualizar metadados corretamente

Pergunte: "Cria exercício de [tópico]" e o agente cuida do resto!

---

**Versão**: 3.0 | **Data**: 2025-11-19
