// .opencode/tool/add_exercise_with_types.ts
import { tool } from "@opencode-ai/plugin"

export default tool({
  description: "Adiciona um exercício à base de dados ExerciseDatabase com tipos pré-definidos de forma não interativa. Usa o script Python localizado em add_exercise_with_types_non_interactive.py para inserir exercícios seguindo a hierarquia disciplina/módulo/conceito/tipo/.",
  args: {
    discipline: tool.schema.string().describe("ID da disciplina (ex: matematica)"),
    module: tool.schema.string().describe("ID do módulo (ex: P4_funcoes)"),
    concept: tool.schema.string().describe("ID do conceito (ex: 4-funcao_inversa)"),
    tipo: tool.schema.string().describe("ID do tipo de exercício (ex: determinacao_analitica)"),
    statement: tool.schema.string().describe("Enunciado principal do exercício em português"),
    difficulty: tool.schema.number().describe("Nível de dificuldade (1-5, onde 1=fácil, 5=difícil)").default(3),
    author: tool.schema.string().describe("Nome do autor do exercício").default("Professor"),
    format: tool.schema.string().describe("Formato do exercício (ex: standard)").default("standard"),
    additional_tags: tool.schema.array(tool.schema.string()).describe("Lista de tags adicionais para categorização").default([]),
    subvariant_functions: tool.schema.array(tool.schema.string()).describe("Lista de funções para exercícios com sub-variants").default([]),
    has_parts: tool.schema.boolean().describe("Se o exercício tem múltiplas partes manuais").default(false),
    parts_count: tool.schema.number().describe("Número de partes se has_parts for true").default(0),
    solution: tool.schema.string().describe("Texto da solução em LaTeX (opcional)").optional(),
    skip_preview: tool.schema.boolean().describe("Se deve pular o sistema de preview").default(false),
  },
  async execute(args, context) {
    // Verificar se args foi passado corretamente
    if (!args) {
      throw new Error("Argumentos não fornecidos para add_exercise_with_types");
    }

    // Garantir que arrays tenham valores padrão se não definidos
    const safeArgs = {
      discipline: args.discipline,
      module: args.module,
      concept: args.concept,
      tipo: args.tipo,
      statement: args.statement,
      difficulty: args.difficulty || 3,
      author: args.author || "Professor",
      format: args.format || "standard",
      additional_tags: Array.isArray(args.additional_tags) ? args.additional_tags : [],
      subvariant_functions: Array.isArray(args.subvariant_functions) ? args.subvariant_functions : [],
      has_parts: Boolean(args.has_parts),
      parts_count: args.parts_count || 0,
      solution: args.solution,
      skip_preview: Boolean(args.skip_preview),
    };

    // Criar arquivo temporário com os argumentos
    const tempFile = `temp_exercise_args_${Date.now()}.json`;
    const tempFilePath = `c:\\Users\\diogo\\AAA\\Projects\\Exercises and Evaluation\\${tempFile}`;

    // Escrever argumentos em arquivo JSON
    const fs = await import("fs");
    await fs.promises.writeFile(tempFilePath, JSON.stringify(safeArgs, null, 2));

    // Construir comando simples que lê do arquivo
    const cmd = [
      "python",
      "ExerciseDatabase/_tools/add_exercise_with_types_non_interactive.py",
      `--config-file=${tempFilePath}`,
    ];

    try {
      // Invoca o script Python
      const result = await Bun.$`${cmd}`.text();
      return result.trim();
    } finally {
      // Limpar arquivo temporário
      try {
        await fs.promises.unlink(tempFilePath);
      } catch (e) {
        // Ignorar erro ao limpar arquivo
      }
    }
  },
})