#!/usr/bin/env node
/**
 * Deployment & Production Smoke-Test Suite (Phase 12: P12-T02).
 *
 * Verifies live deployment readiness:
 * 1. Health and readiness endpoints.
 * 2. Authenticated demo login and token generation.
 * 3. Today dashboard financial metrics.
 * 4. 7-Day scenario planning simulation.
 * 5. Customer invoice portal token and dispute endpoint.
 * 6. Operating reports (Cash, Accrual, Stock, Dues).
 */

const { spawnSync } = require('child_process');
const path = require('path');
const http = require('http');

console.log('=== Shongoti Deployment Smoke-Test Gate ===\n');

const rootDir = path.resolve(__dirname, '..');

// Helper to check if server is already running on port 8000
function checkPort(port) {
  return new Promise((resolve) => {
    const req = http.get(`http://127.0.0.1:${port}/health`, (res) => {
      resolve(res.statusCode === 200);
    });
    req.on('error', () => resolve(false));
    req.setTimeout(1000, () => {
      req.destroy();
      resolve(false);
    });
  });
}

async function run() {
  const isLiveServer = await checkPort(8000);

  if (isLiveServer) {
    console.log('[INFO] Detected running HTTP server on http://127.0.0.1:8000.');
    console.log('Executing live HTTP probe...');
    const endpoints = [
      { path: '/health', expectedStatus: 200 },
      { path: '/ready', expectedStatus: 200 },
    ];
    for (const ep of endpoints) {
      const res = await new Promise((resolve) => {
        http.get(`http://127.0.0.1:8000${ep.path}`, (r) => resolve(r.statusCode));
      });
      if (res === ep.expectedStatus) {
        console.log(`  ✓ GET ${ep.path} -> ${res} OK`);
      } else {
        console.error(`  [FAIL] GET ${ep.path} returned ${res}`);
        process.exit(1);
      }
    }
  }

  // Run Python smoke-test suite to test full business workflow
  console.log('--> Running Application Deployment Workflow Smoke Checks...');
  const result = spawnSync('node', ['scripts/run-python.js', 'scripts/smoke_test.py'], {
    cwd: rootDir,
    stdio: 'inherit',
    shell: true,
  });

  if (result.status !== 0) {
    console.error('\n[FAIL] Deployment smoke-test failed.');
    process.exit(1);
  }

  console.log('\n=== Deployment Smoke-Test Gate PASSED ===');
  process.exit(0);
}

run();
