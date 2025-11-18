# LaTeX Document: exame.tex

This is a LaTeX document for the mathematics exam with exercises on functions and rates of change.

## Building the Document

### Option 1: Using the Build Script (Recommended)
Run the PowerShell build script:
```powershell
.\build.ps1
```

Or use the batch file:
```cmd
build.bat
```

### Option 2: Using VS Code Tasks
1. Open the project in VS Code
2. Press `Ctrl+Shift+P` and select "Tasks: Run Build Task"
3. Choose "Build LaTeX Document"

### Option 3: Manual Compilation
Ensure the correct MiKTeX PATH is set:
```powershell
$env:PATH = "C:\Users\diogo\AppData\Local\Programs\MiKTeX\miktex\bin\x64;$env:PATH"
pdflatex exame.tex
```

## Exercise System

This document uses a custom exercise system with automatic numbering:

### Macros Available:

- **`\exercicio{conteúdo}`** - Creates a main exercise with automatic numbering (Exercício 1., Exercício 2., etc.)
- **`\exercicioDesenvolvimento{conteúdo}`** - Creates a development exercise with large space after the statement
- **`\exercicioEscolha{conteúdo}`** - Creates a multiple-choice exercise
- **`\opcao{conteúdo}`** - Creates multiple-choice options (a), b), c), d), etc.
- **`\subexercicio{conteúdo}`** - Creates a sub-exercise with automatic numbering (1.1, 1.2, 2.1, etc.)

### Usage Examples:

**Development Exercise:**
```latex
\exercicioDesenvolvimento{Resolva a equação $x^2 - 4x + 3 = 0$.}
```

**Multiple-Choice Exercise:**
```latex
\exercicioEscolha{Qual é a derivada de $f(x) = x^2$?}

\opcao{$f'(x) = x$}
\opcao{$f'(x) = 2x$}
\opcao{$f'(x) = 2$}
\opcao{$f'(x) = x^2$}
```

**Regular Exercise with Sub-exercises:**
```latex
\exercicio{Considere as funções reais de variável real $f$ e $g$, definidas por:
\[f(x) = x^3 \text{ e } g(x) = \frac{1}{x}\]}

\subexercicio{Obtenha as representações gráficas de $f$ e $g$.}

\subexercicio{Calcule a taxa de variação média das funções.}
```

This will automatically generate:
- **Exercício 1.** Considere as funções reais...
- **1.1.** Obtenha as representações gráficas...
- **1.2.** Calcule a taxa de variação média...

### Images in Exercises

Images can be included in exercises using the `\includegraphics` command. Place image files in the `content/` folder and reference them as `image.png` (or other formats).

Example:
```latex
\exercicio{See the following graph:

\begin{center}
\includegraphics[width=0.8\textwidth]{image.png}
\end{center}}

\subexercicio{Analyze the graph above.}
```

## Project Structure
- `exame.tex` - Main document file
- `config/` - Configuration files (packages.tex, style.tex)
- `content/` - Content files (titlepage.tex, introduction.tex, exercises, conclusion.tex)
- `Base/` - Source materials
- `build.ps1` / `build.bat` - Build scripts
- `.vscode/` - VS Code configuration

## Troubleshooting

### PATH Issues
If you encounter PATH-related errors, ensure you're using:
```
C:\Users\diogo\AppData\Local\Programs\MiKTeX\miktex\bin\x64
```

This is the MiKTeX installation that contains `pdflatex.exe`.

### Package Installation
If LaTeX packages are missing, MiKTeX should automatically download them. If not, run:
```cmd
miktex packages install <package-name>
```

### Clean Build
To clean auxiliary files and rebuild:
```powershell
.\build.ps1 -Clean
```

## Output
The compiled PDF will be generated as `exame.pdf` in the project root directory.