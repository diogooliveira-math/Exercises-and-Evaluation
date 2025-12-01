import fs from 'fs'
import path from 'path'
import { spawnSync } from 'child_process'
import { pathToFileURL } from 'url'

const report = { timestamp: new Date().toISOString(), attempts: [] }

const candidates = [
  path.join(process.cwd(),'playground_test','opencode','opencode','packages','sdk','js','dist','index.js'),
  path.join(process.cwd(),'playground_test','opencode','day1','node_modules','@opencode-ai','sdk','dist','index.js')
]
let sdkPath = null
for (const c of candidates) if (fs.existsSync(c)) { sdkPath = c; break }

report.sdkPath = sdkPath

if (sdkPath) {
  try {
    const sdk = await import(pathToFileURL(sdkPath).href)
    report.attempts.push({ step: 'import', ok: true, path: sdkPath })
    // try common shapes
    if (sdk.client && typeof sdk.client.run === 'function') {
      try {
        const res = await sdk.client.run({ agent: 'manifesto-journaler', message: 'Test run via sdk.client.run' })
        report.attempts.push({ step: 'client.run', ok: true, res: String(res).slice(0,1000) })
      } catch (e) { report.attempts.push({ step: 'client.run', ok: false, err: String(e) }) }
    }
    if (typeof sdk.run === 'function') {
      try { const res = await sdk.run({ agent: 'manifesto-journaler', message: 'Test run via sdk.run' }); report.attempts.push({ step: 'run', ok: true, res: String(res).slice(0,1000) }) } catch (e) { report.attempts.push({ step: 'run', ok: false, err: String(e) }) }
    }
  } catch (e) {
    report.attempts.push({ step: 'import', ok: false, err: String(e) })
  }
} else {
  report.attempts.push({ step: 'import', ok: false, err: 'SDK dist not found' })
}

// Fallback: try opencode CLI version and help
try {
  const p = spawnSync('opencode', ['--version'], { encoding: 'utf8', timeout: 10000 })
  report.cli = { version: p.status === 0 ? (p.stdout||p.stderr).trim() : null, rc: p.status }
} catch (e) { report.cli = { error: String(e) } }

// Save report
const outPath = path.join(process.cwd(),'..','..','..','temp','playground_sdk_tests.json')
fs.mkdirSync(path.dirname(outPath), { recursive: true })
fs.writeFileSync(outPath, JSON.stringify(report, null, 2), 'utf8')
console.log('Wrote report to', outPath)
console.log(JSON.stringify(report, null, 2))
