"""Owner-reviewed internal accounting. AI never calls this route or transfers external money."""
import hashlib,json,uuid
from typing import Literal
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,Field,StrictInt
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.permissions import require_role
from app.persistence.models import CopilotMessageModel,AccountModel,PartyModel,JournalEntryModel,PostingModel,AuditLogModel,UserModel

proposal_router=APIRouter(prefix='/api/v1/copilot/proposals',tags=['Reviewed proposals'])
SUPPORTED={'cash_sale','credit_sale','debt_collection','expense','supplier_payment'}

def source(db,user,message_id,index):
    message=db.query(CopilotMessageModel).filter_by(id=message_id,tenant_id=user.tenant_id,role='assistant').first()
    if not message:raise HTTPException(404,'Proposal source not found.')
    metadata=json.loads(message.audio_metadata_json or '{}')
    operations=metadata.get('proposed_operations',metadata.get('compound_operations',[]))
    if index<0 or index>=len(operations):raise HTTPException(404,'Proposed operation not found.')
    fingerprint=hashlib.sha256((message.content+'\n'+json.dumps(operations[index],sort_keys=True,ensure_ascii=False)).encode()).hexdigest()
    return message,operations[index],fingerprint,metadata

def event_key(message_id,index):return 'copilot:'+message_id+':'+str(index)

@proposal_router.get('/{message_id}/{index}')
def inspect_proposal(message_id:str,index:int,current_user:UserModel=Depends(get_current_user),db:Session=Depends(get_db)):
    message,operation,fingerprint,metadata=source(db,current_user,message_id,index)
    entry=db.query(JournalEntryModel).filter_by(tenant_id=current_user.tenant_id,event_id=event_key(message_id,index)).first()
    return {'message_id':message.id,'operation_index':index,'operation':operation,'source_hash':fingerprint,'evidence_id':metadata.get('evidence_id'),'source_citations':json.loads(message.citations_json or '[]'),'can_record':operation.get('type') in SUPPORTED,'recorded_entry_id':entry.id if entry else None,'recording_scope':'Internal accounting only. No external transfer or customer message. Inventory and item cost are not inferred.'}

class ReviewDTO(BaseModel):
    confirmed:Literal[True]
    source_hash:str=Field(min_length=64,max_length=64)
    amount_paisa:StrictInt=Field(gt=0,le=99999999999)
    party_id:str|None=None
    channel:Literal['cash','bkash','nagad']='cash'
    expected_party_due_paisa:StrictInt|None=None
    expected_account_balance_paisa:StrictInt|None=None

@proposal_router.post('/{message_id}/{index}/record')
def record_reviewed_proposal(message_id:str,index:int,req:ReviewDTO,current_user:UserModel=Depends(require_role(['owner','manager'])),db:Session=Depends(get_db)):
    message,op,fingerprint,metadata=source(db,current_user,message_id,index)
    if req.source_hash!=fingerprint:raise HTTPException(409,'The proposal changed. Reopen it before confirming.')
    kind=op.get('type')
    if kind not in SUPPORTED:raise HTTPException(422,'This interpretation needs a dedicated workflow or clarification before recording.')
    key=event_key(message_id,index);audit_id=str(uuid.uuid5(uuid.NAMESPACE_URL,current_user.tenant_id+'/'+key))
    business={'type':kind,'party_id':req.party_id,'amount_paisa':req.amount_paisa,'channel':req.channel,'source_hash':fingerprint}
    request_hash=hashlib.sha256(json.dumps(business,sort_keys=True).encode()).hexdigest()
    def existing():
        audit=db.query(AuditLogModel).filter_by(id=audit_id,tenant_id=current_user.tenant_id).first()
        if audit:
            recorded=json.loads(audit.details)
            if recorded['request_hash']!=request_hash:raise HTTPException(409,'This source operation was already recorded with different details. Review its receipt; do not post it again.')
            return {'status':'already_recorded','entry_id':recorded['entry_id'],'idempotent_replay':True}
    replay=existing()
    if replay:return replay
    amount=req.amount_paisa;channel_code='asset:cash' if req.channel=='cash' else 'asset:wallet:'+req.channel
    pair={'cash_sale':[(channel_code,'debit'),('revenue:sales','credit')],'credit_sale':[('asset:accounts_receivable','debit'),('revenue:sales','credit')],'debt_collection':[(channel_code,'debit'),('asset:accounts_receivable','credit')],'expense':[('expense:operating','debit'),(channel_code,'credit')],'supplier_payment':[('liability:accounts_payable','debit'),(channel_code,'credit')]}[kind]
    # Canonical codes come from the same source of truth as all existing merchant pages.
    from app.domain.ledger import StandardAccount
    remap={'revenue:sales':StandardAccount.SALES_REVENUE.value,'asset:accounts_receivable':StandardAccount.RECEIVABLES.value,'expense:operating':StandardAccount.OPERATING_EXPENSE.value,'liability:accounts_payable':StandardAccount.PAYABLES.value}
    pair=[(remap.get(code,code),direction) for code,direction in pair]
    try:
        # Unique event flush serializes duplicate requests before balance mutations.
        entry=JournalEntryModel(tenant_id=current_user.tenant_id,event_id=key,entry_number='REV-'+uuid.uuid4().hex[:10].upper(),description='Owner reviewed '+kind.replace('_',' '))
        db.add(entry);db.flush()
        accounts={}
        for code in sorted({code for code,_ in pair}):
            account=db.query(AccountModel).filter_by(tenant_id=current_user.tenant_id,code=code).with_for_update().first()
            if not account:
                account=AccountModel(tenant_id=current_user.tenant_id,code=code,name=code.split(':')[-1],type=code.split(':')[0],current_balance_paisa=0)
                db.add(account);db.flush()
            accounts[code]=account
        party=None
        if kind in ('credit_sale','debt_collection','supplier_payment'):
            party=db.query(PartyModel).filter_by(id=req.party_id,tenant_id=current_user.tenant_id,party_type='supplier' if kind=='supplier_payment' else 'customer').with_for_update().first()
            if not party:raise HTTPException(422,'Choose the matching registered customer or supplier.')
            if req.expected_party_due_paisa is None or req.expected_party_due_paisa!=party.current_due_paisa:raise HTTPException(409,'Party due changed. Reopen the review.')
            delta=amount if kind=='credit_sale' else -amount
            if party.current_due_paisa+delta<0:raise HTTPException(422,'This amount exceeds the verified outstanding due.')
            changed=db.query(PartyModel).filter_by(id=party.id,tenant_id=current_user.tenant_id,current_due_paisa=req.expected_party_due_paisa).update({PartyModel.current_due_paisa:PartyModel.current_due_paisa+delta},synchronize_session=False)
            if changed!=1:raise HTTPException(409,'Party due changed concurrently. Reopen the review.')
        elif req.party_id:raise HTTPException(422,'This operation does not update a party due. Clear the party selection.')
        if kind in ('expense','supplier_payment') and req.expected_account_balance_paisa!=accounts[channel_code].current_balance_paisa:raise HTTPException(409,'The source balance changed. Reopen the review.')
        for code,direction in pair:
            account=accounts[code]
            normal_debit=account.type in ('asset','expense')
            delta=amount if (direction=='debit')==normal_debit else -amount
            condition=db.query(AccountModel).filter_by(id=account.id,tenant_id=current_user.tenant_id)
            if delta<0:condition=condition.filter(AccountModel.current_balance_paisa>=-delta)
            if condition.update({AccountModel.current_balance_paisa:AccountModel.current_balance_paisa+delta},synchronize_session=False)!=1:raise HTTPException(422,'Insufficient verified balance; no transaction was recorded.')
            db.add(PostingModel(journal_entry_id=entry.id,account_id=account.id,direction=direction,amount_paisa=amount))
        db.add(AuditLogModel(id=audit_id,tenant_id=current_user.tenant_id,user_id=current_user.id,action='reviewed_proposal_posted',details=json.dumps({'entry_id':entry.id,'message_id':message.id,'operation_index':index,'request_hash':request_hash,'approved':business,'original_proposal':op,'scope':'internal_accounting_no_external_execution'},ensure_ascii=False)))
        db.commit();return {'status':'recorded','entry_id':entry.id,'entry_number':entry.entry_number,'idempotent_replay':False}
    except HTTPException:db.rollback();raise
    except IntegrityError:
        db.rollback();replay=existing()
        if replay:return replay
        raise HTTPException(409,'A concurrent record changed. Reopen and inspect the receipt before retrying.')
