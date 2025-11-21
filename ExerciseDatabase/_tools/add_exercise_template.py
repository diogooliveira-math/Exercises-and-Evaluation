#!/usr/bin/env python3
"""
Sistema de Adição de Exercícios por Template
==============================================

Workflow:
1. Gera template LaTeX pré-preenchido
2. Abre automaticamente no VS Code para edição
3. Utilizador edita o template diretamente
4. Sistema valida o template
5. Se válido: incorpora na base de dados
6. Se inválido: mostra erros e reabre para correção

Vantagens:
- Sem wizard interativo
- Edição visual direta
- Validação automática
- Feedback claro de erros
- Mais rápido para utilizadores experientes
"""

import json
import os
import sys
import io
import tempfile
import time
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple, List

# Ensure local _tools directory is on sys.path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Note: avoid changing sys.stdout/sys.stderr at import time; apply encoding fixes in main()

# Adicionar path para imports locais
sys.path.insert(0, str(Path(__file__).parent))

try:
    from preview_system import PreviewManager
except ImportError:
    PreviewManager = None

# Cores para terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


class ExerciseTemplate:
    """Gerencia templates de exercícios editáveis."""
    
    TEMPLATE = """% ====================================================================
% TEMPLATE DE EXERCÍCIO - Preencha os campos abaixo
% ====================================================================
%
% INSTRUÇÕES GERAIS:
% 1. Preencha TODOS os campos marcados com [OBRIGATÓRIO]
% 2. Escolha uma das opções listadas abaixo de cada campo
% 3. Mantenha o formato "Campo: valor"
% 4. Salve e feche o ficheiro quando terminar
%
% ────────────────────────────────────────────────────────────────────
% ⚙️ CONTROLE DE CRIAÇÃO DE NOVOS ELEMENTOS:
% ────────────────────────────────────────────────────────────────────
%
% ❌ NÃO PODE CRIAR:
%   • Disciplina  → Fixas: matematica, teste
%   • Módulo      → Deve existir em modules_config.yaml
%   • Conceito    → Deve existir no módulo em modules_config.yaml
%
% ✅ PODE CRIAR:
%   • Tipo        → Pode criar novo tipo diretamente aqui!
%
% 📝 Para adicionar Disciplina/Módulo/Conceito:
%    Edite: ExerciseDatabase/modules_config.yaml
%
% ====================================================================

% ──────────────────────────────────────────────────────────────────
% CLASSIFICAÇÃO [OBRIGATÓRIO]
% ──────────────────────────────────────────────────────────────────

% Disciplina: matematica
%   ↳ Opções FIXAS: matematica, teste
%   ⚠️ NÃO pode criar nova disciplina aqui
%   → Para adicionar disciplina: edite modules_config.yaml

% Módulo: A8_modelos_discretos
%   ↳ Opções EXISTENTES (só pode usar estas):
%     • A8_modelos_discretos (Modelos Discretos)
%     • A9_funcoes_crescimento (Funções de Crescimento)
%     • A10_funcoes (Funções)
%     • A11_derivadas (Derivadas)
%     • A12_otimizacao (Otimização)
%     • A13_limites (Limites e Continuidade)
%     • A14_integrais (Integrais)
%     • P4_funcoes (MÓDULO P4 - Funções)
%     • P1_modelos_matematicos_para_a_cidadania (Modelos Matemáticos)
%   ⚠️ NÃO pode criar novo módulo aqui
%   → Para adicionar módulo: edite modules_config.yaml

% Conceito: 1-sistemas_numericos
%   ↳ Opções EXISTENTES no módulo escolhido
%   ↳ Exemplos:
%     • A8_modelos_discretos: 1-sistemas_numericos, 2-numeros_figurados
%     • A9_funcoes_crescimento: 0-revisoes, 1-exponenciais
%     • P4_funcoes: 0-revisoes, 1-generalidades_funcoes, 4-funcao_inversa
%   ⚠️ NÃO pode criar novo conceito aqui
%   → Para adicionar conceito: edite modules_config.yaml

% Tipo: determinacao_valores
%   ↳ Pode ser NOVO ou EXISTENTE
%   ✅ PODE criar novo tipo diretamente aqui!
%   ↳ Se o tipo já existe, será reutilizado
%   ↳ Se não existe, será criado automaticamente
%   ↳ Formato: use snake_case (letras minúsculas com _)
%   ↳ Exemplos:
%     • determinacao_valores
%     • determinacao_analitica
%     • determinacao_grafica
%     • introducao_basica
%     • aplicacao_pratica
%     • calculo_direto
%     • teste_conceitual
%     • resolucao_problemas

% ──────────────────────────────────────────────────────────────────
% 📋 INFORMAÇÕES DO TIPO (se criar novo)
% ──────────────────────────────────────────────────────────────────
% Se o tipo NÃO existir, preencha também:

% TipoNome: Determinação de Valores
%   ↳ Nome legível do tipo
%   ↳ Use capitalização normal
%   ↳ Exemplo: "Determinação de Valores", "Introdução Básica"

% TipoDescricao: Traduzir diferentes sistemas numéricos uns nos outros
%   ↳ Breve descrição do que este tipo de exercício aborda
%   ↳ 1-2 frases explicativas
%   ↳ Exemplo: "Exercícios focados no cálculo da expressão analítica"

% TipoTags: conversao, traducao, representacao
%   ↳ Tags específicas deste tipo (separadas por vírgula)
%   ↳ Exemplo: calculo_analitico, expressao_analitica, algebra

% TipoRequerCalculo: sim
%   ↳ Este tipo requer cálculos? Opções: sim, nao

% TipoRequerGrafico: nao
%   ↳ Este tipo requer gráficos? Opções: sim, nao

% ──────────────────────────────────────────────────────────────────
% METADADOS DO EXERCÍCIO [OBRIGATÓRIO]
% ──────────────────────────────────────────────────────────────────

% Formato: desenvolvimento
%   ↳ Opções:
%     • desenvolvimento (Resposta aberta com resolução completa)
%     • escolha_multipla (4 opções com uma correta)
%     • verdadeiro_falso (Afirmações para classificar)
%     • resposta_curta (Resposta breve ou valor numérico)

% Dificuldade: 2
%   ↳ Opções:
%     • 1 (Muito Fácil - Aplicação direta de conceitos básicos)
%     • 2 (Fácil - Exercícios de consolidação simples)
%     • 3 (Médio - Requer compreensão sólida dos conceitos)
%     • 4 (Difícil - Problemas complexos, múltiplos conceitos)
%     • 5 (Muito Difícil - Desafios avançados, pensamento crítico)

% Autor: Professor
%   ↳ Seu nome ou "Professor" (padrão)

% ──────────────────────────────────────────────────────────────────
% TAGS [OPCIONAL]
% ──────────────────────────────────────────────────────────────────

% Tags: sistemas_numericos, binario, decimal
%   ↳ Separe por vírgula
%   ↳ Exemplos: funcoes, derivadas, limites, aplicacao, teoria

% ──────────────────────────────────────────────────────────────────
% SOLUÇÃO [OPCIONAL]
% ──────────────────────────────────────────────────────────────────

% TemSolucao: nao
%   ↳ Opções: sim, nao

% ====================================================================
% CONTEÚDO DO EXERCÍCIO [OBRIGATÓRIO]
% ====================================================================
% 
% COMANDOS LATEX DISPONÍVEIS:
% ───────────────────────────────────────────────────────────────────
% \\exercicio{...}           → Enunciado principal
% \\subexercicio{...}        → Alínea (a, b, c...)
% \\opcao{...}               → Opção de escolha múltipla
% 
% EXEMPLOS POR FORMATO:
% ───────────────────────────────────────────────────────────────────
% 
% [DESENVOLVIMENTO]
% \\exercicio{Calcule a derivada de $f(x) = x^2 + 3x$.}
% 
% [COM ALÍNEAS]
% \\exercicio{Converta para binário:}
% \\subexercicio{10}
% \\subexercicio{25}
% 
% [ESCOLHA MÚLTIPLA]
% \\exercicio{Qual é o valor de $2^3$?}
% \\opcao{6}
% \\opcao{8}  % ← Correta
% \\opcao{9}
% \\opcao{12}
% 
% [RESPOSTA CURTA]
% \\exercicio{Qual é a raiz quadrada de 144?}
% 
% ====================================================================

\\exercicio{
    % ← ESCREVA O ENUNCIADO AQUI
    % Pode usar LaTeX: $x^2$, \\frac{1}{2}, \\sqrt{x}, etc.
}

% ← SE TIVER ALÍNEAS, ADICIONE AQUI:
% \\subexercicio{Primeira alínea}
% \\subexercicio{Segunda alínea}

% ====================================================================
% SOLUÇÃO (se TemSolucao: sim)
% ====================================================================
% 
% Remova os % abaixo para adicionar a solução:
%
% \\solucao{
%     % ← ESCREVA A SOLUÇÃO AQUI
%     % Pode usar comandos LaTeX normalmente
% }

% ====================================================================
% FIM DO TEMPLATE
% ====================================================================
"""

    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.temp_file = None
        self.parsed_data = {}
        
    def create_template(self, prefill: Optional[Dict] = None) -> Path:
        """
        Cria template temporário pré-preenchido.
        
        Args:
            prefill: Dicionário com valores para pré-preencher
            
        Returns:
            Path para o ficheiro template
        """
        # Criar ficheiro temporário
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_dir = Path(tempfile.gettempdir()) / f"exercise_template_{timestamp}"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        self.temp_file = temp_dir / "NOVO_EXERCICIO.tex"
        
        # Template base ou pré-preenchido
        template_content = self.TEMPLATE
        
        if prefill:
            # Substituir valores no template
            for key, value in prefill.items():
                pattern = f"% {key}: .*"
                replacement = f"% {key}: {value}"
                template_content = re.sub(pattern, replacement, template_content)
        
        # Salvar template
        with open(self.temp_file, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        return self.temp_file
    
    def open_for_editing(self) -> bool:
        """Abre template no VS Code para edição."""
        if not self.temp_file:
            return False
        
        print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}📝 EDITANDO TEMPLATE DE EXERCÍCIO{Colors.END}")
        print(f"{Colors.CYAN}{'='*70}{Colors.END}\n")
        print(f"{Colors.YELLOW}➤ Template aberto:{Colors.END} {Colors.BOLD}{self.temp_file}{Colors.END}")
        
        # Abrir modules_config.yaml para referência
        config_path = self.base_path / "modules_config.yaml"
        if config_path.exists():
            print(f"{Colors.YELLOW}➤ Configuração aberta:{Colors.END} {Colors.BOLD}{config_path}{Colors.END}")
            print(f"{Colors.CYAN}   (Para consultar disciplinas/módulos/conceitos disponíveis){Colors.END}")
        
        print(f"\n{Colors.CYAN}Instruções:{Colors.END}")
        print(f"  1. Preencha todos os campos [OBRIGATÓRIO]")
        print(f"  2. Consulte {Colors.BOLD}modules_config.yaml{Colors.END} para opções válidas")
        print(f"  3. Escreva o enunciado na seção CONTEÚDO DO EXERCÍCIO")
        print(f"  4. {Colors.BOLD}Salve e feche ambos os ficheiros{Colors.END} quando terminar")
        print(f"  5. O sistema irá validar automaticamente\n")
        print(f"{Colors.CYAN}{'='*70}{Colors.END}\n")
        
        # Tentar abrir em VS Code
        try:
            os.startfile(str(self.temp_file))
            
            # Abrir também modules_config.yaml
            if config_path.exists():
                time.sleep(0.5)  # Pequeno delay para não sobrepor janelas
                os.startfile(str(config_path))
            
            # Aguardar que utilizador edite
            print(f"{Colors.YELLOW}⏳ Aguardando edição...{Colors.END}")
            print(f"{Colors.CYAN}(O sistema detectará automaticamente quando você salvar e fechar){Colors.END}\n")
            
            return True
        except Exception as e:
            print(f"{Colors.RED}❌ Erro ao abrir ficheiro: {e}{Colors.END}")
            print(f"{Colors.YELLOW}📂 Abra manualmente: {self.temp_file}{Colors.END}")
            return False
    
    def wait_for_edit(self, timeout: int = 300) -> bool:
        """
        Aguarda que utilizador edite e salve o ficheiro.
        
        Args:
            timeout: Tempo máximo de espera em segundos (padrão: 5 minutos)
            
        Returns:
            True se ficheiro foi modificado
        """
        if not self.temp_file or not self.temp_file.exists():
            return False
        
        initial_mtime = self.temp_file.stat().st_mtime
        start_time = time.time()
        
        print(f"{Colors.CYAN}Pressione [Enter] quando terminar a edição...{Colors.END}", end='', flush=True)
        
        try:
            input()  # Aguardar Enter
            
            # Verificar se ficheiro foi modificado
            if self.temp_file.stat().st_mtime > initial_mtime:
                print(f"\n{Colors.GREEN}✓ Ficheiro editado e salvo{Colors.END}\n")
                return True
            else:
                print(f"\n{Colors.YELLOW}⚠️ Ficheiro não foi modificado{Colors.END}")
                retry = input(f"{Colors.CYAN}Deseja continuar mesmo assim? (s/n): {Colors.END}").strip().lower()
                return retry in ['s', 'sim', 'y', 'yes']
                
        except KeyboardInterrupt:
            print(f"\n\n{Colors.RED}❌ Operação cancelada pelo utilizador{Colors.END}")
            return False
    
    def parse_template(self) -> Tuple[bool, Dict, List[str]]:
        """
        Faz parsing do template editado.
        
        Returns:
            Tupla (sucesso, dados_parseados, lista_de_erros)
        """
        if not self.temp_file or not self.temp_file.exists():
            return False, {}, ["Ficheiro template não encontrado"]
        
        # Ler conteúdo
        with open(self.temp_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        errors = []
        data = {}
        
        # Extrair campos obrigatórios
        required_fields = {
            'Disciplina': r'% Disciplina:\s*(.+)',
            'Módulo': r'% Módulo:\s*(.+)',
            'Conceito': r'% Conceito:\s*(.+)',
            'Tipo': r'% Tipo:\s*(.+)',
            'Formato': r'% Formato:\s*(.+)',
            'Dificuldade': r'% Dificuldade:\s*(\d+)',
            'Autor': r'% Autor:\s*(.+)'
        }
        
        for field, pattern in required_fields.items():
            match = re.search(pattern, content)
            if match:
                data[field.lower()] = match.group(1).strip()
            else:
                errors.append(f"Campo obrigatório ausente: {field}")
        
        # Extrair tags (opcional)
        tags_match = re.search(r'% Tags:\s*(.+)', content)
        if tags_match:
            tags_str = tags_match.group(1).strip()
            data['tags'] = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
        else:
            data['tags'] = []
        
        # Extrair TemSolucao (opcional)
        solucao_match = re.search(r'% TemSolucao:\s*(.+)', content)
        data['tem_solucao'] = solucao_match.group(1).strip().lower() == 'sim' if solucao_match else False
        
        # Extrair conteúdo LaTeX do exercício
        exercicio_pattern = r'\\exercicio\{(.*?)\}'
        exercicio_match = re.search(exercicio_pattern, content, re.DOTALL)
        
        if exercicio_match:
            data['conteudo'] = exercicio_match.group(0).strip()
            
            # Verificar se tem conteúdo real
            conteudo_limpo = exercicio_match.group(1)
            # Remover comentários e espaços
            conteudo_limpo = re.sub(r'%.*', '', conteudo_limpo)
            conteudo_limpo = conteudo_limpo.strip()

            # Tratar placeholders comuns como vazios (ex.: '...', 'TODO', templates deixadas por engano)
            if (not conteudo_limpo
                or conteudo_limpo.lower() == '% escreva o enunciado aqui'
                or re.fullmatch(r"\.*", conteudo_limpo)
                or conteudo_limpo.lower() in ['...', 'todo']):
                errors.append("Enunciado do exercício está vazio")
        else:
            errors.append("Comando \\exercicio{} não encontrado ou mal formatado")
        
        # Extrair subexercícios se existirem e filtrar placeholders
        subexercicios = re.findall(r'\\subexercicio\{(.*?)\}', content, re.DOTALL)
        if subexercicios:
            # Remover subexercícios que sejam apenas placeholders como '...'
            cleaned = []
            for s in subexercicios:
                s_clean = re.sub(r'%.*', '', s).strip()
                if s_clean and not re.fullmatch(r"\.*", s_clean) and s_clean.lower() != 'todo':
                    cleaned.append(s_clean)
            if cleaned:
                data['subexercicios'] = cleaned
                data['conteudo'] += '\n\n' + '\n\n'.join([f'\\subexercicio{{{s}}}' for s in cleaned])
        
        # Extrair solução se existir
        if data.get('tem_solucao'):
            solucao_pattern = r'\\solucao\{(.*?)\}'
            solucao_match = re.search(solucao_pattern, content, re.DOTALL)
            if solucao_match:
                data['solucao'] = solucao_match.group(0).strip()
            else:
                errors.append("TemSolucao=sim mas comando \\solucao{} não encontrado")
        
        # Validar dificuldade
        if 'dificuldade' in data:
            try:
                dif = int(data['dificuldade'])
                if not 1 <= dif <= 5:
                    errors.append("Dificuldade deve estar entre 1 e 5")
            except ValueError:
                errors.append("Dificuldade deve ser um número inteiro")
        
        # Validar formato
        valid_formats = ['desenvolvimento', 'escolha_multipla', 'verdadeiro_falso', 'resposta_curta']
        if 'formato' in data and data['formato'] not in valid_formats:
            errors.append(f"Formato inválido. Use um de: {', '.join(valid_formats)}")
        
        self.parsed_data = data
        return len(errors) == 0, data, errors
    
    def show_validation_errors(self, errors: List[str]) -> bool:
        """
        Mostra erros de validação e pergunta se quer reeditar.
        
        Args:
            errors: Lista de erros encontrados
            
        Returns:
            True se utilizador quer reeditar
        """
        print(f"\n{Colors.RED}{'='*70}{Colors.END}")
        print(f"{Colors.RED}{Colors.BOLD}❌ ERROS DE VALIDAÇÃO ENCONTRADOS{Colors.END}")
        print(f"{Colors.RED}{'='*70}{Colors.END}\n")
        
        for i, error in enumerate(errors, 1):
            print(f"{Colors.YELLOW}  {i}. {error}{Colors.END}")
        
        print(f"\n{Colors.CYAN}{'='*70}{Colors.END}\n")
        
        response = input(f"{Colors.YELLOW}Deseja reeditar o template? (s/n): {Colors.END}").strip().lower()
        return response in ['s', 'sim', 'y', 'yes']
    
    def show_success(self, data: Dict):
        """Mostra resumo do exercício validado."""
        print(f"\n{Colors.GREEN}{'='*70}{Colors.END}")
        print(f"{Colors.GREEN}{Colors.BOLD}✓ TEMPLATE VALIDADO COM SUCESSO!{Colors.END}")
        print(f"{Colors.GREEN}{'='*70}{Colors.END}\n")
        
        print(f"{Colors.CYAN}Resumo do Exercício:{Colors.END}\n")
        print(f"  {Colors.BOLD}Disciplina:{Colors.END} {data.get('disciplina', 'N/A')}")
        print(f"  {Colors.BOLD}Módulo:{Colors.END} {data.get('módulo', 'N/A')}")
        print(f"  {Colors.BOLD}Conceito:{Colors.END} {data.get('conceito', 'N/A')}")
        print(f"  {Colors.BOLD}Tipo:{Colors.END} {data.get('tipo', 'N/A')}")
        print(f"  {Colors.BOLD}Formato:{Colors.END} {data.get('formato', 'N/A')}")
        print(f"  {Colors.BOLD}Dificuldade:{Colors.END} {data.get('dificuldade', 'N/A')}/5")
        print(f"  {Colors.BOLD}Tags:{Colors.END} {', '.join(data.get('tags', []))}")
        print(f"  {Colors.BOLD}Tem Solução:{Colors.END} {'Sim' if data.get('tem_solucao') else 'Não'}")
        print(f"\n{Colors.GREEN}{'='*70}{Colors.END}\n")
    
    def cleanup(self):
        """Remove ficheiros temporários."""
        if self.temp_file and self.temp_file.exists():
            try:
                self.temp_file.unlink()
                if self.temp_file.parent.exists():
                    self.temp_file.parent.rmdir()
            except:
                pass


def main():
    """Função principal."""
    base_path = Path(__file__).parent.parent

    # Fix encoding for Windows PowerShell (only when executed as script)
    if sys.platform == 'win32':
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
        except Exception:
            pass  # continue with default encoding
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}  📝 SISTEMA DE EXERCÍCIOS POR TEMPLATE  {Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}\n")
    
    template = ExerciseTemplate(base_path)
    
    # Valores pré-preenchidos (podem vir de argumentos CLI no futuro)
    prefill = {
        'Disciplina': 'matematica',
        'Módulo': 'A8_modelos_discretos',
        'Conceito': '1-sistemas_numericos',
        'Tipo': 'determinacao_valores',
        'Formato': 'desenvolvimento',
        'Dificuldade': '2',
        'Autor': 'Professor'
    }
    
    # 1. Criar template
    template_path = template.create_template(prefill=prefill)
    
    # 2. Abrir para edição
    if not template.open_for_editing():
        print(f"{Colors.RED}Falha ao abrir template{Colors.END}")
        return 1
    
    # 3. Aguardar edição
    max_attempts = 3
    attempt = 0
    
    while attempt < max_attempts:
        attempt += 1
        
        if not template.wait_for_edit():
            print(f"{Colors.RED}Operação cancelada{Colors.END}")
            template.cleanup()
            return 1
        
        # 4. Validar template
        success, data, errors = template.parse_template()
        
        if success:
            # 5. Mostrar sucesso
            template.show_success(data)
            
            # 6. Confirmar incorporação
            response = input(f"{Colors.GREEN}Incorporar exercício na base de dados? (s/n): {Colors.END}").strip().lower()
            
            if response in ['s', 'sim', 'y', 'yes']:
                base = Path(__file__).parent.parent
                disciplina = data.get('disciplina')
                modulo = data.get('módulo')
                conceito = data.get('conceito')
                tipo = data.get('tipo')

                # Ensure type directory (may prompt interactively)
                from exercise_utils import ensure_type_directory, generate_next_id, save_tex_for_exercise, update_type_metadata, update_index, preview_and_confirm

                tipo_path = ensure_type_directory(base, disciplina, modulo, conceito, tipo)

                # Build latex content
                latex_content = data.get('conteudo', '')
                if data.get('subexercicios'):
                    latex_content += '\n\n' + '\n\n'.join([f"\\subexercicio{{{s}}}" for s in data['subexercicios']])

                # Preview + confirm
                metadata_preview = {
                    'id': None,
                    'classification': {
                        'discipline': disciplina,
                        'module': modulo,
                        'concept': conceito,
                        'tipo': tipo,
                        'tags': data.get('tags', []),
                        'difficulty': int(data.get('dificuldade', 2))
                    }
                }
                if not preview_and_confirm(latex_content, metadata_preview, title=f"Novo Exercício ({modulo}/{conceito})"):
                    print(f"\n{Colors.YELLOW}Operação cancelada pelo utilizador (preview).{Colors.END}\n")
                    template.cleanup()
                    return 1

                # Generate ID and save
                exercise_id = generate_next_id(disciplina, modulo, conceito, tipo, base_dir=base)
                tex_file = save_tex_for_exercise(base, disciplina, modulo, conceito, tipo, exercise_id, latex_content)

                exercise_meta = {
                    'created': datetime.now().strftime('%Y-%m-%d'),
                    'author': data.get('autor', 'Professor'),
                    'classification': {
                        'difficulty': int(data.get('dificuldade', 2)),
                        'tags': data.get('tags', [])
                    }
                }

                update_type_metadata(tipo_path, exercise_id, exercise_meta)
                rel_path = str(tex_file.relative_to(base)).replace('\\', '/')
                update_index(base, {'id': exercise_id, 'classification': {'discipline': disciplina, 'module': modulo, 'module_name': data.get('módulo', modulo), 'concept': conceito, 'concept_name': conceito, 'tipo': tipo, 'tipo_nome': tipo}, 'exercise_type': data.get('formato', 'desenvolvimento')}, rel_path)

                print(f"\n{Colors.GREEN}✓ Exercício salvo: {tex_file}{Colors.END}\n")
                template.cleanup()
                return 0
            else:
                print(f"{Colors.YELLOW}Operação cancelada{Colors.END}")
                template.cleanup()
                return 1
        else:
            # Mostrar erros e perguntar se quer reeditar
            if template.show_validation_errors(errors):
                print(f"\n{Colors.CYAN}Reabrindo template para correção...{Colors.END}\n")
                template.open_for_editing()
            else:
                print(f"{Colors.RED}Operação cancelada{Colors.END}")
                template.cleanup()
                return 1
    
    print(f"\n{Colors.RED}Número máximo de tentativas ({max_attempts}) atingido{Colors.END}")
    template.cleanup()
    return 1


if __name__ == "__main__":
    sys.exit(main())
