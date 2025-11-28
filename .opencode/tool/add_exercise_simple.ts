// .opencode/tool/add_exercise_simple.ts
import { tool } from "@opencode-ai/plugin"
import { spawn } from 'child_process'
import fs from 'fs'

function exists(path: string) {
  try { return fs.existsSync(path) } catch (e) { return false }
}

function runProcess(executable: string, args: string[], timeout = 120000) {
  return new Promise<{ stdout: string; stderr: string; code: number | null }>((resolve, reject) => {
    const proc = spawn(executable, args, { stdio: ['ignore', 'pipe', 'pipe'] })
    let stdout = ''
    let stderr = ''
    let finished = false

    const to = setTimeout(() => {
      if (!finished) {
        finished = true
        try { proc.kill() } catch (e) {}
        reject(new Error(`Process timed out after ${timeout}ms`))
      }
    }, timeout)

    proc.stdout?.on('data', (chunk) => { stdout += chunk.toString() })
    proc.stderr?.on('data', (chunk) => { stderr += chunk.toString() })

    proc.on('error', (err) => {
      if (finished) return
      finished = true
      clearTimeout(to)
      reject(err)
    })

    proc.on('close', (code) => {
      if (finished) return
      finished = true
      clearTimeout(to)
      resolve({ stdout: stdout.trim(), stderr: stderr.trim(), code })
    })
  })
}

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

  async execute(rawArgs, context) {
    // Lightweight validation
    if (!rawArgs || typeof rawArgs !== 'object') {
      throw new Error('Arguments must be an object')
    }

    const required = ['discipline', 'module', 'concept', 'tipo', 'statement']
    const missing = required.filter((k) => !rawArgs[k] && rawArgs[k] !== 0)
    if (missing.length) {
      return JSON.stringify({ status: 'error', error: 'missing_fields', missing, suggestion: 'Provide the missing fields' })
    }

    // Normalize and coerce types
    const discipline = String(rawArgs.discipline || 'matematica')
    const moduleName = String(rawArgs.module)
    const concept = String(rawArgs.concept)
    const tipo = String(rawArgs.tipo)
    const statement = String(rawArgs.statement)
    const difficulty = Number.isFinite(Number(rawArgs.difficulty)) ? Number(rawArgs.difficulty) : 3

    // Build payload as JSON to avoid shell/quoting issues
    const payload = { discipline, module: moduleName, concept, tipo, statement, difficulty }
    const payloadStr = JSON.stringify(payload)

    // Candidate Python executables (platform-aware)
    const candidates: string[] = []
    // Check for venv first (Windows and POSIX)
    const venvWin = '.venv\\Scripts\\python.exe'
    const venvPosix = '.venv/bin/python'
    if (exists(venvWin)) candidates.push(venvWin)
    if (exists(venvPosix)) candidates.push(venvPosix)

    // Environment-specified
    if (process.env.PYTHON_EXECUTABLE) candidates.push(process.env.PYTHON_EXECUTABLE)

    // Common names
    candidates.push('python', 'python3', 'py')

    let lastError: Error | null = null

    for (const exe of candidates) {
      try {
        // Invoke python with the script path and the JSON payload as a single argument
        const script = 'scripts/run_add_exercise.py'
        if (!exists(script)) {
          // If script not present in repo, fail fast with informative message
          // But continue to next exe to gather more context
          lastError = new Error(`Expected runner script not found at ${script}`)
          continue
        }

        const { stdout, stderr, code } = await runProcess(exe, [script, payloadStr], 120000)

        // Prefer structured JSON output from the Python runner
        if (stdout) {
          try {
            // If the runner emits JSON, return parsed JSON string for consistency
            const parsed = JSON.parse(stdout)
            return JSON.stringify(parsed)
          } catch (e) {
            // Not JSON — return a structured object with raw output
            return JSON.stringify({ status: 'ok', raw: stdout, stderr: stderr || undefined, code })
          }
        }

        // If no stdout but stderr present, record and try next
        if (stderr) {
          lastError = new Error(`Executable ${exe} stderr: ${stderr}`)
          continue
        }

        // If exit code non-zero and no output, capture that
        if (code && code !== 0) {
          lastError = new Error(`Executable ${exe} exited with code ${code}`)
          continue
        }

      } catch (err: any) {
        lastError = err instanceof Error ? err : new Error(String(err))
        // try next candidate
      }
    }

    // If we get here, all attempts failed
    const message = lastError ? lastError.message : 'No python executable succeeded'
    throw new Error(`Failed to invoke Python runner: ${message}`)
  }
})
