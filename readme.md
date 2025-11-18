# Exercises and Evaluation

**Sistema completo de gestão e geração de materiais educativos em LaTeX**

Um projeto auxiliar para professores e profissionais da educação que necessitam de organizar, reutilizar e gerar documentos pedagógicos de forma eficiente e profissional.

---

## 📋 Visão Geral

O **Exercises and Evaluation** é um sistema modular que permite aos educadores:

1. **Organizar** uma base de dados estruturada de exercícios e conteúdo teórico
2. **Selecionar** exercícios por critérios específicos (tópico, dificuldade, tipo)
3. **Gerar** automaticamente exames, testes, fichas de trabalho e material didático
4. **Compilar** documentos profissionais em PDF com LaTeX
5. **Reutilizar** conteúdo pedagógico de forma sistemática

Este projeto resolve o problema comum de professores que mantêm exercícios dispersos em múltiplos documentos, facilitando a criação de avaliações personalizadas e materiais de apoio.

---

## 🎯 Principais Funcionalidades

### 1. Base de Dados de Exercícios
- **Armazenamento organizado** por disciplina, tópico e subtópico
- **Sistema de metadados** (tags, dificuldade, tipo, autor, data)
- **Indexação automática** para pesquisa rápida
- **Versionamento** e histórico de alterações
- **Validação de integridade** da base de dados

### 2. Geração Automática de Exames
- **Seleção inteligente** de exercícios com múltiplos critérios
- **Templates personalizáveis** (testes curtos, exames completos, fichas)
- **Múltiplas versões** com ordenação aleatória
- **Folhas de resposta** geradas automaticamente
- **Sistema de pontuação** configurável

### 3. Material Didático
- **Biblioteca de conteúdo teórico**:
  - Definições matemáticas
  - Proposições e demonstrações
  - Exemplos resolvidos
  - Explicações detalhadas
- **Compilação automática** de apontamentos e resumos
- **Integração** teoria + exercícios práticos

### 4. Sistema LaTeX Avançado
- **Macros personalizadas** para diferentes tipos de exercício:
  - `\exercicio{}` - Exercício principal com numeração automática
  - `\subexercicio{}` - Sub-exercícios com numeração hierárquica
  - `\exercicioDesenvolvimento{}` - Exercícios de resposta aberta
  - `\exercicioEscolha{}` + `\opcao{}` - Escolha múltipla
- **Estilos profissionais** e layouts configuráveis
- **Suporte para gráficos** com TikZ
- **Compilação otimizada** com scripts automáticos

---

## 📁 Estrutura do Projeto

```
Exercises and Evaluation/
│
├── README.md                    # Este ficheiro
├── TODO.md                      # Roadmap detalhado do projeto
│
├── Teste_modelo/               # Template de referência para exames
│   ├── exame.tex               # Documento principal
│   ├── exercises.tex           # Lista de exercícios
│   ├── build.ps1               # Script de compilação PowerShell
│   ├── build.bat               # Script de compilação Batch
│   │
│   ├── config/                 # Configurações LaTeX
│   │   ├── packages.tex        # Pacotes necessários
│   │   └── style.tex           # Macros e estilos personalizados
│   │
│   ├── content/                # Conteúdo do exame
│   │   ├── titlepage.tex       # Página de título
│   │   ├── introduction.tex    # Instruções do exame
│   │   ├── exercicio1.tex      # Exercícios individuais
│   │   ├── exercicio2.tex
│   │   ├── exercicio3.tex
│   │   └── conclusion.tex      # Conclusão/notas finais
│   │
│   └── Base/                   # Materiais fonte
│
├── ExerciseDatabase/           # [A CRIAR] Base de dados de exercícios
│   ├── matematica/
│   │   ├── funcoes/
│   │   ├── derivadas/
│   │   └── ...
│   └── index.json              # Índice de metadados
│
├── TheoryDatabase/             # [A CRIAR] Base de conteúdo teórico
│   ├── definicoes/
│   ├── proposicoes/
│   └── exemplos/
│
├── templates/                  # [A CRIAR] Templates de documentos
│   ├── exam_short.tex
│   ├── exam_full.tex
│   └── worksheet.tex
│
└── scripts/                    # [A CRIAR] Scripts de automação
    ├── generate_exam.py
    ├── add_exercise.py
    ├── search_exercise.py
    └── validate_database.py
```

---

## 🚀 Como Começar

### Pré-requisitos

1. **LaTeX** (MiKTeX ou TeX Live)
   - Windows: [MiKTeX](https://miktex.org/download)
   - Linux: `sudo apt-get install texlive-full`
   - macOS: `brew install mactex`

2. **Python 3.8+** (para scripts de automação - a implementar)

3. **Editor** (recomendado: VS Code com LaTeX Workshop)

### Uso Atual (Teste_modelo)

1. **Navegar para a pasta do modelo**:
   ```powershell
   cd "Teste_modelo"
   ```

2. **Compilar o exame**:
   ```powershell
   .\build.ps1
   ```
   
   Ou manualmente:
   ```powershell
   pdflatex exame.tex
   ```

3. **Visualizar o resultado**: Abrir `exame.pdf`

### Criar um Novo Exercício

Edite ou crie um ficheiro em `content/` seguindo o formato:

```latex
\exercicio{Enunciado do exercício principal}

\subexercicio{Primeira alínea}

\subexercicio{Segunda alínea}
```

Para exercícios de escolha múltipla:

```latex
\exercicioEscolha{Qual é a resposta correta?}

\opcao{Opção A}
\opcao{Opção B}
\opcao{Opção C}
\opcao{Opção D}
```

---

## 📚 Sistema de Macros LaTeX

### Comandos Disponíveis

| Macro | Descrição | Exemplo |
|-------|-----------|---------|
| `\exercicio{texto}` | Exercício principal (numeração automática) | Exercício 1. |
| `\subexercicio{texto}` | Sub-exercício (numeração hierárquica) | 1.1., 1.2., ... |
| `\exercicioDesenvolvimento{texto}` | Exercício de desenvolvimento com espaço | Com espaço amplo para resposta |
| `\exercicioEscolha{texto}` | Exercício de escolha múltipla | Prepara numeração de opções |
| `\opcao{texto}` | Opção de escolha múltipla | (a), (b), (c), ... |

### Exemplo Completo

```latex
\exercicio{Considere a função $f(x) = x^2 - 4x + 3$}

\subexercicio{Determine as raízes da função.}

\subexercicio{Calcule $f(2)$.}

\exercicioEscolha{A derivada de $f(x)$ é:}

\opcao{$f'(x) = 2x - 4$}
\opcao{$f'(x) = x - 4$}
\opcao{$f'(x) = 2x + 3$}
\opcao{$f'(x) = x^2 - 4$}
```

---

## 🎨 Personalização

### Alterar Informações do Exame

Edite `content/titlepage.tex` e `config/style.tex`:

```latex
\title{Nome do Exame}
\author{Nome da Escola}
\date{Data do Exame}
```

### Adicionar Novos Pacotes

Edite `config/packages.tex`:

```latex
\usepackage{novo-pacote}
```

### Modificar Estilos

Edite `config/style.tex` para personalizar aparência dos exercícios, espaçamentos, fontes, etc.

---

## 🛠️ Scripts de Compilação

### PowerShell (build.ps1)

```powershell
# Compilação simples
.\build.ps1

# Limpeza + compilação
.\build.ps1 -Clean
```

### Batch (build.bat)

```cmd
build.bat
```

### VS Code Tasks

Pressione `Ctrl+Shift+P` → "Tasks: Run Build Task" → "Build LaTeX Document"

---

## 📖 Roadmap e Desenvolvimento

Consulte **[TODO.md](TODO.md)** para o roadmap completo do projeto, incluindo:

- ✅ Fase 1: Análise e Estruturação (em progresso)
- 🔄 Fase 2: Sistema de Base de Dados de Exercícios
- 🔄 Fase 3: Gerador Automático de Exames
- 📅 Fase 4: Gerador de Material Didático
- 📅 Fase 5-10: Ferramentas, automação e funcionalidades avançadas

---

## 🤝 Contribuições

Contribuições são bem-vindas! Este projeto está em desenvolvimento ativo.

### Como Contribuir

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

---

## 📝 Exemplos de Uso

### Caso de Uso 1: Professor de Matemática
*"Preciso criar um teste sobre funções com 5 exercícios de dificuldade média"*

→ Sistema seleciona automaticamente exercícios da base de dados com os critérios especificados e gera o PDF do teste.

### Caso de Uso 2: Formador Técnico
*"Quero compilar todos os exercícios práticos sobre otimização para uma ficha de trabalho"*

→ Sistema agrega exercícios do tópico em documento único com formatação consistente.

### Caso de Uso 3: Preparação de Material
*"Necessito de criar apontamentos teóricos com exemplos sobre derivadas"*

→ Sistema combina definições, proposições e exemplos da base teórica num documento coeso.

---

## 🐛 Resolução de Problemas

### Erro: `pdflatex` não encontrado

**Solução**: Certifique-se que o MiKTeX/TeX Live está no PATH:

```powershell
$env:PATH = "C:\Users\[USER]\AppData\Local\Programs\MiKTeX\miktex\bin\x64;$env:PATH"
```

### Erro: Pacote LaTeX em falta

**Solução**: O MiKTeX instala automaticamente. Se não, execute:

```cmd
miktex packages install <nome-do-pacote>
```

### Erro: Ficheiros .aux/.log a causar problemas

**Solução**: Limpe ficheiros auxiliares:

```powershell
Remove-Item *.aux, *.log, *.out
```

---

## 📄 Licença

[A definir - sugestão: MIT License ou GPL-3.0]

---

## 👨‍💻 Autor

Projeto desenvolvido para auxiliar educadores na criação de materiais pedagógicos de qualidade.

---

## 📧 Contacto e Suporte

Para questões, sugestões ou reportar bugs:
- Abra uma [Issue](../../issues) no GitHub
- [Documentação adicional em desenvolvimento]

---

## 🙏 Agradecimentos

- Comunidade LaTeX pela excelente documentação
- Educadores que testam e fornecem feedback
- Contribuidores do projeto

---

**Versão**: 0.1.0 (em desenvolvimento)  
**Última atualização**: Novembro 2025