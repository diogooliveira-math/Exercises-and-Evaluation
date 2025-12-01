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

    const todosArgs = Array.isArray(args.todos) ? args.todos.map(todo => `--todo"${todo}"`).join(' ') : ''
    // Prefer node process.execPath for Python if it points to a Python binary, else try common names
    const candidates = []
    const execPath = process.execPath || 'node'
    // If execPath looks like python, prefer it
    if (/python/i.test(execPath)) candidates.push(execPath)
    // venv paths
    const venvWin = '.venv\\Scripts\\python.exe'
    const venvPosix = '.venv/bin/python'
    candidates.push(venvWin, venvPosix, process.env.PYTHON_EXECUTABLE || '', 'python', 'python3', 'py')

    const script = 'agents_manifestos/create_intervention.py'
    if (!require('fs').existsSync(script)) {
      throw new Error(`Expected script not found at ${script}`)
    }

    const spawn = require('child_process').spawnSync
    let lastErr = null
    for (const p of candidates) {
      if (!p) continue
      try {
        console.log(`[create-intervention] Trying python executable: ${p}`)
        const argsArr = [script, '--data', `${args.data || ''}`, '--contexto', `${args.contexto}`, '--objetivo', `${args.objetivo}`]
        if (Array.isArray(args.todos)) {
          for (const t of args.todos) argsArr.push('--todo', t)
        }
        const res = spawn(p, argsArr, { encoding: 'utf8', timeout: 120000 })
        if (res.error) throw res.error
        if (res.status !== 0) {
          lastErr = new Error(`Exit ${res.status}: ${res.stderr || ''}`)
          continue
        }
        console.log(`[create-intervention] Python script output: ${res.stdout}`)
        return (res.stdout || '').trim()
      } catch (e) {
        lastErr = e
        continue
      }
    }

    throw lastErr || new Error('Failed to invoke Python runner')
  },
})