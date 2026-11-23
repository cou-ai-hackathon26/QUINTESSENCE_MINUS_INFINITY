from test_workbench_auth import client

def test_supplier_acceptance_requires_original_source_and_explicit_owner_review(client):
    c,_=client;c.post('/api/v1/auth/judge-session',json={});c.headers['Origin']='http://testserver'
    note=c.get('/api/v1/receiving/credits').json()[0]
    assert note['status']=='suspected'
    path='/api/v1/receiving/credits/'+note['id']
    assert c.post(path+'/apply',json={'invoice_ref':'INV-025'}).status_code==400
    assert c.post(path+'/accept',json={'source_evidence_id':'missing','confirmed_supplier_accepted':True}).status_code==422
    proof=c.post('/api/v1/evidence/upload',files={'file':('supplier-acceptance.txt',b'SYNTHETIC ONLY. Supplier explicitly accepted the credit amount shown.','text/plain')}).json()
    assert c.post(path+'/accept',json={'source_evidence_id':proof['evidence_id'],'confirmed_supplier_accepted':False}).status_code==422
    before=c.get('/api/v1/merchant/today').json()
    accepted=c.post(path+'/accept',json={'source_evidence_id':proof['evidence_id'],'confirmed_supplier_accepted':True})
    assert accepted.status_code==200 and accepted.json()['status']=='accepted_by_supplier'
    brief=c.get('/api/v1/notifications/brief').json()
    assert brief['accepted_unapplied_credit_paisa']==int(note['amount_bdt']*100)
    assert brief['liquid_cash_paisa']==before['cash_balance_paisa']+before['digital_wallet_balance_paisa']
    assert c.get('/api/v1/merchant/today').json()==before,'Acceptance cannot create spendable cash or deduct liabilities'
    applied=c.post(path+'/apply',json={'invoice_ref':'INV-025'})
    assert applied.status_code==200 and applied.json()['status']=='applied_to_bill'
    assert 'No cash movement' in applied.json()['scope']
    assert c.post(path+'/apply',json={'invoice_ref':'INV-026'}).status_code==400
    assert c.get('/api/v1/merchant/today').json()==before

def test_receipt_retry_updates_stock_once_and_rejects_changed_details(client):
    c,_=client;c.post('/api/v1/auth/judge-session',json={});c.headers['Origin']='http://testserver'
    product=c.get('/api/v1/merchant/products').json()[0]
    body={'supplier_name':'Synthetic supplier','sku':product['sku'],'ordered_quantity':4,'received_quantity':4,'damaged_quantity':1,'unit_price_paisa':10000}
    first=c.post('/api/v1/receiving/receipts',json=body,headers={'Idempotency-Key':'receiving-test-01'})
    second=c.post('/api/v1/receiving/receipts',json=body,headers={'Idempotency-Key':'receiving-test-01'})
    assert first.status_code==second.status_code==201
    assert first.json()['receipt_id']==second.json()['receipt_id']
    assert c.get('/api/v1/merchant/products').json()[0]['quantity_on_hand']==product['quantity_on_hand']+3
    assert c.post('/api/v1/receiving/receipts',json={**body,'received_quantity':3},headers={'Idempotency-Key':'receiving-test-01'}).status_code==422
