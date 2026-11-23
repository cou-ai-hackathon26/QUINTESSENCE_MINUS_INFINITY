from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base,get_db
from app.domain.merchant_posting import record
from app.persistence.models import JournalEntryModel,PostingModel

def test_two_independent_outflows_cannot_spend_same_cash(tmp_path):
    engine=create_engine('sqlite:///'+str(tmp_path/'outflow-race.db'),connect_args={'check_same_thread':False})
    Base.metadata.create_all(engine);factory=sessionmaker(bind=engine)
    def database():
        with factory() as db:yield db
    app.dependency_overrides[get_db]=database
    try:
        with TestClient(app) as c:
            tenant=c.post('/api/v1/auth/judge-session',json={}).json()['tenant_id'];barrier=Barrier(2)
            def spend(index):
                with factory() as db:
                    barrier.wait()
                    try:return record(db,tenant,'expense',{'amount_paisa':400000,'description':'Concurrent synthetic expense'},'race-'+str(index)).id
                    except HTTPException as error:return error.status_code
            with ThreadPoolExecutor(max_workers=2) as pool:outcomes=list(pool.map(spend,range(2)))
            assert sum(isinstance(outcome,str) for outcome in outcomes)==1 and outcomes.count(422)==1
            assert c.get('/api/v1/merchant/today').json()['cash_balance_paisa']==100000
            with factory() as db:
                entries=db.query(JournalEntryModel).filter_by(tenant_id=tenant).all()
                for entry in entries:
                    lines=db.query(PostingModel).filter_by(journal_entry_id=entry.id).all()
                    assert sum(p.amount_paisa for p in lines if p.direction=='debit')==sum(p.amount_paisa for p in lines if p.direction=='credit')
    finally:app.dependency_overrides.clear();engine.dispose()
