"""Reviewed model interpretations must produce exact, balanced, once-only internal records."""
import json
import pytest
from test_workbench_auth import client
from app.persistence.models import CopilotMessageModel,PartyModel,JournalEntryModel,PostingModel,AccountModel

def setup(c,factory,kind='debt_collection',amount=50000):
    identity=c.post('/api/v1/auth/judge-session',json={}).json();c.headers['Origin']='http://testserver'
    session=c.post('/api/v1/copilot/sessions',json={}).json()
    with factory() as db:
        message=CopilotMessageModel(tenant_id=identity['tenant_id'],session_id=session['id'],role='assistant',content='Synthetic reviewed source',audio_metadata_json=json.dumps({'proposed_operations':[{'type':kind,'party_name':'Synthetic customer','amount_paisa':amount,'payment_method':'cash','source_quote':'Synthetic explicit source'}]}))
        db.add(message);db.commit();message_id=message.id
    path='/api/v1/copilot/proposals/'+message_id+'/0'
    source=c.get(path).json()
    people=c.get('/api/v1/merchant/parties').json()
    party=next((p for p in people if p['party_type']==('supplier' if kind=='supplier_payment' else 'customer')),None)
    body={'confirmed':True,'source_hash':source['source_hash'],'amount_paisa':amount,'channel':'cash','party_id':party['id'] if kind in ('credit_sale','debt_collection','supplier_payment') else None,'expected_party_due_paisa':party['current_due_paisa'] if party else None,'expected_account_balance_paisa':500000}
    return identity,path,body

def test_collection_changes_cash_and_due_once_without_new_revenue(client):
    c,factory=client;identity,path,body=setup(c,factory)
    before=c.get('/api/v1/merchant/today').json()
    first=c.post(path+'/record',json=body);assert first.status_code==200
    repeat=c.post(path+'/record',json=body)
    assert repeat.status_code==200 and repeat.json()['idempotent_replay'] is True
    assert first.json()['entry_id']==repeat.json()['entry_id']
    after=c.get('/api/v1/merchant/today').json()
    assert after['cash_balance_paisa']==before['cash_balance_paisa']+50000
    assert after['customer_dues_paisa']==before['customer_dues_paisa']-50000
    assert after['total_revenue_paisa']==before['total_revenue_paisa']
    assert c.get(path).json()['recorded_entry_id']==first.json()['entry_id']
    assert c.post(path+'/record',json={**body,'amount_paisa':60000}).status_code==409
    with factory() as db:
        postings=db.query(PostingModel).filter_by(journal_entry_id=first.json()['entry_id']).all()
        assert sum(p.amount_paisa for p in postings if p.direction=='debit')==sum(p.amount_paisa for p in postings if p.direction=='credit')==50000

def test_credit_sale_changes_due_and_revenue_but_not_cash(client):
    c,factory=client;identity,path,body=setup(c,factory,'credit_sale',20000)
    before=c.get('/api/v1/merchant/today').json();assert c.post(path+'/record',json=body).status_code==200
    after=c.get('/api/v1/merchant/today').json()
    assert after['customer_dues_paisa']==before['customer_dues_paisa']+20000
    assert after['cash_balance_paisa']==before['cash_balance_paisa']
    assert after['total_revenue_paisa']==before['total_revenue_paisa']+20000

def test_unknown_source_changed_due_and_missing_confirmation_block_all_writes(client):
    c,factory=client;identity,path,body=setup(c,factory)
    before=c.get('/api/v1/merchant/today').json()
    assert c.post(path+'/record',json={**body,'confirmed':False}).status_code==422
    assert c.post(path+'/record',json={**body,'source_hash':'0'*64}).status_code==409
    assert c.post(path+'/record',json={**body,'expected_party_due_paisa':body['expected_party_due_paisa']-1}).status_code==409
    assert c.post(path+'/record',json={**body,'amount_paisa':body['expected_party_due_paisa']+1}).status_code==422
    assert c.get('/api/v1/merchant/today').json()==before
    c.post('/api/v1/auth/judge-session',json={})
    assert c.get(path).status_code==404
    assert c.post(path+'/record',json=body).status_code==404

@pytest.mark.parametrize('kind',['expense','supplier_payment'])
def test_unfunded_outflow_rolls_back_due_accounts_and_entry(client,kind):
    c,factory=client;identity,path,body=setup(c,factory,kind,600000)
    before=c.get('/api/v1/merchant/today').json()
    with factory() as db:count=db.query(JournalEntryModel).filter_by(tenant_id=identity['tenant_id']).count()
    assert c.post(path+'/record',json=body).status_code==422
    assert c.get('/api/v1/merchant/today').json()==before
    with factory() as db:assert db.query(JournalEntryModel).filter_by(tenant_id=identity['tenant_id']).count()==count

def test_partial_known_inclusion_keeps_only_mathematically_possible_payables():
    from app.domain.reconciliation import ReconciliationEngine,DemandFact,PaymentFact,ReturnFact
    from app.domain.money import Money
    args={'case_id':'synthetic','demand':DemandFact('I',Money(2500000)),'eligible_payment':PaymentFact('P','I',Money(400000)),'accepted_return':ReturnFact('R','I',Money(300000))}
    assert ReconciliationEngine.evaluate(**args,payment_included=True,return_included=None).expected_payables==[2200000,2500000]
    assert ReconciliationEngine.evaluate(**args,payment_included=None,return_included=True).expected_payables==[2100000,2500000]

def test_concurrent_retry_of_same_source_creates_one_entry_and_one_due_change(tmp_path):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from fastapi.testclient import TestClient
    from app.main import app
    from app.core.database import Base,get_db
    from app.persistence.models import UserModel
    from app.api.v1.proposal_review import record_reviewed_proposal,ReviewDTO
    engine=create_engine('sqlite:///'+str(tmp_path/'proposal-race.db'),connect_args={'check_same_thread':False})
    Base.metadata.create_all(engine);factory=sessionmaker(bind=engine)
    def database():
        with factory() as db:yield db
    app.dependency_overrides[get_db]=database
    try:
        with TestClient(app) as c:
            identity,path,body=setup(c,factory);before=c.get('/api/v1/merchant/today').json();barrier=Barrier(2)
            def record():
                with factory() as db:
                    user=db.query(UserModel).filter_by(id=identity['user_id']).one();barrier.wait()
                    return record_reviewed_proposal(path.split('/')[-2],0,ReviewDTO(**body),user,db)
            with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(lambda _:record(),range(2)))
            assert {r['status'] for r in results}=={'recorded','already_recorded'}
            assert results[0]['entry_id']==results[1]['entry_id']
            after=c.get('/api/v1/merchant/today').json()
            assert after['cash_balance_paisa']==before['cash_balance_paisa']+50000
            assert after['customer_dues_paisa']==before['customer_dues_paisa']-50000
    finally:app.dependency_overrides.clear();engine.dispose()
