#!/usr/bin/env node
// Documentation/fixture validation only. This never validates the application or AI.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { execFileSync } = require('node:child_process');

const root = path.resolve(__dirname, '..');
const read = p => fs.readFileSync(path.join(root, p), 'utf8').replace(/^\uFEFF/, '');
const checks = [];
function check(condition, message) {
  if (!condition) throw new Error(message);
  checks.push(message);
}

try {
  const plan = read('EXTENSION_PLAN.md');
  const tracker = JSON.parse(read('docs/progress.json'));
  const fixture = JSON.parse(read('tests/fixtures/extension-handoff/confidence-policy-v1.json'));
  const phaseDefs = [...plan.matchAll(/^### Phase (\d{2}) — (.+)$/gm)];
  const extensionIds = Array.from({ length: 14 }, (_, i) => String(i + 13));
  const phases = tracker.phases;
  const phaseMap = new Map(phases.map(p => [p.id, p]));
  check(phaseMap.size === phases.length, 'Unique phase IDs');
  check(extensionIds.every(id => phaseMap.has(id)), 'All 14 extension phases tracked');
  check(Array.from({ length: 13 }, (_, i) => String(i).padStart(2, '0')).every(id => phaseMap.has(id)), 'Original 00-12 phase IDs preserved');
  check(phaseDefs.length === 14 && phaseDefs.every((m, i) => m[1] === extensionIds[i]), 'Plan defines ordered Phase 13-26 exactly once');
  check(tracker.extension.contract === 'EXTENSION_PLAN.md' && tracker.extension.starting_prompt === 'START_EXTENSION.md', 'Current contract and starting prompt are explicit');
  check(tracker.extension.application_features_implemented_by_handoff === false, 'Handoff does not claim application implementation');
  check(JSON.stringify(tracker.extension.phase_ids) === JSON.stringify(extensionIds), 'Extension phase metadata agrees');

  const taskMap = new Map();
  for (const p of phases) {
    for (const t of p.tasks) {
      check(!taskMap.has(t.id), `Unique task ${t.id}`);
      check(t.id.startsWith(`P${p.id}-T`), `Task belongs to phase: ${t.id}`);
      check(['not_started', 'in_progress', 'blocked', 'complete'].includes(t.status), `Valid state: ${t.id}`);
      taskMap.set(t.id, t);
    }
  }
  let newTaskCount = 0;
  phaseDefs.forEach((m, i) => {
    const end = i + 1 < phaseDefs.length ? phaseDefs[i + 1].index : plan.indexOf('\n## G.', m.index);
    const taskIds = [...plan.slice(m.index, end).matchAll(/^- \*\*(P\d{2}-T\d{2}) —/gm)].map(t => t[1]);
    const phase = phaseMap.get(m[1]);
    check(phase.name === m[2], `Phase title matches contract: ${m[1]}`);
    check(JSON.stringify(taskIds) === JSON.stringify(phase.tasks.map(t => t.id)), `Task definitions match tracker: phase ${m[1]}`);
    check(phase.git_checkpoint.required && phase.git_checkpoint.remote === 'origin', `Mandatory origin checkpoint: phase ${m[1]}`);
    if (phase.status === 'complete') {
      check(phase.tasks.every(t => t.status === 'complete' && t.evidence.length > 0), `Completion has task evidence: phase ${m[1]}`);
      check(phase.git_checkpoint.status === 'published' && /^[0-9a-f]{40}$/.test(phase.git_checkpoint.milestone_sha || ''), `Completion has recorded published checkpoint: phase ${m[1]}`);
      check(phase.depends_on.every(id => phaseMap.get(id)?.status === 'complete'), `Completion dependencies satisfied: phase ${m[1]}`);
    }
    newTaskCount += taskIds.length;
  });
  check(newTaskCount === 59 && tracker.extension.task_count === newTaskCount, '59 extension tasks agree with tracker');
  if (tracker.next_task !== null) {
    check(taskMap.has(tracker.next_task) && taskMap.get(tracker.next_task).status !== 'complete', 'Next task exists and remains unfinished');
    check(tracker.next_task.startsWith(`P${tracker.current_phase}-`), 'Current phase agrees with next task');
  }
  const visited = new Set();
  const visiting = new Set();
  function visit(id) {
    if (visited.has(id)) return;
    check(!visiting.has(id), `No dependency cycle at phase ${id}`);
    visiting.add(id);
    for (const dep of phaseMap.get(id).depends_on || []) {
      check(phaseMap.has(dep), `Dependency exists: ${id}->${dep}`);
      visit(dep);
    }
    visiting.delete(id);
    visited.add(id);
  }
  for (const p of phases) visit(p.id);

  const docs = ['EXTENSION_PLAN.md', 'START_EXTENSION.md', 'START_HERE.md', 'AGENTS.md', 'README.md', 'plan.md',
    'docs/PROGRESS.md', 'docs/EXTENSION_PROGRESS.md', 'docs/VALIDATION.md', 'docs/DECISIONS.md',
    'docs/KNOWN_ISSUES.md', 'docs/research/2026-11-23-product-innovation-review.md'];
  let localLinks = 0;
  for (const doc of docs) {
    for (const m of read(doc).matchAll(/\]\(([^)]+)\)/g)) {
      const dest = m[1].replace(/^<|>$/g, '').split('#')[0];
      if (!dest || /^[a-z]+:\/\//i.test(dest)) continue;
      const target = path.resolve(root, path.dirname(doc), dest);
      check(fs.existsSync(target), `Local link resolves: ${doc} -> ${dest}`);
      localLinks++;
    }
  }
  check(read('START_HERE.md').includes('START_EXTENSION.md'), 'Main start entry discovers new prompt');
  check(read('AGENTS.md').includes('EXTENSION_PLAN.md'), 'Persistent rules discover extension contract');
  check(read('docs/EXTENSION_PROGRESS.md').includes('59 tasks'), 'Human extension task count agrees');

  check(fixture.synthetic === true && fixture.not_a_correctness_probability === true, 'Confidence fixtures explicitly synthetic and uncalibrated');
  check(fixture.policy_version === 'evidence-support-v1' && fixture.critical_cap === 59, 'Fixture policy agrees with contract');
  check(fixture.cases.length === 11, '11 independent confidence examples present');
  const caseIds = new Set();
  for (const c of fixture.cases) {
    check(!caseIds.has(c.id), `Unique confidence example: ${c.id}`);
    caseIds.add(c.id);
    const claimKeys = new Set(c.claims.map(x => x.key));
    check(claimKeys.size === c.claims.length, `No duplicate claims: ${c.id}`);
    check(c.claims.every(x => ['supported', 'unknown', 'conflicted', 'unsupported'].includes(x.state)), `Valid claim states: ${c.id}`);
    let base = null, score = null, band = 'unavailable', readiness = c.blocking_validation_failure ? 'blocked' : 'unavailable';
    if (!c.blocking_validation_failure && !c.unavailable_reason && c.claims.length) {
      const weight = x => x.critical ? fixture.weights.critical : fixture.weights.ordinary;
      const denominator = c.claims.reduce((sum, x) => sum + weight(x), 0);
      const numerator = c.claims.filter(x => x.state === 'supported').reduce((sum, x) => sum + weight(x), 0);
      base = Math.floor(100 * numerator / denominator + 0.5);
      const unresolvedCritical = c.claims.some(x => x.critical && x.state !== 'supported');
      score = unresolvedCritical ? Math.min(base, fixture.critical_cap) : base;
      band = score >= 85 ? 'strong' : score >= 60 ? 'review' : 'limited';
      readiness = unresolvedCritical || score < 60 ? 'needs_clarification' : score < 85 ? 'needs_review' : 'ready_for_review';
    }
    const expected = c.expected;
    check(expected.base_score === base && expected.score === score && expected.band === band && expected.readiness === readiness, `Confidence arithmetic/routing derivation: ${c.id}`);
    check(expected.can_execute_without_approval === false, `Score never grants execution authority: ${c.id}`);
  }

  const artifacts = [...docs, 'docs/progress.json', 'tests/fixtures/extension-handoff/confidence-policy-v1.json', 'scripts/validate-extension-handoff.cjs'];
  const hashes = Object.fromEntries(artifacts.map(p => [p, crypto.createHash('sha256').update(fs.readFileSync(path.join(root, p))).digest('hex')]));
  const evidence = {
    check_id: 'extension-v1-handoff-consistency', run_utc: new Date().toISOString(),
    command: 'node scripts/validate-extension-handoff.cjs', working_directory: root,
    source_revision: execFileSync('git', ['rev-parse', 'HEAD'], { cwd: root, encoding: 'utf8' }).trim(),
    tree_context: 'Documentation/fixture working tree; hashes identify the checked files, not a completed application phase.',
    mode: 'documentation', outcome: 'passed', exit_code: 0,
    extension_phases: extensionIds.length, extension_tasks: newTaskCount, confidence_examples: fixture.cases.length,
    local_links_checked: localLinks, assertions_passed: checks.length,
    application_tests_run: false, live_provider_calls_run: false, browser_checks_run: false,
    financial_integration_verified: false, calibrated_probability_verified: false,
    limitation: 'Structural links, task/dependency/tracker consistency and fixture derivations only. Published checkpoint claims still require actual Git verification; no runtime capability is certified.',
    artifact_sha256: hashes
  };
  fs.mkdirSync(path.join(root, 'docs/evidence'), { recursive: true });
  fs.writeFileSync(path.join(root, 'docs/evidence/extension-handoff-validation.json'), JSON.stringify(evidence, null, 2) + '\n');
  process.stdout.write(`PASS: ${extensionIds.length} phases, ${newTaskCount} tasks, ${fixture.cases.length} confidence contracts, ${localLinks} local links. Documentation only; no application/AI/browser verification.\n`);
} catch (error) {
  process.stderr.write(`FAIL: extension handoff validation: ${error.message}\n`);
  process.exitCode = 1;
}
