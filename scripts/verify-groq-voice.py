"""Bounded real Whisper verification using locally synthesized Windows speech."""
import json
from pathlib import Path
import httpx

audio=Path('tmp/groq-live/merchant-voice.wav')
report={'scope':'Actual app voice endpoint, Windows SAPI synthetic English audio, real Groq Whisper and extraction; no Bangla quality claim','passed':False}
try:
    assert audio.is_file() and audio.read_bytes()[:4]==b'RIFF'
    with httpx.Client(base_url='http://127.0.0.1:8000',timeout=180,headers={'Origin':'http://127.0.0.1:8000'}) as client:
        assert client.post('/api/v1/auth/judge-session',json={}).status_code==201
        session=client.post('/api/v1/copilot/sessions',json={'title':'Real speech verification'}).json()
        response=client.post('/api/v1/copilot/sessions/'+session['id']+'/voice',files={'file':('merchant-voice.wav',audio.read_bytes(),'audio/wav')})
        report['http_status']=response.status_code
        body=response.json()
        assert response.status_code==200,str(body)
        report.update({key:body.get(key) for key in ['transcription','compound_operations','provider_receipts','evidence_id']})
        operations=body['compound_operations']
        assert any(op['type']=='debt_collection' and op['amount_paisa']==50000 for op in operations)
        assert any(op['type']=='credit_sale' and op['amount_paisa']==20000 for op in operations)
        assert any(r['model']=='whisper-large-v3' and r['status']=='succeeded' for r in body['provider_receipts'])
        history=client.get('/api/v1/copilot/sessions/'+session['id']).json()
        assert history['messages'][-1]['audio_metadata']['evidence_id']==body['evidence_id']
        original=client.get('/api/v1/evidence/'+body['evidence_id']+'/content')
        assert original.content==audio.read_bytes()
        report['passed']=True
except Exception as error:
    report['failure']=str(error)
finally:
    Path('docs/evidence/real-workflow/JR-02/groq-voice-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'passed':report['passed'],'http_status':report.get('http_status'),'failure':report.get('failure')}))
    if not report['passed']:raise SystemExit(1)
