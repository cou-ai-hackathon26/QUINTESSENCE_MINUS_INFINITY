import { useState } from 'react';
import type { FC } from 'react';
import { useLanguage } from '../i18n/LanguageContext';
import { ConfidenceBadge } from './ConfidenceBadge';
import {
  ShoppingBag,
  AlertTriangle,
  Gift,
  FileCheck,
} from 'lucide-react';

export interface OfferEvaluationView {
  offer_id: string;
  supplier_name: string;
  title: string;
  base_unit_price_bdt: number;
  total_landed_cost_bdt: number;
  effective_unit_cost_bdt: number;
  bonus_units_awarded: number;
  meets_moq: boolean;
  feasibility: 'feasible_cash' | 'feasible_credit' | 'infeasible_insufficient_cash' | string;
  shortfall_bdt: number;
  confidence_score: number;
  has_critical_blocker: boolean;
  credit_period_days: number;
}

export interface BuyingDeskProps {
  sku: string;
  requiredQuantity: number;
  availableLiquidCashBdt: number;
  evaluations: OfferEvaluationView[];
  bestOfferId?: string;
  onDraftOrder?: (offerId: string) => void;
}

const BENGALI_DIGITS = ['০', '১', '২', '৩', '৪', '৫', '৬', '৭', '৮', '৯'];
function toBengaliNumber(n: number): string {
  return n.toString().split('').map(d => {
    const idx = parseInt(d, 10);
    return isNaN(idx) ? d : BENGALI_DIGITS[idx];
  }).join('');
}

export const BuyingDesk: FC<BuyingDeskProps> = ({
  sku,
  requiredQuantity,
  availableLiquidCashBdt,
  evaluations,
  bestOfferId,
  onDraftOrder,
}) => {
  const { language, formatCurrency } = useLanguage();
  const isBn = language === 'bn';
  const [selectedOfferId, setSelectedOfferId] = useState<string>(bestOfferId || evaluations[0]?.offer_id || '');

  return (
    <div
      className="buying-desk-container"
      role="region"
      aria-label={isBn ? 'বাইং ডেস্ক ও অফার তুলনা' : 'Buying Desk Offer Comparison'}
      style={{
        border: '1px solid #e2e8f0',
        borderRadius: '12px',
        padding: '16px',
        backgroundColor: '#ffffff',
      }}
    >
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <div>
          <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 600, color: '#0f172a', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <ShoppingBag size={20} color="#0284c7" />
            {isBn ? 'বাইং ডেস্ক — সরবরাহকারী অফার ও ল্যান্ডেড খরচ তুলনা' : 'Buying Desk — Landed Cost Comparison'}
          </h3>
          <p style={{ margin: '4px 0 0 0', fontSize: '0.85rem', color: '#64748b' }}>
            SKU: <strong style={{ color: '#1e293b' }}>{sku}</strong> | {isBn ? 'প্রয়োজনীয় পরিমাণ: ' : 'Required Qty: '}
            <strong>{isBn ? toBengaliNumber(requiredQuantity) : requiredQuantity}</strong>
          </p>
        </div>

        <div style={{ textAlign: 'right', fontSize: '0.85rem', color: '#475569' }}>
          <div>{isBn ? 'উপলব্ধ নগদ ক্যাশ:' : 'Available Liquid Cash:'}</div>
          <strong style={{ fontSize: '1rem', color: '#0f172a' }}>
            {formatCurrency(availableLiquidCashBdt * 100)}
          </strong>
        </div>
      </div>

      {/* Side-by-Side Offer Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '14px', marginBottom: '16px' }}>
        {evaluations.map((evalItem) => {
          const isBest = evalItem.offer_id === bestOfferId;
          const isInfeasible = evalItem.feasibility === 'infeasible_insufficient_cash';

          return (
            <div
              key={evalItem.offer_id}
              onClick={() => setSelectedOfferId(evalItem.offer_id)}
              style={{
                border: `2px solid ${isBest ? '#10b981' : selectedOfferId === evalItem.offer_id ? '#0284c7' : '#e2e8f0'}`,
                borderRadius: '10px',
                padding: '14px',
                backgroundColor: isInfeasible ? '#fff1f2' : isBest ? '#f0fdf4' : '#f8fafc',
                cursor: 'pointer',
                position: 'relative',
              }}
            >
              {isBest && (
                <span
                  style={{
                    position: 'absolute',
                    top: '-10px',
                    right: '12px',
                    backgroundColor: '#10b981',
                    color: '#ffffff',
                    fontSize: '0.72rem',
                    fontWeight: 700,
                    padding: '2px 8px',
                    borderRadius: '9999px',
                  }}
                >
                  {isBn ? '★ সেরা সাশ্রয়ী অফার' : '★ Best Value'}
                </span>
              )}

              <h4 style={{ margin: '0 0 6px 0', fontSize: '0.98rem', color: '#0f172a' }}>
                {evalItem.supplier_name}
              </h4>
              <p style={{ margin: '0 0 10px 0', fontSize: '0.8rem', color: '#64748b' }}>
                {evalItem.title}
              </p>

              {/* Price Calculations */}
              <div style={{ borderTop: '1px solid #e2e8f0', paddingTop: '8px', fontSize: '0.85rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span style={{ color: '#64748b' }}>{isBn ? 'মূল দাম:' : 'Base Price:'}</span>
                  <span>{formatCurrency(evalItem.base_unit_price_bdt * 100)}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span style={{ color: '#64748b' }}>{isBn ? 'মোট খরচ:' : 'Total Cost:'}</span>
                  <span>{formatCurrency(evalItem.total_landed_cost_bdt * 100)}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 600, color: '#0f172a', marginTop: '6px' }}>
                  <span>{isBn ? 'কার্যকর একক খরচ:' : 'Effective Unit Cost:'}</span>
                  <span style={{ color: '#0284c7', fontSize: '0.95rem' }}>
                    {formatCurrency(evalItem.effective_unit_cost_bdt * 100)}
                  </span>
                </div>
              </div>

              {/* Bonus Tag */}
              {evalItem.bonus_units_awarded > 0 && (
                <div style={{ marginTop: '8px', display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.78rem', color: '#059669' }}>
                  <Gift size={14} />
                  <span>
                    {isBn
                      ? `বোনাস অর্জিত: ${toBengaliNumber(evalItem.bonus_units_awarded)} টি`
                      : `Bonus: ${evalItem.bonus_units_awarded} units`}
                  </span>
                </div>
              )}

              {/* Cash Feasibility Alert */}
              {isInfeasible && (
                <div style={{ marginTop: '10px', padding: '6px 8px', borderRadius: '6px', backgroundColor: '#fee2e2', color: '#991b1b', fontSize: '0.78rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <AlertTriangle size={14} />
                  <span>
                    {isBn
                      ? `নগদ ঘাটতি: ${formatCurrency(evalItem.shortfall_bdt * 100)}`
                      : `Cash shortfall: ${formatCurrency(evalItem.shortfall_bdt * 100)}`}
                  </span>
                </div>
              )}

              {/* Confidence Badge */}
              <div style={{ marginTop: '10px' }}>
                <ConfidenceBadge
                  score={evalItem.confidence_score}
                  band={evalItem.confidence_score >= 80 ? 'strong' : 'limited'}
                  readiness={evalItem.has_critical_blocker ? 'needs_clarification' : 'ready_for_review'}
                  compact={true}
                />
              </div>
            </div>
          );
        })}
      </div>

      {/* Action Draft Button */}
      {onDraftOrder && (
        <div style={{ textAlign: 'right' }}>
          <button
            type="button"
            onClick={() => onDraftOrder(selectedOfferId)}
            style={{
              padding: '10px 18px',
              borderRadius: '8px',
              border: 'none',
              backgroundColor: '#0284c7',
              color: '#ffffff',
              fontSize: '0.9rem',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
            }}
          >
            <FileCheck size={18} />
            <span>{isBn ? 'খসড়া পারচেজ অর্ডার তৈরি করুন' : 'Draft Purchase Order'}</span>
          </button>
        </div>
      )}
    </div>
  );
};
