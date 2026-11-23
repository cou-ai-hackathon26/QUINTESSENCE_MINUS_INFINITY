"""Bounded genuine inference smoke check on a new synthetic tenant only."""
import json, time, sys
from pathlib import Path
import httpx
import pymupdf

OUT=Path('docs/evidence/readiness/AJ-03')
OUT.mkdir(parents=True,exist_ok=True)
report={'mode':'genuine_provider_synthetic_records','checks':[], 'passed':False}

def note(name, **data):
    report['checks'].append({'check':name,**data})
    (OUT/'live-checks.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(name, json.dumps(data),flush=True)

try:
    with httpx.Client(base_url='http://127.0.0.1:8000',headers={'Origin':'http://127.0.0.1:5173'},timeout=120) as c:
        r=c.post('/api/v1/auth/judge-session',json={});r.raise_for_status();who=r.json()
        assert c.get('/api/v1/merchant/today').json()['cash_balance_paisa']==500000
        note('isolated_judge',status=r.status_code)
        document=pymupdf.open();page=document.new_page();page.insert_text((50,80),'SYNTHETIC TEST ONLY\nInvoice READINESS-51929\nSupplier: Synthetic Readiness Trader\nTotal BDT 519.29',fontsize=15)
        native=document.tobytes();pix=page.get_pixmap();png=pix.tobytes('png')
        scan=pymupdf.open();scan.new_page(width=page.rect.width,height=page.rect.height).insert_image(page.rect,stream=png)
        for filename,body,mime in [('readiness.png',png,'image/png'),('readiness-native.pdf',native,'application/pdf'),('readiness-scan.pdf',scan.tobytes(),'application/pdf')]:
            r=c.post('/api/v1/evidence/upload',files={'file':(filename,body,mime)});r.raise_for_status();result=r.json()
            assert result['proposed_amount_paisa']==51929,result.get('extraction_error')
            assert any(x['status']=='succeeded' for x in result['provider_receipts'])
            assert c.get('/api/v1/evidence/'+result['evidence_id']+'/content').content==body
            note(filename,amount_paisa=51929,receipt_count=len(result['provider_receipts']))
        session=c.post('/api/v1/copilot/sessions',json={}).json()['id']
        r=c.post('/api/v1/copilot/sessions/'+session+'/messages',json={'query':'What is the total on invoice READINESS-51929? Cite the document.'});r.raise_for_status();answer=r.json()
        assert answer.get('provider_receipts') and answer.get('citations')
        note('grounded_chat',receipt_count=len(answer['provider_receipts']),citations=len(answer['citations']))
        r=c.post('/api/v1/agents/runs',json={'case_type':'reconciliation','case_id':who['case_id'],'query':'Investigate INV-025. Copy exact nonempty quotes from structured_source_texts or original source text. Preserve known inclusion flags and both supported payable alternatives.','budget_max':4});r.raise_for_status();run_id=r.json()['run_id']
        until=time.monotonic()+150
        while time.monotonic()<until:
            run=c.get('/api/v1/agents/runs/'+run_id).json()
            if run['status'] not in ('queued','running'):break
            time.sleep(1)
        assert run['status'] in ('waiting_user','completed'),run['status']
        assert len(run['provider_receipts'])==3 and all(t['status']=='succeeded' for t in run['tasks'])
        note('actual_specialists',status=run['status'],model_calls=3,tasks=len(run['tasks']))
        audio=Path(next((arg.split('=',1)[1] for arg in sys.argv if arg.startswith('--audio=')), '../Shongoti-video/public/media/voice/owner-input.wav'))
        if audio.exists():
            r=c.post('/api/v1/copilot/sessions/'+session+'/voice',files={'file':('synthetic-owner.wav',audio.read_bytes(),'audio/wav')});r.raise_for_status();voice=r.json()
            types={op['type'] for op in voice['compound_operations']}
            assert {'debt_collection','credit_sale'}<=types
            assert c.get('/api/v1/merchant/today').json()['cash_balance_paisa']==500000
            note('actual_whisper_compound_proposals',operation_types=sorted(types),receipt_count=len(voice['provider_receipts']),no_automatic_posting=True)
        else:raise RuntimeError('Synthetic audio absent. Supply --audio=PATH; Whisper is not verified by this run.')
        r=c.post('/api/v1/voice/speak',json={'text':'Synthetic readiness check. Twelve Taka.','voice':'en-US-GuyNeural','rate':'+0%'})
        assert r.status_code==200,(r.status_code,r.text[:200])
        assert len(r.content)>500 and r.headers['cache-control']=='private, no-store'
        note('actual_online_speech',status=200,audio_bytes=len(r.content))
        report['passed']=True
except Exception as error:
    report['failure']=str(error)[:500]
    print('FAILED',report['failure'],flush=True)
finally:
    (OUT/'live-checks.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
if not report['passed']:raise SystemExit(1)
