import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';
import * as domain from './domain.js';

const dir=path.dirname(fileURLToPath(import.meta.url)), repo=path.dirname(dir);
const require=createRequire(import.meta.url);
const resolvePaths=[path.join(repo,'apps/web'),path.resolve(repo,'../Shongoti/apps/web')];
const { JSDOM }=require(require.resolve('jsdom',{paths:resolvePaths}));
const script=fs.readFileSync(path.join(dir,'app.js'),'utf8').replace(/^import .*?;\s*/,'');
const skeleton=fs.readFileSync(path.join(dir,'index.html'),'utf8').replace(/<script[^>]*>[\s\S]*?<\/script>/g,'').replace(/<link[^>]*>/g,'');
async function mount(hash='dashboard') {
  const dom=new JSDOM(skeleton,{url:'http://localhost/#/'+hash,runScripts:'outside-only',pretendToBeVisual:true});
  Object.assign(dom.window,domain);
  dom.window.scrollTo=()=>{};
  dom.window.fetch=async()=>({ok:true,json:async()=>({user:{id:'test-judge',tenantId:'test-tenant',kind:'judge',name:'Judge',shopName:'Meena Store'}})});
  const ready=new Promise(resolve=>dom.window.addEventListener('preview-ready',resolve,{once:true}));
  const timers=new Map();let id=0;
  dom.window.setTimeout=(fn,ms=0)=>{timers.set(++id,{fn,ms});return id;};
  dom.window.clearTimeout=id=>timers.delete(id);
  dom.window.eval(script);
  await ready;
  const doc=dom.window.document;
  const click=selector=>{const el=doc.querySelector(selector);assert.ok(el,selector);el.click();return el;};
  const tick=ms=>{const entry=[...timers].find(([,t])=>t.ms===ms);assert.ok(entry,`timer ${ms}`);timers.delete(entry[0]);entry[1].fn();};
  return {dom,doc,click,tick,timers};
}
test('money parser preserves decimal paisa and Bengali numerals; rejects ambiguous values',async()=>{
  assert.equal(domain.parseMoneyPaisa('১২৩.০৫'),12305);
  assert.equal(domain.parseMoneyPaisa('8000'),800000);
  for(const input of ['-1','NaN','1e3','1.001','1,000','','  '])assert.throws(()=>domain.parseMoneyPaisa(input));
});
test('unresolved prior inclusion retains two alternatives and critical cap; no guessed payable',async()=>{
  assert.deepEqual(domain.reconcile(null),{duePaisa:null,alternatives:[2200000,1800000],support:59,readiness:'needs_clarification',blocker:'payment_prior_inclusion'});
});
test('already included payment is not deducted a second time',async()=>{
  assert.equal(domain.reconcile(true).duePaisa,2200000);
  assert.equal(domain.reconcile(false).duePaisa,1800000);
});
test('conditional promise never changes actual funds or pre-arrival scenario',async()=>{
  const before=domain.scenario(800000,false),after=domain.scenario(800000,true);
  assert.equal(before.actualPaisa,1200000);assert.equal(after.actualPaisa,1200000);
  assert.deepEqual(before.values,[400000,620000,300000,100000,350000,500000,700000]);
  assert.equal(before.firstReserveBreach,3);
  assert.deepEqual(after.values.slice(0,2),before.values.slice(0,2));
  after.values.slice(2).forEach((value,i)=>assert.equal(value,before.values[i+2]+400000));
  assert.throws(()=>domain.scenario(0.1));
});
test('quotes include actual shipping, exclude unknown free bags and validate quantity',async()=>{
  assert.equal(domain.quoteTotal('rahman',6),732000);
  assert.equal(domain.quoteTotal('shapla',6),726000);
  assert.equal(domain.quoteTotal('nabil',6),732000);
  for(const q of [0,-1,1.5,101])assert.throws(()=>domain.quoteTotal('rahman',q));
});
test('all four hash routes render a unique page and keep disclosure and navigation',async()=>{
  const titles=new Set();
  for(const route of ['dashboard','case','buying','planner']){const m=await mount(route);titles.add(m.doc.querySelector('h1').textContent);assert.equal(m.doc.querySelectorAll('.nav-links a').length,5);assert.equal(m.doc.documentElement.lang,'bn');assert.equal(m.doc.querySelector('#app').dataset.mode,'judge');assert.ok(m.doc.querySelector('a[aria-current="page"]').href.endsWith(route));m.dom.window.close();}
  assert.equal(titles.size,4);
});
test('language toggle covers each page; public preview mode stays explicit',async()=>{
  for(const route of ['dashboard','case','buying','planner']){const m=await mount(route);m.click('[data-action="language"]');assert.equal(m.doc.documentElement.lang,'en');assert.match(m.doc.body.textContent,/synthetic|Synthetic/);assert.equal(m.doc.querySelectorAll('main h1').length,1);m.dom.window.close();}
});
test('cashflow period changes plotted and tabulated totals',async()=>{
  const m=await mount();const before=m.doc.querySelector('.chart-totals').textContent;
  m.click('[data-period="previous"]');assert.notEqual(m.doc.querySelector('.chart-totals').textContent,before);assert.equal(m.doc.querySelector('[data-period="previous"]').getAttribute('aria-pressed'),'true');assert.equal(m.doc.querySelectorAll('.chart-card tbody tr').length,7);m.dom.window.close();
});
test('unknown case blocks draft review; clarification updates payable and reset re-blocks',async()=>{
  const m=await mount('case');assert.equal(m.doc.querySelector('[data-action="review-case"]').disabled,true);
  m.click('[data-answer="included"]');assert.match(m.doc.querySelector('.due-result').textContent,/22,000/);assert.equal(m.doc.querySelector('[data-action="review-case"]').disabled,false);
  m.click('[data-answer="not-included"]');assert.match(m.doc.querySelector('.due-result').textContent,/18,000/);
  m.click('[data-action="reset-case"]');assert.equal(m.doc.querySelector('[data-action="review-case"]').disabled,true);assert.equal(m.doc.querySelector('.due-result'),null);m.dom.window.close();
});
test('agent replay advances only bounded fixture tasks, can pause, ends awaiting input',async()=>{
  const m=await mount('case');m.click('[data-action="replay"]');assert.equal(m.doc.querySelectorAll('.agent-node.active').length,1);assert.equal(m.doc.querySelector('[data-action="review-case"]').disabled,true);
  m.click('[data-action="pause-replay"]');assert.equal([...m.timers.values()].filter(t=>t.ms===1100).length,0);
  m.click('[data-action="pause-replay"]');for(let i=0;i<4;i++)m.tick(1100);
  assert.equal(m.doc.querySelectorAll('.agent-node.active').length,0);assert.equal(m.doc.querySelectorAll('.agent-node.waiting').length,1);assert.equal(m.doc.querySelectorAll('.event-list li').length,4);assert.equal(m.doc.querySelector('[data-action="review-case"]').disabled,true);m.dom.window.close();
});
test('source selection links to explicit synthetic text; modal Escape restores focus',async()=>{
  const m=await mount('case');m.click('[data-source="payment"][data-action="select-source"]');assert.match(m.doc.querySelector('#evidence-trace').textContent,/৪,০০০/);
  const opener=m.doc.querySelector('#evidence-trace [data-action="source"]');opener.focus();opener.click();assert.ok(m.doc.querySelector('[role="dialog"]'));assert.equal(m.doc.querySelector('#app').inert,true);
  m.doc.dispatchEvent(new m.dom.window.KeyboardEvent('keydown',{key:'Escape',bubbles:true}));assert.equal(m.doc.querySelector('[role="dialog"]'),null);assert.equal(m.doc.activeElement,opener);m.dom.window.close();
});
test('buying selection and quantity recompute total without assuming a free bag',async()=>{
  const m=await mount('buying');const radio=m.doc.querySelector('input[value="shapla"]');radio.checked=true;radio.dispatchEvent(new m.dom.window.Event('change',{bubbles:true}));assert.match(m.doc.querySelector('.tray-total').textContent,/7,260/);
  const qty=m.doc.querySelector('#quantity');qty.value='8';qty.dispatchEvent(new m.dom.window.Event('change',{bubbles:true}));assert.match(m.doc.querySelector('.tray-total').textContent,/9,580/);m.dom.window.close();
});
test('planner promise control affects conditional chart while actual figure remains unchanged',async()=>{
  const m=await mount('planner');const original=m.doc.querySelector('.scenario-stats strong').textContent;const before=m.doc.querySelector('.scenario-stats>div:last-child strong').textContent;
  const checkbox=m.doc.querySelector('#promise');checkbox.checked=true;checkbox.dispatchEvent(new m.dom.window.Event('change',{bubbles:true}));assert.equal(m.doc.querySelector('.scenario-stats strong').textContent,original);assert.notEqual(m.doc.querySelector('.scenario-stats>div:last-child strong').textContent,before);assert.equal(m.doc.querySelectorAll('.scenario-chart-card tbody tr').length,7);m.dom.window.close();
});
test('planner validation does not silently accept malformed or negative financial inputs',async()=>{
  const m=await mount('planner');const input=m.doc.querySelector('#expense');input.value='-100';input.dispatchEvent(new m.dom.window.Event('change',{bubbles:true}));assert.equal(input.getAttribute('aria-invalid'),'true');assert.ok(m.doc.querySelector('#expense-error').textContent);m.dom.window.close();
});
test('local copilot loading resolves grounded example and escapes user markup',async()=>{
  const m=await mount();m.click('[data-action="copilot"]');const input=m.doc.querySelector('#chat-input');input.value='<img src=x onerror="window.pwned=true"> available';m.doc.querySelector('#chat-form').dispatchEvent(new m.dom.window.Event('submit',{bubbles:true,cancelable:true}));
  assert.ok(m.doc.querySelector('.loading-dots'));assert.equal(m.doc.querySelector('.chat-message img'),null);m.tick(650);assert.equal(m.doc.querySelector('.loading-dots'),null);assert.match(m.doc.querySelector('.chat-message.assistant').textContent,/12,000/);assert.equal(m.dom.window.pwned,undefined);m.dom.window.close();
});
test('unknown hash safely renders dashboard; navigation really switches page',async()=>{
  const m=await mount('not-a-route');assert.match(m.doc.querySelector('h1').textContent,/আজ/);m.dom.window.location.hash='/buying';m.tick(0);assert.ok(m.doc.querySelector('.offers-grid'));m.dom.window.close();
});
test('motion control persists only preference and turns off animation styling',async()=>{
  const m=await mount();m.click('[data-action="motion"]');assert.equal(m.doc.body.classList.contains('motion-off'),true);assert.equal(m.dom.window.localStorage.getItem('shongoti-design-motion'),'off');m.dom.window.close();
});
