import { tool } from "@opencode-ai/plugin"

export default tool({
  description: "Create a new intervention manifesto using create_intervention.py",
  args: {
    data: tool.schema.string().optional().describe("Date in YYYY-MM-DD format, defaults to today"),
    contexto: tool.schema.string().describe("Context description of the intervention"),
    objetivo: tool.schema.string().describe("Concise objective to achieve"),
    todos: tool.schema.array(tool.schema.string()).describe("List of TODO items for the intervention")
  },
  async execute(args) {
    console.log(`[create-intervention] Starting execution with args:`, args);

    const pythonPath = ".venv/Scripts/python.exe"; // Use Python from venv
    const todosArgs = args.todos.map(todo => `--todo "${todo}"`).join(' ')
    const cmd = `${pythonPath} agents_manifestos/create_intervention.py --data "${args.data || ''}" --contexto "${args.contexto}" --objetivo "${args.objetivo}" ${todosArgs}`

    console.log(`[create-intervention] Command to execute: ${cmd}`);

    try {
      const result = await Bun.$`${cmd}`.text()
      console.log(`[create-intervention] Python script output: ${result}`);
      return result.trim()
    } catch (error) {
      console.log(`[create-intervention] Python script failed with error:`, error);
      throw error;
    }
  },
})