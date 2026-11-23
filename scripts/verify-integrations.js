#!/usr/bin/env node
// Configuration inventory only. A credential is never proof of a successful provider request.
const fs=require('node:fs');
const path=require('node:path');
const root=path.resolve(__dirname,'..'),file=path.join(root,'.env');
const local=fs.existsSync(file)?fs.readFileSync(file,'utf8'):'';
function present(key){const match=local.match(new RegExp('^'+key+'=(.*)$','m'));const value=process.env[key]??match?.[1]??'';return !['',"''",'""'].includes(value.trim());}
const checks=[{name:'Groq inference',state:present('GROQ_API_KEY')?'configured_not_probed':'not_configured',detail:'Genuine task receipts are separate from this read-only inventory.'},{name:'Multilingual local encoder',state:fs.existsSync(path.join(root,'apps/api/data/models/multilingual-e5-small/manifest.json'))?'prepared_not_probed':'not_prepared',detail:'Artifact presence is not observed inference.'},{name:'Online payments',state:'not_connected',detail:'Real gateway transport and sandbox validation remain deferred; credentials alone cannot enable them.'},{name:'SMS / WhatsApp delivery',state:'not_connected',detail:'No verified sender/dispatcher.'},{name:'Cloud Bangla speech playback',state:'not_connected',detail:'Browser playback depends on installed language voices.'}];
console.log(JSON.stringify({mode:'local_configuration_inventory_only',checks,secrets_displayed:false},null,2));
process.exit(process.argv.includes('--strict')&&checks.some(c=>c.state==='not_connected'||c.state==='not_configured')?2:0);
