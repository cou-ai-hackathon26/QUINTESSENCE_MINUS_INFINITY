import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.core.database import Base,get_db
from app.api.v1.workbench_auth import _attempts
from app.persistence.models import UserCredentialModel,PostingModel

@pytest.fixture
def client():
    engine=create_engine('sqlite:///:memory:',connect_args={'check_same_thread':False},poolclass=StaticPool)
    Base.metadata.create_all(engine)
    factory=sessionmaker(bind=engine)
    def db():
        with factory() as session: yield session
    app.dependency_overrides[get_db]=db
    _attempts.clear()
    with TestClient(app) as c: yield c,factory
    app.dependency_overrides.clear();engine.dispose()

def payload():
    return {'name':'Synthetic reviewer','shop_name':'Synthetic shop','phone':'017'+str(uuid.uuid4().int)[-8:],'password':'Synthetic-password-1234','role':'admin'}

def test_register_cookie_login_logout_and_no_otp_bypass(client):
    c,factory=client;p=payload()
    result=c.post('/api/v1/auth/register',json=p)
    assert result.status_code==201
    body=result.json();assert body['role']=='owner' and body['is_demo'] is False
    assert 'HttpOnly' in result.headers['set-cookie'] and 'SameSite=strict' in result.headers['set-cookie']
    assert c.get('/api/v1/auth/me').json()['shop_name']==p['shop_name']
    assert c.post('/api/v1/auth/login',json={'phone':p['phone'],'otp':'123456'}).status_code==401
    with factory() as db:
        credential=db.query(UserCredentialModel).one()
        assert p['password'] not in credential.password_hash and len(credential.password_hash)==128
    old=body['access_token']
    assert c.post('/api/v1/auth/logout',json={},headers={'Origin':'http://testserver'}).status_code==200
    assert c.get('/api/v1/auth/me',headers={'Authorization':'Bearer '+old}).status_code==401
    assert c.post('/api/v1/auth/password-login',json={**p,'password':'wrong'}).status_code==401
    fresh=c.post('/api/v1/auth/password-login',json=p)
    assert fresh.status_code==200 and fresh.json()['access_token']!=old
    assert c.get('/api/v1/merchant/today').json()['cash_balance_paisa']==0

def test_judge_isolation_balanced_seed_and_cookie_csrf(client):
    c,factory=client
    a=c.post('/api/v1/auth/judge-session',json={}).json()
    summary=c.get('/api/v1/merchant/today').json()
    assert summary['cash_balance_paisa']==500000 and summary['digital_wallet_balance_paisa']==700000
    assert summary['customer_dues_paisa']==1850000 and summary['supplier_dues_paisa']==2500000
    assert c.post('/api/v1/merchant/expenses',json={'amount_paisa':100,'description':'Synthetic'},headers={'Origin':'https://untrusted.invalid'}).status_code==403
    b=c.post('/api/v1/auth/judge-session',json={}).json()
    assert a['tenant_id']!=b['tenant_id'] and a['user_id']!=b['user_id']
    assert c.get('/api/v1/cases/'+a['case_id']).status_code==404
    assert c.get('/api/v1/auth/me',headers={'Authorization':'Bearer '+a['access_token']}).status_code==401
    with factory() as db:
        postings=db.query(PostingModel).all()
        assert sum(p.amount_paisa for p in postings if p.direction=='debit')==sum(p.amount_paisa for p in postings if p.direction=='credit')

def test_registration_validation_and_duplicate_identity(client):
    c,_=client;p=payload()
    assert c.post('/api/v1/auth/register',json={**p,'password':'short'}).status_code==422
    assert c.post('/api/v1/auth/register',json={**p,'phone':'invalid'}).status_code==400
    assert c.post('/api/v1/auth/register',json=p).status_code==201
    assert c.post('/api/v1/auth/register',json=p).status_code==409

def test_cashflow_uses_tenant_owned_postings_and_excludes_internal_transfer_gross(client):
    from app.persistence.models import AccountModel,JournalEntryModel
    c,factory=client
    session=c.post('/api/v1/auth/judge-session',json={}).json()
    with factory() as db:
        accounts=db.query(AccountModel).filter_by(tenant_id=session['tenant_id']).all()
        cash=next(a for a in accounts if a.code=='asset:cash')
        wallet=next(a for a in accounts if a.code=='asset:wallet:bkash')
        entry=JournalEntryModel(tenant_id=session['tenant_id'],entry_number='SYNTHETIC-TRANSFER',description='Internal transfer')
        db.add(entry);db.flush()
        db.add_all([PostingModel(journal_entry_id=entry.id,account_id=cash.id,direction='credit',amount_paisa=10000),PostingModel(journal_entry_id=entry.id,account_id=wallet.id,direction='debit',amount_paisa=10000)])
        db.commit()
    flow=c.get('/api/v1/workbench/cashflow')
    assert flow.status_code==200
    assert sum(flow.json()['incoming_paisa'])==1200000
    assert sum(flow.json()['outgoing_paisa'])==0
    assert len(flow.json()['dates'])==7
