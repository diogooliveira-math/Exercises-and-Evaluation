#!/usr/bin/env python3
"""
Sistema de Adição de Exercícios MÍNIMO com Inferência Inteligente
===================================================================

Workflow Ultra-Simplificado:
1. Template mínimo: apenas Módulo + Conceito + Enunciado
2. Sistema infere automaticamente:
   - Disciplina (do módulo)
   - Tipo (análise de palavras-chave)
   - Dificuldade (padrão ou inferência)
   - Formato (análise do enunciado)
   - Tags (conceito + palavras-chave)
3. Validação e incorporação automática

Tempo: ~30-60 segundos por exercício (vs 5 minutos antes)
"""

import json
import os
import sys
import io
import yaml
import tempfile
import time
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple, List

# Ensure local _tools package directory is on sys.path so relative imports work when
# scripts are loaded dynamically by tests or run from other CWDs.
sys.path.insert(0, str(Path(__file__).parent))

# Note: Do not re-wrap sys.stdout/sys.stderr at import time to avoid interfering with
# test harnesses (pytest). Any platform-specific stdout fixes are applied in main().

try:
    from preview_system import PreviewManager, create_exercise_preview
except Exception:
    PreviewManager = None

# Cores para terminal
class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'


class ExerciseInference:
    """Sistema de inferência inteligente de metadados."""
    
    # Palavras-chave para detectar tipo de exercício
    TYPE_KEYWORDS = {
        'determinacao_analitica': [
            'determine', 'calcule', 'obtenha', 'encontre', 'expressão', 
            'analítica', 'fórmula', 'função inversa'
        ],
        'determinacao_grafica': [
            'gráfico', 'esboce', 'represente graficamente', 'trace',
            'desenhe', 'plano cartesiano'
        ],
        'teste_reta_horizontal': [
            'injetiva', 'sobrejetiva', 'bijetiva', 'teste da reta',
            'verifique se', 'função inversa existe'
        ],
        'aplicacao_pratica': [
            'problema', 'situação', 'contexto real', 'aplicação',
            'modelação', 'modelo matemático'
        ],
        'calculo_direto': [
            'calcule', 'compute', 'efetue', 'valor numérico'
        ],
        'demonstracao': [
            'demonstre', 'prove', 'mostre que', 'justifique'
        ],
        'interpretacao': [
            'interprete', 'explique', 'significado', 'o que representa'
        ]
    }
    
    # Palavras-chave para detectar formato
    FORMAT_KEYWORDS = {
        'escolha_multipla': ['opção correta', 'alternativa', 'assinale', 'selecione'],
        'verdadeiro_falso': ['verdadeiro ou falso', 'classifique', 'V ou F'],
        'resposta_curta': ['qual é', 'quanto vale', 'valor de']
    }
    
    # Palavras para ajustar dificuldade
    DIFFICULTY_KEYWORDS = {
        1: ['básico', 'simples', 'elementar', 'direto'],
        3: ['complexo', 'múltiplos passos', 'combine'],
        4: ['avançado', 'difícil', 'desafio', 'prove'],
        5: ['muito difícil', 'pensamento crítico', 'generalização']
    }
    
    @staticmethod
    def infer_type(enunciado: str, conceito: str) -> str:
        """Infere tipo de exercício baseado no enunciado."""
        enunciado_lower = enunciado.lower()
        
        # Tentar detectar por palavras-chave
        scores = {}
        for tipo, keywords in ExerciseInference.TYPE_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in enunciado_lower)
            if score > 0:
                scores[tipo] = score
        
        if scores:
            return max(scores, key=scores.get)
        
        # Default: desenvolvimento
        return 'desenvolvimento'
    
    @staticmethod
    def infer_format(enunciado: str) -> str:
        """Infere formato baseado no enunciado."""
        enunciado_lower = enunciado.lower()
        
        for formato, keywords in ExerciseInference.FORMAT_KEYWORDS.items():
            if any(kw in enunciado_lower for kw in keywords):
                return formato
        
        # Default: desenvolvimento
        return 'desenvolvimento'
    
    @staticmethod
    def infer_difficulty(enunciado: str) -> int:
        """Infere dificuldade baseado em palavras-chave."""
        enunciado_lower = enunciado.lower()
        
        for difficulty, keywords in ExerciseInference.DIFFICULTY_KEYWORDS.items():
            if any(kw in enunciado_lower for kw in keywords):
                return difficulty
        
        # Default: 2 (Fácil)
        return 2
    
    @staticmethod
    def extract_tags(enunciado: str, conceito: str, tipo: str) -> List[str]:
        """Extrai tags baseado no enunciado e contexto."""
        tags = []
        
        # Tags do conceito (limpas)
        concept_clean = conceito.split('-', 1)[-1].replace('_', ' ')
        tags.append(conceito.split('-', 1)[-1])
        
        # Tags do tipo
        if tipo != 'desenvolvimento':
            tags.append(tipo.replace('_', ' '))
        
        # Palavras-chave matemáticas comuns
        math_keywords = {
            'função': 'funcoes',
            'inversa': 'inversa',
            'derivada': 'derivadas',
            'limite': 'limites',
            'integral': 'integrais',
            'gráfico': 'grafico',
            'exponencial': 'exponencial',
            'logaritmo': 'logaritmos',
            'polinomial': 'polinomial',
            'linear': 'funcao_linear',
            'quadrática': 'funcao_quadratica',
            'cálculo': 'calculo',
            'álgebra': 'algebra'
        }
        
        enunciado_lower = enunciado.lower()
        for palavra, tag in math_keywords.items():
            if palavra in enunciado_lower and tag not in tags:
                tags.append(tag)
        
        return tags[:5]  # Máximo 5 tags


class MinimalExerciseTemplate:
    """Template mínimo para criação rápida de exercícios."""
    
    MINIMAL_TEMPLATE = """% ====================================================================
% ⚡ TEMPLATE MÍNIMO DE EXERCÍCIO ⚡
% ====================================================================
%
% 📝 PREENCHA APENAS 3 CAMPOS:
%   1. Módulo (obrigatório)
%   2. Conceito (obrigatório)
%   3. Enunciado (obrigatório)
%
% ⚠️ ATENÇÃO À ESTRUTURA:
%   ✅ Enunciado DENTRO de \\exercicio{...}
%   ✅ Alíneas FORA, cada uma em \\subexercicio{...}
%   ✅ APAGAR texto de exemplo antes de salvar!
%
% ====================================================================

% ──────────────────────────────────────────────────────────────────
% 1️⃣ MÓDULO (obrigatório)
% ──────────────────────────────────────────────────────────────────
% Módulo: P4_funcoes
%   ↳ Exemplos: P4_funcoes, P2_estatistica, A9_funcoes_crescimento

% ──────────────────────────────────────────────────────────────────
% 2️⃣ CONCEITO (obrigatório)
% ──────────────────────────────────────────────────────────────────
% Conceito: 4-funcao_inversa
%   ↳ Formato: numero-nome_conceito
%   ↳ Exemplos: 4-funcao_inversa, 0-revisoes, 1-Medicoes_basicas

% ──────────────────────────────────────────────────────────────────
% ⚙️ OPCIONAIS (deixe vazio = inferência automática)
% ──────────────────────────────────────────────────────────────────
% Tipo: 
% Dificuldade: 
% Tags: 

% ──────────────────────────────────────────────────────────────────
% 3️⃣ ENUNCIADO (obrigatório)
% ──────────────────────────────────────────────────────────────────
%
% ⚠️ REGRAS IMPORTANTES:
%
% ✅ CORRETO - Enunciado simples:
%    \\exercicio{
%    Determine a função inversa de $f(x) = 2x + 3$.
%    }
%
% ✅ CORRETO - Com tabela:
%    \\exercicio{
%    A tabela mostra vendas de fruta:
%    
%    \\begin{center}
%    \\begin{tabular}{|l|c|}
%    \\hline
%    Fruta & Quantidade \\\\
%    \\hline
%    Maçãs & 45 \\\\
%    Peras & 30 \\\\
%    \\hline
%    \\end{tabular}
%    \\end{center}
%    }
%
% ✅ CORRETO - Alíneas separadas:
%    \\exercicio{
%    Considere a função $f(x) = x^2 - 4$.
%    }
%    
%    \\subexercicio{Calcule $f(2)$.}
%    
%    \\subexercicio{Determine os zeros da função.}
%
% ❌ ERRADO - Alíneas dentro do \\exercicio{}:
%    \\exercicio{
%    Considere...
%    \\subexercicio{...}  ← NÃO!
%    }
%
% ❌ ERRADO - Chavetas não fechadas:
%    \\begin{tabular}{|l|c|}
%    ...
%    \\end{tabular  ← FALTA "}"!
%
% ──────────────────────────────────────────────────────────────────

\\exercicio{
Determine a função inversa de $f(x) = 2x + 3$.
}

\\subexercicio{Verifique que $f(f^{-1}(x)) = x$.}

% ====================================================================
% ✅ CHECKLIST ANTES DE SALVAR:
%   [ ] Preenchi Módulo e Conceito
%   [ ] Escrevi o enunciado dentro de \\exercicio{...}
%   [ ] Todas as chavetas "{" têm o seu "}" correspondente
%   [ ] Apaguei ou adaptei o texto de exemplo
%   [ ] Alíneas estão em \\subexercicio{...} FORA do \\exercicio{}
% ====================================================================
"""

    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.temp_file = None
        self.config = self.load_config()
        self.inference = ExerciseInference()
        
    def load_config(self) -> Dict:
        """Carrega configuração de módulos."""
        config_path = self.base_path / "modules_config.yaml"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)

        # Fallback: use repository-level modules_config.yaml if present
        repo_config = Path(__file__).parent.parent / "modules_config.yaml"
        if repo_config.exists():
            with open(repo_config, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)

        # No config found - raise to surface the issue to the caller/tests
        raise FileNotFoundError(f"modules_config.yaml not found in {self.base_path} or repository root")
    
    def create_minimal_template(self, prefill: Optional[Dict] = None) -> Path:
        """Cria template mínimo."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_dir = Path(tempfile.gettempdir()) / f"exercise_minimal_{timestamp}"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        self.temp_file = temp_dir / "NOVO_EXERCICIO_MINIMO.tex"
        
        template_content = self.MINIMAL_TEMPLATE
        
        if prefill:
            for key, value in prefill.items():
                if value:  # Só substitui se tiver valor
                    pattern = f"% {key}: .*"
                    replacement = f"% {key}: {value}"
                    template_content = re.sub(pattern, replacement, template_content)
        
        with open(self.temp_file, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        return self.temp_file
    
    def open_for_editing(self) -> bool:
        """Abre template e config para edição."""
        if not self.temp_file:
            return False
        
        print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}⚡ TEMPLATE MÍNIMO - Criação Rápida{Colors.END}")
        print(f"{Colors.CYAN}{'='*70}{Colors.END}\n")
        print(f"{Colors.YELLOW}➤ Template:{Colors.END} {Colors.BOLD}{self.temp_file}{Colors.END}")
        
        # Abrir modules_config.yaml para referência
        config_path = self.base_path / "modules_config.yaml"
        if config_path.exists():
            print(f"{Colors.YELLOW}➤ Configuração:{Colors.END} {Colors.BOLD}{config_path}{Colors.END}")
        
        print(f"\n{Colors.GREEN}{Colors.BOLD}⚡ PREENCHA APENAS 3 CAMPOS:{Colors.END}")
        print(f"  1. {Colors.BOLD}Módulo{Colors.END} (ex: P4_funcoes)")
        print(f"  2. {Colors.BOLD}Conceito{Colors.END} (ex: 4-funcao_inversa)")
        print(f"  3. {Colors.BOLD}Enunciado{Colors.END} do exercício")
        print(f"\n{Colors.CYAN}🤖 O resto é inferido automaticamente!{Colors.END}\n")
        print(f"{Colors.CYAN}{'='*70}{Colors.END}\n")
        
        try:
            os.startfile(str(self.temp_file))
            
            if config_path.exists():
                time.sleep(0.5)
                os.startfile(str(config_path))
            
            print(f"{Colors.YELLOW}⏳ Aguardando edição...{Colors.END}\n")
            return True
        except Exception as e:
            print(f"{Colors.RED}Erro ao abrir ficheiros: {e}{Colors.END}")
            return False
    
    def wait_for_edit(self) -> bool:
        """Aguarda utilizador terminar edição."""
        input(f"{Colors.GREEN}Pressione [Enter] quando terminar a edição...{Colors.END} ")
        
        if not self.temp_file.exists():
            return False
        
        # Verificar se foi modificado
        with open(self.temp_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se tem conteúdo mínimo
        if '\\exercicio{' not in content or len(content) < 500:
            response = input(f"\n{Colors.YELLOW}⚠️ Ficheiro parece vazio. Continuar? (s/n): {Colors.END}").strip().lower()
            return response in ['s', 'sim', 'y', 'yes']
        
        return True
    
    def _extract_balanced_braces(self, text: str, start_pos: int) -> str:
        """Extrai conteúdo entre chavetas balanceadas a partir de start_pos.
        
        Args:
            text: Texto completo
            start_pos: Posição do '{' inicial
            
        Returns:
            Conteúdo entre as chavetas (sem incluir as próprias chavetas)
        """
        if start_pos >= len(text) or text[start_pos] != '{':
            return "", False

        depth = 0
        i = start_pos

        while i < len(text):
            char = text[i]

            # Ignorar chavetas escapadas
            if i > 0 and text[i-1] == '\\':
                i += 1
                continue

            if char == '{':
                depth += 1
            elif char == '}':
                depth -= 1

                # Encontramos o fecho correspondente
                if depth == 0:
                    return text[start_pos + 1:i], True

            i += 1

        # Chavetas não fechadas
        return text[start_pos + 1:], False
    
    def parse_minimal_template(self) -> Tuple[bool, Dict, List[str]]:
        """Parse do template mínimo com inferência."""
        if not self.temp_file or not self.temp_file.exists():
            return False, {}, ["Template não encontrado"]
        
        with open(self.temp_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        errors = []
        data = {}
        
        # 1. CAMPOS OBRIGATÓRIOS
        modulo_match = re.search(r'% Módulo:\s*(.+)', content)
        conceito_match = re.search(r'% Conceito:\s*(.+)', content)
        
        # Extrair enunciado - usar contagem de chavetas balanceadas
        exercicio_start = content.find('\\exercicio{')
        if exercicio_start == -1:
            errors.append("Enunciado (\\exercicio{...}) é obrigatório")
            enunciado_content = ""
        else:
            # Encontrar a posição do '{' após \exercicio
            brace_pos = exercicio_start + len('\\exercicio')
            enunciado_content, closed = self._extract_balanced_braces(content, brace_pos)

            if not closed:
                errors.append("Chavetas não fechadas no enunciado (\\exercicio{...})")

            if not enunciado_content or enunciado_content.strip() == '':
                errors.append("Enunciado (\\exercicio{...}) está vazio")
        
        if not modulo_match or not modulo_match.group(1).strip():
            errors.append("Campo 'Módulo' é obrigatório")
        else:
            data['módulo'] = modulo_match.group(1).strip()
        
        if not conceito_match or not conceito_match.group(1).strip():
            errors.append("Campo 'Conceito' é obrigatório")
        else:
            data['conceito'] = conceito_match.group(1).strip()
        
        if enunciado_content:
            # Consider common placeholders as empty (e.g., '...','TODO')
            enunciado_clean = enunciado_content.strip()
            if enunciado_clean.lower() in ['...', 'todo'] or re.fullmatch(r"\.*", enunciado_clean):
                # Treat as empty to force user correction
                errors.append("Enunciado (\\exercicio{...}) parece conter apenas um placeholder")
            else:
                data['enunciado'] = enunciado_clean
        
        if errors:
            return False, data, errors
        
        # 2. INFERIR DISCIPLINA do módulo
        modulo_id = data['módulo']
        disciplina = None
        for disc, modules in self.config.items():
            if modulo_id in modules:
                disciplina = disc
                break
        
        if not disciplina:
            errors.append(f"Módulo '{modulo_id}' não encontrado em modules_config.yaml")
            return False, data, errors
        
        data['disciplina'] = disciplina
        
        # 3. CAMPOS OPCIONAIS (ou inferidos)
        tipo_match = re.search(r'% Tipo:\s*(.+)', content)
        if tipo_match:
            tipo_value = tipo_match.group(1).strip()
            # Ignorar se for comentário (começa com ↳ ou %) ou vazio
            if tipo_value and not tipo_value.startswith('↳') and not tipo_value.startswith('%'):
                data['tipo'] = tipo_value
            else:
                # INFERIR TIPO
                data['tipo'] = self.inference.infer_type(data['enunciado'], data['conceito'])
                data['tipo_inferido'] = True
        else:
            # INFERIR TIPO
            data['tipo'] = self.inference.infer_type(data['enunciado'], data['conceito'])
            data['tipo_inferido'] = True
        
        dificuldade_match = re.search(r'% Dificuldade:\s*(\d+)', content)
        if dificuldade_match:
            data['dificuldade'] = int(dificuldade_match.group(1))
        else:
            # INFERIR DIFICULDADE
            data['dificuldade'] = self.inference.infer_difficulty(data['enunciado'])
            data['dificuldade_inferida'] = True
        
        tags_match = re.search(r'% Tags:\s*(.+)', content)
        if tags_match:
            tags_value = tags_match.group(1).strip()
            # Ignorar se for comentário (começa com ↳ ou %) ou vazio
            if tags_value and not tags_value.startswith('↳') and not tags_value.startswith('%'):
                data['tags'] = [t.strip() for t in tags_value.split(',')]
            else:
                # INFERIR TAGS
                data['tags'] = self.inference.extract_tags(
                    data['enunciado'], 
                    data['conceito'],
                    data['tipo']
                )
                data['tags_inferidas'] = True
        else:
            # INFERIR TAGS
            data['tags'] = self.inference.extract_tags(
                data['enunciado'], 
                data['conceito'],
                data['tipo']
            )
            data['tags_inferidas'] = True
        
        # 4. DEFAULTS
        data['formato'] = self.inference.infer_format(data['enunciado'])
        data['autor'] = 'Professor'
        data['tem_solucao'] = False
        
        # 5. Extrair alíneas se existirem
        subalíneas = re.findall(r'\\subexercicio\{([^}]+)\}', content)
        if subalíneas:
            # Filtrar alíneas que sejam só placeholders
            cleaned = []
            for s in subalíneas:
                s_clean = re.sub(r'%.*', '', s).strip()
                if s_clean and not re.fullmatch(r"\.*", s_clean) and s_clean.lower() != 'todo':
                    cleaned.append(s_clean)
            if cleaned:
                data['subalíneas'] = cleaned
        
        return True, data, []
    
    def show_inferred_summary(self, data: Dict):
        """Mostra resumo com campos inferidos destacados."""
        print(f"\n{Colors.GREEN}{'='*70}{Colors.END}")
        print(f"{Colors.GREEN}{Colors.BOLD}✓ EXERCÍCIO VALIDADO COM SUCESSO!{Colors.END}")
        print(f"{Colors.GREEN}{'='*70}{Colors.END}\n")
        
        print(f"{Colors.CYAN}📋 Resumo:{Colors.END}\n")
        
        # Campos preenchidos
        print(f"  {Colors.BOLD}Módulo:{Colors.END} {data.get('módulo')}")
        print(f"  {Colors.BOLD}Conceito:{Colors.END} {data.get('conceito')}")
        print(f"  {Colors.BOLD}Disciplina:{Colors.END} {data.get('disciplina')} {Colors.CYAN}(inferida){Colors.END}")
        
        # Campos inferidos
        tipo_label = f"{data.get('tipo')}"
        if data.get('tipo_inferido'):
            tipo_label += f" {Colors.CYAN}(inferido){Colors.END}"
        print(f"  {Colors.BOLD}Tipo:{Colors.END} {tipo_label}")
        
        dif_label = f"{data.get('dificuldade')}/5"
        if data.get('dificuldade_inferida'):
            dif_label += f" {Colors.CYAN}(inferida){Colors.END}"
        print(f"  {Colors.BOLD}Dificuldade:{Colors.END} {dif_label}")
        
        print(f"  {Colors.BOLD}Formato:{Colors.END} {data.get('formato')}")
        
        tags_label = ', '.join(data.get('tags', []))
        if data.get('tags_inferidas'):
            tags_label += f" {Colors.CYAN}(inferidas){Colors.END}"
        print(f"  {Colors.BOLD}Tags:{Colors.END} {tags_label}")
        
        print(f"\n{Colors.YELLOW}💡 Campos inferidos automaticamente marcados em azul{Colors.END}")
        print(f"{Colors.GREEN}{'='*70}{Colors.END}\n")
    
    def cleanup(self):
        """Remove ficheiros temporários."""
        if self.temp_file and self.temp_file.exists():
            try:
                self.temp_file.unlink()
                if self.temp_file.parent.exists():
                    self.temp_file.parent.rmdir()
            except:
                pass
    
    def incorporate_exercise(self, data: Dict) -> bool:
        """Incorpora exercício na base de dados."""
        try:
            # Use shared helpers to generate id, save .tex and update metadata/index
            from exercise_utils import generate_next_id, save_tex_for_exercise, update_type_metadata, update_index, get_base_dir

            tipo_id = data['tipo']
            # Ensure the type directory and metadata exist (interactive if needed)
            from exercise_utils import generate_next_id, save_tex_for_exercise, update_type_metadata, update_index, get_base_dir, ensure_type_directory, preview_and_confirm

            tipo_path = ensure_type_directory(self.base_path, data['disciplina'], data['módulo'], data['conceito'], tipo_id)

            exercise_id = generate_next_id(data['disciplina'], data['módulo'], data['conceito'], data['tipo'], base_dir=self.base_path)
            print(f"{Colors.GREEN}✓ ID gerado: {exercise_id}{Colors.END}")

            # 3. Criar conteúdo LaTeX
            today = datetime.now().strftime("%Y-%m-%d")
            enunciado_texto = data['enunciado'].strip()

            latex_content = f"""% Exercise ID: {exercise_id}
% Module: {data.get('módulo_nome', data['módulo'])} | Concept: {data.get('conceito_nome', data['conceito'])}
% Type: {data['tipo']} | Difficulty: {data['dificuldade']}/5
% Tags: {', '.join(data.get('tags', []))}
% Author: {data.get('autor', 'Professor')} | Date: {today}

\\exercicio{{
{enunciado_texto}
}}
"""
            if 'subalíneas' in data:
                latex_content += "\n"
                for sub in data['subalíneas']:
                    latex_content += f"\\subexercicio{{{sub}}}\n"

            tex_file = save_tex_for_exercise(self.base_path, data['disciplina'], data['módulo'], data['conceito'], data['tipo'], exercise_id, latex_content)
            print(f"{Colors.GREEN}✓ Ficheiro criado: {tex_file.name}{Colors.END}")

            # update tipo metadata and global index
            exercise_meta = {
                'id': exercise_id,
                'created': today,
                'author': data.get('autor', 'Professor'),
                'classification': {
                    'difficulty': data['dificuldade'],
                    'tags': data.get('tags', [])
                }
            }

            update_type_metadata(self.base_path / data['disciplina'] / data['módulo'] / data['conceito'] / data['tipo'], exercise_id, exercise_meta)
            update_index(self.base_path, {'id': exercise_id, 'classification': {'discipline': data['disciplina'], 'module': data['módulo'], 'module_name': data.get('módulo_nome', data['módulo']), 'concept': data['conceito'], 'concept_name': data.get('conceito_nome', data['conceito']), 'tipo': data['tipo'], 'tipo_nome': data.get('tipo_nome', data['tipo']), 'tags': data.get('tags', []), 'difficulty': data['dificuldade']}, 'exercise_type': data.get('formato', 'desenvolvimento')}, str(tex_file.relative_to(self.base_path)))

            print(f"\n{Colors.GREEN}{Colors.BOLD}✅ EXERCÍCIO INCORPORADO COM SUCESSO!{Colors.END}")
            print(f"{Colors.CYAN}📍 Localização: {data['disciplina']}/{data['módulo']}/{data['conceito']}/{tipo_id}/{exercise_id}{Colors.END}\n")

            return True
            
        except Exception as e:
            print(f"\n{Colors.RED}❌ Erro ao incorporar: {e}{Colors.END}")
            import traceback
            traceback.print_exc()
            return False
    
    def generate_exercise_id(self, data: Dict) -> str:
        """Gera ID único para o exercício."""
        # Formato: MAT_P4FUNCOE_4FIN_ANA_001
        disc_abbr = data['disciplina'][:3].upper()
        
        # Módulo (primeiros 8 caracteres, sem separadores)
        module_clean = data['módulo'].replace('_', '').replace('-', '')[:8].upper()
        
        # Conceito (3-4 caracteres)
        concept_parts = data['conceito'].split('-')
        if len(concept_parts) > 1:
            concept_abbr = concept_parts[1][:4].upper()
        else:
            concept_abbr = data['conceito'][:4].upper()
        
        # Tipo (3 letras)
        tipo_abbr = ''.join([w[0].upper() for w in data['tipo'].split('_')])[:3]
        
        # Número sequencial
        tipo_path = self.base_path / data['disciplina'] / data['módulo'] / data['conceito'] / data['tipo']
        existing = list(tipo_path.glob(f"{disc_abbr}_{module_clean}_{concept_abbr}_{tipo_abbr}_*.tex"))
        next_num = len(existing) + 1
        
        return f"{disc_abbr}_{module_clean}_{concept_abbr}_{tipo_abbr}_{next_num:03d}"
    
    def update_global_index(self, exercise_id: str, data: Dict, tex_file: Path):
        """Atualiza index.json global."""
        index_file = self.base_path / "index.json"
        
        if index_file.exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                index = json.load(f)
        else:
            index = {
                "database_version": "3.0",
                "last_updated": "",
                "total_exercises": 0,
                "statistics": {
                    "by_module": {},
                    "by_difficulty": {},
                    "by_type": {}
                },
                "exercises": []
            }
        
        # Adicionar exercício
        module_name = self.config.get(data['disciplina'], {}).get(data['módulo'], {}).get('name', data['módulo'])
        
        concept_info = None
        concepts = self.config.get(data['disciplina'], {}).get(data['módulo'], {}).get('concepts', [])
        for c in concepts:
            if c['id'] == data['conceito']:
                concept_info = c
                break
        
        concept_name = concept_info['name'] if concept_info else data['conceito']
        
        exercise_entry = {
            "id": exercise_id,
            "path": str(tex_file.relative_to(self.base_path)).replace("\\", "/"),
            "module": data['módulo'],
            "module_name": module_name,
            "concept": data['conceito'],
            "concept_name": concept_name,
            "tipo": data['tipo'],
            "difficulty": data['dificuldade'],
            "type": data['formato'],
            "tags": data.get('tags', []),
            "points": 0
        }
        
        index["exercises"].append(exercise_entry)
        index["total_exercises"] = len(index["exercises"])
        index["last_updated"] = datetime.now().isoformat()
        
        # Atualizar estatísticas
        mod_name = module_name
        index["statistics"]["by_module"][mod_name] = index["statistics"]["by_module"].get(mod_name, 0) + 1
        
        diff_labels = {1: "Muito Fácil", 2: "Fácil", 3: "Médio", 4: "Difícil", 5: "Muito Difícil"}
        diff_label = diff_labels.get(data['dificuldade'], "Fácil")
        index["statistics"]["by_difficulty"][diff_label] = index["statistics"]["by_difficulty"].get(diff_label, 0) + 1
        
        tipo_nome = data.get('tipo_nome', data['tipo'].replace('_', ' ').title())
        index["statistics"]["by_type"][tipo_nome] = index["statistics"]["by_type"].get(tipo_nome, 0) + 1
        
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
        
        print(f"{Colors.GREEN}✓ Índice atualizado: {index['total_exercises']} exercícios{Colors.END}")


def main():
    """Função principal."""
    base_path = Path(__file__).parent.parent

    # Fix encoding for Windows PowerShell (apply only when running as script)
    if sys.platform == 'win32':
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
        except Exception:
            pass
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}  ⚡ SISTEMA MÍNIMO - Criação Rápida de Exercícios  {Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}\n")
    print(f"{Colors.GREEN}🎯 Preencha apenas 3 campos - O resto é automático!{Colors.END}\n")
    
    template = MinimalExerciseTemplate(base_path)
    
    # Valores pré-preenchidos (últimos usados ou defaults)
    prefill = {
        'Módulo': 'P4_funcoes',
        'Conceito': '4-funcao_inversa'
    }
    
    # 1. Criar template
    template.create_minimal_template(prefill=prefill)
    
    # 2. Abrir para edição
    if not template.open_for_editing():
        print(f"{Colors.RED}Falha ao abrir template{Colors.END}")
        return 1
    
    # 3. Aguardar edição
    if not template.wait_for_edit():
        print(f"{Colors.RED}Operação cancelada{Colors.END}")
        template.cleanup()
        return 1
    
    # 4. Parse e inferência
    success, data, errors = template.parse_minimal_template()
    
    if not success:
        print(f"\n{Colors.RED}{'='*70}{Colors.END}")
        print(f"{Colors.RED}{Colors.BOLD}❌ ERROS ENCONTRADOS:{Colors.END}\n")
        for i, error in enumerate(errors, 1):
            print(f"{Colors.YELLOW}  {i}. {error}{Colors.END}")
        print(f"\n{Colors.RED}{'='*70}{Colors.END}\n")
        template.cleanup()
        return 1
    
    # 5. Mostrar resumo
    template.show_inferred_summary(data)
    
    # 6. Preview + confirmação (usa helper que tenta PreviewManager e fallback a input)
    from exercise_utils import preview_and_confirm

    today = datetime.now().strftime("%Y-%m-%d")
    enunciado_texto = data['enunciado'].strip()
    latex_content = f"""% Exercise preview (não guardado ainda)
% Module: {data.get('módulo')}
% Concept: {data.get('conceito')}
% Type: {data.get('tipo')}
% Difficulty: {data.get('dificuldade')}/5
% Tags: {', '.join(data.get('tags', []))}

\\exercicio{{
{enunciado_texto}
}}
"""
    if 'subalíneas' in data:
        latex_content += '\n'
        for sub in data['subalíneas']:
            latex_content += f"\\subexercicio{{{sub}}}\n"

    metadata_preview = {
        'módulo': data['módulo'],
        'conceito': data['conceito'],
        'disciplina': data['disciplina'],
        'tipo': data['tipo'],
        'dificuldade': data['dificuldade'],
        'tags': data.get('tags', []),
        'autor': data.get('autor', 'Professor')
    }

    confirmed = preview_and_confirm(latex_content, metadata_preview, title=f"Preview: {data.get('módulo')}/{data.get('conceito')}")
    if not confirmed:
        print(f"\n{Colors.YELLOW}Operação cancelada pelo utilizador (preview).{Colors.END}\n")
        template.cleanup()
        return 1

    # Incorporar na base de dados
    print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}💾 INCORPORANDO EXERCÍCIO...{Colors.END}")
    print(f"{Colors.CYAN}{'='*70}{Colors.END}\n")

    success = template.incorporate_exercise(data)

    if success:
        template.cleanup()
        return 0
    else:
        print(f"\n{Colors.RED}❌ Falha ao incorporar exercício{Colors.END}\n")
        template.cleanup()
        return 1


if __name__ == "__main__":
    sys.exit(main())
