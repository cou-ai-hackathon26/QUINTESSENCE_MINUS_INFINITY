"""Retry only remaining live smoke checks after a provider rate-limit failure."""
import json,time,sys
from pathlib import Path
import httpx
OUT=Path('docs/evidence/readiness/AJ-03');report={'mode':'genuine_retry_after_429','checks':[],'passed':False}
def note(name,**data):
    report['checks'].append({'check':name,**data});print(name,json.dumps(data),flush=True)
    (OUT/'live-remaining.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
try:
    with httpx.Client(base_url='http://127.0.0.1:8000',headers={'Origin':'http://127.0.0.1:5173'},timeout=120) as c:
        who=c.post('/api/v1/auth/judge-session',json={}).json()
        r=c.post('/api/v1/agents/runs',json={'case_type':'reconciliation','case_id':who['case_id'],'query':'Investigate INV-025. Copy exact nonempty quotes from structured_source_texts or original source text. Preserve known inclusion flags and both supported payable alternatives.','budget_max':4});r.raise_for_status();run_id=r.json()['run_id']
        until=time.monotonic()+150
        while time.monotonic()<until:
            run=c.get('/api/v1/agents/runs/'+run_id).json()
            if run['status'] not in ('queued','running'):break
            time.sleep(1)
        events=c.get('/api/v1/agents/runs/'+run_id+'/events').json()
        assert run['status'] in ('waiting_user','completed'),next((e['payload'] for e in events if e['event_type']=='run_failed'),run['status'])
        assert len(run['provider_receipts'])==3 and all(t['status']=='succeeded' for t in run['tasks'])
        note('actual_specialists',status=run['status'],model_calls=3,tasks=len(run['tasks']))
        session=c.post('/api/v1/copilot/sessions',json={}).json()['id'];audio=Path(next((arg.split('=',1)[1] for arg in sys.argv if arg.startswith('--audio=')), '../Shongoti-video/public/media/voice/owner-input.wav'))
        r=c.post('/api/v1/copilot/sessions/'+session+'/voice',files={'file':('synthetic-owner.wav',audio.read_bytes(),'audio/wav')});r.raise_for_status();voice=r.json();types={o['type'] for o in voice['compound_operations']}
        assert {'debt_collection','credit_sale'}<=types
        assert c.get('/api/v1/merchant/today').json()['cash_balance_paisa']==500000
        note('actual_whisper',operation_types=sorted(types),no_automatic_posting=True,receipts=len(voice['provider_receipts']))
        r=c.post('/api/v1/voice/speak',json={'text':'Synthetic readiness check. Twelve Taka.','voice':'en-US-GuyNeural','rate':'+0%'})
        assert r.status_code==200,(r.status_code,r.text[:150])
        assert len(r.content)>500
        note('actual_online_speech',status=200,bytes=len(r.content));report['passed']=True
except Exception as error:report['failure']=str(error)[:500];print('FAILED',report['failure'],flush=True)
finally:(OUT/'live-remaining.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
if not report['passed']:raise SystemExit(1)
