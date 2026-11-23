"""Read-only presentation data derived from tenant-owned journal postings."""
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter,Depends,Query
from sqlalchemy.orm import Session
from app.core.auth import get_current_user
from app.core.database import get_db
from app.persistence.models import AccountModel,JournalEntryModel,PostingModel,UserModel
workbench_router=APIRouter(prefix='/api/v1/workbench',tags=['Workbench data'])
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
