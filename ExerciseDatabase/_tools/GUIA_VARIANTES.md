═══════════════════════════════════════════════════════════════════
🔄 GERADOR DE VARIANTES DE EXERCÍCIOS
═══════════════════════════════════════════════════════════════════

O que é?
--------
Sistema para criar variações de exercícios existentes de forma rápida,
mantendo a estrutura base e alterando valores/contexto.

═══════════════════════════════════════════════════════════════════
🎯 COMO USAR
═══════════════════════════════════════════════════════════════════

MÉTODO 1: Via Task VS Code (RECOMENDADO)
-----------------------------------------
1. Abrir ficheiro .tex do exercício original
2. Ctrl+Shift+P → "Tasks: Run Task"
3. Selecionar: "🔄 Gerar Variante de Exercício"
4. Confirmar quando solicitado
5. Editar a variante gerada

MÉTODO 2: Via Terminal
----------------------
python ExerciseDatabase/_tools/generate_variant.py --source "caminho/para/exercicio.tex"

# Com estratégia de variação
python ExerciseDatabase/_tools/generate_variant.py --source "exercicio.tex" --strategy auto

# Sem variação (cópia direta)
python ExerciseDatabase/_tools/generate_variant.py --source "exercicio.tex" --strategy none


═══════════════════════════════════════════════════════════════════
⚙️ ESTRATÉGIAS DE VARIAÇÃO
═══════════════════════════════════════════════════════════════════

auto (padrão)
-------------
• Incrementa números em expressões matemáticas ($...$)
• Exemplo: $f(x) = 2x + 3$ → $f(x) = 3x + 4$
• Seguro: Só altera números inteiros pequenos (-9 a 9)
• Preserva estrutura LaTeX

none
----
• Cópia direta sem alterações
• Útil quando queres fazer todas as alterações manualmente
• Mantém ID e metadados diferentes


═══════════════════════════════════════════════════════════════════
📋 O QUE O SISTEMA FAZ AUTOMATICAMENTE
═══════════════════════════════════════════════════════════════════

✅ Gera novo ID sequencial
   • Original: MAT_P4FUNCOE_4FIN_001
   • Variante: MAT_P4FUNCOE_4FIN_002

✅ Atualiza cabeçalho do .tex
   • % Exercise ID: MAT_P4FUNCOE_4FIN_002
   • % Date: 2025-11-21

✅ Mantém mesma localização
   • matematica/P4_funcoes/4-funcao_inversa/determinacao_analitica/

✅ Atualiza metadados
   • metadata.json do tipo (adiciona novo exercício)
   • index.json global (adiciona entrada)
   • Recalcula estatísticas

✅ Preserva contexto
   • Disciplina
   • Módulo
   • Conceito
   • Tipo
   • Dificuldade


═══════════════════════════════════════════════════════════════════
💡 BOAS PRÁTICAS
═══════════════════════════════════════════════════════════════════

1. Criar Variações Significativas
   ✅ Mudar valores numéricos
   ✅ Mudar contexto (história, situação)
   ✅ Mudar funções (f(x) = 2x + 3 → g(x) = x² - 1)
   ❌ Cópias quase idênticas

2. Manter Dificuldade Equivalente
   • Variantes devem ter dificuldade similar ao original
   • Se mudar dificuldade, atualizar metadados manualmente

3. Editar Após Gerar
   • Sistema cria base, mas SEMPRE reveja e edite
   • Variação automática é ponto de partida, não final

4. Testar Compilação
   • Verificar LaTeX compila corretamente
   • Validar estrutura com validate_exercise_structure.py


═══════════════════════════════════════════════════════════════════
🔍 EXEMPLO COMPLETO
═══════════════════════════════════════════════════════════════════

ORIGINAL (MAT_P4FUNCOE_4FIN_001.tex):
--------------------------------------
\exercicio{
Determine a função inversa de $f(x) = 2x + 3$.
}

\subexercicio{Calcule $f(5)$.}
\subexercicio{Verifique que $f(f^{-1}(x)) = x$.}


VARIANTE AUTOMÁTICA (MAT_P4FUNCOE_4FIN_002.tex):
-------------------------------------------------
\exercicio{
Determine a função inversa de $f(x) = 3x + 4$.
}

\subexercicio{Calcule $f(6)$.}
\subexercicio{Verifique que $f(f^{-1}(x)) = x$.}


VARIANTE EDITADA MANUALMENTE (versão final):
---------------------------------------------
\exercicio{
Determine a função inversa de $g(x) = 3x + 4$.
}

\subexercicio{Calcule $g(2)$ e $g^{-1}(10)$.}
\subexercicio{Verifique que $g(g^{-1}(x)) = x$ para $x = 10$.}


═══════════════════════════════════════════════════════════════════
⚠️ LIMITAÇÕES E AVISOS
═══════════════════════════════════════════════════════════════════

❌ Não altera:
   • Figuras/imagens
   • Gráficos TikZ (mantém iguais)
   • Tabelas de dados
   • Texto fora de $...$

❌ Variação automática limitada:
   • Só números pequenos (-9 a 9)
   • Só dentro de $...$
   • Não entende contexto matemático

⚠️ SEMPRE reveja e edite a variante gerada!


═══════════════════════════════════════════════════════════════════
📊 ESTATÍSTICAS E RASTREAMENTO
═══════════════════════════════════════════════════════════════════

Cada variante:
• Conta como exercício separado no index.json
• Mantém referência ao tipo original
• Aparece nas estatísticas por módulo/conceito
• Pode ser pesquisada independentemente

Para ver exercícios de um conceito:
python ExerciseDatabase/_tools/search_exercises.py


═══════════════════════════════════════════════════════════════════
🛠️ TROUBLESHOOTING
═══════════════════════════════════════════════════════════════════

ERRO: "ID inesperado"
---------------------
• ID do ficheiro original não segue formato esperado
• Deve terminar com 3 dígitos: XXX_YYY_ZZZ_001
• Solução: Renomear ficheiro original

ERRO: "Ficheiro não encontrado"
--------------------------------
• Caminho incorreto
• Solução: Usar caminho absoluto ou relativo correto

VARIANTE NÃO COMPILA
---------------------
• Variação automática pode ter quebrado LaTeX
• Solução: Usar --strategy none e editar manualmente

VARIANTE MUITO SIMILAR
-----------------------
• Variação automática limitada
• Solução: Editar manualmente após gerar


═══════════════════════════════════════════════════════════════════
📚 VER TAMBÉM
═══════════════════════════════════════════════════════════════════

• MINIMAL_SYSTEM_GUIDE.md - Sistema de criação rápida
• VSCODE_TASKS_GUIDE.md - Todas as tasks disponíveis
• validate_exercise_structure.py - Validar estrutura LaTeX

═══════════════════════════════════════════════════════════════════
