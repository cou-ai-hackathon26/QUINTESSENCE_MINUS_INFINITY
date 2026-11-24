export interface Session { user_id:string; tenant_id:string; role:string; is_demo:boolean; name:string; shop_name:string; case_id?:string; phone_verified?:boolean }
let scope:Session|null=null;
export function setWorkspaceSession(session:Session|null){scope=session;}
export function currentWorkspaceSession(){return scope;}
export function money(paisa:number){return '৳'+(paisa/100).toLocaleString('en-US',{maximumFractionDigits:2});}
export function parsePaisa(value:string){const normalized=value.trim().replace(/[০-৯]/g,d=>String('০১২৩৪৫৬৭৮৯'.indexOf(d)));if(!/^\d{1,9}(\.\d{1,2})?$/.test(normalized))throw new Error('০ বা তার বেশি টাকা দিন, সর্বোচ্চ ২ decimal place / Enter an exact non-negative amount.');const [whole,decimal='']=normalized.split('.');const result=Number(whole)*100+Number(decimal.padEnd(2,'0'));if(!Number.isSafeInteger(result))throw new Error('Amount exceeds exact range');return result;}
export async function workspaceFetch(input:RequestInfo|URL,init:RequestInit={}):Promise<Response>{
  return fetch(input,{...init,credentials:'same-origin'});
}
export async function request<T=Record<string,unknown>>(path:string,options:RequestInit={}):Promise<T>{
  if(!path.startsWith('/api/v1/'))throw new Error('Only scoped application API paths are allowed');
  const headers=new Headers(options.headers);if(options.body&&!(options.body instanceof FormData))headers.set('Content-Type','application/json');
  const response=await workspaceFetch(path,{...options,headers});
  if(!response.ok){let detail:unknown;try{detail=(await response.json()).detail;}catch{detail='Request failed';}if(response.status===401)window.dispatchEvent(new Event('shongoti-session-expired'));throw new Error(typeof detail==='string'?detail:Array.isArray(detail)?detail.map(x=>x.msg||'Invalid field').join('; '):`Request failed (${response.status})`);}
  if(response.status===204)return undefined as T;return response.json() as Promise<T>;
}
export const post=<T=Record<string,unknown>>(path:string,body:unknown={})=>request<T>(path,{method:'POST',body:body instanceof FormData?body:JSON.stringify(body)});
export async function requestBlob(path:string,mimeType:string){
  if(!path.startsWith('/api/v1/'))throw new Error('Only scoped application API paths are allowed');
  const headers=new Headers();
  const response=await workspaceFetch(path,{headers});
  if(!response.ok)throw new Error(`Original source is unavailable (${response.status})`);
  return new Blob([await response.arrayBuffer()],{type:mimeType||'application/octet-stream'});
}
