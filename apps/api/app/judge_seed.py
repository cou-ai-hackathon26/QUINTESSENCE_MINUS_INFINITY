"""One-time sample records in an isolated merchant tenant; no alternate execution engine."""
import json
from datetime import timedelta
from app.persistence import models as m
from app.ingestion.storage import storage
from app.retrieval.engine import normalize_search_query
from app.confidence.policy import evaluate_confidence


def seed_judge_workflows(db,tenant,case):
    sources=[]
    documents=[
        ('INV-025','Supplier demand','Supplier Rahman Traders. Invoice INV-025. Current demand BDT 25,000. Prior payment inclusion is not established.',2500000,'invoice'),
        ('PAY-004','Payment receipt','Payment PAY-004 of BDT 4,000 applies to invoice INV-025. This receipt does not establish whether the supplier already deducted it.',400000,'bill'),
        ('RETURN-003','Accepted return','Supplier accepted return RETURN-003 worth BDT 3,000 for invoice INV-025. Supplier confirms this return is not yet deducted from the current demand.',300000,'return_terms'),
    ]
    for reference,title,text,amount,kind in documents:
        text='SEEDED EXAMPLE RECORD - not a real merchant document.\n'+text
        digest,file_path,size,source_type=storage.store_file(tenant.id,reference+'.txt',text.encode('utf-8'),'text/plain')
        evidence=m.EvidenceModel(tenant_id=tenant.id,filename=reference+'.txt',mime_type='text/plain',file_size_bytes=size,content_sha256=digest,storage_path=file_path,source_type=source_type,status='reviewed')
        db.add(evidence);db.flush()
        db.add(m.ExtractedClaimModel(tenant_id=tenant.id,evidence_id=evidence.id,party_name='রহমান ট্রেডার্স',invoice_ref='INV-025',amount_paisa=amount,status='confirmed',is_reviewed=True,raw_model_response=text))
        db.add(m.DocumentChunkModel(tenant_id=tenant.id,document_id=evidence.id,chunk_index=0,source_type=kind,content=text,normalized_content=normalize_search_query(text),metadata_json=json.dumps({'invoice_ref':'INV-025','reference':reference,'origin':'seeded_example'})))
        sources.append({'reference':reference,'evidence_id':evidence.id,'title':title})
    inputs={'demand_paisa':2500000,'payment_paisa':400000,'return_paisa':300000,'source_refs':[s['reference'] for s in sources],'source_ids':[s['evidence_id'] for s in sources],'supplier':'রহমান ট্রেডার্স','payment_applicable':True,'return_accepted':True,'payment_included':None,'return_included':False}
    version=db.query(m.CaseVersionModel).filter_by(case_id=case.id,version_num=1).one()
    version.state_snapshot_json=json.dumps({'origin':'seeded_example','inputs':inputs})
    claims=[('payment_applicable','supported',sources[1],{'amount_paisa':400000}),('return_acceptance_and_prior_inclusion','supported',sources[2],{'accepted':True,'prior_included':False}),('payment_prior_inclusion','unknown',sources[0],{'included':None})]
    for key,state,source,value in claims:
        db.add(m.EvidenceClaimModel(tenant_id=tenant.id,case_id=case.id,claim_key=key,is_critical=True,weight=3,state=state,evaluator_type='human',source_locator_json=json.dumps(source),claim_value_json=json.dumps(value),reasons_json=json.dumps(['Seeded example document; supplier payment inclusion still needs clarification'])))
    confidence=evaluate_confidence(claims=[{'key':key,'critical':True,'state':state,'weight':3} for key,state,_,_ in claims])
    db.add(m.ConfidenceAssessmentModel(tenant_id=tenant.id,case_id=case.id,case_version=1,base_score=confidence.base_score,score=confidence.score,band=confidence.band,readiness=confidence.readiness,can_execute_without_approval=False,policy_version=confidence.policy_version))
    for supplier,title,price,delivery,bonus in [('রহমান ট্রেডার্স','25kg rice; delivery extra',119000,18000,None),('শাপলা এন্টারপ্রাইজ','6+1 offer; eligibility needs confirmation',116000,30000,{'description':'6+1','is_verified':False}),('নাবিল অ্যান্ড সন্স','Delivery included',122000,0,None)]:
        db.add(m.SupplierOfferModel(tenant_id=tenant.id,supplier_name=supplier,title=title,sku='RICE-025',base_unit_price_paisa=price,pack_size=1,pack_unit='bag',min_order_quantity=1,delivery_fee_paisa=delivery,bonus_condition_json=json.dumps(bonus) if bonus else None,source_type='seeded_example',confidence_score=59 if bonus else 85,has_critical_blocker=bool(bonus)))
    receipt=m.GoodsReceiptModel(tenant_id=tenant.id,supplier_name='রহমান ট্রেডার্স',sku='RICE-025',ordered_quantity=10,received_quantity=8,damaged_quantity=1,shortage_quantity=2,status='discrepant',batch_number='EXAMPLE-RECEIPT')
    db.add(receipt);db.flush()
    db.add(m.CreditNoteModel(tenant_id=tenant.id,receipt_id=receipt.id,supplier_name='রহমান ট্রেডার্স',claim_reason='shortage_and_damaged',amount_paisa=360000,status='suspected',return_window_deadline=m.now_utc()+timedelta(days=7)))
    db.add(m.UnmetDemandModel(tenant_id=tenant.id,customer_name='উদাহরণের ক্রেতা',requested_product='মিনিকেট চাল ২৫ কেজি',sku='RICE-025',quantity=3,reason='stockout'))
    db.add(m.ActionModel(tenant_id=tenant.id,action_type='customer_reminder',recipient='করিম',status='draft',payload_json=json.dumps({'origin':'seeded_example','note':'Review due before contacting customer; nothing has been sent.'})))
    supplier=db.query(m.PartyModel).filter_by(tenant_id=tenant.id,party_type='supplier').one()
    for reference,amount,days in [('INV-101',600000,1),('INV-102',400000,2),('INV-103',1500000,4)]:
        db.add(m.ObligationModel(tenant_id=tenant.id,party_id=supplier.id,party_name=supplier.name,invoice_ref=reference,amount_paisa=amount,accepted_methods='cash',status='supported',due_at=m.now_utc()+timedelta(days=days)))
    db.add(m.RecurringCommitmentModel(tenant_id=tenant.id,title='দোকান ভাড়া',category='rent',amount_paisa=800000,frequency='monthly',due_day_of_month=28))
    for title,message,category,entity,entity_id in [
        ('Supplier payment inclusion যাচাই করুন','রসিদ আছে; current demand-এ আগে বাদ আছে কি না নিশ্চিত করুন।','unresolved_receipt','case',case.id),
        ('কম পাওয়া মাল ও ক্ষতির credit দেখুন','Supplier acceptance pending; suspected credit কোনো payable কমায়নি।','unapplied_credit','receiving',receipt.id),
        ('দুই দিন পরের cash payment দেখুন','Supported obligation আছে; spending scenario-তে প্রভাব দেখুন।','cash_constraint','planner',None),
    ]:
        db.add(m.NotificationModel(tenant_id=tenant.id,title=title,message=message,category=category,priority='high',status='unread',target_entity_type=entity,target_entity_id=entity_id,dedup_key='seed-'+category))
    db.add(m.CustomerReservationModel(tenant_id=tenant.id,customer_name='উদাহরণের pickup customer',items_json=json.dumps([{'sku':'RICE-025','quantity':1,'unit_price_paisa':130000}]),status='reserved',total_estimated_paisa=130000,deposit_paisa=0,expires_at=m.now_utc()+timedelta(hours=24)))
    db.add(m.ReturnableContainerModel(tenant_id=tenant.id,container_type='crate',party_name='উদাহরণের beverage supplier',issued_count=12,returned_count=8,outstanding_count=4,deposit_per_unit_paisa=5000,total_deposit_held_paisa=20000))
    db.add(m.ShiftHandoverModel(tenant_id=tenant.id,shift_name='উদাহরণের evening shift',opened_by='Owner',closed_by='Cashier',declared_cash_paisa=497500,system_cash_paisa=500000,variance_paisa=-2500,possible_reasons_json='[]'))
    db.add(m.BusinessDocumentModel(tenant_id=tenant.id,doc_type='lease_agreement',title='উদাহরণের shop lease metadata',issuing_authority='Example landlord',expiry_date='2027-06-30',status='pending_verification'))
    return sources
