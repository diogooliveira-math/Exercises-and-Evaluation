Guia rápido: Instalar TeX em Windows (MikTeX)

Este pequeno guia descreve os passos para instalar uma distribuição TeX em Windows e garantir que `pdflatex` esteja disponível no PATH, de forma a usar `scripts/build_temp_preview.py`.

1) Instalar MiKTeX
- Visite https://miktex.org/download e instale o instalador apropriado para Windows.
- Durante a instalação, escolha a opção que permita instalar pacotes on-the-fly (se disponível).
- Após instalar, abra a "MiKTeX Console" como administrador e atualize os pacotes.

2) Verificar `pdflatex`
- Abra `cmd` ou `PowerShell` e execute:
  pdflatex --version
- Deve mostrar a versão do pdfTeX/MiKTeX. Se o comando não for encontrado, adicione a pasta bin do MiKTeX ao PATH.

3) Instalar pacotes necessários
- Alguns documentos LaTeX podem necessitar de pacotes (ex: `lmodern`, `inputenc`). Use a MiKTeX Console para instalar pacotes faltantes.

4) Usando o script de preview
- Execute: `python scripts/build_temp_preview.py path/to/exercise.tex`
- O script criará um diretório `temp/preview_<timestamp>/` contendo o PDF.

Notas:
- Alternativamente, use TeX Live para uma instalação mais completa (https://www.tug.org/texlive/).
- Em ambientes de CI, prefira instalar TeX Live via pacote do sistema ou ações específicas do CI.
