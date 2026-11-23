#!/usr/bin/env node
// Isolated design-study checks. Not an application/browser/AI validation.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const crypto = require('node:crypto');
const cp = require('node:child_process');
const root = path.resolve(__dirname, '../..');
const read = file => fs.readFileSync(path.join(root, file), 'utf8');
const assert = (ok, message) => { if (!ok) throw new Error(message); };
try {
  const doc = 'UI_DESIGN_PLAN.md', htmlPath = 'docs/design/shongoti-directions.html';
  const plan = read(doc), html = read(htmlPath), checks = [];
  const source = html.match(/<script>([\s\S]*?)<\/script>/)[1];
  new vm.Script(source);
  checks.push('Inline prototype JavaScript parses');
  const fn = source.match(/function resolveExample\(reply\)\{[^\n]+\}/)[0];
  const context = vm.createContext({});
  vm.runInContext(fn, context);
  for (const [reply, amount, score] of [['included', 22000, 100], ['not_included', 18000, 100], ['unknown', null, 59], ['invalid', null, 59]]) {
    const result = context.resolveExample(reply);
    assert(result.amount === amount && result.score === score && !result.canExecuteWithoutApproval, 'Incorrect synthetic branch ' + reply);
    checks.push('Independent synthetic branch: ' + reply);
  }
  const ids = [...html.matchAll(/\bid="([^"]+)"/g)].map(m => m[1]);
  assert(new Set(ids).size === ids.length, 'Duplicate HTML ID');
  for (const link of html.matchAll(/href="([^"]+)"/g)) {
    const value = link[1];
    if (value.startsWith('#')) assert(ids.includes(value.slice(1)), 'Broken anchor ' + value);
    else if (!/^https?:/.test(value)) assert(fs.existsSync(path.resolve(root, path.dirname(htmlPath), value)), 'Broken concept file link ' + value);
  }
  for (const link of plan.matchAll(/\]\(([^)]+)\)/g)) {
    const value = link[1];
    if (!/^https?:/.test(value)) assert(fs.existsSync(path.resolve(root, path.dirname(doc), value.split('#')[0])), 'Broken plan link ' + value);
  }
  assert((html.match(/data-direction="/g) || []).length === 4, 'Four direction controls required');
  assert((html.match(/data-reply="/g) || []).length === 3, 'Three supplier replies required');
  assert(html.includes('prefers-reduced-motion:reduce') && html.includes('aria-pressed') && html.includes('aria-live="polite"'), 'Missing declared accessibility hooks');
  assert(!/fetch\(|XMLHttpRequest|WebSocket|<script[^>]+src=/.test(html), 'Unexpected remote/service script path');
  assert(html.includes('AI/API call') && html.includes('live agent status'), 'Missing illustrative mode labels');
  checks.push('HTML IDs, anchors, file links and direction/reply controls', 'Declared reduced-motion and accessibility hooks (not browser verified)', 'No model/service request path', 'Explicit illustrative mode labels');
  const pairs = [['ink/paper', '#12251f', '#f7f5ee'], ['muted/paper', '#586c62', '#f7f5ee'], ['white/forest', '#ffffff', '#0a6650'], ['ink/lime', '#12251f', '#d9ff6e'], ['amber/pale', '#805000', '#fff2d5']];
  function luminance(h) {
    const a = h.slice(1).match(/../g).map(x => parseInt(x, 16) / 255).map(x => x <= .04045 ? x / 12.92 : ((x + .055) / 1.055) ** 2.4);
    return .2126 * a[0] + .7152 * a[1] + .0722 * a[2];
  }
  const contrast = Object.fromEntries(pairs.map(([name, a, b]) => {
    const ratio = (Math.max(luminance(a), luminance(b)) + .05) / (Math.min(luminance(a), luminance(b)) + .05);
    assert(ratio >= 4.5, 'Contrast pair failed ' + name);
    return [name, Number(ratio.toFixed(2))];
  }));
  checks.push('Five proposed solid-color text pair ratios exceed 4.5:1');
  const artifacts = [doc, htmlPath, 'docs/design/validate-study.cjs'];
  const result = {
    check_id: 'ui-design-research-concept', run_utc: new Date().toISOString(),
    command: 'node docs/design/validate-study.cjs', working_directory: root,
    source_revision: cp.execFileSync('git', ['rev-parse', 'HEAD'], { cwd: root, encoding: 'utf8' }).trim(),
    mode: 'documentation_and_isolated_concept', outcome: 'passed', exit_code: 0, checks, contrast,
    artifact_sha256: Object.fromEntries(artifacts.map(p => [p, crypto.createHash('sha256').update(fs.readFileSync(path.join(root, p))).digest('hex')])),
    application_source_changed_by_this_task: false, application_tests_run: false,
    real_ai_calls_run: false, browser_visual_qa_run: false, merchant_usability_tested: false,
    limitation: 'Browser initialization failed. Syntax/hooks and example arithmetic do not establish rendered layout, motion, full accessibility, conversion or runtime performance. Study uses device font fallbacks; no font assets bundled. Concurrent application changes belong to the other developer.'
  };
  const output = path.join(root, 'docs/evidence/ui-design-research-2026-11-23/concept-validation.json');
  fs.mkdirSync(path.dirname(output), { recursive: true });
  fs.writeFileSync(output, JSON.stringify(result, null, 2) + '\n');
  process.stdout.write(`PASS: ${checks.length} structural/example checks and 5 contrast pairs. Browser and application verification not run.\n`);
} catch (error) {
  process.stderr.write('FAIL: design study validation: ' + error.message + '\n');
  process.exitCode = 1;
}
