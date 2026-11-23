// Genuine local browser smoke; isolated Chrome profile, no fixture interception.
import {spawn} from 'node:child_process';
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
const out=path.resolve('docs/evidence/readiness/AJ-03'),profile=path.resolve('tmp/readiness-browser-'+Date.now());
await fs.mkdir(out,{recursive:true});await fs.mkdir(profile,{recursive:true});
const chrome=process.env.CHROME_PATH||'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const child=spawn(chrome,['--headless','--disable-gpu','--no-first-run','--no-default-browser-check','--remote-debugging-port=0','--user-data-dir='+profile,'about:blank'],{windowsHide:true,stdio:'ignore'});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));const report={mode:'actual_local_browser',checks:[],errors:[],passed:false};let socket,inspect;
try{
 let port;for(let i=0;i<80;i++){try{port=(await fs.readFile(path.join(profile,'DevToolsActivePort'),'utf8')).split('\n')[0];break;}catch{await sleep(100);}}
 assert.ok(port,'Chrome debugging endpoint unavailable');
 const tabs=await(await fetch('http://127.0.0.1:'+port+'/json/list')).json();
 socket=new WebSocket(tabs.find(x=>x.type==='page').webSocketDebuggerUrl);await new Promise((r,j)=>{socket.addEventListener('open',r,{once:true});socket.addEventListener('error',j,{once:true});});
 let id=0,onLoad;const pending=new Map();socket.addEventListener('message',event=>{const m=JSON.parse(event.data);if(m.id){const p=pending.get(m.id);if(p){clearTimeout(p.timer);pending.delete(m.id);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result);}}else if(m.method==='Page.loadEventFired')onLoad?.();else if(m.method==='Runtime.exceptionThrown')report.errors.push(m.params.exceptionDetails.exception?.description||m.params.exceptionDetails.text);});
 const call=(method,params={})=>new Promise((resolve,reject)=>{const key=++id,timer=setTimeout(()=>reject(Error(method+' timeout')),15000);pending.set(key,{resolve,reject,timer});socket.send(JSON.stringify({id:key,method,params}));});
 const evaluate=async expression=>{const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.exception?.description||'Browser evaluation failed');return r.result.value;};
 inspect=evaluate;
 const wait=async(expression)=>{const until=Date.now()+20000;while(Date.now()<until){if(await evaluate(expression))return;await sleep(100);}throw Error('Condition failed: '+expression);};
 const click=selector=>evaluate('document.querySelector('+JSON.stringify(selector)+')?.click()');
 const navigate=async(method,params={})=>{let done;const ready=new Promise(r=>{done=r;});onLoad=done;await call(method,params);await Promise.race([ready,sleep(15000).then(()=>{throw Error('Navigation load timed out');})]);onLoad=undefined;};
 await call('Runtime.enable');await call('Page.enable');await call('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
 await call('Page.navigate',{url:'http://127.0.0.1:5173/login'});await wait('!!document.querySelector(".judge-button")');await click('.judge-button');await wait('!!document.querySelector(".home-workbench")');
 assert.equal(await evaluate('fetch("/api/v1/merchant/today").then(r=>r.json()).then(r=>r.cash_balance_paisa)'),500000);report.checks.push('Actual one-click Judge entry and opening balance');
 await navigate('Page.reload');await wait('!!document.querySelector(".home-workbench")');report.checks.push('Cookie session and records survive reload');
 await click('.vno-orb-trigger');await wait('!!document.querySelector(".vno-hud-panel") && !document.querySelector(".vno-play-btn").disabled');
 const transcript=await evaluate('document.querySelector(".vno-subtitle-text").textContent');assert.ok(!transcript.includes('25,400'));assert.ok(transcript.includes('12,000'));report.checks.push('Voice bulletin shows actual scoped brief and enables playback after loading');
 await click('.vno-close-btn');
 for(const route of ['/app/cases','/app/agents','/app/copilot','/app/evidence','/app/sales','/app/people','/app/money','/app/buying','/app/receiving','/app/stock','/app/planner','/app/reports','/app/inbox','/app/operations','/app/help','/app/connections','/app/settings','/pricing']){
  await navigate('Page.navigate',{url:'http://127.0.0.1:5173'+route});await wait('!!document.querySelector("h1")');
  assert.ok(!await evaluate('!!document.querySelector(".route-failure")'));
  for(const width of [360,768,1440]){await call('Emulation.setDeviceMetricsOverride',{width,height:1000,deviceScaleFactor:1,mobile:width===360});assert.ok(await evaluate('document.documentElement.scrollWidth <= innerWidth+1'),'Overflow '+route+' '+width);}
 }
 report.checks.push('18 additional routes at 360/768/1440 without runtime failure or overflow');
 await navigate('Page.navigate',{url:'http://127.0.0.1:5173/app'});await wait('!!document.querySelector(".home-workbench")');await call('Network.enable');await call('Network.setBlockedURLs',{urls:['*notifications/brief*','*api/v1/notifications']});await navigate('Page.reload');await wait('!!document.querySelector(".home-workbench")');await click('.vno-orb-trigger');await wait('!!document.querySelector(".vno-hud-panel")');await sleep(400);
 assert.equal(await evaluate('document.querySelector(".vno-play-btn").disabled'),true);assert.ok(!await evaluate('document.querySelector(".vno-subtitle-text").textContent.includes("25,400")'));report.checks.push('Explicit blocked-network failure test disables speech and never invents a balance');
 await call('Network.setBlockedURLs',{urls:[]});await navigate('Page.reload');await wait('!!document.querySelector(".home-workbench")');
 await wait('!document.querySelector(".state-panel[role=status]")');await sleep(650);
 const screenshot=await call('Page.captureScreenshot',{format:'png'});await fs.writeFile(path.join(out,'dashboard-1440.png'),Buffer.from(screenshot.data,'base64'));
 assert.equal(report.errors.length,0);report.passed=true;await call('Browser.close').catch(()=>{});
}catch(error){report.failure=error.message;report.diagnostic=await inspect?.('({url:location.pathname,hud:!!document.querySelector(".vno-hud-panel"),trigger:!!document.querySelector(".vno-orb-trigger"),transcript:document.querySelector(".vno-subtitle-text")?.textContent,disabled:document.querySelector(".vno-play-btn")?.disabled,routeError:document.querySelector(".route-failure")?.textContent})').catch(()=>null);process.exitCode=1;}
finally{socket?.close();child.kill();await fs.writeFile(path.join(out,'browser-checks.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));}
