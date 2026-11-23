#!/usr/bin/env node
// A comparative architecture benchmark requires independent candidate execution on held-out inputs.
// Contract tests and synthetic smoke requests do not establish architecture superiority.
console.error('[NOT_RUN] Comparative architecture benchmark has not been implemented or independently evaluated. No scores, latency or cost results are generated.');
console.error('Use pnpm test:domain for exact domain contracts and pnpm eval:ai --live for bounded genuine provider smoke checks. Neither is a comparative benchmark.');
process.exit(2);
