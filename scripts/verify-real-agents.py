"""Actual application background specialists and multilingual hybrid retrieval."""
import json,time
from pathlib import Path
import httpx

report={'scope':'Actual local app HTTP, genuine Groq specialist requests, deterministic reconciliation, real local E5 retrieval','passed':False,'poll_states':[]}
try:
    with httpx.Client(base_url='http://127.0.0.1:8000',timeout=180,headers={'Origin':'http://127.0.0.1:8000'}) as client:
        identity=client.post('/api/v1/auth/judge-session',json={}).json()
        for content in ['Damaged goods may be returned within seven days of delivery. An invoice is required.','Karim bought two hundred taka of rice on credit.','The shop opens at nine in the morning and closes at night.']:
            result=client.post('/api/v1/search/index',json={'source_type':'note','content':content})
            assert result.status_code==201
        search=client.post('/api/v1/search',json={'query':'নষ্ট পণ্য কত দিনের মধ্যে ফেরত দেওয়া যাবে?','top_k':3}).json()
        report['retrieval']={key:search.get(key) for key in ['retrieval_mode','semantic','results']}
        assert search['retrieval_mode']=='hybrid_bm25_dense_rrf'
        assert search['results'][0]['content'].startswith('Damaged goods')
        started=time.monotonic()
        response=client.post('/api/v1/agents/runs',json={'case_type':'reconciliation','case_id':identity['case_id'],'query':'এই supplier-এর দাবি থেকে আগের payment আর return বাদ গেছে কি? কী নিশ্চিত, কী অজানা, আর কত দিতে হবে—প্রমাণসহ তদন্ত করো।','budget_max':4})
        report['start_http_ms']=int((time.monotonic()-started)*1000)
        assert response.status_code==202,'Expected accepted asynchronous run'
        run_id=response.json()['run_id'];deadline=time.monotonic()+160
        while time.monotonic()<deadline:
            run=client.get('/api/v1/agents/runs/'+run_id).json()
            state={'status':run['status'],'tasks':[(t['role'],t['status']) for t in run['tasks']]}
            if not report['poll_states'] or state!=report['poll_states'][-1]:report['poll_states'].append(state)
            if run['status'] not in ('queued','running'):break
            time.sleep(.5)
        events=client.get('/api/v1/agents/runs/'+run_id+'/events').json()
        report.update({'run':run,'events':events,'elapsed_ms':int((time.monotonic()-started)*1000)})
        assert run['status'] in ('completed','waiting_user'),str(events[-1])
        assert len(run['provider_receipts'])==3 and all(r['status']=='succeeded' for r in run['provider_receipts'])
        tool=next(e['payload']['result'] for e in events if e['event_type']=='tool_receipt')
        assert tool['expected_payables']==[1800000,2200000] and tool['expected_state']=='unresolved'
        conclusion=next(e['payload'] for e in events if e['event_type']=='finding_recorded' and e['role']=='report')
        assert conclusion['case_facts']['return_included'] is False and conclusion['case_facts']['payment_included'] is None
        assert sorted(conclusion['payable_options_paisa'])==[1800000,2200000]
        report['passed']=True
except Exception as error:report['failure']=str(error)
finally:
    Path('docs/evidence/real-workflow/JR-03').mkdir(parents=True,exist_ok=True)
    Path('docs/evidence/real-workflow/JR-03/actual-agent-retrieval.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'passed':report['passed'],'start_http_ms':report.get('start_http_ms'),'poll_states':len(report['poll_states']),'failure':report.get('failure')}))
    if not report['passed']:raise SystemExit(1)
