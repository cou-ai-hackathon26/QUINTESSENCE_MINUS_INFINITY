import {afterEach,expect,it,vi} from 'vitest';
import {render,screen,fireEvent,waitFor,cleanup} from '@testing-library/react';
import {MemoryRouter} from 'react-router-dom';
import App from '../App';
import {setWorkspaceSession} from '../workbench/api';
afterEach(()=>{cleanup();vi.unstubAllGlobals();setWorkspaceSession(null);localStorage.clear();});
it('a real empty account cannot review an unfunded withdrawal or send a financial mutation',async()=>{
 localStorage.setItem('shongoti_lang','en');setWorkspaceSession(null);
 const calls:{path:string;method:string}[]=[];
 vi.stubGlobal('fetch',vi.fn(async(input:RequestInfo|URL,init?:RequestInit)=>{const path=String(input);calls.push({path,method:init?.method||'GET'});return new Response(JSON.stringify(path.endsWith('/auth/me')?{user_id:'real-owner',tenant_id:'empty-shop',name:'Owner',shop_name:'Empty shop',role:'owner',is_demo:false}:[]),{status:200,headers:{'Content-Type':'application/json'}});}));
 render(<MemoryRouter initialEntries={['/app/money']}><App/></MemoryRouter>);
 fireEvent.click(await screen.findByRole('button',{name:'Owner draw'}));
 fireEvent.change(screen.getByLabelText('Amount (BDT)'),{target:{value:'100'}});
 const review=screen.getByRole('button',{name:'Review record'});
 await waitFor(()=>expect(review).not.toBeDisabled());fireEvent.click(review);
 await screen.findByText('Insufficient funds in the selected account.');
 expect(screen.queryByRole('dialog')).toBeNull();
 expect(calls.filter(c=>c.method==='POST'&&c.path.includes('/merchant/'))).toEqual([]);
});
