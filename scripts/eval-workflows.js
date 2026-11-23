#!/usr/bin/env node
// Execute actual API/domain workflow tests in isolated databases.
const {spawnSync}=require('node:child_process');
const path=require('node:path');
const live=process.argv.includes('--live');
console.log(live?'Actual configured provider/application verification; bounded synthetic requests may incur usage.':'Offline contract tests with explicit provider doubles; no live-provider or benchmark claim.');
const args=live?["-m","pytest","apps/api/tests/test_merchant_workflow.py","apps/api/tests/test_daily_posting_guards.py","apps/api/tests/test_daily_posting_race.py","apps/api/tests/test_buying_desk.py","apps/api/tests/test_receiving_and_returns.py","apps/api/tests/test_credit_acceptance.py","apps/api/tests/test_demand_memory.py","apps/api/tests/test_notifications.py","apps/api/tests/test_operations.py","apps/api/tests/test_business_help.py","-q","-p","no:cacheprovider"]:["-m","pytest","apps/api/tests/test_merchant_workflow.py","apps/api/tests/test_daily_posting_guards.py","apps/api/tests/test_daily_posting_race.py","apps/api/tests/test_buying_desk.py","apps/api/tests/test_receiving_and_returns.py","apps/api/tests/test_credit_acceptance.py","apps/api/tests/test_demand_memory.py","apps/api/tests/test_notifications.py","apps/api/tests/test_operations.py","apps/api/tests/test_business_help.py","-q","-p","no:cacheprovider"];
const result=spawnSync(process.execPath,['scripts/run-python.js',...args],{cwd:path.resolve(__dirname,'..'),stdio:'inherit',windowsHide:true});
if(result.error)console.error('Runner failed to start.');
process.exit(Number.isInteger(result.status)?result.status:1);
