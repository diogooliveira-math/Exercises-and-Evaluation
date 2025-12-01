import { spawnSync } from 'child_process';
import fs from 'fs';
import path from 'path';

const agents = [
  'manifesto-interventionist',
  'intervention-planner',
  'manifesto-journaler',
  'manifesto-writer'
];

const sdkCandidate = path.resolve(process.cwd(), 'playground_test', 'opencode', 'day1', 'node_modules', '@opencode-ai', 'sdk', 'dist', 'index.js');
let sdk = null;
let sdkInfo = { available: false, path: sdkCandidate, note: '' };

if (fs.existsSync(sdkCandidate)) {
  try {
    const mod = await import(pathToFileURL(sdkCandidate).href);
    sdk = mod;
    sdkInfo.available = true;
    sdkInfo.note = 'Imported SDK module';
  } catch (e) {
    sdkInfo.available = false;
    sdkInfo.note = `Failed to import SDK: ${e.message}`;
  }
} else {
  sdkInfo.note = 'SDK dist not found at expected path';
}

function listArtifacts() {
  const out = [];
  const dirs = [
    path.join(process.cwd(), 'agents_manifestos', 'intervencoes'),
    path.join(process.cwd(), 'agents_manifestos', 'journaling'),
  ];
  for (const d of dirs) {
    if (fs.existsSync(d)) {
      for (const f of fs.readdirSync(d)) {
        if (f.endsWith('.md')) out.push(path.join(d, f));
      }
    }
  }
  return out.sort();
}

function listLogs() {
  const root = path.join(process.cwd(), 'temp', 'opencode_logs');
  const files = [];
  if (!fs.existsSync(root)) return files;
  function walk(dir) {
    for (const entry of fs.readdirSync(dir)) {
      const p = path.join(dir, entry);
      const stat = fs.statSync(p);
      if (stat.isDirectory()) walk(p); else files.push(p);
    }
  }
  walk(root);
  return files.sort();
}

function runCli(agent, message, timeoutMs = 120000) {
  const cmd = ['opencode', 'run', message, '--agent', agent];
  console.log('Running CLI:', cmd.join(' '));
  try {
    const r = spawnSync(cmd[0], cmd.slice(1), { encoding: 'utf8', timeout: timeoutMs });
    console.log('Finished CLI; rc=', r.status);
    return { rc: r.status ?? -1, stdout: r.stdout ?? '', stderr: r.stderr ?? '' };
  } catch (e) {
    console.log('CLI invocation error or timeout:', e && e.message ? e.message : String(e));
    return { rc: -2, stdout: '', stderr: String(e) };
  }
}

async function validate(dry = false) {
  const beforeArtifacts = listArtifacts();
  const beforeLogs = listLogs();

  const results = [];

  for (const agent of agents) {
    console.log(`\n>>> Validating: ${agent}`);
    let rc = -1, stdout = '', stderr = '';
    const message = 'Perform a compact validation: try to produce a manifesto and journaling entry.';
    try {
      if (!dry && sdkInfo.available) {
        try {
          const rr = await runWithSdk(agent, message);
          rc = rr.rc; stdout = rr.stdout; stderr = rr.stderr;
          console.log(`Used SDK for agent ${agent}`);
        } catch (e) {
          console.log(`SDK invocation failed for ${agent}: ${e.message}. Falling back to CLI`);
          const rr = runCli(agent, message);
          rc = rr.rc; stdout = rr.stdout; stderr = rr.stderr;
        }
      } else if (!dry) {
        const rr = runCli(agent, message);
        rc = rr.rc; stdout = rr.stdout; stderr = rr.stderr;
      } else {
        console.log('(dry-run) skipping invocation');
      }
    } catch (e) {
      stderr = String(e);
    }

    const afterArtifacts = listArtifacts();
    const afterLogs = listLogs();

    const combined = `${stdout}\n${stderr}`;
    const helpDetected = /Positionals:|Options:|Usage:/.test(combined);

    const newArtifacts = afterArtifacts.filter(x => !beforeArtifacts.includes(x));
    const newLogs = afterLogs.filter(x => !beforeLogs.includes(x));

    results.push({
      agent,
      rc,
      helpDetected,
      stdout_snippet: stdout.slice(0, 2000),
      stderr_snippet: stderr.slice(0, 2000),
      newArtifacts,
      newLogs,
    });

    beforeArtifacts.push(...newArtifacts);
    beforeLogs.push(...newLogs);
  }

  const report = {
    timestamp: new Date().toISOString(),
    sdk: sdkInfo,
    results,
  };

  const outdir = path.join(process.cwd(), 'temp');
  if (!fs.existsSync(outdir)) fs.mkdirSync(outdir, { recursive: true });
  const outpath = path.join(outdir, `validation_report_${Date.now()}.json`);
  fs.writeFileSync(outpath, JSON.stringify(report, null, 2), 'utf8');
  console.log('\nReport written to:', outpath);
  console.log(JSON.stringify(report, null, 2).slice(0, 20000));
}

// Helpers for SDK call if needed
async function runWithSdk(agent, message) {
  if (!sdk) throw new Error('SDK not loaded');
  if (sdk.client && typeof sdk.client.run === 'function') {
    try { const res = await sdk.client.run({ agent, message }); return { rc: 0, stdout: JSON.stringify(res).slice(0,2000), stderr: '' } } catch (e) { return { rc: -1, stdout: '', stderr: String(e) } }
  }
  if (typeof sdk.run === 'function') {
    try { const res = await sdk.run({ agent, message }); return { rc: 0, stdout: JSON.stringify(res).slice(0,2000), stderr: '' } } catch (e) { return { rc: -1, stdout: '', stderr: String(e) } }
  }
  throw new Error('SDK imported but no usable run API found')
}

// small shim: import pathToFileURL for earlier code
import { pathToFileURL } from 'url';

// Run active
validate(false).catch(e => { console.error('Validator error', e); process.exit(2) })
