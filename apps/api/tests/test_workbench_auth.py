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


def test_copilot_requires_amount_and_transcription_provider(client, monkeypatch):
    from app.core.config import settings
    from app.ingestion.adapters import parse_paisa_amount
    c, factory = client
    c.post('/api/v1/auth/register', json=payload())
    c.headers['Origin'] = 'http://testserver'
    session_id = c.post('/api/v1/copilot/sessions', json={}).json()['id']
    assert c.post(f'/api/v1/copilot/sessions/{session_id}/messages', json={'query':'draft payment to supplier'}).status_code == 422
    assert c.get('/api/v1/actions').json() == []
    monkeypatch.setattr(settings, 'GEMINI_API_KEY', '')
    response = c.post(f'/api/v1/copilot/sessions/{session_id}/voice', files={'file':('note.webm', b'real-audio-not-a-fixture', 'audio/webm')})
    assert response.status_code == 503
    assert c.get('/api/v1/actions').json() == []
    assert parse_paisa_amount('5000.25 টাকা') == 500025
    assert parse_paisa_amount('২৫,০০০ টাকা') == 2500000


def test_case_action_version_guard_and_no_fake_external_execution(client):
    from app.persistence.models import CaseModel
    c, factory = client
    identity = c.post('/api/v1/auth/judge-session',json={}).json()
    c.headers['Origin'] = 'http://testserver'
    action_id = c.post('/api/v1/actions',json={'action_type':'supplier_payment','recipient':'Synthetic supplier','amount_paisa':1800000,'payload':{'case_id':identity['case_id'],'case_version':1}}).json()['action_id']
    assert c.post(f'/api/v1/actions/{action_id}/approve').status_code == 200
    assert c.post(f'/api/v1/actions/{action_id}/execute').status_code == 503
    assert c.get('/api/v1/actions').json()[0]['status'] == 'approved'
    with factory() as db:
        case = db.query(CaseModel).filter(CaseModel.id==identity['case_id']).one()
        case.current_version += 1
        db.commit()
    assert c.post(f'/api/v1/actions/{action_id}/execute').status_code == 409


def test_merchant_sale_collection_transfer_and_opening_receipts(client):
    c, _ = client
    identity = c.post('/api/v1/auth/register', json=payload()).json()
    c.headers['Origin'] = 'http://testserver'
    opening = {'description':'Verified synthetic opening','event_id':'opening-'+identity['tenant_id'],'postings':[{'account_code':'asset:cash','direction':'debit','amount_paisa':100000},{'account_code':'asset:wallet:bkash','direction':'debit','amount_paisa':50000},{'account_code':'equity:owner_capital','direction':'credit','amount_paisa':150000}]}
    assert c.post('/api/v1/ledger/post',json=opening).status_code == 200
    assert c.post('/api/v1/ledger/post',json=opening).status_code == 409
    customer = c.post('/api/v1/merchant/parties',json={'name':'Synthetic customer','party_type':'customer'}).json()['id']
    sale = c.post('/api/v1/merchant/sales',json={'sale_type':'credit','total_amount_paisa':10025,'party_id':customer})
    assert sale.status_code == 200 and sale.json()['sale_id']
    assert c.post('/api/v1/merchant/collect-due',json={'party_id':customer,'amount_paisa':5000}).json()['entry_id']
    assert c.get('/api/v1/merchant/today').json()['total_revenue_paisa'] == 10025
    assert c.get('/api/v1/merchant/parties').json()[0]['current_due_paisa'] == 5025
    transfer = c.post('/api/v1/merchant/transfer',json={'from_channel':'bkash','to_channel':'cash','principal_paisa':10000,'fee_paisa':185})
    assert transfer.status_code == 200 and transfer.json()['transfer_id']
    balances = {a['code']:a['current_balance_paisa'] for a in c.get('/api/v1/ledger/accounts').json()}
    assert balances['asset:cash'] == 115000
    assert balances['asset:wallet:bkash'] == 39815


def test_receiving_only_usable_units_and_pending_credit_cannot_apply(client):
    c, factory = client
    identity = c.post('/api/v1/auth/register',json=payload()).json()
    c.headers['Origin'] = 'http://testserver'
    product = c.post('/api/v1/stock/products',json={'name':'Synthetic rice','sku':'TEST-RICE','quantity_on_hand':0,'selling_price_paisa':12000}).json()
    receipt = c.post('/api/v1/receiving/receipts',json={'supplier_name':'Synthetic supplier','sku':'TEST-RICE','ordered_quantity':10,'received_quantity':8,'damaged_quantity':1,'unit_price_paisa':10000})
    assert receipt.status_code == 201
    assert receipt.json()['usable_quantity_added'] == 7
    stock = c.get('/api/v1/stock/products').json()['products'][0]
    assert stock['quantity_on_hand'] == 7 and stock['cost_price_paisa'] == 10000
    credit = c.get('/api/v1/receiving/credits').json()[0]
    assert credit['amount_bdt'] == 300 and credit['status'] == 'suspected'
    assert c.post('/api/v1/receiving/credits/'+credit['id']+'/apply',json={'invoice_ref':'TEST-INV'}).status_code >= 400
    assert c.get('/api/v1/receiving/credits').json()[0]['status'] == 'suspected'
    assert c.post('/api/v1/demand/unmet',json={'requested_product':'Synthetic rice','sku':'TEST-RICE','quantity':2}).status_code == 201
    analysis = c.get('/api/v1/demand/analysis/TEST-RICE')
    assert analysis.status_code == 200 and analysis.json()['current_stock'] == 7


def test_planner_has_no_fabricated_baseline_and_report_uses_real_accounts(client):
    c, _ = client
    c.post('/api/v1/auth/register',json=payload())
    c.headers['Origin'] = 'http://testserver'
    baseline = c.get('/api/v1/scenarios/baseline').json()
    assert baseline['opening_cash_paisa'] == 0
    assert baseline['assumed_daily_receipt_paisa'] == 0
    assert baseline['planned_outflows_paisa'] == [0] * 7
    c.post('/api/v1/auth/judge-session',json={})
    before = c.get('/api/v1/merchant/today').json()
    baseline = c.get('/api/v1/scenarios/baseline').json()
    data = {'case_id':'test','dates':baseline['dates'],'opening_cash_paisa':500000,'assumed_daily_receipt_paisa':0,'planned_outflows_paisa':[0]*7,'reserve_target_paisa':300000,'extra_expense_day_1_paisa':250000,'conditional_promise_paisa':100000,'conditional_promise_date':baseline['dates'][2]}
    scenario = c.post('/api/v1/scenarios/simulate',json=data).json()
    assert scenario['closing_cash_series'] == [250000,250000,350000,350000,350000,350000,350000]
    assert c.post('/api/v1/scenarios/save',json={**data,'name':'Synthetic planning test'}).status_code == 200
    saved = c.get('/api/v1/scenarios').json()[0]
    assert saved['planned_outflows_paisa'] == [0]*7 and saved['conditional_promise_paisa'] == 100000
    assert c.get('/api/v1/merchant/today').json() == before
    report = c.get('/api/v1/reports/operating-summary').json()
    assert report['cash_statement']['total_liquid_cash_paisa'] == 1200000


def test_inbox_and_reservation_actions_do_not_post_money(client):
    c, _ = client
    c.post('/api/v1/auth/judge-session',json={})
    c.headers['Origin'] = 'http://testserver'
    before = c.get('/api/v1/merchant/today').json()
    notification = c.post('/api/v1/notifications/emit',json={'title':'Synthetic alert','message':'Review receipt','category':'unresolved_receipt'}).json()
    assert c.post('/api/v1/notifications/'+notification['id']+'/snooze',json={'hours':4}).status_code == 200
    assert c.post('/api/v1/notifications/'+notification['id']+'/resolve').status_code == 200
    reservation = c.post('/api/v1/operations/reservations',json={'customer_name':'Synthetic customer','items':[{'sku':'RICE-025','quantity':1,'unit_price_paisa':10000}]}).json()
    assert reservation['status'] == 'reserved'
    assert c.post('/api/v1/operations/reservations/'+reservation['id']+'/pick').json()['status'] == 'picked'
    assert c.get('/api/v1/merchant/today').json() == before
    assert c.get('/api/v1/notifications/brief').json()['liquid_cash_bdt'] == 12000


def test_public_invoice_is_scoped_and_unverified_payments_cannot_post(client):
    from datetime import datetime,timedelta
    from app.persistence.models import CustomerPortalTokenModel
    c, factory = client
    c.post('/api/v1/auth/judge-session',json={})
    c.headers['Origin'] = 'http://testserver'
    capability = c.get('/api/v1/workbench/capabilities').json()
    assert next(r for r in capability['capabilities'] if r['id']=='payments')['state'] == 'unavailable'
    party = next(p for p in c.get('/api/v1/merchant/parties').json() if p['party_type']=='customer')
    link = c.post('/api/v1/portal/generate-link',json={'party_id':party['id'],'invoice_number':'TEST-ONLY','amount_paisa':10000}).json()
    token = link['token']
    before = c.get('/api/v1/merchant/today').json()
    invoice = c.get('/api/v1/portal/'+token).json()
    assert invoice['invoice_number']=='TEST-ONLY' and invoice['amount_paisa']==10000
    assert 'tenant_id' not in invoice and 'phone' not in invoice and 'accounts' not in invoice
    assert c.post('/api/v1/portal/'+token+'/pay').status_code == 503
    assert c.post('/api/v1/payments/sslcommerz/ipn',json={'status':'VALID','amount':'100','currency':'BDT','tran_id':'UNVERIFIED','token':token}).status_code == 503
    assert c.get('/api/v1/merchant/today').json() == before
    assert c.post('/api/v1/portal/'+token+'/dispute',json={'dispute_note':'Synthetic mismatch'}).status_code == 200
    with factory() as db:
        row=db.query(CustomerPortalTokenModel).filter_by(token=token).one()
        row.expires_at=datetime.utcnow()-timedelta(days=1)
        db.commit()
    assert c.get('/api/v1/portal/'+token).status_code == 410
    assert c.post('/api/v1/portal/'+token+'/dispute',json={'dispute_note':'Expired note'}).status_code == 410
