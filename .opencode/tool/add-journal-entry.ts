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

    const candidates = []
    const execPath = process.execPath || 'node'
    if (/python/i.test(execPath)) candidates.push(execPath)
    candidates.push('.venv\\Scripts\\python.exe', '.venv/bin/python', process.env.PYTHON_EXECUTABLE || '', 'python', 'python3', 'py')

    const script = 'agents_manifestos/add_journal_entry.py'
    if (!require('fs').existsSync(script)) {
      throw new Error(`Expected script not found at ${script}`)
    }

    const spawn = require('child_process').spawnSync

    let lastErr = null
    for (const p of candidates) {
      if (!p) continue
      try {
        console.log(`[add-journal-entry] Trying python executable: ${p}`)
        const argsArr = [script, '--entry', `${args.entry || ''}`]
        if (args.category) argsArr.push('--category', `${args.category}`)
        if (Array.isArray(args.tags)) {
          for (const t of args.tags) argsArr.push('--tag', t)
        }
        const res = spawn(p, argsArr, { encoding: 'utf8', timeout: 120000 })
        if (res.error) throw res.error
        if (res.status !== 0) {
          lastErr = new Error(`Exit ${res.status}: ${res.stderr || ''}`)
          continue
        }
        console.log(`[add-journal-entry] Python script output: ${res.stdout}`)
        return (res.stdout || '').trim()
      } catch (e) {
        lastErr = e
        continue
      }
    }

    throw lastErr || new Error('Failed to invoke Python runner')
  },
})