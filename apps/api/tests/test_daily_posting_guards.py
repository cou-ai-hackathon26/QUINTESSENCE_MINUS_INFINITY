"""Ordinary merchant API invariants after removing the fixture interceptor."""
from test_workbench_auth import client

def judge(c):
    identity=c.post('/api/v1/auth/judge-session',json={}).json();c.headers['Origin']='http://testserver';return identity

def test_sale_retry_posts_once_and_reused_key_cannot_change_payload(client):
    c,_=client;judge(c);before=c.get('/api/v1/merchant/today').json()
    first=c.post('/api/v1/merchant/sales',headers={'Idempotency-Key':'synthetic-sale-01'},json={'sale_type':'cash','total_amount_paisa':12345})
    second=c.post('/api/v1/merchant/sales',headers={'Idempotency-Key':'synthetic-sale-01'},json={'sale_type':'cash','total_amount_paisa':12345})
    assert first.status_code==second.status_code==200 and first.json()['sale_id']==second.json()['sale_id']
    assert c.get('/api/v1/merchant/today').json()['cash_balance_paisa']==before['cash_balance_paisa']+12345
    assert c.post('/api/v1/merchant/expenses',headers={'Idempotency-Key':'synthetic-sale-01'},json={'amount_paisa':12345,'description':'Different event'}).status_code==409

def test_server_blocks_unfunded_money_movements_without_changing_balances(client):
    c,_=client;judge(c);before=c.get('/api/v1/merchant/today').json()
    supplier=next(p for p in c.get('/api/v1/merchant/parties').json() if p['party_type']=='supplier')
    operations=[('/expenses',{'amount_paisa':500001,'description':'Too much'}),('/withdrawals',{'amount_paisa':500001}),('/transfer',{'from_channel':'nagad','to_channel':'cash','principal_paisa':500000,'fee_paisa':1}),('/supplier-payment',{'amount_paisa':500001,'party_id':supplier['id'],'channel':'cash'})]
    for path,payload in operations:
        assert c.post('/api/v1/merchant'+path,json=payload).status_code==422
        assert c.get('/api/v1/merchant/today').json()==before

def test_invalid_party_and_duplicate_stock_lines_cannot_silently_post(client):
    c,_=client;judge(c);before=c.get('/api/v1/merchant/today').json()
    product=c.get('/api/v1/merchant/products').json()[0]
    assert product['quantity_on_hand']==4
    assert c.post('/api/v1/merchant/sales',json={'sale_type':'credit','total_amount_paisa':10000}).status_code==422
    assert c.post('/api/v1/merchant/sales',json={'sale_type':'split','total_amount_paisa':10000,'cash_received_paisa':10001}).status_code==422
    assert c.post('/api/v1/merchant/sales',json={'sale_type':'cash','total_amount_paisa':10000,'items':[{'product_id':product['id'],'quantity':3},{'product_id':product['id'],'quantity':2}]}).status_code==422
    assert c.get('/api/v1/merchant/products').json()[0]['quantity_on_hand']==4
    assert c.get('/api/v1/merchant/today').json()==before

def test_party_opening_dues_are_balanced_and_do_not_create_revenue(client):
    c,_=client;judge(c);before=c.get('/api/v1/merchant/today').json()
    party=c.post('/api/v1/merchant/parties',json={'name':'Synthetic opening customer','party_type':'customer','initial_due_paisa':45000})
    assert party.status_code==200
    after=c.get('/api/v1/merchant/today').json()
    assert after['customer_dues_paisa']==before['customer_dues_paisa']+45000 and after['total_revenue_paisa']==before['total_revenue_paisa']
    assert c.post('/api/v1/merchant/collect-due',json={'party_id':party.json()['id'],'amount_paisa':45001}).status_code==422

def test_cross_tenant_party_and_product_cannot_create_unlinked_records(client):
    c,_=client;judge(c);party=next(p for p in c.get('/api/v1/merchant/parties').json() if p['party_type']=='customer');product=c.get('/api/v1/merchant/products').json()[0]
    judge(c)
    assert c.post('/api/v1/merchant/sales',json={'sale_type':'credit','total_amount_paisa':1000,'party_id':party['id']}).status_code==422
    assert c.post('/api/v1/merchant/sales',json={'sale_type':'cash','total_amount_paisa':1000,'items':[{'product_id':product['id'],'quantity':1}]}).status_code==422

def test_runtime_has_no_shared_demo_or_otp_test_shortcut(client,monkeypatch):
    from app.core.config import settings
    c,_=client;monkeypatch.setattr(settings,'ALLOW_LEGACY_TEST_AUTH',False)
    assert c.post('/api/v1/auth/demo-session',json={}).status_code==410
    assert c.post('/api/v1/auth/login',json={'phone':'01712345678','otp':'123456'}).status_code==503
    assert c.post('/api/v1/auth/judge-session',json={}).status_code==201
