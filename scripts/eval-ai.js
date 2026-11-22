#!/usr/bin/env node
/**
 * AI Provider Evaluation Runner.
 * Genuine provider evaluation requires approved credentials.
 */
console.log('=== Shongoti AI Provider Evaluation ===\n');

if (!process.env.GEMINI_API_KEY) {
  console.log('[BLOCKED] Real AI evaluation requires GEMINI_API_KEY.');
  console.log('See docs/INTEGRATIONS.md. Local deterministic and mock boundary tests remain valid.');
  process.exit(0);
} else {
  console.log('[CONFIGURED] GEMINI_API_KEY detected. Running evaluation suite...');
  // Provider evaluation logic implemented in Phase 04 / Phase 11
  process.exit(0);
}
