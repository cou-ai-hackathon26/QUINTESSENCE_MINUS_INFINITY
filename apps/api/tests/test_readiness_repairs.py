"""Regression contracts from the readiness review; isolated synthetic accounts."""
import pytest
from test_workbench_auth import client
from app.persistence.models import ProductItemModel

HEADER = 'sku,name,unit,quantity_on_hand,cost_price_bdt,selling_price_bdt\n'


def judge(client):
    c, factory = client
    who = c.post('/api/v1/auth/judge-session', json={}).json()
    return c, factory, who, {'Authorization': 'Bearer ' + who['access_token']}


def test_exact_csv_money_keeps_existing_create_and_update_workflows(client):
    c, factory, who, headers = judge(client)
    for qty, expected_created in [(5, 1), (8, 0)]:
        r = c.post('/api/v1/reports/import/products.csv', headers=headers,
                   json={'csv_content': HEADER + f'PRECISION,Synthetic product,pcs,{qty},0.29,১.০৯\n'})
        assert r.status_code == 200
        assert r.json()['created_count'] == expected_created
        with factory() as db:
            item = db.query(ProductItemModel).filter_by(tenant_id=who['tenant_id'], sku='PRECISION').one()
            assert (item.quantity_on_hand, item.cost_price_paisa, item.selling_price_paisa) == (qty, 29, 109)


@pytest.mark.parametrize('bad_row', [
    'INVALID,Bad,pcs,-5,1.00,1.00', 'INVALID,Bad,pcs,5,0.001,1.00',
    'INVALID,Bad,pcs,5,NaN,1.00', 'INVALID,Bad,pcs,5,1.00,Infinity',
    'GOOD,Duplicate,pcs,5,1.00,1.00',
])
def test_invalid_csv_is_atomic_and_does_not_change_stock(client, bad_row):
    c, factory, who, headers = judge(client)
    r = c.post('/api/v1/reports/import/products.csv', headers=headers,
               json={'csv_content': HEADER + 'GOOD,Valid,pcs,5,0.29,1.00\n' + bad_row + '\n'})
    assert r.status_code == 422
    with factory() as db:
        assert db.query(ProductItemModel).filter(ProductItemModel.tenant_id == who['tenant_id'], ProductItemModel.sku.in_(['GOOD', 'INVALID'])).count() == 0


def test_csv_text_cannot_be_exported_as_formula(client):
    c, _, _, headers = judge(client)
    r = c.post('/api/v1/reports/import/products.csv', headers=headers,
               json={'csv_content': HEADER + 'SAFE,=1+1,pcs,1,0.29,1.00\n'})
    assert r.status_code == 200
    r = c.get('/api/v1/reports/export/products.csv', headers=headers)
    assert ",=1+1," not in r.text
    assert ",'=1+1," in r.text
