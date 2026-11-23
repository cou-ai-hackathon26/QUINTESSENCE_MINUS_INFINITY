"""Genuine bounded provider checks through the running app; no credential output."""
import json,uuid,sys
from pathlib import Path
import httpx
import pymupdf

root=Path('docs/evidence/real-workflow/JR-02');root.mkdir(parents=True,exist_ok=True)
fixtures=Path('tmp/groq-live');fixtures.mkdir(parents=True,exist_ok=True)
reference='LIVE-'+uuid.uuid4().hex[:8].upper()
amount='1,763.55'
text='SHONGOTI SYNTHETIC SUPPLIES\nSYNTHETIC TEST INVOICE - NOT A REAL SALE\nInvoice: '+reference+'\nItem: Merchant test supplies\nTOTAL DUE: BDT '+amount+'\nPayment method: cash\nNo payment has been made.'
doc=pymupdf.open();page=doc.new_page(width=595,height=700);page.insert_text((42,80),text,fontsize=17,lineheight=1.7)
pdf=doc.tobytes();image=page.get_pixmap(matrix=pymupdf.Matrix(1.6,1.6),alpha=False).tobytes('png')
scanned=pymupdf.open();scan=scanned.new_page(width=595,height=700);scan.insert_image(scan.rect,stream=image)
samples=[('unseen-invoice.txt',text.encode(),'text/plain'),('unseen-invoice.png',image,'image/png'),('unseen-native.pdf',pdf,'application/pdf'),('unseen-scanned.pdf',scanned.tobytes(),'application/pdf')]
report={'provider':'groq','scope':'Actual app HTTP and genuine provider responses on newly generated synthetic sources','expected_invoice_ref':reference,'expected_amount_paisa':176355,'checks':[],'passed':False}
try:
    with httpx.Client(base_url='http://127.0.0.1:8000',timeout=180,headers={'Origin':'http://127.0.0.1:8000'}) as client:
        auth=client.post('/api/v1/auth/judge-session',json={});assert auth.status_code==201,'Judge entry failed'
        for name,content,mime in samples:
            (fixtures/name).write_bytes(content)
            result=client.post('/api/v1/evidence/upload',files={'file':(name,content,mime)})
            assert result.status_code==200,'Upload HTTP '+str(result.status_code)
            body=result.json();detail=client.get('/api/v1/evidence/'+body['evidence_id']).json()
            correct=body['status']=='extracted' and body['proposed_amount_paisa']==176355 and detail['extraction']['invoice_ref']==reference
            receipts=detail.get('provider_receipts',[])
            row={'source':name,'status':body['status'],'amount_paisa':body['proposed_amount_paisa'],'invoice_ref':detail.get('extraction',{}).get('invoice_ref') if detail.get('extraction') else None,'correct':correct,'error':body.get('extraction_error'),'receipts':receipts}
            report['checks'].append(row);print(json.dumps({'source':name,'status':body['status'],'correct':correct,'error':row['error']}),flush=True)
            assert correct,'Live extraction mismatch for '+name
        session=client.post('/api/v1/copilot/sessions',json={'title':'Actual provider verification','context_entity_type':'case','context_entity_id':auth.json()['case_id']}).json()
        answer=client.post('/api/v1/copilot/sessions/'+session['id']+'/messages',json={'query':'আমার হাতে cash আর wallet মিলিয়ে মোট কত টাকা আছে? Source দেখাও, পাওনা যোগ করো না।'})
        assert answer.status_code==200,'Chat HTTP '+str(answer.status_code)
        body=answer.json();assert body.get('provider_receipts') and body.get('citations'),'Expected actual inference and source citations'
        report['checks'].append({'type':'grounded_chat','answer':body['content'],'citations':body['citations'],'receipts':body['provider_receipts']})
        audio=fixtures/'merchant-voice.wav'
        if audio.exists():
            result=client.post('/api/v1/copilot/sessions/'+session['id']+'/voice',files={'file':(audio.name,audio.read_bytes(),'audio/wav')})
            assert result.status_code==200,'Voice HTTP '+str(result.status_code)
            body=result.json();assert body.get('transcription') and body.get('provider_receipts'),'Expected genuine audio transcription'
            report['checks'].append({'type':'voice','transcription':body['transcription'],'operations':body['compound_operations'],'receipts':body['provider_receipts']})
        report['passed']=True
except Exception as error:
    report['failure']=str(error);print(json.dumps({'passed':False,'failure':str(error)}));sys.exitcode=1
finally:
    (root/'groq-live-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if not report['passed']:raise SystemExit(1)
    print(json.dumps({'passed':True,'checks':len(report['checks'])}))
