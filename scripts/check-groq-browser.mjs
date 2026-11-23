// Real Chromium/CDP checks against this local preview only; no existing browser profile.
import { spawn } from 'node:child_process';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
const dir=path.resolve('docs/evidence/real-workflow/JR-02');
const base='http://127.0.0.1:5173';
const profile=path.resolve('tmp','react-ui-qa-'+Date.now());
await fs.mkdir(path.join(dir,'evidence'),{recursive:true});
const browser=spawn('C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',['--headless','--disable-gpu','--no-first-run','--no-default-browser-check','--remote-debugging-port=0','--user-data-dir='+profile,'about:blank'],{windowsHide:true,stdio:['ignore','ignore','pipe']});
let browserLog='';browser.stderr.on('data',chunk=>{browserLog=(browserLog+chunk).slice(-3000);});
const sleep=ms=>new Promise(resolve=>setTimeout(resolve,ms));
const report={date:new Date().toISOString(),mode:'actual_groq_multimodal_judge',browser:'installed Chrome, isolated headless profile',checks:[],screenshots:[],errors:[],passed:false};
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

  const uploadPath=path.resolve('tmp/groq-live/unseen-invoice.png');
  await nav('/app/evidence','.upload-label');await call('DOM.enable');let document=await call('DOM.getDocument');let input=await call('DOM.querySelector',{nodeId:document.root.nodeId,selector:'.upload-label input[type=file]'});await call('DOM.setFileInputFiles',{nodeId:input.nodeId,files:[uploadPath]});
  await wait('document.querySelector(".extracted-source")?.textContent.includes("LIVE-")',90000);await wait('document.querySelector(".inference-receipts")?.textContent.includes("qwen/")');
  assert.ok(await evaluate('document.querySelector(".evidence-detail").textContent.includes("1,763.55")'));report.checks.push('Unseen image uses real Groq vision and renders extracted text, exact amount and actual receipt');
  for(const width of [1440,768,360]){await call('Emulation.setDeviceMetricsOverride',{width,height:1050,deviceScaleFactor:1,mobile:width===360});await shot('actual-image-'+width);assert.ok(await evaluate('document.documentElement.scrollWidth<=innerWidth+1'));}
  await nav('/app/copilot','.voice-studio');
  document=await call('DOM.getDocument');input=await call('DOM.querySelector',{nodeId:document.root.nodeId,selector:'.voice-studio input[type=file]'});await call('DOM.setFileInputFiles',{nodeId:input.nodeId,files:[path.resolve('tmp/groq-live/merchant-voice.wav')]});await wait('!!document.querySelector(".clip-review")');await click('.clip-review .primary');
  await wait('document.querySelector(".proposed-operations")?.textContent.includes("debt collection")',90000);assert.ok(await evaluate('document.querySelector(".proposed-operations").textContent.includes("credit sale")'));assert.ok(await evaluate('document.querySelector(".proposed-operations").textContent.includes("500")'));assert.ok(await evaluate('document.querySelector(".inference-receipts").textContent.includes("whisper-large-v3")'));report.checks.push('Actual audio produces separately reviewable debt collection and credit sale with Whisper receipt and retained source');
  for(const width of [1440,768,360]){await call('Emulation.setDeviceMetricsOverride',{width,height:1050,deviceScaleFactor:1,mobile:width===360});await shot('actual-voice-'+width);assert.ok(await evaluate('document.documentElement.scrollWidth<=innerWidth+1'));}
  await evaluate('(()=>{const el=document.querySelector("#copilot-query");Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,"value").set.call(el,"What is my actual liquid cash, excluding customer dues? Cite the ledger source.");el.dispatchEvent(new Event("input",{bubbles:true}));})()');await click('.chat-composer button');await wait('document.querySelectorAll(".chat-message.assistant").length===2',90000);assert.ok(await evaluate('document.querySelector(".chat-message.assistant:last-of-type").textContent.includes("12,000")'));report.checks.push('Actual grounded chat answers from current persisted ledger and renders provider receipt');await shot('actual-chat-360');
  await call('Page.reload');await wait('!!document.querySelector(".conversation-list button")');await click('.conversation-list button');await wait('document.querySelectorAll(".chat-message.assistant").length===2');report.checks.push('Real transcript, proposals and chat receipts survive reload and history reopening');
  assert.equal(report.errors.length,0,'Unexpected browser runtime errors');report.passed=true;
  await call('Browser.close').catch(()=>{});
}catch(error){report.failure=error.message;console.error(error.message);process.exitCode=1;}
finally{socket?.close();browser.kill();await fs.writeFile(path.join(dir,'evidence','browser-report.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({passed:report.passed,checks:report.checks.length,screenshots:report.screenshots.length,failure:report.failure}));}
