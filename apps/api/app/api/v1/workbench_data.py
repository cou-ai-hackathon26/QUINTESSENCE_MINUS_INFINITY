"""Read-only presentation data derived from tenant-owned journal postings."""
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter,Depends,Query
from sqlalchemy.orm import Session
from app.core.auth import get_current_user
from app.core.database import get_db
from app.persistence.models import AccountModel,JournalEntryModel,PostingModel,UserModel
from app.ingestion.adapters import AIModelAdapter
workbench_router=APIRouter(prefix='/api/v1/workbench',tags=['Workbench data'])
@workbench_router.get('/capabilities')
def capabilities(user:UserModel=Depends(get_current_user)):
    return {'checked_at':datetime.now(timezone.utc).isoformat(),'capabilities':[
        {'id':'inference','title':'Document & voice inference','state':'configured_not_verified' if AIModelAdapter().is_configured() else 'not_configured','detail':'Configured credentials are not a successful inference receipt.'},
        {'id':'agents','title':'Agent workflow','state':'recorded_history','detail':'Synchronous tool workflow. Recorded events and explicit replay; no live parallel streaming claim.'},
        {'id':'retrieval','title':'Shop memory search','state':'lexical_vector_test_boundary','detail':'Keyword plus deterministic lexical-vector retrieval; learned dense embedding quality has not been verified.'},
        {'id':'payments','title':'Online payment execution','state':'unavailable','detail':'Gateway adapter does not perform verified provider session/validation requests.'},
        {'id':'messages','title':'SMS / WhatsApp dispatch','state':'unavailable','detail':'No verified delivery provider or receipt.'},
        {'id':'files','title':'CSV import / export','state':'available','detail':'Selected-file review and tenant-scoped exports.'},
        {'id':'legal','title':'Business document references','state':'reference_only','detail':'Seeded source references are not current jurisdiction-specific legal verification.'}
    ]}
@workbench_router.get('/cashflow')
def cashflow(days:int=Query(7,ge=1,le=31),user:UserModel=Depends(get_current_user),db:Session=Depends(get_db)):
    dhaka=timezone(timedelta(hours=6));today=datetime.now(dhaka).date()
    dates=[today-timedelta(days=days-1-i) for i in range(days)]
    start=datetime.combine(dates[0],datetime.min.time(),dhaka).astimezone(timezone.utc).replace(tzinfo=None)
    end=datetime.combine(today+timedelta(days=1),datetime.min.time(),dhaka).astimezone(timezone.utc).replace(tzinfo=None)
    rows=db.query(JournalEntryModel,PostingModel,AccountModel).select_from(JournalEntryModel).join(PostingModel,PostingModel.journal_entry_id==JournalEntryModel.id).join(AccountModel,AccountModel.id==PostingModel.account_id).filter(JournalEntryModel.tenant_id==user.tenant_id,AccountModel.tenant_id==user.tenant_id,JournalEntryModel.created_at>=start,JournalEntryModel.created_at<end).all()
    entries={}
    for journal,posting,account in rows:
        if account.code!='asset:cash' and not account.code.startswith('asset:wallet:'):continue
        created=journal.created_at.replace(tzinfo=timezone.utc) if journal.created_at.tzinfo is None else journal.created_at
        item=entries.setdefault(journal.id,{'date':created.astimezone(dhaka).date(),'net':0})
        item['net']+=posting.amount_paisa if posting.direction=='debit' else -posting.amount_paisa
    incoming=[sum(v['net'] for v in entries.values() if v['date']==d and v['net']>0) for d in dates]
    outgoing=[-sum(v['net'] for v in entries.values() if v['date']==d and v['net']<0) for d in dates]
    return {'dates':[d.isoformat() for d in dates],'incoming_paisa':incoming,'outgoing_paisa':outgoing,'source_entry_count':len(entries),'as_of':datetime.now(timezone.utc).isoformat(),'definition':'Net cash+wallet movement per journal entry; internal transfers cancel, fees remain outflows; includes opening entries.'}
