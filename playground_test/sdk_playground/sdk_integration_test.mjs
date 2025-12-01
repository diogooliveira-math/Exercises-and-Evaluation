import { pathToFileURL } from 'url'
import fs from 'fs'
import path from 'path'

const sdkPath = path.join(process.cwd(),'playground_test','opencode','day1','node_modules','@opencode-ai','sdk','dist','index.js')
if (!fs.existsSync(sdkPath)) throw new Error('SDK dist not found: ' + sdkPath)
const sdk = await import(pathToFileURL(sdkPath).href)

const report = { timestamp: new Date().toISOString(), sdkPath, steps: [] }

try {
  // Start a server and client
  const { client, server } = await sdk.createOpencode({ port: 4096, timeout: 20000, config: {}, directory: path.join(process.cwd()) })
  report.steps.push({ step: 'createOpencode', ok: true, url: server.url })

  // Use client to call read-only endpoints
  try {
    const p = await client.path.get()
    report.steps.push({ step: 'path.get', ok: true, res: p })
  } catch (e) { report.steps.push({ step: 'path.get', ok: false, err: String(e) }) }

  try {
    const agents = await client.app.agents()
    report.steps.push({ step: 'app.agents', ok: true, resCount: Array.isArray(agents) ? agents.length : agents })
  } catch (e) { report.steps.push({ step: 'app.agents', ok: false, err: String(e) }) }

  try {
    const tools = await client.tool.ids()
    report.steps.push({ step: 'tool.ids', ok: true, resCount: Array.isArray(tools) ? tools.length : tools })
  } catch (e) { report.steps.push({ step: 'tool.ids', ok: false, err: String(e) }) }

  try {
    const cfg = await client.config.get()
    report.steps.push({ step: 'config.get', ok: true, keys: Object.keys(cfg || {}) })
  } catch (e) { report.steps.push({ step: 'config.get', ok: false, err: String(e) }) }

  // Close server
  try { server.close(); report.steps.push({ step: 'server.close', ok: true }) } catch (e) { report.steps.push({ step: 'server.close', ok: false, err: String(e) }) }
} catch (e) {
  report.steps.push({ step: 'createOpencode', ok: false, err: String(e) })
}

const out = path.join(process.cwd(),'..','..','temp','sdk_integration_report.json')
fs.mkdirSync(path.dirname(out), { recursive: true })
fs.writeFileSync(out, JSON.stringify(report, null, 2), 'utf8')
console.log('Wrote report to', out)
console.log(JSON.stringify(report, null, 2))
