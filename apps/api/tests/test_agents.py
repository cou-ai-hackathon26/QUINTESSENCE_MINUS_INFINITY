"""Actual agent contract tests with explicit offline model HTTP doubles."""
import json
import httpx
import pytest
from app.core.config import settings
from app.groq_provider import GroqProvider
from test_workbench_auth import client

@pytest.fixture
def provider(monkeypatch):
    monkeypatch.setattr(settings,'GROQ_API_KEY','explicit-agent-http-test-key')
    state={'calls':0,'hook':None}
    def handler(request):
        state['calls']+=1
        body=json.loads(request.content);context=json.loads(body['messages'][1]['content'])
        if state['hook']:state['hook'](state['calls'],context)
        source=context['case']['source_id'] if context.get('case') else 'ledger/current'
        inputs=context['case'].get('inputs') if context.get('case') else None
        facts={key:inputs.get(key) for key in ('payment_applicable','return_accepted','payment_included','return_included')} if inputs else None
        if body['response_format']['json_schema']['name']=='AgentConclusion':
            result={'answer':'Source facts need confirmation.','cited_source_ids':[source],'missing_facts':[],'proposed_operations':[],'suggested_page':'cases','case_facts':facts,'payable_options_paisa':context['specialist_outputs'].get('reconciliation',{}).get('expected_payables',[])}
        else:
            result={'summary':'Explicit test model read the supplied original inputs.','case_facts':facts,'findings':[{'source_id':source,'claim':'Inclusion is not yet established.','quote':context['structured_source_texts'][source]}],'missing_facts':[],'questions':[]}
        if state.get('mutate'):state['mutate'](result,context)
        return httpx.Response(200,json={'id':'explicit-model-double-'+str(state['calls']),'choices':[{'message':{'content':json.dumps(result)}}],'usage':{'prompt_tokens':20,'completion_tokens':12}})
    original=GroqProvider.__init__
    def init(self,*args,**kwargs):kwargs['transport']=httpx.MockTransport(handler);original(self,*args,**kwargs)
    monkeypatch.setattr(GroqProvider,'__init__',init)
    return state

def judge(c):
    identity=c.post('/api/v1/auth/judge-session',json={}).json();c.headers['Origin']='http://testserver';return identity

def test_compound_calls_actual_boundary_and_exact_tool_with_persisted_sources(client,provider):
    c,_=client;identity=judge(c)
    result=c.post('/api/v1/agents/runs',json={'case_type':'supplier_discrepancy','case_id':identity['case_id'],'query':'Investigate supplier invoice and prior inclusion','budget_max':4})
    assert result.status_code==202 and result.json()['status']=='queued'
    run_id=result.json()['run_id'];run=c.get('/api/v1/agents/runs/'+run_id).json()
    assert run['status']=='waiting_user' and run['budget_calls_used']==3
    assert provider['calls']==3 and len(run['provider_receipts'])==3
    assert all(r['status']=='succeeded' for r in run['provider_receipts'])
    events=c.get('/api/v1/agents/runs/'+run_id+'/events').json()
    tool=next(e['payload']['result'] for e in events if e['event_type']=='tool_receipt')
    # Seed demand 25,000; payment 4,000 has unknown inclusion; accepted return 3,000 is excluded.
    assert tool['expected_payables']==[1800000,2200000]
    assert tool['expected_state']=='unresolved'
    assert any(e['event_type']=='skeptic_critique' for e in events)
    sequences=[e['event_seq'] for e in events];assert sequences==sorted(set(sequences))

def test_no_provider_never_returns_successful_canned_investigation(client, monkeypatch):
    from app.core.config import settings
    monkeypatch.setattr(settings, 'GROQ_API_KEY', '')
    monkeypatch.setattr(settings, 'GROQ_API_KEYS', '')
    c,_=client;judge(c)
    result=c.post('/api/v1/agents/runs',json={'query':'Investigate invoice'})
    assert result.status_code==503

def test_simple_cash_query_reads_real_accounts_without_model_counter(client):
    c,_=client;judge(c)
    result=c.post('/api/v1/agents/runs',json={'case_type':'cash_query','query':'Current cash'})
    assert result.status_code==202
    run=c.get('/api/v1/agents/runs/'+result.json()['run_id']).json()
    assert run['status']=='completed' and run['budget_calls_used']==0
    events=c.get('/api/v1/agents/runs/'+run['id']+'/events').json()
    tool=next(e['payload'] for e in events if e['event_type']=='tool_receipt')
    assert tool['result']['ledger']['liquid_cash_paisa']==1200000
    assert run['provider_receipts']==[]
    cancelled=c.post('/api/v1/agents/runs/'+run['id']+'/cancel',json={}).json()
    assert cancelled['status']=='completed','Finished history must not be relabeled cancelled'

def test_model_budget_exhaustion_is_real_failure_after_only_one_model_call(client,provider):
    c,_=client;identity=judge(c)
    result=c.post('/api/v1/agents/runs',json={'case_id':identity['case_id'],'query':'Investigate supplier invoice','budget_max':1})
    run_id=result.json()['run_id'];run=c.get('/api/v1/agents/runs/'+run_id).json()
    assert run['status']=='failed' and run['budget_calls_used']==1 and provider['calls']==1
    events=c.get('/api/v1/agents/runs/'+run_id+'/events').json()
    assert events[-1]['payload']['error_code']=='budget_exhausted'

def test_cross_tenant_runs_and_case_references_are_private(client,provider):
    c,_=client;first=judge(c)
    result=c.post('/api/v1/agents/runs',json={'case_id':first['case_id'],'query':'Investigate supplier invoice'})
    run_id=result.json()['run_id'];judge(c)
    assert c.get('/api/v1/agents/runs/'+run_id).status_code==404
    assert c.get('/api/v1/agents/runs/'+run_id+'/events').status_code==404
    assert c.post('/api/v1/agents/runs/'+run_id+'/cancel',json={}).status_code==404
    assert c.post('/api/v1/agents/runs',json={'case_id':first['case_id'],'query':'Investigate other tenant'}).status_code==404

def test_cancel_during_inference_does_not_accept_inflight_findings(client,provider):
    from app.agents.real_orchestrator import AgentOrchestrator
    from app.persistence.models import AgentRunModel
    c,factory=client;identity=judge(c)
    def hook(count,context):
        if count==1:
            with factory() as db:
                run=db.query(AgentRunModel).filter_by(tenant_id=identity['tenant_id']).one()
                AgentOrchestrator(db,identity['tenant_id']).cancel_run(run.id)
    provider['hook']=hook
    result=c.post('/api/v1/agents/runs',json={'case_id':identity['case_id'],'query':'Investigate supplier inclusion'})
    run=c.get('/api/v1/agents/runs/'+result.json()['run_id']).json()
    assert run['status']=='cancelled' and provider['calls']==1
    assert all(task['status']=='cancelled' for task in run['tasks'])
    events=c.get('/api/v1/agents/runs/'+run['id']+'/events').json()
    assert not any(e['event_type']=='finding_recorded' for e in events)

def test_model_cannot_change_confirmed_case_flags(client,provider):
    c,_=client;identity=judge(c)
    provider['mutate']=lambda result,context:result['case_facts'].update({'return_included':None})
    result=c.post('/api/v1/agents/runs',json={'case_id':identity['case_id'],'query':'Investigate invoice'})
    run_id=result.json()['run_id'];run=c.get('/api/v1/agents/runs/'+run_id).json()
    assert run['status']=='failed' and provider['calls']==1
    events=c.get('/api/v1/agents/runs/'+run_id+'/events').json()
    assert events[-1]['payload']['error_code']=='agent_case_fact_mismatch'
    assert not any(e['event_type']=='finding_recorded' for e in events)

def test_old_run_confidence_is_hidden_after_case_version_changes(client,provider):
    c,_=client;identity=judge(c)
    result=c.post('/api/v1/agents/runs',json={'case_id':identity['case_id'],'query':'Investigate invoice'})
    run_id=result.json()['run_id'];initial=c.get('/api/v1/agents/runs/'+run_id).json()
    assert initial['case_assessment']['score']==59 and initial['source_version_stale'] is False
    case=c.get('/api/v1/cases/'+identity['case_id']).json()
    body={**case['inputs'],'payment_included':False,'expected_version':case['current_version']}
    assert c.put('/api/v1/cases/'+identity['case_id']+'/inputs',json=body).status_code==200
    old=c.get('/api/v1/agents/runs/'+run_id).json()
    assert old['source_version_stale'] is True and old['case_assessment'] is None
