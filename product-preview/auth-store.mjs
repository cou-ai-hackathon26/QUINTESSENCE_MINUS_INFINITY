import { randomBytes, randomUUID, scrypt as scryptCallback, timingSafeEqual, createHash } from 'node:crypto';
import { promisify } from 'node:util';
import fs from 'node:fs/promises';
import path from 'node:path';

const scrypt=promisify(scryptCallback);
export const normalizePhone=value=>{
  let phone=String(value||'').trim().replace(/[০-৯]/g,d=>String('০১২৩৪৫৬৭৮৯'.indexOf(d))).replace(/[ -]/g,'');
  if(phone.startsWith('+88'))phone=phone.slice(3);
  if(!/^01[3-9]\d{8}$/.test(phone))throw Object.assign(new Error('Enter a valid Bangladesh mobile number.'),{status:400});
  return phone;
};
const failure=(message,status=400)=>Object.assign(new Error(message),{status});
const hash=value=>createHash('sha256').update(value).digest('hex');
const SESSION_MS=12*60*60*1000;
// OWASP-listed scrypt configuration; memory/CPU trade-off suitable for this local build.
const passwordParams={N:16384,r:8,p:5};
export async function createAuthStore(filename){
  let users=[];
  try{users=JSON.parse(await fs.readFile(filename,'utf8')).users;if(!Array.isArray(users))throw new Error('Invalid account store');}catch(error){if(error.code!=='ENOENT')throw error;}
  const sessions=new Map(),attempts=new Map();let queue=Promise.resolve();
  const locked=fn=>{const result=queue.then(fn);queue=result.catch(()=>{});return result;};
  async function persist(){await fs.mkdir(path.dirname(filename),{recursive:true});const temp=filename+'.tmp';await fs.writeFile(temp,JSON.stringify({version:1,users}),{mode:0o600});await fs.rename(temp,filename);}
  const publicUser=user=>({id:user.id,tenantId:user.tenantId,name:user.name,shopName:user.shopName,phone:user.phone,phoneVerified:false,kind:'merchant',role:'owner'});
  function issue(user){for(const [key,value]of sessions)if(value.expires<Date.now())sessions.delete(key);if(sessions.size>=5000)throw failure('Session capacity reached. Try again later.',503);const token=randomBytes(32).toString('base64url');sessions.set(hash(token),{user,expires:Date.now()+SESSION_MS});return {token,user};}
  function checkRate(key){const now=Date.now();for(const [k,v]of attempts)if(now-v.start>60000)attempts.delete(k);if(attempts.size>2000)throw failure('Please try again shortly.',429);const record=attempts.get(key)||{start:now,count:0};if(++record.count>8)throw failure('Too many attempts. Try again in one minute.',429);attempts.set(key,record);}
  return {
    async register(body,ip){
      checkRate('register:'+ip);
      const phone=normalizePhone(body.phone),name=String(body.name||'').trim(),shopName=String(body.shopName||'').trim(),password=body.password;
      if(name.length<2||name.length>80||shopName.length<2||shopName.length>100)throw failure('Enter your name and shop name.');
      if(typeof password!=='string'||password.length<12||password.length>128)throw failure('Use a password of 12–128 characters.');
      const salt=randomBytes(16).toString('hex');const derived=(await scrypt(password,salt,64,passwordParams)).toString('hex');
      return locked(async()=>{
        if(users.some(u=>u.phone===phone))throw failure('An account with this number already exists. Please sign in.',409);
        const user={id:randomUUID(),tenantId:randomUUID(),name,shopName,phone,salt,derived,passwordParams,createdAt:new Date().toISOString()};
        users.push(user);try{await persist();}catch(error){users.pop();throw error;}
        return issue(publicUser(user));
      });
    },
    async login(body,ip){
      checkRate('login:'+ip);
      let phone;try{phone=normalizePhone(body.phone);}catch{throw failure('Invalid phone or password.',401);}
      const password=typeof body.password==='string'?body.password:'';
      if(password.length>128)throw failure('Invalid phone or password.',401);
      const user=users.find(u=>u.phone===phone);
      const params=user?(user.passwordParams||{N:16384,r:8,p:1}):passwordParams;
      const derived=await scrypt(password,user?.salt||'local-login-timing-salt',64,params);
      const expected=user?Buffer.from(user.derived,'hex'):Buffer.alloc(64);
      if(!timingSafeEqual(derived,expected)||!user)throw failure('Invalid phone or password.',401);
      if(!user.passwordParams){const salt=randomBytes(16).toString('hex'),upgraded=(await scrypt(password,salt,64,passwordParams)).toString('hex');await locked(async()=>{Object.assign(user,{salt,derived:upgraded,passwordParams});await persist();});}
      return issue(publicUser(user));
    },
    judge(ip){checkRate('judge:'+ip);return issue({id:randomUUID(),tenantId:'judge-'+randomUUID(),name:'Judge',shopName:'Meena Store',kind:'judge',role:'demo_owner',phoneVerified:false});},
    session(token){if(!token)return null;const key=hash(token),session=sessions.get(key);if(!session)return null;if(session.expires<Date.now()){sessions.delete(key);return null;}return session.user;},
    revoke(token){if(token)sessions.delete(hash(token));},
  };
}
