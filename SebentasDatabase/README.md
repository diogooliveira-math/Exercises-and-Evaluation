# SebentasDatabase 📚

Sistema automatizado de geração de sebentas (compilações de exercícios em PDF) a partir da ExerciseDatabase.

## Estrutura

```
SebentasDatabase/
├── README.md                  # Este ficheiro
├── _tools/
│   └── generate_sebentas.py  # Script principal de geração
├── _templates/
│   └── sebenta_template.tex  # Template LaTeX base
└── [disciplina]/
    └── [módulo]/
        └── [conceito]/
            ├── sebenta_[conceito].tex  # Fonte LaTeX gerada
            └── sebenta_[conceito].pdf  # PDF final
```

## Características ✨

- ✅ **Geração automática** de PDFs a partir da ExerciseDatabase
- ✅ **Organização hierárquica** por disciplina/módulo/conceito
- ✅ **Limpeza automática** de ficheiros temporários do LaTeX
- ✅ **Templates centralizados** para consistência visual
- ✅ **Compilação automática** com pdflatex
- ✅ **Filtragem flexível** por disciplina, módulo ou conceito

## Uso Básico 🚀

### Gerar todas as sebentas

```bash
python SebentasDatabase\_tools\generate_sebentas.py
```

### Gerar para módulo específico

```bash
python SebentasDatabase\_tools\generate_sebentas.py --module P4_funcoes
```

### Gerar para conceito específico

```bash
python SebentasDatabase\_tools\generate_sebentas.py --module P4_funcoes --concept 4-funcao_inversa
```

### Apenas limpar ficheiros temporários

```bash
python SebentasDatabase\_tools\generate_sebentas.py --clean-only
```

### Gerar .tex sem compilar PDF

```bash
python SebentasDatabase\_tools\generate_sebentas.py --no-compile
```

## Opções de Linha de Comando

| Opção | Descrição | Exemplo |
|-------|-----------|---------|
| `--discipline` | Filtrar por disciplina | `--discipline matematica` |
| `--module` | Filtrar por módulo | `--module P4_funcoes` |
| `--concept` | Filtrar por conceito | `--concept 4-funcao_inversa` |
| `--tipo` | Filtrar por tipo de exercício | `--tipo determinacao_analitica` |
| `--clean-only` | Apenas limpar ficheiros temporários | `--clean-only` |
| `--no-compile` | Gerar .tex mas não compilar | `--no-compile` |

## Ficheiros Temporários Limpos 🧹

O sistema remove automaticamente após compilação:

- `.aux` - Informações auxiliares
- `.log` - Logs de compilação
- `.out` - Dados de hyperref
- `.toc` - Índice
- `.fls` - Lista de ficheiros
- `.fdb_latexmk` - Base de dados latexmk
- `.synctex.gz` - Dados de sincronização
- E outros ficheiros auxiliares

## Template LaTeX 📄

O template base (`_templates/sebenta_template.tex`) inclui:

- **Pacotes**: amsmath, tikz, geometry, hyperref
- **Macros personalizadas**: `\exercicio`, `\subexercicio`, `\option`
- **Cabeçalhos**: Disciplina, módulo e conceito
- **Layout**: A4, margens 2.5cm, fonte 12pt

### Variáveis do Template

- `%%TITLE%%` - Título da sebenta
- `%%AUTHOR%%` - Autor (gerado automaticamente)
- `%%DATE%%` - Data de geração
- `%%HEADER_LEFT%%` - Cabeçalho esquerdo (disciplina/módulo)
- `%%HEADER_RIGHT%%` - Cabeçalho direito (conceito)
- `%%CONTENT%%` - Conteúdo dos exercícios

## Estrutura de Output

Para cada conceito, o sistema gera:

```
SebentasDatabase/matematica/P4_funcoes/4-funcao_inversa/
├── sebenta_4-funcao_inversa.tex    # Fonte LaTeX
└── sebenta_4-funcao_inversa.pdf    # PDF final
```

## Requisitos 📋

- **Python 3.8+**
- **pdflatex** (MiKTeX, TeX Live ou similar)
- ExerciseDatabase estruturada corretamente

## Verificar Instalação do LaTeX

```powershell
pdflatex --version
```

Se não estiver instalado:
- **Windows**: [MiKTeX](https://miktex.org/download)
- **Linux**: `sudo apt install texlive-full`
- **macOS**: [MacTeX](https://www.tug.org/mactex/)

## Workflow Típico 🔄

1. **Adicionar exercícios** à ExerciseDatabase
2. **Gerar sebentas**:
   ```bash
   python SebentasDatabase\_tools\generate_sebentas.py
   ```
3. **Verificar PDFs** em `SebentasDatabase/[disciplina]/[módulo]/[conceito]/`
4. **Distribuir** aos alunos

## Logs e Depuração 🐛

### Se a compilação falhar:

- Verifique o ficheiro `*_error.log` na pasta do conceito
- Verifique se todos os ficheiros `.tex` referenciados existem
- Confirme que as macros usadas estão definidas no template

### Limpar ficheiros temporários manualmente:

```bash
python SebentasDatabase\_tools\generate_sebentas.py --clean-only
```

## Estatísticas de Geração 📊

Ao finalizar, o script apresenta:

```
📊 RESUMO
============================================================
Sebentas geradas: 5
PDFs compilados:  5
Ficheiros limpos: 25
============================================================
```

## Integração com ExerciseDatabase 🔗

O sistema lê automaticamente:

- **Estrutura de pastas**: disciplina/módulo/conceito/tipo
- **Metadados JSON**: informações dos tipos de exercícios
- **Ficheiros .tex**: exercícios individuais
- **modules_config.yaml**: configurações dos módulos

## Personalização 🎨

### Modificar o Template

Edite `_templates/sebenta_template.tex` para alterar:
- Layout e margens
- Estilo de cabeçalhos
- Macros personalizadas
- Pacotes LaTeX adicionais

### Adicionar Novos Tipos de Sebentas

Crie novos templates em `_templates/` e modifique o script para suportá-los.

## Boas Práticas ✅

1. **Sempre compile** antes de distribuir
2. **Verifique visualmente** os PDFs gerados
3. **Mantenha templates** versionados
4. **Use `--clean-only`** periodicamente para manter ordem
5. **Teste individualmente** conceitos novos antes de gerar tudo

## Resolução de Problemas 🔧

### "pdflatex não encontrado"

Instale uma distribuição TeX e adicione ao PATH.

### "Nenhum exercício encontrado"

Verifique se os ficheiros `.tex` existem no diretório do conceito.

### "Erro na compilação"

1. Abra o ficheiro `*_error.log`
2. Procure por linhas com `!` (erros LaTeX)
3. Corrija os exercícios fonte na ExerciseDatabase
4. Regenere a sebenta

### PDFs com formatação incorreta

Verifique se as macros `\exercicio`, `\subexercicio` e `\option` estão corretamente usadas nos ficheiros `.tex` fonte.

## Versionamento 📌

- **v1.0** - Sistema básico de geração
- **v2.0** - Suporte a tipos de exercícios
- **v3.0** - Limpeza automática de ficheiros temporários ✨ (atual)

## Contribuir 🤝

Para melhorias:
1. Teste as alterações em módulos individuais
2. Documente no código
3. Atualize este README

---

**Versão**: 3.0  
**Última atualização**: 2025-11-19  
**Autor**: Sistema Automático ExerciseDatabase
