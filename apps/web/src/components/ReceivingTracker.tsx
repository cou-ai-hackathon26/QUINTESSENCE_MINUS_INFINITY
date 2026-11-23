import { useState } from 'react';
import type { FC } from 'react';
import { useLanguage } from '../i18n/LanguageContext';
import {
  PackageCheck,
  ArrowRight,
  ShieldCheck,
} from 'lucide-react';

export interface GoodsReceiptView {
  id: string;
  supplier_name: string;
  sku: string;
  ordered_quantity: number;
  received_quantity: number;
  damaged_quantity: number;
  shortage_quantity: number;
  status: 'complete' | 'partial' | 'discrepant' | string;
  created_at?: string;
}

export interface CreditNoteView {
  id: string;
  supplier_name: string;
  claim_reason: string;
  amount_bdt: number;
  status: 'suspected' | 'reviewed' | 'accepted_by_supplier' | 'applied_to_bill' | 'rejected' | string;
  applied_invoice_ref?: string | null;
  return_window_deadline?: string | null;
}

export interface ReceivingTrackerProps {
  receipts: GoodsReceiptView[];
  creditNotes: CreditNoteView[];
  onApplyCredit?: (creditNoteId: string, invoiceRef: string) => void;
}

const BENGALI_DIGITS = ['০', '১', '২', '৩', '৪', '৫', '৬', '৭', '৮', '৯'];
function toBengaliNumber(n: number): string {
  return n.toString().split('').map(d => {
    const idx = parseInt(d, 10);
    return isNaN(idx) ? d : BENGALI_DIGITS[idx];
  }).join('');
}

export const ReceivingTracker: FC<ReceivingTrackerProps> = ({
  receipts,
  creditNotes,
  onApplyCredit,
}) => {
  const { language, formatCurrency } = useLanguage();
  const isBn = language === 'bn';
  const [targetInvoice, setTargetInvoice] = useState('');

  return (
    <div
      className="receiving-tracker-container"
      role="region"
      aria-label={isBn ? 'পণ্য গ্রহণ ও ক্রেডিট আদায় ট্র্যাকার' : 'Receiving & Credit Recovery Tracker'}
      style={{
        border: '1px solid #e2e8f0',
        borderRadius: '12px',
        padding: '16px',
        backgroundColor: '#ffffff',
      }}
    >
      {/* Receipts Section */}
      <div style={{ marginBottom: '24px' }}>
        <h3 style={{ margin: '0 0 12px 0', fontSize: '1.05rem', fontWeight: 600, color: '#0f172a', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <PackageCheck size={20} color="#0284c7" />
          {isBn ? 'পণ্য সরবরাহ গ্রহণ ও অমিল যাচাই' : 'Goods Receipts & Discrepancies'}
        </h3>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {receipts.map((r) => (
            <div
              key={r.id}
              style={{
                border: `1px solid ${r.status === 'discrepant' ? '#fecaca' : '#e2e8f0'}`,
                borderRadius: '8px',
                padding: '12px',
                backgroundColor: r.status === 'discrepant' ? '#fff5f5' : '#f8fafc',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}
            >
              <div>
                <strong style={{ fontSize: '0.92rem', color: '#1e293b' }}>{r.supplier_name}</strong>
                <span style={{ fontSize: '0.8rem', color: '#64748b', marginLeft: '8px' }}>({r.sku})</span>
                <div style={{ fontSize: '0.82rem', color: '#475569', marginTop: '4px' }}>
                  {isBn ? 'অর্ডার: ' : 'Ordered: '}<strong>{isBn ? toBengaliNumber(r.ordered_quantity) : r.ordered_quantity}</strong> |{' '}
                  {isBn ? 'গৃহীত: ' : 'Received: '}<strong>{isBn ? toBengaliNumber(r.received_quantity) : r.received_quantity}</strong>
                  {r.damaged_quantity > 0 && (
                    <span style={{ color: '#dc2626', marginLeft: '6px' }}>
                      ({isBn ? 'নষ্ট: ' : 'Damaged: '}{isBn ? toBengaliNumber(r.damaged_quantity) : r.damaged_quantity})
                    </span>
                  )}
                  {r.shortage_quantity > 0 && (
                    <span style={{ color: '#d97706', marginLeft: '6px' }}>
                      ({isBn ? 'কমতি: ' : 'Shortage: '}{isBn ? toBengaliNumber(r.shortage_quantity) : r.shortage_quantity})
                    </span>
                  )}
                </div>
              </div>

              <span
                style={{
                  fontSize: '0.78rem',
                  padding: '3px 8px',
                  borderRadius: '9999px',
                  fontWeight: 600,
                  backgroundColor: r.status === 'complete' ? '#dcfce7' : '#fee2e2',
                  color: r.status === 'complete' ? '#166534' : '#991b1b',
                }}
              >
                {isBn
                  ? r.status === 'complete' ? 'সম্পূর্ণ' : 'অমিলে চিহ্নিত'
                  : r.status.toUpperCase()}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Credit Recovery Lifecycle Section */}
      <div>
        <h3 style={{ margin: '0 0 12px 0', fontSize: '1.05rem', fontWeight: 600, color: '#0f172a', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <ShieldCheck size={20} color="#10b981" />
          {isBn ? 'ক্রেডিট নোট আদায় ও ইনভয়েস সমন্বয়' : 'Credit Recovery & Invoice Application'}
        </h3>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {creditNotes.map((cn) => {
            const isApplied = cn.status === 'applied_to_bill';
            return (
              <div
                key={cn.id}
                style={{
                  border: '1px solid #e2e8f0',
                  borderRadius: '8px',
                  padding: '12px',
                  backgroundColor: isApplied ? '#f0fdf4' : '#ffffff',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <strong style={{ fontSize: '0.9rem', color: '#0f172a' }}>{cn.supplier_name}</strong>
                    <span style={{ fontSize: '0.8rem', color: '#64748b', marginLeft: '8px' }}>
                      ({cn.claim_reason})
                    </span>
                    <div style={{ fontSize: '0.95rem', fontWeight: 700, color: '#0284c7', marginTop: '2px' }}>
                      {formatCurrency(cn.amount_bdt * 100)}
                    </div>
                  </div>

                  <span
                    style={{
                      fontSize: '0.75rem',
                      padding: '3px 8px',
                      borderRadius: '4px',
                      backgroundColor: isApplied ? '#dcfce7' : '#fef3c7',
                      color: isApplied ? '#166534' : '#92400e',
                      fontWeight: 600,
                    }}
                  >
                    {isBn
                      ? isApplied ? `সমন্বিত (${cn.applied_invoice_ref})` : 'দাবীকৃত ক্রেডিট'
                      : isApplied ? `Applied (${cn.applied_invoice_ref})` : 'Suspected'}
                  </span>
                </div>

                {/* Apply Control */}
                {!isApplied && onApplyCredit && (
                  <div style={{ marginTop: '10px', display: 'flex', gap: '8px', alignItems: 'center' }}>
                    <input
                      type="text"
                      placeholder={isBn ? 'চালান নম্বর (যেমন: INV-2026-041)' : 'Invoice Ref (e.g. INV-41)'}
                      value={targetInvoice}
                      onChange={(e) => setTargetInvoice(e.target.value)}
                      style={{
                        padding: '6px 10px',
                        borderRadius: '6px',
                        border: '1px solid #cbd5e1',
                        fontSize: '0.82rem',
                        flex: 1,
                      }}
                    />
                    <button
                      type="button"
                      onClick={() => {
                        if (targetInvoice.trim()) {
                          onApplyCredit(cn.id, targetInvoice.trim());
                        }
                      }}
                      style={{
                        padding: '6px 12px',
                        borderRadius: '6px',
                        border: 'none',
                        backgroundColor: '#10b981',
                        color: '#ffffff',
                        fontSize: '0.82rem',
                        fontWeight: 600,
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px',
                      }}
                    >
                      <span>{isBn ? 'সমন্বয় করুন' : 'Apply'}</span>
                      <ArrowRight size={14} />
                    </button>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
