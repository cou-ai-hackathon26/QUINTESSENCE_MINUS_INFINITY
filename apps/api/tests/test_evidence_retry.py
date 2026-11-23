from test_workbench_auth import client

def test_retry_uses_same_private_source_and_keeps_human_review(client):
    c,_=client;c.post('/api/v1/auth/judge-session',json={});c.headers['Origin']='http://testserver'
    upload=c.post('/api/v1/evidence/upload',files={'file':('retry-source.txt',b'Original source with unknown amount','text/plain')}).json()
    identifier=upload['evidence_id'];before=c.get('/api/v1/evidence/'+identifier).json()
    retry=c.post('/api/v1/evidence/'+identifier+'/reprocess',json={})
    assert retry.status_code==200 and retry.json()['evidence_id']==identifier
    after=c.get('/api/v1/evidence/'+identifier).json()
    assert len(after['claims'])==1 and after['content_sha256']==before['content_sha256']
    assert c.patch('/api/v1/evidence/'+identifier+'/claims/'+after['claims'][0]['id'],json={'status':'confirmed','corrected_amount_paisa':12345}).status_code==200
    assert c.post('/api/v1/evidence/'+identifier+'/reprocess',json={}).status_code==409
    assert c.get('/api/v1/evidence/'+identifier).json()['claims'][0]['amount_paisa']==12345
    c.post('/api/v1/auth/judge-session',json={})
    assert c.post('/api/v1/evidence/'+identifier+'/reprocess',json={}).status_code==404
