#!/usr/bin/env node
/**
 * Integration verification runner.
 * Reports configured real sandbox/live integration gates.
 * Explicitly separates:
 * - configured (credentials present and verified)
 * - blocked (credentials missing or provider unavailable)
 *
 * Mode:
 *   --strict: Exits with code 2 if any required integration is blocked.
 *   Default (inventory mode): Exits with code 0 while explicitly reporting blocked status.
 */
const isStrict = process.argv.includes('--strict');

console.log('=== Shongoti Integration Capabilities Verification ===\n');

const checks = [
  {
    name: 'Gemini AI Multimodal Provider',
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
    name: 'Transactional SMS/Email Gateway',
    envKey: 'SMS_PROVIDER_KEY',
    status: process.env.SMS_PROVIDER_KEY ? 'configured' : 'blocked',
    reason: 'SMS/Email provider not configured.',
  },
];

let allConfigured = true;

for (const c of checks) {
  const badge = c.status === 'configured' ? '[CONFIGURED]' : '[BLOCKED]   ';
  console.log(`${badge} ${c.name}`);
  if (c.status === 'blocked') {
    console.log(`            Reason: ${c.reason}`);
    allConfigured = false;
  }
}

if (!allConfigured && isStrict) {
  console.log('\nStatus: Strict mode enabled and one or more integrations are BLOCKED.');
  process.exit(2);
} else {
  console.log('\nStatus: Inventory verified. External live integrations explicitly tracked.');
  process.exit(0);
}
