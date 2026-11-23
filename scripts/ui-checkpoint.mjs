// Explicit UI checkpoint publication; stage only named files, never unrelated working changes.
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
const [phase,...files]=process.argv.slice(2),root=process.cwd();
if(!/^UIR-0\d$/.test(phase)||!files.length)throw new Error('Usage: node scripts/ui-checkpoint.mjs UIR-XX <explicit files...>');
const git=(...args)=>{const r=spawnSync('git',['-c','safe.directory='+root.replaceAll('\\','/'),...args],{cwd:root,encoding:'utf8'});if(r.status!==0)throw new Error((r.stderr||r.stdout||'Git operation failed').trim());return r.stdout.trim();};
if(git('branch','--show-current')!=='main')throw new Error('UI execution is authorized on main only');
if(git('diff','--cached','--name-only'))throw new Error('Existing staged work must be reviewed before a checkpoint');
if(files.some(f=>f==='.'||f==='docs'||f==='docs/DATABASE_SETUP.md'))throw new Error('Specify task-owned files; preserve unrelated database notes');
const trackerPath='docs/ui-redesign-progress.json',progress=JSON.parse(fs.readFileSync(trackerPath,'utf8')),entry=progress.phases.find(p=>p.id===phase);
if(!entry)throw new Error('Unknown UI phase');
entry.status='verified_pending_publication';progress.current_phase=phase;fs.writeFileSync(trackerPath,JSON.stringify(progress,null,2)+'\n');
git('add','--',...files,trackerPath);git('diff','--cached','--check');
git('commit','-m',`feat(${phase.toLowerCase()}): ${entry.name}`,'-m',`Shongoti-UI-Phase: ${phase}`);
const milestone=git('rev-parse','HEAD');
try{
  git('push','origin','main');const remote=git('ls-remote','--heads','origin','refs/heads/main').split(/\s/)[0];if(remote!==milestone)throw new Error('Remote tip differs from published milestone; inspect concurrent work');
  const receiptPath=`docs/evidence/ui-redesign/${phase}/git-checkpoint.json`;
  fs.mkdirSync(path.dirname(receiptPath),{recursive:true});fs.writeFileSync(receiptPath,JSON.stringify({phase_id:phase,status:'milestone_published',remote:'https://github.com/sakibul-shovon/Shongoti.git',branch:'main',milestone_sha:milestone,verified_remote_tip_at_milestone:remote,verified_at_utc:new Date().toISOString(),verification:'Normal push and exact ls-remote main tip match.'},null,2)+'\n');
  entry.status='complete';entry.git_checkpoint={status:'milestone_published',milestone_sha:milestone,receipt:receiptPath};fs.writeFileSync(trackerPath,JSON.stringify(progress,null,2)+'\n');
  git('add','--',receiptPath,trackerPath);git('commit','-m',`docs(${phase.toLowerCase()}): record published checkpoint`,'-m',`Shongoti-UI-Checkpoint-Receipt: ${phase}`);git('push','origin','main');
  const tip=git('rev-parse','HEAD'),published=git('ls-remote','--heads','origin','refs/heads/main').split(/\s/)[0];if(tip!==published)throw new Error('Receipt tip publication not verified');console.log(JSON.stringify({phase,milestone,receipt_tip:tip,published:true}));
}catch(error){entry.status='publication_blocked';entry.git_checkpoint={status:'blocked',milestone_sha:milestone,error:error.message};fs.writeFileSync(trackerPath,JSON.stringify(progress,null,2)+'\n');throw error;}
