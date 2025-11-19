"""Script simplificado para gerar sebenta de função inversa."""
import subprocess
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
EXERCISE_DB = PROJECT_ROOT / "ExerciseDatabase"
SEBENTAS_DB = PROJECT_ROOT / "SebentasDatabase"
TEMPLATE_PATH = SEBENTAS_DB / "_templates" / "sebenta_template.tex"

# Paths específicos
concept_path = EXERCISE_DB / "matematica" / "P4_funcoes" / "4-funcao_inversa"
output_dir = SEBENTAS_DB / "matematica" / "P4_funcoes" / "4-funcao_inversa"
output_dir.mkdir(parents=True, exist_ok=True)

# Carregar template
with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
    template = f.read()

# Coletar exercícios
exercises = []
for tipo_dir in sorted(concept_path.iterdir()):
    if tipo_dir.is_dir():
        for tex_file in sorted(tipo_dir.glob("*.tex")):
            exercises.append(tex_file)

# Gerar conteúdo
content_lines = []
content_lines.append("\\section*{Função Inversa}")
content_lines.append("")

for tex_file in exercises:
    content_lines.append(f"% {tex_file.name}")
    try:
        with open(tex_file, 'r', encoding='utf-8') as f:
            content_lines.append(f.read().strip())
        content_lines.append("\\FloatBarrier")
        content_lines.append("")
    except Exception as e:
        content_lines.append(f"% ERRO: {e}")

content = "\n".join(content_lines)

# Preencher template
latex_content = template.replace("%%TITLE%%", "")
latex_content = latex_content.replace("%%AUTHOR%%", "")
latex_content = latex_content.replace("%%DATE%%", "")
latex_content = latex_content.replace("%%HEADER_LEFT%%", "MÓDULO P4 - Funções")
latex_content = latex_content.replace("%%HEADER_RIGHT%%", "Função Inversa")
latex_content = latex_content.replace("%%CONTENT%%", content)

# Salvar .tex
tex_file = output_dir / "sebenta_4-funcao_inversa.tex"
with open(tex_file, 'w', encoding='utf-8') as f:
    f.write(latex_content)

print(f"✅ Gerado: {tex_file}")

# Compilar
pdflatex = shutil.which('pdflatex')
if pdflatex:
    print("🔨 Compilando PDF...")
    for i in range(2):
        subprocess.run(
            [pdflatex, '-interaction=nonstopmode', tex_file.name],
            cwd=str(output_dir),
            capture_output=True
        )
    
    pdf_file = output_dir / "sebenta_4-funcao_inversa.pdf"
    if pdf_file.exists():
        # Mover para pdfs/
        pdfs_dir = output_dir / "pdfs"
        pdfs_dir.mkdir(exist_ok=True)
        pdf_dest = pdfs_dir / pdf_file.name
        if pdf_dest.exists():
            pdf_dest.unlink()
        pdf_file.rename(pdf_dest)
        print(f"✅ PDF: {pdf_dest}")
        
        # Limpar temporários
        for file in output_dir.iterdir():
            if file.suffix in {'.aux', '.log', '.out', '.fls', '.fdb_latexmk', '.synctex.gz'} or file.name.startswith('sebenta_'):
                file.unlink()
        print("🧹 Limpeza concluída")
    else:
        print("❌ Erro na compilação")
else:
    print("⚠️ pdflatex não encontrado")
