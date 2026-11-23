// Reproducible local checks. Tests never use the developer's default merchant database.
import fs from 'node:fs';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
const root=process.cwd(),dir=path.join(root,'docs/evidence/ui-redesign/UIR-09');
fs.mkdirSync(dir,{recursive:true});
const env={...process.env,DATABASE_URL:'sqlite:///:memory:',ENVIRONMENT:'development',SECRET_KEY:'synthetic-ui-test-only-not-a-production-key',GEMINI_API_KEY:'',SSLCOMMERZ_STORE_ID:'',SSLCOMMERZ_STORE_PASS:''};
const checks=[['api',['node',['scripts/run-python.js','-m','pytest','apps/api/tests','-q','-p','no:cacheprovider','--tb=short']]],['web',['pnpm',['--filter','@shongoti/web','test','--run']]],['build',['pnpm',['--filter','@shongoti/web','build']]]];
const results=[];
for(const [name,[command,args]] of checks){
  console.log('Running '+name+' checks…');const started=Date.now();
  const options={cwd:root,env,encoding:'utf8',maxBuffer:8*1024*1024,windowsHide:true};
  const run=process.platform==='win32'&&command==='pnpm'?spawnSync(process.env.ComSpec||'C:\Windows\System32\cmd.exe',['/d','/s','/c','pnpm.cmd '+args.join(' ')],options):spawnSync(command,args,options);
  const output=((run.stdout||'')+(run.stderr||'')).replace(/[[0-9;]*m/g,'').replaceAll(root,'<repository>');
  fs.writeFileSync(path.join(dir,name+'-checks.log'),output);
  const row={name,command:[command,...args].join(' '),exit_code:run.status,elapsed_ms:Date.now()-started,log:name+'-checks.log'};results.push(row);console.log(JSON.stringify(row));
  if(run.status!==0){process.exitCode=1;break;}
}
const sources={};
function walk(directory){for(const entry of fs.readdirSync(path.join(root,directory),{withFileTypes:true})){const rel=directory+'/'+entry.name;if(entry.isDirectory())walk(rel);else if(/\.(tsx?|css|py)$/.test(rel))sources[rel]=createHash('sha256').update(fs.readFileSync(path.join(root,rel))).digest('hex');}}
for(const folder of ['apps/web/src/workbench','apps/api/app/api/v1'])walk(folder);
sources['apps/web/src/App.tsx']=createHash('sha256').update(fs.readFileSync('apps/web/src/App.tsx')).digest('hex');
fs.writeFileSync(path.join(dir,'local-checks.json'),JSON.stringify({date:new Date().toISOString(),scope:'Local automated tests and production build; browser evidence is separate',test_database:'isolated in-memory fallback; per-test database overrides',provider_calls:'disabled in this check run',checks:results,source_sha256:sources,passed:results.length===3&&results.every(r=>r.exit_code===0)},null,2)+'\n');
