#!/usr/bin/env node
/**
 * AI Provider Evaluation Runner.
 * Executes actual multimodal extraction scoring across text, audio, and image cases.
 * Reports mode: live_gemini (when GEMINI_API_KEY is configured) or offline_test_double.
 */
const { spawnSync } = require('child_process');
const path = require('path');

const rootDir = path.resolve(__dirname, '..');

console.log('=== Running Shongoti Multimodal AI Evaluation Runner ===\n');

const res = spawnSync('node', ['scripts/run-python.js', 'scripts/eval_ai.py'], {
  cwd: rootDir,
  stdio: 'inherit',
  shell: true,
});

process.exit(res.status || 0);
