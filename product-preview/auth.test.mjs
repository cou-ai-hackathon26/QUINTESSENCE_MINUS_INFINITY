import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { randomUUID } from 'node:crypto';
import { createAuthStore, normalizePhone } from './auth-store.mjs';

const fixture={name:'Synthetic Reviewer',shopName:'Synthetic Test Shop',phone:'01712345678',password:'Only-synthetic-test-1234'};
async function storeForTest(t){const filename=path.join(os.tmpdir(),'shongoti-auth-test-'+randomUUID()+'.json');t.after(async()=>{await fs.unlink(filename).catch(()=>{});await fs.unlink(filename+'.tmp').catch(()=>{});});return {store:await createAuthStore(filename),filename};}
test('Bangladesh phone normalization accepts Bengali digits and country code, rejects malformed identity',()=>{
  assert.equal(normalizePhone('+8801712345678'),'01712345678');
  assert.equal(normalizePhone('০১৭১২৩৪৫৬৭৮'),'01712345678');
  for(const phone of ['01112345678','017123','x','017123456789'])assert.throws(()=>normalizePhone(phone));
});
test('registration persists salted password hash, creates its own tenant and server session',async t=>{
  const {store,filename}=await storeForTest(t);const result=await store.register({...fixture,tenantId:'attacker-tenant',role:'admin'},'register-a');
  assert.equal(result.user.kind,'merchant');assert.equal(result.user.role,'owner');assert.notEqual(result.user.tenantId,'attacker-tenant');assert.equal(result.user.phoneVerified,false);assert.equal(store.session(result.token).id,result.user.id);
  const raw=await fs.readFile(filename,'utf8');assert.equal(raw.includes(fixture.password),false);assert.equal('derived'in result.user,false);assert.equal('salt'in result.user,false);assert.ok(JSON.parse(raw).users[0].derived.length>=128);
});
test('correct password works after store reload; wrong password and nonexistent user are rejected',async t=>{
  const {store,filename}=await storeForTest(t);await store.register(fixture,'register-b');const reloaded=await createAuthStore(filename);
  await assert.rejects(reloaded.login({...fixture,password:'incorrect'},'login-b'),error=>error.status===401);
  await assert.rejects(reloaded.login({...fixture,phone:'01812345678'},'login-c'),error=>error.status===401);
  const result=await reloaded.login(fixture,'login-d');assert.equal(result.user.shopName,fixture.shopName);
});
test('concurrent duplicate registrations create one account rather than duplicate tenants',async t=>{
  const {store,filename}=await storeForTest(t);const results=await Promise.allSettled([store.register(fixture,'parallel-a'),store.register(fixture,'parallel-b')]);
  assert.equal(results.filter(r=>r.status==='fulfilled').length,1);assert.equal(results.filter(r=>r.status==='rejected'&&r.reason.status===409).length,1);assert.equal(JSON.parse(await fs.readFile(filename,'utf8')).users.length,1);
});
test('each judge gets an isolated principal; revoked or forged sessions fail',async t=>{
  const {store}=await storeForTest(t),first=store.judge('judge-a'),second=store.judge('judge-b');
  assert.notEqual(first.user.id,second.user.id);assert.notEqual(first.user.tenantId,second.user.tenantId);assert.notEqual(first.token,second.token);assert.equal(first.user.kind,'judge');assert.equal(store.session('forged'),null);
  store.revoke(first.token);assert.equal(store.session(first.token),null);assert.ok(store.session(second.token));
});
test('weak password is refused and repeated failed login is rate limited',async t=>{
  const {store}=await storeForTest(t);await assert.rejects(store.register({...fixture,password:'123456'},'weak'),error=>error.status===400);
  for(let i=0;i<8;i++)await assert.rejects(store.login({...fixture,password:'wrong'},'rate'),error=>error.status===401);
  await assert.rejects(store.login({...fixture,password:'wrong'},'rate'),error=>error.status===429);
});
