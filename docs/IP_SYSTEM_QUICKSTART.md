# 🚀 Quick Start: Testes com IPs

> Em **5 minutos** da migração ao primeiro teste PDF

## ⚡ Setup Rápido

### 1. Migrar Exercícios (Uma vez)

```bash
# Ver IPs que serão atribuídos
python scripts/migrate_ips.py --dry-run --base ExerciseDatabase

# Aplicar
python scripts/migrate_ips.py --apply --base ExerciseDatabase
```

✅ Cria `ExerciseDatabase/_registry/ip_registry.json`  
✅ Adiciona `exercise.json` em cada exercício

### 2. Descobrir IPs

```bash
# Listar IPs de função inversa
python scripts/ip_lookup.py "1.2.4.*"
```

Output exemplo:
```
1.2.4.1.1 → matematica/P4_funcoes/4-funcao_inversa/determinacao_analitica/MAT_P4FUNCOE_4FIN_ANA_001
1.2.4.1.2 → matematica/P4_funcoes/4-funcao_inversa/determinacao_analitica/MAT_P4FUNCOE_4FIN_ANA_002
1.2.4.2.1 → matematica/P4_funcoes/4-funcao_inversa/determinacao_grafica/MAT_P4FUNCOE_4FIN_GRA_001
```

### 3. Gerar Teste

**Via VS Code** (recomendado):
```
Ctrl+Shift+P → Tasks: Run Task → 🎯 Gerar Teste (por IPs)
```

Preencher:
- **IPs**: `1.2.4.1.1,1.2.4.1.2,1.2.4.2.1`
- **Título**: `Teste de Funções`
- **Autor**: `Prof. Silva`

**Via CLI**:
```bash
python SebentasDatabase/_tools/generate_test_from_ips.py \
  --ips "1.2.4.1.1,1.2.4.1.2,1.2.4.2.1" \
  --title "Teste de Funções" \
  --author "Prof. Silva"
```

### 4. Resultado

PDF gerado em `SebentasDatabase/tests/test_ips_TIMESTAMP/test.pdf` 🎉

---

## 🔥 Casos de Uso Rápidos

### Teste com 3 exercícios específicos
```bash
python SebentasDatabase/_tools/generate_test_from_ips.py \
  --ips "1.2.4.1.1,1.2.4.1.3,1.2.4.2.1"
```

### Todos os exercícios de um tipo (wildcard)
```bash
python SebentasDatabase/_tools/generate_test_from_ips.py \
  --ips "1.2.4.1.*" \
  --title "Treino - Determinação Analítica"
```

### Sem preview (CI/automation)
```bash
python SebentasDatabase/_tools/generate_test_from_ips.py \
  --ips "1.2.4.1.1" \
  --no-preview \
  --auto-approve
```

### Apenas gerar .tex (não compilar)
```bash
python SebentasDatabase/_tools/generate_test_from_ips.py \
  --ips "1.2.4.1.1" \
  --no-compile
```

---

## 📚 Formato de IPs

```
1  .  2  .  4  .  1  .  3
│     │     │     │     └─── Exercício #3
│     │     │     └───────── Tipo (Determinação Analítica)
│     │     └─────────────── Conceito (Função Inversa)
│     └───────────────────── Módulo (P4 - Funções)
└─────────────────────────── Disciplina (Matemática)
```

### Wildcards

- `1.2.4.1.*` → Todos exercícios do tipo "determinacao_analitica"
- `1.2.4.*` → Todos exercícios do conceito "funcao_inversa"
- `1.2.*` → Todos exercícios do módulo "P4_funcoes"

---

## 🛠️ Comandos Úteis

```bash
# Lookup de IP específico
python scripts/ip_lookup.py 1.2.4.1.3

# Lookup com wildcard
python scripts/ip_lookup.py "1.2.4.*"

# Validar registry
python scripts/check_registry_consistency.py

# Reparar registry (backup automático)
python scripts/registry_repair.py --rebuild --backup
```

---

## ✅ Checklist de Validação

Depois de gerar teste:

- [ ] PDF compilado existe em `SebentasDatabase/tests/test_ips_*/test.pdf`
- [ ] Exercícios numerados sequencialmente ("Exercício 1.", "Exercício 2.", ...)
- [ ] Sem heading duplicado nos exercícios
- [ ] Sub-variants incluídos corretamente (se aplicável)
- [ ] Ficheiros temporários LaTeX limpos (`.aux`, `.log`)

---

## 🆘 Troubleshooting Rápido

| Erro | Solução |
|------|---------|
| "No exercises resolved" | Verificar IP com `ip_lookup.py` |
| "IP Resolver não disponível" | Verificar import: `from ExerciseDatabase._tools.ip_resolver import IPResolver` |
| Paths quebrados | Executar `check_registry_consistency.py` |
| Registry corrompido | `registry_repair.py --rebuild` |

---

## 📖 Documentação Completa

👉 `docs/IP_SYSTEM_GUIDE.md` - Guia técnico completo  
👉 `docs/ip_registry.md` - Especificação do registry  
👉 `reference/QA2/` - Estrutura de referência

---

**Tempo total**: ~5 minutos ⏱️  
**Dificuldade**: Básico 🟢  
**Pré-requisitos**: Python 3.8+, pdflatex
