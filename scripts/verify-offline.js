#!/usr/bin/env node
/**
 * Offline verification runner.
 * Executes required local deterministic/type/build/boundary gates.
 * Exits with:
 *   0: All required local gates passed.
 *   1: Hard test/type/build failure.
 *   2: Blocked gate (e.g. headless browser missing).
 */
const { execSync } = require('child_process');
const path = require('path');

const rootDir = path.resolve(__dirname, '..');

const steps = [
  { name: 'Frontend Typecheck', cmd: 'pnpm --filter @shongoti/web typecheck', required: true },
  { name: 'Domain Golden Contracts', cmd: 'node scripts/run-python.js -m pytest apps/api/tests/test_domain_contracts.py apps/api/tests/test_domain_golden.py -v', required: true },
  { name: 'API, Persistence & Security Tests', cmd: 'node scripts/run-python.js -m pytest apps/api/tests/ -v', required: true },
  { name: 'Web Unit & Workflow Tests', cmd: 'pnpm --filter @shongoti/web test', required: true },
  { name: 'Web Production Build', cmd: 'pnpm --filter @shongoti/web build', required: true },
  { name: 'CSS & Accessibility Static Scan', cmd: 'node scripts/check-css.js', required: true },
  { name: 'Security & Secrets Scan', cmd: 'node scripts/scan-secrets.js', required: true },
];

console.log('=== Running Shongoti Offline Verification Gate ===\n');
let failed = false;

for (const step of steps) {
  console.log(`--> [RUNNING] ${step.name}...`);
  try {
    execSync(step.cmd, { stdio: 'inherit', cwd: rootDir });
    console.log(`--> [PASSED]  ${step.name}\n`);
  } catch (err) {
    console.error(`\n[FAILED]  ${step.name} (exit code non-zero)\n`);
    failed = true;
    break;
  }
}

if (failed) {
  console.error('Offline verification FAILED.');
  process.exit(1);
} else {
  console.log('=== All executed offline gates passed. Comparative/live-provider gates are separate and are not certified here. ===');
  process.exit(0);
}
