#!/usr/bin/env node
/**
 * Cross-platform Python runner.
 * Locates the project venv or system Python and passes arguments through.
 */
const { spawnSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const rootDir = path.resolve(__dirname, '..');
const venvWindows = path.join(rootDir, 'apps', 'api', '.venv', 'Scripts', 'python.exe');
const venvUnix = path.join(rootDir, 'apps', 'api', '.venv', 'bin', 'python');

let pythonPath = 'python';

if (fs.existsSync(venvWindows)) {
  pythonPath = venvWindows;
} else if (fs.existsSync(venvUnix)) {
  pythonPath = venvUnix;
}

const args = process.argv.slice(2);
const result = spawnSync(pythonPath, args, {
  stdio: 'inherit',
  cwd: rootDir,
  env: {
    ...process.env,
    PYTHONPATH: path.join(rootDir, 'apps', 'api'),
  },
});

if (result.error) {
  console.error('Failed to execute Python process:', result.error.message);
  process.exit(1);
}

process.exit(result.status !== null ? result.status : 0);
