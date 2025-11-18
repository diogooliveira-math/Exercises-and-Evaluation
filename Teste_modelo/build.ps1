# LaTeX Build Script for exame.tex
# Sets the correct MiKTeX PATH and compiles the document

param(
    [switch]$Clean
)

$MiKTeXPath = "C:\Users\diogo\AppData\Local\Programs\MiKTeX\miktex\bin\x64"
$env:PATH = "$MiKTeXPath;$env:PATH"

if ($Clean) {
    Write-Host "Cleaning auxiliary files..."
    Remove-Item *.aux, *.log, *.fdb_latexmk, *.fls, *.synctex.gz -ErrorAction SilentlyContinue
}

Write-Host "Building exame.tex..." -ForegroundColor Green

try {
    & pdflatex -interaction=nonstopmode exame.tex

    if ($LASTEXITCODE -eq 0) {
        Write-Host "`nSUCCESS: exame.pdf has been generated!" -ForegroundColor Green
        Write-Host "File location: $(Get-Location)\exame.pdf" -ForegroundColor Cyan
    } else {
        Write-Host "`nERROR: LaTeX compilation failed!" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "`nERROR: Failed to run pdflatex. Please check your MiKTeX installation." -ForegroundColor Red
    exit 1
}