"""Test Generator with Exercise Content Loading

Creates LaTeX test files from selected exercise IDs, loading the actual
exercise content from ExerciseDatabase.

Behavior:
- Reads `--module` and `--concept` CLI args (optional).
- Reads env `TEST_SELECTED_EXERCISES` (comma-separated IDs).
- Loads exercise content from ExerciseDatabase index.json and .tex files
- Honors env flags: `TEST_NO_PREVIEW` (1=true), `TEST_NO_COMPILE` (1=true).
- Writes `SebentasDatabase/tests/<module>/<concept>/test_<module>_<concept>.tex`.
- If compile requested and `pdflatex` is available, attempts to compile.
"""
import os
import sys
import argparse
from pathlib import Path
import subprocess
import json
import re

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SEBENTA_DIR = REPO_ROOT / "SebentasDatabase"
EXERCISE_DB = REPO_ROOT / "ExerciseDatabase"


class TestTemplate:
    def __init__(self, module: str = '', concept: str = '', exercises: list = None,
                 no_preview: bool = True, no_compile: bool = True):
        self.module = module or 'misc'
        self.concept = concept or 'general'
        self.exercises = exercises or []
        self.no_preview = no_preview
        self.no_compile = no_compile
        self.index_data = self.load_index()

    def load_index(self):
        """Load ExerciseDatabase index.json"""
        index_file = EXERCISE_DB / "index.json"
        if not index_file.exists():
            return {'exercises': []}
        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load index.json: {e}")
            return {'exercises': []}

    def find_exercise_path(self, exercise_id: str) -> Path:
        """Find the .tex file path for a given exercise ID"""
        for ex in self.index_data.get('exercises', []):
            if ex.get('id') == exercise_id:
                # Try 'path' field first (common in index.json)
                ex_path = ex.get('path', '')
                if not ex_path:
                    # Fallback to 'source_file'
                    ex_path = ex.get('source_file', '')
                
                if ex_path:
                    # Normalize path separators for Windows
                    ex_path = ex_path.replace('\\', '/').replace('//', '/')
                    
                    # Check if path is a directory (exercise with subvariants)
                    full_path = EXERCISE_DB / ex_path
                    
                    if full_path.exists():
                        if full_path.is_dir():
                            # Look for main.tex inside the directory
                            main_tex = full_path / "main.tex"
                            if main_tex.exists():
                                return main_tex
                        else:
                            # It's a direct .tex file
                            return full_path
                    
                    # Try adding .tex extension if not present
                    if not ex_path.endswith('.tex'):
                        tex_file = EXERCISE_DB / f"{ex_path}.tex"
                        if tex_file.exists():
                            return tex_file
                        
                        # Try looking for main.tex in a directory with that name
                        dir_path = EXERCISE_DB / ex_path
                        if dir_path.is_dir():
                            main_tex = dir_path / "main.tex"
                            if main_tex.exists():
                                return main_tex
        
        # Fallback: search by ID pattern in filesystem
        return None

    def load_exercise_content(self, exercise_id: str) -> str:
        """Load the actual LaTeX content of an exercise"""
        tex_path = self.find_exercise_path(exercise_id)
        
        if not tex_path or not tex_path.exists():
            return f"\\item \\textbf{{Exercício {exercise_id}}} (ficheiro não encontrado)"
        
        try:
            with open(tex_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # If it's a main.tex with subvariants, process the includes
            if tex_path.name == 'main.tex' and tex_path.parent.is_dir():
                content = self.process_subvariant_inputs(content, tex_path.parent)
            
            # Remove metadata comments at the top (lines starting with % meta:)
            lines = content.split('\n')
            filtered_lines = []
            in_meta_block = False
            
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('% meta:'):
                    in_meta_block = True
                    continue
                elif in_meta_block and stripped.startswith('%'):
                    continue
                else:
                    in_meta_block = False
                    # Skip standalone comment lines with just exercise IDs
                    if re.match(r'^%\s*(Exercise ID|Sub-variant|Function):.*$', line):
                        continue
                    filtered_lines.append(line)
            
            content = '\n'.join(filtered_lines).strip()
            
            return content
            
        except Exception as e:
            return f"\\item \\textbf{{Erro ao carregar exercício {exercise_id}: {e}}}"

    def process_subvariant_inputs(self, content: str, exercise_dir: Path) -> str:
        """Process \\input{subvariant_N} and replace with actual content"""
        def replace_input(match):
            subvariant_name = match.group(1)
            subvariant_file = exercise_dir / f"{subvariant_name}.tex"
            
            if subvariant_file.exists():
                try:
                    with open(subvariant_file, 'r', encoding='utf-8') as f:
                        return f.read().strip()
                except Exception:
                    return f"% Erro ao carregar {subvariant_name}"
            else:
                return f"% Subvariant não encontrado: {subvariant_name}"
        
        pattern = r'\\input\{(subvariant_\d+)\}'
        return re.sub(pattern, replace_input, content)

    def generate_tex(self) -> str:
        # Use proper LaTeX template from SebentasDatabase if available
        template_path = SEBENTA_DIR / "_templates" / "test_template.tex"
        
        if template_path.exists():
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    template = f.read()
                # Will implement template substitution if needed
            except Exception:
                template = None
        else:
            template = None
        
        # Generate with basic template
        header = [
            "\\documentclass[12pt]{article}",
            "\\usepackage[utf8]{inputenc}",
            "\\usepackage[portuguese]{babel}",
            "\\usepackage{geometry}",
            "\\usepackage{amsmath, amssymb}",
            "\\usepackage{graphicx}",
            "\\usepackage{enumitem}",
            "\\usepackage{tikz}",
            "\\usepackage{placeins}",
            "\\geometry{a4paper, margin=2cm}",
            "",
            "% Custom commands (add project-specific macros here)",
            "\\newcommand{\\exercicio}[1]{\\textbf{#1}}",
            "\\newcommand{\\subexercicio}[1]{\\item #1}",
            "",
            "\\begin{document}",
            ""
        ]

        title = f"\\section*{{Teste: {self.module.replace('_', ' ')} / {self.concept.replace('_', ' ').replace('-', ' - ')}}}"
        body = [title, ""]

        if not self.exercises:
            body.append("\\textit{Nenhum exercício selecionado.}")
        else:
            body.append("\\begin{enumerate}[label=\\arabic*)]")
            for idx, ex_id in enumerate(self.exercises, 1):
                content = self.load_exercise_content(ex_id)
                body.append(f"\n\\item % {ex_id}")
                # Remove any leading \section or \exercicio wrapper if it exists
                # since we're numbering with enumerate
                content_clean = re.sub(r'^\\section\*?\{[^}]*\}\s*', '', content)
                content_clean = re.sub(r'^\\exercicio\{([^}]*)\}', r'\1', content_clean)
                body.append(content_clean)
                body.append("\\FloatBarrier")
                body.append("")
            body.append("\\end{enumerate}")

        footer = ["", "\\end{document}"]

        return "\n".join(header + body + footer)

    def save(self) -> Path:
        out_dir = SEBENTA_DIR / 'tests' / self.module / self.concept
        out_dir.mkdir(parents=True, exist_ok=True)
        tex_file = out_dir / f"test_{self.module}_{self.concept}.tex"
        content = self.generate_tex()
        with open(tex_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Generated .tex: {tex_file.relative_to(REPO_ROOT)}")
        return tex_file

    def compile_pdf(self, tex_file: Path) -> bool:
        if self.no_compile:
            print("Skipping compilation (no_compile=True)")
            return True

        pdflatex = shutil_which('pdflatex')
        if not pdflatex:
            print("pdflatex not found in PATH; cannot compile PDF")
            return False

        try:
            # Run twice to settle references
            for _ in range(2):
                subprocess.run([pdflatex, '-interaction=nonstopmode', tex_file.name], cwd=str(tex_file.parent), check=False)

            pdf_file = tex_file.with_suffix('.pdf')
            if pdf_file.exists():
                pdfs_dir = tex_file.parent / 'pdfs'
                pdfs_dir.mkdir(exist_ok=True)
                dest = pdfs_dir / pdf_file.name
                if dest.exists():
                    dest.unlink()
                pdf_file.rename(dest)
                print(f"PDF generated: {dest.relative_to(REPO_ROOT)}")
                return True
            else:
                print("PDF not produced by pdflatex")
                return False
        except Exception as e:
            print(f"Error during compilation: {e}")
            return False


def shutil_which(name: str):
    # small wrapper to avoid importing shutil at top-level for test speed
    try:
        import shutil
        return shutil.which(name)
    except Exception:
        return None


def parse_env_selected_exercises():
    v = os.environ.get('TEST_SELECTED_EXERCISES', '')
    if not v:
        return []
    parts = [p.strip() for p in v.split(',') if p.strip()]
    return parts


def main():
    parser = argparse.ArgumentParser(description='Minimal Test Generator shim')
    parser.add_argument('--module', help='module filter', default='')
    parser.add_argument('--concept', help='concept filter', default='')
    args = parser.parse_args()

    # Env flags
    def env_flag(name: str) -> bool:
        v = os.environ.get(name, '')
        return str(v).lower() in ('1', 'true', 'yes', 's', 'sim')

    no_preview = env_flag('TEST_NO_PREVIEW')
    no_compile = env_flag('TEST_NO_COMPILE')

    exercises = parse_env_selected_exercises()

    template = TestTemplate(module=args.module or 'misc', concept=args.concept or 'general',
                            exercises=exercises, no_preview=no_preview, no_compile=no_compile)

    tex_file = template.save()

    # Optionally compile
    if not no_compile:
        template.compile_pdf(tex_file)


if __name__ == '__main__':
    main()
