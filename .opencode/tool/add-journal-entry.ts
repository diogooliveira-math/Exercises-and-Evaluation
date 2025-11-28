import { tool } from "@opencode-ai/plugin"

export default tool({
  description: "Add a journal entry using add_journal_entry.py",
  args: {
    entry: tool.schema.string().describe("The journal entry content to add"),
    category: tool.schema.string().optional().describe("Category for the journal entry"),
    tags: tool.schema.array(tool.schema.string()).optional().describe("Tags for the journal entry")
  },
  async execute(args) {
    console.log(`[add-journal-entry] Starting execution with args:`, args);

    const pythonPath = ".venv/Scripts/python.exe"; // Use Python from venv
    const tagsArgs = args.tags ? args.tags.map(tag => `--tag "${tag}"`).join(' ') : ''
    const cmd = `${pythonPath} agents_manifestos/add_journal_entry.py --entry "${args.entry}" ${args.category ? `--category "${args.category}"` : ''} ${tagsArgs}`

    console.log(`[add-journal-entry] Command to execute: ${cmd}`);

    try {
      const result = await Bun.$`${cmd}`.text()
      console.log(`[add-journal-entry] Python script output: ${result}`);
      return result.trim()
    } catch (error) {
      console.log(`[add-journal-entry] Python script failed with error:`, error);
      throw error;
    }
  },
})