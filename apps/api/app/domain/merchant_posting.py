"""One atomic posting boundary for ordinary daily merchant mutations."""
import hashlib,json,uuid
from collections import Counter
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from app.domain.ledger import StandardAccount as A
from app.persistence.models import AccountModel,PartyModel,ProductItemModel,JournalEntryModel,PostingModel,StockMovementModel,AuditLogModel

def record(db,tenant_id,kind,data,request_key=None):
    if request_key and (len(request_key)>100 or not request_key.strip()):raise HTTPException(422,'Use a non-empty idempotency key of at most 100 characters.')
    key='merchant:'+request_key if request_key else 'merchant:'+str(uuid.uuid4())
    fingerprint=hashlib.sha256(json.dumps({'kind':kind,'data':data},sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    audit_id=str(uuid.uuid5(uuid.NAMESPACE_URL,tenant_id+'/'+key))
    def existing():
        audit=db.query(AuditLogModel).filter_by(id=audit_id,tenant_id=tenant_id).first()
        if not audit:return None
        payload=json.loads(audit.details)
        if payload['fingerprint']!=fingerprint:raise HTTPException(409,'This idempotency key already recorded different details. Use its receipt before starting another record.')
        return db.query(JournalEntryModel).filter_by(id=payload['entry_id'],tenant_id=tenant_id).one()
    previous=existing()
    if previous:return previous
    amount=data.get('amount_paisa',data.get('total_amount_paisa',data.get('principal_paisa')))
    if type(amount) is not int or amount<=0:raise HTTPException(422,'Enter a positive integer-paisa amount.')
    lines=[];party_delta=0;party_kind=None;items=Counter()
    def line(code,direction,value):
        if value:lines.append((code.value if isinstance(code,A) else code,direction,value))
    channel=data.get('channel','cash')
    if channel not in ('cash','bkash','nagad'):raise HTTPException(422,'Choose cash, bKash or Nagad.')
    source=A.CASH.value if channel=='cash' else 'asset:wallet:'+channel
    if kind=='sale':
        sale_type=data['sale_type'];cash=amount if sale_type=='cash' else 0 if sale_type=='credit' else data.get('cash_received_paisa',0)
        if sale_type not in ('cash','credit','split') or type(cash) is not int or not 0<=cash<=amount:raise HTTPException(422,'Sale type or cash received is invalid.')
        due=amount-cash
        line(A.CASH,'debit',cash);line(A.RECEIVABLES,'debit',due);line(A.SALES_REVENUE,'credit',amount)
        if due:party_kind='customer';party_delta=due
        for item in data.get('items') or []:
            if type(item.get('quantity')) is not int or item['quantity']<=0:raise HTTPException(422,'Stock quantity must be a positive integer.')
            items[item['product_id']]+=item['quantity']
    elif kind=='collection':
        line(source,'debit',amount);line(A.RECEIVABLES,'credit',amount);party_kind='customer';party_delta=-amount
    elif kind=='supplier':
        line(A.PAYABLES,'debit',amount);line(source,'credit',amount);party_kind='supplier';party_delta=-amount
    elif kind=='expense':line(A.OPERATING_EXPENSE,'debit',amount);line(A.CASH,'credit',amount)
    elif kind=='withdrawal':
        if data.get('user_role')!='owner':raise HTTPException(403,'Only owners may withdraw capital.')
        line(A.OWNER_DRAW,'debit',amount);line(A.CASH,'credit',amount)
    elif kind=='transfer':
        fee=data.get('fee_paisa',0)
        if type(fee) is not int or fee<0 or data['from_channel'] not in ('bkash','nagad') or data['to_channel']!='cash':raise HTTPException(422,'Use a verified bKash/Nagad-to-cash transfer and non-negative actual fee.')
        line(A.CASH,'debit',amount);line(A.TRANSFER_FEE,'debit',fee);line('asset:wallet:'+data['from_channel'],'credit',amount+fee)
    else:raise HTTPException(422,'Unsupported merchant event.')
    if sum(v for _,d,v in lines if d=='debit')!=sum(v for _,d,v in lines if d=='credit'):raise HTTPException(422,'Unbalanced record rejected.')
    try:
        entry=JournalEntryModel(tenant_id=tenant_id,event_id=key,entry_number=kind[:3].upper()+'-'+uuid.uuid4().hex[:10].upper(),description=(data.get('description') or kind.replace('_',' '))[:255])
        db.add(entry);db.flush()
        accounts={}
        for code in sorted({code for code,_,_ in lines}):
            account=db.query(AccountModel).filter_by(tenant_id=tenant_id,code=code).with_for_update().first()
            if not account:
                account=AccountModel(tenant_id=tenant_id,code=code,type=code.split(':')[0],name=code.split(':')[-1],current_balance_paisa=0);db.add(account);db.flush()
            accounts[code]=account
        if party_kind:
            party=db.query(PartyModel).filter_by(id=data.get('party_id'),tenant_id=tenant_id,party_type=party_kind).with_for_update().first()
            if not party:raise HTTPException(422,'Choose a registered '+party_kind+' in this shop.')
            update=db.query(PartyModel).filter_by(id=party.id,tenant_id=tenant_id)
            if party_delta<0:update=update.filter(PartyModel.current_due_paisa>=-party_delta)
            if update.update({PartyModel.current_due_paisa:PartyModel.current_due_paisa+party_delta},synchronize_session=False)!=1:raise HTTPException(422,'Amount exceeds the verified party due.')
        # Aggregate duplicate stock lines before a single conditional decrement and compute perpetual COGS.
        total_cogs = 0
        product_rows = {}
        for product_id,quantity in sorted(items.items()):
            prod=db.query(ProductItemModel).filter_by(id=product_id,tenant_id=tenant_id).with_for_update().first()
            if not prod or prod.quantity_on_hand<quantity:raise HTTPException(422,'A stock item is missing or has insufficient quantity.')
            product_rows[product_id]=(prod,quantity)
            if prod.cost_price_paisa is not None and prod.cost_price_paisa>0:
                total_cogs+=quantity*prod.cost_price_paisa
        if total_cogs>0:
            line(A.COGS,'debit',total_cogs)
            line(A.INVENTORY,'credit',total_cogs)
            for code in (A.COGS.value,A.INVENTORY.value):
                if code not in accounts:
                    account=db.query(AccountModel).filter_by(tenant_id=tenant_id,code=code).with_for_update().first()
                    if not account:
                        account=AccountModel(tenant_id=tenant_id,code=code,type=code.split(':')[0],name=code.split(':')[-1],current_balance_paisa=0);db.add(account);db.flush()
                    accounts[code]=account
            inv_acc=accounts[A.INVENTORY.value]
            if inv_acc.current_balance_paisa<total_cogs:
                # Synchronize unseeded inventory asset balance when physical stock with cost was directly inserted
                db.query(AccountModel).filter_by(id=inv_acc.id,tenant_id=tenant_id).update({AccountModel.current_balance_paisa:total_cogs},synchronize_session=False)
                inv_acc.current_balance_paisa=total_cogs
        for product_id,(prod,quantity) in product_rows.items():
            changed=db.query(ProductItemModel).filter_by(id=product_id,tenant_id=tenant_id).filter(ProductItemModel.quantity_on_hand>=quantity).update({ProductItemModel.quantity_on_hand:ProductItemModel.quantity_on_hand-quantity},synchronize_session=False)
            if changed!=1:raise HTTPException(422,'A stock item is missing or has insufficient quantity.')
            db.add(StockMovementModel(tenant_id=tenant_id,product_id=product_id,movement_type='sale_deduction',quantity_change=-quantity,reference_id=entry.id))
        for code,direction,value in lines:
            account=accounts[code];normal_debit=account.type in ('asset','expense') or code==A.OWNER_DRAW.value
            delta=value if (direction=='debit')==normal_debit else -value
            update=db.query(AccountModel).filter_by(id=account.id,tenant_id=tenant_id)
            if delta<0:update=update.filter(AccountModel.current_balance_paisa>=-delta)
            if update.update({AccountModel.current_balance_paisa:AccountModel.current_balance_paisa+delta},synchronize_session=False)!=1:raise HTTPException(422,'Insufficient verified account balance; nothing was recorded.')
            db.add(PostingModel(journal_entry_id=entry.id,account_id=account.id,direction=direction,amount_paisa=value))
        db.add(AuditLogModel(id=audit_id,tenant_id=tenant_id,action='merchant_record_posted',details=json.dumps({'entry_id':entry.id,'fingerprint':fingerprint,'kind':kind,'scope':'internal_accounting'},ensure_ascii=False)))
        db.commit();return entry
    except HTTPException:db.rollback();raise
    except IntegrityError:
        db.rollback();previous=existing()
        if previous:return previous
        raise HTTPException(409,'A concurrent record changed. Check balances and retry the same reviewed request.')
