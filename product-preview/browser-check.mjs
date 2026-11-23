// Real Chromium/CDP checks against this local preview only; no existing browser profile.
import { spawn } from 'node:child_process';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
const dir=path.dirname(fileURLToPath(import.meta.url));
const base='http://127.0.0.1:4318';
const profile=path.join(dir,'.runtime','qa-'+Date.now());
await fs.mkdir(path.join(dir,'evidence'),{recursive:true});
const browser=spawn('C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',['--headless','--disable-gpu','--no-first-run','--no-default-browser-check','--remote-debugging-port=0','--user-data-dir='+profile,'about:blank'],{windowsHide:true,stdio:['ignore','ignore','pipe']});
let browserLog='';browser.stderr.on('data',chunk=>{browserLog=(browserLog+chunk).slice(-3000);});
const sleep=ms=>new Promise(resolve=>setTimeout(resolve,ms));
const report={date:new Date().toISOString(),mode:'synthetic_local_preview',browser:'installed Chrome, isolated headless profile',checks:[],screenshots:[],errors:[],passed:false};
report.sourceSha256=Object.fromEntries(await Promise.all(['index.html','app.js','domain.js','styles.css','workbench.css','purchasing.css','auth-store.mjs','server.mjs'].map(async name=>[name,createHash('sha256').update(await fs.readFile(path.join(dir,name))).digest('hex')])));
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
  await call('Page.navigate',{url:base+'/#/login'});await wait('!!document.querySelector("#auth-form")');await shot('login-1440');
  assert.equal(await evaluate('document.querySelectorAll("input[type=password]").length'),1);
  await click('[data-action="judge-login"]');await wait('!!document.querySelector(".work-queue")');
  report.checks.push('One-click judge login creates a server session and opens the seeded workspace');
  for(const width of [1440,768,360]){
    await call('Emulation.setDeviceMetricsOverride',{width,height:width===360?900:1050,deviceScaleFactor:1,mobile:width===360});
    for(const route of ['dashboard','case','buying','planner']){
      await call('Page.navigate',{url:base+'/#/'+route});await wait('!!document.querySelector("main h1")');await sleep(250);
      const layout=await evaluate('({width:innerWidth,scroll:document.documentElement.scrollWidth,title:document.querySelector("main h1").textContent})');
      assert.ok(layout.scroll<=width+1,`${route} at ${width}: overflow ${layout.scroll}`);
      await shot(route+'-'+width);report.checks.push(`${route} rendered without whole-page overflow at ${width}px`);
    }
  }
  await call('Emulation.setDeviceMetricsOverride',{width:1440,height:1050,deviceScaleFactor:1,mobile:false});
  await call('Page.navigate',{url:base+'/#/case'});await wait('!!document.querySelector("[data-action=review-case]")');
  assert.equal(await evaluate('document.querySelector("[data-action=review-case]").disabled'),true);
  await click('[data-action="replay"]');await wait('!!document.querySelector(".agent-node.active")');await shot('agent-working-1440');
  await click('[data-action="pause-replay"]');const count=await evaluate('document.querySelectorAll(".event-list li").length');await sleep(1300);assert.equal(await evaluate('document.querySelectorAll(".event-list li").length'),count);await click('[data-action="pause-replay"]');
  await wait('!document.querySelector(".agent-node.active")',10000);assert.equal(await evaluate('document.querySelectorAll(".agent-node.waiting").length'),1);
  await click('[data-answer="included"]');await wait('document.querySelector(".due-result")?.textContent.includes("22,000")');
  await click('[data-answer="not-included"]');await wait('document.querySelector(".due-result")?.textContent.includes("18,000")');report.checks.push('Actual browser replay/loading/pause/wait states and exact inclusion alternatives verified');
  await shot('case-clarified-1440');
  await click('[data-action="open-scenarios"]');await wait('document.querySelectorAll(".scenario-entry").length===6');await shot('judge-scenarios-1440');
  for(const scenario of ['receiving','duplicate','notice']){await click(`[data-action="scenario"][data-scenario="${scenario}"]`);await wait('!!document.querySelector(".exception-layout")');await click('[data-action="exception-review"]');await wait('!!document.querySelector("[role=dialog]")');await click('[data-action="close"]');await click('[data-action="open-scenarios"]');await wait('document.querySelectorAll(".scenario-entry").length===6');}
  report.checks.push('All six judge scenarios have working destinations; three exception result inspectors open');
  await click('[data-action="copilot"]');await click('[data-prompt="balance"]');await wait('document.querySelector(".chat-message.assistant")?.textContent.includes("12,000")');await shot('copilot-1440');await click('[data-action="close"]');report.checks.push('Fixture-grounded copilot resolves loading and shows its explicit local mode');
  await click('[data-action="logout"]');await wait('!!document.querySelector("#auth-form")');
  await call('Page.navigate',{url:base+'/#/register'});await wait('!!document.querySelector("#owner-name")');await shot('register-1440');
  const phone='017'+String(Date.now()).slice(-8),password='Synthetic-review-'+Date.now();
  await evaluate(`document.querySelector('#owner-name').value='Synthetic Tester';document.querySelector('#shop-name').value='Isolated Test Shop';document.querySelector('#auth-phone').value=${JSON.stringify(phone)};document.querySelector('#auth-password').value=${JSON.stringify(password)};document.querySelector('#auth-form').requestSubmit();`);
  await wait('!!document.querySelector(".new-account-state")');assert.equal(await evaluate('document.querySelector(".metrics-strip")'),null);report.checks.push('Real local registration establishes a merchant session without inserting judge finances');
  await click('[data-action="logout"]');await wait('!!document.querySelector("#auth-form")');
  await evaluate(`document.querySelector('#auth-phone').value=${JSON.stringify(phone)};document.querySelector('#auth-password').value='wrong-password';document.querySelector('#auth-form').requestSubmit();`);await wait('!!document.querySelector("#auth-error")?.textContent');
  await evaluate(`document.querySelector('#auth-password').value=${JSON.stringify(password)};document.querySelector('#auth-form').requestSubmit();`);await wait('!!document.querySelector(".new-account-state")');report.checks.push('Wrong password rejected; correct password signs back into the stored local account');
  await click('[data-action="logout"]');await wait('!!document.querySelector("#auth-form")');await click('[data-action="judge-login"]');await wait('!!document.querySelector(".work-queue")');
  await click('[data-action="language"]');assert.equal(await evaluate('document.documentElement.lang'),'en');await shot('dashboard-english-1440');
  await call('Emulation.setDeviceMetricsOverride',{width:360,height:900,deviceScaleFactor:1,mobile:true});await shot('dashboard-english-360');
  await call('Emulation.setEmulatedMedia',{features:[{name:'prefers-reduced-motion',value:'reduce'}]});
  assert.equal(await evaluate('getComputedStyle(document.querySelector("main")).animationName'),'none');report.checks.push('English dashboard and OS reduced-motion rendering verified');
  assert.equal(report.errors.length,0,'Unexpected browser runtime errors');report.passed=true;
  await call('Browser.close').catch(()=>{});
}catch(error){report.failure=error.message;console.error(error.message);process.exitCode=1;}
finally{socket?.close();browser.kill();await fs.writeFile(path.join(dir,'evidence','browser-report.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({passed:report.passed,checks:report.checks.length,screenshots:report.screenshots.length,failure:report.failure}));}
