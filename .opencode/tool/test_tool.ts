// .opencode/tool/test_tool.ts
import { tool } from "@opencode-ai/plugin"

export default tool({
  description: "Ferramenta de teste simples",
  args: {
    message: tool.schema.string().describe("Mensagem de teste"),
  },
  async execute(args, context) {
    return `Teste: ${args.message}`;
  },
})