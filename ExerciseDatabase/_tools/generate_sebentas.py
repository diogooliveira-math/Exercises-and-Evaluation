"""Gera um ficheiro 'sebenta' (master .tex) em cada pasta de conceito de um módulo.
- Procura por todas as pastas dentro de um módulo (por defeito: matematica/P4_funcoes).
- Para cada pasta, cria `sebenta_<concept>.tex` que contém um preâmbulo mínimo, macros usadas (
  \exercicio, \subexercicio, \option) e inclui por `\input{}` todos os .tex nessa pasta por ordem alfabética.

Não executa pdflatex; gera apenas os .tex combinados. Se quiseres que eu também compile em PDF, diz.
"""
from pathlib import Path
import sys
import subprocess
import shutil

BASE = Path(__file__).parent.parent
DISC = 'matematica'
MODULE = 'P4_funcoes'
MODULE_PATH = BASE / DISC / MODULE

if not MODULE_PATH.exists():
    print(f"Módulo não encontrado: {MODULE_PATH}")
    sys.exit(1)

# Carregar nomes 'humanos' dos conceitos a partir da configuração
cfg_path = BASE / 'modules_config.yaml'

def find_concept_name_from_yaml(cfg_path, module_name, concept_id):
    """Procura de forma simples no ficheiro YAML o campo 'name' do conceito.
    Não depende de PyYAML; faz uma procura de texto limitada dentro do bloco do módulo.
    """
    import re
    if not cfg_path.exists():
        return None
    with open(cfg_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # localizar bloco do módulo
    module_line_idx = None
    for i, line in enumerate(lines):
        if re.match(rf'^\s*{re.escape(module_name)}\s*:', line):
            module_line_idx = i
            break
    if module_line_idx is None:
        return None

    # procurar id do conceito próximo ao bloco do módulo (limite de pesquisa)
    for j in range(module_line_idx, min(module_line_idx + 1000, len(lines))):
        m = re.match(r"^\s*-\s*id\s*:\s*[\"']?([^\"'\n]+)[\"']?", lines[j])
        if m:
            found_id = m.group(1).strip()
            if found_id == concept_id:
                # procurar o campo name nas linhas seguintes
                for k in range(j, min(j + 20, len(lines))):
                    m2 = re.match(r"^\s*name\s*:\s*(.*)", lines[k])
                    if m2:
                        val = m2.group(1).strip()
                        # remover aspas se existirem
                        if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                            val = val[1:-1]
                        return val
                return None
    return None

# Caminho relativo do style.tex a partir de cada pasta de conceito (subir 4 níveis até raiz do workspace)
STYLE_REL = '../../../../Teste_modelo/config/style.tex'

COUNT = 0
for concept_dir in sorted([p for p in MODULE_PATH.iterdir() if p.is_dir()]):
    # Excluir ficheiros gerados 'sebenta_*.tex' para evitar inclusão recursiva
    tex_files = sorted([f for f in concept_dir.iterdir() if f.suffix == '.tex' and not f.name.startswith('sebenta_')])
    if not tex_files:
        print(f"Sem .tex em {concept_dir.relative_to(BASE)} — pulo")
        continue

    # name for sebenta file
    sebenta_name = concept_dir / f"sebenta_{concept_dir.name}.tex"

    # Determinar o nome legível do conceito (preservando acentos), se disponível
    concept_name = concept_dir.name.replace('_', ' ')
    # tentar obter nome via parsing simples do YAML (se existir)
    try:
        found = find_concept_name_from_yaml(cfg_path, MODULE, concept_dir.name)
        if found:
            concept_name = found
    except Exception:
        pass

    with open(sebenta_name, 'w', encoding='utf-8') as out:
        out.write('% Arquivo gerado automaticamente por generate_sebentas.py\n')
        out.write('\\documentclass[12pt]{article}\n')
        out.write('\\usepackage[utf8]{inputenc}\n')
        out.write('\\usepackage[T1]{fontenc}\n')
        out.write('\\usepackage[portuguese]{babel}\n')
        out.write('\\usepackage{amsmath,amssymb}\n')
        out.write('\\usepackage{geometry}\n')
        out.write('\\geometry{a4paper,margin=2.5cm}\n')
        out.write('% Inclui macros e formatação centralizadas\n')
        out.write('\\input{' + STYLE_REL + '}\n')
        # sobrescrever título do style.tex com o título da sebenta
        out.write('\\title{Sebenta - ' + concept_name + '}\n')
        out.write('\\date{}\n')
        out.write('\\begin{document}\n')
        out.write('\\maketitle\n')

        # Include each .tex file (exclui os sebenta_ gerados)
        for f in tex_files:
            rel = f.name
            out.write('% ---- Inclui: ' + rel + '\n')
            out.write('\\input{' + rel + '}\n\n')

        out.write('\\end{document}\n')

    print(f"Gerado: {sebenta_name.relative_to(BASE)}")
    COUNT += 1

print(f"Concluído: {COUNT} sebentas geradas em {MODULE_PATH.relative_to(BASE)}")

# Tentativa de compilação automática com pdflatex, se disponível
pdflatex_path = shutil.which('pdflatex')
if not pdflatex_path:
    print('\nAviso: `pdflatex` não encontrado no PATH. Para gerar PDFs, instale uma distribuição TeX e garanta que `pdflatex` está acessível.')
    sys.exit(0)

print('\n`pdflatex` encontrado — iniciando compilação das sebentas geradas...')
compiled = 0
for concept_dir in sorted([p for p in MODULE_PATH.iterdir() if p.is_dir()]):
    sebenta_file = concept_dir / f"sebenta_{concept_dir.name}.tex"
    if not sebenta_file.exists():
        continue

    # Executar pdflatex 2 vezes para resolver referências básicas
    cmd = [pdflatex_path, '-interaction=nonstopmode', sebenta_file.name]
    try:
        # rodar em cwd=concept_dir
        res1 = subprocess.run(cmd, cwd=str(concept_dir), capture_output=True, text=True)
        res2 = subprocess.run(cmd, cwd=str(concept_dir), capture_output=True, text=True)

        # Guardar log combinado
        log_path = concept_dir / f"sebenta_{concept_dir.name}.build.log"
        with open(log_path, 'w', encoding='utf-8') as lf:
            lf.write('=== pdflatex pass 1 stdout ===\n')
            lf.write(res1.stdout or '')
            lf.write('\n=== pdflatex pass 1 stderr ===\n')
            lf.write(res1.stderr or '')
            lf.write('\n=== pdflatex pass 2 stdout ===\n')
            lf.write(res2.stdout or '')
            lf.write('\n=== pdflatex pass 2 stderr ===\n')
            lf.write(res2.stderr or '')
        pdf_path = concept_dir / sebenta_file.with_suffix('.pdf').name
        # Criar pasta de build para mover ficheiros temporários e o .tex gerado
        build_dir = concept_dir / 'build'
        build_dir.mkdir(exist_ok=True)

        # Mover ficheiros temporários e o sebenta_*.tex para build/
        aux_suffixes = {'.aux', '.log', '.out', '.toc', '.fls', '.fdb_latexmk', '.synctex.gz'}
        for f in concept_dir.iterdir():
            try:
                if f == pdf_path:
                    continue
                # mover o ficheiro de build do script
                if f == log_path:
                    f.rename(build_dir / f.name)
                    continue
                # mover o sebenta source e quaisquer ficheiros auxiliares gerados
                if f.name.startswith('sebenta_') or f.suffix in aux_suffixes:
                    f.rename(build_dir / f.name)
            except Exception:
                # se não for possível mover, ignorar e continuar
                pass

        if res2.returncode == 0 and pdf_path.exists():
            print(f"Compilado com sucesso: {pdf_path.relative_to(BASE)}")
            compiled += 1
        else:
            print(f"Falha na compilação: {sebenta_file.relative_to(BASE)} — ver {log_path.relative_to(BASE)}")
    except Exception as e:
        print(f"Erro ao tentar compilar {sebenta_file}: {e}")

print(f"\nCompilação concluída: {compiled} PDFs gerados.")
