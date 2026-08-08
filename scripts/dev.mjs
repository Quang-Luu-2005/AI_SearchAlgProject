import { spawn, spawnSync } from 'node:child_process'
import { existsSync } from 'node:fs'
import path from 'node:path'
import process from 'node:process'
import { fileURLToPath } from 'node:url'

const repositoryRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const backendPythonCandidates = process.platform === 'win32'
  ? [path.join(repositoryRoot, '.venv', 'Scripts', 'python.exe')]
  : [path.join(repositoryRoot, '.venv', 'bin', 'python')]
const backendPython = backendPythonCandidates.find(existsSync)
const viteEntry = path.join(repositoryRoot, 'frontend', 'node_modules', 'vite', 'bin', 'vite.js')
const backendOnly = process.argv.includes('--backend-only')
const frontendOnly = process.argv.includes('--frontend-only')
const viteExtraArgs = process.argv.slice(2).filter(
  (argument) => argument !== '--backend-only' && argument !== '--frontend-only',
)

if (backendOnly && frontendOnly) {
  console.error('Chỉ được chọn một trong --backend-only hoặc --frontend-only.')
  process.exit(2)
}

if (!frontendOnly && !backendPython) {
  console.error('Không tìm thấy Python trong .venv.')
  console.error('Chạy: python -m venv .venv')
  console.error('Sau đó: .\\.venv\\Scripts\\python.exe -m pip install -e ".\\backend[dev]"')
  process.exit(1)
}

if (!backendOnly && !existsSync(viteEntry)) {
  console.error('Frontend dependencies chưa được cài.')
  console.error('Chạy: npm --prefix frontend install')
  process.exit(1)
}

const services = []
let shuttingDown = false
let exitCode = 0

function startService(name, command, args, cwd = repositoryRoot) {
  const child = spawn(command, args, {
    cwd,
    env: process.env,
    stdio: 'inherit',
  })
  services.push({ name, child })
  child.on('error', (error) => {
    console.error(`[${name}] Không thể khởi động: ${error.message}`)
    exitCode = 1
    shutdown()
  })
  child.on('exit', (code, signal) => {
    if (shuttingDown) return
    console.error(`[${name}] Đã dừng (${signal ?? `exit ${code ?? 1}`}).`)
    exitCode = code ?? 1
    shutdown()
  })
}

function shutdown() {
  if (shuttingDown) return
  shuttingDown = true
  for (const { child } of services) {
    if (child.killed || child.pid === undefined) continue
    if (process.platform === 'win32') {
      spawnSync('taskkill', ['/pid', String(child.pid), '/T', '/F'], { stdio: 'ignore' })
    } else {
      child.kill('SIGTERM')
    }
  }
  setTimeout(() => process.exit(exitCode), 250)
}

process.on('SIGINT', () => {
  console.log('\nĐang dừng các service…')
  shutdown()
})
process.on('SIGTERM', shutdown)

if (!frontendOnly) {
  startService('backend', backendPython, [
    '-m',
    'uvicorn',
    'backend.app.main:app',
    '--reload',
    '--reload-dir',
    'backend',
    '--host',
    '127.0.0.1',
    '--port',
    '8000',
  ])
}

if (!backendOnly) {
  startService('frontend', process.execPath, [
    viteEntry,
    '--host',
    '127.0.0.1',
    '--port',
    '5173',
    '--strictPort',
    ...viteExtraArgs,
  ], path.join(repositoryRoot, 'frontend'))
}

console.log('FloodRoute development services')
if (!frontendOnly) console.log('- API:      http://127.0.0.1:8000')
if (!backendOnly) console.log('- Frontend: http://127.0.0.1:5173')
console.log('Nhấn Ctrl+C để dừng.')
