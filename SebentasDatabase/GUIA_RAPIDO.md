# Guia Rápido - SebentasDatabase

## Gerar todas as sebentas

```bash
python SebentasDatabase/_tools/generate_sebentas.py
```

## Gerar para módulo específico (TODOS os conceitos + consolidada)

```bash
python SebentasDatabase/_tools/generate_sebentas.py --module P4_funcoes
```

Isto gera:
- Uma sebenta para cada conceito individual
- Uma sebenta consolidada do módulo inteiro (`sebenta_modulo_[nome].tex` e `.pdf`)

## Gerar apenas conceitos individuais (sem consolidada)

```bash
python SebentasDatabase/_tools/generate_sebentas.py --module P4_funcoes --no-module-sebenta
```

## Gerar apenas um conceito específico

```bash
python SebentasDatabase/_tools/generate_sebentas.py --module P4_funcoes --concept 4-funcao_inversa
```

## Apenas limpar ficheiros temporários

```bash
python SebentasDatabase/_tools/generate_sebentas.py --clean-only
```

## Output

- **Sebentas .tex**: `SebentasDatabase/[disciplina]/[módulo]/[conceito]/sebenta_[conceito].tex`
- **PDFs**: `SebentasDatabase/[disciplina]/[módulo]/[conceito]/sebenta_[conceito].pdf`

## Limpeza Automática

O sistema remove automaticamente:
- `.aux`, `.log`, `.out`, `.fls`, `.fdb_latexmk`, `.synctex.gz`
- E outros ficheiros temporários do LaTeX

Os PDFs gerados são preservados.

## Resolução de Problemas

### Warnings "Missing $"
São avisos normais do LaTeX com caracteres especiais. O PDF é gerado mesmo assim.

### "pdflatex não encontrado"
Instale MiKTeX ou TeX Live e adicione ao PATH.

### Compilação falha
Verifique o ficheiro `*_error.log` no diretório da sebenta para detalhes do erro.
