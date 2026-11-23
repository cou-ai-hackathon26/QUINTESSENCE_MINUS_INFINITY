// Real Chromium/CDP checks against this local preview only; no existing browser profile.
import { spawn } from 'node:child_process';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
const dir=path.resolve('docs/evidence/real-workflow/JR-01');
const base='http://127.0.0.1:5173';
const profile=path.resolve('tmp','react-ui-qa-'+Date.now());
await fs.mkdir(path.join(dir,'evidence'),{recursive:true});
const browser=spawn('C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',['--headless','--disable-gpu','--no-first-run','--no-default-browser-check','--remote-debugging-port=0','--user-data-dir='+profile,'about:blank'],{windowsHide:true,stdio:['ignore','ignore','pipe']});
let browserLog='';browser.stderr.on('data',chunk=>{browserLog=(browserLog+chunk).slice(-3000);});
const sleep=ms=>new Promise(resolve=>setTimeout(resolve,ms));
const report={date:new Date().toISOString(),mode:'main_react_foundation_judge',browser:'installed Chrome, isolated headless profile',checks:[],screenshots:[],errors:[],passed:false};
let socket;
try{
  let port;
  for(let i=0;i<60;i++){try{port=(await fs.readFile(path.join(profile,'DevToolsActivePort'),'utf8')).split('\n')[0];break;}catch{await sleep(200);}}
  if(!port)throw new Error('Chrome debugging endpoint unavailable: '+browserLog.slice(-600));
  const targets=await (await fetch('http://127.0.0.1:'+port+'/json/list')).json();
  const target=targets.find(t=>t.type==='page');if(!target)throw new Error('No isolated test page');
  socket=new WebSocket(target.webSocketDebuggerUrl);await new Promise((resolve,reject)=>{socket.addEventListener('open',resolve,{once:true});socket.addEventListener('error',reject,{once:true});});
  let id=0;const pending=new Map();
  socket.addEventListener('message',event=>{const message=JSON.parse(event.data);if(message.id){const request=pending.get(message.id);if(request){pending.delete(message.id);clearTimeout(request.timer);message.error?request.reject(new Error(JSON.stringify(message.error))):request.resolve(message.result);}}else if(message.method==='Runtime.exceptionThrown')report.errors.push(message.params.exceptionDetails.text+': '+(message.params.exceptionDetails.exception?.description||''));});
  const call=(method,params={})=>new Promise((resolve,reject)=>{const current=++id;const timer=setTimeout(()=>{pending.delete(current);reject(new Error('CDP timeout: '+method));},12000);pending.set(current,{resolve,reject,timer});socket.send(JSON.stringify({id:current,method,params}));});
  const evaluate=async expression=>{const result=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(result.exceptionDetails)throw new Error(result.exceptionDetails.exception?.description||result.exceptionDetails.text);return result.result.value;};
  const wait=async(expression,timeout=10000)=>{const end=Date.now()+timeout;while(Date.now()<end){if(await evaluate(expression))return;await sleep(100);}throw new Error('Condition failed: '+expression);};
  const click=async selector=>{await evaluate(`document.querySelector(${JSON.stringify(selector)})?.click()`);};
  const shot=async name=>{await evaluate('Promise.race([document.fonts.ready,new Promise(resolve=>setTimeout(resolve,2000))])');await sleep(350);const result=await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:true});await fs.writeFile(path.join(dir,'evidence',name+'.png'),Buffer.from(result.data,'base64'));report.screenshots.push(name+'.png');};
  await call('Runtime.enable');await call('Page.enable');
  await call('Emulation.setDeviceMetricsOverride',{width:1440,height:1050,deviceScaleFactor:1,mobile:false});
  const fill=async(selector,value)=>evaluate('(()=>{const el=document.querySelector('+JSON.stringify(selector)+');Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,"value").set.call(el,'+JSON.stringify(value)+');el.dispatchEvent(new Event("input",{bubbles:true}));})()');
  const nav=async(path,selector)=>{await click('a[href="'+path+'"]');await wait('!!document.querySelector('+JSON.stringify(selector)+')');};
  const confirm=async()=>{await wait('!!document.querySelector("[role=dialog]")');assert.ok(await evaluate('document.querySelector("[role=dialog] .primary").disabled'));await click('[role=dialog] input[type=checkbox]');await click('[role=dialog] .primary');await wait('!document.querySelector("[role=dialog]")');await wait('!!document.querySelector(".mutation-receipt")');};
  await call('Page.navigate',{url:base+'/login'});await wait('!!document.querySelector(".judge-button")');await click('.judge-button');await wait('!!document.querySelector(".home-workbench")');
  const identity=await evaluate('fetch("/api/v1/auth/me").then(r=>r.json())');assert.ok(identity.case_id&&!identity.case_id.includes('demo-case'));assert.equal(identity.execution_mode,'persistent_api');
  await evaluate('location.href='+JSON.stringify('/app/cases/')+'+'+JSON.stringify(identity.case_id));await wait('document.querySelectorAll(".source-paper input")[1]?.value==="25000"');await evaluate('document.querySelectorAll(".answer-buttons button")[1].click()');await wait('document.querySelector(".payable-alternatives")?.textContent.includes("18,000")');report.checks.push('Persisted judge case sources are loaded from the API and actual clarification resolves 18,000');await shot('persistent-case-1440');
  await call('Page.reload');await wait('document.querySelector(".answer-buttons button[aria-pressed=true]")?.textContent.includes("not yet")||document.querySelectorAll(".answer-buttons button")[1]?.getAttribute("aria-pressed")==="true"');report.checks.push('Case inputs and assessment survive actual browser reload');
  const uploadPath=path.resolve('tmp','unseen-judge-source.txt');await fs.writeFile(uploadPath,'Unseen uploaded source TEST-883. Merchant sample bill BDT 765.43.');await nav('/app/evidence','.upload-label');await call('DOM.enable');const document=await call('DOM.getDocument');const input=await call('DOM.querySelector',{nodeId:document.root.nodeId,selector:'.upload-label input[type=file]'});await call('DOM.setFileInputFiles',{nodeId:input.nodeId,files:[uploadPath]});await wait('location.pathname.startsWith("/app/evidence/")');await wait('document.querySelector(".evidence-detail h2")?.textContent==="unseen-judge-source.txt"');const evidenceId=await evaluate('location.pathname.split("/").pop()');const original=await evaluate('fetch("/api/v1/evidence/"+'+JSON.stringify(evidenceId)+'+"/content").then(r=>r.text())');assert.ok(original.includes('TEST-883'));await call('Page.reload');await wait('document.querySelector(".evidence-detail h2")?.textContent==="unseen-judge-source.txt"');report.checks.push('New judge upload reaches the real API, is downloadable and survives reload');await shot('uploaded-judge-file-1440');
  await nav('/app/sales','.summary-strip');await fill('.workspace-form input[inputmode=decimal]','100.25');await click('.workspace-form .primary');await confirm();await nav('/app/money','.account-cards');await wait('document.querySelector(".account-cards").textContent.includes("5,100.25")');await call('Page.reload');await wait('document.querySelector(".account-cards")?.textContent.includes("5,100.25")');report.checks.push('Judge sale posts an actual ledger entry and the updated balance survives reload');
  for(const width of [1440,768,360]){await call('Emulation.setDeviceMetricsOverride',{width,height:1050,deviceScaleFactor:1,mobile:width===360});await shot('persistent-money-'+width);assert.ok(await evaluate('document.documentElement.scrollWidth<=innerWidth+1'));}
  assert.equal(report.errors.length,0,'Unexpected browser runtime errors');report.passed=true;
  await call('Browser.close').catch(()=>{});
}catch(error){report.failure=error.message;console.error(error.message);process.exitCode=1;}
finally{socket?.close();browser.kill();await fs.writeFile(path.join(dir,'evidence','browser-report.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({passed:report.passed,checks:report.checks.length,screenshots:report.screenshots.length,failure:report.failure}));}
