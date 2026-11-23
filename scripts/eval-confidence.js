#!/usr/bin/env node
// Execute the actual versioned evidence-support policy tests, not copied expected scores.
const {spawnSync}=require('node:child_process');
const path=require('node:path');
const live=process.argv.includes('--live');
console.log(live?'Actual configured provider/application verification; bounded synthetic requests may incur usage.':'Offline contract tests with explicit provider doubles; no live-provider or benchmark claim.');
const args=live?["-m","pytest","apps/api/tests/test_confidence_and_cases.py","apps/api/tests/test_agents.py","-q","-p","no:cacheprovider"]:["-m","pytest","apps/api/tests/test_confidence_and_cases.py","apps/api/tests/test_agents.py","-q","-p","no:cacheprovider"];
const result=spawnSync(process.execPath,['scripts/run-python.js',...args],{cwd:path.resolve(__dirname,'..'),stdio:'inherit',windowsHide:true});
if(result.error)console.error('Runner failed to start.');
process.exit(Number.isInteger(result.status)?result.status:1);
