import { spawnSync } from 'node:child_process'
import { existsSync } from 'node:fs'
import path from 'node:path'
import process from 'node:process'
import { fileURLToPath } from 'node:url'

const repositoryRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const pythonCandidates = process.platform === 'win32'
  ? [path.join(repositoryRoot, '.venv', 'Scripts', 'python.exe')]
  : [path.join(repositoryRoot, '.venv', 'bin', 'python')]
const python = pythonCandidates.find(existsSync)

if (!python) {
  console.error('Không tìm thấy Python trong .venv.')
  console.error('Hãy tạo virtual environment và cài backend dependencies trước.')
  process.exit(1)
}

const result = spawnSync(python, process.argv.slice(2), {
  cwd: repositoryRoot,
  env: process.env,
  stdio: 'inherit',
})

if (result.error) {
  console.error(`Không thể chạy Python: ${result.error.message}`)
  process.exit(1)
}

process.exit(result.status ?? 1)
