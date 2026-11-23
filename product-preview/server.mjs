import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createAuthStore } from './auth-store.mjs';
const root = path.dirname(fileURLToPath(import.meta.url));
const port = Number(process.env.SHONGOTI_PRODUCT_PORT || 4318);
if (!Number.isInteger(port) || port < 1024 || port > 65535) throw new Error('Invalid port');
const files = new Set(['index.html', 'app.js', 'domain.js', 'styles.css', 'workbench.css', 'purchasing.css', 'favicon.svg']);
const types = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8', '.svg': 'image/svg+xml' };
const authFile=process.env.SHONGOTI_AUTH_FILE||'accounts.json';
if(!/^[a-zA-Z0-9_-]+\.json$/.test(authFile))throw new Error('Invalid local account file name');
const auth=await createAuthStore(path.join(root,'.runtime',authFile));
const cookieName='shongoti_review_session';
const server = http.createServer(async (req, res) => {
  const requestUrl=new URL(req.url,'http://localhost');
  if(requestUrl.pathname.startsWith('/preview-api/')){
    const send=(status,data,headers={})=>{res.writeHead(status,{'content-type':'application/json; charset=utf-8','cache-control':'no-store','x-content-type-options':'nosniff',...headers}).end(JSON.stringify(data));};
    const token=String(req.headers.cookie||'').split(';').map(p=>p.trim()).find(p=>p.startsWith(cookieName+'='))?.slice(cookieName.length+1);
    if(req.method==='GET'&&requestUrl.pathname==='/preview-api/auth/session'){send(200,{user:auth.session(token)});return;}
    if(req.method!=='POST'){send(405,{error:'Method not allowed'});return;}
    const validOrigins=new Set([`http://127.0.0.1:${port}`,`http://localhost:${port}`]);
    if(!validOrigins.has(req.headers.origin)||!String(req.headers['content-type']||'').startsWith('application/json')){send(403,{error:'Same-origin JSON requests are required.'});return;}
    let bytes=0,body='';
    try{
      for await(const chunk of req){bytes+=chunk.length;if(bytes>8192){send(413,{error:'Request too large.'});return;}body+=chunk;}
      const data=JSON.parse(body||'{}');if(!data||Array.isArray(data)||typeof data!=='object'){send(400,{error:'Invalid request.'});return;}
      const ip=req.socket.remoteAddress||'local';
      if(requestUrl.pathname==='/preview-api/auth/logout'){auth.revoke(token);send(200,{ok:true},{'set-cookie':`${cookieName}=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0`});return;}
      let result;
      if(requestUrl.pathname==='/preview-api/auth/register')result=await auth.register(data,ip);
      else if(requestUrl.pathname==='/preview-api/auth/login')result=await auth.login(data,ip);
      else if(requestUrl.pathname==='/preview-api/auth/judge')result=auth.judge(ip);
      else{send(404,{error:'Unknown endpoint.'});return;}
      auth.revoke(token);
      send(200,{user:result.user},{'set-cookie':`${cookieName}=${result.token}; HttpOnly; SameSite=Strict; Path=/; Max-Age=43200`});
    }catch(error){send(error.status||400,{error:error.status?error.message:'Request could not be completed.'});}
    return;
  }
  if (!['GET', 'HEAD'].includes(req.method)) { res.writeHead(405, { allow: 'GET, HEAD' }).end(); return; }
  let name;
  try { name = decodeURIComponent(new URL(req.url, 'http://localhost').pathname).slice(1) || 'index.html'; } catch { res.writeHead(400).end(); return; }
  if (name === '__preview_health') { res.writeHead(200, { 'content-type': 'application/json' }).end(JSON.stringify({ status: 'ok', mode: 'synthetic_design_preview', pages: 4, liveAI: false })); return; }
  if (!files.has(name)) { res.writeHead(404).end('Not found'); return; }
  fs.readFile(path.join(root, name), (error, bytes) => {
    if (error) { res.writeHead(500).end('Preview unavailable'); return; }
    res.writeHead(200, { 'content-type': types[path.extname(name)], 'cache-control': 'no-store', 'x-content-type-options': 'nosniff', 'referrer-policy': 'no-referrer' });
    res.end(req.method === 'HEAD' ? undefined : bytes);
  });
});
server.on('error', error => { process.stderr.write(`Preview start failed: ${error.code || error.message}. Existing servers were not stopped.\n`); process.exitCode = 1; });
server.listen(port, '127.0.0.1', () => process.stdout.write(`Shongoti four-page design preview\nLocal: http://127.0.0.1:${port}\nSynthetic data; no backend or model calls.\n`));
process.on('SIGINT', () => server.close(() => process.exit(0)));
process.on('SIGTERM', () => server.close(() => process.exit(0)));
