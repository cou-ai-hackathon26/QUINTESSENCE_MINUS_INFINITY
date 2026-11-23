from test_workbench_auth import client


def test_judge_uses_persistent_sources_cases_and_mutations(client):
    c,_=client
    identity=c.post('/api/v1/auth/judge-session',json={}).json()
    c.headers['Origin']='http://testserver'
    assert identity['execution_mode']=='persistent_api'
    case=c.get('/api/v1/cases/'+identity['case_id']).json()
    assert case['inputs']['demand_paisa']==2500000
    assert len(case['claims'])==3 and case['latest_assessment']['score']==59
    source_id=case['inputs']['source_ids'][0]
    assert c.get('/api/v1/evidence/'+source_id+'/content').status_code==200
    assert len(c.get('/api/v1/buying/offers').json())==3
    assert len(c.get('/api/v1/receiving/receipts').json())==1
    before=c.get('/api/v1/merchant/today').json()
    recorded=c.post('/api/v1/merchant/sales',json={'sale_type':'cash','total_amount_paisa':12345})
    assert recorded.status_code==200 and recorded.json()['sale_id']
    assert c.get('/api/v1/auth/me').json()['case_id']==identity['case_id']
    assert c.get('/api/v1/merchant/today').json()['cash_balance_paisa']==before['cash_balance_paisa']+12345
    upload=c.post('/api/v1/evidence/upload',files={'file':('unseen.txt',b'Unseen invoice: TEST-883, amount BDT 765.43','text/plain')})
    assert upload.status_code==200
    document=c.get('/api/v1/evidence/'+upload.json()['evidence_id']).json()
    assert document['filename']=='unseen.txt'
    inputs={**case['inputs'],'payment_included':False,'expected_version':case['current_version']}
    updated=c.put('/api/v1/cases/'+identity['case_id']+'/inputs',json=inputs)
    assert updated.status_code==200 and updated.json()['current_version']==2
    assert c.get('/api/v1/cases/'+identity['case_id']).json()['latest_assessment'] is None
    assert c.post('/api/v1/cases/'+identity['case_id']+'/assess',json={}).status_code==200
    restored=c.get('/api/v1/cases/'+identity['case_id']).json()
    assert restored['inputs']['payment_included'] is False and restored['latest_assessment']['score']==100
    assert len(restored['claims'])==3
    assert c.put('/api/v1/cases/'+identity['case_id']+'/inputs',json=inputs).status_code==409
    other=c.post('/api/v1/auth/judge-session',json={}).json()
    assert other['tenant_id']!=identity['tenant_id']
    assert c.get('/api/v1/evidence/'+document['id']).status_code==404


def test_case_source_references_cannot_attach_other_tenant_evidence(client):
    c,_=client
    first=c.post('/api/v1/auth/judge-session',json={}).json()
    own=c.get('/api/v1/cases/'+first['case_id']).json()
    c.headers['Origin']='http://testserver'
    second=c.post('/api/v1/auth/judge-session',json={}).json()
    body={**own['inputs'],'expected_version':1}
    assert c.put('/api/v1/cases/'+second['case_id']+'/inputs',json=body).status_code==404
