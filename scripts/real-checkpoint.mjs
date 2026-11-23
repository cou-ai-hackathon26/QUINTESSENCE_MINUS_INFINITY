import fs from 'node:fs';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
const [phase,...files]=process.argv.slice(2),root=process.cwd();
if(!/^JR-0[1-4]$/.test(phase)||!files.length)throw new Error('Specify a real-workflow phase and explicit task files');
const git=(...args)=>{const r=spawnSync('git',['-c','safe.directory='+root.replaceAll('\\','/'),...args],{cwd:root,encoding:'utf8'});if(r.status!==0)throw new Error((r.stderr||r.stdout).trim());return r.stdout.trim();};
if(git('branch','--show-current')!=='main'||git('diff','--cached','--name-only'))throw new Error('Require main and a reviewed empty index');
if(files.some(p=>p==='.'||p==='docs'||p.endsWith('.env')||p==='docs/DATABASE_SETUP.md'))throw new Error('Explicit task files only; secrets and unrelated notes must stay out');
const tracker='docs/real-workflow-progress.json',progress=JSON.parse(fs.readFileSync(tracker,'utf8')),entry=progress.phases.find(p=>p.id===phase);
if(!entry)throw new Error('Unknown phase');entry.status='verified_pending_publication';fs.writeFileSync(tracker,JSON.stringify(progress,null,2)+'\n');
git('add','--',...files,tracker);git('diff','--cached','--check');git('commit','-m',`fix(${phase.toLowerCase()}): ${entry.scope}`,'-m',`Shongoti-Real-Phase: ${phase}`);const milestone=git('rev-parse','HEAD');
try{git('push','origin','main');let remote=git('ls-remote','--heads','origin','refs/heads/main').split(/\s/)[0];if(remote!==milestone)throw new Error('Milestone remote tip mismatch');
 const receipt=`docs/evidence/real-workflow/${phase}/git-checkpoint.json`;fs.mkdirSync(path.dirname(receipt),{recursive:true});fs.writeFileSync(receipt,JSON.stringify({phase,status:'published',milestone_sha:milestone,verified_remote_tip:remote,verified_at:new Date().toISOString()},null,2)+'\n');entry.status='complete';entry.git_checkpoint={status:'published',milestone_sha:milestone,receipt};fs.writeFileSync(tracker,JSON.stringify(progress,null,2)+'\n');git('add','--',tracker,receipt);git('commit','-m',`docs(${phase.toLowerCase()}): publish verified checkpoint receipt`);git('push','origin','main');remote=git('ls-remote','--heads','origin','refs/heads/main').split(/\s/)[0];if(remote!==git('rev-parse','HEAD'))throw new Error('Receipt remote tip mismatch');console.log(JSON.stringify({phase,milestone,receipt_tip:remote,published:true}));
}catch(error){entry.status='publication_blocked';entry.git_checkpoint={status:'blocked',milestone_sha:milestone,error:error.message};fs.writeFileSync(tracker,JSON.stringify(progress,null,2)+'\n');throw error;}
