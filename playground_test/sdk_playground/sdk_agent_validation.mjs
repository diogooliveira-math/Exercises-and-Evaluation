import fs from 'fs'
import path from 'path'
import { pathToFileURL } from 'url'

const sdkPath = path.join(process.cwd(),'playground_test','opencode','day1','node_modules','@opencode-ai','sdk','dist','index.js')
if (!fs.existsSync(sdkPath)) {
  console.error('SDK dist not found:', sdkPath)
  process.exit(1)
}
const sdk = await import(pathToFileURL(sdkPath).href)

const report = { timestamp: new Date().toISOString(), sdkPath, results: [] }

async function findFreePort(start=4096, max=4106){ const net = await import('net'); for(let p=start;p<=max;p++){ const s = net.createServer().listen(p); try{ await new Promise((res,rej)=>s.once('listening',res).once('error',rej)); s.close(); return p }catch(e){ try{s.close()}catch(_){} } } throw new Error('No free port found') }
const port = await findFreePort(4096, 4200)
let client, server
try {
  ({ client, server } = await sdk.createOpencode({ port, timeout: 20000, config: {}, directory: path.join(process.cwd(), '..','..') }))
  report.serverUrl = server.url
} catch (e) {
  report.serverStartError = String(e)
  const fallbackUrl = `http://127.0.0.1:${port}`
  client = sdk.createOpencodeClient({ baseUrl: fallbackUrl, directory: path.join(process.cwd(), '..','..') })
  server = null
  report.serverUrl = fallbackUrl
  report.serverFallback = true
}

const agents = [ 'manifesto-interventionist','intervention-planner','manifesto-journaler','manifesto-writer' ]

function listArtifacts() {
  const out = []
  const dirs = [ path.join(process.cwd(), '..','..','agents_manifestos','intervencoes'), path.join(process.cwd(),'..','..','agents_manifestos','journaling') ]
  for (const d of dirs) {
    if (!fs.existsSync(d)) continue
    for (const f of fs.readdirSync(d)) if (f.endsWith('.md')) out.push(path.join(d,f))
  }
  return out.sort()
}
function listLogs() {
  const root = path.join(process.cwd(),'..','..','temp','opencode_logs')
  const files = []
  if (!fs.existsSync(root)) return files
  function walk(dir){ for (const e of fs.readdirSync(dir)){ const p=path.join(dir,e); const st=fs.statSync(p); if (st.isDirectory()) walk(p); else files.push(p) }}
  walk(root); return files.sort()
}

const baselineArtifacts = listArtifacts()
const baselineLogs = listLogs()

for (const agent of agents) {
  const start = Date.now()
  const item = { agent, start: new Date().toISOString(), status: 'started', steps: [] }
  report.results.push(item)

  try {
    // create a session
    const sessionCreate = await client.session.create({ json: {} })
    const sessionId = sessionCreate?.data?.id || sessionCreate?.data || sessionCreate?.request?.body?.id || sessionCreate?.id
    item.steps.push({ step: 'session.create', ok: true, sessionCreate: safePreview(sessionCreate) })

    // prompt asynchronously
    const message = 'Perform a compact validation: create manifesto and journaling entry for testing subagent/tool invocation.'
    const promptBody = { agent, parts: [{ type: 'text', text: message }], noReply: false }
    try {
      await client.session.promptAsync({ id: sessionId, json: promptBody })
      item.steps.push({ step: 'promptAsync.sent', ok: true })
    } catch (e) {
      item.steps.push({ step: 'promptAsync.sent', ok: false, err: String(e) })
    }

    // poll status until not running or timeout
    const timeoutMs = 120000
    const pollInterval = 2000
    let finished = false
    const deadline = Date.now() + timeoutMs
    while (Date.now() < deadline) {
      try {
        const st = await client.session.status({ id: sessionId })
        item.steps.push({ step: 'status', ok: true, status: safePreview(st) })
        const state = (st?.data?.state) ?? (st?.data?.status) ?? (st?.data) ?? st
        if (!state || (typeof state === 'string' && state !== 'running' && state !== 'busy') ) { finished = true; break }
      } catch (e) {
        item.steps.push({ step: 'status', ok: false, err: String(e) })
        // continue polling
      }
      await new Promise(r=>setTimeout(r,pollInterval))
    }
    item.steps.push({ step: 'wait.complete', ok: finished })

    // fetch messages
    try {
      const msgs = await client.session.messages({ id: sessionId })
      item.steps.push({ step: 'messages', ok: true, messagesPreview: safePreview(msgs) })
    } catch (e) {
      item.steps.push({ step: 'messages', ok: false, err: String(e) })
    }

    // compare artifacts/logs
    const afterArtifacts = listArtifacts()
    const afterLogs = listLogs()
    item.newArtifacts = afterArtifacts.filter(x=>!baselineArtifacts.includes(x))
    item.newLogs = afterLogs.filter(x=>!baselineLogs.includes(x))

    // close session
    try { await client.session.abort({ id: sessionId }); item.steps.push({ step: 'session.abort', ok: true }) } catch(e){ item.steps.push({ step: 'session.abort', ok: false, err: String(e) }) }

    item.status = 'done'
  } catch (e) {
    item.status = 'error'
    item.error = String(e)
  }
}

// close server
try { server.close(); report.serverClosed = true } catch (e) { report.serverClosed = String(e) }

const outPath = path.join(process.cwd(),'..','..','temp', `sdk_agent_validation_${Date.now()}.json`)
fs.writeFileSync(outPath, JSON.stringify(report, null, 2), 'utf8')
console.log('Wrote', outPath)

function safePreview(obj){ try{ const s = JSON.stringify(obj); return s.length>1000? s.slice(0,1000)+'...': JSON.parse(s) } catch(e){ return String(obj) }}

