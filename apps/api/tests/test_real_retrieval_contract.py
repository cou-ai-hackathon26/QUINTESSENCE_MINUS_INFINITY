from test_workbench_auth import client

def test_unrelated_query_returns_no_hash_vector_noise(client):
    c,_=client;c.post('/api/v1/auth/judge-session',json={});c.headers['Origin']='http://testserver'
    indexed=c.post('/api/v1/search/index',json={'source_type':'note','content':'Synthetic red bicycle repair schedule','embedding':[1]*16,'metadata':{'embedding_model':'pretend-live-model'}})
    assert indexed.status_code==201
    result=c.post('/api/v1/search',json={'query':'astronomy quantum telescope'}).json()
    assert result['results']==[] and result['is_sufficient'] is False
    assert result['retrieval_mode']=='keyword_only' and result['semantic']['enabled'] is False

def test_source_link_must_belong_to_current_tenant(client):
    c,_=client;first=c.post('/api/v1/auth/judge-session',json={}).json();c.headers['Origin']='http://testserver'
    case=c.get('/api/v1/cases/'+first['case_id']).json();document=case['inputs']['source_ids'][0]
    c.post('/api/v1/auth/judge-session',json={})
    assert c.post('/api/v1/search/index',json={'source_type':'note','document_id':document,'content':'Do not link someone else\'s private file'}).status_code==404

def test_reviewed_aliases_do_not_replace_inside_unrelated_words():
    from app.retrieval.engine import normalize_search_query
    assert normalize_search_query('price unchanged')=='price unchanged'
