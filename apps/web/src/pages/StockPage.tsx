import { useState, useEffect } from 'react';
import type { FC } from 'react';
import { Navbar } from '../components/Navbar';
import { Sidebar } from '../components/Sidebar';
import { useLanguage } from '../i18n/LanguageContext';
import { Boxes, AlertTriangle, Plus, ShoppingCart, RotateCcw, CheckCircle2 } from 'lucide-react';

interface ProductItem {
  id: string;
  name: string;
  sku: string | null;
  unit: string;
  quantity_on_hand: number;
  cost_price_paisa: number | null;
  selling_price_paisa: number;
  reorder_threshold: number;
  lead_time_days: number;
  margin_paisa: number | null;
  margin_percent: number | null;
  daily_sales_velocity: number;
  stock_cover_days: number;
  reorder_status: 'normal' | 'reorder_urgent' | 'out_of_stock';
}

interface ReorderRecommendation {
  product_id: string;
  name: string;
  sku: string | null;
  quantity_on_hand: number;
  reorder_threshold: number;
  lead_time_days: number;
  suggested_order_qty: number;
  estimated_unit_cost_paisa: number;
  estimated_total_cost_paisa: number;
  urgency: 'critical' | 'warning';
}

export const StockPage: FC = () => {
  const { t, formatCurrency } = useLanguage();
  const [products, setProducts] = useState<ProductItem[]>([]);
  const [recommendations, setRecommendations] = useState<ReorderRecommendation[]>([]);
  const [cashWarning, setCashWarning] = useState<string | null>(null);
  const [cashSufficient, setCashSufficient] = useState<boolean>(true);
  const [spendableCashPaisa, setSpendableCashPaisa] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);
  const [activeModal, setActiveModal] = useState<'product' | 'purchase' | 'return' | null>(null);

  // Form states
  const [newProdName, setNewProdName] = useState('');
  const [newProdSku, setNewProdSku] = useState('');
  const [newProdUnit, setNewProdUnit] = useState('pcs');
  const [newProdQty, setNewProdQty] = useState('10');
  const [newProdCost, setNewProdCost] = useState('100');
  const [newProdPrice, setNewProdPrice] = useState('150');

  const [purchaseProdId, setPurchaseProdId] = useState('');
  const [purchaseQty, setPurchaseQty] = useState('20');
  const [purchaseCost, setPurchaseCost] = useState('100');

  const [returnType, setReturnType] = useState<'customer_return' | 'supplier_return'>('customer_return');
  const [returnProdId, setReturnProdId] = useState('');
  const [returnQty, setReturnQty] = useState('1');

  const token = localStorage.getItem('shongoti_token');

  const fetchStockData = async () => {
    try {
      const headers: Record<string, string> = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;

      const [prodsRes, reorderRes] = await Promise.all([
        fetch('/api/v1/stock/products', { headers }),
        fetch('/api/v1/stock/reorder-recommendations', { headers }),
      ]);

      if (prodsRes.ok) {
        const data = await prodsRes.json();
        setProducts(data.products || []);
        if (data.products?.length > 0 && !purchaseProdId) {
          setPurchaseProdId(data.products[0].id);
          setReturnProdId(data.products[0].id);
        }
      }

      if (reorderRes.ok) {
        const reorderData = await reorderRes.json();
        setRecommendations(reorderData.recommendations || []);
        setCashWarning(reorderData.cash_warning || null);
        setCashSufficient(reorderData.cash_sufficient);
        setSpendableCashPaisa(reorderData.spendable_cash_paisa || 0);
      }
    } catch {
      // Fallback sample data for offline demo preview
      const sampleProds: ProductItem[] = [
        {
          id: 'p1',
          name: 'মিনিকেট চাল (Miniket Rice 25kg)',
          sku: 'RICE-MIN-25',
          unit: 'sack',
          quantity_on_hand: 4,
          cost_price_paisa: 165000,
          selling_price_paisa: 185000,
          reorder_threshold: 5,
          lead_time_days: 2,
          margin_paisa: 20000,
          margin_percent: 10.81,
          daily_sales_velocity: 1.5,
          stock_cover_days: 2.7,
          reorder_status: 'reorder_urgent',
        },
        {
          id: 'p2',
          name: 'তীর সয়াবিন তেল ৫ লিটার (Teer Oil 5L)',
          sku: 'OIL-TEER-5L',
          unit: 'bottle',
          quantity_on_hand: 12,
          cost_price_paisa: 78000,
          selling_price_paisa: 85000,
          reorder_threshold: 4,
          lead_time_days: 3,
          margin_paisa: 7000,
          margin_percent: 8.24,
          daily_sales_velocity: 0.8,
          stock_cover_days: 15.0,
          reorder_status: 'normal',
        },
        {
          id: 'p3',
          name: 'দেশি ডিম (Local Egg 100pcs)',
          sku: 'EGG-LOC-100',
          unit: 'tray',
          quantity_on_hand: 1,
          cost_price_paisa: null,
          selling_price_paisa: 125000,
          reorder_threshold: 3,
          lead_time_days: 1,
          margin_paisa: null,
          margin_percent: null,
          daily_sales_velocity: 0.5,
          stock_cover_days: 2.0,
          reorder_status: 'reorder_urgent',
        },
      ];
      setProducts(sampleProds);
      setRecommendations([
        {
          product_id: 'p1',
          name: 'মিনিকেট চাল (Miniket Rice 25kg)',
          sku: 'RICE-MIN-25',
          quantity_on_hand: 4,
          reorder_threshold: 5,
          lead_time_days: 2,
          suggested_order_qty: 6,
          estimated_unit_cost_paisa: 165000,
          estimated_total_cost_paisa: 990000,
          urgency: 'warning',
        },
      ]);
      setCashWarning('Available spendable cash (৳500) is insufficient to fund all recommended reorders (৳9,900). Shortfall: ৳9,400.');
      setCashSufficient(false);
      setSpendableCashPaisa(50000);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStockData();
  }, []);

  const handleCreateProduct = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const headers: Record<string, string> = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;

      await fetch('/api/v1/stock/products', {
        method: 'POST',
        headers,
        body: JSON.stringify({
          name: newProdName,
          sku: newProdSku || null,
          unit: newProdUnit,
          quantity_on_hand: parseInt(newProdQty) || 0,
          cost_price_paisa: newProdCost ? Math.round(parseFloat(newProdCost) * 100) : null,
          selling_price_paisa: Math.round(parseFloat(newProdPrice) * 100) || 0,
          reorder_threshold: 5,
          lead_time_days: 3,
        }),
      });
      setActiveModal(null);
      fetchStockData();
    } catch {
      setActiveModal(null);
    }
  };

  const handlePurchaseAndReceive = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const headers: Record<string, string> = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;

      const draftRes = await fetch('/api/v1/stock/purchase-drafts', {
        method: 'POST',
        headers,
        body: JSON.stringify({
          product_id: purchaseProdId,
          quantity: parseInt(purchaseQty) || 1,
          unit_cost_paisa: Math.round(parseFloat(purchaseCost) * 100),
          lead_time_days: 3,
        }),
      });

      if (draftRes.ok) {
        const draftData = await draftRes.json();
        // Immediately receive goods and update WAC
        await fetch(`/api/v1/stock/purchase-drafts/${draftData.draft_id}/receive`, {
          method: 'POST',
          headers,
        });
      }
      setActiveModal(null);
      fetchStockData();
    } catch {
      setActiveModal(null);
    }
  };

  const handleProcessReturn = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const headers: Record<string, string> = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;

      await fetch('/api/v1/stock/returns', {
        method: 'POST',
        headers,
        body: JSON.stringify({
          return_type: returnType,
          product_id: returnProdId,
          quantity: parseInt(returnQty) || 1,
        }),
      });
      setActiveModal(null);
      fetchStockData();
    } catch {
      setActiveModal(null);
    }
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f8fafc', color: '#0f172a' }}>
      <Navbar />
      <div style={{ display: 'flex' }}>
        <Sidebar />
        <main style={{ flex: 1, padding: '2rem', maxWidth: '1200px' }}>
          {/* Header */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
            <div>
              <h1 style={{ fontSize: '1.5rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Boxes color="#0284c7" size={24} />
                {t('stock.title')}
              </h1>
              <p style={{ color: '#64748b', fontSize: '0.875rem', marginTop: '0.25rem' }}>
                {t('stock.subtitle')}
              </p>
            </div>
            <div style={{ display: 'flex', gap: '0.75rem' }}>
              <button
                onClick={() => setActiveModal('product')}
                style={{
                  display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.5rem 1rem',
                  backgroundColor: '#0284c7', color: '#fff', border: 'none', borderRadius: '0.375rem',
                  fontWeight: 600, fontSize: '0.875rem', cursor: 'pointer'
                }}
              >
                <Plus size={16} />
                {t('stock.add_product')}
              </button>
              <button
                onClick={() => setActiveModal('purchase')}
                style={{
                  display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.5rem 1rem',
                  backgroundColor: '#059669', color: '#fff', border: 'none', borderRadius: '0.375rem',
                  fontWeight: 600, fontSize: '0.875rem', cursor: 'pointer'
                }}
              >
                <ShoppingCart size={16} />
                {t('stock.new_purchase')}
              </button>
              <button
                onClick={() => setActiveModal('return')}
                style={{
                  display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.5rem 1rem',
                  backgroundColor: '#64748b', color: '#fff', border: 'none', borderRadius: '0.375rem',
                  fontWeight: 600, fontSize: '0.875rem', cursor: 'pointer'
                }}
              >
                <RotateCcw size={16} />
                {t('stock.returns')}
              </button>
            </div>
          </div>

          {/* Reorder & Cash Awareness Warning Banner */}
          {recommendations.length > 0 && (
            <div style={{
              backgroundColor: cashSufficient ? '#f0fdf4' : '#fffbeb',
              border: `1px solid ${cashSufficient ? '#bbf7d0' : '#fef08a'}`,
              borderRadius: '0.5rem',
              padding: '1rem 1.25rem',
              marginBottom: '1.5rem',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 700, color: cashSufficient ? '#166534' : '#854d0e' }}>
                  {cashSufficient ? <CheckCircle2 size={18} /> : <AlertTriangle size={18} />}
                  <span>{t('stock.reorder_alert_title')} ({recommendations.length})</span>
                </div>
                <div style={{ fontSize: '0.8125rem', color: '#64748b' }}>
                  বর্তমান তরল নগদ: <strong>{formatCurrency(spendableCashPaisa)}</strong>
                </div>
              </div>
              {!cashSufficient && cashWarning && (
                <p style={{ fontSize: '0.875rem', color: '#b45309', fontWeight: 600, margin: '0 0 0.75rem 0' }}>
                  {cashWarning}
                </p>
              )}
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem' }}>
                {recommendations.map((rec) => (
                  <div key={rec.product_id} style={{
                    backgroundColor: '#ffffff',
                    border: '1px solid #e2e8f0',
                    borderRadius: '0.375rem',
                    padding: '0.5rem 0.75rem',
                    fontSize: '0.8125rem'
                  }}>
                    <span style={{ fontWeight: 600 }}>{rec.name}</span>: {rec.quantity_on_hand} অবশিষ্ট | পুনর্ক্রয় সুপারিশ: <strong>+{rec.suggested_order_qty}</strong> (আনুমানিক ৳{(rec.estimated_total_cost_paisa / 100).toLocaleString()})
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Product Catalog & Inventory Table */}
          <div style={{ backgroundColor: '#ffffff', borderRadius: '0.5rem', border: '1px solid #e2e8f0', overflow: 'hidden' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
              <thead>
                <tr style={{ backgroundColor: '#f8fafc', borderBottom: '1px solid #e2e8f0', color: '#64748b' }}>
                  <th style={{ padding: '0.75rem 1rem' }}>{t('stock.col_product')}</th>
                  <th style={{ padding: '0.75rem 1rem' }}>{t('stock.col_qty')}</th>
                  <th style={{ padding: '0.75rem 1rem' }}>{t('stock.col_cost')}</th>
                  <th style={{ padding: '0.75rem 1rem' }}>{t('stock.col_price')}</th>
                  <th style={{ padding: '0.75rem 1rem' }}>{t('stock.col_margin')}</th>
                  <th style={{ padding: '0.75rem 1rem' }}>{t('stock.col_velocity')}</th>
                  <th style={{ padding: '0.75rem 1rem' }}>{t('stock.col_cover')}</th>
                  <th style={{ padding: '0.75rem 1rem' }}>{t('stock.col_status')}</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr><td colSpan={8} style={{ padding: '2rem', textAlign: 'center', color: '#94a3b8' }}>তথ্য লোড হচ্ছে...</td></tr>
                ) : products.length === 0 ? (
                  <tr><td colSpan={8} style={{ padding: '2rem', textAlign: 'center', color: '#94a3b8' }}>কোনো পণ্য তালিকাভুক্ত নেই।</td></tr>
                ) : (
                  products.map((p) => {
                    const statusColor = p.reorder_status === 'normal' ? '#166534' : p.reorder_status === 'reorder_urgent' ? '#b45309' : '#991b1b';
                    const statusBg = p.reorder_status === 'normal' ? '#dcfce7' : p.reorder_status === 'reorder_urgent' ? '#fef3c7' : '#fee2e2';
                    const statusLabel = p.reorder_status === 'normal' ? t('stock.status_normal') : p.reorder_status === 'reorder_urgent' ? t('stock.status_urgent') : t('stock.status_out');

                    return (
                      <tr key={p.id} style={{ borderBottom: '1px solid #f1f5f9' }}>
                        <td style={{ padding: '0.75rem 1rem' }}>
                          <div style={{ fontWeight: 600 }}>{p.name}</div>
                          {p.sku && <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>SKU: {p.sku}</div>}
                        </td>
                        <td style={{ padding: '0.75rem 1rem' }}>
                          <strong style={{ fontSize: '0.9375rem' }}>{p.quantity_on_hand}</strong> {p.unit}
                        </td>
                        <td style={{ padding: '0.75rem 1rem' }}>
                          {p.cost_price_paisa !== null ? (
                            formatCurrency(p.cost_price_paisa)
                          ) : (
                            <span style={{ fontSize: '0.75rem', backgroundColor: '#fee2e2', color: '#991b1b', padding: '0.125rem 0.375rem', borderRadius: '0.25rem', fontWeight: 600 }}>
                              {t('stock.uncosted')}
                            </span>
                          )}
                        </td>
                        <td style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>
                          {formatCurrency(p.selling_price_paisa)}
                        </td>
                        <td style={{ padding: '0.75rem 1rem' }}>
                          {p.margin_percent !== null ? (
                            <span style={{ color: p.margin_percent >= 15 ? '#166534' : '#b45309', fontWeight: 600 }}>
                              {p.margin_percent}%
                            </span>
                          ) : (
                            <span style={{ color: '#94a3b8', fontStyle: 'italic', fontSize: '0.75rem' }}>গোপন (D011)</span>
                          )}
                        </td>
                        <td style={{ padding: '0.75rem 1rem', color: '#475569' }}>
                          {p.daily_sales_velocity} {p.unit}/দিন
                        </td>
                        <td style={{ padding: '0.75rem 1rem', color: p.stock_cover_days <= p.lead_time_days ? '#dc2626' : '#475569', fontWeight: p.stock_cover_days <= p.lead_time_days ? 700 : 400 }}>
                          {p.stock_cover_days < 900 ? `${p.stock_cover_days} দিন` : '—'}
                        </td>
                        <td style={{ padding: '0.75rem 1rem' }}>
                          <span style={{
                            backgroundColor: statusBg,
                            color: statusColor,
                            padding: '0.25rem 0.5rem',
                            borderRadius: '0.25rem',
                            fontSize: '0.75rem',
                            fontWeight: 600,
                          }}>
                            {statusLabel}
                          </span>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>

          {/* Modal: Add Product */}
          {activeModal === 'product' && (
            <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 50 }}>
              <form onSubmit={handleCreateProduct} style={{ backgroundColor: '#fff', padding: '1.5rem', borderRadius: '0.5rem', width: '420px', display: 'flex', flexDirection: 'column', gap: '0.875rem' }}>
                <h3 style={{ margin: 0, fontWeight: 700, fontSize: '1.125rem' }}>{t('stock.add_product')}</h3>
                <input required placeholder="পণ্যের নাম (যেমন: মিনিকেট চাল)" value={newProdName} onChange={e => setNewProdName(e.target.value)} style={{ padding: '0.5rem', border: '1px solid #cbd5e1', borderRadius: '0.25rem' }} />
                <input placeholder="SKU কোড (ঐচ্ছিক)" value={newProdSku} onChange={e => setNewProdSku(e.target.value)} style={{ padding: '0.5rem', border: '1px solid #cbd5e1', borderRadius: '0.25rem' }} />
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <input placeholder="একক (pcs/kg/sack)" value={newProdUnit} onChange={e => setNewProdUnit(e.target.value)} style={{ flex: 1, padding: '0.5rem', border: '1px solid #cbd5e1', borderRadius: '0.25rem' }} />
                  <input type="number" placeholder="প্রারম্ভিক মজুদ" value={newProdQty} onChange={e => setNewProdQty(e.target.value)} style={{ flex: 1, padding: '0.5rem', border: '1px solid #cbd5e1', borderRadius: '0.25rem' }} />
                </div>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <input type="number" placeholder="ক্রয়মূল্য ৳" value={newProdCost} onChange={e => setNewProdCost(e.target.value)} style={{ flex: 1, padding: '0.5rem', border: '1px solid #cbd5e1', borderRadius: '0.25rem' }} />
                  <input type="number" placeholder="বিক্রয়মূল্য ৳" value={newProdPrice} onChange={e => setNewProdPrice(e.target.value)} style={{ flex: 1, padding: '0.5rem', border: '1px solid #cbd5e1', borderRadius: '0.25rem' }} />
                </div>
                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem', marginTop: '0.5rem' }}>
                  <button type="button" onClick={() => setActiveModal(null)} style={{ padding: '0.5rem 1rem', border: '1px solid #cbd5e1', backgroundColor: '#fff', borderRadius: '0.25rem', cursor: 'pointer' }}>বাতিল</button>
                  <button type="submit" style={{ padding: '0.5rem 1rem', backgroundColor: '#0284c7', color: '#fff', border: 'none', borderRadius: '0.25rem', cursor: 'pointer', fontWeight: 600 }}>যোগ করুন</button>
                </div>
              </form>
            </div>
          )}

          {/* Modal: Purchase Draft & Receive */}
          {activeModal === 'purchase' && (
            <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 50 }}>
              <form onSubmit={handlePurchaseAndReceive} style={{ backgroundColor: '#fff', padding: '1.5rem', borderRadius: '0.5rem', width: '420px', display: 'flex', flexDirection: 'column', gap: '0.875rem' }}>
                <h3 style={{ margin: 0, fontWeight: 700, fontSize: '1.125rem' }}>{t('stock.new_purchase')} ও মালপত্র গ্রহণ</h3>
                <label style={{ fontSize: '0.8125rem', color: '#475569' }}>পণ্য নির্বাচন করুন:</label>
                <select value={purchaseProdId} onChange={e => setPurchaseProdId(e.target.value)} style={{ padding: '0.5rem', border: '1px solid #cbd5e1', borderRadius: '0.25rem' }}>
                  {products.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
                </select>
                <input type="number" placeholder="ক্রয়কৃত পরিমাণ" value={purchaseQty} onChange={e => setPurchaseQty(e.target.value)} style={{ padding: '0.5rem', border: '1px solid #cbd5e1', borderRadius: '0.25rem' }} />
                <input type="number" placeholder="একক ক্রয়মূল্য ৳" value={purchaseCost} onChange={e => setPurchaseCost(e.target.value)} style={{ padding: '0.5rem', border: '1px solid #cbd5e1', borderRadius: '0.25rem' }} />
                <p style={{ fontSize: '0.75rem', color: '#64748b', margin: 0 }}>মালপত্র প্রাপ্তির সাথে সাথে D011 নীতি অনুযায়ী গড় ক্রয়মূল্য (WAC) স্বয়ংক্রিয়ভাবে পুনঃহিসাব হবে।</p>
                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem', marginTop: '0.5rem' }}>
                  <button type="button" onClick={() => setActiveModal(null)} style={{ padding: '0.5rem 1rem', border: '1px solid #cbd5e1', backgroundColor: '#fff', borderRadius: '0.25rem', cursor: 'pointer' }}>বাতিল</button>
                  <button type="submit" style={{ padding: '0.5rem 1rem', backgroundColor: '#059669', color: '#fff', border: 'none', borderRadius: '0.25rem', cursor: 'pointer', fontWeight: 600 }}>গ্রহণ নিশ্চিত করুন</button>
                </div>
              </form>
            </div>
          )}

          {/* Modal: Process Return */}
          {activeModal === 'return' && (
            <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 50 }}>
              <form onSubmit={handleProcessReturn} style={{ backgroundColor: '#fff', padding: '1.5rem', borderRadius: '0.5rem', width: '420px', display: 'flex', flexDirection: 'column', gap: '0.875rem' }}>
                <h3 style={{ margin: 0, fontWeight: 700, fontSize: '1.125rem' }}>{t('stock.returns')}</h3>
                <div style={{ display: 'flex', gap: '1rem' }}>
                  <label style={{ fontSize: '0.875rem' }}>
                    <input type="radio" checked={returnType === 'customer_return'} onChange={() => setReturnType('customer_return')} /> কাস্টমার ফেরত
                  </label>
                  <label style={{ fontSize: '0.875rem' }}>
                    <input type="radio" checked={returnType === 'supplier_return'} onChange={() => setReturnType('supplier_return')} /> মহাজনকে ফেরত
                  </label>
                </div>
                <select value={returnProdId} onChange={e => setReturnProdId(e.target.value)} style={{ padding: '0.5rem', border: '1px solid #cbd5e1', borderRadius: '0.25rem' }}>
                  {products.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
                </select>
                <input type="number" placeholder="ফেরত পরিমাণ" value={returnQty} onChange={e => setReturnQty(e.target.value)} style={{ padding: '0.5rem', border: '1px solid #cbd5e1', borderRadius: '0.25rem' }} />
                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem', marginTop: '0.5rem' }}>
                  <button type="button" onClick={() => setActiveModal(null)} style={{ padding: '0.5rem 1rem', border: '1px solid #cbd5e1', backgroundColor: '#fff', borderRadius: '0.25rem', cursor: 'pointer' }}>বাতিল</button>
                  <button type="submit" style={{ padding: '0.5rem 1rem', backgroundColor: '#64748b', color: '#fff', border: 'none', borderRadius: '0.25rem', cursor: 'pointer', fontWeight: 600 }}>ফেরত সম্পন্ন করুন</button>
                </div>
              </form>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default StockPage;
