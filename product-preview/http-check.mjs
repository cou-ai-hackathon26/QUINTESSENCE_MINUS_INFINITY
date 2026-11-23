import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
const base='http://127.0.0.1:4318',checks=[];
const post=(endpoint,body={},cookie='',origin=base,type='application/json')=>fetch(base+'/preview-api/auth/'+endpoint,{method:'POST',headers:{Origin:origin,'Content-Type':type,...(cookie?{Cookie:cookie}:{})},body:JSON.stringify(body)});
const getSession=async cookie=>(await (await fetch(base+'/preview-api/auth/session',{headers:{Cookie:cookie}})).json()).user;
for(const asset of ['/','/app.js','/domain.js','/styles.css','/workbench.css','/purchasing.css','/favicon.svg']){const response=await fetch(base+asset);assert.equal(response.status,200);assert.equal(response.headers.get('x-content-type-options'),'nosniff');checks.push('Asset serves: '+asset);}
for(const asset of ['/.runtime/accounts.json','/auth-store.mjs','/server.mjs','/../../.env']){assert.equal((await fetch(base+asset)).status,404);checks.push('Private path excluded: '+asset);}
assert.equal(await getSession(''),null);checks.push('Anonymous session contains no account');
assert.equal((await post('judge',{},'','https://untrusted.invalid')).status,403);checks.push('Cross-origin mutation refused');
assert.equal((await post('judge',{},'',base,'text/plain')).status,403);checks.push('Non-JSON mutation refused');
const first=await post('judge');assert.equal(first.status,200);const cookie=first.headers.get('set-cookie');assert.match(cookie,/HttpOnly/);assert.match(cookie,/SameSite=Strict/);const cookie1=cookie.split(';')[0],user1=(await first.json()).user;assert.equal(user1.kind,'judge');assert.equal('token'in user1,false);checks.push('Judge cookie is HttpOnly/SameSite Strict; no token exposed in response');
const second=await post('judge',{},cookie1);assert.equal(second.status,200);const cookie2=second.headers.get('set-cookie').split(';')[0],user2=(await second.json()).user;
assert.notEqual(user1.tenantId,user2.tenantId);assert.equal(await getSession(cookie1),null);assert.equal((await getSession(cookie2)).id,user2.id);checks.push('Reset creates new judge tenant and revokes replaced session');
const logout=await post('logout',{},cookie2);assert.equal(logout.status,200);assert.match(logout.headers.get('set-cookie'),/Max-Age=0/);assert.equal(await getSession(cookie2),null);checks.push('Logout revokes session and expires cookie');
const report={date:new Date().toISOString(),passed:true,checks,scope:'Local preview HTTP/auth boundaries only; not main FastAPI or production financial integration.'};
await fs.writeFile(path.join(path.dirname(fileURLToPath(import.meta.url)),'evidence','http-report.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({passed:true,checks:checks.length}));
