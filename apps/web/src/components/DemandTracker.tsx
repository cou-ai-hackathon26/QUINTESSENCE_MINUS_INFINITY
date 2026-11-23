import { useState } from 'react';
import type { FC, FormEvent } from 'react';
import { useLanguage } from '../i18n/LanguageContext';
import {
  TrendingUp,
  AlertOctagon,
  PlusCircle,
  FileCheck2,
} from 'lucide-react';

export interface UnmetDemandView {
  id: string;
  customer_name?: string | null;
  requested_product: string;
  sku?: string | null;
  quantity: number;
  reason: 'stockout' | 'not_carried' | 'price_too_high' | string;
  notes?: string | null;
  recorded_at?: string;
}

export interface DemandAnalysisView {
  sku: string;
  product_name: string;
  current_stock: number;
  daily_velocity: number;
  stock_cover_days: number;
  total_unmet_demand_count: number;
  recommended_reorder_units: number;
  is_stockout_alert: boolean;
  assumption_disclaimer: string;
}

export interface DemandTrackerProps {
  demands: UnmetDemandView[];
  analysis?: DemandAnalysisView | null;
  onRecordDemand?: (product: string, qty: number, reason: string) => Promise<void>;
}

const BENGALI_DIGITS = ['০', '১', '২', '৩', '৪', '৫', '৬', '৭', '৮', '৯'];
function toBengaliNumber(n: number): string {
  return n.toString().split('').map(d => {
    const idx = parseInt(d, 10);
    return isNaN(idx) ? d : BENGALI_DIGITS[idx];
  }).join('');
}

export const DemandTracker: FC<DemandTrackerProps> = ({
  demands,
  analysis,
  onRecordDemand,
}) => {
  const { language } = useLanguage();
  const isBn = language === 'bn';

  const [productName, setProductName] = useState('');
  const [quantity, setQuantity] = useState(1);
  const [reason, setReason] = useState('stockout');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!productName.trim() || !onRecordDemand) return;
    setSubmitting(true);
    await onRecordDemand(productName.trim(), quantity, reason);
    setProductName('');
    setQuantity(1);
    setSubmitting(false);
  };

  return (
    <div
      className="demand-tracker-container"
      role="region"
      aria-label={isBn ? 'চাহিদা মেমোরি ও ঘাটতি বিশ্লেষণ' : 'Demand Memory & Stockout Impact'}
      style={{
        border: '1px solid #e2e8f0',
        borderRadius: '12px',
        padding: '16px',
        backgroundColor: '#ffffff',
      }}
    >
      {/* Analysis Card if provided */}
      {analysis && (
        <div
          style={{
            border: `1px solid ${analysis.is_stockout_alert ? '#f87171' : '#e2e8f0'}`,
            borderRadius: '10px',
            padding: '14px',
            backgroundColor: analysis.is_stockout_alert ? '#fff1f2' : '#f0fdf4',
            marginBottom: '18px',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h4 style={{ margin: '0 0 4px 0', fontSize: '1rem', color: '#0f172a', display: 'flex', alignItems: 'center', gap: '6px' }}>
                {analysis.is_stockout_alert && <AlertOctagon size={18} color="#dc2626" />}
                <span>{analysis.product_name}</span>
                <span style={{ fontSize: '0.8rem', color: '#64748b' }}>({analysis.sku})</span>
              </h4>
              <p style={{ margin: 0, fontSize: '0.82rem', color: '#475569' }}>
                {isBn ? 'বর্তমান স্টক: ' : 'Stock: '}<strong>{isBn ? toBengaliNumber(analysis.current_stock) : analysis.current_stock}</strong> |{' '}
                {isBn ? 'হারানো ক্রেতার চাহিদা: ' : 'Unmet Demand: '}<strong>{isBn ? toBengaliNumber(analysis.total_unmet_demand_count) : analysis.total_unmet_demand_count}</strong>
              </p>
            </div>

            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '0.75rem', color: '#64748b' }}>{isBn ? 'প্রস্তাবিত রি-অর্ডার' : 'Suggested Reorder'}</div>
              <strong style={{ fontSize: '1.1rem', color: '#0284c7' }}>
                {isBn ? toBengaliNumber(analysis.recommended_reorder_units) : analysis.recommended_reorder_units} টি
              </strong>
            </div>
          </div>

          <div style={{ marginTop: '8px', fontSize: '0.75rem', color: '#64748b', fontStyle: 'italic' }}>
            ℹ️ {analysis.assumption_disclaimer}
          </div>
        </div>
      )}

      {/* Record Unmet Demand Form */}
      {onRecordDemand && (
        <form onSubmit={handleSubmit} style={{ marginBottom: '20px', padding: '12px', border: '1px solid #e2e8f0', borderRadius: '8px', backgroundColor: '#f8fafc' }}>
          <h4 style={{ margin: '0 0 10px 0', fontSize: '0.92rem', color: '#1e293b', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <PlusCircle size={16} color="#0284c7" />
            {isBn ? 'ক্রেতার অবিক্রীত বা অপ্রাপ্ত চাহিদা লিপিবদ্ধ করুন' : 'Log Unmet Customer Request'}
          </h4>

          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            <input
              type="text"
              placeholder={isBn ? 'পণ্যের নাম (যেমন: ডানো দুধ ৫০০ গ্রাম)' : 'Product Name'}
              value={productName}
              onChange={(e) => setProductName(e.target.value)}
              style={{ flex: 2, minWidth: '180px', padding: '8px 10px', borderRadius: '6px', border: '1px solid #cbd5e1', fontSize: '0.85rem' }}
              required
            />
            <input
              type="number"
              min={1}
              value={quantity}
              onChange={(e) => setQuantity(parseInt(e.target.value, 10) || 1)}
              style={{ width: '70px', padding: '8px 10px', borderRadius: '6px', border: '1px solid #cbd5e1', fontSize: '0.85rem' }}
            />
            <select
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              style={{ padding: '8px 10px', borderRadius: '6px', border: '1px solid #cbd5e1', fontSize: '0.85rem' }}
            >
              <option value="stockout">{isBn ? 'স্টক শেষ' : 'Stockout'}</option>
              <option value="not_carried">{isBn ? 'দোকানে রাখা হয় না' : 'Not Carried'}</option>
              <option value="price_too_high">{isBn ? 'দাম বেশি' : 'Price Too High'}</option>
            </select>
            <button
              type="submit"
              disabled={submitting}
              style={{
                padding: '8px 14px',
                borderRadius: '6px',
                border: 'none',
                backgroundColor: '#0284c7',
                color: '#ffffff',
                fontWeight: 600,
                fontSize: '0.85rem',
                cursor: 'pointer',
              }}
            >
              {isBn ? 'লিপিবদ্ধ করুন' : 'Record'}
            </button>
          </div>
        </form>
      )}

      {/* Demand Records List */}
      <div>
        <h4 style={{ margin: '0 0 10px 0', fontSize: '0.95rem', color: '#1e293b', display: 'flex', alignItems: 'center', gap: '6px' }}>
          <TrendingUp size={16} color="#10b981" />
          {isBn ? 'সাম্প্রতিক চাহিদার রেকর্ড' : 'Recent Demand Logs'}
        </h4>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {demands.map((d) => (
            <div
              key={d.id}
              style={{
                padding: '8px 12px',
                borderRadius: '6px',
                backgroundColor: '#f8fafc',
                border: '1px solid #e2e8f0',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                fontSize: '0.85rem',
              }}
            >
              <div>
                <strong>{d.requested_product}</strong>
                {d.customer_name && <span style={{ color: '#64748b', marginLeft: '6px' }}>({d.customer_name})</span>}
                <div style={{ fontSize: '0.78rem', color: '#64748b' }}>
                  {isBn ? 'পরিমাণ: ' : 'Qty: '}{isBn ? toBengaliNumber(d.quantity) : d.quantity} |{' '}
                  {isBn ? 'কারণ: ' : 'Reason: '}{d.reason === 'stockout' ? (isBn ? 'স্টক শেষ' : 'Stockout') : d.reason}
                </div>
              </div>
              <span style={{ fontSize: '0.72rem', color: '#94a3b8', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <FileCheck2 size={12} />
                {isBn ? 'নথিভুক্ত' : 'Logged'}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
