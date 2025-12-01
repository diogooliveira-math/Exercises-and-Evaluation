import fs from 'fs'
import path from 'path'
import { pathToFileURL } from 'url'

const sdkPath = path.join(process.cwd(),'playground_test','opencode','day1','node_modules','@opencode-ai','sdk','dist','index.js')
if (!fs.existsSync(sdkPath)) { console.error('SDK not found', sdkPath); process.exit(1) }
const sdk = await import(pathToFileURL(sdkPath).href)

console.log('Using SDK:', sdkPath)

const { client, server } = await sdk.createOpencode({ port: 4121, timeout: 20000, config: {}, directory: path.join(process.cwd(),'..','..') })
console.log('Server URL:', server.url)

// inspect client internals
console.log('Client keys:', Object.keys(client))
console.log('Client internal keys:', Object.keys(client._client || client.client || {}))

function safe(obj){ try{ return JSON.stringify(obj,null,2) }catch(e){ return String(obj) } }

// add request/response interceptors to log full details
if (client._client && client._client.interceptors) {
  const reqIdCounter = { v: 0 }
  client._client.interceptors.request.use(async (req, opts) => {
    const id = ++reqIdCounter.v
    try {
      const cloned = new Request(req)
      const bodyText = cloned.body ? await cloned.text().catch(()=>"<body-unreadable>") : undefined
      console.log(`[REQ ${id}] ${cloned.method} ${cloned.url}`)
      console.log(`[REQ ${id}] headers:`, JSON.stringify(Array.from(cloned.headers.entries())))
      if (bodyText) console.log(`[REQ ${id}] body:`, bodyText.slice(0,2000))
    } catch (e) {
      console.log('Failed to log request', e)
    }
    return req
  })
  client._client.interceptors.response.use(async (res, req) => {
    const url = req?.url || (res && res.url) || '<unknown>'
    try{
      const txt = await res.clone().text().catch(()=>'<body-unreadable>')
      console.log(`[RES] ${res.status} ${url}`)
      console.log(`[RES] bodyPreview:`, txt.slice(0,2000))
    }catch(e){ console.log('Failed to log response', e) }
    return res
  })
} else {
  console.log('No interceptors available on client internals')
}

// create session
const sessionCreate = await client.session.create({ json: {} })
const sessionId = sessionCreate?.data?.id || sessionCreate?.id
console.log('Created session:', sessionId)

// build URLs using internal buildUrl if available
if (client._client && typeof client._client.buildUrl === 'function'){
  const urlMessages = client._client.buildUrl({ url: '/session/{id}/message', path: { id: sessionId } })
  const urlStatus = client._client.buildUrl({ url: '/session/status' })
  console.log('Built URL (messages):', urlMessages)
  console.log('Built URL (status):', urlStatus)
} else {
  console.log('No internal buildUrl available')
}

// send promptAsync properly typed
const promptBody = { agent: 'manifesto-interventionist', parts: [{ type: 'text', text: 'Test run: create manifesto and journaling entry' }], noReply: false }
console.log('Sending promptAsync body:', safe(promptBody))
await client.session.promptAsync({ path: { id: sessionId }, json: promptBody })
console.log('promptAsync accepted')

// wait a short while then fetch messages
await new Promise(r=>setTimeout(r,2000))
const msgs = await client.session.messages({ path: { id: sessionId }, query: { limit: 10 } })
console.log('messages result preview:', safe(msgs?.data ? msgs.data : msgs))

// poll status once
const st = await client.session.status({})
console.log('status result preview:', safe(st?.data ? st.data : st))

// abort and close
await client.session.abort({ path: { id: sessionId } })
server.close()
console.log('Done')
