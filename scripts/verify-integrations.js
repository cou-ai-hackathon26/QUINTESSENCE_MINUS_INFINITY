#!/usr/bin/env node
/**
 * Integration verification runner.
 * Reports configured real sandbox/live integration gates.
 * Missing access is reported as blocked, not passed.
 */
console.log('=== Shongoti Integration Capabilities Verification ===\n');

const checks = [
  {
    name: 'Gemini AI Provider',
    envKey: 'GEMINI_API_KEY',
    status: process.env.GEMINI_API_KEY ? 'configured' : 'blocked',
    reason: 'GEMINI_API_KEY not configured. Offline mock boundaries are active.',
  },
  {
    name: 'SSLCOMMERZ Payment Gateway',
    envKey: 'SSLCOMMERZ_STORE_ID',
    status: process.env.SSLCOMMERZ_STORE_ID ? 'configured' : 'blocked',
    reason: 'SSLCOMMERZ credentials not configured. Synthetic payment double active.',
  },
  {
    name: 'Transactional SMS/Email',
    envKey: 'SMS_PROVIDER_KEY',
    status: process.env.SMS_PROVIDER_KEY ? 'configured' : 'blocked',
    reason: 'SMS/Email provider not configured.',
  },
];

let allConfigured = true;

for (const c of checks) {
  console.log(`[${c.status.toUpperCase()}] ${c.name}`);
  if (c.status === 'blocked') {
    console.log(`  Reason: ${c.reason}`);
    allConfigured = false;
  }
}

console.log('\nStatus: Real integrations are currently unconfigured/blocked (as expected in Phase 01).');
// In Phase 01, this returns 0 while explicitly reporting blocked status per INTEGRATIONS.md
process.exit(0);
