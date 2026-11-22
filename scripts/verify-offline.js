#!/usr/bin/env node
/**
 * Offline verification runner.
 * Executes required local deterministic/type/build/boundary gates.
 * Exits with nonzero on any failure.
 */
const { execSync } = require('child_process');
const path = require('path');

const rootDir = path.resolve(__dirname, '..');

const steps = [
  { name: 'Frontend Typecheck', cmd: 'pnpm --filter @shongoti/web typecheck' },
  { name: 'Domain Golden Contracts', cmd: 'node scripts/run-python.js -m pytest apps/api/tests/test_domain_contracts.py apps/api/tests/test_domain_golden.py -v' },
  { name: 'API & Health Tests', cmd: 'node scripts/run-python.js -m pytest apps/api/tests/test_health.py apps/api/tests/test_persistence_and_auth.py -v' },
  { name: 'Web Unit Tests', cmd: 'pnpm --filter @shongoti/web test' },
  { name: 'Web Production Build', cmd: 'pnpm --filter @shongoti/web build' },
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
  console.log('=== All Offline Verification Gates PASSED ===');
  process.exit(0);
}
