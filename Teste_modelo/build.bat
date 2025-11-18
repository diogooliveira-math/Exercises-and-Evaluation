@echo off
REM LaTeX Build Script for exame.tex
REM Sets the correct MiKTeX PATH and compiles the document

set "MIKTEX_PATH=C:\Users\diogo\AppData\Local\Programs\MiKTeX\miktex\bin\x64"
set "PATH=%MIKTEX_PATH%;%PATH%"

echo Building exame.tex...
pdflatex -interaction=nonstopmode exame.tex

if %ERRORLEVEL% EQU 0 (
    echo.
    echo SUCCESS: exame.pdf has been generated!
    echo.
) else (
    echo.
    echo ERROR: LaTeX compilation failed!
    echo.
)

pause