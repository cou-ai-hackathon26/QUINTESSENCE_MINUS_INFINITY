import {afterEach,expect,it,vi} from 'vitest';
import {setWorkspaceSession,post,request} from '../workbench/api';
afterEach(()=>{setWorkspaceSession(null);vi.unstubAllGlobals();});
it('judge file uploads and reads use the real HTTP boundary, without fixture interception',async()=>{
 setWorkspaceSession({user_id:'judge',tenant_id:'isolated-merchant',role:'owner',name:'Judge',shop_name:'Seeded shop',is_demo:true});
 const calls:RequestInit[]=[];
 const network=vi.fn(async(_path:RequestInfo|URL,init?:RequestInit)=>{calls.push(init||{});return new Response(JSON.stringify({evidence_id:'persisted-server-document'}),{status:200,headers:{'Content-Type':'application/json'}});});vi.stubGlobal('fetch',network);
 const form=new FormData();form.append('file',new Blob(['Unseen source'],{type:'text/plain'}),'new-source.txt');
 const uploaded=await post('/api/v1/evidence/upload',form);expect(uploaded.evidence_id).toBe('persisted-server-document');
 expect(network).toHaveBeenCalledTimes(1);expect(calls[0].body).toBe(form);expect(calls[0].credentials).toBe('same-origin');
 await request('/api/v1/merchant/today');expect(network).toHaveBeenCalledTimes(2);
});
