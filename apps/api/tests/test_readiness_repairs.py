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


def test_perpetual_inventory_cogs_on_sale_and_csv_audit_trail(client):
    from app.persistence.models import AccountModel, StockMovementModel
    c, factory, who, headers = judge(client)
    c.headers['Origin'] = 'http://testserver'
    # 1. CSV import with blank SKU deduplicates by name and creates StockMovement + inventory ledger posting
    csv_blank_sku = HEADER + ',Loose Lentils,kg,10,100.00,120.00\n'
    r1 = c.post('/api/v1/reports/import/products.csv', headers=headers, json={'csv_content': csv_blank_sku})
    assert r1.status_code == 200 and r1.json()['created_count'] == 1
    r2 = c.post('/api/v1/reports/import/products.csv', headers=headers, json={'csv_content': HEADER + ',Loose Lentils,kg,15,100.00,120.00\n'})
    assert r2.status_code == 200 and r2.json()['created_count'] == 0 and r2.json()['updated_count'] == 1

    # 2. Sell 1 bag of seeded RICE-025 (cost 119000 paisa, selling 130000 paisa)
    rice = next(p for p in c.get('/api/v1/merchant/products', headers=headers).json() if p['sku'] == 'RICE-025')
    sale = c.post(
        '/api/v1/merchant/sales',
        headers=headers,
        json={
            'sale_type': 'cash',
            'total_amount_paisa': 130000,
            'cash_received_paisa': 130000,
            'items': [{'product_id': rice['id'], 'quantity': 1}],
        },
    )
    assert sale.status_code == 200
    with factory() as db:
        cogs = db.query(AccountModel).filter_by(tenant_id=who['tenant_id'], code='expense:cogs').one()
        inv = db.query(AccountModel).filter_by(tenant_id=who['tenant_id'], code='asset:inventory').one()
        assert cogs.current_balance_paisa == 119000
        # Seeded 476000 + CSV 150000 - Sold 119000 = 507000
        assert inv.current_balance_paisa == 476000 + 150000 - 119000
        movements = db.query(StockMovementModel).filter_by(tenant_id=who['tenant_id'], movement_type='csv_import_adjustment').all()
        assert [m.quantity_change for m in movements] == [10, 5]
