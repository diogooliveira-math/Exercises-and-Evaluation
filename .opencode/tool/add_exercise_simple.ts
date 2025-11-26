// .opencode/tool/add_exercise_simple.ts
import { tool } from "@opencode-ai/plugin"

export default tool({
  description: "Adiciona um exercício simples à base de dados. Versão simplificada para agentes.",
  args: {
    discipline: tool.schema.string().describe("Disciplina (ex: matematica)").default("matematica"),
    module: tool.schema.string().describe("Módulo (ex: A8_modelos_discretos)"),
    concept: tool.schema.string().describe("Conceito (ex: 1-sistemas_numericos)"),
    tipo: tool.schema.string().describe("Tipo de exercício (ex: numeros_figurados)"),
    statement: tool.schema.string().describe("Enunciado do exercício"),
    difficulty: tool.schema.number().describe("Dificuldade (1-5)").default(3),
  },
  async execute(args, context) {
    if (!args) {
      throw new Error("Argumentos não fornecidos");
    }

    // Comando direto e simples
    const cmd = [
      "python",
      "ExerciseDatabase/_tools/add_exercise_simple.py",
      args.discipline,
      args.module,
      args.concept,
      args.tipo,
      args.difficulty.toString(),
      JSON.stringify(args.statement)
    ];

    const result = await Bun.$`${cmd}`.text();
    return result.trim();
  },
})