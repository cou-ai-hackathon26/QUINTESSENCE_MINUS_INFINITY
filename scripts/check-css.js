#!/usr/bin/env node
/**
 * Static CSS & Accessibility Scanner.
 * Verifies responsive rules, touch targets, and accessibility patterns.
 */
const fs = require('fs');
const path = require('path');

const rootDir = path.resolve(__dirname, '..');
const webDir = path.join(rootDir, 'apps', 'web');

console.log('=== Shongoti CSS & Accessibility Static Verification ===\n');

const cssPath = path.join(webDir, 'src', 'index.css');
if (!fs.existsSync(cssPath)) {
  console.error(`[FAIL] CSS file not found at ${cssPath}`);
  process.exit(1);
}

const cssContent = fs.readFileSync(cssPath, 'utf-8');
const checks = [
  { name: 'max-width: 768px (Mobile/Tablet layout)', pattern: /@media\s*\(max-width:\s*768px\)/ },
  { name: 'prefers-reduced-motion accessibility', pattern: /@media\s*\(prefers-reduced-motion:\s*reduce\)/ },
  { name: 'touch-action manipulation for mobile touch targets', pattern: /touch-action:\s*manipulation/ },
  { name: 'focus-visible indicator', pattern: /\*:focus-visible/ },
];

let failed = false;
for (const check of checks) {
  if (!check.pattern.test(cssContent)) {
    console.error(`[FAIL] Missing CSS check: ${check.name}`);
    failed = true;
  } else {
    console.log(`  ✓ [PASS] ${check.name}`);
  }
}

if (failed) {
  console.error('\nCSS Verification FAILED.');
  process.exit(1);
} else {
  console.log('\n[PASS] All CSS responsive & accessibility patterns verified.');
  process.exit(0);
}
