// Real Chromium/CDP checks against this local preview only; no existing browser profile.
import { spawn } from 'node:child_process';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
const dir=path.resolve('docs/evidence/ui-redesign/UIR-01');
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
  await call('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
  await call('Page.navigate',{url:base+'/login'});await wait('!!document.querySelector(".judge-button")');
  for(const width of [1440,768,360]){await call('Emulation.setDeviceMetricsOverride',{width,height:1000,deviceScaleFactor:1,mobile:width===360});await shot('login-'+width);assert.ok(await evaluate('document.documentElement.scrollWidth<=innerWidth+1'));}
  await call('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
  await click('.judge-button');await wait('!!document.querySelector(".wb-sidebar")');
  assert.ok(await evaluate('document.querySelector(".workspace-mode").textContent.includes("Judge")'));
  report.checks.push('Judge cookie session opens protected React shell');await shot('shell-1440');
  await click('.profile-button');await wait('!!document.querySelector("[role=dialog]")');
  await call('Input.dispatchKeyEvent',{type:'keyDown',key:'Escape',code:'Escape'});await wait('!document.querySelector("[role=dialog]")');
  report.checks.push('Profile dialog keyboard Escape closes and restores focus');
  assert.equal(report.errors.length,0,'Unexpected browser runtime errors');report.passed=true;
  await call('Browser.close').catch(()=>{});
}catch(error){report.failure=error.message;console.error(error.message);process.exitCode=1;}
finally{socket?.close();browser.kill();await fs.writeFile(path.join(dir,'evidence','browser-report.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({passed:report.passed,checks:report.checks.length,screenshots:report.screenshots.length,failure:report.failure}));}
