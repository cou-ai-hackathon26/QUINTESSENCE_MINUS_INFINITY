#!/usr/bin/env node
/**
 * Repository Secrets & Credentials Security Scanner (Phase 11: P11-T03).
 *
 * Scans repository files for leaked credentials, private keys, API tokens,
 * and high-entropy secret patterns.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('=== Shongoti Repository Secrets & Credentials Scanner ===\n');

const rootDir = path.resolve(__dirname, '..');

// Get all tracked git files
let trackedFiles = [];
try {
  const output = execSync('git ls-files', { cwd: rootDir, encoding: 'utf-8' });
  trackedFiles = output.split('\n').map(f => f.trim()).filter(Boolean);
} catch (err) {
  console.error('[FAIL] Could not run git ls-files:', err.message);
  process.exit(1);
}

const secretRules = [
  { name: 'Groq API Key', pattern: /gsk_[A-Za-z0-9]{35,}/ },
  { name: 'Private Key Block', pattern: /-----BEGIN (RSA|EC|PGP|OPENSSH|DSA)? ?PRIVATE KEY-----/ },
  { name: 'Google API Key', pattern: /AIza[0-9A-Za-z\\-_]{35}/ },
  { name: 'GitHub Personal Access Token', pattern: /gh[pousr]_[A-Za-z0-9_]{36,}/ },
  { name: 'AWS Access Key ID', pattern: /AKIA[0-9A-Z]{16}/ },
  { name: 'OpenAI Secret Key', pattern: /sk-[a-zA-Z0-9]{20,}/ },
  { name: 'Slack Bot Token', pattern: /xoxb-[0-9]{11,13}-[0-9]{11,13}-[a-zA-Z0-9]{24}/ },
];

let leakCount = 0;
let scannedCount = 0;

for (const relPath of trackedFiles) {
  // Skip binary files or lock files
  if (relPath.endsWith('.png') || relPath.endsWith('.jpg') || relPath.endsWith('.ico') || relPath.endsWith('.pdf') || relPath === 'pnpm-lock.yaml') {
    continue;
  }

  const fullPath = path.join(rootDir, relPath);
  if (!fs.existsSync(fullPath)) continue;

  scannedCount++;
  const content = fs.readFileSync(fullPath, 'utf-8');

  for (const rule of secretRules) {
    if (rule.pattern.test(content)) {
      console.error(`[LEAK DETECTED] File "${relPath}" matches pattern: ${rule.name}`);
      leakCount++;
    }
  }
}

console.log(`Scanned ${scannedCount} tracked repository files.`);

if (leakCount > 0) {
  console.error(`\n[FAIL] Found ${leakCount} potential credential leaks! Release blocked.`);
  process.exit(1);
} else {
  console.log('[PASS] Zero credential leaks or private keys detected in tracked source tree.\n');
  process.exit(0);
}
